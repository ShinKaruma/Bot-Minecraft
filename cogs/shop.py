import interactions
from interactions import Embed, Extension, slash_command, slash_option, OptionType, SlashContext, Button, ButtonStyle, listen, LocalisedName, LocalisedDesc, Permissions, slash_default_member_permission, AutocompleteContext, SlashCommandChoice
from interactions.api.events import Component
from interactions.ext.paginators import Paginator
from Classes.passerelle import Passerelle
from Classes.class_rcon import Rcon
from Classes.lang_pack import LocalisedMessages


class Shop(Extension):
    def __init__(self, bot):
        self.bot = bot
        self.BDD = Passerelle()
        self.lang_pack = LocalisedMessages()

    async def do_everything_exists(self, ctx: SlashContext):
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

###### Moderation commands ######

    @slash_command(
        name="give_coins", 
        description=LocalisedDesc(
            english_us="Give coins to a user",
            french="Donner des coins à un utilisateur"
        )
    )
    @slash_option(
        name="user",
        description=LocalisedDesc(
            english_us="The user to give coins to",
            french="L'utilisateur à qui donner des coins"
        ),
        required=True,
        opt_type=OptionType.USER
    )
    @slash_option(
        name=LocalisedName(
            english_us="amount",
            french="montant"
        ),
        description=LocalisedDesc(
            english_us="The amount of coins to give",
            french="Le montant de coins à donner"
        ),
        required=True,
        opt_type=OptionType.INTEGER
    )
    @slash_default_member_permission(Permissions.MODERATE_MEMBERS)
    async def give_coins(self, ctx: SlashContext, user, amount):

        if not self.BDD.doDiscordExists(id_discord=ctx.guild_id):
            await self.lang_pack.send_message(ctx, "server_not_linked")
            return
        
        if not self.BDD.doUserExists(id_serveur_discord=ctx.guild_id, id_user_discord=user.id):
            await self.lang_pack.send_message(ctx, "user_not_linked")
            return
        
        if amount < 0:
            await self.lang_pack.send_message(ctx, "error_coin_amount")
            return

        self.BDD.addCoins(user.id, ctx.guild_id, amount)
        await self.lang_pack.send_message(ctx, "coins_added", player=user.mention, coins=amount)

    
    @slash_command(
        name="remove_coins", 
        description=LocalisedDesc(
            english_us="Give coins to a user",
            french="Donner des coins à un utilisateur"
        )
    )
    @slash_option(
        name="user",
        description=LocalisedDesc(
            english_us="The user to remove coins to",
            french="L'utilisateur à qui retirer des coins"
        ),
        required=True,
        opt_type=OptionType.USER
    )
    @slash_option(
        name=LocalisedName(
            english_us="amount",
            french="montant"
        ),
        description=LocalisedDesc(
            english_us="The amount of coins to remove",
            french="Le montant de coins à retirer"
        ),
        required=True,
        opt_type=OptionType.INTEGER
    )
    @slash_default_member_permission(Permissions.MODERATE_MEMBERS)
    async def remove_coins(self, ctx: SlashContext, user, amount):

        if not self.BDD.doDiscordExists(id_discord=ctx.guild_id):
            await self.lang_pack.send_message(ctx, "server_not_linked")
            return
        
        if not self.BDD.doUserExists(id_serveur_discord=ctx.guild_id, id_user_discord=user.id):
            await self.lang_pack.send_message(ctx, "user_not_linked")
            return
        
        if amount < 0:
            await self.lang_pack.send_message(ctx, "error_coin_amount")
            return

        self.BDD.removeCoins(user.id, ctx.guild_id, amount)
        await self.lang_pack.send_message(ctx, "coins_removed", player=user.mention, coins=amount)



###### users commands ######

    @slash_command(
        name="pay",
        description=LocalisedDesc(
            english_us="Pay another player",
            french="Payer un autre joueur"
        )
    )
    @slash_option(
        name="player",
        description=LocalisedDesc(
            english_us="The player to pay",
            french="Le joueur à payer"
        ),
        required=True,
        opt_type=OptionType.USER
    )
    @slash_option(
        name=LocalisedName(
            english_us="amount",
            french="montant"
        ),
        description=LocalisedDesc(
            english_us="The amount of coins to pay",
            french="Le montant de coins à payer"
        ),
        required=True,
        opt_type=OptionType.INTEGER
    )
    async def pay(self, ctx: SlashContext, player, amount):

        if not self.do_everything_exists(ctx):
            return

        if amount < 0:
            await self.lang_pack.send_message(ctx, "error_coin_amount")
            return

        if self.BDD.getNbCoins(ctx.author_id, ctx.guild_id) < amount:
            await self.lang_pack.send_message(ctx, "not_enough_coins")
            return

        self.BDD.remCoins(ctx.author_id, ctx.guild_id, amount)
        self.BDD.addCoins(player.id, ctx.guild_id, amount)
        await self.lang_pack.send_message(ctx, "coins_paid", player=player.mention, coins=amount)

    

    @slash_command(
        name="shop",
        description=LocalisedDesc(
            english_us="Access the shop",
            french="Accéder à la boutique"
        )
    )
    async def shop(self, ctx: SlashContext):
        if not self.do_everything_exists(ctx):
            return
        
        embeds = self.BDD.getShopItems()

        # if self.BDD.isServerPremium(ctx.guild_id):
        #     embeds += self.BDD.getShopitemsPremium()

        paginator = Paginator.create_from_embeds(self.bot, *embeds)

        async def buy(ctx):
            print("Button pressed",paginator.page_index+1)

        paginator.callback = buy
        paginator.callback_button_emoji = "🪙"
        paginator.show_callback_button = True
        paginator.timeout_interval = 30
        await paginator.send(ctx)

    


        


def setup(bot):
    Shop(bot)