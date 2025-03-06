import math
import random
import wave
import array
import os
import random
import time

class Synth8Bit:
    def __init__(self, sample_rate=44100, channels=1, seed=None):
        self.sample_rate = sample_rate
        self.channels = channels
        self.frequency = 440.0
        self.amplitude = 0.5
        self.duty_cycle = 0.5
        self.waveform_type = 'square'
        self.all_samples = []
        self.seed = seed if seed is not None else int(time.time() * 1000)
        self.rng = random.Random(self.seed)

    def generate_sample(self, time_val):
        if self.waveform_type == 'square':
            return 1.0 if (time_val * self.frequency) % 1 < self.duty_cycle else -1.0
        elif self.waveform_type == 'sine':
            return math.sin(2 * math.pi * self.frequency * time_val)
        elif self.waveform_type == 'triangle':
            return 2 * abs(2 * (time_val * self.frequency % 1) - 1) - 1
        elif self.waveform_type == 'sawtooth':
            return 2 * (time_val * self.frequency % 1) - 1
        else:
            return 0.0

    def add_note(self, duration=1.0):
        num_frames = int(self.sample_rate * duration)
        samples = [self.amplitude * self.generate_sample(i / self.sample_rate) for i in range(num_frames)]
        self.all_samples.extend(samples)

    def save_to_wav(self, filename):
        samples_clipped = [max(-1.0, min(1.0, sample)) for sample in self.all_samples]
        samples_int8 = array.array('b', [int(sample * 127) for sample in samples_clipped])
        with wave.open(filename, 'w') as wav_file:
            wav_file.setnchannels(self.channels)
            wav_file.setsampwidth(1)
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(samples_int8.tobytes())

    def set_frequency(self, frequency):
        self.frequency = frequency

    def set_amplitude(self, amplitude):
        self.amplitude = amplitude

    def set_waveform(self, waveform_type):
        self.waveform_type = waveform_type

    def get_seed(self):
        return self.seed
def synth(seed=None, dur=10):
    synth = Synth8Bit(sample_rate=22050, seed=seed)
    
    print(f"Using seed: {synth.get_seed()}")

    freq_weights = {
        440.00: 10,  # A4 - common baseline
        493.88: 8,   # B4 - common melody
        523.25: 8,   # C5 - common melody
        587.33: 7,   # D5
        659.25: 7,   # E5
        329.63: 4,   # E4 - lower register
        392.00: 4,   # G4 - harmony
        698.46: 4,   # F5 - higher notes
        783.99: 3,   # G5
        220.00: 2,   # A3 - bass notes
        880.00: 2,   # A5 - high notes
        1046.50: 1,  # C6 - very high (sparse use)
    }

    frequencies = []
    weights = []
    for freq, weight in freq_weights.items():
        frequencies.append(freq)
        weights.append(weight)

    waveforms = {
        'square': 0.5,    # Classic 8-bit lead
        'triangle': 0.3,  # Softer sound
        'sawtooth': 0.1   # Harsh effect sounds
    }

    total_time = 0
    while total_time < dur:
        freq = synth.rng.choices(frequencies, weights=weights, k=1)[0]
        synth.set_frequency(freq)
        
        waveform = synth.rng.choices(list(waveforms.keys()), 
                                   weights=list(waveforms.values()), k=1)[0]
        synth.set_waveform(waveform)
        
        duration = synth.rng.choice([0.1, 0.2, 0.3])
        synth.set_amplitude(synth.rng.uniform(0.4, 0.7))
        synth.add_note(duration)
        total_time += duration
        print(f"Freq: {freq:.2f} Hz, Wave: {waveform}")

    output_path = os.path.join(os.path.expanduser('~'), f'8bit_tune_{synth.get_seed()}.wav')
    synth.save_to_wav(output_path)


synth(43242895734852703587340573409878437268957389679805763489027589478695437258960532, 15)