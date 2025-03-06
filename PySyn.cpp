#include <vector>
#include <string>
#include <cmath>

class Compose {
public:
    std::vector<int> A;
    std::vector<int> B;
    std::vector<int> C;
    std::vector<int> samples;

    int sample_rate = 44100;
    int channels = 1;
    float amplitude = 0.5;
    float duty_cycle = 0.5;

    std::string waveform = "square";

    float sample(int time, float frequency = 440.0, std::string waveform = "square") {
        if (waveform == "square") {
            if (std::fmod(time * frequency, 1.0) < duty_cycle) {
                return 1.0;
            } else {
                return -1.0;
            }
        } else if (waveform == "triangle") {
            return 2 * abs(2 * (std::fmod(time * frequency, 1.0)) - 1) - 1;
        } else if (waveform == "sawtooth") {
            return 2 * (std::fmod(time * frequency, 1.0)) - 1;
        } else if (waveform == "sine") {
            return sin(2 * M_PI * frequency * time);
        } else if (waveform == "noise") {
            return (rand() / (float)RAND_MAX) * 2 - 1;
        } else if (waveform == "pulse") {
            float phase = std::fmod(time * frequency, 1.0);
            return (phase < duty_cycle) ? 1.0 : -0.5;
        } else if (waveform == "exponential") {
            float phase = std::fmod(time * frequency, 1.0);
            return 2 * std::exp(-4 * phase) - 1;
        } else if (waveform == "harmonics") {
            float result = 0;
            for (int i = 1; i <= 4; i++) {
                result += sin(2 * M_PI * frequency * i * time) / i;
            }
            return result;
        }
        return 0.0;
    };

    int add(float duration=1.0){
        int frames = sample_rate * duration;
        for (int i = 0; i < frames; i++) {
            samples.push_back(amplitude * sample(i / (float)sample_rate));
        }
        return frames;
    };

    int save(std::string name = "") {
        if (name.empty()) {
            name = "output.raw";
        }

        FILE* file = fopen(name.c_str(), "wb");

        if (!file) {
            return -1;
        }
        
        for (int sample : samples) {
            fwrite(&sample, sizeof(int), 1, file);
        }
        
        fclose(file);
        return samples.size();
    };

    int generateRandomSound(float duration = 1.0) {
        std::vector<std::string> waveforms = {
            "square", "triangle", "sawtooth", "sine",
            "noise", "pulse", "exponential", "harmonics"
        };
        std::string randomWaveform = waveforms[rand() % waveforms.size()];
        
        int frames = sample_rate * duration;
        for (int i = 0; i < frames; i++) {
            float frequency = 220.0 + (rand() % 440); // Random frequency between 220-660 Hz
            samples.push_back(amplitude * sample(i / (float)sample_rate, frequency, randomWaveform));
        }
        return frames;
    }
};

int main() {
    Compose composer;
    composer.generateRandomSound(15.0); // Generates 2 seconds of random sound
    composer.save("random_sound.raw"); // Save to a file
    return 0;
};

main();