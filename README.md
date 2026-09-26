<h1 align="center">Fanfiction Finder</h1>

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/arzkar)

This is a discord bot which scrapes google for a fanfiction then redirects to fanfiction.net & archiveofourown.org and parses the html into readable metadata and sends the metadata as an embed message. <br>
Features-

- Currently supports searching for fanfiction.net & archiveofourown.org <br>
- For ao3 searching, works as well as series is supported <br>
- Fanfiction info include- Story name, summary, last updated, word count, rating, genre, pairing. <br>

# Bot Usage

To start using the bot on your discord server (You need to be an admin or owner to do this):

- Use `,allow` command in the channel you want to enable the bot
- Use `,disallow` command in the channel you want to disable the bot
- Use `,allow_all` command to enable the bot for all channels
- Use `,disallow_all` command to disable the bot for all channels

You can use `,help` command for the help menu which will show all the ways you can use to search for fanfiction using the bot.
<br>
Use `ao3 fic_name` or `ao3 fic_name series` and `ffn fic_name` to search a fanfiction. <br>
You can also use the url of the fanfiction for searching. <br>
The query string is not case-sensitive so either uppercase, lowercase or combination of both can be used to search.<br>
The following is an example on how the bot works in realtime-<br>

![](https://raw.githubusercontent.com/arzkar/Fanfiction-Finder-Bot/main/data/img/bot_output.gif)

# Development & Hosting

Clone the repository in one of the directories in your system using:

```
git clone https://github.com/Maccygoat/Fanfiction-Finder.git
```

## Python

- Install Python v3.8.5

- Create a virtual environment for the bot using venv, virtualenv etc. (Optional but Recommended)

- Install the dependencies using pip:

  - For development: `pip install -r requirements_dev.txt`
  - For production: `pip install -r requirements_prod.txt`

## Discord

- Create a `.env` file which should contain the `DISCORD_TOKEN` for your testing bot as shown in the `.env.ex` file.

- Create a bot from the [Discord Developer Portal](https://discord.com/developers/applications) and copy the bot token to the `.env` file.

- Run the bot using `python main.py` in the root directory.

## Hosting

Use any cloud hosting provider of your choice like Heroku, DigitalOcean etc and follow the steps as above.
