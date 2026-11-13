# Estilo dinâmico

O estilo desta pasta: vídeo falado, gravado no celular, com cara de feito à mão. A pessoa fala para a câmera; a
edição tira o que sobra, corrige a cor sem filtro, põe um título de abertura, poucas inserções animadas e a legenda,
e fecha com uma trilha baixa e poucos efeitos. Foi medido nos Reels da Ana e adaptado para fontes e sons que
podem ser repassados.

Medidas em px no quadro 1080 × 1920 (y = 0 no topo); tempos em segundos do vídeo cortado. As skills já trazem
estes valores como padrão: este arquivo é a regra, e o que muda um vídeo específico vai no arquivo de plano dele.

## Corte (`/decupar`)

| Regra | Valor |
|---|---|
| Sai sempre | frase gravada de novo (fica a última versão boa), gagueira, frase recomeçada, conversa de bastidor |
| Pausa dentro da frase | sai acima de 0,22 s (`pausa_max: 0.22`) |
| Bordas | pelo som (`"bordas": "som"`), com o respiro natural no fim da frase |
| Fica sempre | a fala da pessoa: só sai erro, repetição e pausa |

## Cor (`/cor`)

| Regra | Valor |
|---|---|
| O que é | correção: luz e branco medidos no próprio vídeo, mais um acabamento leve |
| Receita | `marca/cores/cor.json`: contraste +8, sombra −4, saturação +5, sem tom quente |
| Régua | pele rosada e natural, sem laranja nem cinza; saturação nunca sobe mais de 10 % |

## Legenda (`/inserir`)

| Regra | Valor |
|---|---|
| Fonte | Be Vietnam Pro **Bold** (`marca/fontes/BeVietnamPro-Bold.ttf`), 80 px |
| Cor | branco `#FFFFFF`, com sombra escura, sem contorno e sem caixa |
| Palavras por vez | de 2 a 4, trocando com a fala, sem animação |
| Letra | minúscula; nomes próprios como se escrevem; número e unidade juntos ("20 segundos") |
| Posição | centrada, pé das letras em y 1290 (no peito, abaixo do rosto) |
| Destaque | 2 ou 3 palavras no vídeo de 20 s: a palavra que carrega a frase, em Instrument Serif *Italic* (`marca/fontes/InstrumentSerif-Italic.ttf`), 1,3 × maior, na cor de destaque `#FFD23F` |
| Some | durante o gancho e enquanto uma peça grande está na tela |

## Peças (`/inserir`)

| Regra | Valor |
|---|---|
| Lugar | acima da cabeça (entre y 260 e o topo do cabelo); sem espaço, no peito. Nunca em cima do rosto |
| Gancho | placa clara `#FCFCFC` com texto `#111111` em Be Vietnam Pro Bold; na tela desde o quadro 0 até o fim da 1ª frase |
| Título em cima da cabeça | balão escuro `#111111` com texto branco, levemente inclinado; entra com mola na palavra que o pede |
| Número e etapas | número grande em Bold, complemento em Instrument Serif Italic; conta ou acende no tempo da fala |
| Gráfico | barras brancas em painel escuro; a barra principal na cor de destaque `#FFD23F` |
| Destaque no texto | uma ou duas palavras em Instrument Serif Italic (`*palavra*` no plano) |
| Quantas | o gancho e até 2 inserções num vídeo de 20 s; uma por vez; de 1,5 a 6 s cada |
| Só o que foi dito | texto, número e nome saem da fala |
| Movimento | chegada rápida com cauda longa, mola leve em posição e tamanho; o que pousou fica parado |

## Som (`/sonorizar`)

| Regra | Valor |
|---|---|
| De onde | só `marca/sons/` (licenças em `marca/sons/creditos.md`) |
| Trilha | uma, do começo ao fim, 16 abaixo da voz; durante a fala ela abaixa sozinha (20 ou mais) |
| Efeitos | um por peça que entra, mais um no fecho, no máximo; gancho mudo; volume de 0 a +5 |
| Volume final | −14 LUFS |

## Cores

| Nome | Valor | Uso |
|---|---|---|
| Branco | `#FFFFFF` | legenda, números |
| Placa | `#FCFCFC` | fundo do gancho |
| Tinta | `#111111` | texto do gancho, fundo do balão e dos painéis |
| Destaque | `#FFD23F` | palavra de destaque da legenda, barra principal |

## Fontes

Be Vietnam Pro (texto) e Instrument Serif (destaque), as duas com a licença SIL Open Font License 1.1, que permite
usar e repassar. Os arquivos e as licenças estão em `marca/fontes/`.
