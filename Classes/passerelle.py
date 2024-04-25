import mysql.connector as bdd
from dotenv import dotenv_values
from random import choices
from Classes.class_rcon import Rcon
from Crypto.Cipher import AES
from Crypto.Util import Counter


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
        req = "select ip_serveur_minecraft, pwd_rcon, port_rcon from serveur where id_serveur_discord = {0}".format(id_discord)

        self.cursor.execute(req)

        resultat = self.cursor.fetchone()

        decrypted_pwd_rcon = self.decryptPwd(bytes(resultat[1]), id_discord)

        return Rcon(resultat[0], decrypted_pwd_rcon, resultat[2])
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
        req = "select if(id_serveur_discord = {0} and pseudo_minecraft = '{1}', true, false) as 'result' from user where id_serveur_discord = {0} and pseudo_minecraft = '{1}'".format(id_serveur_discord, pseudo_minecraft)

        self.cursor.execute(req)

        resultat = self.cursor.fetchone()

        if resultat == None:
            return False
        elif resultat[0] == 1:
            return True
        elif resultat[0] == 0:
            return False
    
        query = "SELECT COUNT(*) FROM user WHERE id_serveur_discord = %s AND pseudo_minecraft = %s"
        result = self._execute_query(query, (id_serveur_discord, pseudo_minecraft))
        return result[0] == 1 if result else False

    def addPlayer(self, id_serveur_discord, id_user_discord, pseudo_minecraft) -> None:
        ### fonction permettant d'ajouter un joueur dépendant d'un serveur discord 
        query = "INSERT INTO user (id_user_discord, pseudo_minecraft, id_serveur_discord) VALUES (%s, %s, %s)"
        self._execute_query(query, (id_user_discord, pseudo_minecraft, id_serveur_discord))
        self.connector.commit()

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
    
    def getitemsDaily(self) -> dict: 
        ### Fonction permettant de ressortir une liste d'id avec un poids pour sélection aléatoire
        req = "select id_libelle, poids from daily"
        resultat = {}
        self.cursor.execute(req)

        output = self.cursor.fetchall()

        for x in output:
            resultat.update({x[0]:x[1]})
            
        return resultat
    
    def randItemChoice(self, data):
        ### fonction permettant de faire un choix d'item à partir de son poids et qui retourne l'id minecraft de l'item
        poids = list(data.values())
        ids = list(data.keys())

        choix = choices(ids, weights=poids, k=1)

        req = "select ID_item from daily where id_libelle = %s"

        self.cursor.execute(req, (choix))

        resultat = self.cursor.fetchone()

        return resultat

    def updatePlayerDate(self, id_user_discord) -> None:
        ### fonction permettant d'actualiser la date de la dernière utilisation de la commande /daily
        req = "update user set date_dernier_daily = DATE(NOW()) where id_user_discord = %s"

        self.cursor.execute(req, id_user_discord)

        self.connector.commit()