# TwitterBot
A FOSS Discord Twitter bot using the nitter.net service.

## Description
This bot will post tweets from twitter accounts that you add to TwitterBot.

## How to run?
Build the TwitterBot docker image on your server.

```
docker build -t twitter-bot-app .
```

Then run the TwitterBot docker image.

```
docker run -it --rm --name running-twitter-bot-app twitter-bot-app
```
