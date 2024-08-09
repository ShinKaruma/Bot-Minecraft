from mcrcon import MCRcon

class Rcon:

    def __init__(self, host, pwd, port) -> None:
        self.host = host
        self.pwd = pwd
        self.port = port
    
    def sendOTP(self, pseudo, OTP) -> None:
        ### fonction permettant d'envoyer à un utilisateur l'OTP pour la liaison du compte
        with MCRcon(self.host, self.pwd, self.port) as mcr:
            mcr.command("/msg {0} Le code pour la liaison du compte est: {1}".format(pseudo, OTP))

    def giveItem(self, pseudo, id_item) -> None:
        ### fonction permettant de donner un objet à un joueur (principalement utilisé par le daily et le shop)
        with MCRcon(self.host, self.pwd, self.port) as mcr:
            mcr.command("/execute as {0} run give {0} {1}".format(pseudo, id_item))

    def getOninePlayers(self) -> list:
        with MCRcon(self.host, self.pwd, self.port) as mcr:
            response = mcr.command("list")
            players = response.split(": ")[1].split(", ")

            return players

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
