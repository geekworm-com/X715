#!/usr/bin/env bash

apt install python3-dev python3-venv python3-lgpio libsystemd-dev python3-pkgconfig gpiod

if [ ! -f "/etc/udev/rules.d/60-gpio.rules" ]; then
    install --group root --owner root --mode 0644 ./60-gpio.rules /etc/udev/rules.d
fi