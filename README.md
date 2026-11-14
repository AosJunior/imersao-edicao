# imersao-edicao · a pasta do aluno da imersão de 14/11/2026

Este README é para o Junior. O aluno não o recebe: o empacotador deixa de fora este arquivo, `ferramentas/` e o
`.git`.

A raiz deste repositório **é** a pasta que o aluno baixa em `.zip`, descompacta e abre no Claude Code (aba Code do
app, escolher a pasta). Não há `npx`, GitHub nem instalação em `~/.claude`: as skills moram em `.claude/skills/`
dentro da própria pasta. Montado em 13/11/2026, a partir do kit público `AosJunior/claude-skills` no commit
`091416b` (HyperFrames travado na 0.9.26) e do que foi combinado na reunião de 12/11 e no `roteiro-da-aula.md`.

## O que o aluno digita

| Passo | Pedido | Depois |
|---|---|---|
| abrir | `O que tem nesta pasta?` | |
| 1 | `/decupar O meu vídeo está em videos/meu-primeiro-video/brutos. Tira os erros e as pausas, não mexe na cor e me mostra o que vai cortar antes de cortar.` | `Pode instalar.` · `Pode cortar.` |
| 2 | `/cor Corrige a luz e o branco do meu vídeo, sem filtro. Me mostra o antes e depois antes de aplicar.` | `Pode aplicar.` |
| 3 | `/inserir Coloca o gancho, as 2 inserções do roteiro e a legenda. Antes de animar, me mostra uma imagem de cada inserção.` | `Aprovado. Pode animar.` |
| 4 | `/sonorizar Coloca trilha e efeitos só com os sons da pasta marca/sons. Não cria nenhum som. Me mostra onde entra cada som antes de mixar.` | `Pode mixar.` |

Os quatro comandos também funcionam sozinhos (`/decupar`, sem a frase) e em conversa nova: o estado fica em
`videos/<vídeo>/sequencia/`.

## Estrutura

```
COMECE-AQUI.txt  GUIA.html  GUIA.md  roteiro.txt     o que o aluno lê (.txt e .html abrem com dois cliques)
CLAUDE.md                                            o que o Claude lê ao abrir a pasta
.claude/skills/{decupar,cor,inserir,sonorizar}/      as skills da imersão
.claude/settings.json                                permissões já liberadas (ver "Permissões")
.imersao/oferta.md                                   o recado da oferta; vazio = desligado
marca/estilo.md  fontes/  cores/cor.json  sons/      a identidade pronta
videos/meu-primeiro-video/brutos/                    o aluno põe o vídeo aqui
videos/meu-primeiro-video/sequencia/                 1-decupado.mp4 · 2-cor.mp4 · 3-insercoes.mp4 · 4-final.mp4
videos/exemplo/                                      plano B: só um LEIA-ME; falta você gravar e pôr o seu
ferramentas/empacotar.sh  gerar-guia.py              só no repositório
```

Dentro de `sequencia/` nascem também `decupagem/`, `insercoes/` e `som/`: são as pastas de trabalho do kit (os
scripts leem umas das outras por caminho relativo, então ficaram com o nome do kit) e o `creditos.md` do vídeo.

## O que mudou em relação ao kit

### Voltou em 14/11, a pedido do Junior

- `/decupar`: **zoom nos cortes e velocidade**, só quando a pessoa pede ("põe zoom nos cortes", "deixa mais
  rápido"). O motor (`cortar.py`) nunca saiu; voltou a instrução na skill e na referência. O pedido do dia segue sem
  os dois. Testado em 14/11 no Mac: corte e cor com zoom 1,12 e 1,15× de velocidade. `/inserir` e `/sonorizar`
  sobre um vídeo com zoom ou velocidade não foram testados.
- `/sonorizar`: **Epidemic Sound**, só quando a pessoa pede e o conector está na conversa. O som é baixado para
  `marca/sons/` e anotado no `creditos.md`. Não testado nesta pasta; o aluno, sem assinatura, segue com os sons CC0.

### Saiu

- Skills: `/minha-edicao`, `/criticar`, `/reel-novela`, `docs-init`, `primeiro-valor`. Nada de `/black-motion` nem
  `/motion-apple`.
- Da `/decupar`: a cor (virou o `/cor`), a lista de ganchos e de "onde cabe imagem", a
  `decupagem.md`, a oferta do final à parte, o XML do Premiere e o guia do CapCut como entrega (o `cortar.py` ainda
  grava os dois arquivos na pasta de trabalho, só não são anunciados), a conferência com Whisper do vídeo cortado, a
  chamada à `/criticar`, o "pedido completo" com grilling, o LUT (`lut_capcut.py` não veio).
- Da `/inserir`: **todo o motor de cartões** (`inserir.py`, `compor.py`, `legenda.py`, `mascara.py`,
  `mascara_vision.swift`, `print.py`, `modelos/cartao.html`, `windows.md`) e com ele cartões de lista, etapas,
  comparação, print de site, imagem, colagem, tela dividida, vídeo atrás da pessoa com máscara, letterings em HTML
  da marca, `prompts.md` de imagem gerada, e o navegador do Playwright (600 MB a menos para baixar). Saíram também
  as cópias das skills oficiais de GSAP e HyperFrames (`referencias/`), o modo "100 % motion só com a voz", os
  agentes por cena e a telemetria ligada (o script desliga).
- Da `/sonorizar`: a busca de trilha nos Reels da pessoa, no YouTube e no Pixabay, o `identificar.py`
  (Shazam), o áudio em alta, as três candidatas com prévia (agora propõe **uma**), a roleta montada, a conferência
  de fala com Whisper (`ouvir.py` não veio), a pasta `entrega/`, a versão sem trilha, "Fala baixa".

### Entrou

- **`/cor`** (skill nova): `cor/scripts/aplicar.py`. Ver "Como a cor foi separada".
- **`/inserir` com gerador**: `inserir/scripts/motion.py` + `inserir/modelos/motion.html` + `inserir/scripts/rosto.py`.
  O Claude escreve um plano pequeno (`insercoes.json`: gancho, balão em cima da cabeça, número, etapas, gráfico,
  legenda) e o script monta a página do HyperFrames, tira o storyboard (`snapshot`) e renderiza (`render`).
  **O rosto é zona proibida**: o `rosto.py` (o mesmo detector do `enquadrar.py` do kit) acha o rosto nos instantes
  de cada peça; a página põe a peça em cima da cabeça se couber inteira, senão afasta o vídeo (encolhe preso à
  base, até 68 %) para abrir a faixa de cima, senão põe abaixo ou ao lado do rosto. A trava: antes do storyboard e
  do vídeo o script abre a página no navegador do HyperFrames, lê onde cada peça pousou e confere contra a caixa do
  rosto; peça que toca sai em vermelho no storyboard e o `--video` não grava. Motivo: no kit o motion é
  HTML escrito do zero por agentes em Opus (os 20 a 40 min da reunião); com 40 leigos no plano de 20 dólares isso
  não fecha. O modelo fixa o desenho e o movimento; o aluno muda texto, tempo e posição pelo plano. **É código
  novo, de hoje, testado só neste Mac.**
- `decupar/scripts/imersao.py` (pasta `sequencia/`, vídeos numerados, abrir o arquivo, recado da oferta),
  `decupar/scripts/entregar.py` (grava `1-decupado.mp4`), `decupar/scripts/preparar.py` (confere o computador e
  adianta os downloads do Whisper e do HyperFrames), `sonorizar/scripts/entregar.py` (grava `4-final.mp4`).

### Mexido nos scripts do kit (3 pontos, o resto é cópia do `091416b`)

1. `decupar/scripts/comum.py`, `pasta_decupagem`: bruto dentro de `brutos/` faz a decupagem nascer em
   `<vídeo>/sequencia/decupagem/` (no kit nasceria dentro de `brutos/`).
2. `decupar/scripts/cor.py`, `filtro`: tirei o `pl=1` do `colorbalance` (o tom quente, `calor`). Com o ffmpeg 9.0.1
   ele manchava de rosa as áreas claras estouradas (a camisa branca do teste). **Vale levar para o kit.**
3. A `/inserir` não tem `contrato.py` próprio: o `motion.py` importa o da `/decupar` (as skills viajam juntas na
   pasta). O da `/sonorizar` é a cópia do kit.

## Como a cor foi separada

- O `/decupar` grava o `cortes.json` **sem** `"cor"` e entrega `1-decupado.mp4` (o `entregar.py` tira o campo se
  ele aparecer).
- O `/cor` roda o `aplicar.py` duas vezes. Sem flag: põe a receita num arquivo à parte
  (`sequencia/decupagem/cor-proposta.json`, que nasce de `marca/cores/cor.json`), roda o `cor.py` do kit e abre a
  folha antes × depois; o vídeo não muda. Com `--aplicar`: escreve a receita no `cortes.json`, roda
  `cortar.py --final` (refaz os pedaços com a cor ligada), confere que a saída diz "com cor" (senão para com erro) e
  copia para `2-cor.mp4`. Não depende de instrução: a skill só termina com o `2-cor.mp4` gravado.
- O `/inserir` lê `sequencia/decupagem/final.mp4` e **para** se o `cortes.json` não tem `"cor"` ("rode o /cor
  antes"; `--sem-cor` força). O `/sonorizar` lê o vídeo do `/inserir`.
- Correção de corte depois da cor: o `entregar.py` do `/decupar` percebe e chama o `aplicar.py --aplicar`, que
  atualiza o `2-cor.mp4`.
- A receita padrão é correção, não filtro: `corrigir` (luz e branco medidos) + contraste 8, sombra −4, saturação 5,
  sem tom quente. "Mais quente", "mais claro" etc. mudam um número do `cor-proposta.json` (tabela no SKILL).

## Saudação e recado da oferta

- **Saudação**: regra no `CLAUDE.md`. No primeiro uso de qualquer skill o Claude cumprimenta e grava
  `.imersao/saudacao-feita.txt`. É por instrução (não há script antes de o `uv` existir).
- **Recado**: `.imersao/oferta.md` nasce **vazio**. Quando o `/sonorizar` entrega o `4-final.mp4`, o
  `sonorizar/scripts/entregar.py` imprime o texto desse arquivo num bloco `RECADO DA IMERSÃO` (e grava
  `.imersao/oferta-mostrada.txt`); o Claude repassa. Vazio = não imprime nada. Uma vez por pasta.
- **Para ligar**: escreva o texto final em `.imersao/oferta.md` (texto puro, como o aluno deve ler) e rode o
  empacotador. Ele avisa "Recado da oferta: LIGADO". Quem já baixou a pasta sem o texto pode receber só esse
  arquivo e pôr em `.imersao/`.

## Ativos e licenças

- **Fontes** (`marca/fontes/`): Be Vietnam Pro Bold, ExtraBold e Medium (texto) e Instrument Serif Italic e
  Regular (destaque), do repositório oficial `google/fonts`, SIL OFL 1.1, com o `OFL-*.txt` de cada uma. Trocam a
  Neue Montreal e a Apple Garamond da Ana, que não podem ser repassadas. O `marca/estilo.md` foi escrito para elas.
- **Sons** (`marca/sons/`, 14 MB): 3 trilhas e 14 efeitos, **todos CC0 1.0**, com origem e licença por arquivo em
  `marca/sons/creditos.md` (o nome é minúsculo porque é o que o `sonorizar.py` lê). Trilhas: "Catchy Swing" (Doge,
  OpenGameArt), "Game Travel 1 (Piano)" e "Make Funk" (HoliznaCC0, Free Music Archive). Efeitos: 8 do `banco/`
  (Freesound, CC0 reconferido na página em 13/11) e 6 de Kenney e Freesound. Nada de Epidemic, pack de terceiros
  ou rip. **Ninguém ouviu as trilhas**: foram escolhidas por medida e pelas etiquetas da página. Ouça as três antes
  da aula; para tirar uma, apague o arquivo e a linha dela no `creditos.md`.
- **Cor**: `marca/cores/cor.json` (números, nosso).
- **Assinatura** no `GUIA.html`: `principal-azul.svg` do sistema visual. As fontes da marca (Manrope, Source Serif
  4) não vão embutidas no guia: ele cai em Arial e Georgia.
- O estilo foi medido nos Reels da Ana e cita o nome dela uma vez (`marca/estilo.md`). Nenhum bruto, chave ou
  nome de cliente na pasta (o empacotador confere chave e vídeo solto).

## Empacotar e atualizar

```
ferramentas/empacotar.sh [pasta de destino]      # gera edicao-imersao.zip com a pasta edicao-imersao/ dentro
```

- Refaz o `GUIA.html` a partir do `GUIA.md` (`uv run ferramentas/gerar-guia.py`). O `GUIA.md` é a cópia de
  `producao/2026-11-14-imersao-kit-video/guia-do-aluno.md`: mudou lá, copie para cá e empacote.
- **Exemplo (plano B)**: ponha o seu bruto em `videos/exemplo/brutos/` e os quatro vídeos em
  `videos/exemplo/sequencia/`. O Git ignora (mídia pesada fica fora), o empacotador leva. O `/decupar` sem
  argumento ignora a pasta `exemplo`.
- O `.gitignore` deixa fora do Git tudo o que o aluno põe e o que as skills gravam.

## Permissões

`.claude/settings.json` libera sem perguntar: editar arquivos da pasta (`acceptEdits`), `uv run
.claude/skills/...` e as checagens de versão, para a ferramenta Bash e para a PowerShell (que é o shell do Claude
Code no Windows). As regras **só valem depois que o aluno aceita "confiar na pasta"** ao abrir. Sobram esse clique
e o de instalar (`brew install` / `winget install`).

Medido aqui com `claude -p`: a regra `Bash(uv run .claude/skills/*)` libera os scripts das skills (com argumento
entre aspas também) e segura `uv run` de qualquer outra coisa. **Não contado**: quantos botões aparecem num app
recém-instalado, e se as regras `PowerShell(...)` casam no Windows. Se preferir o aluno aprovando tudo, apague o
arquivo.

## Na sua máquina

`~/.claude/skills/decupar`, `inserir` e `sonorizar` (a linha privada) têm o mesmo nome das skills desta pasta, e a
skill pessoal ganha da skill do projeto. Para demonstrar o que o aluno tem, abra a pasta num usuário do Mac sem
essas skills, ou tire os três links de `~/.claude/skills/` durante a aula. O `/cor` só existe aqui.

## Testes (13/11/2026, MacBook com chip M4, ffmpeg 9.0.1, uv 0.12.5, Node 22.23.3)

Tudo em diretório temporário, a partir do `.zip` descompactado; nenhum bruto ou resultado ficou no repositório.

| O que | Vídeo | Resultado | Tempo |
|---|---|---|---|
| Decupagem sem cor (scripts) | 27 s de um bruto falado (C2529, recortado em pé) → 13 s | passou | transcrever 9 s · `1-decupado.mp4` 3 s |
| Cor (scripts) | o mesmo | passou, "com cor" conferido | folha 3 s · `2-cor.mp4` 11 a 13 s |
| HyperFrames 0.9.26 nesta máquina | sonda: um cartão sobre 26 s de vídeo | passou (`check`, `snapshot`, `render`) | render 19 a 28 s |
| Inserções completas (gancho, balão, etapas, legenda) | 13 s | passou | storyboard 9 s · vídeo 80 s |
| Som com os sons da pasta | 13 s | passou: −14,0 LUFS, trilha 26 a 30 abaixo da voz | 2 s |
| Recado da oferta | — | vazio não imprime; com texto imprime uma vez | — |
| **Ensaio do fluxo inteiro por um agente novo**, lendo só o `CLAUDE.md` e os `SKILL.md`, com os pedidos do roteiro | 31 s com o texto do roteiro (voz sintética do Mac, uma frase repetida de propósito) → 20 s | os quatro arquivos saíram; a frase repetida foi cortada; 14 pontos de instrução ruim anotados e corrigidos em seguida | decupar 44 s · cor 38 s · inserir 139 s (100 s de animação) · som 10 s: **3 min 50 s de máquina** |
| O mesmo fluxo, pelos scripts, numa pasta com espaço e acento no caminho (`João Silva/Vídeos/`) | 31 s → 20 s | passou | transcrever 37 s · corte 4 s · cor 2 + 14 s · storyboard 11 s · **animação 52 s** · som 4 s |

A reunião estimou de 20 a 40 min para as inserções. Aqui, com o modelo pronto, a animação de um vídeo de 20 s levou
de 52 a 100 s. Em máquina mais fraca conte com 2 a 10 min.

O ensaio corrigiu: a receita de "sobrou uma pausa" (dividir o trecho sozinha piorava; agora divide e aperta as bordas
com `ajustes`), os ids `F<n>` do exemplo do `/inserir`, `legenda.apagar` para palavra que o Whisper inventa, o passo
de "mais quente" (0,2 era invisível; agora 0,4), a legenda que piscava 0,4 s antes de uma peça e a palavra sozinha
no fim da frase.

**Rosto coberto (corrigido depois do ensaio).** A primeira versão punha as peças por uma altura medida à mão
(`cabeca_y`) e, no enquadramento fechado, o gancho e o balão caíam em cima dos olhos. Agora o script mede o rosto e
decide (ver "Entrou"). Conferido nos dois enquadramentos, quadro a quadro, com a zona do rosto desenhada por cima
(`--storyboard --ver-rosto`):

| Enquadramento | O que o script fez | Animação |
|---|---|---|
| Fechado (rosto de y 100 a 1050, sem espaço em cima) | afastou o vídeo para 74 % no gancho e no balão e para 68 % nas etapas; legenda desceu para baixo do queixo | 70 s para 13 s de vídeo |
| Aberto (um palmo acima da cabeça) | gancho e balão em cima da cabeça, sem mexer no vídeo; etapas com o vídeo a 90 % | 73 s para 20 s de vídeo |

Os dois tempos foram medidos com a máquina muito ocupada por outros trabalhos (carga acima de 40); sem carga a mesma
animação levava de 52 a 80 s. A trava foi testada forçando o gancho em cima do rosto (`"y": 700`): o storyboard saiu
com o contorno vermelho e o `--video` recusou com código 2. O detector acha rosto de frente e de perfil; **não foi
testado** com óculos escuros, boné, duas pessoas no quadro ou rosto muito pequeno. Sem rosto achado, o script pede
`"rosto": [x, y, largura, altura]` no plano.

### Não testado

- **Windows**: nada rodou num Windows. Ver a lista abaixo.
- **Mac limpo, sem Homebrew**: o `/decupar` manda a pessoa instalar o Homebrew pelo Terminal (pede a senha do Mac e
  baixa as ferramentas da Apple). É o ponto mais frágil do Mac. Vale mostrar isso no bloco das 9h50.
- **Conta de 20 dólares, numa conversa de verdade no app**: o ensaio foi com um agente lendo as instruções, não com
  o aluno digitando `/decupar` no Claude Desktop. Consumo do plano e número real de botões de permissão: não medidos.
- **Primeiro download real** (Whisper 1,6 GB + HyperFrames e navegador uns 500 MB + bibliotecas): aqui estava tudo em
  cache. Com 40 pessoas baixando no mesmo minuto, o tempo é desconhecido.
- **Vídeo de iPhone de verdade** (HDR, 4K, 60 quadros, taxa variável) e vídeo gravado deitado: o teste usou H.264
  1080×1920 a 30 quadros.
- **As trilhas ninguém ouviu.** O desenho das peças (placa, balão, painel das etapas) ninguém aprovou: é de hoje.
- Correção de cor num vídeo escuro ou com luz amarela de casa; `preparar.py` numa máquina sem nada em cache.

### Riscos no Windows (revisão por leitura do código)

Travam o aluno:
1. **PATH depois do `winget`**: se o Claude ficar na bandeja, os programas novos não aparecem. O SKILL e o guia já
   mandam sair pelo ícone ao lado do relógio; em último caso, reiniciar.
2. **Vídeo aberto no player**: o Windows não deixa trocar um arquivo aberto. Tratado: o script grava
   `<n>-<nome>-novo.mp4` ao lado e avisa.
3. **Usuário com acento** (`C:\Users\João`): o Whisper do Windows (faster-whisper/CTranslate2) pode não abrir o
   modelo. Se aparecer "Unable to open file 'model.bin'": definir `HF_HOME=C:\hf` e abrir o Claude de novo.
4. **"DLL load failed"** no Whisper: falta o Visual C++ Redistributable
   (`winget install -e --id Microsoft.VCRedist.2015+.x64`). Windows em ARM (Snapdragon): o Whisper pode não instalar.
5. **HyperFrames** com espaço e acento no caminho, o aviso do Firewall para o Node e o antivírus no navegador dele:
   nunca rodou num Windows. Plano B do SKILL: seguir para o `/sonorizar` com o `2-cor.mp4`.
6. **Vídeo deitado + acento no caminho**: o `enquadrar.py` (OpenCV) não abre caminho com acento no Windows. O
   `rosto.py` do `/inserir` foi escrito para não depender disso (quadros por cano do ffmpeg, detector lido da
   memória), mas não rodou num Windows. A conferência do rosto abre o navegador do HyperFrames direto
   (`--dump-dom`); se ela não rodar, o script avisa e a página deixa de fora do vídeo a peça que tocaria o rosto.
7. **Mover a pasta depois do passo 1**: a decupagem guarda o caminho inteiro do bruto. Mover (por exemplo, tirar do
   OneDrive) pede apagar `sequencia/decupagem` e decupar de novo.

Pioram ou assustam:
8. Tempo com vírgula sem aspas no PowerShell (`--ouvir 00:08,2`) parte em dois: o SKILL agora manda aspas.
9. Janelas pretas piscando durante a cópia leve de vídeo acima de 1080 (`transcrever.py`, `DETACHED_PROCESS`).
10. Os limites de tempo dos comandos do HyperFrames não matam os processos filhos no Windows.
11. `-hwaccel auto` com HEVC de 10 bits pode corromper a imagem em placa antiga.
12. OneDrive e arquivo "só na nuvem": o guia manda deixar a pasta em Vídeos, fora do OneDrive.

O que a leitura deu como certo: nada de `open`, `/tmp` ou `shell=True` fora do ramo do Mac; nenhum caminho dentro de
filtro do ffmpeg; todo texto lido e gravado em UTF-8; `libx264` no lugar do videotoolbox; `npx.cmd` chamado com
lista de argumentos; a árvore de pastas soma até uns 180 caracteres.

## Diferenças em relação ao `roteiro-da-aula.md` (seção 3)

| No roteiro | Na pasta |
|---|---|
| `guia` | `GUIA.html` (dois cliques) e `GUIA.md` (o mesmo texto; é a fonte) |
| `roteiro` | `roteiro.txt` |
| — | `COMECE-AQUI.txt`, e as pastas ocultas `.claude/` e `.imersao/` |
| `sequencia/` começa vazia | começa com um `LEIA-ME.txt`; durante a edição ganha `decupagem/`, `insercoes/`, `som/` e `creditos.md` |
| `videos/exemplo/` com o bruto e cada etapa | só um `LEIA-ME.txt`, até você gravar |
| "Pode instalar." sempre | só é pedido se faltar programa ou download; com tudo no lugar o `/decupar` vai direto para a lista de cortes |
| "Não feche o Claude enquanto baixa" | no Windows, depois do `winget`, **precisa** sair do Claude e abrir de novo (acrescentei ao `GUIA.md`) |
| `Na inserção [2] …` "refaz só aquela imagem" | refaz a folha inteira do storyboard (10 a 20 s) |
| `Deixa um pouco mais claro.` | sobe as sombras (`sombra` +6); a receita não tem exposição solta |
| J-cut | a skill não faz (o corte tira imagem e som no mesmo ponto): fica só como explicação |
| vídeo aberto no player (Windows) | o arquivo novo pode sair como `3-insercoes-novo.mp4` |

Os nomes dos quatro vídeos, das pastas `marca/{fontes,cores,sons}` e `videos/meu-primeiro-video/{brutos,sequencia}`
e o texto dos pedidos são os do roteiro.

## Depende de você

1. Ouvir as três trilhas (`marca/sons/trilhas/`) e olhar um vídeo feito com o modelo das inserções.
2. Gravar o roteiro, editar pelos quatro comandos e pôr o resultado em `videos/exemplo/` (plano B). Empacotar de novo.
3. Rodar a pasta num Mac sem Homebrew e num Windows antes das 9h30, ou combinar quem socorre quem travar.
4. O texto de `.imersao/oferta.md`, quando a oferta fechar com o Gabriel.
5. Para a demonstração: tirar do caminho as suas skills `decupar`, `inserir` e `sonorizar` de `~/.claude/skills/`.
6. Levar para o kit o conserto do `cor.py` (`pl=1`).
