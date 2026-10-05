// Recebe o formulário "Lista do Piccolo" e grava no Notion (uma linha por criança).
// Variável de ambiente no Netlify: NOTION_LISTA_TOKEN (integração com permissão de inserir na base Lista do Piccolo).
const DS = '122410e3-f980-4241-ad73-0dcc5190e35b';
const TAM = ['RN','P','M','G','1','2','3','4','5','6','7','8','9','10','11','12'];
const MESES = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'];
const INT = ['Dia a dia','Festa','Inverno','Calçados','Enxoval','Brinquedos','Importados'];

export default async (req) => {
  if (req.method !== 'POST') return new Response('Método não permitido', { status: 405 });
  const token = process.env.NOTION_LISTA_TOKEN;
  if (!token) return Response.json({ ok: false, erro: 'Sem NOTION_LISTA_TOKEN' }, { status: 500 });
  let d; try { d = await req.json(); } catch { return Response.json({ ok: false, erro: 'JSON inválido' }, { status: 400 }); }
  const nome = String(d.nome || '').slice(0, 80).trim();
  const zap = String(d.zap || '').replace(/\D/g, '').slice(0, 13);
  if (nome.length < 2 || zap.length < 10) return Response.json({ ok: false, erro: 'Dados incompletos' }, { status: 400 });
  const cidade = String(d.cidade || '').slice(0, 80);
  const origem = String(d.origem || 'Site').slice(0, 120);
  const interesses = (Array.isArray(d.interesses) ? d.interesses : []).filter(i => INT.includes(i)).map(name => ({ name }));
  const criancas = (Array.isArray(d.criancas) ? d.criancas : []).slice(0, 6);
  const grupo = Date.now().toString(36) + '-' + zap.slice(-4);
  const fone = zap.startsWith('55') ? '+' + zap : '+55' + zap;
  const resultados = [];
  for (const c of (criancas.length ? criancas : [{}])) {
    const props = {
      'Contato': { title: [{ text: { content: nome } }] },
      'WhatsApp': { phone_number: fone },
      'Status': { select: { name: 'Novo' } },
      'Grupo': { rich_text: [{ text: { content: grupo } }] },
      'Origem': { rich_text: [{ text: { content: origem } }] },
      'Interesses': { multi_select: interesses },
    };
    if (cidade) props['Cidade'] = { rich_text: [{ text: { content: cidade } }] };
    if (c.sexo === 'Menina' || c.sexo === 'Menino') props['Criança'] = { select: { name: c.sexo } };
    if (TAM.includes(String(c.tam))) props['Tamanho'] = { select: { name: String(c.tam) } };
    if (MESES.includes(c.mes)) props['Aniversário'] = { select: { name: c.mes } };
    const r = await fetch('https://api.notion.com/v1/pages', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}`, 'Notion-Version': '2025-09-03', 'Content-Type': 'application/json' },
      body: JSON.stringify({ parent: { type: 'data_source_id', data_source_id: DS }, properties: props }),
    });
    resultados.push(r.status);
  }
  const ok = resultados.every(s => s < 300);
  return Response.json({ ok, grupo, resultados }, { status: ok ? 200 : 502 });
};

export const config = { path: '/.netlify/functions/lista' };
