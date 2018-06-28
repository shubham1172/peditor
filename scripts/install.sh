#!/usr/bin/env bash
sudo pip3 install -r requirements.txt
pyinstaller peditor.py --onefile
sudo cp ./dist/peditor /usr/local/bin