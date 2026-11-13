# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""/inserir da imersão: gancho, peças animadas e legenda por cima do vídeo cortado, em HyperFrames + GSAP.

Uso:  uv run "<skill>/scripts/motion.py" ["<pasta do vídeo>"] --resumo       só confere o plano e os tempos
      uv run "<skill>/scripts/motion.py" ["<pasta do vídeo>"] --storyboard   uma imagem de cada peça no ápice (abre)
      uv run "<skill>/scripts/motion.py" ["<pasta do vídeo>"] --video        anima, grava sequencia/3-insercoes.mp4 e abre
Sem a pasta, vale a do único vídeo que estiver em videos/*/brutos/.

O rosto é zona proibida: o script acha o rosto (rosto.py) nos instantes de cada peça e decide onde ela pousa (em cima
da cabeça; sem espaço, afasta o vídeo; senão abaixo ou ao lado do rosto). Peça que tocaria o rosto: o --storyboard
acusa em vermelho e sai com código 2, e o --video não grava.

Lê  <pasta do vídeo>/sequencia/insercoes/insercoes.json (o plano, que o Claude escreve; formato no referencia.md),
    sequencia/decupagem/final.mp4 (já com a cor do /cor) e palavras-corte.json, e as fontes de marca/fontes/.
Grava em <pasta do vídeo>/sequencia/:
  insercoes/motion/             o projeto HyperFrames (index.html gerado; não edite à mão, mude o plano)
  insercoes/storyboard.jpg      as peças paradas no ápice, numeradas, para aprovar antes de animar
  insercoes/final-insercoes.mp4 o vídeo com tudo na imagem (a /sonorizar lê este)
  insercoes/legenda-curta.srt   a mesma legenda que está na imagem
  3-insercoes.mp4               a cópia numerada, que abre no fim

O HyperFrames roda por npx na versão fixa abaixo, com a telemetria desligada.
"""
import html
import json
import os
import re
import shutil
import subprocess
import sys
import time
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "decupar" / "scripts"))
from contrato import Ancoras, ErroContrato, achar_marca  # noqa: E402
from imersao import abrir, entregar, pasta_do_video  # noqa: E402

HYPERFRAMES = "hyperframes@0.9.26"
GSAP = "https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"
W, H = 1080, 1920
TIPOS = ("gancho", "balao", "numero", "etapas", "grafico", "html")
# margens da zona proibida, em fração da caixa do detector (que vai da testa ao queixo, de orelha a orelha)
ROSTO_CIMA, ROSTO_BAIXO, ROSTO_LADO = 0.15, 0.12, 0.08    # o rosto: nenhuma peça pode tocar (trava)
CABELO = 0.5                                                # acima da caixa: até onde vai o cabelo
FPS_OK = {"24/1": "24", "25/1": "25", "30/1": "30", "50/1": "50", "60/1": "60",
          "24000/1001": "24000/1001", "30000/1001": "30000/1001", "60000/1001": "60000/1001"}
UNIDADES = {"mil", "milhao", "milhoes", "bilhao", "bilhoes", "reais", "real", "anos", "ano", "dias", "dia",
            "horas", "hora", "minutos", "minuto", "segundos", "segundo", "vezes", "por", "%", "x", "k"}
ESTILO = {
    "fonte": "marca/fontes/BeVietnamPro-Bold.ttf",
    "fonte_destaque": "marca/fontes/InstrumentSerif-Italic.ttf",
    "fonte_apoio": "marca/fontes/BeVietnamPro-Medium.ttf",
    "tamanho": 80,             # legenda, px no quadro 1080×1920
    "palavras_max": 4,         # palavras por vez na legenda (de 2 a 4)
    "letras_max": 22,
    "minusculas": True,
    "juntar_numeros": True,
    "cor": "#FFFFFF",
    "cor_destaque": "#FFD23F",  # só no gráfico (a barra principal) e no grifo do gancho
    "sombra": 0.6,
    "legenda_y": 1290,          # pé das letras da legenda
    "escala_destaque": 1.3,     # a palavra de destaque, na fonte de destaque, dentro da legenda
    "zona_segura": [260, 1600],
}


def utf8():
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def sair(msg, codigo=1):
    print(msg)
    sys.exit(codigo)


def chave(w):
    s = unicodedata.normalize("NFKD", str(w)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9%$]+", "", s)


def fmt_t(s):
    cs = int(round(max(0.0, float(s)) * 100))
    return f"{cs // 6000:02d}:{cs // 100 % 60:02d},{cs % 100:02d}"


def srt_t(t):
    ms = int(round(max(0.0, t) * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def ambiente():
    env = dict(os.environ)
    env["HYPERFRAMES_NO_TELEMETRY"] = "1"
    return env


def npx(args, cwd=None, limite=1500):
    """Roda o HyperFrames pela versão fixa. Devolve (código, saída)."""
    exe = shutil.which("npx")
    if not exe:
        sair("Falta o Node neste computador (ele traz o npx, que roda o HyperFrames). "
             "Mac: brew install node · Windows: winget install OpenJS.NodeJS.LTS "
             "(no Windows, feche e abra o Claude depois de instalar).")
    cmd = [exe, "--yes", HYPERFRAMES, *args]
    try:
        r = subprocess.run(cmd, cwd=cwd, env=ambiente(), capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=limite)
    except subprocess.TimeoutExpired:
        return 124, f"passou de {limite} s"
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def comando(args):
    return "npx --yes " + HYPERFRAMES + " " + " ".join(args)


# ---------------------------------------------------------------- pastas e plano

def achar_video(arg):
    p = pasta_do_video(arg)
    if not (p / "sequencia" / "decupagem" / "palavras-corte.json").is_file():
        sair(f"Não achei o vídeo decupado em {p / 'sequencia' / 'decupagem'}. Primeiro vem o /decupar e depois o /cor.")
    return p


def ler_plano(pasta):
    pj = pasta / "sequencia" / "insercoes" / "insercoes.json"
    if not pj.is_file():
        sair(f"Falta o plano: {pj}. Escreva o insercoes.json (formato no referencia.md desta skill).")
    try:
        plano = json.loads(pj.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        sair(f"insercoes.json com erro de escrita (linha {e.lineno}, coluna {e.colno}): {e.msg}")
    return pj, plano


def texto_rico(txt):
    """"Meu *primeiro* vídeo" -> HTML seguro, com *trecho* na fonte de destaque."""
    partes = re.split(r"\*([^*]+)\*", str(txt))
    out = []
    for i, p in enumerate(partes):
        e = html.escape(p)
        out.append(f'<em>{e}</em>' if i % 2 else e)
    return "".join(out)


def resolver(pasta, plano):
    """Confere o plano e devolve os dados prontos para a página (tempos em segundos do vídeo cortado)."""
    erros, avisos = [], []
    dec = pasta / "sequencia" / "decupagem"
    anc = Ancoras.de_corte(dec / "palavras-corte.json")
    pc = json.loads((dec / "palavras-corte.json").read_text(encoding="utf-8"))
    video = (pasta / "sequencia" / "insercoes" / plano["video"]).resolve() if plano.get("video") else dec / "final.mp4"
    if not video.is_file():
        sair(f"Falta o vídeo {video}. Ele nasce no /decupar (passo 1) e ganha a cor no /cor (passo 2).")
    cortes = dec / "cortes.json"
    if cortes.is_file() and not json.loads(cortes.read_text(encoding="utf-8")).get("cor") and "--sem-cor" not in sys.argv:
        sair("O vídeo ainda está sem a cor do passo 2. Rode o /cor antes (ou, se a pessoa quer mesmo seguir sem cor, "
             "repita este comando com --sem-cor).", 2)
    dur = sondar(video)["duracao"]
    if pc.get("duracao") and abs(float(pc["duracao"]) - dur) > 0.5:
        avisos.append(f"o palavras-corte.json fala de um vídeo de {pc['duracao']:.1f} s e o {video.name} tem {dur:.1f} s: "
                      "rode o cortar.py --final de novo (a legenda pode sair fora do tempo).")

    est = dict(ESTILO)
    est.update(plano.get("estilo") or {})
    zs = est["zona_segura"]

    def T(v, fim, onde):
        try:
            return max(0.0, min(dur, anc.tempo(v, fim)))
        except (ErroContrato, ValueError, TypeError) as e:
            erros.append(f"{onde}: {e}")
            return 0.0

    camadas, ids = [], set()
    for k, c in enumerate(plano.get("camadas") or []):
        onde = f"camadas[{k}]"
        tipo, cid = c.get("tipo"), str(c.get("id") or f"peca{k + 1}")
        if tipo not in TIPOS:
            erros.append(f"{onde}: \"tipo\" é um de {', '.join(TIPOS)} (veio {tipo!r})")
            continue
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", cid) or cid in ids:
            erros.append(f"{onde}: \"id\" único, começando por letra, só letras, números, - e _ (veio {cid!r})")
            continue
        ids.add(cid)
        de, ate = T(c.get("de", 0), False, f"{onde}.de"), T(c.get("ate"), True, f"{onde}.ate")
        if tipo == "gancho" and de > 0.05:
            avisos.append(f"{cid}: o gancho começa em {de:.2f} s; o título precisa estar na tela desde o quadro 0 (\"de\": 0).")
        if ate - de < 0.8:
            erros.append(f"{onde}: fica {ate - de:.2f} s na tela (de {de:.2f} a {ate:.2f}); precisa de 0,8 s ou mais")
            continue
        if ate - de > 8 and tipo != "gancho":
            avisos.append(f"{cid}: {ate - de:.1f} s na tela é muito; peça fica de 1,5 a 6 s.")
        d = {"id": cid, "tipo": tipo, "de": round(de, 3), "ate": round(ate, 3),
             "legenda": c.get("legenda") or ("fica" if tipo == "balao" else "some")}
        if c.get("y") is not None:
            d["y"] = float(c["y"])
        if tipo in ("gancho", "balao"):
            if not str(c.get("texto") or "").strip():
                erros.append(f"{onde}: falta o \"texto\"")
                continue
            d["texto"] = texto_rico(c["texto"])
            d["lado"] = c.get("lado") or "centro"
        elif tipo == "numero":
            try:
                d["valor"] = float(str(c.get("valor")).replace(",", "."))
            except (TypeError, ValueError):
                erros.append(f"{onde}: \"valor\" é o número dito na fala, só o número (ex.: 20)")
                continue
            d["casas"] = int(c.get("casas", 0))
            d["prefixo"], d["sufixo"] = html.escape(str(c.get("prefixo") or "")), html.escape(str(c.get("sufixo") or ""))
            d["texto"] = texto_rico(c.get("texto") or "")
        elif tipo == "etapas":
            itens = c.get("itens") or []
            if not 2 <= len(itens) <= 5:
                erros.append(f"{onde}: \"itens\" leva de 2 a 5 partes, cada uma com \"texto\" e \"em\" (a palavra em que acende)")
                continue
            d["itens"] = []
            for n, it in enumerate(itens):
                quando = T(it["em"], False, f"{onde}.itens[{n}].em") if it.get("em") is not None else de + (n + 1) * (ate - de) / (len(itens) + 1.5)
                d["itens"].append({"texto": html.escape(str(it.get("texto") or "")), "t": round(min(max(quando, de + 0.1), ate - 0.3), 3)})
            d["numero"] = html.escape(str(c.get("numero") if c.get("numero") is not None else len(itens)))
            d["texto"] = html.escape(str(c.get("texto") or ""))
        elif tipo == "grafico":
            barras = c.get("barras") or []
            if not 2 <= len(barras) <= 4:
                erros.append(f"{onde}: o gráfico leva de 2 a 4 barras")
                continue
            try:
                d["barras"] = [{"rotulo": html.escape(str(b["rotulo"])), "valor": float(b["valor"]),
                                "texto": html.escape(str(b.get("texto") or b["valor"])),
                                "destaque": bool(b.get("destaque"))} for b in barras]
            except (KeyError, TypeError, ValueError):
                erros.append(f"{onde}: cada barra tem \"rotulo\" e \"valor\" (número); \"texto\" é o que se lê na ponta")
                continue
            d["titulo"] = html.escape(str(c.get("titulo") or ""))
        else:  # html livre
            if not str(c.get("html") or "").strip():
                erros.append(f"{onde}: o tipo \"html\" leva o campo \"html\" com a peça")
                continue
            d["html"], d["css"] = str(c["html"]), str(c.get("css") or "")
        camadas.append(d)
    camadas.sort(key=lambda x: x["de"])
    for a, b in zip(camadas, camadas[1:]):
        if b["de"] < a["ate"] - 0.01:
            erros.append(f"as peças «{a['id']}» e «{b['id']}» estão na tela ao mesmo tempo "
                         f"({fmt_t(b['de'])} a {fmt_t(a['ate'])}): encurte uma ou mova a outra")

    # ---- onde está o rosto em cada peça (zona proibida) e no vídeo todo (para a legenda)
    amostras = rostos(pasta, video, dur, camadas, plano, avisos, erros)
    todas = [cx for _, cx in amostras]
    for c in camadas:
        perto = [cx for t, cx in amostras if c["de"] - 0.45 <= t <= c["ate"] + 0.1] or todas
        if perto:
            c["f"], c["z"] = zona(perto), zona(perto, cabelo=True)
    geral = None
    if todas:
        baixos = sorted(cx[1] + cx[3] * (1 + ROSTO_BAIXO) for cx in todas)
        geral = {"baixo": round(baixos[min(len(baixos) - 1, int(len(baixos) * 0.85))]),
                 "amostras": [[round(t, 2)] + zona([cx]) for t, cx in amostras]}

    # ---- legenda
    lg = plano.get("legenda") or {}
    palavras = [w for w in pc.get("palavras", []) if str(w.get("w", "")).strip()]
    corr = {chave(k): v for k, v in (lg.get("correcoes") or {}).items()}
    nomes = {chave(n): n for n in (lg.get("nomes") or [])}
    dest = set()
    for k, a in enumerate(lg.get("destaques") or []):
        try:
            _, w = anc.resolver(a)
            if w is None:
                erros.append(f"legenda.destaques[{k}] «{a}»: aponte uma palavra (\"F3:Claude\")")
            else:
                dest.add((w["frase"], w.get("n")))
        except ErroContrato as e:
            erros.append(f"legenda.destaques[{k}]: {e}")
    fora = set()
    for k, a in enumerate(lg.get("apagar") or []):
        try:
            _, w = anc.resolver(a)
            if w is None:
                erros.append(f"legenda.apagar[{k}] «{a}»: aponte uma palavra (\"F4:ou\")")
            else:
                fora.add((w["frase"], w.get("n")))
        except ErroContrato as e:
            erros.append(f"legenda.apagar[{k}]: {e}")
    palavras = [w for w in palavras if (w["frase"], w.get("n")) not in fora]
    esconder = [(c["de"], c["ate"]) for c in camadas if c["legenda"] == "some"]
    for k, par in enumerate(lg.get("esconder") or []):
        if isinstance(par, (list, tuple)) and len(par) == 2:
            esconder.append((T(par[0], False, f"legenda.esconder[{k}]"), T(par[1], True, f"legenda.esconder[{k}]")))

    def limpar(w):
        bruto = str(w["w"]).strip()
        base = bruto.strip(".,;:!…\"“”'()")
        k = chave(base)
        if k in corr:
            base = corr[k]
        elif k in nomes:
            base = nomes[k]
        elif est["minusculas"]:
            base = base.lower()
        return base + ("?" if bruto.endswith("?") else "")

    grupos, i = [], 0
    nmax = max(1, min(4, int(est["palavras_max"])))
    while i < len(palavras):
        g = [palavras[i]]
        j = i + 1
        while j < len(palavras):
            ant, w = g[-1], palavras[j]
            cola = est["juntar_numeros"] and ((re.search(r"\d", str(ant["w"])) and chave(w["w"]) in UNIDADES)
                                             or str(ant["w"]).strip() in ("R$", "US$", "$"))
            cabe = (len(g) < nmax and w["a"] - ant["b"] < 0.35 and w.get("frase") == ant.get("frase")
                    and not re.search(r"[.?!,;:]$", str(ant["w"]).strip())
                    and len(" ".join(limpar(x) for x in g + [w])) <= est["letras_max"])
            if not (cola or cabe):
                break
            g.append(w)
            j += 1
        grupos.append(g)
        i = j
    for n in range(1, len(grupos)):                  # palavra sozinha no fim da frase: puxa a última do grupo anterior
        ant, g = grupos[n - 1], grupos[n]
        if (len(g) == 1 and len(ant) >= 3 and nmax >= 2 and g[0].get("frase") == ant[-1].get("frase")
                and g[0]["a"] - ant[-1]["b"] < 0.35):
            g.insert(0, ant.pop())
    legenda = []
    for n, g in enumerate(grupos):
        a = g[0]["a"]
        prox = grupos[n + 1][0]["a"] if n + 1 < len(grupos) else dur
        b = prox if prox - g[-1]["b"] < 0.45 else g[-1]["b"] + 0.18
        b = min(b, dur)
        for x0, x1 in sorted(esconder):          # começa escondido: entra quando a peça sai, se sobrar tempo de ler
            if x0 - 0.02 <= a < x1:
                a = x1
        cheio = b - a
        b = min([b] + [x0 for x0, x1 in esconder if a < x0 < b])
        if b - a < 0.3 or (b - a < 0.7 and b - a < cheio - 0.05):   # sobrou só um piscar antes da peça: não mostra
            continue
        partes = [(limpar(w), (w["frase"], w.get("n")) in dest) for w in g]
        partes = [(t, d) for t, d in partes if t]
        if not partes:
            continue
        legenda.append({"a": round(a, 3), "b": round(b, 3), "d": any(d for _, d in partes),
                        "t": " ".join(f"<em>{html.escape(t)}</em>" if d else html.escape(t) for t, d in partes),
                        "puro": " ".join(t for t, _ in partes)})
    ndest = sum(1 for x in legenda if x["d"])
    if erros:
        sair("O plano tem erro:\n- " + "\n- ".join(erros), 2)
    return {"video": video, "dur": dur, "estilo": est, "zona": zs, "rosto": geral, "camadas": camadas,
            "legenda": legenda, "avisos": avisos, "ndest": ndest, "fps": sondar(video)["fps"]}


def zona(caixas, cabelo=False):
    """União das caixas do detector com a margem do rosto (ou até o topo do cabelo): [x0, y0, x1, y1]."""
    cima = CABELO if cabelo else ROSTO_CIMA
    return [round(max(0, min(x - w * ROSTO_LADO for x, y, w, h in caixas))),
            round(max(0, min(y - h * cima for x, y, w, h in caixas))),
            round(min(W, max(x + w * (1 + ROSTO_LADO) for x, y, w, h in caixas))),
            round(min(H, max(y + h * (1 + ROSTO_BAIXO) for x, y, w, h in caixas)))]


def rostos(pasta, video, dur, camadas, plano, avisos, erros):
    """[(tempo, [x, y, l, a])]: a caixa do rosto nos instantes de cada peça e ao longo do vídeo.
    Medida pelo rosto.py (guardada em insercoes/.rosto.json). Se o plano traz "rosto": [x, y, l, a], vale ele."""
    manual = plano.get("rosto")
    if manual is not None:
        try:
            x, y, w, h = [float(v) for v in manual]
            if w < 60 or h < 60:
                raise ValueError
            return [(dur / 2, [x, y, w, h])]
        except (TypeError, ValueError):
            erros.append("\"rosto\": é [x, y, largura, altura] da testa ao queixo e de uma orelha à outra, em px do "
                         "quadro 1080×1920")
            return []
    tempos = {round(dur * (k + 0.5) / 10, 2) for k in range(10)}
    for c in camadas:
        n = max(3, min(8, int((c["ate"] - c["de"]) / 0.5) + 1))
        tempos |= {round(min(dur - 0.05, max(0.0, c["de"] - 0.3 + (c["ate"] - c["de"] + 0.3) * k / (n - 1))), 2) for k in range(n)}
    tempos = sorted(tempos)
    st = video.stat()
    chave_cache = {"tamanho": st.st_size, "mtime": int(st.st_mtime)}
    cache = pasta / "sequencia" / "insercoes" / ".rosto.json"
    medido = {}
    if cache.is_file():
        try:
            d = json.loads(cache.read_text(encoding="utf-8"))
            if d.get("video") == chave_cache:
                medido = d.get("rostos") or {}
        except Exception:
            medido = {}
    faltam = [t for t in tempos if f"{t:.2f}" not in medido]
    if faltam:
        uv = shutil.which("uv")
        if uv:
            print(f"Procurando o rosto em {len(faltam)} quadros (na primeira vez instala o detector, uns 50 MB)...", flush=True)
            r = subprocess.run([uv, "run", str(Path(__file__).resolve().parent / "rosto.py"), str(video),
                                ",".join(f"{t:.2f}" for t in faltam)], capture_output=True, text=True, encoding="utf-8",
                               errors="replace")
            try:
                medido.update(json.loads((r.stdout or "").strip().splitlines()[-1])["rostos"])
                cache.parent.mkdir(parents=True, exist_ok=True)
                cache.write_text(json.dumps({"video": chave_cache, "rostos": medido}) + "\n", encoding="utf-8")
            except Exception:
                avisos.append("o detector de rosto não rodou: " + ((r.stderr or r.stdout or "").strip().splitlines() or ["sem saída"])[-1][:160])
    achados = [(t, medido[f"{t:.2f}"]) for t in tempos if medido.get(f"{t:.2f}")]
    if not achados:
        erros.append("não achei o rosto no vídeo. Rode com --quadros, abra um quadro (Read), meça a caixa do rosto "
                     "(da testa ao queixo, de uma orelha à outra), multiplique por 2 e ponha no plano: "
                     "\"rosto\": [x, y, largura, altura]")
    elif len(achados) < len(tempos) * 0.5:
        avisos.append(f"o rosto só apareceu em {len(achados)} de {len(tempos)} quadros; confira o storyboard com atenção.")
    return achados


def sondar(video):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=r_frame_rate,width,height:format=duration", "-of", "json", str(video)],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        sair(f"Não consegui abrir o vídeo {video} (falta o ffmpeg, ou o arquivo está incompleto).")
    d = json.loads(r.stdout or "{}")
    st = (d.get("streams") or [{}])[0]
    return {"duracao": float((d.get("format") or {}).get("duration") or 0), "fps": st.get("r_frame_rate") or "30/1",
            "w": int(st.get("width") or 0), "h": int(st.get("height") or 0)}


# ---------------------------------------------------------------- projeto HyperFrames

def copiar_se_mudou(origem, destino):
    o = Path(origem)
    if destino.exists() and destino.stat().st_size == o.stat().st_size and int(destino.stat().st_mtime) >= int(o.stat().st_mtime):
        return
    destino.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(o, destino)


def montar(pasta, dados):
    proj = pasta / "sequencia" / "insercoes" / "motion"
    (proj / "assets" / "fontes").mkdir(parents=True, exist_ok=True)
    copiar_se_mudou(dados["video"], proj / "assets" / "video.mp4")
    marca = achar_marca(pasta)
    est, faces = dados["estilo"], []
    for nome, campo, peso, estilo_css in (("Legenda", "fonte", 700, "normal"), ("Destaque", "fonte_destaque", 400, "italic"),
                                          ("Apoio", "fonte_apoio", 500, "normal")):
        c = str(est.get(campo) or "")
        arq = None
        if c:
            arq = (marca.parent / c) if c.startswith("marca/") and marca else Path(c).expanduser()
            if not arq.is_absolute():
                arq = pasta / "sequencia" / "insercoes" / c
        if arq and arq.is_file():
            alvo = proj / "assets" / "fontes" / re.sub(r"[^A-Za-z0-9._-]", "-", arq.name)
            copiar_se_mudou(arq, alvo)
            faces.append(f'@font-face {{ font-family: "{nome}"; src: url("assets/fontes/{alvo.name}"); '
                         f'font-weight: {peso}; font-style: {estilo_css}; }}')
        else:
            dados["avisos"].append(f"fonte «{c or campo}» não encontrada: a peça sai na fonte do sistema.")
    modelo = (Path(__file__).resolve().parent.parent / "modelos" / "motion.html").read_text(encoding="utf-8")
    pagina = {"dur": round(dados["dur"], 3), "rosto": dados["rosto"], "zona": dados["zona"], "estilo": est,
              "debug": "--ver-rosto" in sys.argv, "travar": "--video" in sys.argv,
              "camadas": dados["camadas"], "legenda": [{k: x[k] for k in ("a", "b", "t", "d")} for x in dados["legenda"]]}
    css_livre = "\n".join(c.get("css", "") for c in dados["camadas"] if c["tipo"] == "html")
    saida = (modelo.replace("/*FONTES*/", "\n      ".join(faces)).replace("/*CSS_LIVRE*/", css_livre)
             .replace("__GSAP__", GSAP).replace("__DUR__", f"{dados['dur']:.3f}")
             .replace("__DADOS__", json.dumps(pagina, ensure_ascii=False).replace("</", "<\\/")))
    (proj / "index.html").write_text(saida, encoding="utf-8")
    for nome, conteudo in (("hyperframes.json", {"paths": {"blocks": "compositions", "components": "compositions/components",
                                                             "assets": "assets"}, "media": {"autoProxy": True}}),
                           ("meta.json", {"id": "motion", "name": "motion"}),
                           ("package.json", {"name": "motion", "private": True, "type": "module"})):
        if not (proj / nome).exists():
            (proj / nome).write_text(json.dumps(conteudo, indent=2) + "\n", encoding="utf-8")
    srt = []
    for n, x in enumerate(dados["legenda"], 1):
        srt.append(f"{n}\n{srt_t(x['a'])} --> {srt_t(x['b'])}\n{x['puro']}\n")
    (pasta / "sequencia" / "insercoes" / "legenda-curta.srt").write_text("\n".join(srt), encoding="utf-8")
    return proj


def apices(dados):
    """Um instante por peça (já pousada) e dois da legenda (uma palavra comum e uma de destaque)."""
    out = []
    for c in dados["camadas"]:
        folga = 1.25 if c["tipo"] in ("numero", "grafico") else 0.7
        t = c["itens"][-1]["t"] + 0.45 if c["tipo"] == "etapas" else c["de"] + folga
        out.append((min(t, c["ate"] - 0.25), f"{c['tipo']} «{c['id']}»{c.get('onde', '')}"))
    comum = next((x for x in dados["legenda"] if not x["d"]), None)
    forte = next((x for x in dados["legenda"] if x["d"]), None)
    if comum:
        out.append(((comum["a"] + comum["b"]) / 2, f"legenda «{comum['puro']}»"))
    if forte:
        out.append(((forte["a"] + forte["b"]) / 2, f"legenda com destaque «{forte['puro']}»"))
    return sorted(out)


def resumo(dados):
    print(f"Vídeo: {dados['video'].name} · {dados['dur']:.1f} s")
    for c in dados["camadas"]:
        f = c.get("f")
        print(f"  {fmt_t(c['de'])} → {fmt_t(c['ate'])}  {c['tipo']:<8} «{c['id']}»  legenda {c['legenda']}"
              + (f"  · rosto de y {f[1]} a {f[3]}" if f else ""))
    print(f"Legenda: {len(dados['legenda'])} grupos, {dados['ndest']} com palavra de destaque")
    for a in dados["avisos"]:
        print(f"Aviso: {a}")


MODOS = {"cima": "acima da cabeça", "afasta": "acima da cabeça, com o vídeo afastado para {e} %",
         "baixo": "abaixo do rosto", "lado": "ao lado do rosto", "fixo": "na altura pedida no plano (\"y\")"}


def conferir(proj, dados):
    """A trava: abre a página no navegador do HyperFrames, lê onde cada peça pousou e confere, por conta própria,
    que nenhuma toca a caixa do rosto. Devolve a lista de peças que tocam (vazia = pode renderizar)."""
    cod, out = npx(["browser", "path"], limite=600)
    chrome = next((x.strip() for x in reversed(out.strip().splitlines()) if x.strip() and Path(x.strip()).is_file()), None)
    if cod != 0 or not chrome:
        print("Aviso: não consegui abrir o navegador para conferir as peças contra o rosto.")
        return None
    try:
        r = subprocess.run([chrome, "--headless", "--disable-gpu", "--hide-scrollbars", "--window-size=1080,1920",
                            "--allow-file-access-from-files", "--virtual-time-budget=6000", "--dump-dom",
                            (proj / "index.html").resolve().as_uri()], capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=120)
    except Exception as e:  # noqa: BLE001
        print(f"Aviso: a conferência das peças contra o rosto não rodou ({e}).")
        return None
    dom = r.stdout or ""
    if 'data-pronto="1"' not in dom:
        print("Aviso: a página não terminou de se arrumar na conferência (sem internet para o GSAP?).")
        return None
    ruins = []
    por_id = {c["id"]: c for c in dados["camadas"]}
    for m in re.finditer(r'<div[^>]*data-peca="([^"]+)"[^>]*>', dom):
        tag = m.group(0)
        def campo(nome):
            x = re.search(nome + r'="([^"]*)"', tag)
            return x.group(1) if x else ""
        c = por_id.get(m.group(1))
        if not c:
            continue
        caixa = [float(v) for v in campo("data-caixa").split(",")] if campo("data-caixa") else None
        rosto = [float(v) for v in campo("data-rosto").split(",")] if campo("data-rosto") else None
        modo, esc = campo("data-modo"), campo("data-escala")
        c["onde"] = " · " + MODOS.get(modo, modo).format(e=round(float(esc or 1) * 100))
        toca = bool(caixa and rosto and caixa[0] < rosto[2] and caixa[2] > rosto[0] and caixa[1] < rosto[3] and caixa[3] > rosto[1])
        fora = bool(caixa and (caixa[1] < dados["zona"][0] - 1 or caixa[3] > dados["zona"][1] + 1 or caixa[0] < 0 or caixa[2] > W))
        if toca or campo("data-ok") != "1":
            ruins.append(f"«{c['id']}» cobre o rosto (peça em y {caixa[1]:.0f}–{caixa[3]:.0f}, rosto em y {rosto[1]:.0f}–{rosto[3]:.0f})"
                         if caixa and rosto else f"«{c['id']}» não coube sem tocar o rosto")
        elif fora:
            ruins.append(f"«{c['id']}» sai da área segura do Instagram (y {caixa[1]:.0f}–{caixa[3]:.0f})")
    ocultas = len(re.findall(r'data-oculta="1"', dom))
    if ocultas:
        print(f"Legenda: {ocultas} grupo(s) escondido(s) porque cairiam em cima do rosto ou de uma peça.")
    return ruins


def checar(proj):
    cod, out = npx(["check"], cwd=proj, limite=300)
    if cod != 0:
        linhas = [x for x in out.splitlines() if x.strip()][-25:]
        print("ATENÇÃO: o HyperFrames achou problema na página (o vídeo pode sair errado):")
        print("\n".join("  " + x for x in linhas))
    return cod == 0


def quadros(pasta):
    """Três quadros do vídeo cortado, em 540×960, para ver o enquadramento (px do quadro × 2 = px do vídeo)."""
    video = pasta / "sequencia" / "decupagem" / "final.mp4"
    if not video.is_file():
        sair(f"Falta o vídeo {video}. Ele nasce no /decupar (passo 1) e ganha a cor no /cor (passo 2).")
    dur = sondar(video)["duracao"]
    destino = pasta / "sequencia" / "insercoes" / "quadros"
    destino.mkdir(parents=True, exist_ok=True)
    print(f"Vídeo: {video.name} · {dur:.1f} s. Quadros em 540×960 (multiplique o y por 2):")
    for n, fr in enumerate((0.15, 0.5, 0.85), 1):
        arq = destino / f"quadro-{n}.jpg"
        subprocess.run(["ffmpeg", "-hide_banner", "-v", "error", "-y", "-ss", f"{dur * fr:.2f}", "-i", str(video),
                        "-frames:v", "1", "-vf", "scale=540:960:force_original_aspect_ratio=decrease,pad=540:960:(ow-iw)/2:(oh-ih)/2",
                        "-q:v", "4", str(arq)], capture_output=True)
        print(f"  {arq}")


def main():
    utf8()
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--preparar" in sys.argv:
        t0 = time.time()
        cod, out = npx(["browser", "ensure"], limite=1500)
        print("\n".join(out.strip().splitlines()[-4:]))
        print(f"HyperFrames pronto em {time.time() - t0:.0f} s." if cod == 0 else
              "O HyperFrames não baixou agora; ele tenta de novo no /inserir.")
        return
    pasta = achar_video(args[0] if args else None)
    if "--quadros" in sys.argv:
        quadros(pasta)
        return
    pj, plano = ler_plano(pasta)
    dados = resolver(pasta, plano)
    resumo(dados)
    if "--resumo" in sys.argv:
        return
    proj = montar(pasta, dados)
    ins = pasta / "sequencia" / "insercoes"
    if "--storyboard" in sys.argv:
        t0 = time.time()
        checar(proj)
        ruins = conferir(proj, dados)
        pts = apices(dados)
        if not pts:
            sair("O plano não tem peça nem legenda para mostrar.")
        sb = ins / "storyboard"
        if sb.exists():
            shutil.rmtree(sb, ignore_errors=True)
        a = ["snapshot", "--at", ",".join(f"{t:.2f}" for t, _ in pts), "--no-end", "-o", "../storyboard"]
        cod, out = npx(a, cwd=proj, limite=600)
        folha = sb / "contact-sheet.jpg"
        if cod != 0 or not folha.is_file():
            print("\n".join(out.strip().splitlines()[-15:]))
            sair(f"O storyboard não saiu. Para ver o erro inteiro, rode dentro de {proj}: {comando(a)}", 3)
        shutil.copy2(folha, ins / "storyboard.jpg")
        abrir(ins / "storyboard.jpg")
        print(f"Storyboard: {ins / 'storyboard.jpg'} ({time.time() - t0:.0f} s). A folha foi aberta. Na ordem:")
        for n, (t, rot) in enumerate(pts, 1):
            print(f"  {n}. {fmt_t(t)}  {rot}")
        print("Cada quadro em tamanho cheio: " + str(sb))
        if ruins:
            print("ATENÇÃO, o vídeo NÃO será gravado assim (a peça aparece contornada de vermelho no storyboard):\n- "
                  + "\n- ".join(ruins) + "\nEncurte o texto da peça, troque o tipo ou fixe a altura com \"y\".")
            sys.exit(2)
        return
    if "--video" in sys.argv:
        t0 = time.time()
        if not checar(proj):
            print("Seguindo mesmo assim; confira o vídeo.")
        ruins = conferir(proj, dados)
        if ruins is None:
            ruins = conferir(proj, dados)        # uma segunda tentativa (máquina ocupada)
        if ruins is None:
            print("Aviso: a conferência contra o rosto não rodou. As peças foram postas fora do rosto pela página, e "
                  "peça que tocaria o rosto fica de fora do vídeo. Confira o resultado.")
        if ruins:
            sair("O vídeo não foi gravado: há peça em cima do rosto.\n- " + "\n- ".join(ruins)
                 + "\nEncurte o texto da peça, troque o tipo ou fixe a altura com \"y\", e veja o storyboard de novo.", 2)
        saida = ins / "final-insercoes.mp4"
        tmp = "final-insercoes.parcial.mp4"
        a = ["render", "-o", tmp, "--fps", FPS_OK.get(dados["fps"], "30"), "--crf", "18", "--quiet"]
        cod, out = npx(a, cwd=proj, limite=3000)
        feito = proj / tmp
        if cod != 0 or not feito.is_file() or feito.stat().st_size < 10000:
            print("\n".join(x for x in out.strip().splitlines() if "initSession" not in x and "runtime fps" not in x)[-1500:])
            sair(f"O vídeo não saiu. Para ver o erro inteiro, rode dentro de {proj}: {comando(a)}", 3)
        shutil.move(str(feito), str(saida))
        d = sondar(saida)
        aviso = "" if abs(d["duracao"] - dados["dur"]) < 0.2 else f" · ATENÇÃO: esperava {dados['dur']:.1f} s"
        destino = entregar(saida, pasta, "insercoes")
        print(f"Pronto: {destino} · {d['duracao']:.1f} s · {d['w']}×{d['h']} · {time.time() - t0:.0f} s de render{aviso}. "
              "O vídeo foi aberto para conferir.")
        return
    print("Plano conferido. Rode com --storyboard (imagens para aprovar) e depois com --video.")


if __name__ == "__main__":
    main()
