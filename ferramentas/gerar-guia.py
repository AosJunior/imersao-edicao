# /// script
# requires-python = ">=3.9"
# dependencies = ["markdown>=3.5"]
# ///
"""Gera o GUIA.html (abre com dois cliques) a partir do GUIA.md. Uso: uv run ferramentas/gerar-guia.py"""
import re
from pathlib import Path

import markdown

RAIZ = Path(__file__).resolve().parent.parent
md = (RAIZ / "GUIA.md").read_text(encoding="utf-8")
linhas, dentro = [], False
for linha in md.splitlines():                       # lista colada no parágrafo: o conversor pede uma linha em branco antes
    if linha.startswith("```"):
        dentro = not dentro
    item = re.match(r"(- |\d+\. )", linha) and not dentro
    if item and linhas and linhas[-1].strip() and not re.match(r"(- |\d+\. |  )", linhas[-1]):
        linhas.append("")
    linhas.append(linha)
corpo = markdown.markdown("\n".join(linhas), extensions=["tables", "fenced_code", "sane_lists"])
corpo = corpo.replace("<pre><code>", '<div class="copiar"><pre><code>').replace("</code></pre>", "</code></pre><button type=\"button\">copiar</button></div>")
titulo = re.search(r"^# (.+)$", md, re.M).group(1)
svg = (Path(__file__).resolve().parent / "ativos" / "assinatura.svg").read_text(encoding="utf-8")
svg = re.sub(r"<\?xml[^>]*\?>", "", svg)
pagina = f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titulo}</title>
<style>
  :root {{ --papel:#F4F5F2; --tinta:#202B35; --azul:#2C4A6E; --nevoa:#E4EBF1; --sec:#526274; --grafite:#191C1F; }}
  * {{ box-sizing: border-box; }}
  html {{ background: var(--papel); }}
  body {{ margin: 0 auto; max-width: 760px; padding: 48px 24px 96px; color: var(--tinta); background: var(--papel);
         font: 18px/1.6 Manrope, "Segoe UI", Arial, sans-serif; }}
  .assinatura {{ width: 260px; max-width: 70%; margin-bottom: 32px; }}
  .assinatura svg {{ width: 100%; height: auto; display: block; }}
  h1, h2 {{ font-family: "Source Serif 4", Georgia, serif; font-weight: 600; line-height: 1.2; color: var(--tinta); }}
  h1 {{ font-size: 38px; margin: 0 0 16px; }}
  h2 {{ font-size: 27px; margin: 56px 0 12px; padding-top: 24px; border-top: 1px solid #cfd8df; color: var(--azul); }}
  p, li {{ max-width: 68ch; }}
  hr {{ display: none; }}
  code {{ font: 15px/1.5 ui-monospace, Menlo, Consolas, monospace; background: var(--nevoa); padding: 2px 6px; border-radius: 6px; }}
  .copiar {{ position: relative; margin: 16px 0; }}
  pre {{ margin: 0; background: var(--grafite); color: #fff; padding: 18px 96px 18px 20px; border-radius: 12px; white-space: pre-wrap; word-break: break-word; }}
  pre code {{ background: none; padding: 0; color: inherit; font-size: 16px; }}
  .copiar button {{ position: absolute; top: 10px; right: 10px; font: 600 14px Manrope, Arial, sans-serif; color: var(--grafite);
                    background: #fff; border: 0; border-radius: 8px; padding: 8px 12px; cursor: pointer; }}
  .copiar button:focus-visible {{ outline: 3px solid #2358A3; outline-offset: 2px; }}
  blockquote {{ margin: 12px 0; padding: 4px 20px; border-left: 4px solid var(--azul); background: #fff; border-radius: 0 12px 12px 0; }}
  blockquote p {{ margin: 10px 0; font-family: "Source Serif 4", Georgia, serif; font-size: 20px; }}
  table {{ border-collapse: collapse; width: 100%; margin: 16px 0; font-size: 16px; }}
  th, td {{ text-align: left; vertical-align: top; padding: 10px 12px; border-bottom: 1px solid #cfd8df; }}
  th {{ color: var(--sec); font-weight: 600; }}
  strong {{ font-weight: 700; }}
  @media print {{ body {{ font-size: 12pt; padding: 0; }} .copiar button {{ display: none; }} pre {{ background: #fff; color: #000; border: 1px solid #999; }} h2 {{ break-after: avoid; }} }}
</style>
</head>
<body>
<div class="assinatura" role="img" aria-label="Claude Descomplicado">{svg}</div>
{corpo}
<script>
  document.querySelectorAll(".copiar button").forEach(function (b) {{
    b.addEventListener("click", function () {{
      var t = b.parentNode.querySelector("code").innerText.trim();
      var feito = function () {{ b.textContent = "copiado"; setTimeout(function () {{ b.textContent = "copiar"; }}, 1500); }};
      if (navigator.clipboard && navigator.clipboard.writeText) {{ navigator.clipboard.writeText(t).then(feito, function () {{}}); }}
      else {{ var r = document.createRange(); r.selectNodeContents(b.parentNode.querySelector("code")); var s = getSelection(); s.removeAllRanges(); s.addRange(r); document.execCommand("copy"); feito(); }}
    }});
  }});
</script>
</body>
</html>
"""
(RAIZ / "GUIA.html").write_text(pagina, encoding="utf-8")
print(f"GUIA.html gravado ({len(pagina) // 1024} KB)")
