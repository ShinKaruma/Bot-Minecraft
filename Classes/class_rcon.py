from mcrcon import MCRcon

class Rcon:

    def __init__(self, host, pwd, port) -> None:
        self.host = host
        self.pwd = pwd
        self.port = port
    
    def sendOTP(self, pseudo, OTP) -> None:
        with MCRcon(self.host, self.pwd, self.port) as mcr:
            mcr.command("/msg {0} Le code pour la liaison du compte est: {1}".format(pseudo, OTP))