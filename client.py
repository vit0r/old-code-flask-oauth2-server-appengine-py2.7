from os import environ
from flask import Flask, url_for, session, request, jsonify
from flask_oauthlib.client import OAuth
from werkzeug.utils import redirect

CLIENT_ID = environ.get('CLIENT_ID_OAUTH')
CLIENT_SECRET = environ.get('CLIENT_SECRET_OAUTH')
OAUTH_SERVER_BASE_URL = environ.get('OAUTH_SERVER_BASE_URL')

app = Flask(__name__)
app.debug = True
app.secret_key = 'secret'
oauth = OAuth(app)

remote = oauth.remote_app(
    'remote',
    consumer_key=CLIENT_ID,
    consumer_secret=CLIENT_SECRET,
    request_token_params={'scope': 'email'},
    base_url=f'{OAUTH_SERVER_BASE_URL}/api/',
    request_token_url=None,
    access_token_url=f'{OAUTH_SERVER_BASE_URL}/oauth/token',
    authorize_url=f'{OAUTH_SERVER_BASE_URL}/oauth/authorize'
)


@app.route('/')
def index():
    if 'remote_oauth' in session:
        resp = remote.get('me')
        if resp:
            return jsonify(resp.data)
    next_url = request.args.get('next') or request.referrer or None
    return remote.authorize(
        callback=url_for('authorized', next=next_url, _external=True)
    )


@app.route('/authorized')
def authorized():
    resp = remote.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['remote_oauth'] = (resp['access_token'], '')
    return redirect('/')


@remote.tokengetter
def get_oauth_token():
    return session.get('remote_oauth')


if __name__ == '__main__':
    import os
    os.environ['DEBUG'] = 'true'
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = 'false'
    app.run(host='localhost', port=8000)
