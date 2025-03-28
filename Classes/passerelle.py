import mysql.connector as bdd
from dotenv import dotenv_values
from random import choices
from datetime import date
from Classes.class_rcon import Rcon
from interactions import Embed, EmbedField, ModalContext, LocalisedDesc
from Crypto.Cipher import AES
from Crypto.Util import Counter
from typing import List


class Passerelle:
    config = dotenv_values(".env.local")

    def __init__(self) -> None:
        ### initialisation de la connection à la base de donnée à partir des informations du fichier .env (ou .env.local hors environnement prod)
        self.connector = bdd.connect(
         host = self.config["URI"],
         user = self.config["USER"],
         password = self.config["PASSWORD"],
         database = self.config["USER"]   
        )
        self.cursor = self.connector.cursor()

    def _execute_query(self, query, params=None):
        self.cursor.execute(query, params)
        return self.cursor.fetchone()

    def doDiscordExists(self, id_discord) -> bool:
        ### fonction de vérification si un serveur discord existe déjà dans la base de données
        query = "SELECT COUNT(*) FROM serveur WHERE id_serveur_discord = %s"
        result = self._execute_query(query, (id_discord,))
        return result[0] == 1 if result else False

    def addDiscordServer(self, id_discord, ip_server, pwd_rcon, port_rcon) -> None:
        ### fonction permettant d'ajouter un serveur discord et le lier à un serveur minecraft
        query = "INSERT INTO serveur (id_serveur_discord, ip_serveur_minecraft, pwd_rcon, port_rcon) VALUES (%s, %s, %s, %s)"
        encrypted_pwd_rcon = self.encryptPwd(pwd_rcon, id_discord)
        self._execute_query(query, (id_discord, ip_server, encrypted_pwd_rcon, port_rcon))
        self.connector.commit()

    def getRconDiscord(self, id_discord) -> Rcon:
        ### fonction permettant de créer un objet rcon dépendant d'un serveur discord
        query = "SELECT ip_serveur_minecraft, pwd_rcon, port_rcon FROM serveur WHERE id_serveur_discord = %s"
        result = self._execute_query(query, (id_discord,))
        if result:
            decrypted_pwd_rcon = self.decryptPwd(result[1], id_discord)
            return Rcon(result[0], decrypted_pwd_rcon, result[2])
        else:
            # Handle case when no record found
            return None

    def doUserExists(self, id_serveur_discord, id_user_discord) -> bool:
        ### fonction de vérification si un utilisateur s'est déjà linké à un serveur discord
        query = "SELECT COUNT(*) FROM user WHERE id_serveur_discord = %s AND id_user_discord = %s"
        result = self._execute_query(query, (id_serveur_discord, id_user_discord))
        return result[0] == 1 if result else False

    def isPlayerLinked(self, id_serveur_discord, pseudo_minecraft) -> bool:
        ### fonction de vérification si un joueur a déjà été linké à un serveur discord   
        query = "SELECT COUNT(*) FROM user WHERE id_serveur_discord = %s AND pseudo_minecraft = %s"
        result = self._execute_query(query, (id_serveur_discord, pseudo_minecraft))
        return result[0] == 1 if result else False

    def addPlayer(self, id_serveur_discord, id_user_discord, pseudo_minecraft) -> None:
        ### fonction permettant d'ajouter un joueur dépendant d'un serveur discord 
        query = "INSERT INTO user (id_user_discord, pseudo_minecraft, id_serveur_discord) VALUES (%s, %s, %s)"
        self._execute_query(query, (id_user_discord, pseudo_minecraft, id_serveur_discord))
        self.connector.commit()

    def getPlayer(self, id_serveur_discord, id_user_discord) -> str:
        query = "select pseudo_minecraft from user where id_serveur_discord = %s AND id_user_discord = %s"
        result = self._execute_query(query, (id_serveur_discord, id_user_discord))
        return result[0]

    def getPlayerDateDaily(self, id_serveur_discord, id_user_discord) -> date:
        query = "select date_dernier_daily from user where id_serveur_discord = %s AND id_user_discord = %s"
        query_result = self._execute_query(query, (id_serveur_discord, id_user_discord))[0]
        return query_result


    def encryptPwd(self, plaintext, key: int) -> bytes:
        ### fonction permettant de chiffrer les mots de passes des rcon
        ctr = Counter.new(128)
        cipher = AES.new(key.to_bytes(16, 'big'), AES.MODE_CTR, counter=ctr)
        return cipher.encrypt(plaintext.encode())

    def decryptPwd(self, ciphertext:bytes, key:int) -> str:
        ### fonction permettant de déchiffrer les mots de passes des rcon
        ctr = Counter.new(128)
        cipher = AES.new(key.to_bytes(16, 'big'), AES.MODE_CTR, counter=ctr)
        decrypted_data = cipher.decrypt(ciphertext)
        return decrypted_data.decode()
    
    def getitemsDaily(self, locale: str) -> dict: 
        KnownLocales = ["en-US", "fr"]

        if locale not in KnownLocales:
            locale = "en-US"
        ### Fonction permettant de ressortir une liste d'id avec un poids pour sélection aléatoire
        req = "select libelle, ID_Item, poids from daily join libelle_daily on daily.id_libelle = libelle_daily.id_libelle where locale = %s"
        self.cursor.execute(req, (locale,))
        resultat = {}

        output = self.cursor.fetchall()

        for x in output:
            resultat.update({(x[0], x[1]):x[2]})
            
        return resultat
    
    def randItemChoice(self, data) -> tuple:
        ### fonction permettant de faire un choix d'item à partir de son poids et qui retourne l'id minecraft de l'item
        poids = list(data.values())
        ids = list(data.keys())

        choix = choices(ids, weights=poids, k=1)

        return choix[0]

    def updatePlayerDate(self, id_user_discord, id_serveur_discord) -> None:
        ### fonction permettant d'actualiser la date de la dernière utilisation de la commande /daily
        req = "update user set date_dernier_daily = DATE(NOW()) where id_user_discord = %s and id_serveur_discord = %s"

        self._execute_query(req, (id_user_discord, id_serveur_discord))

        self.connector.commit()

    def addNbDaily(self, id_user_discord, id_serveur_discord):
        req = "select nb_daily from user where id_user_discord = %s and id_serveur_discord = %s"
        nb_daily = self._execute_query(req, (id_user_discord, id_serveur_discord))[0]

        nb_daily+=1

        query = "update user set nb_daily = %s where id_user_discord = %s and id_serveur_discord = %s"

        self._execute_query(query, (nb_daily, id_user_discord, id_serveur_discord))
        
        self.connector.commit()
    
    def addCoins(self, id_user_discord, id_serveur_discord, p_nb_coins):
        req = "select total_coins from user where id_user_discord = %s and id_serveur_discord = %s"
        nb_coins = self._execute_query(req, (id_user_discord, id_serveur_discord))[0]
        nb_coins+= p_nb_coins

        query = "update user set total_coins = %s where id_user_discord = %s and id_serveur_discord = %s"
        self._execute_query(query, (nb_coins, id_user_discord, id_serveur_discord))
        self.connector.commit()

    
    def remCoins(self, id_user_discord, id_serveur_discord, p_nb_coins):
        req = "select total_coins from user where id_user_discord = %s and id_serveur_discord = %s"
        nb_coins = self._execute_query(req, (id_user_discord, id_serveur_discord))[0]
        nb_coins-= p_nb_coins

        if nb_coins < 0:
            nb_coins = 0

        query = "update user set total_coins = %s where id_user_discord = %s and id_serveur_discord = %s"
        self._execute_query(query, (nb_coins, id_user_discord, id_serveur_discord))
        self.connector.commit()
    
    def getNbCoins(self, id_user_discord, id_serveur_discord) -> int:
        req = "select total_coins from user where id_user_discord = %s and id_serveur_discord = %s"
        nb_coins = self._execute_query(req, (id_user_discord, id_serveur_discord))[0]
        return nb_coins
    
    def getShopItems(self) -> List[Embed]:
        req = "select id_item, titre, prix_item, item_id from shop"
        self.cursor.execute(req)
        result = self.cursor.fetchall()
        Embeds = []
        for x in result:
            Embeds.append(Embed(title="Shop", description="item",
            fields=[
                EmbedField(name="Item", value=str(x[1])), 
                EmbedField(name="Price", value=str(x[2])), 
                EmbedField(name="ID", value=str(x[3]))
                ]))
        
        return Embeds

            
    def getShopitemsPremium(self) -> List[Embed]:
        req = "select id_item, libelle, prix_item from shop_premium"
        self.cursor.execute(req)
        result = self.cursor.fetchall()
        Embeds = []
        for x in result:
            Embeds.append(Embed(title="Shop Premium", description="premium item",
            fields=[
                EmbedField(name="Item", value=str(x[1])), 
                EmbedField(name="Price", value=str(x[2])), 
                EmbedField(name="ID", value=str(x[0]))
                ]
            ))
        
        return Embeds
    
    def isServerPremium(self, id_serveur_discord) -> bool:
        req = "select count(id_serveur_discord) from achat where id_serveur_discord = %s and id_package = 1"
        result = self._execute_query(req, (id_serveur_discord,))[0]
        return result == 1 if result else False


    def addItemShop(self, ctx: ModalContext, titre, prix_item, id_item) -> None:
        req = "insert into shop_premium (id_item, prix_item, id_serveur_discord, libelle) values (%s, %s, %s, %s)"
        self._execute_query(req, (id_item, prix_item, ctx.guild_id, titre))
        self.connector.commit()
    
    def removeItemShop(self, id_item, id_serveur_discord) -> None:
        req = "delete from shop_premium where id_item = %s and id_serveur_discord = %s"
        self._execute_query(req, (id_item, id_serveur_discord))
        self.connector.commit()

    def addPremium(self, id_server_discord) -> None:
        req = "insert into achat (id_serveur_discord, id_package) values (%s, 1)"
        self._execute_query(req, (id_server_discord,))
        self.connector.commit()

    def removePremium(self, id_server_discord) -> None:
        req = "delete from achat where id_serveur_discord = %s"
        self._execute_query(req, (id_server_discord,))
        self.connector.commit()

    def addItemDaily(self, id_serveur_discord, id_item, libelle, poids) -> None:
        req = "insert into daily_premium (id_item, libelle, poids, id_serveur_discord) values (%s, %s, %s, %s)"
        self._execute_query(req, (id_item, libelle, poids, id_serveur_discord))
        self.connector.commit()

    def removeItemDaily(self, id_item, id_serveur_discord) -> None:
        req = "delete from daily_premium where id_item = %s and id_serveur_discord = %s"
        self._execute_query(req, (id_item, id_serveur_discord))
        self.connector.commit()
    
    def getDailyItemsPremium(self, id_serveur_discord) -> dict:
        req = "select id_item, libelle, poids from daily_premium where id_serveur_discord = %s"
        self.cursor.execute(req, (id_serveur_discord,))
        resultat = {}

        output = self.cursor.fetchall()

        for x in output:
            resultat.update({(x[1], x[0]):x[2]})
            
        return resultat
        