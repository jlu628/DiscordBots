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
    pass


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
    user_searches[ctx.author] = matches
    msg = "Search result UWU:\n"
    for i in range(len(matches)):
        msg += f"{str(i+1)}. {matches[i][1]}\n"
    await ctx.send(msg)


def get_matches(keywords):
    matches = []
    for file_name in file_name_list:
        word_list = re.split('[()\[\],./，。、/\\`_（）（）「」?？！!？！~\-=\"" "]', file_name)
        word_list = list(filter(lambda a: ((a != "") and ("mp3" not in a)), word_list))
        match_score = longest_common_sequence_word(keywords, word_list)
        if match_score > 0:
            matches.append((match_score, file_name))

    matches = sorted(matches, key=lambda a: a[0], reverse=True)
    return matches


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
