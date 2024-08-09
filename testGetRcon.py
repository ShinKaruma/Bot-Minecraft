from Classes.passerelle import Passerelle

BDD = Passerelle()


BDD.getRconDiscord(id_discord=956195070795730974)
id_discord=956195070795730974

ResultEncrypt = BDD.encryptPwd("test", id_discord)
print(ResultEncrypt)

Result = BDD.decryptPwd(ResultEncrypt, id_discord)
print(Result)
