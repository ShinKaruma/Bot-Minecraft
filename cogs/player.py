import interactions
from interactions import Extension, slash_command, slash_option, OptionType, SlashContext, Permissions, slash_default_member_permission, AutocompleteContext, SlashCommandChoice

from Classes.class_rcon import Rcon
from Classes.passerelle import Passerelle
from datetime import date, timedelta
import mcrcon


class Player(Extension):
    def __init__(self, bot):
        self.bot = bot
        self.rcon_info = {
            "server_ip": "127.0.0.1",
            "rcon_port": 25575,
            "rcon_password": "1234"
        }
        self.rcon = Rcon(self.rcon_info["server_ip"], self.rcon_info["rcon_password"], self.rcon_info["rcon_port"])
        self.BDD = Passerelle()

    async def getOnlinePlayers(self):
        return self.rcon.getOninePlayers()

    async def isPlayerOnline(self, playerName):
        onlinePlayer = await self.getOnlinePlayers()
        return playerName in onlinePlayer

    # ==================== PlayerList ====================

    @slash_command(
        name="players",
        description="Affiche une liste de joueurs présents sur le serveur"
    )
    async def players(self, ctx: SlashContext):
        players = await self.getOnlinePlayers()
        if players[0] == "There are 0":
            await ctx.send("Aucun joueur n'est actuellement en ligne.")
        else:
            players_str = "\n".join(players)
            await ctx.send(f"Liste des joueurs en ligne :\n{players_str}")

    # ==================== Kill ====================

    @slash_command(
        name="kill",
        description="Commande pour tuer un joueur."
    )
    @slash_option(
        name="target",
        description="Le joueur à tuer",
        required=True,
        opt_type=OptionType.STRING,
        autocomplete=True
    )
    @slash_option(
        name="reason",
        description="La raison de la mort",
        required=False,
        opt_type=OptionType.STRING
    )
    @slash_default_member_permission(Permissions.MODERATE_MEMBERS)
    async def kill(self, ctx: SlashContext, target: str, reason: str = "Aucune raison"):
        if await self.isPlayerOnline(target):
            self.rcon.killPlayer(target)
            await ctx.send(f"Le joueur `{target}` a été tué. Raison : `{reason}`")
        else:
            await ctx.send(f"Le joueur `{target}` n'est pas en ligne.")
    
    @kill.autocomplete("target")
    async def autoCompleteTarget(self, ctx: AutocompleteContext):
        string_option_input = ctx.input_text
        onlinePlayers = await self.getOnlinePlayers()
        choices = [
            {"name": player, "value": player} for player in onlinePlayers if player.startswith(string_option_input)
        ]
        await ctx.send(choices=choices)
    

    # ==================== Tp joueur vers joueur ====================

    @slash_command(
        name="tp_joueur",
        description="Téléporter joueur vers un autre joueur."
    )
    @slash_option(
        name="joueur1",
        description="Joueur à téléporter",
        required=True,
        opt_type=OptionType.STRING,
        autocomplete=True
    )
    @slash_option(
        name="joueur2",
        description="Joueur vers lesquels se téléporter",
        required=True,
        opt_type=OptionType.STRING,
        autocomplete=True
    )
    @slash_default_member_permission(Permissions.MODERATE_MEMBERS)
    async def tpPlayer(self, ctx: SlashContext, playerName: str, targetPlayerName: str):
        if await self.isPlayerOnline(playerName):
            if await self.isPlayerOnline(targetPlayerName):
                self.rcon.tpPlayerToPlayer(playerName, targetPlayerName)
                await ctx.send(f"Le joueur `{playerName}` a été téléporté vers `{targetPlayerName}`.")
            else:
                await ctx.send(f"Le joueur `{targetPlayerName}` n'est pas en ligne.")
        else:
            await ctx.send(f"Le joueur `{playerName}` n'est pas en ligne.")
    
    @tpPlayer.autocomplete("joueur1")
    async def autoComplete_playerName(self, ctx: AutocompleteContext):
        string_option_input = ctx.input_text
        onlinePlayers = await self.getOnlinePlayers()
        choices = [
            {"name": player, "value": player} for player in onlinePlayers if player.startswith(string_option_input)
        ]
        await ctx.send(choices=choices)
    
    @tpPlayer.autocomplete("joueur2")
    async def autocomplete_targetPlayerName(self, ctx: AutocompleteContext):
        string_option_input = ctx.input_text
        onlinePlayers = await self.getOnlinePlayers()
        choices = [
            {"name": player, "value": player} for player in onlinePlayers if player.startswith(string_option_input)
        ]
        await ctx.send(choices=choices)


    # ==================== Tp joueur vers coordonnées ====================

    @slash_command(
        name="tp_coord",
        description="Téléporter joueur vers des coordonnées."
    )
    @slash_option(
        name="joueur",
        description="Joueur à téléporter",
        required=True,
        opt_type=OptionType.STRING,
        autocomplete=True
    )
    @slash_option(
        name="coordonnees",
        description="X Y Z vers lesquels se téléporter",
        required=True,
        opt_type=OptionType.STRING
    )
    @slash_default_member_permission(Permissions.MODERATE_MEMBERS)
    async def tpCoords(self, ctx: SlashContext, playerName: str, coords: str):
        if await self.isPlayerOnline(playerName):
            self.rcon.tpPlayerToCoords(playerName, coords)
            await ctx.send(f"Le joueur `{playerName}` a été téléporté vers `{coords}`.")
        else:
            await ctx.send(f"Le joueur `{playerName}` n'est pas en ligne.")
    
    @tpCoords.autocomplete("joueur")
    async def autocomplete_joueur(self, ctx: AutocompleteContext):
        string_option_input = ctx.input_text
        onlinePlayers = await self.getOnlinePlayers()
        choices = [
            {"name": player, "value": player} for player in onlinePlayers if player.startswith(string_option_input)
        ]
        await ctx.send(choices=choices)
    

    # ==================== Gamemode ====================
    
    @slash_command(
        name="gamemode",
        description="Modifier le gamemode d'un joueur."
    )
    @slash_option(
        name="joueur",
        description="Joueur ciblé",
        required=True,
        opt_type=OptionType.STRING,
        autocomplete=True
    )
    @slash_option(
        name="gamemode",
        description="Gamemode ciblé",
        required=True,
        opt_type=OptionType.STRING,
        choices=[
            SlashCommandChoice(name="Aventure", value="adventure"),
            SlashCommandChoice(name="Creatif", value="creative"),
            SlashCommandChoice(name="Spectateur", value="spectator"),
            SlashCommandChoice(name="Survie", value="survival")
        ]
    )
    @slash_default_member_permission(Permissions.MODERATE_MEMBERS)
    async def gamemode(self, ctx: SlashContext, playerName: str, gamemode: str):
        if await self.isPlayerOnline(playerName):
            self.rcon.changeGamemode(playerName, gamemode)
            await ctx.send(f"Le joueur `{playerName}` a changé de gamemode: `{gamemode}`.")
        else:
            await ctx.send(f"Le joueur `{playerName}` n'est pas en ligne.")

    @gamemode.autocomplete("joueur")
    async def autocomplete_joueur(self, ctx: AutocompleteContext):
        string_option_input = ctx.input_text
        onlinePlayers = await self.getOnlinePlayers()
        choices = [
            {"name": player, "value": player} for player in onlinePlayers if player.startswith(string_option_input)
        ]
        await ctx.send(choices=choices)
    

    # ==================== Clear Inventory ====================

    @slash_command(
        name="clearinventory",
        description="Supprime tous les items de l'inventaire du joueur ciblé."
    )
    @slash_option(
        name="joueur",
        description="Joueur ciblé",
        required=True,
        opt_type=OptionType.STRING,
        autocomplete=True
    )
    @slash_default_member_permission(Permissions.MODERATE_MEMBERS)
    async def clearInventory(self, ctx: SlashContext, playerName: str):
        if self.isPlayerOnline(playerName):
            self.rcon.clearInventory(playerName)
            await ctx.send(f"Le joueur `{playerName}` n'a plus rien dans son inventaire.")
        else:
            await ctx.send(f"Le joueur `{playerName}` n'est pas en ligne.")

    @clearInventory.autocomplete("joueur")
    async def autocomplete_playerName(self, ctx: AutocompleteContext):
        string_option_input = ctx.input_text
        onlinePlayers = await self.getOnlinePlayers()
        choices = [
            {"name": player, "value": player} for player in onlinePlayers if player.startswith(string_option_input)
        ]
        await ctx.send(choices=choices)
    

    # ==================== Player Location ====================

    @slash_command(
        name="playerlocation",
        description="Obtenir la position actuelle d'un joueur."
    )
    @slash_option(
        name="joueur",
        description="Le joueur dont vous voulez connaître la position",
        required=True,
        opt_type=OptionType.STRING,
        autocomplete=True
    )
    @slash_default_member_permission(Permissions.MODERATE_MEMBERS)
    async def playerLocation(self, ctx: SlashContext, playerName: str):
        if await self.isPlayerOnline(playerName):
            coords = self.rcon.getPlayerLocation(playerName)
            await ctx.send(f"Position actuelle de `{playerName}` : X: `{coords['x']}`, Y: `{coords['y']}`, Z: `{coords['z']}`")
        else:
            await ctx.send(f"Le joueur `{playerName}` n'est pas en ligne.")

    @playerLocation.autocomplete("joueur")
    async def autocomplete_joueur(self, ctx: AutocompleteContext):
        string_option_input = ctx.input_text
        onlinePlayers = await self.getOnlinePlayers()
        choices = [
            {"name": player, "value": player} for player in onlinePlayers if player.startswith(string_option_input)
        ]
        await ctx.send(choices=choices)



    @slash_command(
        name="daily",
        description="Obtenir la récompense quotidienne"
    )
    async def dailyClaim(self, ctx: SlashContext):
        id_serveur_discord = ctx.guild_id
        id_user_discord = ctx.author_id

        if self.BDD.doDiscordExists(id_discord=id_serveur_discord) == False:
            await ctx.send("Le serveur discord sur lequel vous voulez récupérer votre récompense quotidienne n'est lié à aucun serveur minecraft, veuillez vous référer à l'administrateur du serveur", ephemeral=True)
            return

        if self.BDD.doUserExists(id_serveur_discord=id_serveur_discord, id_user_discord=id_user_discord) == False:
            await ctx.send("Vous n'avez pas lié de compte minecraft à ce serveur, veuillez commencer par la commande `/link`")
            return
        
        date_dernier_daily = self.BDD.getPlayerDateDaily(id_serveur_discord=id_serveur_discord, id_user_discord=id_user_discord)
        
        if date_dernier_daily != None and date_dernier_daily - date.today() == timedelta(days=0):
            await ctx.send("Vous avez déjà utilisé votre daily pour la journée, revenez demain")
            return
        
        pseudo_minecraft = self.BDD.getPlayer(id_serveur_discord=id_serveur_discord, id_user_discord=id_user_discord)

        if self.is_player_online(pseudo_minecraft) != True:
            ctx.send("vous n'etes pas connecte au serveur minecraft", ephemeral=True)
            return
        
        rcon = self.BDD.getRconDiscord(id_serveur_discord)
        items = self.BDD.getitemsDaily()
        choix_item = self.BDD.randItemChoice(items)
        rcon.giveItem(pseudo_minecraft, choix_item[0])
        libelle_item = self.BDD.getItemLibelle(choix_item[1])
        self.BDD.updatePlayerDate(id_user_discord=id_user_discord, id_serveur_discord=id_serveur_discord)
        self.BDD.addNbDaily(id_user_discord=id_user_discord, id_serveur_discord=id_serveur_discord)
        self.BDD.addCoins(id_user_discord, id_serveur_discord, 10)
        await ctx.send("Félicitation, vous avez obtenu {} et 10 pieces! Revenez demain pour votre prochaine récompense !".format(libelle_item))


    @slash_command(
        name="balance",
        description="Commande pour afficher le nombre de pieces d'un joueur"
    )
    @slash_option(
        name="user",
        description="l'utilisateur dont tu veux connaitre le nombre de pieces",
        required=False,
        opt_type=OptionType.USER
    )
    async def getBalance(self, ctx: SlashContext, user: interactions.Member = None):
        id_serveur_discord = ctx.guild_id
        id_user_discord = ctx.author_id
        

        if self.BDD.doDiscordExists(id_discord=id_serveur_discord) == False:
            await ctx.send("Le serveur discord sur lequel vous voulez récupérer votre récompense quotidienne n'est lié à aucun serveur minecraft, veuillez vous référer à l'administrateur du serveur", ephemeral=True)
            return

        if self.BDD.doUserExists(id_serveur_discord=id_serveur_discord, id_user_discord=id_user_discord) == False:
            await ctx.send("l'utilisateur pas lié de compte minecraft à ce serveur, veuillez commencer par la commande `/link`")
            return

        if user != None:
            if self.BDD.doUserExists(id_serveur_discord=id_serveur_discord, id_user_discord=user.id) == False:
                await ctx.send("l'utilisateur pas lié de compte minecraft à ce serveur, veuillez commencer par la commande `/link`")
                return
        
            params_id_user = user.id
            user_coins = self.BDD.getNbCoins(params_id_user, id_serveur_discord=id_serveur_discord)
            await ctx.send("**{}** possede **{}** pieces".format(user.display_name, user_coins))
            return
        
        
        user_coins = self.BDD.getNbCoins(id_user_discord=id_user_discord, id_serveur_discord=id_serveur_discord)
        await ctx.send("Vous avez **{}** pieces".format(user_coins))

    


def setup(bot):
    Player(bot)