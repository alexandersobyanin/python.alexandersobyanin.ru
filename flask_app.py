#!python3
import os
import json
import git
from flask import Flask
from flask import request
from flask import render_template
from flask_sslify import SSLify
from flask_cors import cross_origin
import telepot
from scripts import github


telegram_secret = os.getenv('TELEGRAM_BOT_SECRET')

telegram_euc_urals_radio_bot_token = os.getenv('TELEGRAM_BOT_EUC_URALS_RADIO_BOT')
telegram_euc_urals_radio_bot_url = '/telegram/TELEGRAM_BOT_EUC_URALS_RADIO_BOT/{}/'.format(telegram_secret)
telegram_euc_urals_radio_bot = telepot.Bot(telegram_euc_urals_radio_bot_token)
telegram_euc_urals_radio_bot.setWebhook(telegram_euc_urals_radio_bot_url, max_connections=1)

telegram_euc_urals_pets_bot_token = os.getenv('TELEGRAM_BOT_EUC_URALS_PETS_BOT')
telegram_euc_urals_pets_bot_url = '/telegram/TELEGRAM_BOT_EUC_URALS_PETS_BOT/{}/'.format(telegram_secret)
telegram_euc_urals_pets_bot = telepot.Bot(telegram_euc_urals_pets_bot_token)
telegram_euc_urals_pets_bot.setWebhook(telegram_euc_urals_pets_bot_url, max_connections=1)

telegram_sret_shot_bot_token = os.getenv('TELEGRAM_BOT_SRET_SHOT_BOT')
telegram_sret_shot_bot_url = '/telegram/TELEGRAM_BOT_SRET_SHOT_BOT/{}/'.format(telegram_secret)
telegram_sret_shot_bot = telepot.Bot(telegram_sret_shot_bot_token)
telegram_sret_shot_bot.setWebhook(telegram_sret_shot_bot_url, max_connections=1)

telegram_must_do_it_bot_token = os.getenv('TELEGRAM_BOT_MUST_DO_IT_BOT')
telegram_must_do_it_bot_url = '/telegram/TELEGRAM_BOT_MUST_DO_IT_BOT/{}/'.format(telegram_secret)
telegram_must_do_it_bot = telepot.Bot(telegram_must_do_it_bot_token)
telegram_must_do_it_bot.setWebhook(telegram_must_do_it_bot_url, max_connections=1)


app = Flask(__name__, static_url_path='/static')
app.debug = False
sslify = SSLify(app)

global_context = {}


@app.route('/', methods=['GET'])
def root():
    return render_template('root.html', **global_context)


@app.route('/health.php', methods=['GET'])
@cross_origin(origins=['alexandersobyanin.ru'], methods=['GET'])
def health():
    return '{"health":1}'


@app.route(telegram_euc_urals_radio_bot_url, methods=["POST"])
def telegram_euc_urals_radio_bot_webhook():
    update = request.get_json()
    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        telegram_euc_urals_pets_bot.sendMessage(chat_id, "Как слышно, моноколёсник? Приём!")
        if "text" in update["message"]:
            text = update["message"]["text"]
            telegram_euc_urals_radio_bot.sendMessage(chat_id, "From the web: you said '{}'".format(text))
        else:
            telegram_euc_urals_radio_bot.sendMessage(chat_id, "From the web: sorry, I didn't understand that kind of message")
    return "OK"


@app.route(telegram_euc_urals_pets_bot_url, methods=["POST"])
def telegram_euc_urals_pets_bot_webhook():
    update = request.get_json()
    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        telegram_euc_urals_pets_bot.sendMessage(chat_id, "Привёт, монокотята!")
        if "text" in update["message"]:
            text = update["message"]["text"]
            telegram_euc_urals_pets_bot.sendMessage(chat_id, "From the web: you said '{}'".format(text))
        else:
            telegram_euc_urals_pets_bot.sendMessage(chat_id, "From the web: sorry, I didn't understand that kind of message")
    return "OK"


@app.route(telegram_sret_shot_bot_url, methods=["POST"])
def telegram_sret_shot_bot_webhook():
    update = request.get_json()
    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        telegram_sret_shot_bot.sendMessage(chat_id, "Скоро сможете прислать скриншот…")
        if "text" in update["message"]:
            text = update["message"]["text"]
            telegram_sret_shot_bot.sendMessage(chat_id, "From the web: you said '{}'".format(text))
        else:
            telegram_sret_shot_bot.sendMessage(chat_id, "From the web: sorry, I didn't understand that kind of message")
    return "OK"


@app.route(telegram_must_do_it_bot_url, methods=["POST"])
def telegram_must_do_it_bot_webhook():
    update = request.get_json()
    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        telegram_must_do_it_bot.sendMessage(chat_id, "JUST DO IT!")
        if "text" in update["message"]:
            text = update["message"]["text"]
            telegram_must_do_it_bot.sendMessage(chat_id, "From the web: you said '{}'".format(text))
        else:
            telegram_must_do_it_bot.sendMessage(chat_id, "From the web: sorry, I didn't understand that kind of message")
    return "OK"


@app.route('/update_server', methods=['POST'])
def update_server_webhook():
    if request.method != 'POST':
        return 'Wrong event type', 405
    x_hub_signature = request.headers.get('X-Hub-Signature')
    if not x_hub_signature:
        return 'Wrong params', 402
    w_secret = os.getenv('UPDATE_SERVER_WEBHOOK_SECRET_KEY')
    if not isinstance(w_secret, str):
        return 'Wrong secret', 500
    if not github.is_valid_signature(x_hub_signature, request.data, w_secret):
        return 'Access denied', 403
    repo = git.Repo('~/mysite/')
    origin = repo.remotes.origin
    origin.pull()
    return 'Updated successfully', 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
