import mysql.connector as bdd
from dotenv import dotenv_values
from Classes.class_rcon import Rcon
from Crypto.Cipher import AES
from Crypto.Util import Counter


class Passerelle:
    config = dotenv_values(".env.local")

    def __init__(self) -> None:
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
        query = "SELECT COUNT(*) FROM serveur WHERE id_serveur_discord = %s"
        result = self._execute_query(query, (id_discord,))
        return result[0] == 1 if result else False

    def addDiscordServer(self, id_discord, ip_server, pwd_rcon, port_rcon) -> None:
        query = "INSERT INTO serveur (id_serveur_discord, ip_serveur_minecraft, pwd_rcon, port_rcon) VALUES (%s, %s, %s, %s)"
        encrypted_pwd_rcon = self.encryptPwd(pwd_rcon, id_discord)
        self._execute_query(query, (id_discord, ip_server, encrypted_pwd_rcon, port_rcon))
        self.connector.commit()

    def getRconDiscord(self, id_discord) -> Rcon:
        query = "SELECT ip_serveur_minecraft, pwd_rcon, port_rcon FROM serveur WHERE id_serveur_discord = %s"
        result = self._execute_query(query, (id_discord,))
        if result:
            decrypted_pwd_rcon = self.decryptPwd(result[1], id_discord)
            return Rcon(result[0], decrypted_pwd_rcon, result[2])
        else:
            # Handle case when no record found
            return None

    def doUserExists(self, id_serveur_discord, id_user_discord) -> bool:
        query = "SELECT COUNT(*) FROM user WHERE id_serveur_discord = %s AND id_user_discord = %s"
        result = self._execute_query(query, (id_serveur_discord, id_user_discord))
        return result[0] == 1 if result else False

    def isPlayerLinked(self, id_serveur_discord, pseudo_minecraft) -> bool:
        query = "SELECT COUNT(*) FROM user WHERE id_serveur_discord = %s AND pseudo_minecraft = %s"
        result = self._execute_query(query, (id_serveur_discord, pseudo_minecraft))
        return result[0] == 1 if result else False

    def addPlayer(self, id_serveur_discord, id_user_discord, pseudo_minecraft) -> None:
        query = "INSERT INTO user (id_user_discord, pseudo_minecraft, id_serveur_discord) VALUES (%s, %s, %s)"
        self._execute_query(query, (id_user_discord, pseudo_minecraft, id_serveur_discord))
        self.connector.commit()

    def encryptPwd(self, plaintext, key: int) -> bytes:
        ctr = Counter.new(128)
        cipher = AES.new(key.to_bytes(16, 'big'), AES.MODE_CTR, counter=ctr)
        return cipher.encrypt(plaintext.encode())

    def decryptPwd(self, ciphertext: bytes, key: int) -> str:
        ctr = Counter.new(128)
        cipher = AES.new(key.to_bytes(16, 'big'), AES.MODE_CTR, counter=ctr)
        decrypted_data = cipher.decrypt(ciphertext)
        return decrypted_data.decode()
