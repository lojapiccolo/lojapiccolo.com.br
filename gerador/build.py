"""Gera play/index.html a partir de gerador/template.html + produtos.json + icons.json.
Uso: python3 gerador/build.py   (rodar na raiz do repositório)
Próxima etapa: produtos.json passa a ser lido do Notion (base Produtos do Catálogo)."""
import json, re, pathlib
R = pathlib.Path(__file__).parent
T = (R / 'template.html').read_text(encoding='utf-8')
prods = json.load(open(R / 'produtos.json', encoding='utf-8'))
ic = json.load(open(R / 'icons.json', encoding='utf-8'))
T = T.replace('/*__DATA__*/', 'const PRODUTOS=' + json.dumps(prods, ensure_ascii=False) + ';\nconst IC=' + json.dumps(ic['IC'], ensure_ascii=False) + ';\nconst MAPA=' + json.dumps(ic['MAPA'], ensure_ascii=False) + ';')
T = re.sub(r'<div class="proto">.*?</div>\n', '', T, count=1)
HEAD = '''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="description" content="Piccolo Play: brinquedos impressos em 3D, sob encomenda, em Petrópolis. Para montar, encaixar, equilibrar e inventar o que acontece depois.">
<meta property="og:title" content="Piccolo Play">
<meta property="og:description" content="Brinquedos impressos em 3D, sob encomenda, para a criança brincar de verdade.">
<meta property="og:image" content="https://lojapiccolo.com.br/play/img/cena_015.webp">
<meta property="og:url" content="https://lojapiccolo.com.br/play/">
<meta name="theme-color" content="#FAF5EE">
<link rel="icon" href="img/icone.png" type="image/png">
<link rel="apple-touch-icon" href="img/icone.png">
'''
T = T.replace('<title>Piccolo Play</title>', '<title>Piccolo Play · Brinquedos para brincar de verdade</title>', 1)
m = re.search(r'<style>.*?</style>\n', T, re.S); st = m.group(0); T = T.replace(st, '', 1)
i = T.index('<header'); head_part, body = T[:i], T[i:]
out = HEAD + head_part + st + '</head>\n<body>\n' + body.rstrip() + '\n</body>\n</html>\n'
(R.parent / 'play' / 'index.html').write_text(out, encoding='utf-8')
print('play/index.html gerado:', len(out) // 1024, 'KB')
