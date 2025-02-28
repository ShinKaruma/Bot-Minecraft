import json, interactions
from interactions import SlashContext, ModalContext

class LocalisedMessages:
    def __init__(self):
        self.lang_path = "..\lang.json"

    def get_message(self, ctx: SlashContext|ModalContext , key):
        KnownLocales = ["en-US", "fr"]

        locale = ctx.locale
        if locale not in KnownLocales:
            locale = "en-US"
  
        with open('lang.json', 'r', encoding='utf-8') as f:
            lang_data = json.load(f)
        
        return lang_data.get(locale, {}).get(key, lang_data["en-US"].get(key, "Message not found"))

    async def send_message(self, ctx: SlashContext|ModalContext, key, **kwargs):
        message = self.get_message(ctx, key)
        await ctx.send(message.format(**kwargs))


