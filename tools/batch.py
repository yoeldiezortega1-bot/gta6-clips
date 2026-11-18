"""Render every beats JSON in a folder to MP4 (run tools/cb_batch.py first for voice "cb").
Usage: python3 tools/batch.py <folder>"""
import sys, glob, os, time, traceback
folder = sys.argv[1]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render
for f in sorted(glob.glob(os.path.join(folder, "*.json"))):
    out = f[:-5] + ".mp4"
    if os.path.exists(out): continue
    t = time.time()
    try:
        sys.argv = ["render.py", f, out]; render.main()
        print("OK", os.path.basename(out), round(time.time() - t), "s", flush=True)
    except Exception:
        print("FAIL", f, traceback.format_exc()[-800:], flush=True)
