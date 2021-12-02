# Fan control for Geekworm X715 on Ubuntu 21.04 and newer

Tested on Ubuntu 21.10 arm64

```bash
sudo python3 -OO pwm_fan_control.py
```


```bash
sudo useradd -M --shell /bin/false gpiousr
sudo usermod -L gpiousr
sudo groupadd gpiod
sudo usermod -G gpiod gpiousr
echo '# udev rules for gpio port access through libgpiod
SUBSYSTEM=="gpio", KERNEL=="gpiochip[0-4]", GROUP="gpiod", MODE="0660"' | sudo tee /etc/udev/rules.d/60-gpiod.rules

sudo mkdir -p /opt/job/fan_control
sudo cp ./pwm_fan_control.py /opt/job/fan_control/
sudo chmod -R 755 /opt/job/fan_control/

#test
pushd /tmp
sudo -u gpiousr python3 -OO /opt/job/fan_control/pwm_fan_control.py
popd

#install
sudo cp ./fan_control.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable fan_control
sudo service fan_control start
sudo journalctl -f -u fan_control

```

# See also

- https://blogjawn.stufftoread.com/raspberry-pi-gpio-tutorial.html
- https://waldorf.waveform.org.uk/2021/the-pins-they-are-a-changin.html
- https://www.udoo.org/forum/threads/gpio-permissions-for-libgpiod-sudo-or-not.32453/