"""Congela candidatos privados CONFAZ e controles completos, sem promoção."""
import argparse
import ast
import gzip
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
from confaz_auditar_piloto_privado_v3_20261027 import html5lib, tinycss2, cssselect2


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--saida', type=Path, required=True)
    args = parser.parse_args()
    base = ROOT / 'reguladores/_fonte/auditorias'
    args.saida = args.saida.resolve()
    args.saida.mkdir(parents=True, exist_ok=False)
    names = ['confaz-indice2026-captura-001-20261027', 'confaz-indice2026-entrada-qa-002-20261027',
             'confaz-indice2026-qa-002-20261027', 'confaz-indice2026-head-002-20261027',
             'confaz-indice2026-candidatos-002-20261027']
    files = {str(p.relative_to(ROOT)) for name in names for p in (base / name).rglob('*')
             if p.is_file() and p.name != 'ls-tree-reguladores.z'}
    capture = json.loads((base / names[0] / 'manifesto-captura.json').read_text())
    entry = json.loads((base / names[1] / 'manifesto-captura.json').read_text())
    qa = json.loads((base / names[2] / 'resumo.json').read_text())
    head = json.loads((base / names[3] / 'confronto-head.json').read_text())
    candidates = json.loads((base / names[4] / 'mapa-candidatos.json').read_text())
    assert not capture['incompletos'] and len(capture['documentos']) == 127
    assert len(entry['paginas']) == 126 and len(entry['retidos_preflight']) == 1
    assert qa['aprovados_representacao'] == 116 and qa['retidos'] == 10
    assert head['sem_alias'] == candidates['candidatos'] == 110 and head['aliases'] == 6
    assert all(not row['alvo_preexistente'] for row in candidates['resultados'])
    for proof in capture['capturas']:
        path = ROOT / proof['arquivo']
        assert sha(path) == proof['sha256'] and path.stat().st_size == proof['bytes']
        files.add(proof['arquivo'])
        for key in ['metadata', 'headers_arquivo', 'stderr_arquivo']:
            if proof.get(key):
                assert (ROOT / proof[key]).is_file()
                files.add(proof[key])
    cache_base = capture['cache_base']
    assert sha(ROOT / cache_base['path']) == cache_base['sha256']
    files.add(cache_base['path'])
    tree = base / names[3] / 'ls-tree-reguladores.z'
    packed = args.saida / 'ls-tree-reguladores.z.gz'
    packed.write_bytes(gzip.compress(tree.read_bytes(), mtime=0))
    baseline = head['baseline_v8']
    for key in ['path', 'cache']:
        files.add(baseline[key])
    files.add('scripts/dados/baseline-reguladores-head-v8-gerador-20261027.txt')
    code = ['confaz_coletar_indice2026_privado_20261027.py', 'confaz_preparar_qa_indice2026_20261027.py',
            'confaz_auditar_piloto_privado_v3_20261027.py', 'confaz_auditar_piloto_privado_v2_20261027.py',
            'confaz_capturar_piloto_privado_v2_20261027.py', 'confaz_confrontar_head_privado_v3_20261027.py',
            'confaz_preparar_candidatos_privados_20261027.py', 'test_confaz_indice2026_privado_20261027.py',
            'test_confaz_piloto_privado_v2_20261027.py', 'representacao_html_dou.py', 'representacao_html_dou_v2.py',
            'auditar_dou_css_tabelas_privado_20261027.py', 'auditar.py', 'comum.py', 'html2md.py',
            'baixar_dou.py', 'metadados_lotes.py', 'estados/pe_fidelidade_visivel.py']
    files.update('scripts/' + name for name in code)
    files.add(str(Path(__file__).resolve().relative_to(ROOT)))
    # Auditor compartilhado pode evoluir em outra frente. Sua cópia exata fica
    # vinculada aqui, sem exigir que a versão viva volte a uma preimagem antiga.
    live = ROOT / 'scripts/auditar_cache_dou.py'
    snapshot = args.saida / 'auditar_cache_dou.snapshot.py'
    snapshot.write_bytes(live.read_bytes())
    source = live.read_text()
    node = next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == 'meta_corpo')
    function = ast.get_source_segment(source, node)
    dump(args.saida / 'runtime-e-codigo.json', dict(python=sys.version, html5lib=html5lib.__version__,
         tinycss2=tinycss2.__version__, cssselect2=cssselect2.__version__, markdown_it='4.0.0',
         bibliotecas_incluidas=False, auditor_snapshot=str(snapshot.relative_to(ROOT)),
         sha256_meta_corpo=hashlib.sha256(function.encode()).hexdigest(),
         limite='Apenas meta_corpo é usado pelo confronto; cópia do auditor preservada, sem substituir o helper vivo.'))
    dump(args.saida / 'identidades-formais.json', [dict(tipo='Convênio ICMS', numero=r['numero'], ano=r['ano'],
         path_proposto=r['path_canonico_proposto'], candidato=r['candidato'], sha256_md=r['sha256_md']) for r in candidates['resultados']])
    dump(args.saida / 'retencoes-e-aliases.json', dict(preflight=entry['retidos_preflight'],
         qa=[r for r in qa['resultados'] if r['estado'] == 'retido'],
         aliases=[r for r in head['resultados'] if r['estado'] == 'alias_HEAD_sem_contagem_nova']))
    dump(args.saida / 'resumo.json', dict(candidatos=110, aliases_publicados=6, retidos_qa=10,
         retificacao_separada=1, fontes_indice=127, novas_requisicoes=capture['novas_requisicoes'],
         commit_confronto=head['commit'], cabecalhos_HEAD=head['cabecalhos_canonicos_HEAD'],
         representacao='Campo integral do portal, DOM textual e atributos preservados, confronto independente CommonMark e matrizes HTML5; CSS capturados e verificados.',
         limites=['Edição capturada do portal; não afirma equivalência editorial com o DOU nem vigência jurídica integral.',
                  'Condições, notas, ratificação e efeitos permanecem literais, sem calcular vigência.',
                  'Histórico, tachas e identidades inconclusivas continuam retidos; nenhum canônico foi escrito.',
                  'ROOT deve rever os candidatos e revalidar HEAD/reservas qualificadas antes de qualquer promoção.']))
    prefix = 'python3 -I '
    (args.saida / 'TESTAR.txt').write_text(prefix + 'scripts/test_confaz_piloto_privado_v2_20261027.py\n' +
        prefix + 'scripts/test_confaz_indice2026_privado_20261027.py\n\n' +
        prefix + 'scripts/confaz_auditar_piloto_privado_v3_20261027.py --captura reguladores/_fonte/auditorias/' + names[1] + ' --saida NOVA_SAIDA_QA\n' +
        'Esperado: 116 representações, 10 retidos. Seis representações são aliases já publicados, não novas adições.\n' +
        prefix + 'scripts/confaz_confrontar_head_privado_v3_20261027.py --qa reguladores/_fonte/auditorias/' + names[2] + ' --saida NOVA_SAIDA_HEAD\n' +
        'O confronto lê HEAD real; novas publicações podem aumentar aliases. Nenhum comando faz HTTP ou promove canônicos.\n')
    files.update(str(p.relative_to(ROOT)) for p in args.saida.iterdir() if p.is_file())
    listing = args.saida / 'artefatos.paths.txt'
    listing.write_text('\n'.join(sorted(files)) + '\n')
    files.add(str(listing.relative_to(ROOT)))
    records = [dict(arquivo=p, sha256=sha(ROOT / p), bytes=(ROOT / p).stat().st_size) for p in sorted(files)]
    receipt = args.saida / 'manifesto.json'
    dump(receipt, dict(candidatos=110, promocao_automatica=False, arquivos=records, bytes=sum(r['bytes'] for r in records)))
    print(json.dumps(dict(manifesto=str(receipt.relative_to(ROOT)), sha256=sha(receipt), arquivos=len(records), bytes=sum(r['bytes'] for r in records))))


if __name__ == '__main__':
    main()
