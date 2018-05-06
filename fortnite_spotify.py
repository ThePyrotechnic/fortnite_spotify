import time
import logging
import argparse
import signal
import sys
from typing import Callable, Iterable

import lib.fortnite_lib as fl
from lib.fortnite_lib import GameState
import lib.spotify_lib as sl


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


def handle_in_menu(cl: sl.SpotifyClient):
    try_spotify_function(cl.set_volume, ['Unable to set volume'], func_args=(100,))
    try_spotify_function(cl.play, handled_errors=['Unable to play'])


def handle_waiting(cl: sl.SpotifyClient):
    pass


def handle_launching(cl: sl.SpotifyClient):
    try_spotify_function(cl.set_volume, ['Unable to set volume'], func_args=(50,))


def handle_can_parachute(cl: sl.SpotifyClient):
    pass


def handle_storm_waiting(cl: sl.SpotifyClient):
    try_spotify_function(cl.pause, handled_errors=['Unable to pause'])


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


def main():
    cl = setup()

    state_map = {
        GameState.UNKNOWN: lambda _: None,
        GameState.IN_MENU: handle_in_menu,
        GameState.WAITING: handle_waiting,
        GameState.LAUNCHING: handle_launching,
        GameState.CAN_PARACHUTE: handle_can_parachute,
        GameState.STORM_WAITING: handle_storm_waiting,
    }

    print('Running. Press Ctrl+C to quit.')
    last_state = fl.get_state()
    logging.info(f'Fortnite: Initial state: {last_state}')
    while True:
        cur_state = fl.get_state()
        if cur_state != last_state:
            last_state = cur_state
            logging.info(f'Fortnite: Changed state: {cur_state}')
            state_map[cur_state](cl)
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
