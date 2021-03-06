from base64 import decode
from chardet import detect
import discord
from discord.ext import commands
from protected import token, API_key
from deep_translator import GoogleTranslator, single_detection
from languages import lang_to_code, code_to_lang, detect_only, detect_to_translator

client = commands.Bot(command_prefix="::")
sent_langlists = {}

@client.command()
async def transl(ctx: discord.ext.commands.context.Context, *args):
    # Sanity check
    if len(args) < 2:
        await ctx.send("Wrong request format. Use ::help for more info.")
        return

    lan1 = args[0]
    lan2 = args[1]

    if len(args) == 2 and lan1 in code_to_lang.keys() and lan2 in code_to_lang.keys():
        await ctx.send("Wrong request format. Use ::help for more info.")
        return

    if lan1 not in code_to_lang.keys():
        await ctx.send(f"{lan1} is not identified as a valid language code, use ::langlist to see a list of language codes.")
        return

    # process message
    raw_message = ctx.message.content
    if lan2 in code_to_lang.keys():
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
        detected_lang = single_detection(text, api_key=API_key)

        if detected_lang in detect_only:
            await ctx.send(f"Detected source language is {detect_only[detected_lang]}, which is currently not supported by the translator. Use ::langlist to see all supported langauages.")
            return
        elif detected_lang in detect_to_translator:
            detected_lang = detect_to_translator[detected_lang]

        translated = GoogleTranslator(source=detected_lang, target=lan1).translate(text=text)
        await ctx.send(f"No source language provided, detected language is {code_to_lang[detected_lang]}:\n" + translated)


@client.command()
async def detectlang(ctx: discord.ext.commands.context.Context):
    raw_message = ctx.message.content
    text = raw_message[raw_message.index("::detectlang") + len("::detectlang"):]
    detected_code = single_detection(text, api_key=API_key)

    msg = "Detected language: "
    if detected_code in code_to_lang.keys():
        msg += code_to_lang[detected_code]
    elif detected_code in detect_to_translator.keys():
        msg += code_to_lang[detect_to_translator[detected_code]]
    else:
        msg += detect_only[detected_code]
        msg += "\nNote: the translator does not currently support this language, it can only be detected."
    await ctx.send(msg)


@client.command()
async def langlist(ctx: discord.ext.commands.context.Context):
    msg = ""
    for k,v in code_to_lang.items():
        msg += f"{v}: {k}\n"
    sent = await ctx.send(msg)

    sent_langlists[(ctx.author.name, ctx.author.discriminator)] = sent


@client.command()
async def hidelanglist(ctx: discord.ext.commands.context.Context):
    if (ctx.author.name, ctx.author.discriminator) not in sent_langlists.keys():
        return

    await sent_langlists[(ctx.author.name, ctx.author.discriminator)].delete()
    del sent_langlists[(ctx.author.name, ctx.author.discriminator)]


@client.command()
async def lookup(ctx: discord.ext.commands.context.Context, *args):
    if len(args) < 1:
        await ctx.send("Wrong request format. Use ::help for more info.")
        return

    msg = ""
    unfound = []
    for target_lang in args:
        if target_lang.lower() in lang_to_code:
            msg += f"{target_lang}: {lang_to_code[target_lang.lower()]}\n"
        elif target_lang.lower().includes("chinese"):
            msg += "Chinese (Simplified): zh-CN\nChinese (Traditional): zh-TW"
        else:
            unfound.append(target_lang)

    if unfound:
        msg += f"The following languages are not found: {', '.join(unfound)}"

    await ctx.send(msg)


client.remove_command("help")
@client.command()
async def help(ctx: discord.ext.commands.context.Context):
    doc = """
    This bot allows you to translate discord messages with google translator. List of helpful commands:

            **::transl [src lang(optional)] [dest lang] [text]**
                    ??? Source language and destination language must be language codes (see ::langlist for details).
                    ??? If source language is not provided, the translator auto detects language for you.

            **::langlist**
                    ??? Displays a list of language map into abbreviations (codes).

            **::hidelanglist**
                    ??? Hide the most recently langlist asked by the current user.

            **::lookup [lang1] [lang2] ...**
                    ??? Display a mapping of specified languages into their language abbreviations (codes).
                    
            **::detectlang [text]**
                    ??? Detects the language of of provided text.

?? Copyright 2022 jlu@gatech
    """
    await ctx.send(doc)


client.run(token)