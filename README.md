# Fan control for Geekworm X715 on Ubuntu 22.04 LTS 

Tested on RPI4, which is arm64/aarch64

Installation:
```bash
sudo apt install build-essential
sudo make install
```

On first installation, this modifies the udev rules that gpiod honors to allow the dialout group to talk to the gpiochip. You may need to reboot for the kernel to reload these rules.

Reading the fan speed:

```bash
make venv
. ./.venv/bin/activate
# Can't open the gpiochip?
# usermod -aG dialout $USER
python3 read_fan_speed.py
```

# See also

- https://blogjawn.stufftoread.com/raspberry-pi-gpio-tutorial.html
- https://waldorf.waveform.org.uk/2021/the-pins-they-are-a-changin.html
- https://www.udoo.org/forum/threads/gpio-permissions-for-libgpiod-sudo-or-not.32453/