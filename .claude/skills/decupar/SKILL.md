---
name: decupar
description: Passo 1 da imersão de edição de vídeo. Tira de um vídeo falado os erros, as frases gravadas de novo e as pausas, mostra a lista de cortes e entrega o vídeo cortado, sem cor. Na primeira vez, instala o que falta no computador. Use quando a pessoa mandar /decupar ou pedir para decupar, cortar erros e pausas, ou corrigir um corte já feito.
---

# /decupar · passo 1

A pessoa gravou um vídeo curto falando para a câmera. Você transcreve, decide o que sai, mostra a lista de cortes,
espera o sim e entrega `sequencia/1-decupado.mp4`, **sem cor** (a cor é o passo 2, `/cor`). O bruto só é lido.

Os scripts ficam em `.claude/skills/decupar/scripts/`; rode sempre a partir da pasta da imersão (a que tem `marca/`).
A saudação do primeiro uso e o jeito de falar estão no `CLAUDE.md` da pasta.

Se `sequencia/decupagem/cortes.json` já existe para o vídeo, é uma correção: vá ao passo 6.

## 1. Conferir o computador

```
ffmpeg -version
uv --version
node --version
```

Os três respondem com a versão: siga para o passo 2.

**Falta algum, ou é a primeira vez nesta pasta** (você acabou de fazer a saudação): avise antes de qualquer download,
com estas informações, e espere o sim:

- vai instalar o que edita o vídeo (FFmpeg), o que roda as skills (uv e Node) e baixar o que transcreve a fala
  (Whisper) e o que anima as inserções (HyperFrames);
- são cerca de **2 GB**, uma vez só neste computador; leva de 5 a 15 minutos conforme a internet; o download é
  grande assim mesmo e é esperado; a tela pode parecer parada.

Com o sim ("Pode instalar."):

- **Mac**: `brew install ffmpeg uv node` (só o que faltar). Sem o `brew` (`brew --version` não responde), quem
  instala o Homebrew é a pessoa, porque ele pede a senha do Mac: ela abre o app Terminal, cola o comando da página
  brew.sh, digita a senha (não aparece nada enquanto digita) e avisa quando terminar. Depois rode o `brew install`.
- **Windows**: `winget install --accept-source-agreements --accept-package-agreements Gyan.FFmpeg astral-sh.uv OpenJS.NodeJS.LTS`
  (só o que faltar). O Windows só enxerga programa novo numa janela nova: peça para ela fechar o Claude, abrir de
  novo na mesma pasta e mandar `/decupar` outra vez.

Pronto quando os três comandos respondem com a versão.

## 2. Achar o vídeo

```
uv run .claude/skills/decupar/scripts/preparar.py --conferir
```

A última linha lista os vídeos em `videos/*/brutos/`.

- **Um vídeo**: é ele (mesmo que a pessoa só tenha mandado `/decupar`).
- **Mais de um**: pergunte qual, pelo nome da pasta.
- **Nenhum**: rode `uv run .claude/skills/decupar/scripts/preparar.py` em segundo plano (ele adianta os downloads
  do Whisper e do HyperFrames), diga onde pôr o vídeo (`videos/meu-primeiro-video/brutos`) e que é só mandar
  `/decupar` de novo quando ele estiver lá. Pare aqui.
- Vídeo fora da pasta (ela arrastou um arquivo de outro lugar): copie para `videos/meu-primeiro-video/brutos/` e
  use a cópia.

## 3. Transcrever

Em segundo plano, para o passo 3 não esperar depois (só baixa na primeira vez do computador):

```
uv run .claude/skills/inserir/scripts/motion.py --preparar
```

E a transcrição:

```
uv run .claude/skills/decupar/scripts/transcrever.py "videos/<pasta>/brutos/<arquivo>"
```

Na primeira vez do computador ela baixa o Whisper (os 2 GB do aviso): rode em segundo plano e espere o aviso de
término. Depois disso leva uns 10 s por minuto de vídeo no Mac com chip M e 1 a 2 min por minuto no Windows.

Pronto quando imprime "Pronto" e existe `videos/<pasta>/sequencia/decupagem/transcricao.txt`.

## 4. Decidir os cortes

Leia a `transcricao.txt` inteira (cada frase tem um id `F<n>` e o tempo no bruto) e o `roteiro.txt` da pasta, se o
vídeo for o do roteiro: ele diz o que a pessoa quis falar.

Resolva antes cada **pista** que a transcrição imprimiu:

- **voz sem texto**: o Whisper costuma pular justamente a frase repetida. Escute o pedaço:
  `uv run .claude/skills/decupar/scripts/transcrever.py "<vídeo>" --ouvir 00:08,2 00:11,6`. Se aparecer fala que
  faltava, repita o comando com `--trocar` no fim: a transcrição é corrigida e as frases, renumeradas.
- **possível parte gravada de novo**: confirme lendo as duas frases.

Depois, frase por frase:

- **Gravada de novo**: fica a **última versão boa** (completa, sem tropeço). Sai junto o que foi dito entre as
  versões ("pera", "de novo").
- **Frase recomeçada ou gagueira**: fica a partir do recomeço. `{"de": "F3:2", "ate": "F3:fim"}` tira a primeira
  palavra da F3.
- **Começo e fim**: o vídeo começa na primeira frase útil e termina na última.
- **A fala é da pessoa**: saem só erro, repetição e pausa. Frase boa fica.
- **Pausas**: saem sozinhas as maiores que `pausa_max`. A sua lista é só de trechos.

Grave `sequencia/decupagem/cortes.json`:

```json
{
  "pausa_max": 0.22,
  "bordas": "som",
  "trechos": [
    {"de": "F1", "ate": "F2", "nota": "abertura"},
    {"de": "F4", "ate": "F7", "nota": "fica a segunda versão da frase 3 (a F3 saiu)"}
  ]
}
```

A ordem da lista é a ordem do vídeo. `de` e `ate` são do bruto: a frase (`"F4"`), uma palavra dela (`"F4:2"`,
`"F4:título"`, `"F4:fim"`) ou segundos. O `cortes.json` desta etapa fica sem `"cor"`. Os outros campos estão em
[referencia.md](referencia.md); leia só se precisar de um.

Confira a duração e o tempo de cada frase no vídeo cortado:

```
uv run .claude/skills/decupar/scripts/cortar.py "videos/<pasta>/sequencia/decupagem" --resumo
```

Pronto quando cada frase da transcrição está dentro de um trecho ou tem motivo para ter saído.

## 5. Mostrar a lista de cortes e entregar

Mande no chat: a duração antes → depois, e de 3 a 6 linhas do que sai e por quê (a frase repetida, o erro, as
pausas somadas). Uma pergunta: "Posso cortar assim?"

Com o sim ("Pode cortar."):

```
uv run .claude/skills/decupar/scripts/entregar.py "videos/<pasta>"
```

Ele grava o vídeo em 1080×1920 (uns 15 s por minuto de vídeo no Mac; 1 a 2 min por minuto no Windows), copia para
`sequencia/1-decupado.mp4` e abre. Pronto quando imprime "Pronto: … 1-decupado.mp4".

Diga em uma linha onde está o arquivo e que o vídeo abriu para ela assistir com som. O próximo passo é `/cor`.

## 6. Corrigir

A pessoa aponta o defeito pelo segundo do vídeo cortado ("No segundo 8, sobrou uma pausa"). O `--resumo` do passo 4
mostra qual frase está nesse segundo. Mude só o que ela pediu no `cortes.json` e rode o `entregar.py` de novo:

| Pedido | O que mudar |
|---|---|
| "Sobrou uma pausa" | divida o trecho em dois na pausa, ou desça `pausa_max` para 0.18 |
| "Ficou corrido", "cortou o fim da palavra" | `"ajustes": {"T2.ate": 0.08}` termina o 2º trecho 0,08 s depois (`T2.de` mexe no começo); ou suba `pausa_max` para 0.35 |
| "Tira a frase sobre X" | divida o trecho em volta dela |
| "Mantém a frase sobre X" | devolva a frase ao trecho |

Se o vídeo já passou pelo `/cor`, o `entregar.py` percebe e atualiza o `2-cor.mp4` com o corte novo.

## Limites

- Vídeo gravado deitado: o corte sai deitado. Rode `uv run .claude/skills/decupar/scripts/enquadrar.py
  "<pasta decupagem>"`, ponha `"vertical": true` no `cortes.json` e entregue de novo: o recorte segue o rosto.
- O corte tira imagem e som juntos, no mesmo ponto.
- Esta etapa é mecânica: esforço baixo ou médio.
