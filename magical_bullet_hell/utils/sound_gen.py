"""
Utility to procedurally generate retro sound effects as WAV files.
"""
import wave
import struct
import math
import random
import os


def generate_wav(filename, samples, sample_rate=44100):
    """Save a list of float samples (-1.0 to 1.0) to a WAV file."""
    with wave.open(filename, 'w') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        for s in samples:
            val = max(-32768, min(32767, int(s * 32767)))
            f.writeframesraw(struct.pack('<h', val))


def generate_all_sounds(out_dir):
    """Generate all game sounds."""
    os.makedirs(out_dir, exist_ok=True)
    sr = 44100

    # 1. Shoot (high pitch sweep down)
    samples = []
    length = int(sr * 0.1)
    phase = 0
    for i in range(length):
        t = i / length
        freq = 1200 * (1 - t) + 400
        phase += 2 * math.pi * freq / sr
        vol = (1 - t) * 0.15
        # Square wave for retro feel
        s = 1.0 if math.sin(phase) > 0 else -1.0
        samples.append(s * vol)
    generate_wav(os.path.join(out_dir, "shoot.wav"), samples)

    # 2. Explosion (white noise decaying)
    samples = []
    length = int(sr * 0.4)
    for i in range(length):
        t = i / length
        vol = (1 - t)**2 * 0.4
        s = random.uniform(-1.0, 1.0) * vol
        samples.append(s)
    generate_wav(os.path.join(out_dir, "explosion.wav"), samples)

    # 3. Item (chime / bell)
    samples = []
    length = int(sr * 0.2)
    phase1 = 0
    phase2 = 0
    for i in range(length):
        t = i / length
        freq1 = 880
        freq2 = 1760 if t > 0.05 else 0
        phase1 += 2 * math.pi * freq1 / sr
        phase2 += 2 * math.pi * freq2 / sr
        vol = (1 - t) * 0.2
        s = math.sin(phase1)
        if freq2 > 0:
            s += math.sin(phase2)
        samples.append(s * vol)
    generate_wav(os.path.join(out_dir, "item.wav"), samples)

    # 4. Graze (tiny tick)
    samples = []
    length = int(sr * 0.05)
    phase = 0
    for i in range(length):
        t = i / length
        freq = 2500
        phase += 2 * math.pi * freq / sr
        vol = (1 - t) * 0.1
        samples.append(math.sin(phase) * vol)
    generate_wav(os.path.join(out_dir, "graze.wav"), samples)

    # 5. Bomb (windup and noise)
    samples = []
    length = int(sr * 1.5)
    phase = 0
    for i in range(length):
        t = i / length
        freq = 200 + 800 * t
        phase += 2 * math.pi * freq / sr
        noise = random.uniform(-1, 1)
        vol = math.sin(t * math.pi) * 0.4
        samples.append((math.sin(phase)*0.5 + noise*0.5) * vol)
    generate_wav(os.path.join(out_dir, "bomb.wav"), samples)

    # 6. Death (falling pitch)
    samples = []
    length = int(sr * 0.8)
    phase = 0
    for i in range(length):
        t = i / length
        freq = 400 * (1 - t)**2 + 50
        phase += 2 * math.pi * freq / sr
        noise = random.uniform(-1, 1) * 0.3
        vol = (1 - t) * 0.5
        # square wave + noise
        s = (1.0 if math.sin(phase) > 0 else -1.0) * 0.7 + noise
        samples.append(s * vol)
    generate_wav(os.path.join(out_dir, "death.wav"), samples)


if __name__ == "__main__":
    generate_all_sounds("assets/sounds")
