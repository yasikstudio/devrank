import os
from requests_oauthlib import OAuth2Session
from icecream.settings import GITHUB_APP_ID
from icecream.settings import GITHUB_API_SECRET

os.environ["DEBUG"]="true"
github_authorization_base_url = 'https://github.com/login/oauth/authorize'
github_token_url = 'https://github.com/login/oauth/access_token'

class OAuthManager(object):
    def __init__(self):
        self.github = OAuth2Session(GITHUB_APP_ID)

    def login_request(self):
        authorization_url, status = \
                self.github.authorization_url(github_authorization_base_url)
        return authorization_url

    def callback_response(self, url):
        self.github.fetch_token(github_token_url,
                        client_secret = GITHUB_API_SECRET,
                        authorization_response = url)
    def getUser(self):
        r = self.github.get('https://api.github.com/user')
        return r.content

