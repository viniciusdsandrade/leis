"""Agrega recibos TA congelados em diretório explícito, sem rede nem Git."""
import argparse
import hashlib
import json
from pathlib import Path


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump(path, value):
    with path.open('x') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write('\n')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--manifesto', type=Path, action='append', required=True)
    ap.add_argument('--saida', type=Path, required=True)
    a = ap.parse_args()
    records = {}
    norms = []
    mapping = []
    componentes = []

    def add(path, expected=None):
        path = Path(path)
        if path.is_absolute():
            path = path.relative_to(Path.cwd())
        path = str(path)
        row = dict(arquivo=path, sha256=sha(path), bytes=Path(path).stat().st_size)
        if expected:
            assert row == expected, path
        if path in records:
            assert row == records[path], path
        records[path] = row

    for p in a.manifesto:
        m = json.loads(p.read_text())
        for r in m['arquivos']:
            add(r['arquivo'], r)
        add(p)
        lista = Path(m.get('lista_normas') or m['listas']['normas'])
        mapa = Path(m.get('mapeamento_fontes') or p.parent/'mapeamento-fontes.json')
        ns = lista.read_text().splitlines()
        rows = json.loads(mapa.read_text())
        assert len(ns) == m['normas'] and {r['path'] for r in rows} == set(ns)
        assert not set(ns).intersection(norms), 'Normas repetidas entre componentes'
        norms += ns
        for r in rows:
            mapping.append(dict(path=r['path'], sha256=r['sha256'],
                fonte=r.get('fonte') or r['prova_frontend'],
                prova_tabelas=r.get('prova_tabelas') or r.get('gates', {}).get('tabelas_nativas_prova')))
        componentes.append(dict(manifesto=str(p),sha256=sha(p),normas=len(ns)))
    a.saida.mkdir(parents=True, exist_ok=False)
    lista = a.saida/'normas.paths.txt'
    mapa = a.saida/'mapeamento-fontes.json'
    lista.write_text('\n'.join(norms)+'\n')
    dump(mapa, mapping)
    dump(a.saida/'componentes.json', componentes)
    receipt = a.saida/'entrega-final.json'
    (a.saida/'TESTAR.txt').write_text(
        'python3 -I '
        'scripts/qa_municipal_persistente_20261027.py scripts/verificar_entrega_ta_sem_promocoes_v2.py '
        f'--manifesto {receipt} --replay --saida {a.saida}/replay-ROOT-NOVO.json\n'
        f'Esperado: {len(norms)} replays aprovados, zero problemas. Use saída nova.\n')
    for p in a.saida.iterdir():
        add(p)
    add(Path(__file__))
    add('scripts/qa_municipal_persistente_20261027.py')
    add('_fonte/operacao_root_20261027/dependencias-qa.json')
    paths = a.saida/'entrega-final.paths.txt'
    paths.write_text('\n'.join(sorted(records))+'\n')
    add(paths)
    dump(receipt, dict(normas=len(norms),mapeamento_fontes=str(mapa),lista_normas=str(lista),
                       componentes=componentes,arquivos=list(records.values()),
                       bytes=sum(r['bytes'] for r in records.values()),
                       limite='Agregado de seleções auditadas; vigência e cobertura integral não são certificadas pela contagem.'))
    print(json.dumps(dict(manifesto=str(receipt),sha256=sha(receipt),normas=len(norms),arquivos=len(records))))


if __name__ == '__main__':
    main()
