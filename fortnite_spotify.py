import time
import logging
import argparse
import signal
import sys
import json
from typing import Callable

import lib.fortnite_lib as fl
from lib.fortnite_lib import GameState
import lib.spotify_lib as sl


CONFIG: dict = {}

CFG_MAP: dict = {}


def handle_sigint(sig, frame):
    logging.info('Recieved SIGINT')
    logging.debug(f'Signal: {sig}')
    exit(0)


def try_spotify_function(func: Callable, handled_errors: list, func_args=None):
    if func_args is None:
        func_args = []
    try:
        func(*func_args)
    except sl.RequestFailedError as e:
        if str(e) in handled_errors:
            pass
        else:
            logging.error('Spotify: An unhandled error has been raised')
            logging.debug(e)


def handle_event(event_name: str):
    global CFG_MAP

    for action in CONFIG[event_name]['actions']:
        try:
            action_name, *action_args = action
            func = CFG_MAP[action_name]['func']
            handled_errors = CFG_MAP[action_name]['handled_errors']

            try_spotify_function(func, handled_errors=handled_errors, func_args=action_args)
        except ValueError:  # A null event was passed (bad config)
            pass


def setup() -> sl.SpotifyClient:
    signal.signal(signal.SIGINT, handle_sigint)

    try:
        with open('spotify_secret.key', 'r') as secret_file:
            client_id = secret_file.readline().rstrip()
            client_secret = secret_file.readline().rstrip()
            logging.info('Successfully loaded client information')
    except (OSError, IOError, FileNotFoundError) as e:
        logging.info('Could not access "spotify_secret.key".')
        logging.debug(e)

        client_id = input('Enter your Spotify application\'s Client ID: ')
        client_secret = input('Enter your Spotify application\'s Client Secret: ')
        try:
            with open('spotify_secret.key', 'w') as secret_file:
                print(client_id, file=secret_file)
                print(client_secret, file=secret_file)
            logging.info('Successfully saved client information')
        except (OSError, IOError) as e:
            logging.error('Unable to write to "spotify_secret.key" file. Client info will not persist')
            logging.debug(e)

    cl = sl.SpotifyClient(client_id, client_secret, ['user-modify-playback-state'])
    cl.authenticate()
    return cl


def load_config():
    global CONFIG

    try:
        with open('fortnite_spotify.cfg', 'r') as cfg_file:
            CONFIG = json.load(cfg_file)
            CONFIG['unknown'] = {'actions': []}
            logging.info('Successfully loaded "fortnite_spotify.cfg"')
            return
    except json.JSONDecodeError as e:
        logging.info('"fortnite_spotify.cfg" is invalid.')
        logging.debug(e)
    except (OSError, IOError, FileNotFoundError) as e:
        logging.info('Could not access "fortnite_spotify.cfg".')
        logging.debug(e)

    # Load reasonable defaults if the config file could not be loaded
    CONFIG = {
        'main_menu': {'actions': [["set_volume", 70], ["play"]]},
        'waiting_for_players': {'actions': []},
        'waiting_to_drop': {'actions': [["set_volume", 50]]},
        'parachuting': {'actions': []},
        'landed': {'actions': [["pause"]]},
        'unknown': {'actions': []},
    }


def main():
    global CFG_MAP

    load_config()

    cl = setup()

    CFG_MAP = {
        'set_volume': {'func': cl.set_volume, 'handled_errors': ['Unable to set volume']},
        'play': {'func': cl.play, 'handled_errors': ['Unable to play']},
        'pause': {'func': cl.pause, 'handled_errors': ['Unable to pause']},
    }

    state_map = {
        GameState.UNKNOWN: 'unknown',
        GameState.IN_MENU: 'main_menu',
        GameState.WAITING: 'waiting_for_players',
        GameState.LAUNCHING: 'waiting_to_drop',
        GameState.CAN_PARACHUTE: 'parachuting',
        GameState.STORM_WAITING: 'landed',
    }

    print('Running. Press Ctrl+C to quit.')
    last_state = fl.get_state()
    logging.info(f'Fortnite: Initial state: {last_state}')
    while True:
        cur_state = fl.get_state()
        if cur_state != last_state:
            last_state = cur_state
            logging.info(f'Fortnite: Changed state: {cur_state}')
            handle_event(state_map[cur_state])
        time.sleep(1)
    pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Automatically start/stop Spotify when in Fortnite\'s main menu')
    parser.add_argument('-d', '--debug_level', type=int, nargs='?', const=3, default=3, help='1: Debug, 2: Info, 3 (default): Warning, 4: Error, 5: Critical, 6: None')
    parser.add_argument('--debug_stderr', action='store_true', help='Send debug to stderr instead of log file')
    args = parser.parse_args()
    if args.debug_stderr:
        logging.basicConfig(stream=sys.stderr, level=args.debug_level * 10)
    else:
        logging.basicConfig(filename='fortnite_spotify.log', filemode='w', level=args.debug_level * 10)
    main()
