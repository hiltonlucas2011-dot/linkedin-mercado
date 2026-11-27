# Agente do LinkedIn pessoal do Hilton: varejo e consumo

Este repositório é o agente que prepara **1 post por semana** para o **LinkedIn pessoal do Hilton Lucas** com dados de varejo e consumo e uma leitura prática.
É um projeto separado da Eprint: **não use a marca, as cores nem o nome da Eprint** aqui.
Nada é publicado sem a aprovação do Hilton na página de aprovação.

## Fluxo

```
quinta 19h  ──►  PREPARAR: notícia + texto + foto (IA)  ──►  página de aprovação
                                                                │  Hilton aprova / edita / pede ajuste / descarta
sexta 9h, 11h, 14h ──►  PUBLICAR: aprovado → Buffer (sexta 11h30, ou 17h se aprovado depois das 11h)
                                   ajuste   → refaz e volta para aprovação
```

- Configuração: `config.json` (canal do Buffer, agenda, imagem, URLs).
- Fontes confiáveis: `conteudo/fontes.md`. Histórico: `conteudo/historico.md` (não repetir tema ou fonte em menos de 6 semanas).

## Rotina PREPARAR (quinta à noite)

1. **Ache o dado da semana.** Busque na web (WebSearch) pesquisas ou índices de **varejo e consumo no Brasil** publicados nos **últimos 30 dias**, nas fontes de `conteudo/fontes.md`. Escolha **um** dado que gere uma leitura prática para lojas e pontos de venda. Abra a fonte original e confira cada número. Se não conseguir confirmar um número na fonte, não use.
2. **Escreva o post** (`texto`), em português, **sem emoji**, nesta estrutura:
   1. **Gancho em uma linha** com a conclusão do dado.
   2. **Os dados**: números, quem fez a pesquisa e como foi feita (amostra, período, método). Comparação com período anterior, se houver.
   3. **Aspas de um especialista** só se estiverem na fonte, com nome e cargo exatos.
   4. **"Daqui para baixo é a minha leitura, não os dados:"** ou **"Minha leitura:"**: a opinião do Hilton, como empresário que está no dia a dia do comércio. Primeira pessoa do singular.
   5. **"Na prática:"** uma recomendação concreta para o lojista. Quando fizer sentido, puxe **de leve** para comunicação visual: vitrine, gôndola, balcão, sinalização, ponto de venda. Nunca cite a Eprint, produtos específicos ou preços.
   6. **Fechamento** de uma ou duas linhas que retoma o número do começo.
   7. `Fonte nos comentários.`
   8. **2 hashtags**, por exemplo `#varejo #visualmerchandising` ou `#varejo #consumo`.
   Tamanho: 1.100 a 1.600 caracteres. Parágrafos curtos, linha em branco entre eles.
3. **Comentário da fonte** (`primeiro_comentario`): `Fonte: <nome da pesquisa/instituição>, <data de publicação>. <link da fonte original>`.
4. **Foto** (`prompt_imagem`): descreva em português uma **cena realista** que mostre a situação do post (ex.: cliente olhando o celular diante de uma prateleira; vitrine de loja de rua num fim de tarde). Seja específico: lugar, luz, enquadramento, objetos. Nada de texto, números, logotipos ou marcas na imagem; pessoas sem rosto identificável. Rode `python3 scripts/gerar_imagem.py posts/<id>/post.json` e **abra o PNG** para conferir: mãos e objetos sem deformação, nenhuma letra ou marca aparecendo, cena coerente com o texto. Se ficar ruim, ajuste o prompt e gere de novo (no máximo 3 tentativas).
5. Crie `posts/AAAA-MM-DD-<slug>/post.json` com: `id`, `data_publicacao` (sexta 11:30, `-03:00`), `tema`, `fonte_nome`, `fonte_url`, `fonte_data`, `texto`, `primeiro_comentario`, `prompt_imagem`, `alt`.
6. Commit e push (`git -c push.negotiate=true push origin main`). A imagem fica pública em `config.imagens.url_base + posts/<id>/post.png`.
7. Suba o PNG como asset na página de aprovação (ferramenta Artifact, `url` = `config.aprovacao.pagina_url`, `asset: true`) e grave o documento na coleção `posts` com ArtifactData:
   `{id, data_publicacao, tema, preview_url, imagem_url, alt, texto, primeiro_comentario, fonte_nome, fonte_url, status: "pendente", feedback: "", versao: 1, criado_em}`.
8. Termine com um resumo curto: o dado escolhido, a fonte e o link da página de aprovação.

## Rotina PUBLICAR (sexta, 9h, 11h e 14h)

1. Leia a coleção `posts` da página de aprovação.
2. `status: "aprovado"` → crie o post no Buffer (`create_post`):
   - `channelId` = `config.buffer.canal_linkedin_pessoal`, `schedulingType: "automatic"`, `mode: "customScheduled"`
   - `dueAt`: sexta 11:30 (`-03:00`); se já passou, sexta 17:00; se também já passou, a próxima segunda 08:30.
   - `text` = `texto` (use o texto salvo no documento: o Hilton pode ter editado)
   - `assets[0].image.url` = `imagem_url`, com `metadata.altText` = `alt`
   - `metadata.linkedin.firstComment` = `primeiro_comentario`
   - Depois: `update` no documento com `status: "agendado"`, `buffer_id`, `agendado_para`. Acrescente uma linha em `conteudo/historico.md`, commit e push.
3. `status: "ajuste"` → refaça seguindo o `feedback` (texto, foto ou os dois), suba a nova foto, volte para `status: "pendente"` com `versao` + 1 e `feedback` limpo.
4. `pendente`, `reprovado` ou `agendado` → nada a fazer.
5. Se as ferramentas do Buffer não estiverem disponíveis, não marque nada como agendado: termine avisando.

## Regras que não mudam

- **Nunca publique sem `status: "aprovado"`.** Nunca use `shareNow`.
- **Nunca recomende comprar ou vender investimentos** (ações, fundos, moedas). O assunto é varejo e consumo.
- Só números conferidos na fonte original. Não invente pesquisas, porcentagens, especialistas ou aspas.
- Não cite a Eprint nem faça propaganda. Não cite concorrentes.
- Commits com autor `hiltonlucas2011-dot` e e-mail `hiltonlucas2011-dot@users.noreply.github.com`.
- O Buffer gratuito permite 10 posts agendados ao mesmo tempo, somando este projeto e a Eprint. Se o limite estiver cheio, avise o Hilton em vez de apagar posts.
