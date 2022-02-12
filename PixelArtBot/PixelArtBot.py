import os
import discord
from discord.ext import commands
from protected import token
from PIL import Image, ImageOps
import requests
import numpy as np
import io

client = commands.Bot(command_prefix=",,")
asciis_small = " .:-=+*#%@"
asciis = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. "

@client.command()
async def pixel(ctx: discord.ext.commands.context.Context, *args):
    if not ctx.message.attachments:
        await ctx.send("Please send one or more image attachments with this command. Use ,,help for more information.")
        return

    files = ctx.message.attachments

    for file in files:
        if not (file.url.endswith('jpg') or file.url.endswith('png') or file.url.endswith('jpeg') or file.url.endswith('jfif') or file.url.endswith('bmp')):
            await ctx.send("Wrong file format. Only support image files in jpg/jpeg, png, jfif or bmp format.")
            return
    for a in args:
        if not a.isdecimal:
            await ctx.send(f"Invalid command parameter {a} detected. Parameters must be positive integer values. Use ,,help for more information.")
            return

    dim = [a for a in args] if args else [100]
    if len(dim) < len(files):
        dim = dim + dim[-1:]*(len(files)-len(dim))


    results = []
    filename = f"{ctx.guild}_{ctx.channel}_{ctx.author}"

    for i in range(len(files)):
        file = files[i]
        width = int(dim[i])
        width = width if width <= 1000 else 1000
        width = width if width >= 50 else 50

        response = requests.get(file.url)
        image_bytes = io.BytesIO(response.content)
        img = Image.open(image_bytes)

        pixel_art = toPixelArt(img, width)
        results.append({
            'width': width,
            'pixel_art': pixel_art
        })
        
        filename += f"_{'.'.join(file.filename.split('.')[:-1])}"

    filename = writeResult(results, filename)
    await ctx.send(file = discord.File(f'{filename}.html', f'{filename}.html'))
    os.remove(f"{filename}.html")


def toPixelArt(img, width):
    gray_img = ImageOps.grayscale(img)
    im_width, im_height = gray_img.size
    height = int(im_height/im_width*width)
    gray_img = gray_img.resize((width, height))
    gray_img = np.array(gray_img)
    conversion = asciis if width >= 200 else asciis_small

    gray_img = gray_img/256*len(conversion)
    pixel_map = np.frompyfunc(lambda x: conversion[int(x)], 1, 1)
    char_img = pixel_map(gray_img)
    pixel_art = '\n'.join([' '.join(row) for row in char_img])

    return pixel_art


def writeResult(results, filename):
    for illegal in ['/', '<', '>', ':', '"', '\\', '|', '?', '*']:
        filename = filename.replace(illegal,'__')

    content = """<!doctype html>
        <html lang='en'>
        <head>
        <meta charset='utf-8'>
        <title>'""" + filename + """'</title>
        <meta name='ASCII Art' content='ASCII Art'>
        </head>
        <body style='background-color: black;'>
    """
    for result in results:
        content += """
        <center style='margin-top: 50px'>
        <pre style="color:white; font-family: monospace; font-size: """ + str(500/result["width"]) + """px;">""" + result["pixel_art"] + """</pre>
        <center>
    """

    content += """</body>
        </html>
    """
    with open(filename+'.html', 'w') as fh:
        fh.write(content);
    return filename


client.remove_command("help")
@client.command()
async def help(ctx: discord.ext.commands.context.Context):
    doc = """
    This bot makes pixel art from your images attachments! Command format:
    
            **,,pixel [width1] [width2] ... [attachment1] [attachment2] ...**
                    • **widths**
                            - Widths controls how many characters per line in your output.
                            - Height (number of lines) and font size will be adjusted automatically.
                            - Widths should be integers range from 50 to 1000. Values out side of the range will be considered as boundary values.
                            - If multiple attachments are given, each width corresponds one attachment.
                            - If no widths provided, defaulted to 100 for all attachments.
                            - If too much widths provided, the excess ones are ignored.
                            - If not enough widths present, then list will be extended by the last width to fit number of attachments.
                    • **attachments**
                            - Before sending this command, drag your image files into discord to send attachments as command arguments.
                            - Only support image files in jpg/jpeg, png, jfif and bmp format.
                    • **output**
                            - The bot replies by sending a .html file in the channel.
                            - You can download the html file and view the pixel arts in browser.
                            - The output uses monospace font, which may be overwritten when copied to another text editor and result in glitches.

© Copyright 2022 jlu@gatech
    """
    await ctx.send(doc)


client.run(token)