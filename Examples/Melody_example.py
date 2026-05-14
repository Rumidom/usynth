import time
import usynth
import _thread
from machine import Pin,PWM

buzzer_pwm = PWM(Pin(22,Pin.OUT))  # create a PWM object on a pin
A = 440; # a is 440 hz...

@micropython.native
def midiNoteToFreq(note):
    return A*(2**((note - 69) / 12))

core1_free = True

def note_osc(freq,volume,duration,pwm_obj):
    pwm_obj.freq(300_000)
    pwm_obj.duty_u16(0)
    global core1_free
    core1_free = False
    initTime = time.ticks_us()
    oscTime = time.ticks_us()
    period = (1/freq)*1000000
    halfperiod =  period/2
    noteToggle = False
    vol = int(65536*volume)
    while (time.ticks_us()-initTime)<= duration:
        if (time.ticks_us()-oscTime) >= halfperiod:
            oscTime = time.ticks_us()
            noteToggle = not noteToggle
        if noteToggle:
            pwm_obj.duty_u16(vol)
        else:
            pwm_obj.duty_u16(0)
    core1_free = True

#midi_dict = usynth.readMidiFile('Kid Dracula - Go-Go at the Great Castle.mid')
midi_dict = usynth.readMidiFile('game_over.mid')

last_note_ticks = 0
volume = 0.3
for item in midi_dict['melody']:
    if last_note_ticks != item['st']:
        wt_ticks = item['st']-last_note_ticks
        wt_us = int(midi_dict['header']['us_per_tick']*wt_ticks)
        time.sleep_us(wt_us)
    last_note_ticks = item['delt']+item['st']
    freq = midiNoteToFreq(item['n'])
    delt_ticks = item['delt']
    delt_us = int(midi_dict['header']['us_per_tick']*delt_ticks)
    while not core1_free:
        time.sleep_us(1)
    _thread.start_new_thread(note_osc,(freq,volume,delt_us,buzzer_pwm))
    time.sleep_us(5)
