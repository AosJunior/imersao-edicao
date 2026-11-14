# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""A cor da /decupar da imersão: corrige a cor do vídeo já cortado. Primeiro mostra o antes × depois; depois aplica.

Uso:  uv run "<skill>/scripts/aplicar_cor.py" ["<pasta do vídeo>"]             mostra: grava e abre a folha antes × depois
      uv run "<skill>/scripts/aplicar_cor.py" ["<pasta do vídeo>"] --aplicar   aplica: grava sequencia/2-cor.mp4 e abre

A receita da cor fica em <pasta do vídeo>/sequencia/decupagem/cor-proposta.json. Na primeira vez ela nasce da
receita da pasta (marca/cores/cor.json). Para outra cor, o Claude edita o cor-proposta.json e roda de novo.

  mostra    mede o vídeo e grava sequencia/decupagem/cor-antes-depois.jpg (em cima antes, embaixo depois).
            O vídeo ainda não muda.
  --aplicar põe a receita no cortes.json, refaz o vídeo cortado em 1080×1920 com a cor ligada (cortar.py --final)
            e copia para sequencia/2-cor.mp4. A cor é sempre aplicada: se o vídeo sair sem cor, o script para com erro.
"""
import json
import subprocess
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DECUPAR = AQUI
sys.path.insert(0, str(DECUPAR))
from contrato import achar_marca  # noqa: E402
from imersao import abrir, entregar, pasta_do_video, sair, utf8  # noqa: E402

PADRAO = {"corrigir": True, "look": {"nome": "natural", "contraste": 8, "sombra": -4, "calor": 0, "saturacao": 5}}


def receita(dec, video):
    """A receita em uso: cor-proposta.json; se não existe, nasce de marca/cores/cor.json."""
    prop = dec / "cor-proposta.json"
    if prop.is_file():
        try:
            cor = json.loads(prop.read_text(encoding="utf-8"))
            if isinstance(cor, dict) and cor:
                return cor, "cor-proposta.json"
        except json.JSONDecodeError as e:
            sair(f"{prop} com erro de escrita (linha {e.lineno}): {e.msg}. Corrija e rode de novo.", 2)
    cor, origem = dict(PADRAO), "padrão do script"
    marca = achar_marca(video)
    arq = marca / "cores" / "cor.json" if marca else None
    if arq and arq.is_file():
        try:
            lido = json.loads(arq.read_text(encoding="utf-8"))
            if isinstance(lido, dict) and lido:
                cor, origem = lido, "marca/cores/cor.json"
        except json.JSONDecodeError:
            print(f"Aviso: {arq} com erro de escrita; usando o padrão do script.")
    prop.write_text(json.dumps(cor, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return cor, origem


def rodar(script, *args):
    r = subprocess.run([sys.executable, str(DECUPAR / script), *[str(a) for a in args]], capture_output=True,
                       text=True, encoding="utf-8", errors="replace")
    return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()


def folha(dec, cor):
    """Roda o cor.py com a receita dada, sem deixar a receita no cortes.json. Devolve o filtro."""
    cj = dec / "cortes.json"
    original = cj.read_text(encoding="utf-8")
    cortes = json.loads(original)
    cortes["cor"] = cor
    try:
        cj.write_text(json.dumps(cortes, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        cod, out = rodar("cor.py", dec)
    finally:
        cj.write_text(original, encoding="utf-8")
    print(out)
    if cod != 0:
        sair("A medida da cor falhou (acima).", 2)
    filtro = json.loads((dec / ".dados" / "cor.json").read_text(encoding="utf-8")).get("filtro") or ""
    if not filtro:
        sair("ATENÇÃO: com essa receita o vídeo não muda (a luz e o branco já estão no lugar e não há ajuste). "
             "Ponha um ajuste leve em \"look\" no cor-proposta.json e rode de novo.", 2)
    return filtro


def main():
    utf8()
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    video = pasta_do_video(args[0] if args else None)
    dec = video / "sequencia" / "decupagem"
    if not (dec / "cortes.json").is_file() or not (dec / ".dados" / "info.json").is_file():
        sair(f"Não achei o vídeo decupado em {dec}. A cor vem depois do corte: rode antes o corte da /decupar.")
    cor, origem = receita(dec, video)
    print(f"Receita ({origem}): {json.dumps(cor, ensure_ascii=False)}")
    t0 = time.time()
    filtro = folha(dec, cor)
    jpg = dec / "cor-antes-depois.jpg"
    if "--aplicar" not in sys.argv:
        abrir(jpg)
        print(f"Antes × depois: {jpg} ({time.time() - t0:.0f} s). A folha foi aberta: em cima antes, embaixo depois.")
        print("O vídeo ainda não mudou. Com o sim da pessoa, rode de novo com --aplicar.")
        return

    cj = dec / "cortes.json"
    cortes = json.loads(cj.read_text(encoding="utf-8"))
    cortes["cor"] = cor
    cj.write_text(json.dumps(cortes, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    t1 = time.time()
    cod, out = rodar("cortar.py", dec, "--final")
    print("\n".join(out.splitlines()[-6:]))
    final = dec / "final.mp4"
    if cod != 0 or not final.is_file():
        sair("O vídeo com cor não saiu (acima).", 2)
    if "com cor" not in out:
        sair("ATENÇÃO: o vídeo saiu SEM cor. Confira o cor-proposta.json e rode de novo com --aplicar.", 2)
    (dec / ".dados" / "cor-aplicada.json").write_text(json.dumps({"cor": cor, "filtro": filtro}, ensure_ascii=False) + "\n",
                                                      encoding="utf-8")
    destino = entregar(final, video, "cor")
    print(f"Pronto: {destino} · com cor · {time.time() - t1:.0f} s de render. O vídeo foi aberto para conferir.")


if __name__ == "__main__":
    main()
