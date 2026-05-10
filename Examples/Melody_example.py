import time
import usynth
from machine import Pin,PWM

buzzer_pwm = PWM(Pin(22,Pin.OUT))  # create a PWM object on a pin
A = 440; # a is 440 hz...

def midiNoteToFreq(note):
    return (A / 32) * ((note - 9) / 12)**2

def note_osc(freq,volume,duration,pwm_obj):
    pwm_obj.init(freq=300_000)
    initTime = time.ticks_us()
    oscTime = time.ticks_us()
    period = (1/freq)*1000000
    noteToggle = False
    while (time.ticks_us() - initTime)<= duration:
        if (time.ticks_us()-oscTime) >= period:
            oscTime = time.ticks_us()
            noteToggle = not noteToggle
        if noteToggle:
            pwm_obj.duty_u16(int(65536*volume))
        else:
            pwm_obj.duty_u16(0)
    pwm_obj.duty_u16(0)

midi_dict = usynth.readMidiFile('Kid Dracula - Go-Go at the Great Castle.mid')

last_note_ticks = 0
volume = 0.5
for item in midi_dict['melody']:
    if last_note_ticks != item['st']:
        wt_ticks = item['st']-last_note_ticks
        wt_us = int(midi_dict['header']['us_per_tick']*wt_ticks)
        time.sleep_us(wt_us)
    last_note_ticks = item['delt']+item['st']
    freq = midiNoteToFreq(item['n'])
    delt_ticks = item['delt']
    delt_us = int(midi_dict['header']['us_per_tick']*delt_ticks)
    note_osc(freq,volume,delt_us,buzzer_pwm)
        
