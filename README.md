# Fortnite_Spotify.py
This program controls Spotify while playing Fortnite Battle Royale.

## Requirements
1. `Fortnite`
2. `Spotify Premium`
3. `Python 3.6.5+` (Untested on lower versions)
4. `Windows` (Linux pending) 

## Limitations
 - Brightess must be set to .50 in-game
   - Until non-screen-dependent method is developed, a configurator will be used to calibrate the script to the user's display
 - Screen resolution must be `1920x1080`
   - Currently, the script reads a handful of pixels to determine the state.
   - This is temporary and a more robust method will be developed in the future.
 - Windows only
   - After the development of the non-screen-dependent method, Mac support will be tested.

## Installation
1. [Register a Spotify application](https://beta.developer.spotify.com/documentation/general/guides/app-settings/#register-your-app)
2. After registering, go to the [dashboard](https://beta.developer.spotify.com/dashboard/) for that app and click `EDIT SETTINGS`.
3. Scroll down to the `Redirect URIs` section and add `https://localhost/`.
4. Save these settings
5. Run `setup.bat`
6. Run `fortnite_spotify.bat`. You will be asked to enter your app's credentials.

## Running
1. Run `fortnite_spotify.bat`
2. Enjoy.
3. Report any problems in an issue to this repository.

## Customization
To configure the program, edit `fortnite_spotify.cfg`.

The defaults are a good working example of what is currently possible.
 
**Possible actions:**
 - `["set_volume", int]` - Set the volume to the specified value. Must be between `0` and `100`, inclusive
 - `["play"]` - Start playback
 - `["pause"]` - Pause playback

## Troubleshooting

**The music doesn't start.**
 - Open the spotify client and play a song, then pause it. It should work now.
 
**It really doesn't start!**
 - Run `python fortnite_spotify.py -d 1` and post the `fortnite_spotify.log` file in a new issue, if you can't debug it yourself.
