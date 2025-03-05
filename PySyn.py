"""
TODO:
- Add a method to change the waveform type (square, sine, triangle, sawtooth)
- Fix save location
- Add more randomness to note selection
"""

import numpy as np
import math
import random
import wave

class Synth8Bit:
    def __init__(self, sample_rate=44100, channels=1):
        self.sample_rate = sample_rate
        self.channels = channels
        self.frequency = 440.0
        self.amplitude = 0.5
        self.duty_cycle = 0.5
        self.waveform_type = 'square'
        self.all_samples = np.array([], dtype=np.float32)  # Store all samples

    def generate_sample(self, time_val):
        # Same as before
        if self.waveform_type == 'square':
            return 1.0 if (time_val * self.frequency) % 1 < self.duty_cycle else -1.0
        elif self.waveform_type == 'sine':
            return math.sin(2 * math.pi * self.frequency * time_val)
        elif self.waveform_type == 'triangle':
            return 2 * abs((time_val * self.frequency) - math.floor((time_val * self.frequency) + 0.5)) - 1
        elif self.waveform_type == 'sawtooth':
            return 2 * ((time_val * self.frequency) - math.floor(time_val * self.frequency)) - 1
        else:
            return 0.0

    def add_note(self, duration=1.0):
        num_frames = int(self.sample_rate * duration)
        samples = np.array([self.amplitude * self.generate_sample(i / self.sample_rate)
                          for i in range(num_frames)], dtype=np.float32)
        self.all_samples = np.concatenate([self.all_samples, samples])

    def save_to_wav(self, filename):
        # Convert to int16 format, clipping values to [-1, 1]
        samples_clipped = np.clip(self.all_samples, -1.0, 1.0)
        samples_int16 = (samples_clipped * 32767).astype(np.int16)
        with wave.open(filename, 'w') as wav_file:
            wav_file.setnchannels(self.channels)  # Set number of channels
            wav_file.setsampwidth(2)  # 2 bytes for int16
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(samples_int16.tobytes())

    def set_frequency(self, frequency):
        self.frequency = frequency

    def set_amplitude(self, amplitude):
        self.amplitude = amplitude

    def set_waveform(self, waveform_type):
        self.waveform_type = waveform_type

if __name__ == '__main__':
    synth = Synth8Bit()
    # C major scale frequencies
    frequencies = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25]
    
    synth.set_waveform('square')

    # Generate 3 minutes of music (180 seconds)
    total_time = 0
    current_freq_index = 0
    last_two_indices = [-1, -1]  # Keep track of last two frequency indices
    
    while total_time < 120:
        # Get potential new index within 4 steps of current index
        new_index = current_freq_index + random.randint(-2, 2)
        new_index = max(0, min(new_index, len(frequencies) - 1))
        
        # Keep generating new indices if the current one was used in last two times
        while new_index in last_two_indices:
            direction = random.choice([-1, 1])
            new_index = current_freq_index + direction
            new_index = max(0, min(new_index, len(frequencies) - 1))
        
        # Update history
        last_two_indices[0] = last_two_indices[1]
        last_two_indices[1] = new_index
        current_freq_index = new_index
        
        freq = frequencies[current_freq_index]
        synth.set_frequency(freq)
        duration = random.uniform(0.2, 0.5)
        synth.add_note(duration)
        total_time += duration
        print(f"""Frequency:{freq:.2f}""")

    # Save to WAV file in Documents folder
    import os
    documents_path = os.path.join(os.path.expanduser('~'), 'Documents')
    output_path = os.path.join(documents_path, 'output_song.wav')
    synth.save_to_wav(output_path)
