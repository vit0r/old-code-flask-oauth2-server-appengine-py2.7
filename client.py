from os import environ
from flask import Flask, url_for, session, request, jsonify
from flask_oauthlib.client import OAuth
from werkzeug.utils import redirect

CLIENT_ID = environ.get('CLIENT_ID_OAUTH')
CLIENT_SECRET = environ.get('CLIENT_SECRET_OAUTH')
OAUTH_SERVER_BASE_URL = environ.get('OAUTH_SERVER_BASE_URL')

environ['DEBUG'] = 'true'
environ['OAUTHLIB_INSECURE_TRANSPORT'] = 'false'

app = Flask(__name__)
app.secret_key = 'secret'
oauth = OAuth(app)

remote = oauth.remote_app(
    'remote',
    consumer_key=CLIENT_ID,
    consumer_secret=CLIENT_SECRET,
    request_token_params={'scope': 'email'},
    base_url='{}/api/'.format(OAUTH_SERVER_BASE_URL),
    request_token_url=None,
    access_token_url='{}/oauth/token'.format(OAUTH_SERVER_BASE_URL),
    authorize_url='{}/oauth/authorize'.format(OAUTH_SERVER_BASE_URL)
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
    app.run(debug=True, port=8000)
