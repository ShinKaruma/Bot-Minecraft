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