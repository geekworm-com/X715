#!/usr/bin/env python3
# Min version 3.8

import asyncio
from typing import Final
from contextlib import asynccontextmanager
import lgpio

@asynccontextmanager
async def _gpio_servo():
     h = lgpio.gpiochip_open(0)
     if h >= 0:
          try:
               yield h
          finally:
               lgpio.gpiochip_close(h)
     else:
          raise RuntimeError("GPIO handle not acquired...")

async def _get_temp() -> float:
     """Get CPU temp"""
     SENSOR: Final[str] = "/sys/class/thermal/thermal_zone0/temp"

     with open(SENSOR, mode="r") as f:
          temp = float(f.read()) / 1000.00
          temp = float('%.2f' % temp)
          return temp

async def main():
     SERVO: Final[int] = 13
     FREQUENCY: Final[int] = 2500 #hz
     DEFAULT_DUTY_CYCLE: Final[int] = 100 # 100%

     async with _gpio_servo() as h:
          lgpio.gpio_claim_output(h, SERVO)
          lgpio.tx_pwm(h, SERVO, FREQUENCY, DEFAULT_DUTY_CYCLE)
          duty_cycle = DEFAULT_DUTY_CYCLE

          while True:
               temp: float = await _get_temp()

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

               lgpio.tx_pwm(h, SERVO, FREQUENCY, duty_cycle)

               print(f"Temp: {temp} --> {duty_cycle}%")

               await asyncio.sleep(3)

if __name__ == "__main__":
     asyncio.run(main())