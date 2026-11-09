"""Original soundtracks for recaps and signature moves, rendered offline (no samples, no outside music).
Usage (from the repo root): python3 kit/music.py <style> <out.mp3> [seconds]      styles: see STYLES below
Every track is ~66.5 s by default (a full recap) with a hard first beat so a Short opens on sound, and a 2-bar
fade-out ending. Shorts and signature moves cut them shorter in short_mp4.sh (with their own fade)."""
import sys, subprocess, tempfile, os
import numpy as np
from scipy.signal import butter, sosfilt

SR = 44100
rng = np.random.default_rng(7)
hz = lambda m: 440.0 * 2 ** ((m - 69) / 12)

def env(n, a, d, sustain=0.0, curve=4.0):
    """attack (s), exponential-ish decay (s) to `sustain` level."""
    t = np.arange(n) / SR
    att = np.clip(t / max(a, 1e-4), 0, 1)
    dec = sustain + (1 - sustain) * np.exp(-curve * np.clip(t - a, 0, None) / max(d, 1e-4))
    return att * dec

def lp(x, f, order=2):
    f = min(max(f, 30), SR / 2 - 100); return sosfilt(butter(order, f, 'low', fs=SR, output='sos'), x)
def hp(x, f, order=2):
    f = min(max(f, 20), SR / 2 - 100); return sosfilt(butter(order, f, 'high', fs=SR, output='sos'), x)
def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], 'band', fs=SR, output='sos'), x)

def saw(f, n, detune=0.0):
    t = np.arange(n) / SR; out = 0
    for d in ([0] if not detune else [-detune, 0, detune]):
        ph = (t * f * 2 ** (d / 1200)) % 1.0; out = out + (2 * ph - 1)
    return out / (1 if not detune else 3)
def square(f, n, pw=0.5):
    t = np.arange(n) / SR; return np.where((t * f) % 1.0 < pw, 1.0, -1.0)
def sine(f, n, phase=0.0):
    return np.sin(2 * np.pi * f * np.arange(n) / SR + phase)
def noise(n):
    return rng.uniform(-1, 1, n)

# ---------- instruments (each returns a mono array) ----------
def kick(punch=1.0, tail=0.28, top=150, low=45):
    n = int(SR * (tail + 0.05)); t = np.arange(n) / SR
    f = low + (top - low) * np.exp(-t / 0.035)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.002, tail, curve=3.0)
    click = hp(noise(n), 3000) * env(n, 0.0005, 0.012, curve=6) * 0.25 * punch
    return np.tanh(1.4 * body) * 0.9 + click

def snare(tone=190, bright=1.0, tail=0.16):
    n = int(SR * (tail + 0.05))
    body = sine(tone, n) * env(n, 0.001, 0.06) * 0.45
    nz = bp(noise(n), 1200, 9000) * env(n, 0.001, tail, curve=4) * 0.8 * bright
    return body + nz

def clap(tail=0.18):
    n = int(SR * (tail + 0.06)); out = np.zeros(n)
    for d in (0, 0.011, 0.022):
        i = int(d * SR); m = int(0.02 * SR)
        out[i:i + m] += bp(noise(m), 900, 2600) * env(m, 0.0005, 0.012) * 0.5
    i = int(0.03 * SR); m = n - i
    out[i:] += bp(noise(m), 1000, 3000) * env(m, 0.001, tail, curve=4) * 0.7
    return out

def rim():
    n = int(SR * 0.08)
    return (bp(noise(n), 1800, 5000) * env(n, 0.0005, 0.02, curve=6) * 0.6 + sine(1700, n) * env(n, 0.0005, 0.03) * 0.25)

def hat(open_=False, level=1.0):
    n = int(SR * (0.32 if open_ else 0.07))
    return hp(noise(n), 7500, 3) * env(n, 0.0005, 0.25 if open_ else 0.035, curve=5) * 0.35 * level

def shaker():
    n = int(SR * 0.09)
    return bp(noise(n), 5000, 12000) * env(n, 0.02, 0.05, curve=5) * 0.18

def crash():
    n = int(SR * 1.6)
    return hp(noise(n), 5000, 2) * env(n, 0.002, 1.5, curve=3.5) * 0.25

def riser(sec):
    n = int(SR * sec); t = np.linspace(0, 1, n)
    nz = noise(n); out = np.zeros(n); blk = 2048
    for i in range(0, n, blk):  # sweep a band upward
        c = 400 + 7000 * t[i] ** 2
        out[i:i + blk] = bp(nz[i:i + blk], c * 0.7, min(c * 1.4, 18000), 1)
    return out * t ** 2 * 0.35

def sub808(midi, sec, glide_from=None, drive=1.6):
    n = int(SR * sec); t = np.arange(n) / SR; f0 = hz(midi)
    f = f0 * (1 + 1.0 * np.exp(-t / 0.02))
    if glide_from: f = hz(glide_from) + (f0 - hz(glide_from)) * np.clip(t / 0.09, 0, 1)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR)
    a = env(n, 0.004, sec * 0.9, sustain=0.0, curve=1.6)
    return np.tanh(drive * x) / np.tanh(drive) * a * 0.75 + np.sin(4 * np.pi * np.cumsum(f) / SR) * a * 0.12

def bass_pluck(midi, sec, cutoff=900, kind='saw'):
    n = int(SR * sec); f = hz(midi)
    raw = saw(f, n) if kind == 'saw' else square(f, n, 0.4)
    e = env(n, 0.003, sec * 0.7, sustain=0.2, curve=3)
    # filter envelope approximated by mixing a bright and a dark copy
    bright = lp(raw, cutoff * 2.5); dark = lp(raw, cutoff * 0.6)
    fe = np.exp(-np.arange(n) / SR / 0.08)
    return (bright * fe + dark * (1 - fe)) * e * 0.5 + sine(f, n) * e * 0.35

def pluck(midi, sec, bright=4000):  # Karplus-Strong string
    f = hz(midi); n = int(SR * sec); p = max(2, int(SR / f))
    buf = lp(noise(p), bright, 1); out = np.zeros(n)
    for i in range(n):
        out[i] = buf[i % p]
        buf[i % p] = 0.5 * (buf[i % p] + buf[(i + 1) % p]) * 0.996
    return out * env(n, 0.001, sec, curve=1.0) * 0.7

def keys(midi, sec, ratio=2.0, index=1.2):  # FM electric piano / bell
    n = int(SR * sec); f = hz(midi); t = np.arange(n) / SR
    mod = np.sin(2 * np.pi * f * ratio * t) * index * np.exp(-t / 0.5)
    x = np.sin(2 * np.pi * f * t + mod)
    return x * env(n, 0.004, sec, curve=2.2) * 0.35

def pad(midis, sec, cutoff=1800, detune=12):
    n = int(SR * sec); out = np.zeros(n)
    for m in midis: out += saw(hz(m), n, detune)
    out = lp(out / len(midis), cutoff, 2)
    a = np.minimum(1, np.arange(n) / (SR * 0.25)) * np.minimum(1, (n - np.arange(n)) / (SR * 0.3))
    return out * a * 0.28

def lead(midi, sec, cutoff=3000, kind='square', vib=0.0):
    n = int(SR * sec); t = np.arange(n) / SR; f = hz(midi) * (1 + vib * np.sin(2 * np.pi * 5.5 * t) * np.clip(t / 0.2, 0, 1))
    ph = np.cumsum(f) / SR
    raw = np.where(ph % 1 < 0.5, 1.0, -1.0) if kind == 'square' else 2 * (ph % 1) - 1
    return lp(raw, cutoff) * env(n, 0.006, sec, sustain=0.5, curve=2.5) * 0.25

def brass(midis, sec, cutoff=2400):  # short synth stab
    n = int(SR * sec); out = sum(saw(hz(m), n, 8) for m in midis) / len(midis)
    fe = np.exp(-np.arange(n) / SR / 0.06)
    return (lp(out, cutoff * 2) * fe + lp(out, cutoff * 0.5) * (1 - fe)) * env(n, 0.008, sec, sustain=0.3, curve=3) * 0.35

# ---------- mixing ----------
class Track:
    def __init__(self, sec, bpm):
        self.sec = sec; self.bpm = bpm; self.step = 60 / bpm / 4; self.bar = self.step * 16
        self.buses = {k: np.zeros(int(SR * (sec + 3))) for k in ('drums', 'bass', 'music', 'fx')}
    def put(self, bus, t, x, gain=1.0):
        if t >= self.sec + 2: return
        i = int(t * SR); b = self.buses[bus]; j = min(len(b), i + len(x))
        if i < len(b): b[i:j] += x[:j - i] * gain
    def at(self, bar, step=0):
        return bar * self.bar + step * self.step

def reverb(x, mix=0.18, size=1.0):
    out = np.zeros_like(x)
    for d, g in ((0.0297, .77), (0.0371, .76), (0.0411, .75), (0.0437, .74)):
        D = int(d * size * SR); y = np.zeros_like(x)
        for i in range(0, len(x), D):  # comb filter, block-wise
            seg = x[i:i + D]; prev = y[i - D:i - D + len(seg)] if i >= D else 0
            y[i:i + len(seg)] = seg + g * prev
        out += y
    out = lp(hp(out / 4, 250), 6000)
    return x * (1 - mix) + out * mix

def delay(x, sec, fb=0.35, mix=0.25):
    D = int(sec * SR); y = x.copy()
    for k in range(1, 6): y[D * k:] += x[:-D * k or None][:len(y) - D * k] * (fb ** k)
    return x * (1 - mix) + lp(y, 4500) * mix

def master(tr, fade_bars=2, duck=0.0, gains=(0.9, 0.85, 0.8, 0.7)):
    d, b, m, fx = (tr.buses[k] for k in ('drums', 'bass', 'music', 'fx'))
    if duck:  # sidechain the music and bass to the kick bus energy
        e = np.abs(lp(d, 120)); e = e / (e.max() + 1e-9)
        sc = 1 - duck * np.clip(lp(e, 8, 1) * 4, 0, 1)
        b, m = b * sc, m * sc
    gd, gb, gm, gf = gains
    mix = d * gd + b * gb + m * gm + fx * gf
    n = int(SR * tr.sec); mix = mix[:n]
    fade = np.ones(n); fl = int(fade_bars * tr.bar * SR); fade[-fl:] = np.linspace(1, 0, fl) ** 1.5
    mix = mix * fade
    mix = hp(mix, 28)
    mix = np.tanh(mix / (np.percentile(np.abs(mix), 99.7) + 1e-9) * 1.1) * 0.89  # soft limiter
    return mix

def write_mp3(x, path):
    with tempfile.TemporaryDirectory() as d:
        wav = os.path.join(d, 'a.wav')
        import wave
        with wave.open(wav, 'w') as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
            w.writeframes((np.clip(x, -1, 1) * 32767).astype('<i2').tobytes())
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', wav, '-af', 'loudnorm=I=-19:TP=-1.5:LRA=11', '-ar', str(SR), '-ac', '1', '-b:a', '160k', path], check=True)

# ---------- styles ----------
def night_game(sec):
    """'Night Game': dark half-time trap, 140 BPM (felt at 70), F minor. Glassy bells, sliding 808s, rolling hats."""
    tr = Track(sec, 140); K, S, H = kick(1.0, 0.35, 140, 42), clap(0.22), hat()
    prog = [(53, [65, 68, 72]), (49, [61, 65, 68]), (51, [63, 67, 70]), (48, [60, 63, 67])]   # Fm Db Eb C(m)
    bell = [[77, 80, 84, 80, 77, 75], [77, 80, 85, 84, 80, 77], [75, 79, 82, 79, 75, 74], [72, 75, 79, 80, 79, 75]]
    nb = int(sec / tr.bar) + 1
    for bar in range(nb):
        root, ch = prog[bar % 4]; t0 = tr.at(bar)
        tr.put('music', t0, pad(ch, tr.bar, 1400, 14), 0.8)
        for i, m in enumerate(bell[bar % 4]):
            tr.put('music', t0 + [0, 3, 6, 8, 11, 14][i] * tr.step, keys(m, 1.2, 3.5, 1.6), 0.55 if bar >= 1 else 0.35)
        if bar == 0: tr.put('drums', t0, K, 1.0); tr.put('fx', t0, crash(), 0.8); continue
        brk = bar % 8 == 7
        for st in ([0, 10] if not brk else [0]):
            tr.put('drums', t0 + st * tr.step, K)
        for st, dur, glide in ([(0, 9, None), (10, 6, root + 12)] if not brk else [(0, 16, None)]):
            tr.put('bass', t0 + st * tr.step, sub808(root - 12, dur * tr.step, glide_from=glide), 0.95)
        tr.put('drums', t0 + 8 * tr.step, S, 0.9)
        for st in range(16):
            if brk and st > 8: break
            tr.put('drums', t0 + st * tr.step, H, 0.7 if st % 2 else 1.0)
            if st in (13, 14) and bar % 2: tr.put('drums', t0 + (st + .5) * tr.step, hat(level=0.7))
        if bar % 8 == 0: tr.put('fx', t0, crash(), 0.6)
        if brk: tr.put('fx', t0 + tr.bar * 0.5, riser(tr.bar * 0.5), 1.0)
    for k in ('music',): tr.buses[k] = reverb(tr.buses[k], 0.3, 1.3)
    return master(tr, duck=0.35, gains=(0.9, 0.75, 1.3, 0.7))

def fast_break(sec):
    """'Fast Break': bright funk-house, 122 BPM, A major. Four-on-the-floor, slap-style bass, brass stabs, shaker."""
    tr = Track(sec, 122); K, C, OH = kick(1.1, 0.22, 170, 50), clap(0.15), hat(True)
    prog = [(45, [69, 73, 76, 80]), (42, [66, 69, 73, 76]), (38, [62, 66, 69, 73]), (40, [64, 68, 71, 74])]  # Amaj7 F#m7 Dmaj7 E7
    bassline = [(0, 0, 2), (3, 12, 1), (4, 0, 1), (6, 7, 2), (8, 0, 2), (11, 12, 1), (12, 10, 1), (14, 7, 2)]
    stab = [2, 6, 11]
    nb = int(sec / tr.bar) + 1
    for bar in range(nb):
        root, ch = prog[bar % 4]; t0 = tr.at(bar)
        tr.put('music', t0, pad(ch, tr.bar, 2600, 8), 0.45)
        for st in range(0, 16, 4): tr.put('drums', t0 + st * tr.step, K)
        if bar == 0: tr.put('fx', t0, crash(), 0.8); continue
        for st in (4, 12): tr.put('drums', t0 + st * tr.step, C, 0.8)
        for st in range(2, 16, 4): tr.put('drums', t0 + st * tr.step, OH, 0.6)
        for st in range(16): tr.put('drums', t0 + st * tr.step, shaker(), 0.9 if st % 2 else 0.6)
        for st, iv, ln in bassline:
            tr.put('bass', t0 + st * tr.step, bass_pluck(root - 12 + iv, ln * tr.step * 0.9, 700, 'square'), 0.9)
        if bar >= 2:
            for st in stab: tr.put('music', t0 + st * tr.step, brass([m + 12 for m in ch[:3]], tr.step * 1.5, 2600), 0.7)
        if bar % 4 == 3 and bar >= 3:
            for i, m in enumerate([ch[3] + 12, ch[2] + 12, ch[1] + 12, ch[0] + 12]):
                tr.put('music', t0 + (12 + i) * tr.step, keys(m, 0.3, 1.0, 0.8), 0.5)
        if bar % 8 == 0: tr.put('fx', t0, crash(), 0.5)
        if bar % 8 == 7: tr.put('fx', t0, riser(tr.bar), 0.7)
    tr.buses['music'] = delay(reverb(tr.buses['music'], 0.15), tr.step * 3, 0.3, 0.2)
    return master(tr, duck=0.3, gains=(0.85, 0.42, 3.2, 0.7))

def film_room(sec):
    """'Film Room': lo-fi boom-bap, 88 BPM, D minor 9ths on electric piano, swung drums, vinyl hiss."""
    tr = Track(sec, 88); K, S, H = kick(0.7, 0.3, 120, 48), snare(200, 0.8, 0.18), hat()
    prog = [(50, [62, 65, 69, 72, 76]), (43, [55, 59, 62, 65, 69]), (48, [60, 64, 67, 71, 74]), (45, [57, 61, 64, 67, 70])]  # Dm9 G13 Cmaj9 A7b9-ish
    swing = lambda st: st + (0.33 if st % 2 else 0)
    nb = int(sec / tr.bar) + 1
    for bar in range(nb):
        root, ch = prog[bar % 4]; t0 = tr.at(bar)
        for st, sub in ((0, ch), (6, ch[1:]), (10, ch[:4])):
            for k, m in enumerate(sub): tr.put('music', t0 + (swing(st) + k * 0.06) * tr.step, keys(m, tr.step * 6, 1.0, 0.7), 0.42)
        tr.put('fx', t0, lp(noise(int(tr.bar * SR)), 3000) * 0.012)
        if bar == 0: tr.put('drums', t0, K); continue
        for st in ([0, 7, 10] if bar % 2 == 0 else [0, 3, 10]): tr.put('drums', t0 + swing(st) * tr.step, K, 0.95)
        for st in (4, 12): tr.put('drums', t0 + st * tr.step, S, 0.75)
        for st in range(0, 16, 2): tr.put('drums', t0 + swing(st) * tr.step, H, 0.8)
        for st in range(1, 16, 2): tr.put('drums', t0 + swing(st) * tr.step, H, 0.35)
        line = [(0, 0, 5), (6, 7, 2), (8, 12, 2), (11, 10, 3), (14, 7, 2)]
        for st, iv, ln in line: tr.put('bass', t0 + swing(st) * tr.step, bass_pluck(root - 12 + iv, ln * tr.step, 450), 0.9)
        if bar % 4 == 1:
            mel = [(0, ch[3] + 12), (3, ch[2] + 12), (4, ch[4] + 12), (7, ch[3] + 12)]
            for st, m in mel: tr.put('music', t0 + (8 + swing(st)) * tr.step, pluck(m, 0.6, 3000), 0.6)
    crackle = np.zeros_like(tr.buses['fx']); idx = rng.integers(0, len(crackle), int(sec * 25)); crackle[idx] = rng.uniform(-0.25, 0.25, len(idx))
    tr.buses['fx'] += lp(crackle, 5000)
    tr.buses['music'] = lp(reverb(tr.buses['music'], 0.22), 5200)
    return master(tr, duck=0.15)

def crunch_time(sec):
    """'Crunch Time': tense, driving 8ths at 128 BPM in E minor. Pulsing bass, rising strings, toms; built for late-game plays."""
    tr = Track(sec, 128); K, S = kick(1.2, 0.25, 160, 46), snare(180, 1.1, 0.2)
    prog = [(40, [64, 67, 71]), (36, [60, 64, 67]), (43, [62, 67, 71]), (38, [62, 66, 69])]   # Em C G/D D
    nb = int(sec / tr.bar) + 1
    for bar in range(nb):
        root, ch = prog[bar % 4]; t0 = tr.at(bar); lvl = min(1.0, 0.55 + 0.06 * (bar % 8))
        tr.put('music', t0, pad([m + 12 for m in ch], tr.bar, 1200 + 300 * (bar % 8), 18), 0.9 * lvl)
        for st in range(0, 16, 2):
            tr.put('bass', t0 + st * tr.step, bass_pluck(root - 12 + (12 if st in (6, 14) else 0), tr.step * 1.7, 600 + 80 * (bar % 8), 'saw'), 0.85)
        if bar == 0: tr.put('drums', t0, K); tr.put('fx', t0, crash()); continue
        for st in (0, 4, 8, 12): tr.put('drums', t0 + st * tr.step, K)
        for st in (4, 12): tr.put('drums', t0 + st * tr.step, S, 0.8)
        for st in range(16): tr.put('drums', t0 + st * tr.step, hat(level=0.9 if st % 2 else 0.5))
        if bar % 4 == 3:
            for i, st in enumerate((10, 12, 13, 14, 15)):
                tom = sine(hz(50 - 3 * i), int(SR * 0.25)) * env(int(SR * 0.25), 0.002, 0.2) * 0.6
                tr.put('drums', t0 + st * tr.step, tom)
        hook = [(0, 76), (3, 74), (6, 71), (8, 79), (11, 78), (14, 74)]
        if bar >= 4:
            for st, m in hook: tr.put('music', t0 + st * tr.step, lead(m + (0 if bar % 4 < 2 else -2 if m == 79 else 0), tr.step * 2.2, 2600, 'saw', 0.004), 0.55)
        if bar % 8 == 7: tr.put('fx', t0, riser(tr.bar), 1.0)
        if bar % 8 == 0: tr.put('fx', t0, crash(), 0.7)
    tr.buses['music'] = reverb(delay(tr.buses['music'], tr.step * 3, 0.3, 0.18), 0.2)
    return master(tr, duck=0.4, gains=(0.85, 0.55, 2.2, 0.7))

STYLES = {'night-game': night_game, 'fast-break': fast_break, 'film-room': film_room, 'crunch-time': crunch_time}

if __name__ == '__main__':
    style, out = sys.argv[1], sys.argv[2]
    sec = float(sys.argv[3]) if len(sys.argv) > 3 else 66.53
    write_mp3(STYLES[style](sec), out)
    print('wrote', out)
