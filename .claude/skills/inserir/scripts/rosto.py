# /// script
# requires-python = ">=3.9"
# dependencies = ["opencv-python-headless>=4.8,<5", "numpy"]   # o OpenCV 5 tirou o detector de rostos clássico
# ///
"""/inserir da imersão: acha o rosto em instantes do vídeo. Quem chama é o motion.py.

Uso:  uv run "<skill>/scripts/rosto.py" "<vídeo>" 0.5,2.1,7.8
Imprime uma linha de JSON: {"quadro": [1080, 1920], "rostos": {"0.50": [x, y, l, a] ou null, ...}}
A caixa é a do detector (da testa ao queixo, de uma orelha à outra), em px do quadro do vídeo.
Os quadros chegam por um cano do ffmpeg e o detector é lido da memória: caminho com acento não atrapalha.
"""
import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

LADO = 540   # largura em que o rosto é procurado (basta e é rápido)


def cascata(nome):
    """Lê o detector pelo conteúdo (o OpenCV do Windows não abre arquivo em pasta com acento)."""
    texto = (Path(cv2.data.haarcascades) / nome).read_text(encoding="utf-8")
    try:
        fs = cv2.FileStorage(texto, cv2.FILE_STORAGE_READ | cv2.FILE_STORAGE_MEMORY)
        c = cv2.CascadeClassifier()
        if c.read(fs.getFirstTopLevelNode()) and not c.empty():
            return c
    except Exception:
        pass
    c = cv2.CascadeClassifier(str(Path(cv2.data.haarcascades) / nome))
    return None if c.empty() else c


def quadro(video, t, w, h):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-v", "error", "-ss", f"{max(0.0, t):.2f}", "-i", str(video), "-frames:v", "1",
                        "-vf", f"scale={w}:{h}", "-f", "rawvideo", "-pix_fmt", "gray", "-"], capture_output=True)
    if r.returncode != 0 or len(r.stdout) < w * h:
        return None
    return np.frombuffer(r.stdout[:w * h], dtype=np.uint8).reshape(h, w)


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    video = sys.argv[1]
    tempos = [float(x) for x in sys.argv[2].split(",") if x.strip()]
    p = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                        "-of", "json", video], capture_output=True, text=True, encoding="utf-8", errors="replace")
    st = (json.loads(p.stdout or "{}").get("streams") or [{}])[0]
    W, H = int(st.get("width") or 1080), int(st.get("height") or 1920)
    w = LADO
    h = max(2, int(round(LADO * H / W / 2)) * 2)
    k = W / w
    frente = [c for c in (cascata("haarcascade_frontalface_default.xml"), cascata("haarcascade_frontalface_alt2.xml")) if c]
    lado = cascata("haarcascade_profileface.xml")
    minimo = max(40, w // 8)
    out = {}
    for t in tempos:
        img = quadro(video, t, w, h)
        achou = None
        if img is not None:
            cinza = cv2.equalizeHist(img)
            for c in frente:
                rs = list(c.detectMultiScale(cinza, 1.1, 5, minSize=(minimo, minimo)))
                if rs:
                    achou = max(rs, key=lambda r: r[2] * r[3])
                    break
            if achou is None and lado is not None:
                rs = list(lado.detectMultiScale(cinza, 1.1, 4, minSize=(minimo, minimo)))
                if not rs:                                   # o detector de perfil só olha para um lado: espelha
                    rs = [(w - x - rw, y, rw, rh) for x, y, rw, rh in lado.detectMultiScale(cv2.flip(cinza, 1), 1.1, 4,
                                                                                         minSize=(minimo, minimo))]
                if rs:
                    achou = max(rs, key=lambda r: r[2] * r[3])
        out[f"{t:.2f}"] = None if achou is None else [int(round(float(v) * k)) for v in achou]
    print(json.dumps({"quadro": [W, H], "rostos": out}))


if __name__ == "__main__":
    main()
