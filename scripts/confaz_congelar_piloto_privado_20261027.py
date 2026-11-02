"""Recibo compacto do piloto privado CONFAZ; não publica nem modifica fontes."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'scripts'))
from confaz_auditar_piloto_privado_v3_20261027 import representar,texto_visivel_html,html5lib,tinycss2,cssselect2


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def dump(p,value):
    with p.open('x') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--saida',type=Path,required=True);a=ap.parse_args()
    a.saida=a.saida.resolve();assert (ROOT/'.git').exists();a.saida.mkdir(parents=True,exist_ok=False)
    base=ROOT/'reguladores/_fonte/auditorias'
    core=['confaz-probe-root-20261027','confaz-piloto-v2-20261027','confaz-piloto-qa-v3-20261027',
          'confaz-piloto-head-v3-20261027','confaz-piloto-candidatos-v2-20261027',
          'confaz-controle-historico35-20261027','confaz-controle-historico35-qa-v3-20261027']
    files=set()
    for name in core:
        files.update(str(p.relative_to(ROOT)) for p in (base/name).rglob('*') if p.is_file() and p.name!='ls-tree-reguladores.z')
    # Preserva o snapshot de nomes/OIDs em gzip, sem copiar a coleção de MDs.
    tree=base/'confaz-piloto-head-v3-20261027/ls-tree-reguladores.z'
    packed=a.saida/'ls-tree-reguladores.z.gz';packed.write_bytes(gzip.compress(tree.read_bytes(),mtime=0))
    capture=json.loads((base/'confaz-piloto-v2-20261027/manifesto-captura.json').read_text())
    qa=json.loads((base/'confaz-piloto-qa-v3-20261027/resumo.json').read_text())
    head=json.loads((base/'confaz-piloto-head-v3-20261027/confronto-head.json').read_text())
    candidates=json.loads((base/'confaz-piloto-candidatos-v2-20261027/mapa-candidatos.json').read_text())
    history=json.loads((base/'confaz-controle-historico35-qa-v3-20261027/35/controle.json').read_text())
    assert qa['aprovados_representacao']==6 and qa['retidos']==0 and candidates['candidatos']==6
    assert head['sem_alias']==6 and head['aliases']==0 and head['retidos']==0
    assert history['estado']=='retido' and len(history['historico_identificado'])>=8
    raw_history=(base/'confaz-controle-historico35-qa-v3-20261027/35/campo-original.html').read_text()
    equality=texto_visivel_html(raw_history)==texto_visivel_html(representar(raw_history))
    assert equality
    dump(a.saida/'controle-historico-negativo.json',dict(numero=35,ano=2025,estado='retido',
        igualdade_textual_isolada_passaria=equality,historicos_identificados=history['historico_identificado'],
        fonte=history['fonte'],motivo=history['motivo'],
        limite='O controle demonstra que rótulos/classes Ant e períodos de efeitos exigem modo explícito de versões, mesmo sem tachado gráfico ou CSS oculto. Não se conclui revogação de todo o ato.'))
    dump(a.saida/'identidades-formais.json',[dict(namespace='CONFAZ',tipo='Convênio ICMS',numero=r['numero'],ano=r['ano'],
        chave=['CONVENIO ICMS',r['numero'],r['ano']],path_proposto=r['path_canonico_proposto'],candidato=r['candidato'],sha256_md=r['sha256_md']) for r in candidates['resultados']])
    dump(a.saida/'runtime.json',dict(python=sys.version,html5lib=html5lib.__version__,tinycss2=tinycss2.__version__,cssselect2=cssselect2.__version__,
        markdown_it='4.0.0',transport='curl 8.7.1 do sistema, SecureTransport, TLS verificado; nunca insecure',
        localizacao_css='scripts/bin/qa-confaz-20261027/python',localizacao_html5='scripts/bin/qa-html5-20261027/python',
        bibliotecas_incluidas=False,limite='Versões e scripts incluídos; runtimes QA isolados permanecem locais e ignorados.'))
    failed=base/'confaz-piloto-v1-20261027/manifesto-captura.json'
    files.add(str(failed.relative_to(ROOT)))
    files.add('municipais/_indice/_recuperacao_20261027/confaz-piloto-captura.log')
    files.add('municipais/_indice/_recuperacao_20261027/confaz-piloto-captura-v2.log')
    baseline=ROOT/head['baseline_v7']['path'];cache=ROOT/head['baseline_v7']['cache']
    files.update([str(baseline.relative_to(ROOT)),str(cache.relative_to(ROOT)),
                  'scripts/dados/baseline-reguladores-head-v7-gerador-20261027.txt'])
    code=['confaz_capturar_piloto_privado_20261027.py','confaz_capturar_piloto_privado_v2_20261027.py',
          'confaz_auditar_piloto_privado_20261027.py','confaz_auditar_piloto_privado_v2_20261027.py','confaz_auditar_piloto_privado_v3_20261027.py',
          'confaz_confrontar_head_privado_20261027.py','confaz_confrontar_head_privado_v2_20261027.py',
          'confaz_preparar_candidatos_privados_20261027.py','test_confaz_piloto_privado_20261027.py','test_confaz_piloto_privado_v2_20261027.py',
          'representacao_html_dou.py','representacao_html_dou_v2.py','auditar_dou_css_tabelas_privado_20261027.py',
          'auditar_cache_dou.py','auditar.py','baixar_dou.py','comum.py','html2md.py','metadados_lotes.py']
    files.update('scripts/'+p for p in code);files.add('scripts/estados/pe_fidelidade_visivel.py');files.add(str(Path(__file__).resolve().relative_to(ROOT)))
    (a.saida/'TESTAR.txt').write_text(
        'Testes offline (8 casos):\npython3 -I scripts/test_confaz_piloto_privado_v2_20261027.py\n\n'
        'Replay da representação/CSS, sempre em saída nova:\npython3 -I scripts/confaz_auditar_piloto_privado_v3_20261027.py --captura reguladores/_fonte/auditorias/confaz-piloto-v2-20261027 --saida NOVA_SAIDA\n'
        'Esperado: 6 representações verificadas, 0 retidos. Não é autorização de publicação.\n'
        'Controle histórico: repetir com --captura reguladores/_fonte/auditorias/confaz-controle-historico35-20261027; esperado 0 representações liberadas, 1 retido.\n'
        'Aliases: scripts/confaz_confrontar_head_privado_v2_20261027.py --qa reguladores/_fonte/auditorias/confaz-piloto-qa-v3-20261027 --saida NOVA_SAIDA_HEAD\n'
        'Este último lê o HEAD real atual; pode encontrar aliases se a integração já tiver ocorrido. O recibo preserva o commit originalmente confrontado. Nenhum desses replays faz HTTP.\n')
    dump(a.saida/'resumo-piloto.json',dict(piloto_privado=True,candidatos=6,historico_retido=1,css_capturados=19,
        novas_respostas_http_200=capture['requisicoes_novas']+1,tentativa_python_tls_pre_http='Retida por falha da cadeia de confiança no runtime; transporte do sistema verificou TLS normalmente. Sem insecure ou alteração do host.',
        commit_confronto=head['commit'],cabecalhos_HEAD=head['cabecalhos_canonicos_HEAD'],blobs_reexaminados=head['blobs_alias_reexaminados'],aliases=0,
        matrizes_texto_sinais_numeros_preservados=True,condicoes_ratificacao_efeitos='Mantidas literalmente. Os novos 122–126 trazem publicação DOU de 26.10.2026 e condição de entrada em vigor vinculada à ratificação; nenhuma vigência foi calculada.',
        precisao_captura='121 usa o dia original da sondagem ROOT, explicitamente declarado e corroborado pelo HTTP Date; horário de cliente desconhecido preservado. Os outros cinco têm timestamp novo com fuso America/Recife.',
        limite_versao='Somente o campo integral de texto/notas oferecido no portal é certificado. O 121 termina na cláusula segunda e não apresenta rol nominal de signatários nesse campo; os 122–126 incluem fecho nominal. Não se inventou conteúdo nem se afirma equivalência editorial com o DOU.',
        limites=['Nenhum canônico, helper vivo, plano ou registro alterado. Nenhuma promoção automática.',
                 'Nova coleta volumosa depende da avaliação do piloto. Históricos como o35 permanecem retidos até modo explícito de versões.',
                 'Revalidar HEAD e reservas qualificadas por namespace/tipo/número/ano antes de integrar; URLs e hierarquias administrativas podem ser aliases.'],
        tree=dict(original_sha256=sha(tree),gzip=str(packed.relative_to(ROOT)),gzip_sha256=sha(packed))))
    files.update(str(p.relative_to(ROOT)) for p in a.saida.iterdir() if p.is_file())
    paths=a.saida/'artefatos.paths.txt';paths.write_text('\n'.join(sorted(files))+'\n');files.add(str(paths.relative_to(ROOT)))
    records=[dict(arquivo=p,sha256=sha(ROOT/p),bytes=(ROOT/p).stat().st_size) for p in sorted(files)]
    receipt=a.saida/'manifesto.json';dump(receipt,dict(arquivos=records,bytes=sum(r['bytes'] for r in records),candidatos=6,historico_retido=1,promocao_automatica=False))
    print(json.dumps(dict(manifesto=str(receipt.relative_to(ROOT)),sha256=sha(receipt),arquivos=len(records),bytes=sum(r['bytes'] for r in records))))


if __name__=='__main__':main()
