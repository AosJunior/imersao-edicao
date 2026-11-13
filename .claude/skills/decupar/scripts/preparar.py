# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""/decupar da imersão, preparo: confere o computador e adianta os downloads grandes, para as próximas etapas
não ficarem paradas.

Uso:  uv run "<skill>/scripts/preparar.py"            confere e baixa o que falta (Whisper e HyperFrames)
      uv run "<skill>/scripts/preparar.py" --conferir  só confere, sem baixar nada (menos de 2 s)

Baixa, só na primeira vez deste computador (cerca de 2 GB no total, de 5 a 15 min conforme a internet):
  - o Whisper, que transcreve a fala: é o maior. Para puxar o download ele transcreve um vídeo de teste de 2 s;
  - o HyperFrames e o navegador que ele usa para desenhar as inserções do passo 3 (precisa do Node).
No fim diz o que está pronto, o que falta e quais vídeos achou em videos/*/brutos/.
"""
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
from imersao import brutos_com_video, raiz_da_pasta, utf8  # noqa: E402

HYPERFRAMES = "hyperframes@0.9.26"


def versao(cmd):
    exe = shutil.which(cmd[0])
    if not exe:
        return None
    try:
        r = subprocess.run([exe, *cmd[1:]], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30)
        return ((r.stdout or r.stderr or "").strip().splitlines() or ["ok"])[0][:60]
    except Exception:
        return None


def main():
    utf8()
    raiz = raiz_da_pasta()
    so_conferir = "--conferir" in sys.argv
    falta = []
    for nome, cmd, serve in (("ffmpeg", ["ffmpeg", "-version"], "corta e junta o vídeo"),
                             ("uv", ["uv", "--version"], "roda os programas das skills"),
                             ("node", ["node", "--version"], "roda o HyperFrames, que anima as inserções")):
        v = versao(cmd)
        print(f"{'ok   ' if v else 'FALTA'} {nome}: {v or serve}")
        if not v:
            falta.append(nome)
    if "ffmpeg" in falta or "uv" in falta:
        print("Instale o que falta e rode de novo. Mac: brew install ffmpeg uv node · "
              "Windows: winget install Gyan.FFmpeg astral-sh.uv OpenJS.NodeJS.LTS (depois feche e abra o Claude).")
        sys.exit(2)

    if not so_conferir:
        t0 = time.time()
        print("Whisper: preparando (na primeira vez baixa cerca de 2 GB; a tela fica parada, é normal)...", flush=True)
        with tempfile.TemporaryDirectory(prefix="imersao-") as tmp:
            teste = Path(tmp) / "teste.mp4"
            subprocess.run(["ffmpeg", "-hide_banner", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=gray:s=360x640:r=30:d=2",
                            "-f", "lavfi", "-i", "sine=frequency=220:duration=2", "-shortest", "-pix_fmt", "yuv420p",
                            str(teste)], capture_output=True)
            r = subprocess.run([shutil.which("uv"), "run", str(AQUI / "transcrever.py"), str(teste)], capture_output=True,
                               text=True, encoding="utf-8", errors="replace")
            ok = r.returncode == 0
            print(f"{'ok   ' if ok else 'FALHA'} Whisper ({time.time() - t0:.0f} s)")
            if not ok:
                print("\n".join(((r.stdout or "") + (r.stderr or "")).strip().splitlines()[-6:]))
        if "node" in falta:
            print("HyperFrames: fica para depois de instalar o Node (ele é do passo 3, /inserir).")
        else:
            t1 = time.time()
            print("HyperFrames: preparando (na primeira vez baixa uns 500 MB)...", flush=True)
            env = dict(os.environ, HYPERFRAMES_NO_TELEMETRY="1")
            try:
                r = subprocess.run([shutil.which("npx"), "--yes", HYPERFRAMES, "browser", "ensure"], capture_output=True,
                                   text=True, encoding="utf-8", errors="replace", env=env, timeout=1500)
                ok = r.returncode == 0
            except Exception:
                ok = False
            print(f"{'ok   ' if ok else 'FALHA'} HyperFrames ({time.time() - t1:.0f} s)"
                  + ("" if ok else " · ele tenta de novo no /inserir"))

    vs = brutos_com_video(raiz)
    if vs:
        print("Vídeo(s) em brutos: " + " · ".join(str(v.relative_to(raiz)) for v in vs))
    else:
        print(f"Nenhum vídeo em brutos ainda. Ponha o vídeo gravado em: {raiz / 'videos' / 'meu-primeiro-video' / 'brutos'}")


if __name__ == "__main__":
    main()
