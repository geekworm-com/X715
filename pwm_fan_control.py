#!/usr/bin/env python3
# Min version 3.8

import asyncio
from contextlib import contextmanager
from typing import Any, Final

import lgpio


@contextmanager
def _gpio_servo() -> Any:
     handle = lgpio.gpiochip_open(0)
     if handle >= 0:
          try:
               yield handle
          finally:
               lgpio.gpiochip_close(handle)
     else:
          raise RuntimeError("GPIO handle not acquired...")

@contextmanager
def _gpio_claim_output(handle: Any, gpio: int) -> int:
     error_code = lgpio.gpio_claim_output(handle, gpio)
     if error_code >= 0:
          try:
               yield gpio
          finally:
               lgpio.gpio_free(handle, gpio)
     else:
          raise RuntimeError(f"GPIO output not acquired: {error_code}")

async def _get_temp() -> float:
     """Get CPU temp"""
     SENSOR: Final[str] = "/sys/class/thermal/thermal_zone0/temp"

     with open(SENSOR, mode="r") as f:
          temp = float(f.read()) / 1000.00
          temp = float('%.2f' % temp)
          return temp

def _temp_to_duty_cycle(temp: float) -> int:
     assert temp is not None

     if temp < 30:
          duty_cycle = 0
     elif 50 > temp >= 30:
          duty_cycle = 40
     elif 55 > temp >= 50:
          duty_cycle = 50
     elif 60 > temp >= 55:
          duty_cycle = 75
     elif 65 > temp >= 60:
          duty_cycle = 90
     else:
          duty_cycle = 100

     assert 100 >= duty_cycle >= 0

     return duty_cycle

async def main():
     SERVO: Final[int] = 13
     FREQUENCY: Final[int] = 10000 #hz
     DEFAULT_DUTY_CYCLE: Final[int] = 100 # 100%
     duty_cycle = DEFAULT_DUTY_CYCLE

     with _gpio_servo() as h:
          with _gpio_claim_output(h, SERVO) as _:
               try:
                    lgpio.tx_pwm(h, SERVO, FREQUENCY, DEFAULT_DUTY_CYCLE)
                    while True:
                         temp = await _get_temp()

                         duty_cycle = _temp_to_duty_cycle(temp)

                         lgpio.tx_pwm(h, SERVO, FREQUENCY, duty_cycle)

                         print(f"Temp: {temp} --> {duty_cycle}%")

                         await asyncio.sleep(3)

               finally:
                    print("Cleanup...")
                    lgpio.tx_pwm(h, SERVO, 0, 0)

if __name__ == "__main__":
     asyncio.run(main())
