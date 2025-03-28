from Classes.passerelle import Passerelle

if __name__ == "__main__":
    BDD = Passerelle()
    items = BDD.getitemsDaily('fr')
    # print(items)
    choix = BDD.randItemChoice(items)
    print(choix)
