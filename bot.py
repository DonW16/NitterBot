import os
import feedparser
import logging
import time
import datetime
import discord
import sqlite3
import re
import asyncio
from discord.ext import commands
from dotenv import load_dotenv

def get_nitter_tweet_rss(url):

    feedparser.USER_AGENT = 'NitterBot 0.0.1 - https://github.com/DonW16/NitterBot'
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

def insert_nitter_tweets_sqlite(author, title, published, link, posted):
    # Prepare statement every query 
    data = [(author, title, published, link, posted)]
    sql_query = "INSERT INTO nitter_tweets (author, title, published, link, discord_posted) VALUES (?, ?, ?, ?, ?)"
    count = cursor.executemany(sql_query, data)
    sqlite_connection.commit()
    print('Inserted %s %s %s %s %s into database.' % (author, title, published, link, posted))

def update_nitter_tweets_posted(link, posted):
    data = [(posted, link)]
    sql_query = "UPDATE nitter_tweets SET discord_posted = ? WHERE link = ?"
    count = cursor.executemany(sql_query, data)
    sqlite_connection.commit()
    print('Updated database link %s and set to %s.' % (link, posted))

def remove_nitter_tweets_sqlite(author, title, published, link, posted):
    # Prepare statement every query 
    data = [(author, title, published, link, posted)]
    sql_query = "DELETE FROM nitter_tweets WHERE nitter_account_url = ?"
    count = cursor.executemany(sql_query, data)
    sqlite_connection.commit()
    print('Inserted %s %s %s %s %s into database.' % (author, title, published, link, posted))

def select_nitter_tweets_sqlite():
    sql_query = "SELECT author, title, published, link, discord_posted FROM nitter_tweets"
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

def check_tweets_sqlite():
    pass

def check_sqlite_database_exists():
    if os.path.isfile('database.db'):
        return True
    else:
        return False

def create_sqlite_database():
    if check_sqlite_database_exists() == True:
        datetime_now = datetime.datetime.utcnow()
        print('%s SQLite database already exists, skipping database creation.' % (datetime_now))
    else:
        try:
            sqlite_connection = sqlite3.connect('database.db')
            cursor = sqlite_connection.cursor()

            sql_query = "CREATE TABLE IF NOT EXISTS 'nitter_account' ('id'	INTEGER, 'nitter_account_url' TEXT, PRIMARY KEY ('id' AUTOINCREMENT))"
            count = cursor.execute(sql_query)
        
            sql_query = "CREATE TABLE IF NOT EXISTS 'nitter_tweets' ('id' INTEGER, 'author' TEXT, 'title' TEXT, 'published' TEXT, 'link' TEXT UNIQUE, 'discord_posted' INTEGER, PRIMARY KEY ('id' AUTOINCREMENT))"
            count = cursor.execute(sql_query)

            sqlite_connection.commit()
            datetime_now = datetime.datetime.utcnow()
            print('%s SQlite database has been created!' % (datetime_now))

        except sqlite3.Error as error:
            datetime_now = datetime.datetime.utcnow()
            print('%s Failed to connect to database.' % (datetime_now))

create_sqlite_database()

try:
    sqlite_connection = sqlite3.connect('database.db')
    cursor = sqlite_connection.cursor() # Is this required?
    datetime_now = datetime.datetime.utcnow()
    print('%s Connected to SQLite database.' % (datetime_now))

except sqlite3.Error as error:
    datetime_now = datetime.datetime.utcnow()
    print('%s Failed to connect to database.' % (datetime_now))

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
#GUILD = os.getenv('DISCORD_GUILD')
intents = discord.Intents.all()
client = commands.Bot(command_prefix="|", case_insensitive=True, intents=intents)

@client.event
async def on_ready():
    # for guild in client.guilds:
    #     if guild.name == GUILD:
    #         break

    datetime_now = datetime.datetime.utcnow()
    print(f'{datetime_now} {client.user} has connected to Discord!')
    #print(client.user.id)
    datetime_now = datetime.datetime.utcnow()
    print('{} Discord.py version: {}'.format(datetime_now, discord.__version__))

@client.command(name='add', help='Add Twitter account to NitterBot.')
async def add_account(ctx, arg):
    datetime_now = datetime.datetime.utcnow()
    await ctx.send('%s Account %s added to NitterBot!' % (datetime_now, arg))
    
    #Change Twitter URL to nitter via regex.
    filter = regex_twitter_url(arg)
    arg = filter

    try:
        data = [(arg)]
        sql_query = "INSERT INTO nitter_account (nitter_account_url) VALUES (?)"
        count = cursor.execute(sql_query, data)
        sqlite_connection.commit()
        datetime_now = datetime.datetime.utcnow()
        print('NitterBot as added %s to the database!' % (arg))
    except sqlite3.OperationalError:
        datetime_now = datetime.datetime.utcnow()
        print('%s Database is locked.' % (datetime_now))

@client.command(name='remove', help='Remove Twitter account from NitterBot.')
async def remove_account(ctx, arg):
    try:
        sql_query = "DELETE FROM nitter_account WHERE nitter_account_url = ?"
        count = cursor.executemany(sql_query, arg)
        sqlite_connection.commit()
        datetime_now = datetime.datetime.utcnow()
        print('%s NitterBot has removed %s from the database!' % (arg))
        await ctx.send('Account %s removed from NitterBot!' % (arg))
    except sqlite3.OperationalError:
        datetime_now = datetime.datetime.utcnow()
        print('%s Database is locked.' % (datetime_now))
        await ctx.send('Error %s.' % (sqlite3.OperationalError))
    except ValueError:
        datetime_now = datetime.datetime.utcnow()
        print('%s %s does not exist within the database.' % (datetime_now, arg))

@client.command(name='list', help='List followed accounts within database.')
async def list_account(ctx):
    try:
        profiles = select_nitter_profile_sqlite()
        for p in profiles:
            await ctx.send('%s within database.' % (p))
    except sqlite3.OperationalError:
        datetime_now = datetime.datetime.utcnow()
        print('%s Database is locked.' % (datetime_now))
        await ctx.send('Error %s.' % (sqlite3.OperationalError))

@client.command(name='run', help='Run NitterBot to fetch tweets from followed accounts.')
async def run_nitter(ctx):
    #await ctx.send('run_nitter(ctx) executed via NitterBot.')
    while True:
        nitter_profiles = select_nitter_profile_sqlite()
        for p in nitter_profiles:
            tweets = get_nitter_tweet_rss(p)
            try:
                
                insert_nitter_tweets_sqlite(tweets[0], tweets[1], tweets[2], tweets[3], '0')
                select_tweets = select_nitter_tweets_sqlite()
                for x in range(0, len(select_tweets)):
                    link = regex_nitter_link(select_tweets[x][3])
                    if(select_tweets[x][4] == 0):
                        await ctx.send('%s\n' % (link))
                        update_nitter_tweets_posted(select_tweets[x][3], '1')

            except sqlite3.IntegrityError:
                datetime_now = datetime.datetime.utcnow()
                print('%s Tweet already exists within datebase.' % (datetime_now))

        datetime_now = datetime.datetime.utcnow()
        print('%s Now sleeping for 5 minutes.' % (datetime_now))
        await asyncio.sleep(300) # 5 minutes
        
client.run(TOKEN)
sqlite_connection.close()