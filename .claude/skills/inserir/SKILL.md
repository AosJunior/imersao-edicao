---
name: inserir
description: Passo 3 da imersão de edição de vídeo. Põe no vídeo já cortado e com cor o gancho, até 2 inserções animadas pedidas pela fala (um título em cima da cabeça, um número ou gráfico) e a legenda; mostra antes um storyboard parado para aprovar. Use quando a pessoa mandar /inserir ou pedir gancho, inserções, título na tela, número, gráfico ou legenda no vídeo.
---

# /inserir · passo 3

A pessoa já tem o vídeo cortado e com cor (`sequencia/2-cor.mp4`). Você planeja as peças, mostra o **storyboard**
(uma imagem parada de cada peça), espera o sim e só então anima e entrega `sequencia/3-insercoes.mp4`.

O escopo é fixo: **o gancho**, **até 2 inserções** que a fala pede e **a legenda**. A animação é HyperFrames +
GSAP, e quem monta a página é o script.

**O rosto é zona proibida.** O script acha o rosto nos instantes de cada peça e decide sozinho onde ela pousa: em
cima da cabeça quando há altura livre para a peça inteira; sem espaço, ele afasta o vídeo (o quadro encolhe um
pouco, preso à base, e a peça ocupa a faixa de cima); se nem assim couber, a peça vai para baixo do rosto ou para o
lado. A legenda fica abaixo do queixo. Peça que tocaria o rosto sai contornada de vermelho no storyboard e o script
se recusa a gravar o vídeo.

Rode a partir da pasta da imersão. A saudação do primeiro uso e o jeito de falar estão no `CLAUDE.md` da pasta.
Sem `sequencia/2-cor.mp4`, falta a cor: diga isso e ofereça corrigir a cor pela `/decupar`.

Se `sequencia/insercoes/insercoes.json` já existe, é uma correção: vá ao passo 5.

## 1. Ler a fala e ver o quadro

- `roteiro.txt` (na raiz da pasta): o texto gravado e a tabela das inserções dele. Se o vídeo é o do roteiro, o
  plano sai dessa tabela.
- `sequencia/decupagem/palavras-corte.json`: as frases que ficaram (`frases`, com o id `F<n>`) e o tempo de cada
  palavra no vídeo cortado. Os tempos do plano são **âncoras na fala**: `"F3:cabeça"` é a palavra "cabeça" da F3.
- `marca/estilo.md`: as regras das peças e da legenda.
- O enquadramento:

  ```
  uv run .claude/skills/inserir/scripts/motion.py "videos/<pasta>" --quadros
  ```

  Abra os 3 quadros (Read) para saber como a pessoa está enquadrada. A posição do rosto o script mede sozinho.

Pronto quando você sabe em que palavra entra cada peça.

## 2. Escrever o plano

Grave `sequencia/insercoes/insercoes.json`. Formato e todos os campos em [referencia.md](referencia.md); leia antes
de escrever o primeiro. Para o vídeo do roteiro:

```json
{
  "camadas": [
    {"id": "gancho", "tipo": "gancho", "texto": "Meu primeiro vídeo editado com *IA*", "de": 0, "ate": "F1:fim+0.2"},
    {"id": "titulo", "tipo": "balao", "texto": "editado com *Claude Code*", "de": "F3:cima", "ate": "F3:fim+0.3"},
    {"id": "etapas", "tipo": "etapas", "numero": 4, "texto": "etapas",
     "itens": [{"texto": "cortar", "em": "F4:cortar"}, {"texto": "cor", "em": "F4:cor"},
               {"texto": "inserções", "em": "F4:inserções"}, {"texto": "som", "em": "F4:som"}],
     "de": "F4:quatro", "ate": "F4:fim+0.4"}
  ],
  "legenda": {"destaques": ["F2:celular", "F5:hoje"], "nomes": ["Claude", "Code"], "correcoes": {"Cloud": "Claude"}}
}
```

Os `F<n>` deste exemplo são ilustrativos. No vídeo da pessoa a numeração é a do bruto e pula as frases que o
corte tirou: ache cada frase **pelo texto** no campo `frases` do `palavras-corte.json` e use o id que estiver lá
("Frase 3" do roteiro é a terceira do texto, não a `F3`).

Réguas:

- **Gancho**: o título já está na tela no quadro 0 (`"de": 0`) e sai no fim da primeira frase.
- **Só o que foi dito**: texto, número e nome de cada peça saem da fala ou do roteiro.
- **Cada peça entra na palavra que a pede** e fica de 1,5 a 6 s. Uma peça por vez na tela.
- **Legenda**: de 2 a 4 palavras por vez, automática. Você escolhe 2 ou 3 palavras de destaque (a que carrega a
  frase), corrige em `correcoes` o que o Whisper ouviu errado e lista em `nomes` os nomes próprios.

Confira sem desenhar nada:

```
uv run .claude/skills/inserir/scripts/motion.py "videos/<pasta>" --resumo
```

Na primeira vez ele procura o rosto (uns 15 s; na primeira vez do computador instala o detector, uns 50 MB).
Pronto quando ele lista as peças sem erro, cada uma com a faixa do rosto ("rosto de y … a …"). Se ele disser que
não achou o rosto, meça a caixa do rosto num dos quadros (da testa ao queixo, de uma orelha à outra), multiplique
por 2 e ponha no plano: `"rosto": [x, y, largura, altura]`.

## 3. Storyboard

Avise antes: na primeira vez do computador o HyperFrames baixa o navegador dele (uns 500 MB, 1 a 5 min); depois o
storyboard leva de 10 a 40 s.

```
uv run .claude/skills/inserir/scripts/motion.py "videos/<pasta>" --storyboard
```

Ele grava `sequencia/insercoes/storyboard.jpg`, com um quadro numerado por peça (já pousada) e dois da legenda, e
abre a folha no computador da pessoa. Abra você também (Read) e confira, peça por peça:

- o texto está certo, com acento;
- nada toca o rosto, em nenhum quadro. A saída diz onde cada peça pousou ("acima da cabeça", "com o vídeo
  afastado para 74 %", "abaixo do rosto"). Contorno vermelho ou "ATENÇÃO … cobre o rosto": encurte o texto da
  peça ou troque o tipo, e rode de novo;
- dá para ler em 1 segundo.

Leia também a `sequencia/insercoes/legenda-curta.srt` inteira (o storyboard mostra só duas legendas): palavra
ouvida errado vai em `correcoes`; palavra que a pessoa não disse vai em `apagar`.

Mande no chat uma linha por imagem (número, o que aparece, em que palavra entra) e uma pergunta: "Aprovado? Se
quiser mudar, diga o número da imagem e o que muda."

Pedido de mudança: edite o plano, rode o `--storyboard` de novo e mostre a folha nova.

Pronto quando a pessoa aprova a folha.

## 4. Animar

Com o sim ("Aprovado. Pode animar."), avise que é a espera mais longa do dia (de 2 a 10 minutos, conforme o
computador) e rode em segundo plano:

```
uv run .claude/skills/inserir/scripts/motion.py "videos/<pasta>" --video
```

Ele anima, grava `sequencia/insercoes/final-insercoes.mp4`, copia para `sequencia/3-insercoes.mp4` e abre. Pronto
quando imprime "Pronto: … 3-insercoes.mp4" sem "ATENÇÃO".

Diga em uma linha onde está o arquivo e que ainda falta o som. O próximo passo é `/sonorizar`, numa conversa nova.

## 5. Corrigir

Edite só o que a pessoa pediu no `insercoes.json`, mostre o storyboard de novo (passo 3) e, com o sim, anime de novo
(passo 4). Pedidos comuns: outro texto, a peça em outra palavra (`de`, `ate`), o título mais para um lado
(`"lado": "esquerda"`), outra palavra de destaque. A altura das peças é do script: ele as mantém fora do rosto.

## Quando falha

- **"Falta o Node"**: instale como no passo 1 do `/decupar` e rode de novo.
- **O storyboard ou o vídeo não sai**: o script imprime o comando do HyperFrames que falhou e a pasta. Rode esse
  comando uma vez para ler o erro inteiro. Erro de download: rode
  `uv run .claude/skills/inserir/scripts/motion.py --preparar` e tente de novo.
- **Continua falhando**: diga à pessoa em uma linha, e que o `/sonorizar` funciona com o `2-cor.mp4` enquanto isso.

## Esforço

Plano e correções: esforço médio. É uma conversa só, sem abrir agentes.
