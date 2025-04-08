import mysql.connector as bdd
from mysql.connector.pooling import MySQLConnectionPool
from mysql.connector import Error as MySQLError
from dotenv import dotenv_values
from random import choices
from datetime import date
from typing import List, Optional, Dict, Tuple
from Classes.class_rcon import Rcon
from interactions import Embed, EmbedField, ModalContext, LocalisedDesc
from Crypto.Cipher import AES
from Crypto.Util import Counter
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log")
    ]
)
logger = logging.getLogger(__name__)


class Passerelle:
    config = dotenv_values(".env")

    def __init__(self) -> None:
        """Initialise le pool de connexions à la base de données."""
        try:
            self.pool = MySQLConnectionPool(
                pool_name="crafty_pool",
                pool_size=20,
                pool_reset_timeout=300,
                pool_reset_session=True,
                host=self.config["URI"],
                user=self.config["USER"],
                password=self.config["PASSWORD"],
                database=self.config["USER"],
                autocommit=True
            )
        except MySQLError as e:
            raise RuntimeError(f"Failed to initialize database connection pool: {e}")

    def _get_connection(self) -> bdd.MySQLConnection:
        """Récupère une connexion du pool."""
        try:
            conn = self.pool.get_connection()
            conn.ping(reconnect=True)
            return conn
        except MySQLError as e:
            raise RuntimeError(f"Failed to get connection from pool: {e}")

    def _execute_query(self, query: str, params: Optional[tuple] = None) -> Optional[tuple]:
        """Exécute une requête SQL et renvoie le premier résultat."""
        conn = None
        cursor = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()
        except MySQLError as e:
            raise RuntimeError(f"Database query failed: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def _execute_query_fetchall(self, query: str, params: Optional[tuple] = None) -> List[tuple]:
        """Exécute une requête SQL et renvoie tous les résultats."""
        conn = None
        cursor = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
        except MySQLError as e:
            raise RuntimeError(f"Database query failed: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def doDiscordExists(self, id_discord: int) -> bool:
        """Vérifie si un serveur Discord existe déjà dans la base de données."""
        query = "SELECT COUNT(*) FROM serveur WHERE id_serveur_discord = %s"
        result = self._execute_query(query, (int(id_discord),))
        return result[0] == 1 if result else False

    def addDiscordServer(self, id_discord: int, ip_server: str, pwd_rcon: str, port_rcon: int) -> None:
        """Ajoute un serveur Discord et le lie à un serveur Minecraft."""
        query = "INSERT INTO serveur (id_serveur_discord, ip_serveur_minecraft, pwd_rcon, port_rcon) VALUES (%s, %s, %s, %s)"
        encrypted_pwd_rcon = self.encryptPwd(pwd_rcon, id_discord)
        self._execute_query(query, (id_discord, ip_server, encrypted_pwd_rcon, port_rcon))
        logger.info(f"addDiscordServer: Added server id_discord={id_discord}, ip_server={ip_server}")

    def getRconDiscord(self, id_discord: int) -> Optional[Rcon]:
        """Crée un objet Rcon pour un serveur Discord donné."""
        query = "SELECT ip_serveur_minecraft, pwd_rcon, port_rcon FROM serveur WHERE id_serveur_discord = %s"
        result = self._execute_query(query, (id_discord,))
        if result:
            decrypted_pwd_rcon = self.decryptPwd(result[1], id_discord)
            return Rcon(result[0], decrypted_pwd_rcon, result[2])
        return None

    def doUserExists(self, id_serveur_discord: int, id_user_discord: int) -> bool:
        """Vérifie si un utilisateur est déjà lié à un serveur Discord."""
        query = "SELECT COUNT(*) FROM user WHERE id_serveur_discord = %s AND id_user_discord = %s"
        result = self._execute_query(query, (id_serveur_discord, id_user_discord))
        logger.info(f"doUserExists: id_serveur_discord={id_serveur_discord}, id_user_discord={id_user_discord}, result={result}")
        return result[0] == 1 if result else False

    def isPlayerLinked(self, id_serveur_discord: int, pseudo_minecraft: str) -> bool:
        """Vérifie si un pseudo Minecraft est déjà lié à un serveur Discord."""
        query = "SELECT COUNT(*) FROM user WHERE id_serveur_discord = %s AND pseudo_minecraft = %s"
        result = self._execute_query(query, (id_serveur_discord, pseudo_minecraft))
        return result[0] == 1 if result else False

    def addPlayer(self, id_serveur_discord: int, id_user_discord: int, pseudo_minecraft: str) -> None:
        """Ajoute un joueur lié à un serveur Discord."""
        query = "INSERT INTO user (id_user_discord, pseudo_minecraft, id_serveur_discord) VALUES (%s, %s, %s)"
        self._execute_query(query, (id_user_discord, pseudo_minecraft, id_serveur_discord))
        logger.info(f"addPlayer: Added user id_user_discord={id_user_discord}, pseudo_minecraft={pseudo_minecraft} to id_serveur_discord={id_serveur_discord}")

    def getPlayer(self, id_serveur_discord: int, id_user_discord: int) -> Optional[str]:
        """Récupère le pseudo Minecraft d'un utilisateur."""
        query = "SELECT pseudo_minecraft FROM user WHERE id_serveur_discord = %s AND id_user_discord = %s"
        result = self._execute_query(query, (id_serveur_discord, id_user_discord))
        return result[0] if result else None

    def getPlayerDateDaily(self, id_serveur_discord: int, id_user_discord: int) -> Optional[date]:
        """Récupère la date du dernier daily d'un utilisateur."""
        query = "SELECT date_dernier_daily FROM user WHERE id_serveur_discord = %s AND id_user_discord = %s"
        result = self._execute_query(query, (id_serveur_discord, id_user_discord))
        return result[0] if result else None

    def encryptPwd(self, plaintext: str, key: int) -> bytes:
        """Chiffre un mot de passe RCON."""
        ctr = Counter.new(128)
        cipher = AES.new(key.to_bytes(16, 'big'), AES.MODE_CTR, counter=ctr)
        return cipher.encrypt(plaintext.encode())

    def decryptPwd(self, ciphertext: bytes, key: int) -> str:
        """Déchiffre un mot de passe RCON."""
        ctr = Counter.new(128)
        cipher = AES.new(key.to_bytes(16, 'big'), AES.MODE_CTR, counter=ctr)
        decrypted_data = cipher.decrypt(ciphertext)
        return decrypted_data.decode()

    def getitemsDaily(self, locale: str) -> Dict[Tuple[str, str], int]:
        """Récupère les items disponibles pour le daily avec leurs poids."""
        KnownLocales = ["en-US", "fr"]
        if locale not in KnownLocales:
            locale = "en-US"
        query = "SELECT libelle, ID_Item, poids FROM daily JOIN libelle_daily ON daily.id_libelle = libelle_daily.id_libelle WHERE locale = %s"
        result = self._execute_query_fetchall(query, (locale,))
        resultat = {}
        for x in result:
            resultat[(x[0], x[1])] = x[2]
        return resultat

    def randItemChoice(self, data: Dict[Tuple[str, str], int]) -> Tuple[str, str]:
        """Choisit un item aléatoirement en fonction de son poids."""
        poids = list(data.values())
        ids = list(data.keys())
        return choices(ids, weights=poids, k=1)[0]

    def updatePlayerDate(self, id_user_discord: int, id_serveur_discord: int) -> None:
        """Met à jour la date du dernier daily d'un utilisateur."""
        query = "UPDATE user SET date_dernier_daily = DATE(NOW()) WHERE id_user_discord = %s AND id_serveur_discord = %s"
        self._execute_query(query, (id_user_discord, id_serveur_discord))

    def addNbDaily(self, id_user_discord: int, id_serveur_discord: int) -> None:
        """Incrémente le compteur de daily d'un utilisateur."""
        query = "SELECT nb_daily FROM user WHERE id_user_discord = %s AND id_serveur_discord = %s"
        nb_daily = self._execute_query(query, (id_user_discord, id_serveur_discord))[0]
        nb_daily += 1
        update_query = "UPDATE user SET nb_daily = %s WHERE id_user_discord = %s AND id_serveur_discord = %s"
        self._execute_query(update_query, (nb_daily, id_user_discord, id_serveur_discord))

    def addCoins(self, id_user_discord: int, id_serveur_discord: int, p_nb_coins: int) -> None:
        """Ajoute des coins à un utilisateur."""
        query = "SELECT total_coins FROM user WHERE id_user_discord = %s AND id_serveur_discord = %s"
        nb_coins = self._execute_query(query, (id_user_discord, id_serveur_discord))[0]
        nb_coins += p_nb_coins
        update_query = "UPDATE user SET total_coins = %s WHERE id_user_discord = %s AND id_serveur_discord = %s"
        self._execute_query(update_query, (nb_coins, id_user_discord, id_serveur_discord))

    def remCoins(self, id_user_discord: int, id_serveur_discord: int, p_nb_coins: int) -> None:
        """Retire des coins à un utilisateur."""
        query = "SELECT total_coins FROM user WHERE id_user_discord = %s AND id_serveur_discord = %s"
        nb_coins = self._execute_query(query, (id_user_discord, id_serveur_discord))[0]
        nb_coins -= p_nb_coins
        if nb_coins < 0:
            nb_coins = 0
        update_query = "UPDATE user SET total_coins = %s WHERE id_user_discord = %s AND id_serveur_discord = %s"
        self._execute_query(update_query, (nb_coins, id_user_discord, id_serveur_discord))

    def getNbCoins(self, id_user_discord: int, id_serveur_discord: int) -> int:
        """Récupère le nombre de coins d'un utilisateur."""
        query = "SELECT total_coins FROM user WHERE id_user_discord = %s AND id_serveur_discord = %s"
        result = self._execute_query(query, (id_user_discord, id_serveur_discord))
        return result[0] if result else 0

    def getShopItems(self) -> List[Embed]:
        """Récupère les items du shop standard."""
        query = "SELECT id_item, titre, prix_item, item_id FROM shop"
        result = self._execute_query_fetchall(query)
        embeds = []
        for x in result:
            embeds.append(Embed(
                title="Shop",
                description="item",
                fields=[
                    EmbedField(name="Item", value=str(x[1])),
                    EmbedField(name="Price", value=str(x[2])),
                    EmbedField(name="ID", value=str(x[3]))
                ]
            ))
        return embeds

    def getShopitemsPremium(self, id_serveur_discord: int) -> List[Embed]:
        """Récupère les items du shop premium."""
        query = "SELECT id_item, libelle, prix_item FROM shop_premium WHERE id_serveur_discord = %s"
        result = self._execute_query_fetchall(query, (id_serveur_discord,))
        embeds = []
        for x in result:
            embeds.append(Embed(
                title="Shop Premium",
                description="premium item",
                fields=[
                    EmbedField(name="Item", value=str(x[1])),
                    EmbedField(name="Price", value=str(x[2])),
                    EmbedField(name="ID", value=str(x[0]))
                ]
            ))
        return embeds

    def isServerPremium(self, id_serveur_discord: int) -> bool:
        """Vérifie si un serveur est premium."""
        query = "SELECT COUNT(id_serveur_discord) FROM achat WHERE id_serveur_discord = %s AND id_package = 1"
        result = self._execute_query(query, (id_serveur_discord,))[0]
        return result == 1 if result else False

    def addItemShop(self, ctx: ModalContext, titre: str, prix_item: int, id_item: str) -> None:
        """Ajoute un item au shop premium."""
        query = "INSERT INTO shop_premium (id_item, prix_item, id_serveur_discord, libelle) VALUES (%s, %s, %s, %s)"
        self._execute_query(query, (id_item, prix_item, int(ctx.guild_id), titre))
        logger.info(f"addItemShop: Added item id_item={id_item}, titre={titre}, prix_item={prix_item} to id_serveur_discord={guild_id}")

    def removeItemShop(self, id_item: str, id_serveur_discord: int) -> None:
        """Supprime un item du shop premium."""
        query = "DELETE FROM shop_premium WHERE id_item = %s AND id_serveur_discord = %s"
        self._execute_query(query, (id_item, id_serveur_discord))
        logger.info(f"removeItemShop: Removed item id_item={id_item} from id_serveur_discord={id_serveur_discord}")

    def addPremium(self, id_server_discord: int) -> None:
        """Ajoute le statut premium à un serveur."""
        query = "INSERT INTO achat (id_serveur_discord, id_package) VALUES (%s, 1)"
        self._execute_query(query, (id_server_discord,))

    def removePremium(self, id_server_discord: int) -> None:
        """Supprime le statut premium d'un serveur."""
        query = "DELETE FROM achat WHERE id_serveur_discord = %s"
        self._execute_query(query, (id_server_discord,))

    def addItemDaily(self, id_serveur_discord: int, id_item: str, libelle: str, poids: int) -> None:
        """Ajoute un item au daily premium."""
        query = "INSERT INTO daily_premium (id_item, libelle, poids, id_serveur_discord) VALUES (%s, %s, %s, %s)"
        self._execute_query(query, (id_item, libelle, poids, id_serveur_discord))
        logger.info(f"addItemDaily: Added daily item id_item={id_item}, libelle={libelle}, poids={poids} to id_serveur_discord={id_serveur_discord}")

    def removeItemDaily(self, id_item: str, id_serveur_discord: int) -> None:
        """Supprime un item du daily premium."""
        query = "DELETE FROM daily_premium WHERE id_item = %s AND id_serveur_discord = %s"
        self._execute_query(query, (id_item, id_serveur_discord))
        logger.info(f"removeItemDaily: Removed daily item id_item={id_item} from id_serveur_discord={id_serveur_discord}")

    def getDailyItemsPremium(self, id_serveur_discord: int) -> Dict[Tuple[str, str], int]:
        """Récupère les items du daily premium."""
        query = "SELECT id_item, libelle, poids FROM daily_premium WHERE id_serveur_discord = %s"
        result = self._execute_query_fetchall(query, (id_serveur_discord,))
        resultat = {}
        for x in result:
            resultat[(x[1], x[0])] = x[2]
        return resultat
