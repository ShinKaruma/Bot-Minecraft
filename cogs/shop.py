import interactions
from interactions import Embed, EmbedField, Extension, ModalContext, ShortText, slash_command, slash_option, Modal, OptionType, SlashContext, Button, ButtonStyle, listen, LocalisedName, LocalisedDesc, Permissions, slash_default_member_permission, AutocompleteContext, SlashCommandChoice
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

        if self.BDD.isServerPremium(ctx.guild_id):
            embeds += self.BDD.getShopitemsPremium()
            

        paginator = Paginator.create_from_embeds(self.bot, *embeds)

        async def buy(ctx: SlashContext):
            id_serveur_discord = ctx.guild_id
            id_user_discord = ctx.author_id

            rcon = self.BDD.getRconDiscord(id_serveur_discord)
            pseudo_minecraft = self.BDD.getPlayer(id_serveur_discord=id_serveur_discord, id_user_discord=id_user_discord)

            if not rcon.is_player_online(pseudo_minecraft):
                await rcon.lang_pack.send_message(ctx, "not_connected")
                return
            
            if self.BDD.getNbCoins(id_user_discord, id_serveur_discord) < int(paginator.pages[paginator.page_index].fields[1].value):
                await self.lang_pack.send_message(ctx, "error_coins_not_enough")
                return
            
            self.BDD.remCoins(id_user_discord, id_serveur_discord, int(paginator.pages[paginator.page_index].fields[1].value))
            if paginator.pages[paginator.page_index].fields[2].value == "X":
                rcon.giveItem(pseudo_minecraft, "minecraft:chainmail_helmet")
                rcon.giveItem(pseudo_minecraft, "minecraft:chainmail_chestplate")
                rcon.giveItem(pseudo_minecraft, "minecraft:chainmail_leggings")
                rcon.giveItem(pseudo_minecraft, "minecraft:chainmail_boots")
                rcon.giveItem(pseudo_minecraft, "minecraft:iron_sword")
            elif paginator.pages[paginator.page_index].fields[2].value == "XX":
                rcon.giveItem(pseudo_minecraft, "minecraft:cooked_beef 8")
                rcon.giveItem(pseudo_minecraft, "minecraft:compass")
                rcon.giveItem(pseudo_minecraft, "minecraft:map")
                rcon.giveItem(pseudo_minecraft, """minecraft:leather_boots{display:{Name:'["",{"text":"Speedy Boots","color":"light_purple"}]',Lore:['["",{"text":"The Boots of an adventurer, gives a small speed boost","italic":false}]']},AttributeModifiers:[{AttributeName:"generic.movement_speed",Amount:2,Slot:feet,Operation:1,UUID:[I;-125228,19374,22513,-38748],Name:1743198732460}]}""")
            elif paginator.pages[paginator.page_index].fields[2].value == "XXX":
                rcon.giveItem(pseudo_minecraft, "minecraft:iron_hoe")
                rcon.giveItem(pseudo_minecraft, "minecraft:wheat_seeds 8")
                rcon.giveItem(pseudo_minecraft, "minecraft:carrot 8")
                rcon.giveItem(pseudo_minecraft, "minecraft:potato 8")
                rcon.giveItem(pseudo_minecraft, "minecraft:cow_spawn_egg 2")
            else:
                rcon.giveItem(pseudo_minecraft, paginator.pages[paginator.page_index].fields[2].value)
                
            await self.lang_pack.send_message(ctx, "item_bought", item=paginator.pages[paginator.page_index].fields[0].value, coins=paginator.pages[paginator.page_index].fields[1].value)

            print("Button pressed",paginator.page_index+1)
            print(paginator.pages[paginator.page_index].fields[2].value)

        paginator.callback = buy
        paginator.show_callback_button = True
        paginator.timeout_interval = 30
        await paginator.send(ctx)


    @slash_command(
        name="add_item",
        description=LocalisedDesc(
            english_us="Add an item to the shop",
            french="Ajouter un item à la boutique"
        )
    )
    @slash_default_member_permission(Permissions.MANAGE_GUILD)
    async def add_item(self, ctx: SlashContext):

        if not await self.do_everything_exists(ctx):
            return
        
        if not self.BDD.isServerPremium(ctx.guild_id):
            await self.lang_pack.send_message(ctx, "server_not_premium")
            return
        
        add_item_modal = Modal(
            ShortText(label="Item name", custom_id="item_name", placeholder="64 stones"),
            ShortText(label="Item price", custom_id="item_price", placeholder="20"),
            ShortText(label="item id", custom_id="item_id", placeholder="minecraft:stone 64"),
            title="Add an item to the shop"
        )

        await ctx.send_modal(modal=add_item_modal)

        modal_ctx: ModalContext = await ctx.bot.wait_for_modal(add_item_modal)
        data = modal_ctx.responses

        print(data)
        self.BDD.addItemShop(modal_ctx, data["item_name"], data["item_price"], data["item_id"])

        await self.lang_pack.send_message(modal_ctx, "item_added")
        
        pass

    @slash_command(
        name="remove_item",
        description=LocalisedDesc(
            english_us="Remove an item from the premium shop",
            french="Retirer un item de la boutique premium"
        )
    )
    @slash_default_member_permission(Permissions.MANAGE_GUILD)
    async def remove_item(self, ctx: SlashContext):
        if not await self.do_everything_exists(ctx):
            return

        if not self.BDD.isServerPremium(ctx.guild_id):
            await self.lang_pack.send_message(ctx, "server_not_premium")
            return
            
        embeds = self.BDD.getShopitemsPremium()

        if len(embeds) == 0:
            await self.lang_pack.send_message(ctx, "no_item_premium")
            return

        paginator = Paginator.create_from_embeds(self.bot, *embeds)

        async def remove(ctx: SlashContext):
            id_serveur_discord = ctx.guild_id
            
            self.BDD.removeItemShop(paginator.pages[paginator.page_index].fields[2].value, id_serveur_discord)
            await self.lang_pack.send_message(ctx, "item_removed")

        paginator.callback = remove
        paginator.show_callback_button = True
        paginator.callback_button_emoji = "❌"
        paginator.timeout_interval = 30
        await paginator.send(ctx)

    @slash_command(
        name="add_daily",
        description=LocalisedDesc(
            english_us="Add a daily reward",
            french="Ajouter une récompense quotidienne"
        )
    )
    @slash_default_member_permission(Permissions.MANAGE_GUILD)
    async def add_daily(self, ctx: SlashContext):
        if not await self.do_everything_exists(ctx):
            return
        
        if not self.BDD.isServerPremium(ctx.guild_id):
            await self.lang_pack.send_message(ctx, "server_not_premium")
            return

        add_item_modal = Modal(
            ShortText(label="Item name", custom_id="item_name", placeholder="64 stones"),
            ShortText(label="weight", custom_id="item_weight", placeholder="20"),
            ShortText(label="item id", custom_id="item_id", placeholder="minecraft:stone 64"),
            title="Add a daily reward"
        )

        await ctx.send_modal(modal=add_item_modal)

        modal_ctx: ModalContext = await ctx.bot.wait_for_modal(add_item_modal)
        data = modal_ctx.responses

        self.BDD.addItemDaily(modal_ctx.guild_id, data["item_id"], data["item_name"], data["item_weight"])

        await self.lang_pack.send_message(modal_ctx, "daily_added")



    @slash_command(
        name="remove_daily",
        description=LocalisedDesc(
            english_us="Remove a daily reward",
            french="Retirer une récompense quotidienne"
        )
    )
    @slash_default_member_permission(Permissions.MANAGE_GUILD)
    async def remove_daily(self, ctx: SlashContext):
        embeds = []
        if not await self.do_everything_exists(ctx):
            return

        if not self.BDD.isServerPremium(ctx.guild_id):
            await self.lang_pack.send_message(ctx, "server_not_premium")
            return
        
        items = self.BDD.getDailyItemsPremium(ctx.guild_id).keys()

        if len(items) == 0:
            await self.lang_pack.send_message(ctx, "no_item_daily")
            return
        
        for item in items:
            embeds.append(Embed(title="Daily Config",
                                description="Item to remove",
                                fields=[
                                    EmbedField(name="Item name", value=item[0], inline=False),
                                    EmbedField(name="Item id", value=item[1], inline=False),
                                ]))

        paginator = Paginator.create_from_embeds(self.bot, *embeds)

        async def remove(ctx: SlashContext):
            id_serveur_discord = ctx.guild_id
            
            self.BDD.removeItemDaily(paginator.pages[paginator.page_index].fields[1].value, id_serveur_discord)
            await self.lang_pack.send_message(ctx, "item_removed_daily")

        paginator.callback = remove
        paginator.show_callback_button = True
        paginator.callback_button_emoji = "❌"
        paginator.timeout_interval = 30
        await paginator.send(ctx)

    


        


def setup(bot):
    Shop(bot)