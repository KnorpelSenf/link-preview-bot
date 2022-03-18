# Link Preview Bot

## What is this

This is a tiny Telegram bot ([@linkpreviewbot](https://t.me/linkpreviewbot))
written in python that sends all links back to you that were found in your
(think: forwarded) message. It can also follow redirects to resolve shortened
links. The bot is useful if you want to (see the link preview or) visit the
instant view page but the original sender disabled the preview. This happens
often when subscribing to newsletter bots. So now you can subscribe to a news
bot that does not send instant view pages and forward all interesting messages
to [@linkpreviewbot](https://t.me/linkpreviewbot) to read them there anyway.

Note that instant view pages may circumvent paywalls in some cases, e. g. when
the reader is permitted to read only a limited number of articles per
day/week/month. Consider buying a subscription from your favorite news page if
you feel guilty.

## How do I run it locally

Make sure you have [Deno](https://deno.land/) installed.

```bash
git clone git@github.com:KnorpelSenf/link-preview-bot.git
export BOT_TOKEN=your-bot-token
deno run --allow-net --allow-env bot.ts
```

## How do I deploy it on Deno Deploy

1. Make sure you have a bot token from [@BotFather](https://t.me/botfather).
1. Create a project on [Deno Deploy](https://deno.com/deploy).
1. Upload this source code.
1. Store the bot token in an environment variable called `BOT_TOKEN`.
1. Remember to set the webhook at api.telegram.org to your deployment's URL.

## I don't understand X and Y isn't working either

Sorry, I hacked the first version of this in under 24 hours and I no longer
bother to work on this. The bot simply does its job, it's convenient, versatile,
stable and even highly scalable due to its Cloud Function nature. Contact me on
[Telegram](https://t.me/KnorpelSenf) if there is something about the project
that you just cannot figure out on your own. I know that there could be better
docs (as always).
