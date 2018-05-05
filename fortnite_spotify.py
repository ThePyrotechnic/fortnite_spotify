import time
import logging
import argparse
import signal
import os

import lib.fortnite_lib as fl
import lib.spotify_lib as sl


def handle_sigint(sig, frame):
    logging.info('Recieved SIGINT')
    logging.debug(f'Signal: {sig}')
    exit(0)


def main():
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

    cl = sl.SpotifyClient(client_id, client_secret)
    cl.authenticate()
    print('Running. Press Ctrl+C to quit.')
    last_state = fl.in_menu()
    while True:
        cur_state = fl.in_menu()
        if cur_state != last_state:
            last_state = cur_state
            if cur_state:
                logging.info('Fortnite: in menu')
                cl.play()
            else:
                logging.info('Fortnite: out of menu')
                cl.pause()
        time.sleep(1)
    pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Autmoatically start/stop Spotify when in Fortnite\'s main menu')
    parser.add_argument('-d', '--debug_level', type=int, nargs='?', const=3, default=3, help='1: Debug, 2: Info, 3 (default): Warning, 4: Error, 5: Critical, 6: None')
    args = parser.parse_args()
    logging.basicConfig(filename='fortnite_spotify.log', filemode='w', level=args.debug_level * 10)
    main()
