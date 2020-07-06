# Link Preview Bot

## What is this

This is a tiny Telegram bot ([@linkpreviewbot](https://t.me/linkpreviewbot)) written in python that sends all links back to you that were found in your (think: forwarded) message.
It can also follow redirects to resolve shortened links.
The bot is useful if you want to (see the link preview or) visit the instant view page but the original sender disabled the preview.
This happens often when subscribing to newsletter bots.
So now you can subscribe to a news bot that does not send instant view pages and forward all interesting messages to [@linkpreviewbot](https://t.me/linkpreviewbot) to read them there anyway.

Note that instant view pages may circumvent paywalls in some cases, e. g. when the reader is permitted to read only a limited number of articles per day/week/month.
Consider buying a subscription from your favorite news page if you feel guilty.

## How do I install it locally

Make sure you have Python 3.7 installed.
(You might want to use a virtual environment.)

```bash
git clone git@github.com:KnorpelSenf/link-preview-bot.git
pip install -r requirements.txt
```

## How do I deploy it on Google

The code acts as a Google Cloud Function.

1) Make sure you have a bot token from [@BotFather](t.me/botfather).
1) Create a project in the Google Cloud Console and create a Cloud Function for your bot.
1) Upload this source code using any of the four options (e. g. from a Google Cloud Source repository that mirrors this GitHub repository).
1) Define "webhook" as the main function.
1) Store the bot token in an environment variable called `BOT_TOKEN`.
1) Remember to set the webhook at api.telegram.org to your Cloud Function's URL.

## I don't understand X and Y isn't working either

Sorry, I hacked the first version of this in under 24 hours and I no longer bother to work on this.
The bot simply does its job, it's convenient, versatile, stable and even highly scalable due to its Cloud Function nature.
Contact me on [Telegram](https://t.me/KnorpelSenf) if there is something about the project that you just cannot figure out on your own.
I know that there could be better docs (as always).
