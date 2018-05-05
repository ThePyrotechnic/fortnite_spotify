import time
import logging
import argparse
import signal

import fortnite_lib as fl
import spotify_lib as sl


def handle_sigint(sig, frame):
    logging.info('Recieved SIGINT')
    logging.debug(f'Signal: {sig}')
    exit(0)


def main():
    signal.signal(signal.SIGINT, handle_sigint)

    cl = sl.SpotifyClient()
    cl.authenticate()

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
