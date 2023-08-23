import interactions
from interactions import Extension, slash_command, slash_option, OptionType, SlashContext, Button, ButtonStyle, listen
from interactions.api.events import Component
import mcrcon
import asyncio


class Player(Extension):
    def __init__(self, bot):
        self.bot = bot
        self.rcon_info = {
            "server_ip": "ip",
            "rcon_port": 99999,
            "rcon_password": "psw"
        }

    @slash_command(
        name="playerlist",
        description="Affiche une liste de joueurs présents sur le serveur"
    )
    async def playerlist(self, ctx: SlashContext):
        try:
            with mcrcon.MCRcon(self.rcon_info["server_ip"], self.rcon_info["rcon_password"], self.rcon_info["rcon_port"]) as rcon:
                response = rcon.command("list")
                players_list = response.split(": ")[1].split(", ")
                
                if players_list[0] == "There are 0":
                    await ctx.send("Aucun joueur n'est actuellement en ligne.")
                else:
                    players_str = "\n".join(players_list)
                    await ctx.send(f"Liste des joueurs en ligne :\n{players_str}")
        except Exception as e:
            await ctx.send("Une erreur s'est produite lors de la récupération de la liste des joueurs.")

    @slash_command(
        name="kill",
        description="Commande pour tuer un joueur"
    )
    @slash_option(
        name="target",
        description="Le joueur à tuer",
        required=True,
        opt_type=OptionType.STRING
    )
    @slash_option(
        name="reason",
        description="La raison de la mort",
        required=False,
        opt_type=OptionType.STRING
    )
    async def kill(self, ctx: SlashContext, target: str, reason: str = "Aucune raison"):
        try:
            with mcrcon.MCRcon(self.rcon_info["server_ip"], self.rcon_info["rcon_password"], self.rcon_info["rcon_port"]) as rcon:
                command = f"kill {target}"
                response = rcon.command(command)
                await ctx.send(f"Le joueur {target} a été tué. Raison : {reason}")
        except Exception as e:
            await ctx.send("Une erreur s'est produite lors de la tentative de tuer le joueur.")

    @slash_command(
        name="killdelay",
        description="Commande pour tuer un joueur avec un délai"
    )
    @slash_option(
        name="target",
        description="Le joueur à tuer",
        required=True,
        opt_type=OptionType.STRING
    )
    @slash_option(
        name="delay",
        description="Délai en secondes avant la mort",
        required=True,
        opt_type=OptionType.INTEGER
    )
    @slash_option(
        name="reason",
        description="La raison de la mort",
        required=False,
        opt_type=OptionType.STRING
    )
    async def killdelay(self, ctx: SlashContext, target: str, delay: int, reason: str = "Aucune raison"):
        try:
            with mcrcon.MCRcon(self.rcon_info["server_ip"], self.rcon_info["rcon_password"], self.rcon_info["rcon_port"]) as rcon:
                command = f"kill {target}"
                response = rcon.command(command)
                await ctx.send(f"Le joueur {target} sera tué dans {delay} secondes. Raison : {reason}")
                # Attente du délai
                await ctx.defer()
                await asyncio.sleep(delay)
                # Confirmation après le délai
                await ctx.send(f"Le joueur {target} a été tué après {delay} secondes. Raison : {reason}")
        except Exception as e:
            await ctx.send("Une erreur s'est produite lors de la tentative de tuer le joueur.")

def setup(bot):
    Player(bot)