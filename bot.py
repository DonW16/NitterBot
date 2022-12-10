import os
import feedparser
import time
import discord
import sqlite3
import re
from discord.ext import commands
from dotenv import load_dotenv

followed_accounts = []
author_list = []
title_list = []
published_list = []
link_list = []

def get_nitter_tweet_rss(url):

    feedparser.USER_AGENT = 'NitterBot 0.0.1'
    rss = feedparser.parse(url[0])
    entries = rss.entries
    
    # for t in entries:
    #     author = t['author']
    #     author_list.append(author)
    #     title = t['title']
    #     title_list.append(title)
    #     published = t['published']
    #     published_list.append(published)
    #     link = t['link']
    #     link_list.append(link)

    author = entries[0]['author']
    title = entries[0]['title']
    published = entries[0]['published']
    link = entries[0]['link']
    
    return author, title, published, link

def select_nitter_profile_sqlite():
    sql_query = "SELECT nitter_account_url FROM nitter_account"
    count = cursor.execute(sql_query)
    result = cursor.fetchall()
    return result

def insert_nitter_tweets_sqlite(author, title, published, link):
    # Prepare statement every query 
    data = [(author, title, published, link)]
    sql_query = "INSERT INTO nitter_tweets (author, title, published, link) VALUES (?, ?, ?, ?)"
    count = cursor.executemany(sql_query, data)
    sqlite_connection.commit()
    print('Inserted %s %s %s %s into database.' % (author, title, published, link))

def select_nitter_tweets_sqlite():
    sql_query = "SELECT author, title, published, link FROM nitter_tweets"
    count = cursor.execute(sql_query)
    result = cursor.fetchall()
    return result

def regex_twitter_url(url):
    regex = r'twitter\.com'
    nitter_url = re.sub(regex, 'nitter.nl', url, count=1)
    # fix trailing slash problem
    nitter_url = nitter_url + '/rss'
    return nitter_url

def regex_nitter_link(link):
    regex = r'nitter\.nl|nitter\.net'
    nitter_link = re.sub(regex, 'twitter.com', link, count=1)
    return nitter_link

try:
    sqlite_connection = sqlite3.connect('database.db')
    cursor = sqlite_connection.cursor()
    pass

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



@client.command(name='add', help='Add Twitter account to NitterBot.')
async def add_account(ctx, arg):
    await ctx.send('Account %s added to NitterBot!' % (arg))

    #followed_accounts.append(arg)
    
    #Change Twitter URL to nitter via regex.
    filter = regex_twitter_url(arg)
    arg = filter

    try:
        data = [(arg)]
        sql_query = "INSERT INTO nitter_account (nitter_account_url) VALUES (?)"
        count = cursor.executemany(sql_query, data)
        sqlite_connection.commit()
        print('NitterBot as added %s to the database!' % (arg))
    except sqlite3.OperationalError:
        print('Database is locked.')

@client.command(name='remove', help='Remove Twitter account from NitterBot.')
async def remove_account(ctx, arg):
    try:
        sql_query = "DELETE FROM nitter_account WHERE nitter_account_url = ?"
        count = cursor.executemany(sql_query, arg)
        sqlite_connection.commit()
        print('NitterBot has removed %s from the database!' % (arg))
        await ctx.send('Account %s removed from NitterBot!' % (arg))
    except sqlite3.OperationalError:
        print('Database is locked.')
        await ctx.send('Error %s.' % (sqlite3.OperationalError))
    except ValueError:
        print('%s does not exist within the database.')

@client.command(name='run', help='Run NitterBot to check for tweets within database (DEBUG)')
async def run_nitter(ctx):
    await ctx.send('run_nitter(ctx) executed via NitterBot.')
    nitter_profiles = select_nitter_profile_sqlite()
    for p in nitter_profiles:
        tweets = get_nitter_tweet_rss(p)
        try:
            insert_nitter_tweets_sqlite(tweets[0], tweets[1], tweets[2], tweets[3])
        except sqlite3.IntegrityError:
            print('Tweet already exists within datebase.')

    select_tweets = select_nitter_tweets_sqlite()
    for x in range(0, len(select_tweets)):
        link = regex_nitter_link(select_tweets[x][3])
        await ctx.send('%s\n' % (link))

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