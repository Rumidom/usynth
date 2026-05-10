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
        out  = int(func(n_samples,half_n_samples,i)*vol)
        out_bytes = out.to_bytes(2,'little')
        output[i*2] = out_bytes[0]
        output[(i*2)+1] = out_bytes[1]
    return output

class secondOrderLowPass:
    @micropython.native
    def __init__(self,cutoff,Q_Res,sampleRate,clipping = 32767):
        samplingInterval = 1/sampleRate
        wc = cutoff*2*math.pi
        tetac = wc*samplingInterval
        self.y1 = 0 
        self.y2 = 0
        self.a1 = -2*Q_Res*math.cos(tetac)
        self.a2 = Q_Res**2
        self.b0 = 0.2
        self.clipping = clipping
        print(self.a1,self.a2)

    @micropython.native
    def solveFunc(self,n_samples,half_n_samples,x):
        y = self.oscFunc(n_samples,half_n_samples,x)
        return self.solve(y)
    
    @micropython.native
    def solve(self,x):
        y = x*self.b0 - self.y1*self.a1 - self.y2*self.a2 
        self.y2 = self.y1
        self.y1 = y
        if y < -self.clipping:
            return -self.clipping
        elif y > self.clipping:
            return self.clipping
        return y


class BiquadLowPass:
    @micropython.native
    def __init__(self,cutoff,Q_Res,sampleRate,oscilatorFunc,clipping = 32767):
        samplingInterval = 1/sampleRate
        wc = cutoff*2*math.pi
        tetac = wc*samplingInterval
        alpha = math.sin(tetac)/(2*Q_Res)
        self.y0 = 0 
        self.y1 = 0
        self.y2 = 0
        self.x1 = 0 
        self.x2 = 0 
        self.a0 = 1 + alpha
        self.a1 = -2*math.cos(tetac)/self.a0
        self.a2 = 1 - alpha/self.a0
        self.b1 = 1 - math.cos(tetac)/self.a0
        self.b0 = (self.b1/2)/self.a0
        self.b2 = (self.b1/2)/self.a0
        self.clipping = clipping
        self.oscFunc = oscilatorFunc
        print(self.a0,self.a1,self.a2,self.b0,self.b1,self.b2)
        
    @micropython.native
    def setCoefficients(self,cutoff,Q_Res,sampleRate,clipping = 32767):
        samplingInterval = 1/sampleRate
        wc = cutoff*2*math.pi
        tetac = wc*samplingInterval
        alpha = math.sin(tetac)/(2*Q_Res)
        self.a0 = 1 + alpha
        self.a1 = -2*math.cos(tetac)/self.a0
        self.a2 = 1 - alpha/self.a0
        self.b1 = 1 - math.cos(tetac)/self.a0
        self.b0 = (self.b1/2)/self.a0
        self.b2 = (self.b1/2)/self.a0
        self.clipping = clipping
        
    @micropython.native
    def solveFunc(self,n_samples,half_n_samples,x):
        y = self.oscFunc(n_samples,half_n_samples,x)
        return self.solve(y)
            
    @micropython.native
    def solve(self,x):
        y = x*self.b0+self.x1*self.b1+self.x2*self.b2 - self.y1*self.a1 - self.y2*self.a2 
        self.y2 = self.y1
        self.y1 = y
        self.x2 = self.x1
        self.x1 = x
        if y < -self.clipping:
            return -self.clipping
        elif y > self.clipping:
            return self.clipping
        return y

def midi_read_variable_length(data, offset):
    # reads a variable acording to the midi the bottom 7 bits are used for value
    # if the 8th bit is 0 the value is done if the 8th bit is 1 grabs one more byte
    value = 0
    while True:
        byte = data[offset]
        offset += 1
        value = (value << 7) | (byte & 0x7F)
        if not (byte & 0x80):
            break
    return value, offset
    
def readMidiFile(path):
    src = open(path, "rb")
    current_ticks = 0
    tempo = 500000
    ticks_per_quarter = 480
    header_dict = {}
    current_note = {}
    melody_list = []
    
    while True:
        chunkID = src.read(4)
        chunklen = int.from_bytes(src.read(4))
        chunk = src.read(chunklen)
        delta_times = False
        if chunkID == b'MThd':
            formt, ntracks, header_dict['tickdiv']  = struct.unpack('>HHH', chunk[0:6])
            header_dict['µs_per_tick'] = tempo/header_dict['tickdiv'] 
            if formt != 1:
                    print('Only format 1 MIDI files are suported')
            #print('Header: ', header_dict)
        elif chunkID == b'MTrk':
            offset = 0
            #print("track:")
            #print(chunk)
            while offset < chunklen:
                # Read delta time
                delta, offset = midi_read_variable_length(chunk, offset)
                current_ticks += delta
                event_status = chunk[offset]
                offset += 1
                if event_status == 0xFF: #Meta event
                    meta_type = chunk[offset]
                    offset += 1
                    meta_length = chunk[offset]
                    offset += 1
                    meta_data = chunk[offset:offset+meta_length]
                    offset += meta_length
                    if meta_type == 0x2F and meta_data == b'':
                        pass
                        #print(current_ticks,"- Metadata > End of track")
                        
                    elif meta_type == 0x03:
                        pass
                        #print(current_ticks,"- Metadata > Track/Sequence name > ",meta_data)
                    elif meta_type == 0x51:
                        tempo = struct.unpack('>i', b'\x00'+meta_data)[0]
                        header_dict['µs_per_tick'] = tempo/header_dict['tickdiv']
                        header_dict['bpm'] = 60000000/tempo
                        #print(current_ticks,"- Metadata > Tempo > ",tempo)
                    elif meta_type == 0x58:
                        num, denom, clocks_per_clck, notes_per_beat = struct.unpack('>bbbb', meta_data)
                        #print(current_ticks,"- Metadata > Time signature >",num, denom, clocks_per_clck, notes_per_beat)
                    else:
                        pass
                        #print(current_ticks,'- type - ',meta_type,' - Meta Data > ',meta_data)
                elif event_status//16 == 9 or event_status//16 == 8:
                    note = chunk[offset]
                    offset += 1
                    vel = chunk[offset]
                    offset += 1
                    event_time = int(current_ticks*header_dict['µs_per_tick'])
                    if event_status//16 == 9:
                        note_ac = 'Note On'
                        current_note = {'n':note,'st':current_ticks}
                    else:
                        note_ac = 'Note Off'
                        current_note['delt'] = current_ticks-current_note['st']
                        melody_list.append(current_note)
                    
                    #print(note_ac+' > n:',note,' v:',vel,'t:',event_time)
                elif event_status//16 == 11:
                    controller = chunk[offset]
                    offset += 1
                    value = chunk[offset]
                    offset += 1
                    #print(current_ticks,' - controller > ctrl: ',controller,'val: ',value)
                elif event_status//16 == 12:
                    pgrm_n = chunk[offset]
                    offset += 1
                    #print(current_ticks,' - program > pgrm_n: ',pgrm_n)
                elif event_status//16 == 14:
                    lsb = chunk[offset]
                    offset += 1
                    msb = chunk[offset]
                    offset += 1
                    #print(current_ticks,' - pitchBend > lsb: ',lsb,' msb: ',msb)
                else:
                    pass
                    #print(current_ticks,' - ',hex(event_status))
        else:
            return({'header':header_dict,'melody':melody_list})