# cortes.json: referência

O Claude escreve em `videos/<pasta>/sequencia/decupagem/cortes.json`; o `cortar.py` lê.

```json
{
  "pausa_max": 0.22,
  "bordas": "som",
  "trechos": [
    {"de": "F1", "ate": "F2", "nota": "abertura"},
    {"de": "F4:2", "ate": "F7:fim", "nota": "tira o 'esse' gaguejado do começo da F4"},
    {"de": 18.2, "ate": 19.6, "exato": true, "nota": "fica o sorriso do fim"}
  ],
  "ajustes": {"T2.de": 0.04, "T2.ate": -0.03}
}
```

## Trechos

- A ordem da lista é a ordem do vídeo final. `T2` é o 2º trecho da lista (contando de 1).
- Fica a palavra cujo meio cai dentro do trecho. As pausas maiores que `pausa_max` saem sozinhas (deixando um
  respiro curto), e também os sons sem palavra de 0,15 s ou mais dentro da frase.
- `"exato": true` usa `de` e `ate` como estão, sem ajustar às palavras nem tirar pausas. Serve para gesto, sorriso
  ou respiro que precisa ficar.
- `"nota"`: o porquê, que aparece no `--resumo`.

## Tempos de `de` e `ate` (sempre do vídeo bruto)

| Forma | Exemplo | No `de` | No `ate` |
|---|---|---|---|
| frase | `"F12"` | início da frase | fim da frase |
| frase:borda | `"F12:inicio"`, `"F12:fim"` | essa borda | essa borda |
| frase:índice | `"F12:3"` | início da 3ª palavra | fim da 3ª palavra |
| frase:palavra | `"F12:loja"`, `"F12:loja#2"` | início da 1ª (2ª) "loja" | fim dela |
| deslocamento | `"F12:fim+0.2"`, `"F12:loja-0.1"` | a âncora mais ou menos segundos | idem |
| relógio | `"01:47,30"` | o tempo da transcrição | idem |
| segundos | `107.3` | idem | idem |

- `F<n>` é o número da frase na `transcricao.txt`. As palavras contam de 1 dentro da frase, e a comparação ignora
  acento, maiúscula e pontuação. Número falado vai com `#`: a palavra "10" é `"F8:10#1"` (`"F8:10"` é a 10ª palavra).
- Âncora que não existe para o script e diz qual.

## Bordas e ajustes

- `"bordas": "som"`: a borda de cada pedaço de fala sai do volume medido no próprio vídeo, com uma folga curta.
  Pega o fim da palavra que o Whisper encurta antes de uma pausa.
- `pausa_max`: 0.22 é o padrão. 0.18 aperta ("ainda tem pausa"); 0.35 a 0.5 solta ("ficou corrido").
- `ajustes`: deslocamento fino da borda de um trecho, em segundos, de -1 a 1. `"T2.de": 0.04` começa o 2º trecho
  40 ms depois; `"T2.ate": 0.08` termina 80 ms depois (devolve o fim de uma palavra comida).

## Velocidade (só quando a pessoa pede)

`"velocidade": 1.15` acelera vídeo e voz juntos (a voz não fica fina). Vai de 0.5 a 2.0. O `--resumo` e o
`palavras-corte.json` já saem no tempo acelerado, que é o que o `/inserir` e o `/sonorizar` leem.

## Zoom (só quando a pessoa pede)

```json
"zoom": {"ancora": [0.5, 0.4], "niveis": [1.0, 1.12], "alternar_na_pausa": true},
"trechos": [{"de": "F1", "ate": "F2", "zoom": 1.0}, {"de": "F4", "ate": "F7", "zoom": 1.12}]
```

- `zoom.ancora`: o ponto do quadro de saída que fica parado no zoom, em fração `[x, y]` (0 a 1). Ponha perto dos
  olhos; sem ela, `[0.5, 0.4]`.
- `zoom.niveis`: os níveis usados, de 1.0 (sem zoom) a 3.0. Para o vídeo do dia, `[1.0, 1.12]`.
- `zoom.alternar_na_pausa: true`: cada emenda **dentro** de um trecho (pausa tirada) troca para o nível vizinho e
  volta na emenda seguinte. A emenda vira um corte de câmera, e o pulo de imagem some.
- `"zoom"` num trecho: o nível daquele trecho (1.0 se faltar).
- O recorte sai da resolução original do bruto (4K vira 1080 sem perder nitidez até 2×). Com `"vertical"`, o zoom
  aperta dentro da janela 9:16.

Com velocidade ou zoom, o vídeo sai em pedaços (cada um com o número exato de quadros e de amostras de som, para a
boca não sair da fala), guardados na pasta de trabalho: a primeira vez demora mais, e uma correção refaz só os
pedaços que mudaram.

## Vertical (só vídeo gravado deitado)

`"vertical": true` usa o centro do rosto achado pelo `enquadrar.py`; `{"centro_x": 0.42}` fixa à mão (fração da
largura, 0 = borda esquerda). Abra a `enquadrar.jpg` para conferir: a parte clara é o que fica.

## Cor

O campo `"cor"` entra depois do corte: quem escreve é o `aplicar_cor.py`, quando a pessoa aprova a cor.

## O que o cortar.py grava

- `--resumo`: só confere e imprime a duração e o tempo de cada frase no vídeo cortado.
- `--final`: `final.mp4` em 1080×1920 (o `entregar.py` chama assim).
- Sempre: `palavras-corte.json`, com cada palavra e cada frase que ficou, no tempo do vídeo cortado. É o que o
  `/inserir` e o `/sonorizar` leem para achar `"F3:cabeça"` no vídeo.
- Os outros arquivos da pasta `decupagem/` são rascunho do script.
