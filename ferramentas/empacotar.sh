#!/bin/bash
# Gera o edicao-imersao.zip que o aluno baixa: a pasta edicao-imersao/ pronta para abrir no Claude Code.
# Uso:  ferramentas/empacotar.sh [pasta de destino]      (padrão: ../dist ao lado do repositório)
# Fica de fora: .git, README.md (é do Junior), ferramentas/, o estado de uso (.imersao/*-feita, *-mostrada) e
# qualquer vídeo ou rascunho que esteja em videos/. O GUIA.html é gerado de novo a partir do GUIA.md.
set -euo pipefail
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
DESTINO="${1:-$RAIZ/../dist}"
NOME="edicao-imersao"
mkdir -p "$DESTINO"
DESTINO="$(cd "$DESTINO" && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

if command -v uv >/dev/null 2>&1; then
  (cd "$RAIZ" && uv run ferramentas/gerar-guia.py)
else
  echo "Aviso: sem o uv, o GUIA.html não foi gerado de novo (vai o que está na pasta)."
fi

rsync -a \
  --exclude '.git' --exclude '.gitignore' --exclude 'README.md' --exclude 'ferramentas' \
  --exclude '.DS_Store' --exclude '__pycache__' --exclude '*.pyc' --exclude '*.zip' \
  --exclude '.imersao/saudacao-feita.txt' --exclude '.imersao/oferta-mostrada.txt' \
  --include 'videos/exemplo/***' \
  --include 'videos/*/sequencia/LEIA-ME.txt' --exclude 'videos/*/sequencia/*' \
  --include 'videos/*/brutos/COLOQUE-SEU-VIDEO-AQUI.txt' --exclude 'videos/*/brutos/*' \
  "$RAIZ/" "$TMP/$NOME/"

# travas: o que nunca pode ir para o aluno
if [ ! -f "$TMP/$NOME/.imersao/oferta.md" ]; then echo "ERRO: falta .imersao/oferta.md"; exit 1; fi
if grep -rIl -e 'ELEVEN' -e 'sk-ant-' -e 'api_key' "$TMP/$NOME" >/dev/null 2>&1; then echo "ERRO: parece haver chave no pacote"; exit 1; fi
if find "$TMP/$NOME/videos" -type f \( -iname '*.mp4' -o -iname '*.mov' \) -not -path '*/exemplo/*' | grep -q .; then
  echo "ERRO: há vídeo fora de videos/exemplo no pacote"; exit 1
fi

rm -f "$DESTINO/$NOME.zip"
(cd "$TMP" && zip -r -q -X "$DESTINO/$NOME.zip" "$NOME")
echo "Pacote: $DESTINO/$NOME.zip ($(du -h "$DESTINO/$NOME.zip" | cut -f1))"
if [ -s "$TMP/$NOME/.imersao/oferta.md" ]; then echo "Recado da oferta: LIGADO (o arquivo .imersao/oferta.md tem texto)"; else echo "Recado da oferta: desligado (.imersao/oferta.md vazio)"; fi
echo "Arquivos: $(cd "$TMP" && find "$NOME" -type f | wc -l | tr -d ' ')"
