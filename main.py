import interactions
from dotenv import dotenv_values
from interactions.ext.wait_for import setup

config = dotenv_values(".env.local")

bot = interactions.Client(token=config["TOKEN"])
setup(bot)

@bot.event
async def on_ready():
	print(bot.me.name, "est prêt", sep=" ")
	print("Lagency : ", bot.latency, "ms", sep=" ")
	




bot.start()