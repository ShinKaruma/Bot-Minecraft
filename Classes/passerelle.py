import mysql.connector as bdd
from dotenv import dotenv_values
from Classes.class_rcon import Rcon


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
    

    def doDiscordExists(self, id_discord) -> bool:
        req = "select if(id_serveur_discord = {0}, true , false ) as 'result' from serveur WHERE id_serveur_discord = {0}".format(id_discord)

        self.cursor.execute(req)

        resultat = self.cursor.fetchone()[0]

        if resultat == 1:
            return True
        else:
            return False
        
    
    def addDiscordServer(self, id_discord, ip_server, pwd_rcon, port_rcon) -> None:
        req = "INSERT INTO `serveur`(`id_serveur_discord`, `ip_serveur_minecraft`, `pwd_rcon`, `port_rcon`) VALUES (%s,%s,%s,%s)"

        self.cursor.execute(req,(id_discord, ip_server, pwd_rcon, port_rcon))

        self.connector.commit()

    def getRconDiscord(self, id_discord) -> Rcon:
        req = "select ip_serveur_minecraft, pwd_rcon, port_rcon from serveur where id_serveur_discord = {0}".format(id_discord)

        self.cursor.execute(req)

        resultat = self.cursor.fetchone()

        return Rcon(resultat[0], resultat[1], resultat[2])

    def doUserExists(self, id_serveur_discord, id_user_discord) -> bool:
        req = "select if(id_serveur_discord = {0} and id_user_discord = {1}, true, false) as 'result' from user where id_serveur_discord = {0} and id_user_discord = {1}".format(id_serveur_discord, id_user_discord)

        self.cursor.execute(req)

        resultat = self.cursor.fetchone()

        if resultat == None:
            return False
        elif resultat[0] == 1:
            return True
        elif resultat[0] == 0:
            return False
        
    
    def isPlayerLinked(self, id_serveur_discord, pseudo_minecraft) -> bool:
        req = "select if(id_serveur_discord = {0} and pseudo_minecraft = '{1}', true, false) as 'result' from user where id_serveur_discord = {0} and pseudo_minecraft = '{1}'".format(id_serveur_discord, pseudo_minecraft)

        self.cursor.execute(req)

        resultat = self.cursor.fetchone()

        if resultat == None:
            return False
        elif resultat[0] == 1:
            return True
        elif resultat[0] == 0:
            return False
    

    def addPlayer(self, id_serveur_discord, id_user_discord, pseudo_minecraft) -> None:
        req = "insert into user (id_user_discord, pseudo_minecraft, id_serveur_discord) values(%s, %s, %s)"

        self.cursor.execute(req, (id_user_discord, pseudo_minecraft, id_serveur_discord))

        self.connector.commit()
        
