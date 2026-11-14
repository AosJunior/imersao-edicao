---
name: sonorizar
description: Passo 4 da imersão de edição de vídeo. Põe uma trilha e poucos efeitos sonoros no vídeo com os sons da pasta marca/sons (ou do Epidemic Sound, só se a pessoa pedir e tiver o conector), mixa com a voz na frente e entrega o vídeo final em -14 LUFS com os créditos. Use quando a pessoa mandar /sonorizar ou pedir música, trilha, efeito sonoro, mixagem, ou para trocar a trilha, usar o Epidemic Sound ou tirar um efeito.
---

# /sonorizar · passo 4

A pessoa já tem o vídeo com as inserções (`sequencia/3-insercoes.mp4`). Você escolhe **uma** trilha e poucos
efeitos, mostra a lista de sons, espera o sim, mixa e entrega `sequencia/4-final.mp4`.

**Todo som sai de `marca/sons/`**: trilhas em `trilhas/`, efeitos em `efeitos/`, e o `creditos.md` diz o clima de
cada trilha e quando usar cada efeito. Som de fora entra de dois jeitos, e só quando a pessoa pede: ela põe o
arquivo nessa pasta e diz de onde veio, ou pede o Epidemic Sound (seção "Epidemic Sound", abaixo). Sem pedido, use
só o que já está na pasta. Efeito é arquivo gravado, usado como está. Nunca gere som por código (tom, ruído,
síntese): sai metálico.

A **voz manda**: a trilha fica bem abaixo da fala e abaixa sozinha quando a pessoa fala. Efeito é pontuação: só
onde algo acontece na tela, cada um com o seu motivo.

Rode a partir da pasta da imersão. A saudação do primeiro uso e o jeito de falar estão no `CLAUDE.md` da pasta.
Se `sequencia/som/som.json` já existe, é uma correção: vá ao passo 5.

## 1. Ler o vídeo e os sons

- O vídeo: `sequencia/insercoes/final-insercoes.mp4`. Se o passo 3 não rodou, use `sequencia/decupagem/final.mp4`
  e diga em uma linha que o vídeo vai sem inserções.
- A fala: `sequencia/decupagem/palavras-corte.json`. As peças: `sequencia/insercoes/insercoes.json` (cada `camadas[]`
  com `id`, `de` e `ate`).
- Os sons:

  ```
  uv run .claude/skills/sonorizar/scripts/sons.py marca/sons
  ```

  e as tabelas de `marca/sons/creditos.md` (colunas Clima e Quando usar).

Escreva para você o clima do vídeo em uma frase e a lista de eventos: cada peça que entra, e a virada ou o fecho
da fala, se houver.

## 2. Escolher

- **Trilha**: a que combina com o clima do vídeo, pela coluna Clima. Uma só, do começo ao fim.
- **Efeitos**: um por peça que entra (o gancho fica mudo: nada no primeiro segundo) e, no máximo, um no fecho. O
  mesmo tipo de evento leva o mesmo som. Em um vídeo de 20 s isso dá 2 ou 3 efeitos.

### Epidemic Sound (só quando a pessoa pede)

Vale quando ela escreve "usa o Epidemic Sound", "pega uma trilha do Epidemic" ou parecido.

1. Veja se o conector está nesta conversa: as ferramentas dele são `SearchRecordings`, `DownloadRecording`,
   `SearchSoundEffects` e `DownloadSoundEffect`. **Sem elas**, diga em uma linha que o Epidemic Sound precisa da
   assinatura dela conectada ao Claude (Configurações › Conectores) e ofereça seguir com os sons da pasta.
2. **Trilha**: `SearchRecordings` com o clima do vídeo em inglês, `vocals: false` e a faixa de bpm do clima.
   Escolha uma (duas, se ela pediu opções), diga título e autor e por que ela.
3. **Efeito**: `SearchSoundEffects` pelo nome do som. Use como veio, só cortado no tamanho do evento.
4. Baixe na hora, porque o link vale poucos minutos (`DownloadRecording` ou `DownloadSoundEffect`, em WAV):

   ```
   uv run .claude/skills/sonorizar/scripts/sons.py --baixar "<link>" "marca/sons/trilhas/<nome-curto>.wav"
   ```

   Efeito vai para `marca/sons/efeitos/`.
5. Anote o som em `marca/sons/creditos.md`, numa linha nova da tabela certa: arquivo, título, autor, Fonte
   `Epidemic Sound`, o ID da faixa, Licença `Epidemic Sound, assinatura da conta conectada (não repassar o
   arquivo)` e o clima. Sem essa linha o `sonorizar.py` recusa o som.
6. Siga para a lista de sons como com qualquer som da pasta. Diga à pessoa que essa trilha é da assinatura dela:
   serve nos vídeos dela enquanto a assinatura valer, e o arquivo não é para repassar.

## 3. Lista de sons

Grave `sequencia/som/som.json`:

```json
{
  "video": "../insercoes/final-insercoes.mp4",
  "palavras": "../decupagem/palavras-corte.json",
  "insercoes": "../insercoes/insercoes.json",
  "legenda": "../decupagem/legenda.srt",
  "sons": {
    "trilha": {"arquivo": "marca/sons/trilhas/groove.mp3"},
    "pop": {"arquivo": "marca/sons/efeitos/pop.flac"},
    "whoosh": {"arquivo": "marca/sons/efeitos/whoosh.flac"}
  },
  "trilha": {"som": "trilha", "de": 0, "abaixo_da_voz": 16, "fade_in": 0.5, "fade_out": 1.5},
  "efeitos": [
    {"camada": "titulo", "som": "pop", "volume": 0, "motivo": "o título aparece em cima da cabeça"},
    {"camada": "etapas", "som": "whoosh", "volume": 0, "motivo": "o painel das 4 etapas entra"}
  ]
}
```

- Efeito de peça vai com `"camada"` (o `id` no `insercoes.json`); efeito na fala, com `"em"` numa âncora
  (`"F6:Comenta"`). `volume` de 0 a +5 (0 em cima da fala).
- Título, autor e licença de cada som saem sozinhos do `marca/sons/creditos.md`.
- Os outros campos estão em [referencia.md](referencia.md); leia só se precisar de um.

Confira:

```
uv run .claude/skills/sonorizar/scripts/sonorizar.py "videos/<pasta>/sequencia/som/som.json" --resumo
```

Pronto quando ele lista a trilha e os efeitos sem erro. O aviso "menos de 5 s depois do anterior" é esperado num
vídeo de 20 s com duas inserções: mantenha um efeito por peça e não acrescente outro perto.

Mande no chat: a trilha (título e autor) e por que ela, e uma linha por efeito (segundo · som · motivo). Uma
pergunta: "Posso mixar?"

## 4. Mixar e entregar

Com o sim ("Pode mixar."):

```
uv run .claude/skills/sonorizar/scripts/sonorizar.py "videos/<pasta>/sequencia/som/som.json"
```

Leva de 15 s a 1 min por minuto de vídeo. Pronto quando imprime "Pronto", o volume final está a até 1 de −14 LUFS e
"Trilha embaixo da fala" dá 20 ou mais. Abaixo de 20, some 4 ao `abaixo_da_voz` e mixe de novo.

Depois:

```
uv run .claude/skills/sonorizar/scripts/entregar.py "videos/<pasta>"
```

Ele copia o vídeo para `sequencia/4-final.mp4`, os créditos para `sequencia/creditos.md` e abre o vídeo.

Diga em uma linha onde está o vídeo final e que os créditos dos sons estão ao lado. Se o `entregar.py` imprimiu o
bloco `RECADO DA IMERSÃO`, repasse o texto do bloco como está, no fim da resposta.

## 5. Corrigir

Mude só o que a pessoa pediu no `som.json`, mixe e entregue de novo (passo 4):

| Pedido | O que mudar |
|---|---|
| "Troca a trilha por outra da pasta" | o `arquivo` da trilha: a seguinte na listagem do `sons.py`; diga qual entrou (título e autor, do `creditos.md`) |
| "Usa uma trilha do Epidemic Sound" | a seção "Epidemic Sound" do passo 2; depois troque o `arquivo` da trilha |
| "Tira o efeito do segundo 5" | apague a linha do efeito que cai nesse segundo (o `--resumo` mostra os tempos) |
| "Música mais baixa" | `abaixo_da_voz` + 4 |
| "Música mais alta" | `abaixo_da_voz` − 3, sem passar de 12; confira a linha "Trilha embaixo da fala" (20 ou mais) |
| "A música começa em outro ponto" | `"inicio"` na trilha, em segundos da música |

## Limites

- O vídeo precisa ter a voz no próprio arquivo; a trilha e os efeitos entram por baixo dela.
- A voz recebe só um filtro leve. Ruído de fundo, eco e vento ficam como estão.
- Trilha mais curta que o vídeo recomeça do início.
- Esta etapa é mecânica: esforço baixo ou médio.
