# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""/sonorizar da imersão, entrega: copia o vídeo mixado para sequencia/4-final.mp4, leva os créditos junto e abre.

Uso:  uv run "<skill>/scripts/entregar.py" ["<pasta do vídeo>"]

Lê  <pasta do vídeo>/sequencia/som/video-com-som.mp4 e creditos.md (o sonorizar.py grava os dois).
Grava sequencia/4-final.mp4 e sequencia/creditos.md.
Na primeira edição completa desta pasta, imprime também o bloco "RECADO DA IMERSÃO" com o texto de .imersao/oferta.md,
se o arquivo tiver texto. Arquivo vazio: não imprime nada. Uma vez só.
"""
import json
import shutil
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent.parent / "decupar" / "scripts"))
from imersao import entregar, oferta, pasta_do_video, raiz_da_pasta, sair, utf8  # noqa: E402


def main():
    utf8()
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    video = pasta_do_video(args[0] if args else None)
    som = video / "sequencia" / "som"
    nome = "video-com-som.mp4"
    try:
        nome = json.loads((som / "som.json").read_text(encoding="utf-8")).get("saida") or nome
    except Exception:
        pass
    mix = som / nome
    if not mix.is_file():
        sair(f"Falta o vídeo mixado ({mix}). Rode antes o sonorizar.py com o som.json.")
    destino = entregar(mix, video, "final")
    if (som / "creditos.md").is_file():
        shutil.copy2(som / "creditos.md", destino.parent / "creditos.md")
    print(f"Pronto: {destino} · é o vídeo final, com trilha e efeitos. Ele foi aberto para conferir.")
    print(f"Créditos dos sons: {destino.parent / 'creditos.md'}")
    recado = oferta(raiz_da_pasta(video))
    if recado:
        print("\n=== RECADO DA IMERSÃO (repasse à pessoa como está, uma vez) ===")
        print(recado)
        print("=== fim do recado ===")


if __name__ == "__main__":
    main()
