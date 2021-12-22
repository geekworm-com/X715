#!/usr/bin/env python3
import asyncio
import time

import lgpio

import X715_fan


class Tachometer:

    t = time.time()
    rpm = 0

    def fell(self, a, b, c, d):
        PULSE = 2

        dt = time.time() - self.t
        if dt < 0.005: return

        freq = 1 / dt
        self.rpm = (freq / PULSE) * 60
        self.t = time.time()


async def main():
    TACH = 16
    WAIT_TIME = 1

    tach = Tachometer()
    with X715_fan._gpiochip(0) as handle:
        with X715_fan._gpio_claim_alert(handle, TACH, lgpio.FALLING_EDGE,
                                        lgpio.SET_BIAS_PULL_UP) as h2:
            with X715_fan._gpio_callback(handle, TACH, lgpio.FALLING_EDGE,
                                         tach.fell) as cbk:

                for i in range(0, 30):
                    print(f"{tach.rpm:.0f} RPM")
                    tach.rpm = 0
                    await asyncio.sleep(WAIT_TIME)


if __name__ == "__main__":
    asyncio.run(main())
