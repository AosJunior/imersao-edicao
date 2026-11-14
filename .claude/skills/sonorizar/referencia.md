# som.json: referência

O Claude escreve em `videos/<pasta>/sequencia/som/som.json`; o `sonorizar.py` lê.

```json
{
  "video": "../insercoes/final-insercoes.mp4",
  "saida": "video-com-som.mp4",
  "palavras": "../decupagem/palavras-corte.json",
  "insercoes": "../insercoes/insercoes.json",
  "legenda": "../decupagem/legenda.srt",
  "sons": {
    "trilha": {"arquivo": "marca/sons/trilhas/groove.mp3"},
    "pop": {"arquivo": "marca/sons/efeitos/pop.flac"},
    "acerto": {"arquivo": "marca/sons/efeitos/acerto.flac"}
  },
  "trilha": {"som": "trilha", "de": 0, "abaixo_da_voz": 16, "fade_in": 0.5, "fade_out": 1.5},
  "efeitos": [
    {"camada": "titulo", "som": "pop", "volume": 0, "motivo": "o título aparece em cima da cabeça"},
    {"em": "F6:Comenta", "som": "acerto", "volume": 0, "motivo": "a chamada final"},
    {"t": 2.1, "som": "pop", "motivo": "evento sem fala nem peça"}
  ]
}
```

## Caminhos

- Começa com `marca/`: vale a partir da pasta da imersão (a que tem `marca/estilo.md`).
- Outros relativos: a partir da pasta do `som.json`.

## Tempos

Todo tempo (`de`, `ate`, `em`, `t`) aceita segundos, `"mm:ss,cc"` ou uma âncora na fala: `"F6"`, `"F6:fim"`,
`"F6:Comenta"`, `"F6:Comenta#2"`, `"F6:3"`, `"F1:fim+0.25"`. As âncoras são as do `palavras-corte.json` (o mesmo
formato do `insercoes.json`). Âncora numa palavra que o corte tirou para o script com a palavra que sumiu.

## sons

Cada som: `arquivo`. Título, autor, fonte e licença saem da linha do arquivo em `marca/sons/creditos.md` (tabela
com a coluna `Arquivo` e as colunas Título, Autor, Fonte, ID e Licença). Som sem licença em lugar nenhum é erro:
anote a linha dele no `creditos.md` antes de usar. Som do Epidemic Sound: Fonte `Epidemic Sound`, o ID da faixa e Licença
`Epidemic Sound, assinatura da conta conectada (não repassar o arquivo)`.

## trilha

| Campo | Padrão | O que faz |
|---|---|---|
| `som` | | nome em `sons` |
| `de` | 0 | onde a trilha entra no vídeo |
| `ate` | o fim | só para acabar antes |
| `inicio` | 0 | o ponto da música que toca quando ela entra (segundos) |
| `abaixo_da_voz` | 16 | quanto a trilha fica abaixo da voz quando ninguém fala; durante a fala ela abaixa mais, sozinha |
| `fade_in` | 1 | entrada |
| `fade_out` | 2 | saída |

## efeitos

Onde cai (um destes):

| Campo | Cai em |
|---|---|
| `camada` | `de` da peça com esse id no `insercoes.json`; com `"em": "fim"`, no `ate` dela |
| `em` | a âncora na fala (sem `camada`) |
| `t` | o tempo, em segundos |

E também: `som` e `motivo` (obrigatórios), `volume` (de 0 a +5; 0 em cima da fala), `desvio` (segundos; adianta
com número negativo).

## Comandos

```
sonorizar.py som.json --resumo            confere tudo; não grava nada
sonorizar.py som.json --trecho 5 15       prévia só desse pedaço (previa-trecho.mp4)
sonorizar.py som.json                     vídeo inteiro, creditos.md e a medida do volume
sons.py <pasta>                           lista sons, duração, pico e licença no creditos.md
entregar.py <pasta do vídeo>              copia para sequencia/4-final.mp4 e abre
```
