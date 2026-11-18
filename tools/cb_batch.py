"""Generate voice B (Chatterbox + reference) for every beat of every JSON in a folder.
Usage: cb/bin/python cb_batch.py <folder> <ref.wav>"""
import sys, os, glob, json, time, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render import pron, text_key
import torch, torchaudio as ta
torch.set_num_threads(os.cpu_count() or 2)
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
folder, ref = sys.argv[1], sys.argv[2]
out = os.path.join(folder, "audio"); os.makedirs(out, exist_ok=True)
m = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
for f in sorted(glob.glob(os.path.join(folder, "*.json"))):
    j = json.load(open(f)); t0 = time.time()
    for b in j["beats"]:
        p = os.path.join(out, text_key(b["say"]) + ".wav")
        if os.path.exists(p): continue
        torch.manual_seed(7)
        wav = m.generate(pron(b["say"]), language_id="es", audio_prompt_path=ref, exaggeration=0.7, cfg_weight=0.4)
        ta.save(p + ".tmp.wav", wav, m.sr); os.replace(p + ".tmp.wav", p)
    print("AUDIO", os.path.basename(f), round(time.time() - t0), "s", flush=True)
