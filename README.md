# Disord Bots
#### Developed by jlu@gatech

## Translator Bot
This bot allows you to translate discord messages with google translator. List of helpful commands:
- **::transl [src lang(optional)] [dest lang] [text]**
  - Source language and destination language must be language codes (see ::langlist for details).
  - If source language is not provided, the translator auto detects language for you.

- **::langlist**
  - Displays a list of all available languages and their abbreviations (codes).

- **::hidelanglist**
  - Hide the most recently langlist asked by the current user.

- **::lookup [lang1] [lang2] ...**
  - Display a mapping of specified languages into their language abbreviations (codes).

- **::detectlang [text]**
  - Detects the language of of provided text.

[Invite Translator Bot to your server](https://discord.com/api/oauth2/authorize?client_id=935800920535605290&permissions=75776&scope=bot)


## Pixel Art Bot
This bot makes pixel art from your images attachments! Command format:
- **,,pixel [width1] [width2] ... [attachment1] [attachment2] ...**
  - **widths**
    - Widths controls how many characters per line in your output. Height (number of lines) and font size will be adjusted automatically.
    - Widths should be integers range from 50 to 1000. Values out side of the range will be considered as boundary values.
    - If multiple attachments are given, each width corresponds one attachment.
    - If no widths provided, defaulted to 100 for all attachments.
    - If too much widths provided, the excess ones are ignored.
    - If not enough widths present, then list will be extended by the last width to fit number of attachments.
  - **attachments**
    - Before sending this command, drag your image files into discord to send attachments as command arguments.
    - Only support image files in jpg/jpeg, png, jfif and bmp format.
  - **output**
    - The bot replies by sending a .html file in the channel.
    - You can download the html file and view the pixel arts in browser.
    - The output uses monospace font, which may be overwritten when copied to another text editor and result in glitches.

[Invite Pixel Art Bot to your server](https://discord.com/oauth2/authorize?client_id=940259038636171326&permissions=108544&scope=bot)
