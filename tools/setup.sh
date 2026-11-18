#!/usr/bin/env bash
# Dependencias: Python 3, ffmpeg. Voz B = Chatterbox multilingüe en un venv aparte.
set -e
pip install --break-system-packages -q soundfile pillow
if [ ! -x /home/claude/cb/bin/python ]; then
  python3 -m venv /home/claude/cb
  /home/claude/cb/bin/pip install -q --upgrade pip
  /home/claude/cb/bin/pip install -q chatterbox-tts "setuptools<81"
fi
T=/tmp/yt-script-tools
if [ ! -f "$T/skills/yt-script/hookscore.py" ]; then
  rm -rf "$T" && git clone -q https://github.com/Jakeschincariol/youtube-agent-skill.git "$T" \
  && git -C "$T" checkout -q a2feb2104981a375ffd4f87ee04f4f5344ac43c6
fi
echo "setup ok"
