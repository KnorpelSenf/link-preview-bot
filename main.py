import logging
import os
from queue import Queue
from threading import Thread

from telegram import Bot, Update
from telegram.ext import CommandHandler, Dispatcher, Filters, MessageHandler, Updater

from linkpreviewbot.extractor import get_pretty_links

# Make sure you have the bot token set in the environment variable BOT_TOKEN
bot_token = os.environ['BOT_TOKEN']
# Set this environment variable to use polling instead of webhooks
try:
    is_dev = os.environ['DEVELOPMENT']
except:
    is_dev = False

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


def abort_say_no_text(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text='No text in message.',
                             reply_to_message_id=update.message.message_id)


def abort_say_help(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=("<b>My friend sent me a message "
                                   "without link preview!</b>\n"
                                   "Maybe the original sender disabled "
                                   "the preview. Forward me the message "
                                   "and I will give you all the previews.\n\n"
                                   "<b>I have a shortened link!</b>\n"
                                   "Reply to a message <i>in this chat</i> "
                                   "with /resolve to see where the "
                                   "links would redirect you.\n\n"
                                   "<b>The link preview is outdated!</b>\n"
                                   "Check out the official @WebpageBot "
                                   "to update it.\n\n"
                                   "<b>Where is your source code?</b>\nIt's "
                                   "<a href=\"https://github.com/KnorpelSenf/link-preview-bot\">"
                                   "on GitHub</a>."),
                             parse_mode='HTML',
                             disable_web_page_preview=True,  # hehe
                             reply_to_message_id=update.message.message_id)


def abort_say_no_reply_to_resolve(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=("Reply to a message to follow all "
                                   "redirects of the contained links!"),
                             reply_to_message_id=update.message.message_id)


def handle_link_message(resolve):
    def handler(update, context):
        status_message_id = None
        msg = update.message
        if resolve:
            status_message_id = context.bot.send_message(chat_id=update.effective_chat.id, text='\N{THINKING FACE}',
                                                         reply_to_message_id=update.message.message_id).message_id
            msg = msg.reply_to_message
        urls = get_pretty_links(msg, resolve=resolve)
        print(urls)
        if status_message_id is not None:
            context.bot.delete_message(chat_id=update.effective_chat.id,
                                       message_id=status_message_id)

        if len(urls) == 0:
            context.bot.send_message(chat_id=update.effective_chat.id, text='No links found.',
                                     reply_to_message_id=update.message.message_id)
        else:
            for url in urls:
                context.bot.send_message(chat_id=update.effective_chat.id, text=url,
                                         reply_to_message_id=update.message.message_id,
                                         disable_web_page_preview=False)
    return handler


if is_dev:
    updater = Updater(token=bot_token, use_context=True)

    dispatcher = updater.dispatcher
else:
    # Create bot, update queue and dispatcher instances
    bot = Bot(bot_token)
    update_queue = Queue()

    dispatcher = Dispatcher(bot, update_queue, use_context=True)

# Register handlers
dispatcher.add_handler(CommandHandler('help', abort_say_help))
dispatcher.add_handler(CommandHandler(
    'resolve', handle_link_message(resolve=True), filters=Filters.reply))
dispatcher.add_handler(CommandHandler(
    'resolve', abort_say_no_reply_to_resolve, filters=~Filters.reply))
dispatcher.add_handler(MessageHandler(
    ~Filters.text & ~Filters.command, abort_say_no_text))
dispatcher.add_handler(MessageHandler(Filters.all, handle_link_message(False)))

if is_dev:
    updater.start_polling()
else:
    # Start the thread
    thread = Thread(target=dispatcher.start, name='dispatcher')
    thread.start()


def webhook(request):
    # Get update object from request
    update = Update.de_json(request.get_json(force=True), bot)
    # Put update object in queue
    update_queue.put(update)
