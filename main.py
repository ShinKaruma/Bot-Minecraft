import interactions, requests
from dotenv import dotenv_values
from interactions import slash_command, SlashContext, Modal, ShortText, Permissions, slash_default_member_permission, listen, ModalContext, Webhook

config = dotenv_values(".env.local")

bot = interactions.Client(token=config["TOKEN"])

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
	formulaireConnection = Modal(
		ShortText(label="IP du serveur Minecraft", custom_id="ip_serveur_minecraft"),
		ShortText(label="Mot de passe du RCON du serveur", custom_id="pwd_rcon"),
		ShortText(label="Port RCON du serveur minecraft", custom_id="port_rcon"),

		title="Formulaire de connection",
		custom_id="form_connection"
	)
	await ctx.send_modal(modal=formulaireConnection)

	modal_ctx: ModalContext = await ctx.bot.wait_for_modal(formulaireConnection)

	print(modal_ctx.responses)
	await modal_ctx.send("Vous avez bien lie vos serveurs", ephemeral=True)

	webhook = Webhook.from_url('https://discord.com/api/webhooks/1142216101883826368/gZPal68Idbj3hHU1MFJYm64H8xEli9CuTtuHfAy3NAT6gJ4YKsNMOelllzbWLyagXvRY', bot)
	await webhook.send("Le Serveur {} s'est bien ajoute a la liste des clients. Pour contacter le proprietaire : {}".format(ctx.guild.name, ctx.guild.get_owner().username))


bot.start()