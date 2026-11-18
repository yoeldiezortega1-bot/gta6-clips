#!/usr/bin/env bash
# Dependencias del pipeline (Python 3, ffmpeg ya instalado)
set -e
pip install --break-system-packages -q torch
pip install --break-system-packages -q git+https://github.com/huggingface/parler-tts.git
pip install --break-system-packages -q -U protobuf sentencepiece soundfile
T=/tmp/yt-script-tools
if [ ! -f "$T/skills/yt-script/hookscore.py" ]; then
  rm -rf "$T" && git clone -q https://github.com/Jakeschincariol/youtube-agent-skill.git "$T" \
  && git -C "$T" checkout -q a2feb2104981a375ffd4f87ee04f4f5344ac43c6
fi
echo "setup ok"
