---
name: cor
description: Passo 2 da imersão de edição de vídeo. Corrige a cor do vídeo já decupado (luz, branco e um acabamento leve, sem filtro), mostra o antes e depois e entrega o vídeo com cor. Use quando a pessoa mandar /cor ou pedir para corrigir, clarear, esquentar ou ajustar a cor do vídeo.
---

# /cor · passo 2

A pessoa já tem o vídeo cortado pelo `/decupar`. Você mostra o antes × depois, espera o sim e entrega
`sequencia/2-cor.mp4`. É **correção**: tira o tom puxado da luz e dá um acabamento leve, com a pele rosada e
natural. A correção é sempre aplicada: este passo só termina com o `2-cor.mp4` gravado.

Rode a partir da pasta da imersão. A saudação do primeiro uso e o jeito de falar estão no `CLAUDE.md` da pasta.
Sem `sequencia/1-decupado.mp4`, o passo 1 ainda não rodou: diga isso e ofereça o `/decupar`.

## 1. Mostrar o antes × depois

```
uv run .claude/skills/cor/scripts/aplicar.py "videos/<pasta>"
```

Sem a pasta, ele usa a do único vídeo que estiver em `videos/*/brutos/`. Leva menos de 10 s no Mac e uns 30 s no
Windows. Ele grava `sequencia/decupagem/cor-antes-depois.jpg` (em cima antes, embaixo depois) e abre a folha no
computador da pessoa. O vídeo ainda não muda.

Abra a folha você também (Read) e olhe a pele: rosada e natural, sem laranja nem cinza. Se a saída trouxer
"ATENÇÃO", ajuste a receita (passo 3) antes de mostrar.

Diga em uma linha o que a correção fez e pergunte: "Posso aplicar?"

Pronto quando a folha existe e a pessoa viu.

## 2. Aplicar

Com o sim ("Pode aplicar."):

```
uv run .claude/skills/cor/scripts/aplicar.py "videos/<pasta>" --aplicar
```

Ele refaz o vídeo cortado com a cor ligada (uns 15 s por minuto de vídeo no Mac; 1 a 2 min por minuto no Windows),
copia para `sequencia/2-cor.mp4` e abre. Pronto quando imprime "Pronto: … 2-cor.mp4 · com cor".

Diga em uma linha onde está o arquivo. O próximo passo é `/inserir`, numa conversa nova.

## 3. Outra cor

A receita em uso fica em `sequencia/decupagem/cor-proposta.json` (nasce de `marca/cores/cor.json`). Mude **um**
número por pedido, rode o passo 1 de novo, mostre a folha nova e espere o sim para o passo 2.

| Pedido | Campo de `look` | Passo | Faixa |
|---|---|---|---|
| "mais quente" | `calor` | +0.2 | 0 a 1 |
| "menos quente", "a pele ficou laranja" | `calor` e depois `saturacao` | −0.2 · −3 | `calor` até 0; `saturacao` de −10 a 5 |
| "mais claro" | `sombra` | +6 | −20 a 20 |
| "mais escuro" | `sombra` | −6 | −20 a 20 |
| "mais contraste", "mais vivo" | `contraste` | +4 | −20 a 20 |
| "mais suave", "lavado demais" → menos | `contraste` | −4 | −20 a 20 |
| "sem acabamento, só a correção" | apague o `look` | | |

`"corrigir": true` (luz e branco medidos no próprio vídeo) fica sempre ligado. Pedido de filtro ou de copiar a cor
de outro vídeo fica fora deste passo: diga isso em uma linha e ofereça o ajuste mais próximo da tabela.
