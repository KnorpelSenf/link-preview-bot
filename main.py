# import everything
import telegram
from telegram.ext import Updater
from telebot.credentials import bot_token, bot_user_name, URL
from telebot.mastermind import get_response

from flask import escape

global TOKEN
global bot
TOKEN = bot_token
bot = telegram.Bot(token=TOKEN)

def hello_http(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <http://flask.pocoo.org/docs/1.0/api/#flask.Request>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>.
    """

    # retrieve the message in JSON and then transform it to Telegram object
    update = telegram.Update.de_json(request.get_json(force=True), bot)

    chat_id = update.message.chat.id
    msg_id = update.message.message_id

    # Telegram understands UTF-8, so encode text for unicode compatibility
    text = update.message.text.encode('utf-8').decode()
    print("got text message :", text)

    response = get_response(text)
    bot.sendMessage(chat_id=chat_id, text=response, reply_to_message_id=msg_id)

    request_json = request.get_json(silent=True)
    request_args = request.args

    if request_json and 'name' in request_json:
        name = request_json['name']
    elif request_args and 'name' in request_args:
        name = request_args['name']
    else:
        name = 'World'
    return 'Hello {}!'.format(escape(name))

#     # # note the threaded arg which allow
#     # # your app to have more than one thread
#     # app.run(threaded=True)


# # # start the flask app
# # app = Flask(__name__)
# #
# # @app.route('/{}'.format(TOKEN), methods=['POST'])
# # def respond():
# #     # retrieve the message in JSON and then transform it to Telegram object
# #     update = telegram.Update.de_json(request.get_json(force=True), bot)
# #     # get the chat_id to be able to respond to the same user
# #     chat_id = update.message.chat.id
# #     # get the message id to be able to reply to this specific message
# #     msg_id = update.message.message_id
# #     # Telegram understands UTF-8, so encode text for unicode compatibility
# #     text = update.message.text.encode('utf-8').decode()
# #     print("got text message :", text)
# #     # here we call our super AI
# #     response = get_response(text)
# #     # now just send the message back
# #     # notice how we specify the chat and the msg we reply to
# #     bot.sendMessage(chat_id=chat_id, text=response, reply_to_message_id=msg_id)
# #     return 'ok'
# #
# # @app.route('/setwebhook', methods=['GET', 'POST'])
# # def set_webhook():
# #     # we use the bot object to link the bot to our app which live
# #     # in the link provided by URL
# #     s = bot.setWebhook('{URL}{HOOK}'.format(URL=URL, HOOK=TOKEN))
# #     # something to let us know things work
# #     if s:
# #         return "webhook setup ok"
# #     else:
# #         return "webhook setup failed"
# #
# # @app.route('/')
# # def index():
# #     return '.'
