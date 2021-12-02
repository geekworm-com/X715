#!/usr/bin/env python3
# Min version 3.8
"""Raspberry Pi 4, Geekwork X715, modern Ubuntu fan control

Requires python 3.8 or newer, which is included with Ubuntu 20.04 LTS and newer.
Requires lpgio:
     `apt install python3-lgpio`

Examples:
     python3 -OO pwm_fan_control.py
     python3 -OO pwm_fan_control.py --gpio 13
     python3 -OO pwm_fan_control.py --gpiochip 0 --gpio 13
"""

import asyncio
import argparse
import contextlib
import pathlib
import signal
from typing import Any, Final

# !!! This module writes to CWD at import time !!!
import lgpio


@contextlib.contextmanager
def _gpiochip(gpiochip: int) -> Any:
     """Context manager for lgpio.gpiochip
     
     Example:
          import lgpio
          with _gpiochip(0) as handle:
               with _gpio_claim_output(handle, 12):
                    lpgio.gpio_write(handle, 12, 1)
     """
     handle: Final[Any] = lgpio.gpiochip_open(gpiochip)
     # Nullable logic, compare against the positive case and invert if needed
     if not handle >= 0:
          raise lgpio.error(f"GPIO handle not acquired: {handle}")

     try:
          yield handle
     finally:
          error_code = lgpio.gpiochip_close(handle)
          # Nullable logic, compare against the positive case and invert if needed
          if not error_code >= 0:
               raise lgpio.error(f"GPIO handle not released: {handle} {error_code}")


@contextlib.contextmanager
def _gpio_claim_output(handle: Any, gpio: int) -> int:
     """Context manager for lgpio gpio output
     
     Example:
          import lgpio
          with _gpiochip(0) as handle:
               with _gpio_claim_output(handle, 12):
                    lpgio.gpio_write(handle, 12, 1)
     """
     error_code = lgpio.gpio_claim_output(handle, gpio)
     # Nullable logic, compare against the positive case and invert if needed
     if not error_code >= 0:
          raise lgpio.error(f"GPIO output not claimed: {gpio} {error_code}")

     try:
          yield gpio
     finally:
          error_code = lgpio.gpio_free(handle, gpio)
          # Nullable logic, compare against the positive case and invert if needed
          if not error_code >= 0:
               raise lgpio.error(f"GPIO output not freed: {gpio} {error_code}")

async def _get_temp() -> float:
     """Get CPU temp"""
     SENSOR_FILE: Final[pathlib.Path] = pathlib.Path("/sys/class/thermal/thermal_zone0/temp")

     with open(SENSOR_FILE, mode="r") as f:
          raw: str = f.read()
          temp = float(raw) / 1000.00
          temp = float('%.2f' % temp)
          assert temp is not None
          return temp

def _temp_to_duty_cycle(temp: float) -> int:
     """Fan curve
     
     Original curve provided by the vendor.
     """
     assert temp is not None

     duty_cycle: int

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

async def fan_control_chiphandle(h: int, gpio: int):
     """Task for controlling the fan based on temp. Runs until cancelled.
     
     Use when you have an already open gpiochip handle.

     Example:
          with _gpiochip(gpiochip) as h:
               fan_task: Final[asyncio.Task] = asyncio.create_task(fan_control_chiphandle(h, 13), name="fan control")
               lights_task: Final[asyncio.Task] = asyncio.create_task(light_control_chiphandle(h), name="light control")

               await asyncio.gather(fan_task, lights_task)
     """

     FREQUENCY: Final[int] = 10 #hz
     
     with _gpio_claim_output(h, gpio):
          try:
               while True:
                    temp = await _get_temp()

                    assert temp is not None

                    duty_cycle = _temp_to_duty_cycle(temp)

                    assert 100 >= duty_cycle >= 0

                    queue_length = lgpio.tx_pwm(h, gpio, FREQUENCY, duty_cycle)
                    # Nullable logic, compare against the positive case and invert if needed
                    if not queue_length >= 0:
                         raise lgpio.error(f"GPIO unable to set PWM: {queue_length} {duty_cycle}")

                    print(f"Temp: {temp} --> {duty_cycle}%")

                    await asyncio.sleep(3)

          except asyncio.CancelledError:
               print("Cancelling...")
               duty_cycle = 0
               queue_length = lgpio.tx_pwm(h, gpio, FREQUENCY, duty_cycle)
               # Nullable logic, compare against the positive case and invert if needed
               if not queue_length >= 0:
                    raise lgpio.error(f"GPIO unable to set PWM: {queue_length} {duty_cycle}")

               raise

async def fan_control(gpiochip: int, gpio: int):
     """Task for controlling the fan based on temp. Runs until cancelled.
     
     Opens and closes the chiphandle for you.
     
     Example:
          task: Final[asyncio.Task] = asyncio.create_task(fan_control(args.gpiochip, args.gpio), name="fan control")
          await task #forever
     """

     with _gpiochip(gpiochip) as h:
          await fan_control_chiphandle(h, gpio)

async def main():
     """Main entry point for PWM fan control"""
     parser = argparse.ArgumentParser(add_help=True)

     DEFAULT_GPIOCHIP: Final[int] = 0
     parser.add_argument(
          '--gpiochip',
          type=int,
          default=DEFAULT_GPIOCHIP,
          help=("GPIO chip to use. "
                f"The Rpi4 hat is {DEFAULT_GPIOCHIP}, which is selected by default.")
     )

     DEFAULT_GPIO: Final[int] = 13
     parser.add_argument(
          '--gpio', 
          type=int, 
          default=DEFAULT_GPIO,
          help=("GPIO mask to control the fan with. "
                f"Geekwork X715 uses mask {DEFAULT_GPIO}, which is selected by default."))

     args: Final[argparse.Namespace] = parser.parse_args()

     task: Final[asyncio.Task] = asyncio.create_task(fan_control(args.gpiochip, args.gpio), name="fan control")

     loop = asyncio.get_running_loop()
     for sig in [signal.SIGINT, signal.SIGHUP, signal.SIGTERM]:
          loop.add_signal_handler(sig, lambda sig=sig: task.cancel(sig))
     del loop, sig

     try:
          await task
     except asyncio.CancelledError:
          print("Cancelled")


if __name__ == "__main__":
     asyncio.run(main())
