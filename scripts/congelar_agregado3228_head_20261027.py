"""Congela somente 595 + 915 + 1.167 + 551 após confronto conjunto HEAD.

Sem novos candidatos, rede ou escrita Git. Fixtures canônicos fora da lista
nova precisam coincidir byte a byte com o blob HEAD e ficam como referências.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = ROOT / 'municipais/_indice/_recuperacao_20261027'
EXPECTED = {
    595: 'f7d0660b9d8fb84d9cf16a0381851fe6e9f6dca27f478b760c6072656beb97e6',
    915: 'db37364aa54e71ec8aa6fe5c454c5451dc0493019d18a9b928044fb914d177f4',
    1167: '0aa9a7f5be35566ec7554177f0442ec5226e930a5bfced89bb23500ce818b33d',
    551: '4d742c8007982d73fde47e1758d4be599e134a31bab20b99dd1e73488affc95a',
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


def canonical(path):
    p = Path(path)
    return p.suffix == '.md' and p.parts[0] == 'municipais' and not any(part.startswith('_') for part in p.parts)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--saida', type=Path, required=True)
    args = parser.parse_args()
    output = args.saida.resolve()
    output.mkdir(parents=True, exist_ok=False)
    composition_path = BASE / 'agregado3228-composicao/entrega-final.json'
    composition = json.loads(composition_path.read_text())
    baseline_path = BASE / 'baseline-head-agregado3228-final/manifesto.json'
    baseline = json.loads(baseline_path.read_text())
    dedup_path = BASE / 'agregado3228-confronto-head.json'
    dedup = json.loads(dedup_path.read_text())
    replay_path = BASE / 'agregado3228-replay-integral.json'
    replay = json.loads(replay_path.read_text())
    assert composition['normas'] == 3228
    assert baseline['normas_head'] == baseline['total'] == 27626 and baseline['reservas'] == []
    assert dedup['comparados'] == 27626 and dedup['candidatos'] == 3228 and not dedup['colisoes']
    assert dedup['commit'] == baseline['commit'] and dedup['sha256_baseline'] == sha(baseline_path)
    assert replay['normas'] == replay['replay'] == replay['replay_aprovados'] == 3228 and not replay['problemas']
    seen = set()
    components = []
    for count, expected in EXPECTED.items():
        path = BASE / f'agregado{count}-final/entrega-final.json'
        assert sha(path) == expected
        manifest = json.loads(path.read_text())
        names = (ROOT / manifest['lista_normas']).read_text().splitlines()
        assert len(names) == count and len(names) == len(set(names)) and not seen.intersection(names)
        seen.update(names)
        components.append(dict(manifesto=str(path.relative_to(ROOT)), sha256=expected, normas=count))
    names = (ROOT / composition['lista_normas']).read_text().splitlines()
    assert len(names) == len(seen) == 3228 and set(names) == seen
    with gzip.open(ROOT / baseline['metadados'], 'rt') as stream:
        head = {row['path']: row for row in map(json.loads, stream)}
    assert len(head) == 27626 and not seen.intersection(head)
    records = {}
    def add(path, expected=None):
        path = Path(path)
        relative = str(path.relative_to(ROOT)) if path.is_absolute() else str(path)
        actual = ROOT / relative
        row = dict(arquivo=relative, sha256=sha(actual), bytes=actual.stat().st_size)
        if expected is not None:
            assert row == expected, relative
        if relative in records:
            assert records[relative] == row
        records[relative] = row
    for row in composition['arquivos']:
        add(row['arquivo'], row)
    add(composition_path)
    for row in baseline['arquivos']:
        add(row['arquivo'], row)
    for path in [baseline_path, dedup_path, replay_path, Path(__file__).resolve()]:
        add(path)
    fixtures = []
    for path, row in records.items():
        if canonical(path) and path not in seen:
            assert path in head and row['sha256'] == head[path]['sha256']
            fixtures.append(dict(path=path, oid=head[path]['oid'], sha256=row['sha256'], natureza='Fixture idêntico a HEAD; referência, sem contagem nova.'))
    assert len(fixtures) == 3
    (output / 'normas.paths.txt').write_text('\n'.join(names) + '\n')
    (output / 'mapeamento-fontes.json').write_bytes((ROOT / composition['mapeamento_fontes']).read_bytes())
    write_json(output / 'componentes.json', components)
    write_json(output / 'fixtures-head.json', fixtures)
    write_json(output / 'confronto-final.json', dict(commit=baseline['commit'], normas_head=27626, reservas=[],
        candidatos=3228, colisoes=0, intersecoes_internas=0, fixtures_referencia=3,
        baseline=str(baseline_path.relative_to(ROOT)), sha256_baseline=sha(baseline_path),
        confronto=str(dedup_path.relative_to(ROOT)), sha256_confronto=sha(dedup_path),
        replay_integral=str(replay_path.relative_to(ROOT)), sha256_replay=sha(replay_path),
        criterio='Confronto conjunto das 3.228 identidades contra blobs completos por OID de HEAD; nenhum componente foi adicionado como reserva nesta comparação final.'))
    prefix = 'python3 -I '
    receipt = output / 'entrega-final.json'
    (output / 'TESTAR.txt').write_text(
        'Replay integral em saída nova:\n' + prefix + 'scripts/qa_municipal_persistente_20261027.py scripts/verificar_entrega_ta_sem_promocoes_v2.py --manifesto ' + str(receipt.relative_to(ROOT)) + ' --replay --saida NOVA_SAIDA_REPLAY.json\n\n' +
        'Confronto congelado, sem reservas:\n' + prefix + 'scripts/comparar_baseline_municipal_head_20261027.py --baseline ' + str(baseline_path.relative_to(ROOT)) + ' --lista ' + str((output / 'normas.paths.txt').relative_to(ROOT)) + ' --saida NOVA_SAIDA_DEDUP.json\n' +
        'Esperado: 27.626 comparados, 3.228 candidatos e zero colisões. ROOT deve revalidar HEAD atual antes de publicar. Não acrescentar candidatos a este sucessor congelado.\n')
    for path in output.iterdir():
        add(path)
    listing = output / 'entrega-final.paths.txt'
    listing.write_text('\n'.join(sorted(records)) + '\n')
    add(listing)
    write_json(receipt, dict(normas=3228, lista_normas=str((output / 'normas.paths.txt').relative_to(ROOT)),
        mapeamento_fontes=str((output / 'mapeamento-fontes.json').relative_to(ROOT)), componentes=components,
        arquivos=list(records.values()), bytes=sum(row['bytes'] for row in records.values()),
        confronto_final=str((output / 'confronto-final.json').relative_to(ROOT)),
        limite='Sucessor imutável dos quatro pacotes. Três fixtures idênticos a HEAD são referências sem contagem. Sem novos candidatos, edição de originais ou certificação de vigência/cobertura integral por contagem.'))
    print(json.dumps(dict(manifesto=str(receipt.relative_to(ROOT)), sha256=sha(receipt), normas=3228, arquivos=len(records), bytes=sum(row['bytes'] for row in records.values()))))


if __name__ == '__main__':
    main()
