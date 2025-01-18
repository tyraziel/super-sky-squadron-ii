# codemash25-pygame-ce
Code for CodeMash 2025 Divez Session - So you want to make video games? - Super Sky Squadron II: The Flying Ace Follies

In order to get the most out of the session, it is strongly advisable that the pre-requisites are completed prior to the session starting.  It is even more advisable to complete the pre-requisites before coming to CodeMash as you and every other attendee will be fighting for bandwidth and some setups (chromebook) might take a long time for downloads.

## NOTE

This project is "locked down" for historical purposes (i.e. to keep it as it was for the codemash 25 session.)  The updated project will be located here:  https://github.com/tyraziel/super-sky-squadron-ii.git

## Pre-Requisites

- A laptop capable of running python3 with pygame-ce and installing various pip packages, and running some type of editor and unzip capabilities.
- Python 3
- pygame-ce (ansible-core on linux based systems)
- git (to clone the project, but could download as zip - https://github.com/tyraziel/codemash25-pygame-ce/archive/refs/heads/main.zip)
- A text editor - VS Code (prefered)
- Assets downloaded and installed (via the scripts in setup/)

## Quick Setup Guide

This guide assumes you already have a version of python 3 installed and have working knowledge of python, python virtual environments and the command line.

*NOTE:*  A major difference between Windows and Linux is windows generally uses `python` and Linux generally uses `python3`.

### Windows (via Windows Powershell)

Run the following commands from a Powershell Command Prompt

```shell
python -m venv .pygame-ce-codemash25
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
./.pygame-ce-codemash25/Scripts/activate
git clone https://github.com/tyraziel/codemash25-pygame-ce.git
cd codemash25-pygame-ce
pip install -r requirements.txt
cd setup
./setup.ps1
cd ../
python codemash2025.py
```

### Linux Based Environments

Ensure that you have a unzip/zip utility before executing the ansible playbook command.

```shell
python3 -m venv .pygame-ce-codemash25
source ./.pygame-ce-codemash25/bin/activate
git clone https://github.com/tyraziel/codemash25-pygame-ce.git
cd codemash25-pygame-ce
pip3 install -r requirements.txt
pip3 install ansible-core
cd setup
ansible-playbook setup.yaml
cd ../
python3 codemash2025.py
```

For more detailed instructions look at [SETUP.md](SETUP.md)

## Refresh / Update

At anytime either re-download the zip file, or execute a `git pull` from the project root to get any last minute updates.

## Credits

All visual assets and sound effects have been provided by [kenney.nl](https://www.kenney.nl)

## Python Code License - CC0 1.0

The python code in this project is licensed under a Creative Commons CC0 1.0 Universal Public Domain Dedication [https://creativecommons.org/publicdomain/zero/1.0/](https://creativecommons.org/publicdomain/zero/1.0/)

## All other asset licenses

Please review the licenses for the other assets.

## Attribution

Since this has been released to the Public Domain under Creative Commons CC0 1.0 Universal Public Domain Dedication, attribution is not needed, but it would be a nice gesture.

## Special Thanks

- My Family

- CodeMash and KidzMash (codemash.org)[https://codemash.org/]

- Pygame-CE - [https://github.com/pygame-community/pygame-ce](https://github.com/pygame-community/pygame-ce)
- Pygame-CE Mantainer - Andrew (oddbookworm)[https://github.com/oddbookworm]
- Pygame-CE Contributor - Mzivic (mzivic7)[https://github.com/mzivic7]
- Pygame-CE Contributor - nuclear pasta (aatle)[https://github.com/aatle]
- The Pygame-CE Community - [discord.com/invite/pygame](discord.com/invite/pygame)

- Kenney.nl - For the fantastic assets.

- Those that attend "So you want to make video games?"