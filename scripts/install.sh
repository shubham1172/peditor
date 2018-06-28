#!/usr/bin/env bash
sudo pip3 install -r requirements.txt
pyinstaller ./src/peditor.py --onefile
sudo cp ./dist/peditor /usr/local/bin