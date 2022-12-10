import os
import feedparser
import time
import discord
import sqlite3
from discord.ext import commands
from dotenv import load_dotenv

followed_accounts = []
author_list = []
title_list = []
published_list = []
link_list = []

def get_nitter_tweet(url):

    feedparser.USER_AGENT = 'NitterBot 0.0.1'
    rss = feedparser.parse(url)
    entries = rss.entries
    
    for t in entries:
        author = t['author']
        author_list.append(author)
        title = t['title']
        title_list.append(title)
        published = t['published']
        published_list.append(published)
        link = t['link']
        link_list.append(link)
    
    return author_list, title_list, published_list, link_list

try:
    sqlite_connection = sqlite3.connect('database.db')
    cursor = sqlite_connection.cursor()

except sqlite3.Error as error:
    print('Failed to connect to database.')



load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
client = commands.Bot(command_prefix="|", case_insensitive=True)

@client.event
async def on_ready():
    # for guild in client.guilds:
    #     if guild.name == GUILD:
    #         break

    print(f'{client.user} has connected to Discord!')
    print(client.user.id)
    print('Discord.py version: {}'.format(discord.__version__))

    for url in followed_accounts:
        tweets = get_nitter_tweet(url)
        for a, t, p, l in tweets:
            print(t)
        #print(f'{guild.name} id: {guild.id}')

@client.command(name='add', help='Add Twitter account to NitterBot.')
async def add_account(ctx, arg):
    await ctx.send('Account %s added to NitterBot!' % (arg))

    followed_accounts.append(arg)

    try:
        sql_query = "INSERT INTO nitter_account (nitter_account_url) VALUES ('%s')" % (arg)
        count = cursor.execute(sql_query)
        sqlite_connection.commit()
        print('NitterBot as added %s to the database!' % (arg))
    except sqlite3.OperationalError:
        print('Database is locked.')


@client.command(name='remove', help='Remove Twitter account from NitterBot.')
async def remove_account(ctx, arg):
    await ctx.send('Account %s removed from NitterBot!' % (arg))

    try:
        sql_query = "DELETE FROM nitter_account WHERE nitter_account_url = '%s'"
        count = cursor.execute(sql_query)
        sqlite_connection.commit()
        print('NitterBot has removed %s from the database!' % (arg))
    except sqlite3.OperationalError:
        print('Database is locked.')
    followed_accounts.remove(arg)

#@client.event
# async def on_message(message):
#     if 'hello' in message.content:
#         await message.channel.send(f"Hi there!")
#     elif 'add' in message.content:
#         await message.channel.send(f"Add Twitter account.")
#     else:
#         await client.process_commands(message)

client.run(TOKEN)

sqlite_connection.close()