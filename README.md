# X715

The PWN fan is not rotating when X715 is connected to PI 4, we need to to install the pwm fan control script

Tested on Ubuntu 21.10 arm64

https://ubuntu.com/tutorials/gpio-on-raspberry-pi#1-overview

```bash
sudo apt-get install -y python3-lgpio
sudo python3 pwm_fan_control.py
```
