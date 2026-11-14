# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""/decupar da imersão, entrega: grava o vídeo cortado em 1080×1920, SEM cor, em sequencia/1-decupado.mp4 e abre.

Uso:  uv run "<skill>/scripts/entregar.py" ["<pasta do vídeo>"]

Roda o cortar.py --final e copia o resultado para <pasta do vídeo>/sequencia/1-decupado.mp4.
Se a cor do passo 2 já foi aplicada neste vídeo (o corte está sendo corrigido depois da cor), quem regrava é o
aplicar_cor.py: o 2-cor.mp4 é atualizado com o corte novo e o 1-decupado.mp4 fica como estava.
"""
import json
import subprocess
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
from imersao import entregar, pasta_do_video, sair, utf8  # noqa: E402


def main():
    utf8()
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    video = pasta_do_video(args[0] if args else None)
    dec = video / "sequencia" / "decupagem"
    if not (dec / "cortes.json").is_file():
        sair(f"Falta o {dec / 'cortes.json'}: a lista de cortes ainda não foi gravada.")
    cortes = json.loads((dec / "cortes.json").read_text(encoding="utf-8"))
    if cortes.get("cor"):
        if (dec / ".dados" / "cor-aplicada.json").is_file():
            print("Este vídeo já tem a cor aplicada: regravando o corte novo já com a cor (2-cor.mp4).")
            r = subprocess.run([sys.executable, str(AQUI / "aplicar_cor.py"), str(video),
                                "--aplicar", *[a for a in sys.argv[1:] if a.startswith("--")]])
            sys.exit(r.returncode)
        cortes.pop("cor")    # a cor é do passo 2: aqui o corte sai sem ela
        (dec / "cortes.json").write_text(json.dumps(cortes, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print("Tirei o \"cor\" do cortes.json: a cor entra depois do corte, pela própria /decupar.")
    t0 = time.time()
    r = subprocess.run([sys.executable, str(AQUI / "cortar.py"), str(dec), "--final"], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    out = ((r.stdout or "") + (r.stderr or "")).strip()
    print("\n".join(out.splitlines()[-8:]))
    final = dec / "final.mp4"
    if r.returncode != 0 or not final.is_file():
        sair("O vídeo cortado não saiu (acima).", 2)
    destino = entregar(final, video, "decupado")
    print(f"Pronto: {destino} · sem cor · {time.time() - t0:.0f} s. O vídeo foi aberto para conferir.")


if __name__ == "__main__":
    main()
