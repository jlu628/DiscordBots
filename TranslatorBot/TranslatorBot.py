from tkinter import Label
import discord
from discord.ext import commands
from protected import token
from deep_translator import GoogleTranslator

langs = GoogleTranslator.get_supported_languages(as_dict=True)
langs = {v: k for k, v in langs.items()}
client = commands.Bot(command_prefix="::")

@client.command()
async def transl(ctx: discord.ext.commands.context.Context, *args):
    # Sanity check
    if len(args) < 2:
        await ctx.send("Wrong request format. Use ::help for more info.")
        return

    lan1 = args[0]
    lan2 = args[1]

    if len(args) == 2 and lan1 in langs.keys() and lan2 in langs.keys():
        await ctx.send("Wrong request format. Use ::help for more info.")
        return

    if lan1 not in langs.keys():
        await ctx.send(f"{lan1} is not identified as a valid language code, use ::langlist to see a list of language codes.")
        return

    # process message
    raw_message = ctx.message.content
    if lan2 in langs.keys():
        # both origin and dst are know
        if lan1 == lan2:
            translated = raw_message[raw_message.index(lan1) + len(lan1):]
            translated = translated[translated.index(lan1) + len(lan1):]
            await ctx.send(translated)
            return

        text = raw_message[raw_message.index(lan2) + len(lan2):]
        translated = GoogleTranslator(source=lan1, target=lan2).translate(text=text)
        await ctx.send(translated)
    else:
        # only dest language is given
        text = raw_message[raw_message.index(lan1) + len(lan1):]
        translated = GoogleTranslator(source=detected, target=lan1).translate(text=text)
        await ctx.send(translated)

client.run(token)