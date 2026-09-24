#!/usr/bin/env python3
"""Genera el índice PMD que usa poke-categorias.html.

Lee tracker.json y sprite/NNNN/AnimData.xml de un clon de PMDCollab/SpriteCollab
y reescribe el bloque entre /*PMD-DATA-START*/ y /*PMD-DATA-END*/ de data/pokedata.js.
Así el juego sabe QUÉ retratos (emociones) y QUÉ poses existen de verdad para
cada especie, sin descargar el tracker de 10 MB en cada carga.

Clon liviano (solo lo necesario):
  git clone --depth 1 --filter=blob:none --no-checkout https://github.com/PMDCollab/SpriteCollab sc
  cd sc && git sparse-checkout set --no-cone /tracker.json '/sprite/*/AnimData.xml' && git checkout
Uso:
  python3 tools/build_pmd_index.py ../sc data/pokedata.js
"""
import json, os, re, sys, xml.etree.ElementTree as ET

SC, HTML = sys.argv[1], sys.argv[2]
t = json.load(open(os.path.join(SC, 'tracker.json'), encoding='utf-8'))
ids = [f'{i:04d}' for i in range(1, 1026)]

# Emociones: orden fijo (base primero, luego variantes ^ = mirando a la derecha, luego Special)
BASE = ['Normal','Happy','Pain','Angry','Worried','Sad','Crying','Shouting','Teary-Eyed',
        'Determined','Joyous','Inspired','Surprised','Dizzy','Sigh','Stunned']
SPECIAL = ['Special0','Special1','Special2','Special3']
EMOTIONS = BASE + SPECIAL + [e + '^' for e in BASE + SPECIAL]

# Poses de cuerpo completo que quedan bien como frame estático.
POSES = ['Idle','Walk','Attack','Strike','QuickStrike','SpAttack','Shoot','Swing','Charge',
         'Double','Hop','Hurt','Sleep','Pose','Eat','Sit','LookUp','Float','Appeal','Dance',
         'Punch','Kick','Bite','Slam','Emit','Hover','RearUp','Twirl']

def b36(n):
    s = ''
    while True:
        n, r = divmod(n, 36); s = '0123456789abcdefghijklmnopqrstuvwxyz'[r] + s
        if not n: return s

rows = []
for k in ids:
    e = t[k]
    mask = 0
    for name in e['portrait_files']:
        if name in EMOTIONS: mask |= 1 << EMOTIONS.index(name)
    poses = []
    p = os.path.join(SC, 'sprite', k, 'AnimData.xml')
    files = set(e.get('sprite_files', {}))
    if os.path.exists(p):
        anims = {a.findtext('Name'): a for a in ET.parse(p).getroot().iter('Anim')}
        seen = set()
        for name in POSES:
            a = anims.get(name)
            if a is None: continue
            src = a
            while src is not None and src.find('CopyOf') is not None:   # CopyOf: usa la hoja de otra anim
                src = anims.get(src.findtext('CopyOf'))
            if src is None: continue
            fname = src.findtext('Name')
            if fname in seen or fname not in files or fname not in POSES: continue
            seen.add(fname)
            fw, fh = int(src.findtext('FrameWidth')), int(src.findtext('FrameHeight'))
            n = len(src.findall('Durations/Duration'))
            hit = src.findtext('HitFrame')
            frame = int(hit) if hit is not None else (0 if fname in ('Idle','Walk','Sleep') else n // 2)
            poses.append(f'{b36(POSES.index(fname))}.{b36(fw)}.{b36(fh)}.{b36(min(frame, n-1))}')
    rows.append(b36(mask) + '|' + ','.join(poses))

block = ('/*PMD-DATA-START*/\n'
         f'const PMD_EMOTIONS = {json.dumps(EMOTIONS)};\n'
         f'const PMD_POSES = {json.dumps(POSES)};\n'
         '/* Una fila por especie (#1…#1025): máscara de retratos en base36 | poses "pose.anchoFrame.altoFrame.frame" en base36 */\n'
         f'const PMD_RAW = "{";".join(rows)}";\n'
         '/*PMD-DATA-END*/')
src = open(HTML, encoding='utf-8').read()
out, n = re.subn(r'/\*PMD-DATA-START\*/.*?/\*PMD-DATA-END\*/', lambda m: block, src, flags=re.S)
if n != 1: sys.exit('No encontré el bloque PMD-DATA en ' + HTML)
open(HTML, 'w', encoding='utf-8').write(out)
print(f'OK: {len(rows)} especies, {len(block)//1024} KB de datos')
