import interactions, requests, generator, os
from dotenv import dotenv_values
from interactions import slash_command, SlashContext, Modal, ShortText, Permissions, slash_default_member_permission, listen, ModalContext, Webhook, Button, ButtonStyle, OptionType, slash_option
from interactions.api.events import Component

config = dotenv_values(".env.local")

bot = interactions.Client(token=config["TOKEN"])
webhook = Webhook.from_url('https://discord.com/api/webhooks/1142216101883826368/gZPal68Idbj3hHU1MFJYm64H8xEli9CuTtuHfAy3NAT6gJ4YKsNMOelllzbWLyagXvRY', bot)
OTC = int


#Information du rcon
rcon_info = {
    "server_ip": "ip",
    "rcon_port": 99999,
    "rcon_password": "psw"
}

bot.load_extension("cogs.player")

@listen()
async def on_ready():
	print(bot.user.display_name, "est prêt", sep=" ")
	print("Lagency : ", bot.latency, "ms", sep=" ")
	
@slash_command(
	name="connect",
	description="Commande permettant de lier un serveur discord a un serveur minecraft",
)
@slash_default_member_permission(Permissions.MANAGE_GUILD)
async def connect(ctx: SlashContext):

	#verif si id_serveur existe si oui pass

	formulaireConnection = Modal(
		ShortText(label="IP du serveur Minecraft", custom_id="ip_serveur_minecraft"),
		ShortText(label="Mot de passe du RCON du serveur", custom_id="pwd_rcon"),
		ShortText(label="Port RCON du serveur minecraft", custom_id="port_rcon"),

		title="Formulaire de connection"
	)
	await ctx.send_modal(modal=formulaireConnection)

	modal_ctx: ModalContext = await ctx.bot.wait_for_modal(formulaireConnection)

	print(modal_ctx.responses)
	await modal_ctx.send("Vous avez bien lie vos serveurs", ephemeral=True)

	await webhook.send("Le Serveur {} s'est bien ajoute a la liste des clients. Pour contacter le proprietaire : {}".format(ctx.guild.name, ctx.guild.get_owner().username))

	#ajout du serveur dans la bdd



@slash_command(
	name="link",
	description="Commande permettant de lier son compte discord au serveur minecraft du discord"
)
@slash_option(
	name="pseudo_minecraft",
	description="Pseudo Minecraft a lier au compte",
	required=True,
	opt_type=OptionType.STRING
)
async def link(ctx: SlashContext, pseudo_minecraft: str):

	#Verif dans bdd si existant pass

	formulaireLien = Modal(
		ShortText(label="Validation OTC", custom_id="OTC_Validation"),

		title="Validation OTC"
	)
	print(pseudo_minecraft)

	await ctx.send_modal(modal=formulaireLien)
	OTC = generator.generate()
	print(OTC)

	modal_ctx: ModalContext = await ctx.bot.wait_for_modal(formulaireLien)
	print(modal_ctx.responses)


	if OTC == modal_ctx.responses["OTC_Validation"]:
		await modal_ctx.send("Vous venez de lier votre compte discord et compte Minecraft, felicitation", ephemeral=True)
		await webhook.send("Le joueur {} s'est lie avec le pseudo {}, pour le serveur {}".format(ctx.author.username, pseudo_minecraft, ctx.guild.name))
		#ajout dans bdd


bot.start()