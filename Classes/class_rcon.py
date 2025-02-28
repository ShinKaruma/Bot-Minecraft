from mcrcon import MCRcon
from Classes.lang_pack import LocalisedMessages

class Rcon:

    def __init__(self, host, pwd, port) -> None:
        self.host = host
        self.pwd = pwd
        self.port = port
        self.lang = LocalisedMessages()

         
    
    def sendOTP(self,ctx, pseudo, OTP) -> None:
        ### fonction permettant d'envoyer à un utilisateur l'OTP pour la liaison du compte
        with MCRcon(self.host, self.pwd, self.port) as mcr:
            mcr.command(self.lang.get_message(ctx, "otc").format(pseudo, OTP))

    def giveItem(self, pseudo, id_item) -> None:
        ### fonction permettant de donner un objet à un joueur (principalement utilisé par le daily et le shop)
        with MCRcon(self.host, self.pwd, self.port) as mcr:
            mcr.command("/execute as {0} run give {0} {1}".format(pseudo, id_item))

    def get_online_players(self):
        try:
            with MCRcon(self.host, self.pwd, self.port) as mcr:
                response = mcr.command("list")
                players_list = response.split(": ")[1].replace("\n", "").split(", ")
                print(players_list)
                return players_list
        except Exception:
            return Exception

    def is_player_online(self, player_name):
        online_players = self.get_online_players()
        return player_name in online_players
    
    # async def kill(self, target: str, reason: str = "Aucune raison"):
    #     try:
    #         if await self.is_player_online(target):
    #             with MCRcon(self.rcon_info["server_ip"], self.rcon_info["rcon_password"], self.rcon_info["rcon_port"]) as mcr:
    #                 command = f"kill {target} {reason}"
    #                 mcr.command(command)
    #                 return True
    #         else:
    #             return False
    #     except Exception as e:
    #         return e