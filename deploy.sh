#!/usr/bin/env bash

set -e

cd /opt/kiberkot

echo "Installing dependencies..."
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

echo "Restarting bot service..."
if [ -x /usr/bin/systemctl ]; then
    sudo /usr/bin/systemctl restart kiberkot-bot
elif [ -x /bin/systemctl ]; then
    sudo /bin/systemctl restart kiberkot-bot
else
    echo "systemctl not found"
    exit 1
fi

echo "Deploy finished."
