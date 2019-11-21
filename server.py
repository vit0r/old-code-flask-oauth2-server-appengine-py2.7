from os import environ
from models import Client, Grant, Token, User
from datetime import datetime, timedelta
from flask import Flask
from flask import session, request
from flask import render_template, redirect, jsonify
from flask_oauthlib.provider import OAuth2Provider
import logging
import jwt

app = Flask(__name__, template_folder='templates')
app.secret_key = environ.get('SERVER_APP_SECRET')
oauth = OAuth2Provider(app)


def get_session_user():
    if 'id' in session:
        return User.get_by_id(session['id'])
    return None


def get_user_by_id(user_id):
    if user_id:
        return User.get_by_id(user_id)
    return None


@app.route('/', methods=('GET', 'POST'))
def home():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query(User.email == email, User.password == password).fetch(1)
        if user:
            session['id'] = user[0].key.integer_id()
    return render_template('home.html')


@oauth.clientgetter
def load_client(client_id):
    client = Client.query(Client.client_id == client_id).fetch(1)
    if client:
        return client[0]
    return None


@oauth.grantgetter
def load_grant(client_id, code):
    grant = Grant.query(Grant.client_id == client_id, Grant.code == code).fetch(1)
    if grant:
        return grant[0]
    return None


@oauth.grantsetter
def save_grant(client_id, code, request, *args, **kwargs):
    expires = datetime.utcnow() + timedelta(seconds=100)
    grant = Grant(
        client_id=client_id,
        code=code['code'],
        redirect_uri=request.redirect_uri,
        scopes=request.scopes,
        user=get_session_user().key.integer_id(),
        expires=expires
    )
    grant.put()
    return grant


@oauth.tokengetter
def load_token(access_token=None, refresh_token=None):
    if access_token:
        current_access_token = Token.query(Token.access_token == access_token).fetch(1)
        if current_access_token:
            return current_access_token[0]
    elif refresh_token:
        return Token.query(Token.refresh_token == refresh_token).fetch(1)[0]


@oauth.tokensetter
def save_token(token, request, *args, **kwargs):
    current_token = Token.query(Token.client_id == request.client.client_id,
                                Token.user == request.user).fetch(1)
    if current_token:
        logging.info('current token {}'.format(current_token))
        current_token[0].key.delete()
    expires_in = token.pop('expires_in')
    expires = datetime.utcnow() + timedelta(seconds=expires_in)
    token = Token(
        access_token=token['access_token'],
        refresh_token=token['refresh_token'],
        token_type=token['token_type'],
        scopes=str(token['scope']).split(),
        expires=expires,
        client_id=request.client.client_id,
        user=request.user,
    )
    token.put()
    return token


@app.route('/oauth/token', methods=['GET', 'POST'])
@oauth.token_handler
def access_token():
    return None


@app.route('/oauth/authorize', methods=['GET', 'POST'])
@oauth.authorize_handler
def authorize(*args, **kwargs):
    user = get_session_user()
    if not user:
        return redirect('/')
    if request.method == 'GET':
        client_id = kwargs.get('client_id')
        client = Client.query(Client.client_id == client_id).fetch(1)
        kwargs['client_id'] = client[0].client_id
        kwargs['email'] = user.email
        return render_template('authorize.html', **kwargs)
    confirm = request.form.get('confirm', 'no')
    return confirm == 'yes'


@app.route('/api/jwt')
@oauth.require_oauth()
def me():
    user = get_user_by_id(request.oauth.user)
    if user:
        try:
            payload = dict(id=user.key.integer_id(), name=user.name, roles=user.roles)
            jwt_token = jwt.encode(payload, app.secret_key, algorithm='HS256')
            return jwt_token
        except ValueError as error:
            logging.error('jwt create payload error %s', error)
    return None
