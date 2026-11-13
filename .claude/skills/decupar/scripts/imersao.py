"""O que é só da pasta da imersão: a pasta sequencia/, os quatro vídeos numerados, abrir o arquivo e os avisos
de marketing (oferta). Só biblioteca padrão. As skills /decupar, /cor, /inserir e /sonorizar importam daqui."""
import os
import shutil
import subprocess
import sys
from pathlib import Path

ETAPAS = {"decupado": "1-decupado.mp4", "cor": "2-cor.mp4", "insercoes": "3-insercoes.mp4", "final": "4-final.mp4"}
VIDEO = {".mp4", ".mov", ".m4v", ".mkv", ".webm", ".avi", ".mts", ".3gp"}


def utf8():
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def sair(msg, codigo=1):
    print(msg)
    sys.exit(codigo)


def raiz_da_pasta(de=None):
    """A pasta da imersão: a primeira, subindo, que tem marca/estilo.md. Sem ela, a pasta atual."""
    p = Path(os.path.abspath(de or os.getcwd()))
    for x in [p, *p.parents]:
        if (x / "marca" / "estilo.md").is_file():
            return x
    return p


def brutos_com_video(raiz):
    """Vídeos que a pessoa pôs em videos/<nome>/brutos/ (a pasta exemplo fica de fora)."""
    achados = []
    base = raiz / "videos"
    if base.is_dir():
        for pasta in sorted(base.iterdir()):
            if pasta.name == "exemplo" or not (pasta / "brutos").is_dir():
                continue
            achados += sorted(f for f in (pasta / "brutos").iterdir()
                              if f.is_file() and f.suffix.lower() in VIDEO and not f.name.startswith("."))
    return achados


def pasta_do_video(arg=None):
    """Aceita o vídeo bruto, a pasta do vídeo, brutos/, sequencia/ ou uma pasta de trabalho dentro dela.
    Sem argumento: a pasta do único vídeo que estiver em videos/*/brutos/."""
    if not arg:
        vs = brutos_com_video(raiz_da_pasta())
        pastas = sorted({v.parent.parent for v in vs})
        if len(pastas) != 1:
            sair("Diga qual é a pasta do vídeo (por exemplo: videos/meu-primeiro-video)." if pastas else
                 "Não achei vídeo em videos/meu-primeiro-video/brutos. Ponha o vídeo gravado lá e peça de novo.")
        return pastas[0]
    p = Path(os.path.abspath(Path(arg).expanduser()))
    if p.is_file():
        p = p.parent
    while p.name in ("brutos", "sequencia", "decupagem", "insercoes", "som", "motion", ".dados") and p.parent != p:
        p = p.parent
    return p


def sequencia(pasta_video):
    return Path(pasta_video) / "sequencia"


def abrir(arquivo):
    """Abre o arquivo no programa padrão do computador (o vídeo no player, a imagem no visualizador)."""
    if os.environ.get("IMERSAO_NAO_ABRIR") or "--nao-abrir" in sys.argv:
        return
    try:
        if sys.platform == "darwin":
            subprocess.Popen(["open", str(arquivo)])
        elif sys.platform.startswith("win"):
            os.startfile(str(arquivo))  # noqa: S606
        else:
            subprocess.Popen(["xdg-open", str(arquivo)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:  # noqa: BLE001
        print(f"(não consegui abrir sozinho: {e}. Abra pelo Finder ou pelo Explorador: {arquivo})")


def entregar(origem, pasta_video, etapa):
    """Copia o resultado da etapa para sequencia/<n>-<nome>.mp4, abre e devolve o caminho."""
    destino = sequencia(pasta_video) / ETAPAS[etapa]
    destino.parent.mkdir(parents=True, exist_ok=True)
    try:
        shutil.copy2(origem, destino)
    except PermissionError:
        # Windows: o vídeo antigo ainda está aberto no player e não pode ser trocado. Grava ao lado, com outro nome.
        novo = destino.with_name(destino.stem + "-novo" + destino.suffix)
        shutil.copy2(origem, novo)
        print(f"Aviso: o {destino.name} antigo está aberto em outro programa e não pôde ser trocado. O vídeo novo é o "
              f"{novo.name}. Feche o player antes do próximo passo.")
        destino = novo
    abrir(destino)
    return destino


def oferta(raiz):
    """O recado da oferta, uma vez só: devolve o texto de .imersao/oferta.md se ele tem texto e ainda não foi
    mostrado nesta pasta (e marca como mostrado). Arquivo vazio ou ausente: devolve None."""
    arq, feito = raiz / ".imersao" / "oferta.md", raiz / ".imersao" / "oferta-mostrada.txt"
    try:
        texto = arq.read_text(encoding="utf-8").strip() if arq.is_file() else ""
    except OSError:
        texto = ""
    if not texto or feito.exists():
        return None
    try:
        feito.write_text("mostrada\n", encoding="utf-8")
    except OSError:
        pass
    return texto
