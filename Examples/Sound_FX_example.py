import os
import math
import struct
import usynth
import time
from machine import I2S
from machine import Pin,PWM


SAMPLE_RATE = 8000
SAMPLE_DURATION = 1/SAMPLE_RATE
with open("Jump_[264828]_8000_.dat", "rb") as data_file:
    samples = data_file.read()


buzzer_pwm = PWM(Pin(22,Pin.OUT), freq=100_000)  # create a PWM object on a pin

last_time = time.ticks_us()
i = 0
while True:
    if i >= len(samples):
        break
    if (time.ticks_us() - last_time) > SAMPLE_DURATION:
        buzzer_pwm.duty_u16(samples[i]*257)
        #print(samples[i])
        last_time = time.ticks_us()
        i += 1

        