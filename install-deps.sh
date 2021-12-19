#!/usr/bin/env bash

apt install python3-venv python3-lgpio libsystemd-dev

getent group gpio || groupadd gpio

if [ -f "/etc/udev/rules.d/60-gpio.rules" ]; then
    install --group root --owner root --mode 0644 ./60-gpio.rules /etc/udev/rules.d/
fi