import json, interactions
from interactions import SlashContext

class LocalisedMessages:
    def __init__(self, bot: interactions.Client):
        self.bot = bot
        self.lang_path = "..\lang.json"

    def get_message(self, ctx: SlashContext, key):
        locale = ctx.locale
  
        with open('lang.json', 'r', encoding='utf-8') as f:
            lang_data = json.load(f)
        
        return lang_data.get(locale, {}).get(key, lang_data["en-US"].get(key, "Message not found"))

    async def send_message(self, ctx: SlashContext, key, **kwargs):
        message = self.get_message(ctx, key)
        await ctx.send(message.format(**kwargs), ephemeral=True)


