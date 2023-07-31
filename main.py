import os
import datetime
import discord
import typing
import asyncio
from discord.ext import commands, tasks
from discord import app_commands, Embed, Interaction
from functions import random_date, get_apod, add_channel, del_inactive, get_channels_apod, get_channels_iotd, get_toppick, get_iotd, del_channel, channel_exists, channel_val


intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, activity=discord.Activity(type=discord.ActivityType.watching, name='the stars'))
bot.remove_command('help')
#guild = discord.Object(id=)
post_time = datetime.time(hour=2, minute=0 ) #UTC TIME, 8am MST

#----------------------------------------------------------------------------------------------------------------------#
#BOT COMMANDS
#----------------------------------------------------------------------------------------------------------------------#

@bot.event
async def on_ready():
    bot.tree.clear_commands()
    synced = await bot.tree.sync()  #use guild=guild parameter to reset
    print("Synced " + str(len(synced)) + " commands\nBot ready")
    send_daily.start()



@bot.tree.command(name="help", description="Learn more about the bot")
async def help(interaction: Interaction):
    embed = Embed(color=discord.Color.red(), title="This is a title")
    embed.set_author(name='HELP')
    embed.add_field(name='schedule/unschedule', value='Posts a random APOD from anytime between present and 1996', inline=False)
    embed.add_field(name='apod', value="Posts NASA's Astronomy Picture of the Day", inline=False)
    embed.add_field(name='iotd', value="Posts AstroBin's Image of the Day", inline=False)
    embed.set_footer(text='Created by Max M')
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="schedule", description="Enable automated daily posts for text channels")
@app_commands.describe(channel="Choose a channel to add to registry")
@app_commands.describe(choice="Choose which posts you would like to be scheduled")
async def schedule(interaction: Interaction, channel: discord.TextChannel, choice: typing.Literal["AstroBin's Image of the Day", "NASA's Astronomy Picture of the Day"]):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You must have admin permissions to use this command", ephemeral=True)
    else:
        channel_id = channel.id
        if choice == "NASA's Astronomy Picture of the Day":
            result = add_channel(channel_id, 'apod')
        else:
            result = add_channel(channel_id, 'iotd')
        await interaction.response.send_message("Channel **{}** will now receive {} posts".format(str(channel), choice), ephemeral=True)


@bot.tree.command(name="unschedule", description="Disable automated daily posts for text channels")
@app_commands.describe(channel="Choose a channel to remove from registry")
@app_commands.describe(choice="Choose which posts you would like to be unscheduled")
async def unschedule(interaction: Interaction, channel: discord.TextChannel, choice: typing.Literal["AstroBin's Image of the Day", "NASA's Astronomy Picture of the Day"]):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You must have admin permissions to use this command", ephemeral=True)
    else:
        channel_id = channel.id
        if choice == "NASA's Astronomy Picture of the Day":
            result = del_channel(channel_id, 'apod')
        else:
            result = del_channel(channel_id, 'iotd')

        if result == 0:
            await interaction.response.send_message("Channel **{}** was not found in the registry".format(str(channel)), ephemeral=True)
        else:
            await interaction.response.send_message("Channel **{}** will no longer receive {} posts".format(str(channel), choice), ephemeral=True)


@bot.tree.command(name="apod_date", description="Get the APOD from a given date (ie. YYYY-MM-DD)")
@app_commands.describe(date="YYYY-MM-DD")
async def apod_date(interaction: Interaction, date: str):
    try:
        response = get_apod(date)
        embed = response[0]
        link = response[1]
        if len(response) == 2:
            await interaction.response.send_message(embed=embed)
            await interaction.response.send_message(link)
        else:
            await interaction.response.send_message(embed=embed)

    except:
        await interaction.response.send_message("APOD not found, ensure date is valid (ie. YYYY-MM-DD)", ephemeral=True)


@bot.tree.command(name="apod_random", description="Get the APOD from a random date")
async def apod_random(interaction: Interaction):
    day = random_date()
    response = get_apod(day)
    embed = response[0]
    link = response[1]
    if len(response) == 2:
        await interaction.response.send_message(embed=embed)
        await interaction.response.send_message(link)
    else:
        await interaction.response.send_message(embed=embed)


@bot.tree.command(name="apod", description="Get today's Astronomy Picture of the Day from NASA")
async def apod(interaction: Interaction):
    response = get_apod(None)
    embed = response[0]
    link = response[1]
    if len(response) == 2:
        await interaction.response.send_message(embed=embed)
        await interaction.response.send_message(link)
    else:
        await interaction.response.send_message(embed=embed)


@bot.tree.command(name="iotd", description="Get today's Image of the day from AstroBin")
async def iotd(interaction: Interaction):
    await interaction.response.send_message(embed=get_iotd())


@bot.tree.command(name='toppick', description="Get a random selection from AstroBin's latest top picks")
async def toppick(interaction: Interaction):
    await interaction.response.defer()
    embed = get_toppick()
    await asyncio.sleep(1)
    await interaction.followup.send(embed=embed)





@tasks.loop(time=post_time)
async def send_daily():
    sent_apod = 0
    sent_iotd = 0

    response = get_apod(None)
    embed = response[0]
    link = response[1]
    for id in get_channels_apod():
        channel = bot.get_channel(id)
        try:
            if len(response) == 2:
                await channel.send(embed=embed)
                await channel.send(link)
            else:
                await channel.send(embed=embed)
            sent_apod += 1
        except:
            pass

    embed = get_iotd()
    for id in get_channels_iotd():
        channel = bot.get_channel(id)
        try:
            await channel.send(embed=embed)
            sent_iotd += 1
        except:
            pass

    del_inactive()
    print("APOD sent to {} channels".format(str(sent_apod)))
    print("IOTD sent to {} channels".format(str(sent_iotd)))



#----------------------------------------------------------------------------------------------------------------------#

bot.run(os.environ["TOKEN"])

#----------------------------------------------------------------------------------------------------------------------#
