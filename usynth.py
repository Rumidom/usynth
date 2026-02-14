import math
import time

# Define note frequencies (middle octave - 4) Hz
BASE_NOTES_HERTZ = {
    'C': 262,
    'C#': 277,
    'D': 294,
    'D#': 311,
    'E': 330,
    'F': 349,
    'F#': 370,
    'G': 392,
    'G#': 415,
    'A': 440,
    'A#': 466,
    'B': 494
}

sine_Lookup = [
0, 2057, 4107, 6140, 8149, 10126, 12062, 13952, 15786, 17557, 19260, 20886, 22431, 23886, 25247, 26509, 27666, 28714, 29648, 30466, 31163, 31738, 32187, 32509, 32702,
32767, 32702, 32509, 32187, 31738, 31163, 30466, 29648, 28714, 27666, 26509, 25247, 23886, 22431, 20886, 19260, 17557, 15786, 13952, 12062, 10126, 8149, 6140, 4107, 2057,
0, -2057, -4107, -6140, -8149, -10126, -12062, -13952, -15786, -17557, -19260, -20886, -22431, -23886, -25247, -26509, -27666, -28714, -29648, -30466, -31163, -31738, -32187,
-32509, -32702, -32767, -32702, -32509, -32187, -31738, -31163, -30466, -29648, -28714, -27666, -26509, -25247, -23886, -22431, -20886, -19260, -17557, -15786, -13952, -12062, -10126, -8149, -6140, -4107, -2057]

tri_Lookup = [0, 1311, 2621, 3932, 5243, 6553, 7864, 9175, 10485, 11796, 13107, 14417, 15728, 17039, 18350, 19660, 20971, 22282, 23592, 24903, 26214, 27524, 28835, 30146, 31456,
 32767, 31456, 30146, 28835, 27524, 26214, 24903, 23592, 22282, 20971, 19660, 18350, 17039, 15728, 14417, 13107, 11796, 10485, 9175, 7864, 6553, 5243, 3932, 2621, 1311,
 0, -1311, -2621, -3932, -5243, -6553, -7864, -9175, -10485, -11796, -13107, -14417, -15728, -17039, -18350, -19660, -20971, -22282, -23592, -24903, -26214, -27524, -28835,
 -30146, -31456, -32767, -31456, -30146, -28835, -27524, -26214, -24903, -23592, -22282, -20971, -19660, -18350, -17039, -15728, -14417, -13107, -11796, -10485, -9175, -7864, -6553, -5243, -3932, -2621, -1311]

saw_Lookup = [0, 655, 1311, 1966, 2621, 3277, 3932, 4587, 5243, 5898, 6553, 7209, 7864, 8519, 9175, 9830, 10485, 11141, 11796, 12451, 13107, 13762, 14417, 15073, 15728, 16384,
17039, 17694, 18350, 19005, 19660, 20316, 20971, 21626, 22282, 22937, 23592, 24248, 24903, 25558, 26214, 26869, 27524, 28180, 28835, 29490, 30146, 30801, 31456, 32112, -32767,
-32112, -31456, -30801, -30146, -29490, -28835, -28180, -27524, -26869, -26214, -25558, -24903, -24248, -23592, -22937, -22282, -21626, -20971, -20316, -19660, -19005, -18350,
-17694, -17039, -16384, -15728, -15073, -14417, -13762, -13107, -12451, -11796, -11141, -10485, -9830, -9175, -8519, -7864, -7209, -6553, -5898, -5243, -4587, -3932, -3277, -2621, -1966, -1311, -655]

LookupLen = len(sine_Lookup)
pi = 3.14159

@micropython.native
def getNoteFrequency(note) -> int:
    return (BASE_NOTES_HERTZ[note])

@micropython.viper
def sqr_wave(n_samples:int,half_n_samples:int,x:int) -> int:
    if x < half_n_samples:
        y = 32767
    else:
        y = -32767
    return y

@micropython.native
def saw_wave(n_samples:int,half_n_samples:int,x:int) -> int:
    index = round((x/n_samples)*(LookupLen-1))
    y = saw_Lookup[index]
    #y = (x/half_n_samples)*32767*(x<half_n_samples)
    #y += ((x/half_n_samples)*32767-65534)*(x>=half_n_samples)
    return int(y)

@micropython.native
def sine_wave(n_samples:int,half_n_samples:int,x:int) -> int:
    index = round((x/n_samples)*(LookupLen-1))
    y = sine_Lookup[index]
    return y

@micropython.native
def tri_wave(n_samples:int,half_n_samples:int,x:int) -> int:
    index = round((x/n_samples)*(LookupLen-1))
    y = tri_Lookup[index]
    #if x < quarter_n_samples:
    #    y = int( (x/quarter_n_samples)*32767 )
    #elif x < two_thirds_n_samples:
    #    y = int( (1-((x-quarter_n_samples)/quarter_n_samples))*32767 )
    #else:
        #y = int( (-1+(x-two_thirds_n_samples)/quarter_n_samples)*32767 )
    return y

@micropython.native
def generateByteWaveTable(sampleRate,func,freq,vol):
    w_len = 1/freq
    n_samples = int(w_len*sampleRate)
    half_n_samples = int(n_samples/2)
    #print(half_n_samples)
    output = bytearray(n_samples*2)
    for i in range(n_samples):
        out  = func(n_samples,half_n_samples,i)*vol
        out_bytes = out.to_bytes(2,'little')
        output[i*2] = out_bytes[0]
        output[(i*2)+1] = out_bytes[1]
    return output