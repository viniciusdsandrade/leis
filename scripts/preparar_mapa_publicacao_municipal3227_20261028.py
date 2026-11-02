"""Mapa seletivo de publicação; somente leitura das três entregas congeladas.

Não usa índice, stage, commit ou correção de canônicos. Confere cada SHA atual,
expõe compartilhamentos e exclui expressamente o canônico antigo de Buritis.
"""
from pathlib import Path
import argparse,collections,hashlib,importlib.metadata,json,sys
R=Path(__file__).resolve().parent.parent
B=Path('municipais/_indice/_recuperacao_20261027')
PACKS=[
 (B/'agregado3227-validado-final/entrega-final.json','9650eb0ed7329c0e1f3ef36b385b2aecda04a45044f5c96c6162e7d1ce973f44'),
 (B/'css-glifos-ta4735-20261027/manifesto.json','d13d4c68f5291b658e9d83f0ec3db19fd7eda4b191f52038f01afe4e3aefe160'),
 (B/'perfil-v7-buritis-final-20261028/manifesto.json','5efa86e88a50fc291017586e056273916dcb3875056395c5ca424b6555b1a370'),
]
HELD='municipais/MG/buritis/leis-ordinarias/1971/leis-ordinarias-8-1971-sapl-787.md'
def sha(path):return hashlib.sha256((R/path).read_bytes()).hexdigest()
def canonical(path):
 p=Path(path)
 return p.suffix=='.md' and p.parts[0]=='municipais' and not any(x.startswith(('_','.')) for x in p.parts)

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--saida',type=Path,required=True);a=ap.parse_args();a.saida.resolve().relative_to(R)
 records={};origins=collections.defaultdict(list);inputs=[];manifests=[]
 def add(path,expected=None,origin=None):
  p=Path(path);assert not p.is_absolute() and '..' not in p.parts;full=R/p;assert full.is_file() and not full.is_symlink(),str(p)
  row=dict(arquivo=str(p),sha256=sha(p),bytes=full.stat().st_size)
  if expected is not None:assert row==expected,dict(path=str(p),esperado=expected,atual=row)
  assert str(p) not in records or records[str(p)]==row,str(p)
  records[str(p)]=row
  if origin:origins[str(p)].append(str(origin))
 for path,expected in PACKS:
  assert sha(path)==expected;manifest=json.loads((R/path).read_text());manifests.append(manifest);inputs.append(dict(manifesto=str(path),sha256=expected))
  for row in manifest['arquivos']:add(row['arquivo'],row,path)
  add(path,origin=path)
 main_manifest=manifests[0];names=(R/main_manifest['lista_normas']).read_text().splitlines();mapping=json.loads((R/main_manifest['mapeamento_fontes']).read_text());assert len(names)==len(set(names))==len(mapping)==3227 and set(names)=={r['path'] for r in mapping}
 assert HELD not in names and HELD not in records
 fixtures=json.loads((R/Path(main_manifest['fixtures_head'])).read_text());fixtures_by={r['path']:r for r in fixtures};extras=[p for p in records if canonical(p) and p not in names]
 assert set(extras)==set(fixtures_by) and len(extras)==3
 for p in extras:assert records[p]['sha256']==fixtures_by[p]['sha256']
 assert {p for p in records if canonical(p)}==set(names)|set(extras)
 for p in [Path('scripts/preparar_mapa_publicacao_municipal3227_20261028.py'),Path('_fonte/operacao_root_20261027/dependencias-qa.json')]:add(p)
 a.saida.mkdir(exist_ok=False,parents=True)
 def dump(path,value):
  with (R/path).open('x') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
  add(path)
 lista=a.saida/'normas.paths.txt';(R/lista).write_text('\n'.join(names)+'\n');add(lista)
 map_path=a.saida/'mapeamento-fontes.json';dump(map_path,mapping)
 dump(a.saida/'hashes-compartilhados.json',dict(divergencias=[],compartilhados=[dict(path=p,sha256=records[p]['sha256'],bytes=records[p]['bytes'],manifestos=sorted(set(v))) for p,v in sorted(origins.items()) if len(set(v))>1]))
 whitespace=[]
 for p in names:
  raw=(R/p).read_bytes();hard=[];other=[]
  for i,line in enumerate(raw.split(b'\n'),1):
   trim=line.rstrip(b' \t\r')
   if line==trim:continue
   if line.endswith(b'  ') and not line.endswith(b'   ') and trim:hard.append(i)
   else:other.append(dict(linha=i,sufixo_hex=line[len(trim):].hex()))
  eof=len(raw)-len(raw.rstrip(b'\n'))
  if hard or other or eof!=1:whitespace.append(dict(path=p,sha256=records[p]['sha256'],hardbreak_duplo_espaco_linhas=hard,outros_sufixos=other,LF_finais=eof))
 dump(a.saida/'whitespace-preservado.json',dict(normas=3227,arquivos_com_marcacoes=len(whitespace),hardbreaks=sum(len(r['hardbreak_duplo_espaco_linhas']) for r in whitespace),arquivos_com_outros_sufixos=sum(bool(r['outros_sufixos']) for r in whitespace),registros=whitespace,criterio='Inventário, não correção. Todos os bytes e EOF pertencem aos SHA congelados; não aplicar strip, formatter ou whitespace=fix.'))
 versions={'markdown-it-py':'4.0.0','mdurl':'0.1.2','tinycss2':'1.4.0','cssselect2':'0.8.0','html5lib':'1.1','six':'1.17.0','webencodings':'0.5.1','lxml':'6.1.1'}
 for relative in ['scripts/bin/qa-20261027/python','scripts/bin/qa-html5-20261027/python','scripts/bin/qa-confaz-20261027/python']:sys.path.insert(0,str(R/relative))
 for name,version in versions.items():assert importlib.metadata.version(name)==version,(name,importlib.metadata.version(name))
 dump(a.saida/'dependencias-runtime.json',dict(python=sys.version,versoes=versions,runtime_existente='Validado; não instalar outra cópia nesta operação.',bibliotecas_incluidas_no_stage=False,gitattributes_sha256_apenas_contexto=sha(Path('.gitattributes'))))
 requirements=a.saida/'requirements-qa-v7.txt';(R/requirements).write_text(''.join(k+'=='+v+'\n' for k,v in versions.items()));add(requirements)
 dump(a.saida/'selecao-publicacao.json',dict(normas_novas=3227,lista_normas=str(lista),fixtures_HEAD_referencia_sem_contagem=fixtures,canônico_Buritis_excluido=HELD,sha256_Buritis_antigo='407f89d8c476b79487840a744769d63589d08d3968039c8ae8b9756446f470ba',reparo_Buritis_somente_TXT_privado=True,pacotes_originais_preservados=inputs,nenhuma_promocao_ou_Git_escrita=True))
 instructions=a.saida/'INSTRUCOES_ROOT.txt';(R/instructions).write_text(
  'Mapa de publicação exclusivo: 3.227 MDs novos. Há três fixtures idênticos a HEAD, sem contagem; não há canônico antigo de Buritis, nem MDs novos dos 921/586. Provas e candidatos de reparo são TXT privados, sem promoção. Os três pacotes de origem continuam intactos.\n\n'
  '1. Repetir SHA/bytes deste manifesto e dos artefatos. Repetir dedup contra HEAD real por OID, formato e gates do índice no ROOT.\n'
  '2. Replay: python3 -I scripts/verificar_entrega_ta_sem_promocoes_v3_privado_20261027.py --manifesto '+str(a.saida/'manifesto.json')+' --replay --saida NOVA_SAIDA_REPLAY3227.json\n'
  '3. Testes: python3 -I scripts/test_perfil_ta_tachados_preservados_20261027.py e python3 -I scripts/test_materializador_ta_v7_privado_20261027.py, usando o Python bundled. Esperado: 14 + 2 testes.\n\n'
  'Stage somente ROOT, quando os gates passarem (não executado pelo agente):\n'
  'git --literal-pathspecs -c core.autocrlf=false add -f --pathspec-from-file='+str(a.saida/'stage.paths.z')+' --pathspec-file-nul\n'
  'O NUL mantém nomes literais e evita ARG_MAX. O manifesto não contém seu próprio SHA; confira o SHA externo entregue e os blobs do índice por :PATH contra cada registro. stage.paths.z inclui o manifesto e a si próprio.\n\n'
  'Hardbreak/EOF: whitespace-preservado.json enumera os bytes intencionais. Não remover espaços duplos, quebras finais ou CRLF de snapshots, nem usar git apply --whitespace=fix. Preservar SHA no índice é o gate definitivo. Para triagem de whitespace intencional: git -c core.whitespace=-blank-at-eol,-blank-at-eof diff --cached --check -- municipais scripts. Alertas de snapshot bruto exigem conferência SHA, não normalização. .gitattributes já preserva HTMLs municipais em _fonte; o mapa também contém cópias de prova fora desse padrão.\n\n'
  'Dependências: o runtime QA já está pronto e foi validado; não instalar duplicado. Em máquina limpa, usar Python compatível e pip install --target scripts/bin/qa-20261027/python -r '+str(requirements)+'. Bibliotecas/runtime não entram na lista de stage. As versões efetivas estão em dependencias-runtime.json.\n\n'
  'CSS4735 inclui controle dos 921/586 que serão publicados depois: seus MDs não são stage deste mapa. O replay CSS integral requer os candidatos locais preservados ou esses dois lotes publicados; as três listas/mapas/recibos e o diagnóstico SHA ficam preservados. O replay de publicação deste mapa exige somente os 3.227 selecionados.\n'
 );add(instructions)
 receipt=a.saida/'manifesto.json';txt=a.saida/'stage.paths.txt';nul=a.saida/'stage.paths.z';paths=sorted(set(records)|{str(receipt),str(txt),str(nul)})
 (R/txt).write_text('\n'.join(paths)+'\n');(R/nul).write_bytes(('\0'.join(paths)+'\0').encode());add(txt);add(nul)
 result=dict(normas=3227,lista_normas=str(lista),mapeamento_fontes=str(map_path),arquivos=list(records.values()),bytes=sum(r['bytes'] for r in records.values()),stage_lista=str(nul),stage_paths=len(paths),origens=inputs,fixtures_referencia=3,buritis_canonico_excluido=True,divergencias_hashes_compartilhados=[],limite='Proposta seletiva pronta para revisão ROOT. Nenhuma escrita Git ou reparo de canônico. SHA/bytes incluem hardbreaks/EOF; não certifica vigência integral ou cobertura por contagem.')
 with (R/receipt).open('x') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps(dict(manifesto=str(receipt),sha256=sha(receipt),normas=3227,artefatos=len(records),stage_paths=len(paths),bytes=result['bytes'])))

if __name__=='__main__':main()
