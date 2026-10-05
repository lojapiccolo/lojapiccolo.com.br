# lojapiccolo.com.br

Site do Piccolo (brechó infantil, Petrópolis/RJ) e da linha de brinquedos Piccolo Play.

- `index.html` — página inicial do domínio
- `play/` — site do Piccolo Play (gerado, não editar à mão)
- `gerador/` — modelo e dados que geram `play/index.html` (`python3 gerador/build.py`)

Fonte de verdade dos produtos: Notion → base "Produtos do Catálogo". Hospedagem: Netlify, publicando a raiz deste repositório.

## Atualização automática

Todo dia às 5h (ou pelo botão **Actions › Atualizar site a partir do Notion › Run workflow**) o GitHub:
1. lê a base "Produtos do Catálogo" no Notion (`gerador/notion_sync.py`), só os produtos com **Publicar** marcado;
2. gera `play/index.html` (`gerador/build.py`);
3. envia a mudança; o Netlify publica em seguida.

Precisa do segredo `NOTION_TOKEN` (Settings › Secrets and variables › Actions) e da base compartilhada com a integração no Notion.

Imagens não vêm do Notion: ficam em `play/img/` com o SKU no nome (`cena_015.webp`, `cut_015.webp`, `ficha_015.webp`). Produto novo precisa das três imagens antes de aparecer bem no site.

## Página do brechó (raiz)

`gerador/brecho_template.html` + `gerador/vitrine.json` (peças em "Chegou esta semana") + `gerador/depoimentos.json` → `index.html`.
- Vitrine: vem da base Notion **Vitrine do brechó (site)** (Publicar marcado e Vendida desmarcado); as fotos são baixadas para `img/brecho/`.
- Lista do Piccolo: o formulário chama `netlify/functions/lista.js`, que grava uma linha por criança na base Notion **Lista do Piccolo (site)**. Precisa da variável `NOTION_LISTA_TOKEN` no Netlify (integração com permissão de inserir, compartilhada só com essa base).
