import discord
from discord.ext import commands
import difflib
import argparse
import os
import re

client = commands.Bot(command_prefix="\\")

src_folder = None
file_path_list = []
file_name_list = []
user_searches = {}


@client.command()
async def play(ctx, *args):
    if not args:
        msg = "Usage"
        await ctx.send(msg)
        return

    if len(args) > 1 or not str.isdecimal(args[0]):
        await search(ctx, *args)
        return


@client.command()
async def join(ctx: discord.ext.commands.context.Context):
    if str(ctx.channel) != "bot-command":
        return
    channel = ctx.author.voice.channel
    if not channel:
        await ctx.send("You are not currently in a voice channel.")
        return

    if ctx.voice_client:
        if ctx.voice_client.channel == channel:
            return
        else:
            await ctx.voice_client.move_to(channel)
    else:
        await channel.connect()


@client.command()
async def leave(ctx: discord.ext.commands.context.Context):
    if str(ctx.channel) != "bot-command":
        return

    if ctx.voice_client:
        await ctx.voice_client.disconnect()


@client.command()
async def search(ctx: discord.ext.commands.context.Context, *args):
    if str(ctx.channel) != "bot-command":
        return

    matches = get_matches(args)
    if not matches:
        await ctx.send("No results found QAQ")
        return

    # To do: separate search results in pages
    msg = "Search result UWU:\n"
    for i in range(min(len(matches), 5)):
        msg += f"{str(i+1)}. {matches[i]}\n"

    if len(matches) > 5:
        msg += "\nUse \\prev or \\next command to flip page, or \\all to show all matches."
        msg += "\nUse \\play <#> command to play a song."
    sent = await ctx.send(msg)
    user_searches[(ctx.author.name, ctx.author.discriminator)] = \
        {"matches": matches, "page": 1, "message": sent, "display_all": False}


def get_matches(keywords):
    matches = []
    for file_name in file_name_list:
        word_list = re.split('[()\[\],./，。、/\\`_（）（）「」?？！!？！~\-=\"" "]', file_name)
        word_list = list(filter(lambda a: ((a != "") and ("mp3" not in a)), word_list))
        match_score = longest_common_sequence_word(keywords, word_list)
        if match_score > 0:
            matches.append((match_score, file_name))

    matches = sorted(matches, key=lambda a: a[0], reverse=True)

    return [match[1] for match in matches]


def longest_common_sequence_word(word_list1, word_list2):
    if not word_list1 or not word_list2:
        return 0
    elif len(word_list1) == 1:
        return 1 if word_list1[0] in word_list2 else 0
    elif len(word_list2) == 1:
        return 1 if word_list2[0] in word_list1 else 0

    m = len(word_list1)
    n = len(word_list2)
    table = [[0] * (n+1)] * (m + 1)
    for i in range(1, m+1):
        for j in range(1, n+1):
            if word_list1[i - 1] == word_list2[j - 1]:
                table[i][j] = table[i-1][j-1] + 1
            else:
                table[i][j] = max(table[i-1][j], table[i][j-1])

    return table[m][n]


@client.command("next")
async def next_page(ctx: discord.ext.commands.context.Context):
    if (ctx.author.name, ctx.author.discriminator) not in user_searches.keys():
        msg = "Usage:\nThe \\next command can only be used when displaying matching song list.\n" \
              "Please use \\search <song name> to display a list of matching songs first to activate this command."
        await ctx.send(msg)
        return

    user_search = user_searches[(ctx.author.name, ctx.author.discriminator)]
    matches = user_search["matches"]
    page = user_search["page"]
    message = user_search["message"]
    display_all = user_search["display_all"]

    if display_all or page * 5 >= len(matches):
        return

    msg = "Search result UWU:\n"
    for i in range(page*5, (page+1)*5):
        if i >= len(matches):
            break
        msg += f"{str(i+1)}. {matches[i]}\n"

    msg += "\nUse \\prev or \\next command to flip page, or \\all to show all matches."
    msg += "\nUse \\play <#> command to play a song."

    await message.edit(content=msg)
    user_searches[(ctx.author.name, ctx.author.discriminator)]["page"] += 1


@client.command("prev")
async def prev_page(ctx: discord.ext.commands.context.Context):
    if (ctx.author.name, ctx.author.discriminator) not in user_searches.keys():
        msg = "Usage:\nThe \\prev command can only be used when displaying matching song list.\n" \
              "Please use \\search <song name> to display a list of matching songs first to activate this command."
        await ctx.send(msg)
        return

    user_search = user_searches[(ctx.author.name, ctx.author.discriminator)]
    matches = user_search["matches"]
    page = user_search["page"]
    message = user_search["message"]
    display_all = user_search["display_all"]

    if display_all or page == 1:
        return

    msg = "Search result UWU:\n"
    for i in range((page-2)*5, (page-1)*5):
        if i >= len(matches):
            break
        msg += f"{str(i+1)}. {matches[i]}\n"

    msg += "\nUse \\prev or \\next command to flip page, or \\all to show all matches."
    msg += "\nUse \\play <#> command to play a song."

    await message.edit(content=msg)
    user_searches[(ctx.author.name, ctx.author.discriminator)]["page"] -= 1


@client.command("all")
async def show_all(ctx: discord.ext.commands.context.Context):
    if (ctx.author.name, ctx.author.discriminator) not in user_searches.keys():
        msg = "Usage:\nThe \\all command can only be used when displaying matching song list.\n" \
              "Please use \\search <song name> to display a list of matching songs first to activate this command."
        await ctx.send(msg)
        return

    user_search = user_searches[(ctx.author.name, ctx.author.discriminator)]
    matches = user_search["matches"]
    message = user_search["message"]
    display_all = user_search["display_all"]

    if display_all:
        return

    msg = "Search result UWU:\n"
    for i in range(len(matches)):
        msg += f"{str(i+1)}. {matches[i]}\n"

    msg += "\nUse \\play <#> command to play a song."

    await message.edit(content=msg)
    user_searches[(ctx.author.name, ctx.author.discriminator)]["display_all"] = True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Specify the source folder location containing music files.")
    parser.add_argument("-src", nargs=1, default=["C:/Users/Jerry/Music"], type=str,
                        help="source file containing music files", metavar="source file location")
    src_folder = parser.parse_args().src[0]
    if not os.path.isdir(src_folder):
        parser.print_help()
        print('\nError: cannot find folder ' + src_folder)

    for root, dirs, files in os.walk(src_folder):
        for file in files:
            if file.endswith(".mp3"):
                file_path_list.append(os.path.join(root, file))
                if file not in file_name_list:
                    file_name_list.append(file)


    client.run("ODE5MTcxMjQyOTc1NDI4NjI4.YEiuqw.X-0est4jXEphoOH3o-YdGMxtF70")
