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
    if str(ctx.channel) != "bot-command":
        return

    if not args or (ctx.author.name, ctx.author.discriminator) not in user_searches.keys():
        msg = "Usage (๑ `▽´๑) :\n" \
              "\\play <#> select a song from search result list to play." \
              "This command is only activated after \\search.\n" \
              "\\play <keywords> - equivalent to the \\search command."
        await ctx.send(msg)
        return

    if len(args) > 1 or not str.isdecimal(args[0]):
        await search(ctx, *args)
        return

    song_num = int(args[0])

    user_search = user_searches[(ctx.author.name, ctx.author.discriminator)]
    matches = user_search["matches"]
    message = user_search["message"]

    if song_num > len(matches):
        msg = f"Only {str(len(matches))} songs found. Number must be within that range. ヽ( ຶ▮ ຶ)ﾉ!!!"
        await ctx.send(msg)
        return

    song = matches[song_num]


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

    if not args:
        msg = "Usage (๑ `▽´๑) :\n" \
              "\\search <keywords> - search for a list of songs by name matching to the keywords."

    matches = get_matches(args)
    if not matches:
        await ctx.send("No results found (;´༎ຶД༎ຶ`)")
        return

    # To do: separate search results in pages
    msg = "Search result (๑•̀ㅂ•́) ✧:\n"
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
    if str(ctx.channel) != "bot-command":
        return

    if (ctx.author.name, ctx.author.discriminator) not in user_searches.keys():
        msg = "Usage (๑ `▽´๑) :\n" \
              "\\next - display the next (up to 5) matching songs from search result. " \
              "This command is only activated after \\search."
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
    if str(ctx.channel) != "bot-command":
        return

    if (ctx.author.name, ctx.author.discriminator) not in user_searches.keys():
        msg = "Usage (๑ `▽´๑) :\n" \
              "\\prev - display the previous (up to 5) matching songs from search result. " \
              "This command is only activated after \\search."

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
    if str(ctx.channel) != "bot-command":
        return

    if (ctx.author.name, ctx.author.discriminator) not in user_searches.keys():
        msg = "Usage (๑ `▽´๑) :\n" \
              "\\all - display all matching songs from search result. " \
              "This command is only activated after \\search."

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


    client.run("ODE5MTcxMjQyOTc1NDI4NjI4.YEiuqw.qCbaVA6UrodIlGP5eR2kSUw-VnM")
