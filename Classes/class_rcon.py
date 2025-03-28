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


    def getOninePlayers(self) -> list:
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

    

    def killPlayer(self, playerName) -> None:
        with MCRcon(self.host, self.pwd, self.port) as mcr:
            mcr.command(f"kill {playerName}")

    def tpPlayerToPlayer(self, playerName, targetPlayerName) -> None:
        with MCRcon(self.host, self.pwd, self.port) as mcr:
            mcr.command(f"tp {playerName} {targetPlayerName}")

    def tpPlayerToCoords(self, playerName, coords) -> None:
        with MCRcon(self.host, self.pwd, self.port) as mcr:
            mcr.command(f"tp {playerName} {coords}")

    def changeGamemode(self, playerName, gamemode) -> None:
        with MCRcon(self.host, self.pwd, self.port) as mcr:
            mcr.command(f"gamemode {gamemode} {playerName}")

    def clearInventory(self, playerName) -> None:
        with MCRcon(self.host, self.pwd, self.port) as mcr:
            mcr.command(f"clear {playerName}")

    def getPlayerLocation(self, playerName) -> dict:
        with MCRcon(self.host, self.pwd, self.port) as mcr:
            response = mcr.command(f"data get entity {playerName} Pos")
            coords = response.split(", ")
            x = round(float(coords[0].split(": ")[1].replace("d", "").strip("[")))
            y = round(float(coords[1].replace("d", "")))
            z = round(float(coords[2].replace("d", "").strip("]")))

            return  {"x": x, "y": y, "z": z}

