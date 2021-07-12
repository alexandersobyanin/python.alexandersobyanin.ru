#!python3
import os
import json
import urllib3
import telepot


# url_base = 'https://python.alexandersobyanin.ru{}'
url_base = 'https://b1oki.pythonanywhere.com{}'

proxy_url = 'http://proxy.server:3128'
telepot.api._pools = {
    'default': urllib3.ProxyManager(proxy_url=proxy_url, num_pools=3, maxsize=10, retries=False, timeout=30),
}
telepot.api._onetime_pool_spec = (urllib3.ProxyManager, dict(proxy_url=proxy_url, num_pools=1, maxsize=1, retries=False, timeout=30))

telegram_secret = os.getenv('TELEGRAM_BOT_SECRET')
telegram_admin_chat_id = int(os.getenv('TELEGRAM_BOT_ADMIN_CHAT_ID'))

telegram_euc_urals_radio_bot_token = os.getenv('TELEGRAM_BOT_EUC_URALS_RADIO_BOT')
telegram_euc_urals_radio_bot_url = '/telegram/TELEGRAM_BOT_EUC_URALS_RADIO_BOT/{}'.format(telegram_secret)
telegram_euc_urals_radio_bot = telepot.Bot(telegram_euc_urals_radio_bot_token)
telegram_euc_urals_radio_bot.setWebhook(url_base.format(telegram_euc_urals_radio_bot_url), max_connections=1)

telegram_euc_urals_pets_bot_token = os.getenv('TELEGRAM_BOT_EUC_URALS_PETS_BOT')
telegram_euc_urals_pets_bot_url = '/telegram/TELEGRAM_BOT_EUC_URALS_PETS_BOT/{}'.format(telegram_secret)
telegram_euc_urals_pets_bot = telepot.Bot(telegram_euc_urals_pets_bot_token)
telegram_euc_urals_pets_bot.setWebhook(url_base.format(telegram_euc_urals_pets_bot_url), max_connections=1)

telegram_sret_shot_bot_token = os.getenv('TELEGRAM_BOT_SRET_SHOT_BOT')
telegram_sret_shot_bot_url = '/telegram/TELEGRAM_BOT_SRET_SHOT_BOT/{}'.format(telegram_secret)
telegram_sret_shot_bot = telepot.Bot(telegram_sret_shot_bot_token)
telegram_sret_shot_bot.setWebhook(url_base.format(telegram_sret_shot_bot_url), max_connections=1)

telegram_must_do_it_bot_token = os.getenv('TELEGRAM_BOT_MUST_DO_IT_BOT')
telegram_must_do_it_bot_url = '/telegram/TELEGRAM_BOT_MUST_DO_IT_BOT/{}'.format(telegram_secret)
telegram_must_do_it_bot = telepot.Bot(telegram_must_do_it_bot_token)
telegram_must_do_it_bot.setWebhook(url_base.format(telegram_must_do_it_bot_url), max_connections=1)


def handle_euc_urals_radio_bot(update):
    if 'message' in update:
        chat_id = update['message']['chat']['id']
        telegram_euc_urals_radio_bot.sendMessage(chat_id, 'Как слышно, моноколёсник? Приём!')
        if 'text' in update['message']:
            text = update['message']['text']
            telegram_euc_urals_radio_bot.sendMessage(chat_id, "From the web: you said '{}'".format(text))
            if chat_id == telegram_admin_chat_id:
                telegram_euc_urals_radio_bot.sendMessage(chat_id, json.dumps(update))
            else:
                telegram_euc_urals_radio_bot.forwardMessage(telegram_admin_chat_id, chat_id, update['message']['message_id'])
        else:
            telegram_euc_urals_radio_bot.sendMessage(chat_id, "From the web: sorry, I didn't understand that kind of message")
    return 'OK'


def handle__euc_urals_pets_bot(update):
    if 'message' in update:
        chat_id = update['message']['chat']['id']
        telegram_euc_urals_pets_bot.sendMessage(chat_id, 'Привёт, монокотята!')
        if 'text' in update['message']:
            text = update['message']['text']
            telegram_euc_urals_pets_bot.sendMessage(chat_id, "From the web: you said '{}'".format(text))
            if chat_id == telegram_admin_chat_id:
                telegram_euc_urals_pets_bot.sendMessage(chat_id, json.dumps(update))
            else:
                telegram_euc_urals_pets_bot.forwardMessage(telegram_admin_chat_id, chat_id, update['message']['message_id'])
        else:
            telegram_euc_urals_pets_bot.sendMessage(chat_id, "From the web: sorry, I didn't understand that kind of message")
    return 'OK'


def handle_sret_shot_bot(update):
    if 'message' in update:
        chat_id = update['message']['chat']['id']
        telegram_sret_shot_bot.sendMessage(chat_id, 'Скоро сможете прислать скриншот…')
        if 'text' in update['message']:
            text = update['message']['text']
            telegram_sret_shot_bot.sendMessage(chat_id, "From the web: you said '{}'".format(text))
            if chat_id == telegram_admin_chat_id:
                telegram_sret_shot_bot.sendMessage(chat_id, json.dumps(update))
            else:
                telegram_sret_shot_bot.forwardMessage(telegram_admin_chat_id, chat_id, update['message']['message_id'])
        else:
            telegram_sret_shot_bot.sendMessage(chat_id, "From the web: sorry, I didn't understand that kind of message")
    return 'OK'


def handle_must_do_it_bot(update):
    if 'message' in update:
        chat_id = update['message']['chat']['id']
        telegram_must_do_it_bot.sendMessage(chat_id, 'JUST DO IT!')
        if 'text' in update['message']:
            text = update['message']['text']
            telegram_must_do_it_bot.sendMessage(chat_id, "From the web: you said '{}'".format(text))
            if chat_id == telegram_admin_chat_id:
                telegram_must_do_it_bot.sendMessage(chat_id, json.dumps(update))
            else:
                telegram_must_do_it_bot.forwardMessage(telegram_admin_chat_id, chat_id, update['message']['message_id'])
        else:
            telegram_must_do_it_bot.sendMessage(chat_id, "From the web: sorry, I didn't understand that kind of message")
    return 'OK'
