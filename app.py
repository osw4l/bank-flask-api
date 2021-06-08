import json
import os
import flask
from flask import Flask, request, render_template
from backend.constants import ACCOUNT_ALREADY_EXIST, ALL_FIELDS_ARE_REQUIRED, INVALID_JSON_FILE
from pymongo import MongoClient

from backend.transaction import start_transaction
from backend.utils import trim

app = Flask('bank_api')

MONGO_HOST = os.environ.get('MONGO_HOST')
MONGO_PORT = os.environ.get('MONGO_PORT')
MONGO_DB = os.environ.get('MONGO_INITDB_DATABASE')
MONGO_USER = os.environ.get('MONGO_INITDB_ROOT_USERNAME')
MONGO_PASS = os.environ.get('MONGO_INITDB_ROOT_PASSWORD')
URI = f'mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}?authSource=admin'
client = MongoClient(URI)
db = client.bank_db

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/new_account', methods=['GET', 'POST'])
def new_account():
    context = {
        'result': None,
        'message': None
    }
    if flask.request.method == 'POST':
        user_id = trim(request.form.get('user_id'))
        pin = trim(request.form.get('pin'))

        if len(user_id) == 0 or len(pin) == 0:
            context['result'] = False
            context['message'] = ALL_FIELDS_ARE_REQUIRED

        if db.accounts.find_one({'user_id': user_id}):
            context['result'] = False
            context['message'] = ACCOUNT_ALREADY_EXIST

        if context.get('result') is not False:
            account = {
                'user_id': user_id,
                'pin': int(pin),
                'balance': 180000
            }
            db.accounts.insert_one(account)
            context['result'] = True

    return render_template('new_account.html', context=context)


@app.route('/transaction', methods=['POST', 'GET'])
def transaction():
    context = {
        'result': None,
        'message': None
    }

    if request.method == 'POST':
        file = request.files.get('file')
        if file:
            file_data = file.read().decode("utf-8")
            data = {}
            try:
                data = json.loads(file_data)
            except ValueError:
                context['result'] = False
                context['message'] = INVALID_JSON_FILE
            start_transaction(collection=db.accounts, data=data)

    return render_template('transaction.html', context=context)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
