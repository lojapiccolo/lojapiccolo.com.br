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


# ---------- página do brechó (raiz) ----------
def brecho():
    import html
    B = (R / 'brecho_template.html').read_text(encoding='utf-8')
    vit = json.load(open(R / 'vitrine.json', encoding='utf-8'))
    dep = json.load(open(R / 'depoimentos.json', encoding='utf-8'))
    e = html.escape
    def preco(v):
        s = f'{v:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.'); i, c = s.split(',')
        return f'<span class="preco">R$ {i}<sup>,{c}</sup></span>'
    def zap(p):
        t = f"Oi! Vi no site a peça {p['peca']} ({p['marca']}, tam. {p['tamanho']}) e tenho interesse. Ainda está disponível?"
        from urllib.parse import quote
        return f'https://wa.me/5524992170426?text={quote(t)}'
    if vit:
        exemplo = any(p.get('exemplo') for p in vit)
        cards = ''.join(f'''<article class="peca" data-para="{e(p['para'])}"><div class="ft"><img src="{p['foto']}" alt="{e(p['peca'])}, {e(p['marca'])}" loading="lazy"></div><span class="tag">{e(p.get('estado') or 'Peça única')}</span>
<div class="txt"><h3>{e(p['peca'])}</h3><div class="meta">{e(p['marca'])} · tam. {e(str(p['tamanho']))} · {e(p['para'])}</div>
<div class="linha">{preco(p['preco'])}<a class="btn zap" href="{zap(p)}" target="_blank" rel="noopener">Quero esta</a></div></div></article>''' for p in vit)
        aviso = '<span class="aviso-proto">Fotos de exemplo · as peças reais entram pela base "Vitrine do brechó" no Notion</span>' if exemplo else ''
        filtro = ('<div class="filtro" role="group" aria-label="Filtrar vitrine"><button type="button" data-f="" aria-pressed="true">Todas</button>'
                  '<button type="button" data-f="Menina" aria-pressed="false">Meninas</button><button type="button" data-f="Menino" aria-pressed="false">Meninos</button></div>')
        js = ('<script>document.querySelectorAll(".filtro button").forEach(b=>b.onclick=()=>{const f=b.dataset.f;'
              'document.querySelectorAll(".filtro button").forEach(x=>x.setAttribute("aria-pressed",x===b));'
              'document.querySelectorAll(".grade .peca").forEach(c=>c.hidden=!!f&&c.dataset.para!==f&&c.dataset.para!=="Unissex")})</script>')
        vitrine = f'{aviso}{filtro}<div class="grade">{cards}</div>{js}<p style="margin-top:22px;color:var(--ameixa2);font-size:15px">Não achou o tamanho? <a href="#lista" style="font-weight:800;color:var(--salvia-esc)">Entre na lista</a> e a gente te mostra o que tem.</p>'
    else:
        vitrine = '<div class="vazio-vitrine"><h3 style="font-size:24px">Esta semana as novidades foram direto para quem está na lista.</h3><p>As peças mais disputadas nem chegam a aparecer aqui. Entre na Lista do Piccolo e receba primeiro, no tamanho do seu filho.</p><a class="btn" href="#lista">Entrar na Lista do Piccolo</a></div>'
    if dep:
        depo = '<div class="depo">' + ''.join(f'<figure><span class="aspas">“</span><blockquote>{e(d["texto"])}</blockquote><figcaption>{e(d["quem"])}</figcaption></figure>' for d in dep) + '</div>'
    else:
        depo = ('<span class="aviso-proto">Aguardando os depoimentos reais (destaque "feedbacks" do Instagram)</span>'
                '<div class="depo placeholder">' + ''.join('<figure><span class="aspas">“</span><blockquote>Depoimento de uma cliente, transcrito do Instagram.</blockquote><figcaption>Nome · cidade</figcaption></figure>' for _ in range(3)) + '</div>')
    mos = vit[3:7] if len(vit) >= 7 else vit[:4]
    mosaico = ''.join(f'<div class="pol"><div class="ft"><img src="{p["foto"]}" alt=""></div><small>{e(p["marca"])} · tam. {e(str(p["tamanho"]))}</small></div>' for p in mos)
    porta = ''.join(f'<span><img src="{p["foto"]}" alt=""></span>' for p in (vit[:1] + vit[2:3] + vit[1:2]))
    out = B.replace('<!--__PORTA__-->', porta).replace('<!--__VITRINE__-->', vitrine).replace('<!--__DEPOIMENTOS__-->', depo).replace('<!--__MOSAICO__-->', mosaico)
    (R.parent / 'index.html').write_text(out, encoding='utf-8')
    print('index.html (brechó) gerado:', len(out) // 1024, 'KB')


brecho()
