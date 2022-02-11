import os
import discord
from discord.ext import commands
from protected import token
from PIL import Image, ImageOps
import requests
import numpy as np
import io

client = commands.Bot(command_prefix=",,")
asciis = " .:-=+*#%@"

@client.command()
async def pixel(ctx: discord.ext.commands.context.Context, *args):
    if not ctx.message.attachments:
        await ctx.send("Wrong format")
        return

    files = ctx.message.attachments

    for file in files:
        if not (file.url.endswith('jpg') or file.url.endswith('png') or file.url.endswith('jpeg') or file.url.endswith('jfif') or file.url.endswith('bmp')):
            await ctx.send("Wrong format")
            return
    for a in args:
        if not a.isdecimal:
            await ctx.send("Wrong format")
            return

    dim = [a for a in args] if args else [100]
    if len(dim) < len(files):
        dim = dim + dim[-1:]*(len(files)-len(dim))

    for i in range(len(files)):
        file = files[i]
        width = int(dim[i])
        width = width if width <= 1000 else 1000
        width = width if width >= 50 else 50

        print(width)
        response = requests.get(file.url)
        image_bytes = io.BytesIO(response.content)
        img = Image.open(image_bytes)

        pixel_art = toPixelArt(img, width)
        filename = writeResult(pixel_art, file.url, width)
        sent_filename = '.'.join(file.filename.split('.')[:-1])
        await ctx.send(file = discord.File(f'{filename}.html', f'{sent_filename}.html'))
        e = discord.MessageEmbed().setURL(f"{filename}.html")
        await ctx.send(embed = e)

        os.remove(f"{filename}.html")


def toPixelArt(img, width):
    gray_img = ImageOps.grayscale(img)
    im_width, im_height = gray_img.size
    height = int(im_height/im_width*width)
    gray_img = gray_img.resize((width, height))
    gray_img = np.array(gray_img)
    gray_img = gray_img/256*10
    pixel_map = np.frompyfunc(lambda x: asciis[int(x)], 1, 1)
    char_img = pixel_map(gray_img)
    pixel_art = '\n'.join([' '.join(row) for row in char_img])

    return pixel_art


def writeResult(pixel_art, filename, width):
    filename = '.'.join(filename.split('.')[:-1])
    for illegal in ['/', '<', '>', ':', '"', '\\', '|', '?', '*']:
        filename = filename.replace(illegal,'_')
    with open(filename+'.html', 'w') as fh:
        content = """
        <!doctype html>
        <html lang='en'>
        <head>
        <meta charset='utf-8'>
        <title>'""" + filename + """'</title>
        <meta name='ASCII Art' content='ASCII Art'>
        </head>
        <body style='background-color: black;'>
            <center style='margin-top: 50px'>
            <pre style="color:white; font-family: monospace; font-size: """ + str(500/width) + """px;">""" + pixel_art + """</pre>
            <center>
        </body>
        </html>
        """
        fh.write(content);
    return filename



client.remove_command("help")
@client.command()
async def help(ctx: discord.ext.commands.context.Context):
    doc = ""
    await ctx.send(doc)


client.run(token)