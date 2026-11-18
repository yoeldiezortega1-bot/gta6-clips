"""Flag beats whose audio speed looks wrong (cut or rambling). Usage: python3 tools/qa.py <folder>"""
import json, sys, glob, os, soundfile as sf
folder = sys.argv[1]; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.argv = ["x"]
import render
bad = 0
for f in sorted(glob.glob(os.path.join(folder, "*.json"))):
    for i, b in enumerate(json.load(open(f))["beats"]):
        p = os.path.join(folder, "audio", render.text_key(b["say"]) + ".wav")
        a, sr = sf.read(p); r = len(render.pron(b["say"])) / (len(a) / sr)
        if r < 10 or r > 21: bad += 1; print("REVISAR", os.path.basename(f), i, round(r, 1), p)
print("qa:", bad, "a revisar")
