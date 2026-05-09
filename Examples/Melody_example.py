import asyncio
import time
from machine import Pin,PWM

buzzer_pwm = PWM(Pin(22,Pin.OUT))  # create a PWM object on a pin
freq = {
'c4':261.63,
'd4':293.66,
'e4':329.63
}


async def note_osc(freq,volume,duration,pwm_obj):
    pwm_obj.init(freq=100_000)
    initTime = time.ticks_ms()
    oscTime = time.ticks_us()
    period = (1/freq)*1000000
    noteToggle = False
    while (time.ticks_ms() - initTime)<= duration:
        if (time.ticks_us()-oscTime) >= period:
            oscTime = time.ticks_us()
            noteToggle = not noteToggle
        if noteToggle:
            pwm_obj.duty_u16(int(65536*volume))
        else:
            pwm_obj.duty_u16(0)
    pwm_obj.duty_u16(0)

print(0)
asyncio.run(note_osc(freq['c4'],0.5,500,buzzer_pwm))
print(1)
asyncio.run(note_osc(freq['d4'],0.5,500,buzzer_pwm))
print(2)
asyncio.run(note_osc(freq['e4'],0.5,500,buzzer_pwm))
