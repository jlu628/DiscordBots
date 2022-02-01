import discord
from discord.ext import commands
from protected import token

client = commands.Bot(command_prefix="!")
is_on = True


@client.event
async def on_message(message):
    if message.author.name == "Reverse String Bot":
        return

    global is_on
    if message.channel.name == "bot-command" and message.content == "reverse on":
        is_on = True
        await client.change_presence(status=discord.Status.online)
        await message.channel.send("Reverse String Bot turned on")
        return
    if message.channel.name == "bot-command" and message.content == "reverse off":
        is_on = False
        await client.change_presence(status=discord.Status.idle)
        await message.channel.send("Reverse String Bot turned off")
        return
    
    if message.channel.name == "bot-command":
        return

    if is_on:
        await message.channel.send(message.content[::-1])

client.run(token)