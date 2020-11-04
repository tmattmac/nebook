from app import app
from models import db
from flask import Blueprint, redirect, url_for, session, request, render_template, flash
from flask_login import login_required, current_user

import google.oauth2.credentials
import google_auth_oauthlib.flow
import google.auth.transport.requests
import json

# Load client secrets from file
with open('client_secret.json') as f:
    data = json.load(f)

# Google Drive API authorization information 
CLIENT_ID =     data['web']['client_id']
CLIENT_SECRET = data['web']['client_secret']
TOKEN_URI =     data['web']['token_uri']
GDRIVE_SCOPES = [
    'https://www.googleapis.com/auth/drive.metadata.readonly',
    'https://www.googleapis.com/auth/drive.file'
]

@app.route('/gdrive-acknowledge')
@login_required
def gdrive_acknowledge():
    return render_template('gauth/gdrive-acknowledge.html')

@app.route('/gdrive-authorize')
@login_required
def gdrive_authorize():
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=GDRIVE_SCOPES
    )

    flow.redirect_uri = url_for('gdrive_callback', _external=True)  # TODO: Change this
    
    auth_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )

    session['state'] = state

    return redirect(auth_url)

@app.route('/gdrive-authorize-callback')
def gdrive_callback():

    # TODO: Confirm request url is from Google oauth page, redirect if not
    state = session['state']
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=GDRIVE_SCOPES,
        state=state
    )

    flow.redirect_uri = url_for('gdrive_callback', _external=True)

    authorization_response = request.url
    try:
        flow.fetch_token(authorization_response=authorization_response)
    except:
        flash('You must provide permission to make full use \
            of this application\'s features.', 'danger')
        return redirect(url_for('gdrive_acknowledge'))

    credentials = flow.credentials
    session['access_token'] = credentials.token
    
    # Store refresh token in database
    current_user.gdrive_permission_granted = True
    current_user.gdrive_refresh_token = credentials.refresh_token
    db.session.add(current_user)
    try:
        db.session.commit()
    except:
        db.session.rollback()

    return redirect(url_for('index'))

def create_credentials(user, access_token=None):

    credentials  = google.oauth2.credentials.Credentials(
        token=access_token,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        token_uri=TOKEN_URI,
        refresh_token=user.gdrive_refresh_token
    )
    if not credentials.valid:
        request = google.auth.transport.requests.Request()
        credentials.refresh(request)
    return credentials