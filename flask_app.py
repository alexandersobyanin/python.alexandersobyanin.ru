#!python3
import os
import git
from flask import Flask
from flask import request
from flask import render_template
from flask_sslify import SSLify
from flask_cors import cross_origin
from scripts import github
import telegram


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


@app.route(telegram.telegram_euc_urals_radio_bot_url, methods=['POST'])
def telegram_euc_urals_radio_bot_webhook():
    return telegram.handle_euc_urals_radio_bot(request.get_json())


@app.route(telegram.telegram_euc_urals_pets_bot_url, methods=['POST'])
def telegram_euc_urals_pets_bot_webhook():
    return telegram.handle__euc_urals_pets_bot(request.get_json())


@app.route(telegram.telegram_sret_shot_bot_url, methods=['POST'])
def telegram_sret_shot_bot_webhook():
    return telegram.handle_sret_shot_bot(request.get_json())


@app.route(telegram.telegram_must_do_it_bot_url, methods=['POST'])
def telegram_must_do_it_bot_webhook():
    return telegram.handle_must_do_it_bot(request.get_json())


@app.route(telegram.telegram_sret_shot_ai_bot_url, methods=['POST'])
def telegram_sret_shot_ai_bot_webhook():
    return telegram.handle_sret_shot_ai_bot(request.get_json())


@app.route('/update_server', methods=['POST'])
def update_server_webhook():
    if request.method != 'POST':
        return 'Wrong event type', 405
    x_hub_signature = request.headers.get('X-Hub-Signature')
    if not x_hub_signature:
        return 'Wrong params', 402
    w_secret = os.getenv('UPDATE_SERVER_WEBHOOK_SECRET_KEY')
    if not isinstance(w_secret, str):
        return 'Wrong server secret', 403
    if not github.is_valid_signature(x_hub_signature, request.data, w_secret):
        return 'Access denied', 403
    repo = git.Repo('~/mysite/')
    origin = repo.remotes.origin
    origin.pull()
    return 'Updated successfully', 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
