import logging
import time
import webbrowser
import json

import requests
from requests.auth import HTTPBasicAuth


class InvalidTokenError(Exception):
    pass


class NotAuthenticatedError(Exception):
    pass


class SpotifyClient:
    def __init__(self):
        self.authenticated: bool = False
        self.access_token: str = None
        self.refresh_token: str = None
        self.scopes = ['user-modify-playback-state']

        try:
            with open('spotify_secret.key', 'r') as secret_file:
                self.client_id = secret_file.readline().rstrip()
                self.client_secret = secret_file.readline().rstrip()
        except (OSError, FileNotFoundError) as e:
            logging.CRITICAL('Could not access "spotify_secret.key". Exiting')
            logging.DEBUG(e)
            exit(1)

    def play(self):
        if self.authenticated:
            base_url = 'api.spotify.com/v1/me/player/play'
            res = requests.put(f'https://{base_url}', headers={'Authorization': f'Bearer {self.access_token}'})
            if res.status_code == 202:
                for tries in range(5):
                    logging.warning('Spotify: device temporarily unavailable. Trying again in 5 seconds')
                    time.sleep(5)
                    res = requests.put(f'https://{base_url}', headers={'Authorization': f'Bearer {self.access_token}'})
                    if res.status_code == 204:
                        break
                    if tries == 4:
                        raise TimeoutError

            if res.status_code == 204:
                logging.info('Spotify: started playback')
            elif res.status_code == 404:
                logging.error('Spotify: playback device not found')
                logging.debug(res.text)
            elif res.status_code == 403:
                logging.error('Spotify: unable to pause')
                logging.debug(res.text)
            elif res.status_code == 401:
                self.authenticated = False
                logging.error('Spotify: access_token is invalid.')
                logging.debug(res.text)
            else:
                logging.error('Spotify: request failed')
                logging.debug(res.text)
        else:
            raise NotAuthenticatedError

    def pause(self):
        if self.authenticated:
            base_url = 'api.spotify.com/v1/me/player/pause'
            res = requests.put(f'https://{base_url}', headers={'Authorization': f'Bearer {self.access_token}'})
            if res.status_code == 202:
                for tries in range(5):
                    logging.warning('Spotify: device temporarily unavailable. Trying again in 5 seconds')
                    time.sleep(5)
                    res = requests.put(f'https://{base_url}', headers={'Authorization': f'Bearer {self.access_token}'})
                    if res.status_code == 204:
                        break
                    if tries == 4:
                        raise TimeoutError

            if res.status_code == 204:
                logging.info('Spotify: paused playback')
            elif res.status_code == 404:
                logging.error('Spotify: playback device not found')
                logging.debug(res.text)
            elif res.status_code == 403:
                logging.error('Spotify: unable to pause')
                logging.debug(res.text)
            elif res.status_code == 401:
                self.authenticated = False
                logging.error('Spotify: access_token is invalid.')
                logging.debug(res.text)
            else:
                logging.error('Spotify: request failed')
                logging.debug(res.text)
        else:
            raise NotAuthenticatedError

    def authenticate(self):
        try:
            with open('refresh.token', 'r') as token_file:
                refresh_token = token_file.readline().rstrip()

            self.refresh_token = refresh_token
            self.refresh()
        except (OSError, FileNotFoundError, InvalidTokenError) as e:
            logging.warning('Unable to authenticate with "refresh.token" file')
            logging.debug(e)

            response_type = 'code'
            redirect_uri = 'https://localhost/'

            base_url = 'accounts.spotify.com/authorize'
            auth_url = (f'https://{base_url}/'
                        f'?client_id={self.client_id}'
                        f'&response_type={response_type}'
                        f'&redirect_uri={redirect_uri}'
                        f'&scope={" ".join(self.scopes)}'
                        )

            print('A browser window will be opened so that you can authorize this app')
            print('After you press enter, authenticate with Spotify and paste the "code" parameter at the next prompt')
            input('<press Enter to continue>')

            logging.info(f'opening {auth_url} in browser')
            webbrowser.open(auth_url, new=2, autoraise=True)

            auth_code = input('Please paste the "code" parameter from the URL here: ')

            access_url = 'accounts.spotify.com/api/token'
            grant_type = 'authorization_code'

            data = {
                'grant_type': grant_type,
                'code': auth_code,
                'redirect_uri': redirect_uri,
                # 'client_id': self.client_id,
                # 'client_secret': self.client_secret
            }

            res = requests.post(f'https://{access_url}', data=data, auth=HTTPBasicAuth(self.client_id, self.client_secret))
            try:
                assert res.status_code == 200
                res_data = json.loads(res.text)
                assert res_data['scope'].split(' ') == self.scopes
                access_token = res_data['access_token']
                refresh_token = res_data['refresh_token']

                self.access_token = access_token
                self.refresh_token = refresh_token
                self.authenticated = True
            except (KeyError, AssertionError) as e:
                logging.critical('Authentication failed. Exiting')
                logging.debug(f'{res.status_code}: {res.text}')
                logging.debug(e)
                exit(1)
            logging.info('Spotify: Authentication succeeded')

            try:
                with open('refresh.token', 'w') as token_file:
                    print(self.refresh_token, file=token_file)
            except OSError as e:
                logging.warning('Unable to write to file "refresh.token". Refresh token will not persist')
                logging.debug(e)

    def refresh(self):
        if not(self.client_id and self.client_secret and self.refresh_token):
            logging.warning('Cannot refresh if client_id, client_secret, or refresh_token are not set')
            logging.debug(f'client_id: {self.client_id}, client_secret: {self.client_secret}, refresh_token: {self.refresh_token}')
            return

        base_url = 'accounts.spotify.com/api/token'

        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token
        }

        # auth_data = f'{self.client_id}:{self.client_secret}'
        # headers = {'Authorization': f'Basic {base64.b64encode(bytes(auth_data, "utf-8"))}'}

        res = requests.post(f'https://{base_url}', data=data, auth=HTTPBasicAuth(self.client_id, self.client_secret))
        try:
            assert res.status_code == 200
            res_data = json.loads(res.text)
            assert res_data['scope'].split(' ') == self.scopes
            access_token = res_data['access_token']
            self.access_token = access_token
            self.authenticated = True
        except (KeyError, AssertionError) as e:
            if res.status_code == 400:
                logging.info('Spotify: Refresh token is invalid. Please delete file "refresh.token"')
            logging.debug(f'{res.status_code}: {res.text}')
            logging.debug(e)
            raise InvalidTokenError
        logging.info('Spotify: Authentication with refresh token succeeded')
