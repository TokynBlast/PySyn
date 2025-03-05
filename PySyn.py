import math
import random
import wave
import array
import os
import struct
import time
import random

class Synth8Bit:
    def __init__(self, sample_rate=44100, channels=1):
        self.sample_rate = sample_rate
        self.channels = channels
        self.frequency = 440.0
        self.amplitude = 0.5
        self.duty_cycle = 0.5
        self.waveform_type = 'square'
        self.all_samples = []  # Store all samples

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
        # Convert to int8 format, clipping values to [-1, 1]
        samples_clipped = [max(-1.0, min(1.0, sample)) for sample in self.all_samples]
        samples_int8 = array.array('b', [int(sample * 127) for sample in samples_clipped])
        with wave.open(filename, 'w') as wav_file:
            wav_file.setnchannels(self.channels)  # Set number of channels
            wav_file.setsampwidth(1)  # 1 byte for int8
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(samples_int8.tobytes())

    def set_frequency(self, frequency):
        self.frequency = frequency

    def set_amplitude(self, amplitude):
        self.amplitude = amplitude

    def set_waveform(self, waveform_type):
        self.waveform_type = waveform_type

def get_random_bytes_from_files():
    """Get random bytes from random system files"""
    system_paths = (['/dev', '/proc', '/sys', '/var/log', os.getcwd()] if os.name != 'nt' 
                   else ['C:\\Windows\\System32', os.getcwd()])
    try:
        base_dir = random.choice(system_paths)
        for root, _, files in os.walk(base_dir, topdown=False):
            if files:
                try:
                    file_name = random.choice(files)
                    file_path = os.path.join(root, file_name)
                    with open(file_path, 'rb') as f:
                        f.seek(random.randint(0, max(0, os.path.getsize(file_path) - 8)))
                        data = f.read(8)
                        if len(data) == 8:
                            # Store the file info as attributes
                            get_random_bytes_from_files.last_file_path = file_name
                            get_random_bytes_from_files.last_directory = root
                            return data
                except (IOError, OSError):
                    continue
    except Exception:
        pass
    # Fallback
    return struct.pack('d', time.time())

def get_random_seed():
    """50% chance of using file-based randomness"""
    if random.random() < 0.5:
        # Use file-based randomness
        random_bytes = get_random_bytes_from_files()
        # Get the last accessed file info from the function
        try:
            file_path = get_random_bytes_from_files.last_file_path
            directory = get_random_bytes_from_files.last_directory
        except AttributeError:
            file_path, directory = '', ''
        return struct.unpack('Q', random_bytes)[0], (file_path, directory)
    return None, (None, None)

if __name__ == '__main__':
    synth = Synth8Bit(sample_rate=22050)  # 8-bit style sample rate

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
    while total_time < 30:
        seed_info = get_random_seed()
        seed = seed_info[0]
        file_path, directory = seed_info[1]
        seed_type = f'file ({directory}/{file_path})' if seed is not None else 'norm'
        if seed is not None:
            random.seed(seed)

        freq = random.choices(frequencies, weights=weights, k=1)[0]
        synth.set_frequency(freq)
        
        waveform = random.choices(list(waveforms.keys()), 
                                  weights=list(waveforms.values()), k=1)[0]
        synth.set_waveform(waveform)
        
        duration = random.choice([0.1, 0.2, 0.3])
        synth.set_amplitude(random.uniform(0.4, 0.7))
        
        synth.add_note(duration)
        total_time += duration
        print(f"Freq: {freq:.2f} Hz, Wave: {waveform}, Seed: {seed_type}")
        
        # Reset the seed to prevent seed looping
        if seed is not None:
            random.seed()

    output_path = os.path.join(os.path.expanduser('~'), '8bit_tune.wav')
    synth.save_to_wav(output_path)
