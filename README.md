# X715

The PWN fan is not rotating when X715 is connected to PI 4, we need to to install the pwm fan control script

The pytone file need pigpiod library, so we need to install it firstly.

```
sudo apt-get install -y pigpio python-pigpio python3-pigpio
sudo apt-get install -y python3-rpi.gpio

sudo systemctl enable pigpiod
git clone https://github.com/geekworm-com/x715
sudo reboot

cd ~
python3 /home/pi/x715/pwm_fan_control.py&
```

Or refer to WIKI: https://wiki.geekworm.com/X715_Software
