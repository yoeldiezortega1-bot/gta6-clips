#!/usr/bin/env python3
"""Render a vertical Short from a beats JSON.

beats JSON: {"slug": "...", "hook_text": "TEXTO GRANDE ARRIBA", "voice": "carlos|alex",
             "beats": [{"say": "...", "image": "Vice_City_03", "screen": "TEXTO OPCIONAL"}]}
Usage: python3 render.py beats.json out.mp4
"""
import json, os, re, subprocess, sys, glob, wave, tempfile

CAPS = os.environ.get("CAPS_DIR", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "caps"))
FONT = "Poppins"
W, H = 1080, 1920

def sh(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

PRON = [
 (r"\bGTA\s*VI\b", "yi ti ei seis"), (r"\bGTA\s*6\b", "yi ti ei seis"), (r"\bGTA\s*5\b", "yi ti ei cinco"), (r"\bGTA\b", "yi ti ei"),
 (r"\bPlayStation\s*5\b", "pléisteishon cinco"), (r"\bPS5\b", "pe ese cinco"), (r"\bPlayStation\b", "pléisteishon"),
 (r"\bXbox\b", "éksbox"), (r"\bRockstar\b", "rókstar"), (r"\bVice City\b", "váis síti"), (r"\bJason\b", "yéison"),
 (r"\bPort Gellhorn\b", "port guéljorn"), (r"\bUltimate Edition\b", "últimeit edíshon"), (r"\bTake-Two\b", "téik tu"),
 (r"\bTwitch\b", "tuích"), (r"\bKick\b", "kik"), (r"\bonline\b", "onláin"), (r"\bOnline\b", "onláin"),
 (r"\bstreamers?\b", "estrímers"), (r"\bUltimate\b", "últimeit"), (r"\bDJ Khaled\b", "di yei jáled"),
 (r"\bReddit\b", "réddit"), (r"\bGrassrivers\b", "grasríbers"), (r"\bLeonida Keys\b", "leónida kis"), (r"\bRideout Customs\b", "ráidaut cástoms"),
 (r"\bHawk\b", "jok"), (r"\bLittle Morgan\b", "lítel mórgan"), (r"\bGrotti Cheetah\b", "grotti chíta"), (r"\bVapid Stanier\b", "vápid stánier"),
 (r"\bVapid\b", "vápid"), (r"\bMoses\b", "móuses"), (r"\bslim jim\b", "slim yim"), (r"\bKey Lento\b", "ki lento"),
 (r"\bOcean Beach\b", "óushen bich"), (r"\bRydeMe\b", "ráid mi"), (r"\bEaster eggs?\b", "íster eg"), (r"\bBigfoot\b", "bigfut"),
 (r"\bWashington Island\b", "guáshinton áiland"), (r"\bLiberty City\b", "líberti síti"), (r"\bThat's Where The Money Is\b", "dats güer de mani is"),
 (r"\bPowerPyx\b", "páuer pix"), (r"\bTalkEsport\b", "tok isport"), (r"\bKenton\b", "kénton"), (r"\bDexter\b", "déxter"), (r"\bDigital Foundry\b", "díyital fáundri"), (r"\bVintage\b", "víntach"), (r"\bPro\b", "pro"), (r"\bShorts\b", "chorts"), (r"\bDLC\b", "de ele ce"), (r"\bfps\b", "efe pe ese"),
 (r"Pay 'n' Spray", "péi en spréi"), (r"\bRandy\b", "rándi"), (r"\bsticks\b", "estiks"), (r"\bstick\b", "estik"),
 (r"\bBuck Me\b", "bak mi"), (r"\bScooter Bros\b", "skúter bros"), (r"\bRed Dead Redemption\b", "red ded ridémpshon"),
]
def pron(t):
    for a, b in PRON: t = re.sub(a, b, t)
    return t

_PARLER = {}
PARLER_DESC = ("A man with a pleasant, slightly low-pitched voice speaks in an engaging and expressive way "
               "at a moderate pace. The recording is very clear and close-sounding with no background noise.")

def parler(text, raw, seed=5):
    import torch, soundfile as sf, warnings
    warnings.filterwarnings("ignore")
    if not _PARLER:
        from parler_tts import ParlerTTSForConditionalGeneration
        from transformers import AutoTokenizer
        M = "parler-tts/parler-tts-mini-multilingual-v1.1"
        torch.set_num_threads(os.cpu_count() or 2)
        m = ParlerTTSForConditionalGeneration.from_pretrained(M)
        _PARLER.update(m=m, tok=AutoTokenizer.from_pretrained(M),
                       dtok=AutoTokenizer.from_pretrained(m.config.text_encoder._name_or_path))
    m, tok, dtok = _PARLER["m"], _PARLER["tok"], _PARLER["dtok"]
    torch.manual_seed(seed)
    d = dtok(PARLER_DESC, return_tensors="pt"); p = tok(text, return_tensors="pt")
    with torch.no_grad():
        a = m.generate(input_ids=d.input_ids, attention_mask=d.attention_mask, prompt_input_ids=p.input_ids,
                       prompt_attention_mask=p.attention_mask, do_sample=True, temperature=1.0)
    sf.write(raw, a.cpu().numpy().squeeze(), m.config.sampling_rate)

CB_AUDIO = {}
def text_key(t):
    import hashlib
    return hashlib.md5(pron(t).encode()).hexdigest()

def tts(text, out, voice):
    text = pron(text)
    raw = out + ".raw.wav"
    if voice == "cb":
        import shutil
        shutil.copy(CB_AUDIO[text_key(text)], raw)
        af = ("aresample=44100,highpass=f=60,afade=t=in:d=0.02,"
              "silenceremove=stop_periods=-1:stop_duration=0.45:stop_threshold=-50dB,acompressor=threshold=-20dB:ratio=2")
    elif voice == "parler":
        parler(text, raw)
        af = ("silenceremove=start_periods=1:start_threshold=-40dB,areverse,silenceremove=start_periods=1:start_threshold=-40dB,areverse,"
              "aresample=44100,highpass=f=60,acompressor=threshold=-20dB:ratio=2")
    elif voice == "sergio":
        subprocess.run(["python3", "-m", "piper", "-m",
                        "/home/claude/tts/vits-piper-es_ES-sharvard-medium/es_ES-sharvard-medium.onnx",
                        "-s", "0", "-f", raw, "--sentence_silence", "0.2", "--noise_scale", "0.6", "--noise_w", "0.7", "--length_scale", "1.02"], input=text.encode(), check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        af = "aresample=44100,highpass=f=70,equalizer=f=3500:t=q:w=1:g=1.5,acompressor=threshold=-20dB:ratio=2"
    elif voice == "alex":
        sh(["python3", "/home/claude/work/tts.py", "em_alex", "es", "1.05", text, raw])
        af = "asetrate=24000*0.97,aresample=44100,atempo=1.03,highpass=f=70,equalizer=f=3000:t=q:w=1:g=3,acompressor=threshold=-18dB:ratio=2.5"
    else:
        model = glob.glob("/home/claude/tts/carlfm/*.onnx")[0]
        subprocess.run(["python3", "-m", "piper", "-m", model, "-f", raw, "--length_scale", "0.95",
                        "--sentence_silence", "0.15"], input=text.encode(), check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        af = "aresample=44100,highpass=f=70,equalizer=f=150:t=q:w=1:g=2,equalizer=f=3500:t=q:w=1:g=2,acompressor=threshold=-18dB:ratio=2.5"
    sh(["ffmpeg", "-y", "-i", raw, "-af", af + ",apad=pad_dur=0.18", "-ar", "44100", "-ac", "1", "-c:a", "pcm_s16le", out])
    with wave.open(out) as w:
        return w.getnframes() / w.getframerate()

def find_image(key):
    if os.path.isabs(key) and os.path.exists(key):
        return key
    m = sorted(glob.glob(os.path.join(CAPS, key + "*.jpg"))) or sorted(glob.glob(os.path.join(CAPS, "*" + key + "*.jpg")))
    if not m:
        raise SystemExit(f"no image for {key}")
    return m[0]

def ts(t):
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"

def esc(t):
    return t.replace("{", "(").replace("}", ")")

def captions(beats, durs, hook_text, path):
    lines = ["[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "",
             "[V4+ Styles]",
             "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
             f"Style: Cap,{FONT},92,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,7,3,5,60,60,0,1",
             f"Style: Hook,{FONT},84,&H0000E6FF,&H0000E6FF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,7,3,8,60,60,230,1",
             f"Style: Scr,{FONT},70,&H0000E6FF,&H0000E6FF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,6,2,8,60,60,260,1",
             "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    t0 = 0.0
    for i, (b, d) in enumerate(zip(beats, durs)):
        top = hook_text if i == 0 and hook_text else b.get("screen", "")
        if top:
            lines.append(f"Dialogue: 1,{ts(t0)},{ts(t0 + d)},{'Hook' if i == 0 else 'Scr'},,0,0,0,,{esc(top.upper())}")
        words = b["say"].split()
        chunks = [" ".join(words[j:j + 3]) for j in range(0, len(words), 3)]
        total = sum(len(c) for c in chunks) or 1
        speak = d - 0.25
        t = t0
        for c in chunks:
            cd = speak * len(c) / total
            lines.append(f"Dialogue: 0,{ts(t)},{ts(t + cd)},Cap,,0,0,0,,{{\\pos(540,1320)\\fscx80\\fscy80\\t(0,90,\\fscx100\\fscy100)}}{esc(c.upper())}")
            t += cd
        t0 += d
    open(path, "w").write("\n".join(lines) + "\n")

def main():
    spec = json.load(open(sys.argv[1])); out = sys.argv[2]
    voice = spec.get("voice", "parler")
    tmp = tempfile.mkdtemp(prefix="short_")
    if voice == "cb":
        adir = os.path.join(os.path.dirname(os.path.abspath(sys.argv[1])), "audio")
        for f in glob.glob(os.path.join(adir, "*.wav")):
            CB_AUDIO[os.path.basename(f)[:-4]] = f
    if spec.get("thumb"):
        tp = os.path.join(tmp, "thumb.png")
        sh(["python3", os.path.join(os.path.dirname(os.path.abspath(__file__)), "thumb.py"), find_image(spec["image0"]), spec["thumb"], tp])
        spec["beats"][0]["image"] = tp
    segs, durs = [], []
    for i, b in enumerate(spec["beats"]):
        a = os.path.join(tmp, f"a{i}.wav")
        d = tts(b["say"], a, voice); durs.append(d)
        img = find_image(b["image"])
        v = os.path.join(tmp, f"v{i}.mp4")
        direction = "(iw-1080)*t/%f" % d if i % 2 == 0 else "(iw-1080)*(1-t/%f)" % d
        if img.endswith("thumb.png"):
            direction = "(iw-1080)/2"
        vf = (f"scale=-2:{int(H*1.08)},crop={W}:{H}:x='{direction}':y='(ih-{H})/2',"
              f"eq=contrast=1.06:saturation=1.12,fps=30,format=yuv420p")
        sh(["ffmpeg", "-y", "-loop", "1", "-t", f"{d:.3f}", "-i", img, "-vf", vf, "-an",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", v])
        segs.append(v)
    lst = os.path.join(tmp, "list.txt")
    open(lst, "w").write("".join(f"file '{s}'\n" for s in segs))
    joined = os.path.join(tmp, "joined.mp4")
    sh(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", joined])
    ass = os.path.join(tmp, "caps.ass")
    captions(spec["beats"], durs, spec.get("hook_text", ""), ass)
    # one continuous narration track: join raw PCM, no per-clip AAC gaps
    voice_wav = os.path.join(tmp, "voice.wav")
    with wave.open(voice_wav, "wb") as wo:
        for i in range(len(segs)):
            with wave.open(os.path.join(tmp, f"a{i}.wav")) as wi:
                if i == 0: wo.setparams(wi.getparams())
                wo.writeframes(wi.readframes(wi.getnframes()))
    sh(["ffmpeg", "-y", "-i", joined, "-i", voice_wav, "-map", "0:v", "-map", "1:a", "-vf", f"ass={ass}", "-af", "loudnorm=I=-14:TP=-1.5",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-c:a", "aac", "-b:a", "160k",
        "-movflags", "+faststart", out])
    print(out, round(sum(durs), 1), "s")

if __name__ == "__main__":
    main()
