import os
import math
import struct
import usynth
from machine import I2S
from machine import Pin

BSCK_PIN = 19
WSEL_PIN = 20
DIN_PIN = 18
TONE_FREQUENCY = usynth.getNoteFrequency('A')
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

Enc_A = machine.Pin(10, Pin.IN, Pin.PULL_UP)
Enc_B = machine.Pin(11, Pin.IN, Pin.PULL_UP)
Enc_BNT = machine.Pin(12, Pin.IN, Pin.PULL_UP)
adc = machine.ADC(machine.Pin(27))        # create an ADC object acting on a pin

class RotaryEncoder():
    def __init__(self,Enc_Pin_A,Enc_Pin_B,Enc_BNT_Pin,max_value=100,min_value=0):
        Enc_Pin_A.irq(trigger=Pin.IRQ_FALLING, handler=self.A_interrupt)
        Enc_Pin_B.irq(trigger=Pin.IRQ_RISING, handler=self.B_interrupt)
        Enc_BNT_Pin.irq(trigger=Pin.IRQ_FALLING, handler=self.BNT_interrupt)
        self.Pin_B = Enc_Pin_B
        self.Pin_A = Enc_Pin_A
        self.Pin_BNT = Enc_BNT_Pin
        self.value = 0
        self.triggered = False
        self.dir = False
        self.max_value = max_value
        self.min_value = min_value
    
    def BNT_interrupt(self,pin):
        self.value = 0
        
    def A_interrupt(self,pin):
        #print("Interrupt A", pin)
        if not self.triggered and pin.value:
            self.triggered = True
            if self.Pin_B.value():
                #print('dir +')
                self.dir = True
            else:
                #print('dir -')
                self.dir = False
                
    def B_interrupt(self,pin):
            if self.Pin_B.value and self.Pin_A.value and self.triggered: 
                self.triggered = False
                #print(self.value)
                if self.dir:
                    if self.value < self.max_value:
                        self.value += 1
                else:
                    if self.value > self.min_value:
                        self.value -= 1

lastCutoff = 0
lastResonance = 0
cutoff = 0

fltr = usynth.BiquadLowPass(cutoff,0.5,SAMPLE_RATE,usynth.sqr_wave)
r0 = RotaryEncoder(Enc_A,Enc_B,Enc_BNT,max_value=100)
samples = usynth.generateByteWaveTable(SAMPLE_RATE,fltr.solveFunc,TONE_FREQUENCY,0.9)
resonance = round(adc.read_u16()/65535 , 1)
update_flag = False

while True:
    cutRead = r0.value
    if lastCutoff != cutRead:
        lastCutoff = cutRead
        update_flag = True
        
    if update_flag:
        update_flag = False
        fltr.setCoefficients(cutRead,0.5,SAMPLE_RATE)
        samples = usynth.generateByteWaveTable(SAMPLE_RATE,fltr.solveFunc,TONE_FREQUENCY,0.2)
        print(cutRead)
    audio_out.write(samples)

audio_out.deinit()
print("Done")