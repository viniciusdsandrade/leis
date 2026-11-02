"""Acrescenta provas de replay/confronto a um agregado sem alterar originais."""
from pathlib import Path
import argparse, gzip, hashlib, json
R=Path(__file__).resolve().parent.parent

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p): return json.loads(Path(p).read_text())
def canonical(p):
 p=Path(p)
 return p.suffix=='.md' and p.parts[0]=='municipais' and not any(x.startswith(('_','.')) for x in p.parts)

def main():
 ap=argparse.ArgumentParser(description=__doc__)
 for key in ['manifesto','baseline','confronto','replay','saida']:ap.add_argument('--'+key,type=Path,required=True)
 a=ap.parse_args();a.saida.resolve().relative_to(R);m=load(a.manifesto);b=load(a.baseline);d=load(a.confronto);r=load(a.replay)
 names=(R/m['lista_normas']).read_text().splitlines();n=m['normas'];assert n==len(names)==len(set(names))
 assert r['normas']==r['replay']==r['replay_aprovados']==n and not r['problemas']
 proofs=r['resultados_replay'];assert len(proofs)==n and {p['path'] for p in proofs}==set(names)
 assert all(p['aprovado'] and p['igualdade_caracteres_nao_brancos'] and p['assinatura_numerica_confere'] for p in proofs)
 assert d['commit']==b['commit'] and d['sha256_baseline']==sha(a.baseline)
 assert d['sha256_lista']==sha(R/m['lista_normas']) and d['comparados']==b['total'] and d['candidatos']==n and not d['colisoes']
 assert set(d['sha256_candidatos'])==set(names)
 with gzip.open(R/b['metadados'],'rt') as stream:existing={row['path']:row for row in map(json.loads,stream)}
 assert len(existing)==b['total'] and not set(names).intersection(existing)
 records={}
 def add(path,expected=None):
  path=Path(path);rel=str(path.relative_to(R)) if path.is_absolute() else str(path);p=R/rel
  actual=dict(arquivo=rel,sha256=sha(p),bytes=p.stat().st_size)
  if expected is not None: assert actual==expected,rel
  assert rel not in records or records[rel]==actual
  records[rel]=actual
 for row in m['arquivos']:add(row['arquivo'],row)
 for p in names: assert records[p]['sha256']==d['sha256_candidatos'][p]
 for row in b['arquivos']:add(row['arquivo'],row)
 for p in [a.manifesto,a.baseline,a.confronto,a.replay,Path(__file__)]:add(p)
 test=Path(__file__).with_name('test_'+Path(__file__).name)
 if test.is_file():add(test)
 fixtures=[]
 for p,row in records.items():
  if canonical(p) and p not in names:
   assert p in existing and existing[p]['origem']=='HEAD' and existing[p]['sha256']==row['sha256'],p
   fixtures.append(dict(path=p,OID=existing[p]['oid'],sha256=row['sha256'],contagem_nova=0))
 a.saida.mkdir(parents=True,exist_ok=False)
 def dump(path,value):
  with path.open('x') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
 dump(a.saida/'fixtures-head.json',fixtures);add(a.saida/'fixtures-head.json')
 receipt=a.saida/'entrega-final.json';prefix='python3 -I '
 (a.saida/'TESTAR.txt').write_text(prefix+'scripts/qa_municipal_persistente_20261027.py scripts/verificar_entrega_ta_sem_promocoes_v2.py --manifesto '+str(receipt)+' --replay --saida NOVA_SAIDA_REPLAY.json\nEsperado: '+str(n)+'/'+str(n)+' replays, zero problemas.\n\n'+prefix+'scripts/comparar_baseline_municipal_head_20261027.py --baseline '+str(a.baseline)+' --lista '+m['lista_normas']+' --saida NOVA_SAIDA_CONFRONTO.json\nEsperado: '+str(b['total'])+' comparados, '+str(n)+' candidatos, zero colisões. Revalidar HEAD atual antes de publicar.\n')
 add(a.saida/'TESTAR.txt');listing=a.saida/'entrega-final.paths.txt';listing.write_text('\n'.join(sorted(records))+'\n');add(listing)
 m.update(arquivos=list(records.values()),bytes=sum(x['bytes'] for x in records.values()),confronto_final=str(a.confronto),replay_integral=str(a.replay),fixtures_head=str(a.saida/'fixtures-head.json'),limite='Agregado com replay integral e confronto conjunto contra blobs completos HEAD e reservas qualificadas externas. Nenhum componente integra o baseline conjunto; fixtures HEAD idênticos sem contagem. Originais preservados. Não certifica vigência/cobertura integral por contagem.')
 dump(receipt,m);print(json.dumps(dict(manifesto=str(receipt),sha256=sha(receipt),normas=n,arquivos=len(records),bytes=m['bytes'])))

if __name__=='__main__':main()
