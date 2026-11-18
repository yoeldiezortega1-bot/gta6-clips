# Pipeline diario de Shorts de GTA 6

Canal de YouTube conectado en Metricool (brand/blogId `8200203`, zona horaria `Europe/Madrid`).
Cada día se publican **10 Shorts en español de España**, con voz generada por IA y capturas oficiales de Rockstar.

## 1. Preparar el entorno

```bash
git clone --depth 1 https://github.com/yoeldiezortega1-bot/gta6-clips /home/claude/gta6-clips
bash /home/claude/gta6-clips/tools/setup.sh
```

Para descargar la voz hacen falta `huggingface.co` y `*.hf.co` en los dominios permitidos.
La voz B es Chatterbox multilingüe, de licencia MIT, y se instala en `/home/claude/cb`.
Toma como referencia `tools/voz_b_ref.wav`, una voz sintética, no de una persona real.

## 2. Tendencias del día

Busca en la web qué es tendencia hoy con GTA 6. El canal se centra en **datos curiosos y trucos**: easter eggs, secretos, formas de ganar dinero, consejos y mecánicas poco conocidas.
Los vídeos y fotos que se hacen virales sirven para saber qué temas interesan, pero nunca se copian: las imágenes de los Shorts son solo las capturas oficiales de `assets/caps`.
Elige **10 temas distintos** y no repitas ninguno de `published.md`.

Reglas de seguridad y veracidad:
- Cada dato tiene que tener una fuente: Rockstar, Take-Two, PlayStation o Xbox, o un medio serio. Apunta la fuente en `published.md`.
- Nada de filtraciones, piratería, exploits ni trucos para "jugar antes".
- Un rumor solo se cuenta si se dice claramente que es un rumor o que está sin confirmar.
- No inventes cifras. Si un dato no está confirmado, el vídeo lo dice.
- Nunca des a entender que el canal es oficial de Rockstar.

## 3. Guiones con /yt-script

Para cada tema:
1. Escribe 3 o más ganchos y puntúa su versión en inglés con
   `python3 -I /tmp/yt-script-tools/skills/yt-script/hookscore.py --hook "..."`.
   Quédate con el de más puntuación, que debe ser 60 o más, y si no llega, reescríbelo con la corrección que sugiera la herramienta.
2. Escribe el guion de 25 a 50 segundos, entre 60 y 120 palabras: gancho, giro, cuerpo, resultado y una sola petición al final.
3. Usa español de España, tuteando, con frases cortas y los números escritos en letra.
4. Guárdalo en `days/AAAA-MM-DD/NN_slug.json` con este formato:

```json
{"slug":"01_tema","voice":"cb","hook_text":"",
 "thumb":"LÍNEA 1|LÍNEA 2|LÍNEA 3 (portada, 2-4 palabras por línea)","image0":"Vice_City_16",
 "title":"Título de YouTube (máx. 90 caracteres, con #GTA6 #Shorts)",
 "description":"2-3 líneas + fuentes + 'Imágenes: Rockstar Games. Canal no oficial.'",
 "tags":["GTA 6","GTA VI","Vice City"],
 "beats":[{"say":"frase locutada","image":"Vice_City_03","screen":"texto en pantalla opcional"}]}
```

`image` es el prefijo de un archivo de `assets/caps/`, por ejemplo `Lucia_Caminos_07`.
Rota las imágenes: mira `assets/used.json` y usa antes las que se han usado menos.
Si una palabra en inglés suena mal, añádela a la lista `PRON` de `tools/render.py`.

## 4. Render

Primero genera la voz y luego monta los vídeos. Hazlo en este orden y nunca a la vez, porque juntos agotan la memoria.

```bash
cd /home/claude/gta6-clips
/home/claude/cb/bin/python tools/cb_batch.py days/AAAA-MM-DD tools/voz_b_ref.wav   # ~4-5 min por vídeo
python3 tools/qa.py days/AAAA-MM-DD      # regenera (borra el wav y relanza cb_batch) las frases marcadas REVISAR
python3 tools/batch.py days/AAAA-MM-DD   # ~1 min por vídeo
```

Cada vídeo empieza con una portada llamativa creada con `thumb.py` a partir de `thumb` e `image0`. En Metricool, añade `"videoCoverMilliseconds": 500` para usarla como miniatura.
Cuando acabe, comprueba que hay 10 MP4 y mira un fotograma de cada uno.

## 5. Subir y programar

1. Haz commit de `days/AAAA-MM-DD/*.mp4` y los JSON, y `git push`.
2. Para cada vídeo, la URL es `https://raw.githubusercontent.com/yoeldiezortega1-bot/gta6-clips/main/days/AAAA-MM-DD/NN_slug.mp4`.
   Comprueba que responde 200 antes de programar.
3. Programa en Metricool con `createScheduledPost`, usando `blogId` 8200203 y la zona `Europe/Madrid`:
   - `providers`: `[{"network":"youtube"}]`
   - `youtubeData`: `{"title":..., "type":"short", "privacy":"public", "tags":[...], "category":"GAMING", "madeForKids":false, "isAiGeneratedContent":true}`
   - `text` = descripción
   - `media` = [URL]
   - `autoPublish`: true
   - `providers`: `[{"network":"youtube"},{"network":"tiktok"}]`, con `tiktokData` `{"privacyOption":"PUBLIC_TO_EVERYONE","title":...,"isAigc":true}`
   - `videoCoverMilliseconds`: 500
4. Horas por defecto: 08:30, 10:00, 11:30, 12:45, 13:45, 14:45, 15:45, 16:30, 17:30 y 19:00.
   Ajústalas con `getBestTimeToPostByNetwork` si hay datos.

## 6. Registro y limpieza

- Añade a `published.md` la fecha, la hora, el título, el gancho con su puntuación, las fuentes y la URL del planner de Metricool.
- Actualiza `assets/used.json`.
- Borra del repositorio las carpetas `days/` de hace más de 7 días, que ya estarán publicadas, para que no crezca demasiado.
