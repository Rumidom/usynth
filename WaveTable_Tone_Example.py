import os
import math
import struct
import usynth
from machine import I2S
from machine import Pin

BSCK_PIN = 19
WSEL_PIN = 20
DIN_PIN = 18
TONE_FREQUENCY = usynth.getNoteFrequency('C')
WAVE_FORM = usynth.sine_wave
SAMPLE_RATE = 11025

audio_out = I2S(
    0,
    sck=Pin(BSCK_PIN),
    ws=Pin(WSEL_PIN),
    sd=Pin(DIN_PIN),
    mode=I2S.TX,
    bits=16,
    format=I2S.MONO,
    rate=SAMPLE_RATE,
    ibuf=2000,
)



# this is the wave form sampled over one single wavelenght  
samples = usynth.generateByteWaveTable(SAMPLE_RATE,WAVE_FORM,TONE_FREQUENCY,0.5)

# continuously write tone sample buffer to an I2S DAC
while True:
    audio_out.write(samples)

audio_out.deinit()