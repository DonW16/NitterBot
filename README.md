# NitterBot
 A FOSS Discord Bot for Twitter using nitter.net.

## Description
This bot will post tweets from twitter accounts that you add to NitterBot.

## How to run?
Build the NitterBot docker image on your server.

```
docker build -t nitter-bot-app .
```

Then run the NitterBot docker image.

```
docker run -it --rm --name running-nitter-bot-app nitter-bot-app
```
