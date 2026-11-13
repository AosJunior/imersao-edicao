# insercoes.json: referência

O plano das inserções. O Claude escreve em `videos/<pasta>/sequencia/insercoes/insercoes.json`; o `motion.py` lê,
monta a página do HyperFrames e grava o storyboard e o vídeo. A `/sonorizar` lê as `camadas` (id, `de`, `ate`) para
prender cada efeito à peça.

```json
{
  "cabeca_y": 430,
  "camadas": [ ... ],
  "legenda": {"destaques": [], "nomes": [], "correcoes": {}, "esconder": []},
  "estilo": {}
}
```

## Tempos (âncoras na fala)

Todo `de`, `ate` e `em` aceita:

| Forma | Exemplo | Em `de` | Em `ate` |
|---|---|---|---|
| segundos | `4.2` | o tempo | o tempo |
| frase | `"F3"` | início da frase | fim da frase |
| borda da frase | `"F3:inicio"`, `"F3:fim"` | essa borda | essa borda |
| palavra pelo texto | `"F3:cabeça"`, `"F3:em#2"` | início da 1ª (2ª) vez | fim dela |
| palavra pela posição | `"F3:4"` | início da 4ª palavra | fim dela |
| deslocamento | `"F1:fim+0.2"`, `"F4:quatro-0.1"` | a âncora ± segundos | idem |

`F<n>` é o id da frase no `sequencia/decupagem/palavras-corte.json` (campo `frases`). A palavra compara sem acento,
maiúscula ou pontuação. Número falado como palavra de âncora leva `#`: `"F4:4#1"` é a palavra "4"; `"F4:4"` é a 4ª
palavra. Âncora numa palavra que o corte tirou é erro, com o nome da palavra.

## cabeca_y

O topo do cabelo, em px, no quadro 1080×1920 (0 é o topo da tela). As peças ficam entre a zona segura (y 260, onde
o Instagram põe o nome do perfil) e a cabeça. Cada tipo precisa de uma altura livre: gancho 150, balão 90, número
300, etapas 330, gráfico 300. Sem essa altura, a peça desce para o peito (pé em y 1520) e a legenda some enquanto
ela está na tela. `"y"` numa camada fixa o pé da peça à mão.

## camadas

Campos de toda camada: `id` (único, letras e números), `tipo`, `de`, `ate`. Opcionais: `"legenda": "some"` ou
`"fica"` (padrão: fica só no balão), `"y"` (pé da peça, em px).

| Tipo | Para quê | Campos | Como entra |
|---|---|---|---|
| `gancho` | o título de abertura, numa placa clara | `texto` | já na tela no quadro 0, assenta e sai no `ate` |
| `balao` | um título curto em cima da cabeça | `texto`, `lado` (`centro`, `esquerda`, `direita`) | pula da cabeça, com mola |
| `numero` | um número dito na fala, grande | `valor` (só o número), `prefixo` ("R$"), `sufixo` ("%", "min"), `casas`, `texto` (linha de baixo) | sobe e conta de 0 até o valor |
| `etapas` | um número e uma barra em partes que acendem uma a uma | `numero`, `texto`, `itens`: 2 a 5 de `{"texto", "em"}` | o painel sobe; cada parte acende no seu `em` |
| `grafico` | comparação em barras | `titulo`, `barras`: 2 a 4 de `{"rotulo", "valor", "texto", "destaque"}` | as barras crescem em escala, uma depois da outra |
| `html` | peça fora dos modelos | `html`, `css` (opcional) | pop simples |

No `texto` do gancho, do balão e da linha de baixo do número, `*palavra*` sai na fonte de destaque (serifa
itálica). Use em uma palavra ou duas.

Limites que o script cobra: uma peça por vez na tela; cada peça com 0,8 s ou mais (aviso acima de 8 s); gancho
começando em 0.

## legenda

Automática, a partir do `palavras-corte.json`: de 2 a 4 palavras por vez, minúsculas, trocando com a fala.

- `destaques`: âncoras de palavra (`"F2:celular"`). A palavra sai na fonte de destaque, maior e na cor de destaque.
- `nomes`: nomes próprios, escritos como devem aparecer (`"Claude"`, `"Instagram"`).
- `correcoes`: o que o Whisper ouviu errado → o certo (`{"Cloud": "Claude"}`).
- `esconder`: pares `[de, ate]` em que a legenda some.

## estilo (só para mudar o padrão)

O padrão é o do `marca/estilo.md` e já está no script. Para um vídeo específico:

| Campo | Padrão | O que é |
|---|---|---|
| `fonte`, `fonte_destaque`, `fonte_apoio` | os arquivos de `marca/fontes/` | arquivo `.ttf` ou `.otf` |
| `tamanho` | 80 | tamanho da legenda, em px |
| `palavras_max` | 4 | palavras por vez (1 a 4) |
| `letras_max` | 22 | letras por linha de legenda |
| `legenda_y` | 1290 | pé das letras da legenda |
| `cor`, `cor_destaque` | `#FFFFFF`, `#FFD23F` | texto e destaque |
| `sombra` | 0.6 | força da sombra do texto, de 0 a 1 |
| `escala_destaque` | 1.3 | tamanho da palavra de destaque em relação à legenda |
| `zona_segura` | `[260, 1600]` | faixa de y em que cabe texto |

## O que o script grava

Em `sequencia/insercoes/`: `motion/` (o projeto HyperFrames; o `index.html` é gerado, mude o plano e não o
arquivo), `storyboard.jpg` e `storyboard/` (os quadros em tamanho cheio), `final-insercoes.mp4`,
`legenda-curta.srt`. Em `sequencia/`: `3-insercoes.mp4`.

O HyperFrames roda por `npx --yes hyperframes@0.9.26`, com a telemetria desligada pelo script.
