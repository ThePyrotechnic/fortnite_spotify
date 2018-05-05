# Fortnite_Spotify.py
This program starts/stops Spotify when the user enters/exits the main menu of Fortnite Battle Royale.

## Requirements
1. `Fortnite`
2. `Spotify Premium`
3. `Python 3.6.5+` (Untested on lower versions)
4. `Windows` (Linux pending) 

## Limitations
 - Screen resolution must be `1920x1080`
   - Currently, the script reads a handful of pixels to determine the state.
   - This is temporary and a more robust method will be developed in the future.
 - Windows only
   - After the development of the non-screen-dependent method, Mac support will be tested.

## Installation
1. [Register a Spotify application](https://beta.developer.spotify.com/documentation/general/guides/app-settings/#register-your-app)
2. Run `setup.bat`
3. Run `fortnite_spotify.bat`. You will be asked to enter your app's credentials.

## Running
1. Run `fortnite_spotify.bat`
2. Enjoy. When you are in the Fortnite Main menu you will hear Spotify start playing. It will stop when you leave the main menu. 
3. Report any problems in an issue to this repository

## Troubleshooting

**The music doesn't start.**
 - Open the spotify client and play a song, then pause it. It should work now.
 
**It really doesn't start!**
 - Run `python fortnite_spotify.py -d 1` and post the `fortnite_spotify.log` file in a new issue, if you can't debug it yourself.
