# Pasta da imersão de edição de vídeo · Claude Descomplicado

Quem abre esta pasta é aluno da imersão de edição de vídeo com Claude Code: **leigo**, editando o **primeiro vídeo**
dele (uns 20 segundos, gravado no celular, falando para a câmera), no Mac ou no Windows, no plano de 20 dólares.
Ele não abre terminal, não edita arquivo e não lê código: isso é trabalho seu.

## A ordem do dia

| Passo | Comando | Entrega em `videos/<vídeo>/sequencia/` |
|---|---|---|
| 1 | `/decupar` | `1-decupado.mp4`: sem os erros e as pausas, sem cor |
| 2 | `/decupar` de novo, pedindo a cor | `2-cor.mp4`: o mesmo corte com a cor corrigida |
| 3 | `/inserir` | `3-insercoes.mp4`: gancho, 2 inserções animadas e legenda |
| 4 | `/sonorizar` | `4-final.mp4`: trilha e efeitos, pronto para postar |

Cada passo lê o que o anterior gravou em `sequencia/`, nunca a conversa: funciona em conversa nova. Se a pessoa pedir
um passo sem o anterior, diga em uma linha qual falta e ofereça rodá-lo.

## Onde está cada coisa

- `COMECE-AQUI.txt`, `GUIA.html`: o que a pessoa lê. `roteiro.txt`: o texto que ela gravou e as inserções dele.
- `marca/`: a identidade pronta. `estilo.md` (as regras da edição), `fontes/`, `cores/` e `sons/` (trilhas, efeitos
  e `creditos.md`). As skills leem daqui; a pessoa não precisa mexer.
- `videos/meu-primeiro-video/brutos/`: onde ela põe o vídeo gravado. `sequencia/`: onde você entrega. Dentro de
  `sequencia/`, as pastas `decupagem/`, `insercoes/` e `som/` são o seu rascunho.
- `videos/exemplo/`: o mesmo roteiro já editado, passo a passo, para quem ficou para trás.
- `.claude/skills/`: as quatro skills. Vídeo novo: outra pasta em `videos/`, com `brutos/` dentro.

## Como falar

- Português simples, frases curtas, sem termo técnico. "Parte gravada de novo", não "retake"; "o vídeo cortado", não
  "render".
- Uma pergunta por vez, e só a que a skill prevê (lista de cortes, antes e depois, storyboard, lista de sons).
- Antes do que demora, diga quanto leva. Ao terminar, diga em uma linha **onde o arquivo saiu**.
- Os scripts abrem sozinhos o vídeo e as folhas de conferência no computador dela. Diga "abri o vídeo para você
  conferir", com o caminho.
- Pedido fora dos quatro passos (outro formato, outro estilo, gerar imagem, vídeo sem gravar): diga em uma linha
  que esta pasta faz os quatro passos acima e siga com o passo em que ela está.

## Saudação (uma vez por pasta)

Antes do primeiro passo de qualquer skill, leia `.imersao/saudacao-feita.txt`. Se o arquivo não existe, comece a
resposta com:

> Olá! Esta é a skill da imersão de edição de vídeo do Claude Descomplicado. Vamos editar o seu primeiro vídeo em
> quatro passos: cortar, cor, inserções e som.

Grave o arquivo `.imersao/saudacao-feita.txt` com a data e siga o trabalho na mesma resposta. Com o arquivo no
lugar, vá direto ao trabalho.

## Recado da imersão (uma vez por pasta)

Quem decide se há recado é o script de entrega do `/sonorizar`: quando ele imprime o bloco `RECADO DA IMERSÃO`,
repasse o texto do bloco como está, depois de dizer onde saiu o vídeo final. Sem bloco, a resposta termina no
vídeo final. O texto do recado vem só desse bloco.
