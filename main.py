import interactions, requests, generator
from Classes.passerelle import Passerelle
from Classes.class_rcon import Rcon
from Classes.lang_pack import LocalisedMessages
from dotenv import dotenv_values
from interactions import LocalisedDesc, LocalisedName, slash_command, SlashContext, Modal, ShortText, Permissions, slash_default_member_permission, listen, ModalContext, Webhook, Button, ButtonStyle, OptionType, slash_option
from interactions.api.events import Component

config = dotenv_values(".env.local")

bot = interactions.Client(token=config["TOKEN"])
webhook = Webhook.from_url('https://discord.com/api/webhooks/1142216101883826368/gZPal68Idbj3hHU1MFJYm64H8xEli9CuTtuHfAy3NAT6gJ4YKsNMOelllzbWLyagXvRY', bot)
OTC = int
BDD = Passerelle()
lang = LocalisedMessages()

bot.load_extension("cogs.player")
bot.load_extension("cogs.shop")
bot.load_extension("interactions.ext.jurigged")

@listen()
async def on_ready():
	print(bot.user.display_name, "est prêt", sep=" ")
	print("Lagency : ", bot.latency, "ms", sep=" ")
	
@slash_command(
	name="connect",
	description=LocalisedDesc(
		english_us="Command to link a discord server to a minecraft server",
		french="Commande permettant de lier un serveur discord a un serveur minecraft",
	),
)
@slash_default_member_permission(Permissions.MANAGE_GUILD)
async def connect(ctx: SlashContext):

	if BDD.doDiscordExists(int(ctx.guild_id)):
		await lang.send_message(ctx, "already_linked")
		return
		


	#verif si id_serveur existe si oui pass
	label_ip = lang.get_message(ctx, "label_ip")
	label_rcon_password = lang.get_message(ctx, "label_rcon_password")
	label_rcon_port = lang.get_message(ctx, "label_rcon_port")
	label_title = lang.get_message(ctx, "label_title")

	formulaireConnection = Modal(
		ShortText(label=label_ip, custom_id="ip_serveur_minecraft"),
		ShortText(label=label_rcon_password, custom_id="pwd_rcon"),
		ShortText(label=label_rcon_port, custom_id="port_rcon"),

		title=label_title
	)
	await ctx.send_modal(modal=formulaireConnection)

	modal_ctx: ModalContext = await ctx.bot.wait_for_modal(formulaireConnection)

	data = modal_ctx.responses
	await lang.send_message(modal_ctx, "server_linked")

	await webhook.send("Le Serveur {} s'est bien ajoute a la liste des clients. Pour contacter le proprietaire : {}".format(ctx.guild.name, ctx.guild.get_owner().username))

	BDD.addDiscordServer(int(ctx.guild_id),data["ip_serveur_minecraft"],data["pwd_rcon"],data["port_rcon"])



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
	if BDD.doDiscordExists(ctx.guild_id) == False:
		await lang.send_message(ctx, "server_not_linked")
		return
	
	if BDD.doUserExists(int(ctx.guild_id), int(ctx.author_id)):
		await lang.send_message(ctx, "user_already_linked")
		return
	

	if BDD.isPlayerLinked(int(ctx.guild_id), pseudo_minecraft):
		await lang.send_message(ctx, "minecraft_already_linked")
		return
	
	formulaireLien = Modal(
		ShortText(label="Validation OTC", custom_id="OTC_Validation"),

		title="Validation OTC"
	)

	rcon = BDD.getRconDiscord(ctx.guild_id)
	
	await ctx.send_modal(modal=formulaireLien)
	OTC = generator.generate()

	rcon.sendOTP(ctx, pseudo=pseudo_minecraft, OTP=OTC)

	modal_ctx: ModalContext = await ctx.bot.wait_for_modal(formulaireLien)


	if OTC == modal_ctx.responses["OTC_Validation"]:
		await lang.send_message(modal_ctx, "otc_validation")
		await webhook.send("Le joueur {} s'est lie avec le pseudo {}, pour le serveur {}".format(ctx.author.username, pseudo_minecraft, ctx.guild.name))
		
		BDD.addPlayer(ctx.guild_id, ctx.author_id, pseudo_minecraft)

		

bot.start()