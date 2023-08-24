import interactions
from interactions import Extension, slash_command, slash_option, OptionType, SlashContext, Button, ButtonStyle, listen, Permissions, slash_default_member_permission, AutocompleteContext
from interactions.api.events import Component
import mcrcon
import asyncio


class Player(Extension):
    def __init__(self, bot):
        self.bot = bot
        self.rcon_info = {
            "server_ip": "127.0.0.1",
            "rcon_port": 25575,
            "rcon_password": "azerty1234"
        }

    async def get_online_players(self):
        try:
            with mcrcon.MCRcon(self.rcon_info["server_ip"], self.rcon_info["rcon_password"], self.rcon_info["rcon_port"]) as rcon:
                response = rcon.command("list")
                players_list = response.split(": ")[1].split(", ")
                return players_list
        except Exception as e:
            players_list="There are 0"
            return players_list

    async def is_player_online(self, player_name):
        online_players = await self.get_online_players()
        return player_name in online_players

    @slash_command(
        name="playerlist",
        description="Affiche une liste de joueurs présents sur le serveur"
    )
    async def playerlist(self, ctx: SlashContext):
        try:
            with mcrcon.MCRcon(self.rcon_info["server_ip"], self.rcon_info["rcon_password"], self.rcon_info["rcon_port"]) as rcon:
                response = rcon.command("list")
                players_list = await self.get_online_players()
                if players_list[0] == "There are 0":
                    await ctx.send("Aucun joueur n'est actuellement en ligne.")
                else:
                    players_str = "\n".join(players_list)
                    await ctx.send(f"Liste des joueurs en ligne :\n{players_str}")
        except Exception as e:
            await ctx.send(e)
            # await ctx.send("Une erreur s'est produite lors de la récupération de la liste des joueurs.")

    @slash_command(
        name="kill",
        description="Commande pour tuer un joueur"
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
        try:
            if await self.is_player_online(target):
                with mcrcon.MCRcon(self.rcon_info["server_ip"], self.rcon_info["rcon_password"], self.rcon_info["rcon_port"]) as rcon:
                    command = f"kill {target}"
                    response = rcon.command(command)
                    await ctx.send(f"Le joueur `{target}` a été tué. Raison : `{reason}`")
            else:
                await ctx.send(f"Le joueur `{target}` n'est pas en ligne.")
        except Exception as e:
            await ctx.send("Une erreur s'est produite lors de la tentative de tuer le joueur.")
    
    #AutoComplete des joueurs online
    @kill.autocomplete("target")
    async def autocomplete_target(self, ctx: AutocompleteContext):
        string_option_input = ctx.input_text
        online_players = await self.get_online_players()
        choices = [
            {"name": player, "value": player} for player in online_players if player.startswith(string_option_input)
        ]
        await ctx.send(choices=choices)
    
    @slash_command(
        name="tp_joueur",
        description="Téléporter joueur vers un autre joueur"
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
    async def tp_joueur(self, ctx: SlashContext, joueur1: str, joueur2: str):
        try:
            if await self.is_player_online(joueur1):
                if await self.is_player_online(joueur2):
                    with mcrcon.MCRcon(self.rcon_info["server_ip"], self.rcon_info["rcon_password"], self.rcon_info["rcon_port"]) as rcon:
                        command = f"tp {joueur1} {joueur2}"
                        response = rcon.command(command)
                        await ctx.send(f"Le joueur `{joueur1}` a été téléporté vers `{joueur2}`.")
                else:
                    await ctx.send(f"Le joueur `{joueur2}` n'est pas en ligne.")
            else:
                await ctx.send(f"Le joueur `{joueur1}` n'est pas en ligne.")
        except Exception as e:
            await ctx.send("Une erreur s'est produite lors de la tentative de téléportation.")
    
    #AutoComplete des joueurs online
    @tp_joueur.autocomplete("joueur1")
    async def autocomplete_joueur1(self, ctx: AutocompleteContext):
        string_option_input = ctx.input_text
        online_players = await self.get_online_players()
        choices = [
            {"name": player, "value": player} for player in online_players if player.startswith(string_option_input)
        ]
        await ctx.send(choices=choices)
    
    @tp_joueur.autocomplete("joueur2")
    async def autocomplete_joueur2(self, ctx: AutocompleteContext):
        string_option_input = ctx.input_text
        online_players = await self.get_online_players()
        choices = [
            {"name": player, "value": player} for player in online_players if player.startswith(string_option_input)
        ]
        await ctx.send(choices=choices)


    @slash_command(
        name="tp_coord",
        description="Téléporter joueur vers des coordonnées"
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
    async def tp_coord(self, ctx: SlashContext, joueur: str, coordonnees: str):
        try:
            if await self.is_player_online(joueur):
                with mcrcon.MCRcon(self.rcon_info["server_ip"], self.rcon_info["rcon_password"], self.rcon_info["rcon_port"]) as rcon:
                    command = f"tp {joueur} {coordonnees}"
                    response = rcon.command(command)
                    await ctx.send(f"Le joueur `{joueur}` a été téléporté vers `{coordonnees}`.")
            else:
                await ctx.send(f"Le joueur `{joueur}` n'est pas en ligne.")
        except Exception as e:
            await ctx.send("Une erreur s'est produite lors de la tentative de téléportation.")
    
    #AutoComplete des joueurs online
    @tp_coord.autocomplete("joueur")
    async def autocomplete_joueur(self, ctx: AutocompleteContext):
        string_option_input = ctx.input_text
        online_players = await self.get_online_players()
        choices = [
            {"name": player, "value": player} for player in online_players if player.startswith(string_option_input)
        ]
        await ctx.send(choices=choices)



def setup(bot):
    Player(bot)