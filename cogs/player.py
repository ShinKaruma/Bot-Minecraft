
import interactions, mcrcon, json
from interactions import Extension, slash_command, slash_option, OptionType, SlashContext, Button, ButtonStyle, listen, LocalisedName, LocalisedDesc, Permissions, slash_default_member_permission, AutocompleteContext, SlashCommandChoice, user_context_menu, Member, ContextMenuContext
from interactions.api.events import Component
from Classes.passerelle import Passerelle
from Classes.lang_pack import LocalisedMessages
from datetime import date, timedelta




class Player(Extension):
    def __init__(self, bot):
        self.bot = bot
        self.BDD = Passerelle()
        self.lang_pack = LocalisedMessages()

    async def do_everything_exists(self, ctx: SlashContext | ContextMenuContext):
        id_serveur_discord = ctx.guild_id
        id_user_discord = ctx.author_id

        if self.BDD.doDiscordExists(id_discord=id_serveur_discord) == False:
            await self.lang_pack.send_message(ctx, "server_not_linked")
            return False

        if self.BDD.doUserExists(id_serveur_discord=id_serveur_discord, id_user_discord=id_user_discord) == False:
            await self.lang_pack.send_message(ctx, "user_not_linked")
            return False
        
        else:
            return True   
   

    # ==================== PlayerList ====================

    @slash_command(
        name="playerlist",
        description=LocalisedDesc(
            english_us="Display the list of connected players on the server",
            french="Affiche la liste des joueurs présents sur le serveur"
        )
    )
    async def playerlist(self, ctx: SlashContext):
        if not self.BDD.doDiscordExists(id_discord=ctx.guild_id):
            await self.lang_pack.send_message(ctx, "server_not_linked")
            return
        
        rcon = self.BDD.getRconDiscord(ctx.guild_id)
        players = rcon.get_online_players()

        if players is Exception or players == ['']:
            await self.lang_pack.send_message(ctx, "no_players_online")
            return
        
        await self.lang_pack.send_message(ctx, "players_online_list", players=", ".join(players))
        


################## A traiter plus tard, pas utile pour une early access ##################

    # # ==================== Kill ====================

    # @slash_command(
    #     name="kill",
    #     description=LocalisedDesc(
    #         english_us="Command to kill a player",
    #         french="Commande pour tuer un joueur"
    #     )
    # )
    # @slash_option(
    #     name="target",
    #     description=LocalisedDesc(
    #         english_us="The player to kill",
    #         french="Le joueur à tuer"
    #     ),
    #     required=True,
    #     opt_type=OptionType.STRING,
    #     autocomplete=True
    # )
    # @slash_option(
    #     name="reason",
    #     description="La raison de la mort",
    #     required=False,
    #     opt_type=OptionType.STRING
    # )
    # @slash_default_member_permission(Permissions.MODERATE_MEMBERS)
    # async def kill(self, ctx: SlashContext, target: str, reason: str = "Aucune raison"):
    #     try:
    #         result = self.rcon.kill(target, reason)

    #         if result:
    #             await self.lang_pack.send_message(ctx, "player_killed", target, reason)
    #         else:
    #             await self.lang_pack.send_message(ctx, "player_not_online", target)
    #     except Exception as e:
    #         await self.lang_pack.send_message(ctx, "kill_error")
    
    # @kill.autocomplete("target")
    # async def autocomplete_target(self, ctx: AutocompleteContext):
    #     string_option_input = ctx.input_text
    #     online_players = await self.get_online_players()
    #     choices = [
    #         {"name": player, "value": player} for player in online_players if player.startswith(string_option_input)
    #     ]
    #     await ctx.send(choices=choices)
    

    # # ==================== Tp joueur vers joueur ====================

    # @slash_command(
    #     name="tp_joueur",
    #     description="Téléporter joueur vers un autre joueur."
    # )
    # @slash_option(
    #     name="joueur1",
    #     description="Joueur à téléporter",
    #     required=True,
    #     opt_type=OptionType.STRING,
    #     autocomplete=True
    # )
    # @slash_option(
    #     name="joueur2",
    #     description="Joueur vers lesquels se téléporter",
    #     required=True,
    #     opt_type=OptionType.STRING,
    #     autocomplete=True
    # )
    # @slash_default_member_permission(Permissions.MODERATE_MEMBERS)
    # async def tp_joueur(self, ctx: SlashContext, joueur1: str, joueur2: str):
    #     try:
    #         if await self.is_player_online(joueur1):
    #             if await self.is_player_online(joueur2):
    #                 with mcrcon.MCRcon(self.rcon_info["server_ip"], self.rcon_info["rcon_password"], self.rcon_info["rcon_port"]) as rcon:
    #                     command = f"tp {joueur1} {joueur2}"
    #                     response = rcon.command(command)
    #                     await ctx.send(f"Le joueur `{joueur1}` a été téléporté vers `{joueur2}`.")
    #             else:
    #                 await ctx.send(f"Le joueur `{joueur2}` n'est pas en ligne.")
    #         else:
    #             await ctx.send(f"Le joueur `{joueur1}` n'est pas en ligne.")
    #     except Exception as e:
    #         await ctx.send("Une erreur s'est produite lors de la tentative de téléportation.")
    
    # @tp_joueur.autocomplete("joueur1")
    # async def autocomplete_joueur1(self, ctx: AutocompleteContext):
    #     string_option_input = ctx.input_text
    #     online_players = await self.get_online_players()
    #     choices = [
    #         {"name": player, "value": player} for player in online_players if player.startswith(string_option_input)
    #     ]
    #     await ctx.send(choices=choices)
    
    # @tp_joueur.autocomplete("joueur2")
    # async def autocomplete_joueur2(self, ctx: AutocompleteContext):
    #     string_option_input = ctx.input_text
    #     online_players = await self.get_online_players()
    #     choices = [
    #         {"name": player, "value": player} for player in online_players if player.startswith(string_option_input)
    #     ]
    #     await ctx.send(choices=choices)


    # # ==================== Tp joueur vers coordonnées ====================

    # @slash_command(
    #     name="tp_coord",
    #     description="Téléporter joueur vers des coordonnées."
    # )
    # @slash_option(
    #     name="joueur",
    #     description="Joueur à téléporter",
    #     required=True,
    #     opt_type=OptionType.STRING,
    #     autocomplete=True
    # )
    # @slash_option(
    #     name="coordonnees",
    #     description="X Y Z vers lesquels se téléporter",
    #     required=True,
    #     opt_type=OptionType.STRING
    # )
    # @slash_default_member_permission(Permissions.MODERATE_MEMBERS)
    # async def tp_coord(self, ctx: SlashContext, joueur: str, coordonnees: str):
    #     try:
    #         if await self.is_player_online(joueur):
    #             with mcrcon.MCRcon(self.rcon_info["server_ip"], self.rcon_info["rcon_password"], self.rcon_info["rcon_port"]) as rcon:
    #                 command = f"tp {joueur} {coordonnees}"
    #                 response = rcon.command(command)
    #                 await ctx.send(f"Le joueur `{joueur}` a été téléporté vers `{coordonnees}`.")
    #         else:
    #             await ctx.send(f"Le joueur `{joueur}` n'est pas en ligne.")
    #     except Exception as e:
    #         await ctx.send("Une erreur s'est produite lors de la tentative de téléportation.")
    
    # @tp_coord.autocomplete("joueur")
    # async def autocomplete_joueur(self, ctx: AutocompleteContext):
    #     string_option_input = ctx.input_text
    #     online_players = await self.get_online_players()
    #     choices = [
    #         {"name": player, "value": player} for player in online_players if player.startswith(string_option_input)
    #     ]
    #     await ctx.send(choices=choices)

    

    # # ==================== Gamemode ====================
    # @slash_command(
    #     name="gamemode",
    #     description="Modifier le gamemode d'un joueur."
    # )
    # @slash_option(
    #     name="joueur",
    #     description="Joueur ciblé",
    #     required=True,
    #     opt_type=OptionType.STRING,
    #     autocomplete=True
    # )
    # @slash_option(
    #     name="gamemode",
    #     description="Gamemode ciblé",
    #     required=True,
    #     opt_type=OptionType.STRING,
    #     choices=[
    #         SlashCommandChoice(name="Aventure", value="adventure"),
    #         SlashCommandChoice(name="Creatif", value="creative"),
    #         SlashCommandChoice(name="Spectateur", value="spectator"),
    #         SlashCommandChoice(name="Survie", value="survival")
    #     ]
    # )
    # @slash_default_member_permission(Permissions.MODERATE_MEMBERS)
    # async def gamemode(self, ctx: SlashContext, joueur: str, gamemode: str):
    #     try:
    #         if await self.is_player_online(joueur):
    #             with mcrcon.MCRcon(self.rcon_info["server_ip"], self.rcon_info["rcon_password"], self.rcon_info["rcon_port"]) as rcon:
    #                 command = f"gamemode {gamemode} {joueur}"
    #                 response = rcon.command(command)
    #                 await ctx.send(f"Le joueur `{joueur}` a changé de gamemode: `{gamemode}`.")
    #         else:
    #             await ctx.send(f"Le joueur `{joueur}` n'est pas en ligne.")
    #     except Exception as e:
    #         await ctx.send("Une erreur s'est produite lors de la modification du gamemode.")
    # @gamemode.autocomplete("joueur")
    # async def autocomplete_joueur(self, ctx: AutocompleteContext):
    #     string_option_input = ctx.input_text
    #     online_players = await self.get_online_players()
    #     choices = [
    #         {"name": player, "value": player} for player in online_players if player.startswith(string_option_input)
    #     ]
    #     await ctx.send(choices=choices)
    

    # # ==================== Clear Inventory ====================

    # @slash_command(
    #     name="clearinventory",
    #     description="Supprime tous les items de l'inventaire du joueur ciblé."
    # )
    # @slash_option(
    #     name="joueur",
    #     description="Joueur ciblé",
    #     required=True,
    #     opt_type=OptionType.STRING,
    #     autocomplete=True
    # )
    # @slash_default_member_permission(Permissions.MODERATE_MEMBERS)
    # async def clearinventory(self, ctx: SlashContext, joueur: str):
    #     try:
    #         if await self.is_player_online(joueur):
    #             with mcrcon.MCRcon(self.rcon_info["server_ip"], self.rcon_info["rcon_password"], self.rcon_info["rcon_port"]) as rcon:
    #                 command = f"clear {joueur}"
    #                 response = rcon.command(command)
    #                 await ctx.send(f"Le joueur `{joueur}` n'a plus rien dans son inventaire.")
    #         else:
    #             await ctx.send(f"Le joueur `{joueur}` n'est pas en ligne.")
    #     except Exception as e:
    #         await ctx.send("Une erreur s'est produite lors du clear de l'inventaire.")
    # @clearinventory.autocomplete("joueur")
    # async def autocomplete_joueur(self, ctx: AutocompleteContext):
    #     string_option_input = ctx.input_text
    #     online_players = await self.get_online_players()
    #     choices = [
    #         {"name": player, "value": player} for player in online_players if player.startswith(string_option_input)
    #     ]
    #     await ctx.send(choices=choices)
    

    # # ==================== Player Location ====================

    # @slash_command(
    #     name="playerlocation",
    #     description="Obtenir la position actuelle d'un joueur."
    # )
    # @slash_option(
    #     name="joueur",
    #     description="Le joueur dont vous voulez connaître la position",
    #     required=True,
    #     opt_type=OptionType.STRING,
    #     autocomplete=True
    # )
    # @slash_default_member_permission(Permissions.MODERATE_MEMBERS)
    # async def playerlocation(self, ctx: SlashContext, joueur: str):
    #     try:
    #         if await self.is_player_online(joueur):
    #             with mcrcon.MCRcon(self.rcon_info["server_ip"], self.rcon_info["rcon_password"], self.rcon_info["rcon_port"]) as rcon:
    #                 command = f"data get entity {joueur} Pos"
    #                 response = rcon.command(command)
    #                 coords = response.split(", ")
    #                 x = round(float(coords[0].split(": ")[1].replace("d", "").strip("[")))
    #                 y = round(float(coords[1].replace("d", "")))
    #                 z = round(float(coords[2].replace("d", "").strip("]")))
    #                 await ctx.send(f"Position actuelle de `{joueur}` : X: `{x}`, Y: `{y}`, Z: `{z}`")
    #         else:
    #             await ctx.send(f"Le joueur `{joueur}` n'est pas en ligne.")
    #     except Exception as e:
    #         await ctx.send("Une erreur s'est produite lors de la récupération de la position du joueur.")
    # @playerlocation.autocomplete("joueur")
    # async def autocomplete_joueur(self, ctx: AutocompleteContext):
    #     string_option_input = ctx.input_text
    #     online_players = await self.get_online_players()
    #     choices = [
    #         {"name": player, "value": player} for player in online_players if player.startswith(string_option_input)
    #     ]
    #     await ctx.send(choices=choices)

    # ==================== Daily ====================


    @slash_command(
        name="daily",
        description=LocalisedDesc(
            english_us="Claim your daily reward",
            french="Obtenir la récompense quotidienne"
            )
    )
    async def dailyClaim(self, ctx: SlashContext):
        id_serveur_discord = ctx.guild_id
        id_user_discord = ctx.author_id

        if not await self.do_everything_exists(ctx):
            return
        
        rcon = self.BDD.getRconDiscord(id_serveur_discord)
        
        date_dernier_daily = self.BDD.getPlayerDateDaily(id_serveur_discord=id_serveur_discord, id_user_discord=id_user_discord)
        
        if date_dernier_daily != None and date_dernier_daily - date.today() == timedelta(days=0):

            await self.lang_pack.send_message(ctx, "already_claimed")
            return

        pseudo_minecraft = self.BDD.getPlayer(id_serveur_discord=id_serveur_discord, id_user_discord=id_user_discord)

        if not rcon.is_player_online(pseudo_minecraft):
            await self.lang_pack.send_message(ctx, "not_connected")
            return

        items = self.BDD.getitemsDaily(ctx.locale)
        
        if self.BDD.isServerPremium(id_serveur_discord):
            items.update(self.BDD.getDailyItemsPremium(id_serveur_discord))


        choix_item = self.BDD.randItemChoice(items)
        rcon.giveItem(pseudo_minecraft, choix_item[1])
        self.BDD.updatePlayerDate(id_user_discord=id_user_discord, id_serveur_discord=id_serveur_discord)
        self.BDD.addNbDaily(id_user_discord=id_user_discord, id_serveur_discord=id_serveur_discord)
        self.BDD.addCoins(id_user_discord, id_serveur_discord, 10)

        await self.lang_pack.send_message(ctx, "reward", libelle_item=choix_item[0])


    @slash_command(
        name="balance",
        description=LocalisedDesc(
            english_us="Command to display the number of coins of a player",
            french="Commande pour afficher le nombre de pieces d'un joueur"
        )
    )
    @slash_option(
        name="user",
        description=LocalisedDesc(
            english_us="The user whose number of coins you want to know",
            french="l'utilisateur dont tu veux connaitre le nombre de pieces"
        ),
        required=False,
        opt_type=OptionType.USER
    )
    async def getBalance(self, ctx: SlashContext, user: interactions.Member = None):
        id_serveur_discord = ctx.guild_id
        id_user_discord = ctx.author_id
        

        if not await self.do_everything_exists(ctx):
            return

        if user != None:
            if self.BDD.doUserExists(id_serveur_discord=id_serveur_discord, id_user_discord=user.id) == False:
                self.lang_pack.send_message(ctx, "user_not_linked")
                return
        
            params_id_user = user.id
            user_coins = self.BDD.getNbCoins(params_id_user, id_serveur_discord=id_serveur_discord)
            await self.lang_pack.send_message(ctx, "user_balance", user=user.display_name, coins=user_coins)
            return
            
        
        
        user_coins = self.BDD.getNbCoins(id_user_discord=id_user_discord, id_serveur_discord=id_serveur_discord)
        await self.lang_pack.send_message(ctx, "your_balance", coins=user_coins)

    @user_context_menu(
        name="Check Balance"
    )
    async def giveCoins(self, ctx: ContextMenuContext):
        if not self.BDD.doDiscordExists(id_discord=ctx.guild_id):
            await self.lang_pack.send_message(ctx, "server_not_linked")
            return

        if not self.BDD.doUserExists(id_serveur_discord=ctx.guild_id, id_user_discord=ctx.target_id):
            await self.lang_pack.send_message(ctx, "user_not_linked")
            return
        
        balance = self.BDD.getNbCoins(ctx.target_id, ctx.guild_id)
        await self.lang_pack.send_message(ctx, "user_balance", user=ctx.target.display_name, coins=balance)


    


def setup(bot):
    Player(bot)