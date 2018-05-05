# Fortnite_Spotify.py
This program starts/stops Spotify when the user enters/exits the main menu of Fortnite Battle Royale.

##Requirements
1. `Fortnite`
2. `Spotify Premium`
3. `Python 3.6.5+` (Untested on lower versions)
4. `Windows` (Linux pending) 

##Installation
1. [Register a Spotify application](https://beta.developer.spotify.com/documentation/general/guides/app-settings/#register-your-app)
2. Create a file in this directory named `spotify_secret.key`
3. Paste the `Client ID` and `Client Secret` from your app's dashboard into the `spotify_secret.key` file on subsequent lines
    - Example:
    ```
    [Client ID here]
    [Client Secret here]
    ```
4. Run `python3 -m venv venv` (replace `python3` with however you call your python3.6 executable)
5. Activate the venv
    - Windows PowerShell: `./venv/Scripts/Activate.ps1`
6. Run `pip install -r requirements.txt`
7. Deactivate the venv: `deactivate`

##Running
1. Activate the venv
    - Windows PowerShell: `./venv/Scripts/Activate.ps1`
2. Run `python fortnite_spotify.py`
3. Enjoy. When you are in the Fortnite Main menu you will hear Spotify start playing. It will stop when you leave the main menu. 
4. Report any problems in an issue to this repository

##Troubleshooting

**The music doesn't start.**
 - Open the spotify client and play a song, then pause it. It should work now.
 
**It really doesn't start!**
 - Run `python fortnite_spotify.py -d 1` and post the `fortnite_spotify.log` file in a new issue, if you can't debug it yourself.