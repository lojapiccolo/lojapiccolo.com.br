"""Lê a base "Produtos do Catálogo" do Notion e grava gerador/produtos.json.

Uso:
  NOTION_TOKEN=... python3 gerador/notion_sync.py          # lê do Notion
  python3 gerador/notion_sync.py --de exportado.json       # testa com um JSON já baixado

Regras:
- Só entram produtos com "Publicar" marcado.
- Preço e idade vêm do rollup do cadastro interno (fonte única).
- Cores: se "Variações" diz que o cliente escolhe, as cores são lidas do texto "Cores";
  senão usa gerador/extras.json (cores_fixas), que descreve a composição fixa.
- Nome em duas linhas (ex.: "Ganso" / "Sobre Rodas") vem de extras.json; produto novo
  sem entrada lá usa a primeira palavra + o resto.
- Imagens não vêm do Notion: ficam em play/img/ com o SKU no nome (cena_015.webp etc.).
"""
import json, os, re, sys, pathlib, urllib.request

R = pathlib.Path(__file__).parent
DS = '43cee971-e821-44f5-bf2c-40c16d6d4bb4'   # data source "Produtos do Catálogo"
API = 'https://api.notion.com/v1'
HEX = {'Azul': '#9CC3D6', 'Rosa': '#EDB3C0', 'Amarelo': '#F0D27A', 'Laranja': '#EE9E6C', 'Branco': '#FFFFFF',
       'Preto': '#403A3C', 'Verde': '#A9BF8E', 'Roxo': '#B7A3CF', 'Vermelho': '#D9574D', 'Lilás': '#C9B8DC',
       'Bege': '#DCC29C', 'Cinza': '#B9B9B9', 'Madeira': '#E3CFAE'}


def notion(path, body=None, token=None):
    req = urllib.request.Request(API + path, data=json.dumps(body).encode() if body is not None else None,
                                 headers={'Authorization': f'Bearer {token}', 'Notion-Version': '2025-09-03',
                                          'Content-Type': 'application/json'}, method='POST' if body is not None else 'GET')
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def baixar(token):
    rows, cursor = [], None
    while True:
        body = {'page_size': 100, 'filter': {'property': 'Publicar', 'checkbox': {'equals': True}}}
        if cursor: body['start_cursor'] = cursor
        r = notion(f'/data_sources/{DS}/query', body, token)
        rows += r['results']
        if not r.get('has_more'): return rows
        cursor = r['next_cursor']


def texto(p):
    t = p.get('type')
    if t in ('rich_text', 'title'): return ''.join(x['plain_text'] for x in p[t]).strip()
    if t == 'select': return (p['select'] or {}).get('name', '')
    if t == 'number': return p['number']
    if t == 'checkbox': return p['checkbox']
    if t == 'rollup':
        r = p['rollup']
        if r['type'] == 'number': return r['number']
        if r['type'] == 'array': return [texto(x) for x in r['array']]
    return ''


def idade_bonita(s):
    s = (s or '').replace('–', ' a ').replace('-', ' a ').replace('(com adulto)', ', com adulto').replace(' ,', ',')
    return re.sub(r'\s+', ' ', s).strip()


def preco_br(v):
    return f'{v:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.') if isinstance(v, (int, float)) else ''


def cores_do_texto(s):
    achadas = []
    for nome in HEX:
        m = re.search(r'\b' + nome.lower() + r'\b', s.lower())
        if m: achadas.append((m.start(), nome))
    return [{'n': n, 'hex': HEX[n]} for _, n in sorted(achadas)]


def converter(rows, extras):
    out = []
    for r in rows:
        p = {k: texto(v) for k, v in r['properties'].items()}
        sku = (p.get('SKU') or '').replace('PIC-PLAY-', '')
        if not sku: continue
        nome1, nome2 = extras['nomes'].get(sku) or (p['Produto'].split(' ', 1) + [''])[:2]
        var = (p.get('Variações') or '').lower(); ctexto = p.get('Cores') or ''
        lidas = cores_do_texto(ctexto)
        escolha = 'sem personalização' not in ctexto.lower() and 'fixa' not in var and len(lidas) >= 2
        if escolha:
            cores = [c for c in lidas if not (sku == '007' and c['n'] == 'Preto')]
            nota = 'Base sempre preta · escolha 1 cor' if sku == '007' else 'Escolha 1 cor'
            if 'tamanhos p e g' in var: nota += ' · tamanho P é mais fácil para os menores'
        else:
            fx = extras['cores_fixas'].get(sku, {'cores': [], 'nota': 'Composição fixa de cores'})
            cores, nota = fx['cores'], fx['nota']
        idades = p.get('Idade recomendada') or []
        bens = [b.strip() for b in re.split(r'\n|<br>', p.get('Benefícios') or '') if b.strip()][:4]
        out.append(dict(
            sku=sku, nome=nome1, nome2=nome2, familia=p.get('Família') or 'Outros', ordem=p.get('Ordem') or 999,
            idade=idade_bonita(idades[0] if idades else ''), preco=preco_br(p.get('Preço')),
            desc=p.get('Descrição curta') or '', beneficios=bens,
            dim=(p.get('Dimensões aproximadas') or '').rstrip('.'), mat=(p.get('Material') or 'PLA'),
            cont=(p.get('Conteúdo') or '').rstrip('.'), cores=cores, escolha=escolha, nota=nota,
            galeria=extras['galeria'].get(sku, [])))
    out.sort(key=lambda x: (x['ordem'], x['sku']))
    return out


if __name__ == '__main__':
    extras = json.load(open(R / 'extras.json', encoding='utf-8'))
    if '--de' in sys.argv:
        rows = json.load(open(sys.argv[sys.argv.index('--de') + 1], encoding='utf-8'))
    else:
        token = os.environ.get('NOTION_TOKEN')
        if not token: sys.exit('Defina NOTION_TOKEN.')
        rows = baixar(token)
    prods = converter(rows, extras)
    # Segurança: preço e idade vêm por rollup; se a integração não enxergar a base interna, eles chegam vazios.
    # Nesse caso usa o valor anterior e avisa, em vez de publicar o site sem preço.
    try: antes = {p['sku']: p for p in json.load(open(R / 'produtos.json', encoding='utf-8'))}
    except Exception: antes = {}
    problemas = []
    for p in prods:
        for campo in ('preco', 'idade'):
            if not p[campo]:
                if antes.get(p['sku'], {}).get(campo):
                    p[campo] = antes[p['sku']][campo]; problemas.append(f"{p['sku']}: {campo} vazio no Notion, mantido o anterior")
                else:
                    sys.exit(f"ERRO: {p['sku']} sem {campo} e sem valor anterior. Compartilhe a base Produtos com a integração.")
    if problemas:
        print('AVISO (rollups vazios — a integração provavelmente não tem acesso à base Produtos):'); print('\n'.join(problemas))
    faltam = [p['sku'] for p in prods if not (R.parent / 'play' / 'img' / f"cena_{p['sku']}.webp").exists()]
    if faltam: print('ATENÇÃO: sem imagens em play/img para', faltam, '(gerar a ficha antes de publicar)')
    json.dump(prods, open(R / 'produtos.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'{len(prods)} produtos gravados em gerador/produtos.json')
