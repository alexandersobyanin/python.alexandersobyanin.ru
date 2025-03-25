#!python3
import os
import json
import urllib3
import traceback

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

telegram_sret_shot_ai_bot_token = os.getenv('TELEGRAM_BOT_SRET_SHOT_AI_BOT')
telegram_sret_shot_ai_bot_url = '/telegram/TELEGRAM_BOT_SRET_SHOT_AI_BOT/{}'.format(telegram_secret)
telegram_sret_shot_ai_bot = telepot.Bot(telegram_sret_shot_ai_bot_token)
telegram_sret_shot_ai_bot.setWebhook(url_base.format(telegram_sret_shot_ai_bot_url), max_connections=1)


def handle_euc_urals_radio_bot(update):
    return basic_message_handler(update, telegram_euc_urals_radio_bot, 'Как слышно, моноколёсник? Приём!')


def handle__euc_urals_pets_bot(update):
    return basic_message_handler(update, telegram_euc_urals_pets_bot, 'Привет, монокотята! Скоро бот заработает…')


def handle_sret_shot_bot(update):
    return basic_message_handler(update, telegram_sret_shot_bot, 'Скоро сможете прислать скриншот…')


def handle_must_do_it_bot(update):
    return basic_message_handler(update, telegram_must_do_it_bot, 'JUST DO IT!')


def handle_sret_shot_ai_bot(update):
    bot = telegram_sret_shot_ai_bot
    if 'message' not in update:
        return 'OK'
    message_data = update['message']
    chat_id = message_data['chat']['id']
    chat_type = message_data['chat']['type']
    message_id = message_data['message_id']
    try:
        # для отладки шлём админку сообщение
        bot.sendMessage(telegram_admin_chat_id, f"update:\n{update}")
        bot.forwardMessage(telegram_admin_chat_id, chat_id, message_id)
        if 'text' not in message_data:
            return 'OK'
        user_text = message_data['text']
        if 'first_name' in message_data['from']:
            user_name = message_data['from']['first_name']
        elif 'username' in message_data['from']:
            user_name = message_data['from']['username']
        else:
            user_name = "Неизвестный"
        bot.sendMessage(telegram_admin_chat_id, f"Привет {user_name}")
    except Exception as e:
        bot.sendMessage(telegram_admin_chat_id, f"Traceback:\n{traceback.format_exc()}")
        bot.sendMessage(telegram_admin_chat_id, f"Exception:\n{e}",)
        bot.sendMessage(telegram_admin_chat_id, f"Exception dict:\n{e.__dict__}", )
    return 'OK'


def basic_message_handler(update, bot, welcome_answer):
    bot.sendMessage(telegram_admin_chat_id, json.dumps(update))
    if 'message' in update:
        message_data = update['message']
        chat_id = message_data['chat']['id']
        chat_type = message_data['chat']['type']
        message_id = message_data['message_id']
        if 'chat' in message_data and chat_type == 'private':
            answer = []
            if chat_id != telegram_admin_chat_id:
                answer.append(welcome_answer)
                answer.append('\n')
            answer.append('Ваше сообщение передано администратору, спасибо.\n')
            answer.append('Мы распознали, что вы прислали нам:\n')
            if 'text' in message_data:
                answer.append('- текст\n')
            if 'photo' in message_data:
                answer.append('- фотографию\n')
            if 'sticker' in message_data:
                answer.append('- стикер\n')
            if 'forward_from' in message_data:
                answer.append('- пересланное сообщение\n')
            if 'voice' in message_data:
                answer.append('- голосовое сообщение\n')
            if 'animation' in message_data:
                answer.append('- GIF\n')
            if 'document' in message_data:
                answer.append('- документ\n')
            try:
                bot.sendMessage(chat_id, ''.join(answer))
            except telepot.exception.BotWasBlockedError:
                bot.sendMessage(telegram_admin_chat_id, 'Бот заблокирован у {}'.format(chat_id))
                try:
                    bot.forwardMessage(telegram_admin_chat_id, chat_id, message_id)
                except Exception as e:
                    bot.sendMessage(telegram_admin_chat_id, f"Traceback:\n{traceback.format_exc()}")
                    bot.sendMessage(telegram_admin_chat_id, f"Exception:\n{e}", )
                    bot.sendMessage(telegram_admin_chat_id, f"Exception dict:\n{e.__dict__}", )
        elif 'chat' in message_data and chat_type == 'supergroup':
            if 'new_chat_participant' in message_data:
                answer = 'Приветствую, {}!'.format(message_data['new_chat_participant']['username'])
                try:
                    bot.sendMessage(chat_id, answer)
                except telepot.exception.BotWasBlockedError:
                    bot.sendMessage(telegram_admin_chat_id, 'Бот заблокирован у {}'.format(chat_id))
        else:
            bot.sendMessage(telegram_admin_chat_id, 'Не обработано, неизвестный тип чата: {}'.format(chat_type))
    else:
        bot.sendMessage(telegram_admin_chat_id, 'Не обработано, это не сообщение!')
    return 'OK'
