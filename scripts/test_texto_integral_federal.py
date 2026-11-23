"""Evita publicar errata avulsa como se fosse a norma integral."""
from pathlib import Path
import sys
import unittest
import tempfile
import gzip
import hashlib
import json
from unittest.mock import patch, Mock
from urllib.error import HTTPError
sys.path.insert(0, str(Path(__file__).resolve().parent))
import baixar_federal as f


class TextoIntegral(unittest.TestCase):
    def test_recusa_http_nao_e_retentada(self):
        error = HTTPError('https://normas.leg.br/', 403, 'Forbidden', {}, None)
        with patch.object(f, 'LIMITE', Mock()), patch.object(f.urllib.request, 'urlopen', side_effect=error) as request:
            with self.assertRaisesRegex(RuntimeError, 'fonte recusou HTTP 403'):
                f.http_get('https://normas.leg.br/')
        self.assertEqual(request.call_count, 1)

    def test_original_antes_da_retificacao_mais_recente(self):
        original = {'contentUrl': 'https://normas.leg.br/original', 'version': 'Original', 'datePublished': '2000-01-01'}
        errata = {'contentUrl': 'https://normas.leg.br/errata', 'version': 'Intermediate', 'datePublished': '2000-02-01'}
        self.assertEqual(f.escolher_texto({'encoding': [original, errata]}), original)

    def test_refazer_so_regrava_republicacao(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = Path(tmp) / 'a.md'; b = Path(tmp) / 'b.md'
            a.write_text('---\nversao_texto: "republicação/retificação"\n---\n', encoding='utf-8')
            b.write_text('---\nversao_texto: "original"\n---\n', encoding='utf-8')
            self.assertTrue(f._e_so_republicacao(str(a)))
            self.assertFalse(f._e_so_republicacao(str(b)))

    def test_compilada_antes_do_original(self):
        original = {'contentUrl': 'https://normas.leg.br/original', 'version': 'Original'}
        atual = {'contentUrl': 'https://normas.leg.br/atual', 'version': 'Current'}
        self.assertEqual(f.escolher_texto({'encoding': [original, atual]}), atual)

    def test_artigo_citado_em_errata_nao_e_artigo_proprio(self):
        corpo = 'DECRETO Nº 3.435, DE 25 DE ABRIL DE 2000.\n\nNos arts. 3º e 5º do Anexo, onde se lê A, leia-se B.'
        self.assertIsNotNone(f.motivo_texto_parcial_decreto('DEC-n', corpo))

    def test_retificacao_com_artigo_copiado_continua_errata(self):
        self.assertIsNotNone(f.motivo_texto_parcial_decreto('DEC-n', '**RETIFICAÇÃO**\n\nArt. 1º Onde se lê A, leia-se B.'))

    def test_artigo_normativo_proprio(self):
        self.assertIsNone(f.motivo_texto_parcial_decreto('DEC-n', 'DECRETO Nº 1\n\n**Art**. 1º Fica aprovado o regulamento.\n\nArt. 2º Revogam-se as disposições.'))

    def test_errata_anexada_depois_da_norma_nao_torna_texto_avulso(self):
        corpo = 'DECRETO Nº 1\n\nArt. 1º Fica aprovado o regulamento.\n\nArt. 2º Este decreto entra em vigor.\n\nBrasília, 1 de janeiro de 2000.\n\nRETIFICAÇÃO\n\nNo anexo, onde se lê A, leia-se B.'
        self.assertIsNone(f.motivo_texto_parcial_decreto('DEC-n', corpo))

    def test_coletor_exige_epigrafe_e_revisao_so_em_area_privada(self):
        d = {'tipo': 'DEC-n', 'numero': '1', 'dataassinatura': '01/01/2000',
             'normaNome': 'Decreto nº 1 de 01/01/2000', 'norma': 'DEC-1-2000-01-01', 'id': 'fixture'}
        html = '<p>DECRETO Nº 1/2000</p><p>Art. 1º Fica autorizado o pagamento.</p><p>Brasília, 1 de janeiro de 2000.</p>'.encode()
        for revision in [False, True]:
            with self.subTest(revisao=revision), tempfile.TemporaryDirectory() as tmp:
                base = Path(tmp) / 'federal'
                stage = base / '_fonte/auditorias/revisao/work'
                with patch.object(f, 'RAIZ', str(stage if revision else base)):
                    info = f.montar(d)
                    meta = json.dumps({'legislationIdentifier': info['urn'], 'legislationDate': info['data'],
                                       'legislationType': 'Decreto Numerado',
                                       'encoding': {'contentUrl': 'https://example.invalid/texto', 'version': 'Original'}}).encode()
                    def response(url, *args, **kwargs):
                        return 200, meta if 'api/public/normas?' in url else html
                    with patch.object(f, 'http_get', response):
                        status, _, _ = f.processar(d, revisao_identidade=revision)
                    self.assertEqual(status, 'ok' if revision else 'sem_texto')
                    self.assertEqual(gzip.decompress(Path(info['fonte']).read_bytes()), html)
                    self.assertEqual(Path(info['md']).exists(), revision)
                    if revision:
                        self.assertIn('identidade_pendente_revisao: true', Path(info['md']).read_text())
                with patch.object(f, 'RAIZ', str(base)), patch.object(f, 'http_get', Mock()) as network:
                    with self.assertRaisesRegex(ValueError, 'nunca na raiz publicável'):
                        f.processar(d, revisao_identidade=True)
                    network.assert_not_called()

    def test_coletor_retem_visual_ou_anexo_ausente_preservando_fonte(self):
        d = {'tipo': 'DEC-n', 'numero': '1', 'dataassinatura': '01/01/2000',
             'normaNome': 'Decreto nº 1 de 01/01/2000', 'norma': 'DEC-1-2000-01-01', 'id': 'fixture'}
        base = '<p>DECRETO Nº 1, DE 1 DE JANEIRO DE 2000.</p><p>Art. 1º Fica aprovado o Regimento que com este baixa.</p><p>Brasília, 1 de janeiro de 2000.</p><p>PRESIDENTE</p>'
        for suffix in ['', '<img src="anexo.png">', '<!--[if gte vml 1]><v:imagedata src="a.wmz"/><![endif]-->']:
            with self.subTest(suffix=suffix), tempfile.TemporaryDirectory() as tmp, patch.object(f, 'RAIZ', tmp):
                info = f.montar(d)
                raw = (base + suffix).encode()
                meta = {'encoding': {'contentUrl': 'https://example.invalid/texto', 'version': 'Original'}}
                with patch.object(f, 'obter_metadados', return_value=(info['urn'], meta)), patch.object(f, 'http_get', return_value=(200, raw)):
                    status, _, detail = f.processar(d)
                self.assertEqual(status, 'sem_texto')
                self.assertFalse(Path(info['md']).exists())
                self.assertEqual(gzip.decompress(Path(info['fonte']).read_bytes()), raw)
                self.assertTrue(detail['elementos_visuais'] or detail['evidencia_anexo'])

    def test_imagem_na_pagina_como_pendencia_de_integralidade(self):
        d = {'tipo': 'DEC-n', 'numero': '1', 'dataassinatura': '01/01/2000',
             'normaNome': 'Decreto nº 1 de 01/01/2000', 'norma': 'DEC-1-2000-01-01', 'id': 'fixture'}
        texto = ('<p>DECRETO Nº 1, DE 1 DE JANEIRO DE 2000.</p><p>Art. 1º Fica aprovada a tabela de preços.</p>'
                 '<table><tr><td>Arroz</td><td><img src="data:image/png;base64,AAAAAAAA" width="13" height="61"></td><td>5.250,00</td></tr></table>'
                 '<p>Brasília, 1 de janeiro de 2000.</p><p>PRESIDENTE</p>')
        casos = {'imagem na tabela': (texto, 'ok'),
                 # sem a imagem não sobra nada do regimento: a trava de anexo próprio continua retendo
                 'regimento que com este baixa, só em imagem': (
                     '<p>DECRETO Nº 1, DE 1 DE JANEIRO DE 2000.</p><p>Art. 1º Fica aprovado o Regimento que com este baixa.</p>'
                     '<p>Brasília, 1 de janeiro de 2000.</p><p>PRESIDENTE</p><p><img src="data:image/png;base64,AAAA"></p>', 'sem_texto'),
                 'outro elemento visual': (texto + '<svg><path d="M0 0"/></svg>', 'sem_texto')}
        for caso, (html, esperado) in casos.items():
            with self.subTest(caso), tempfile.TemporaryDirectory() as tmp, patch.object(f, 'RAIZ', str(Path(tmp) / 'federal')):
                info = f.montar(d)
                meta = type('Metadados', (dict,), {})({'encoding': {'contentUrl': 'https://example.invalid/texto', 'version': 'Original'}})
                meta.captura = {'path': str(Path(tmp) / 'meta.gz'), 'sha256': hashlib.sha256(b'{}').hexdigest()}
                with gzip.open(meta.captura['path'], 'wb') as g:
                    g.write(b'{}')
                with patch.object(f, 'obter_metadados', return_value=(info['urn'], meta)), patch.object(f, 'http_get', return_value=(200, html.encode())):
                    if '<td><img' in html:  # sem o modo, a imagem na tabela continua parando a conversão
                        with self.assertRaisesRegex(ValueError, 'elemento visual não extraído na tabela: img'):
                            f.processar(d)
                    else:
                        self.assertEqual(f.processar(d)[0], 'sem_texto')
                    self.assertFalse(Path(info['md']).exists())
                    status, _, _ = f.processar(d, visual_pendente=True)
                self.assertEqual(status, esperado)
                registro = Path(tmp) / 'federal' / f.VISUAL_PENDENTE
                self.assertEqual(Path(info['md']).exists(), esperado == 'ok')
                self.assertEqual(registro.exists(), esperado == 'ok')
                if esperado == 'ok':
                    md = Path(info['md']).read_text(encoding='utf-8')
                    self.assertIn('imagens_nao_transcritas: "1 imagem na página da fonte', md)
                    self.assertIn('5.250,00', md)
                    self.assertNotIn('base64', md)
                    linha = json.loads(registro.read_text(encoding='utf-8'))
                    self.assertEqual((linha['path'], linha['norma'], linha['imagens'], linha['maior_imagem_bytes']),
                                     ('federal/decretos/2000/dec-1-2000-01-01.md', 'DEC-1-2000-01-01', 1, 6))
                    self.assertEqual(gzip.decompress(Path(info['fonte']).read_bytes()), html.encode())  # a fonte fica inteira

    def test_data_errada_so_na_epigrafe_com_fecho_que_confirma_o_indice(self):
        d = {'tipo': 'DEC-n', 'numero': '30301', 'dataassinatura': '20/12/1951',
             'normaNome': 'Decreto nº 30.301 de 20/12/1951', 'norma': 'DEC-30301-1951-12-20', 'id': 'fixture'}
        texto = ('<p>DECRETO Nº 30.301, DE 20 DE SETEMBRO DE 1951.</p><p>Abre crédito especial.</p>'
                 '<p>O Presidente da República decreta:</p><p>Art. 1º Fica aberto o crédito especial de Cr$ 100.000,00.</p>'
                 '<p>Rio de Janeiro, 20 de dezembro de 1951; 130º da Independência e 63º da República.</p><p>GETÚLIO VARGAS</p>')
        casos = {
            'só a data da epígrafe diverge': (texto, 'ok'),
            'o número também diverge': (texto.replace('30.301', '30.302'), 'sem_texto'),
            'o fecho traz a data da epígrafe': (texto.replace('20 de dezembro de 1951;', '20 de setembro de 1951;'), 'sem_texto'),
            'fecho sem a marca da era': (texto.replace('; 130º da Independência e 63º da República', ''), 'sem_texto'),
            'o primeiro fecho é de outra data': (texto.replace('<p>GETÚLIO', '<p>Rio de Janeiro, 20 de dezembro de 1951; 130º da Independência.</p><p>GETÚLIO')
                                                 .replace('20 de dezembro de 1951; 130º da Independência e', '19 de dezembro de 1951; 130º da Independência e'), 'sem_texto'),
            'outro fecho repete a data da epígrafe': (texto + '<p>Rio de Janeiro, 20 de setembro de 1951; 130º da Independência.</p>', 'sem_texto'),
        }
        for caso, (html, esperado) in casos.items():
            with self.subTest(caso), tempfile.TemporaryDirectory() as tmp, patch.object(f, 'RAIZ', str(Path(tmp) / 'federal')):
                info = f.montar(d)
                meta = type('Metadados', (dict,), {})({'encoding': {'contentUrl': 'https://example.invalid/texto', 'version': 'Original'}})
                meta.captura = {'path': str(Path(tmp) / 'meta.gz'), 'sha256': hashlib.sha256(b'{}').hexdigest()}
                with gzip.open(meta.captura['path'], 'wb') as g:
                    g.write(b'{}')
                with patch.object(f, 'obter_metadados', return_value=(info['urn'], meta)), patch.object(f, 'http_get', return_value=(200, html.encode())):
                    status, _, detalhe = f.processar(d)
                self.assertEqual(status, esperado)
                if esperado == 'ok':
                    md = Path(info['md']).read_text(encoding='utf-8')
                    self.assertIn('data: 1951-12-20', md)
                    self.assertIn('data_na_epigrafe_da_fonte: "1951-09-20"', md)
                    self.assertIn('DECRETO Nº 30.301, DE 20 DE SETEMBRO DE 1951.', md)  # a redação da fonte fica
                else:
                    self.assertIn('diverge', detalhe['motivo'])
                    self.assertFalse(Path(info['md']).exists())

    def test_visual_fora_tabela_e_em_comentario_condicional(self):
        from preparar_lote_decretos_cache import Visivel
        for html in ['<p>Anexo</p><img src="anexo.png">',
                     '<!--[if gte vml 1]><v:shape><v:imagedata src="anexo.wmz"/></v:shape><![endif]-->',
                     '<p>Fórmula</p><m:oMath>f</m:oMath>']:
            parser = Visivel()
            parser.feed(html)
            self.assertTrue(parser.visual, html)

    def test_comando_sem_artigos_exige_revisao(self):
        self.assertIsNotNone(f.motivo_texto_parcial_decreto('DEC-n', 'O PRESIDENTE faz públicos os depósitos.\n\nRio de Janeiro.'))


# Decretos de dispositivo único reais (normas.leg.br, 20/11/2026), recortados.
REPUBLICA = ('DECRETO N. 17.168 – DE 23 DE DEZEMBRO DE 1925\n\nAbre ao Ministerio da Fazenda o credito especial de réis 58:374$918, '
             'para pagamento a Alberto Chagas, em virtude de sentença judiciaria\n\nO Presidente da Republica dos Estados Unidos do '
             'Brasil, usando da autorização contida no decreto legislativo n. 4.968, de 20 de outubro ultimo, resolve abrir, ao '
             'Ministerio da Fazenda, o credito especial de 58:374$918, para pagamento a Alberto Chagas.\n\nRio de Janeiro, 23 de '
             'dezembro de 1925, 104º da Independencia e 37º da Republica.\n\nARTHUR DA SILVA BERNARDES.\n\nAnnibal Freire da Fonseca.')
IMPERIO = ('**DECRETO N. 10.339 - DE 6 DE SETEMBRO DE 1889**\n\n***Deroga o Decreto n. 10.083 de 24 de Novembro de 1888 na parte '
           'referente á comarca da Constituição, na Provincia de S. Paulo.***\n\nHei por bem Derogar o Decreto n. 10.083 de 24 de '
           'Novembro do anno findo, na parte em que declarou especial a comarca da Constituição.\n\nCandido Luiz Maria de Oliveira, '
           'Ministro e Secretario de Estado dos Negocios da Justiça, assim o tenha entendido e faça executar. Palacio do Rio de '
           'Janeiro em 6 de Setembro de 1889, 68º da Independencia e do Imperio.\n\nCom a rubrica de Sua Magestade o Imperador.\n\n'
           'Candido Luiz Maria de Oliveira.')
PROVISORIO = ('**DECRETO N. 1309 - DE 17 DE JANEIRO DE 1891**\n\n***Concede permissão a Manoel Augusto Pereira de Amorim para '
              'estabelecer centros telephonicos.***\n\nO Chefe do Governo Provisorio da Republica dos Estados Unidos do Brazil, '
              'considerando que a concessão é de incontestavel vantagem:\n\nResolve fazer-lhe a referida concessão, mediante as '
              'seguintes clausulas:\n\nI\n\nO prazo da concessão é de 15 annos.\n\nO Ministro e Secretario de Estado dos Negocios '
              'da Instrucção Publica assim o faça executar.\n\nPalacio do Governo Provisorio, 17 de janeiro de 1891, 3º da '
              'Republica.\n\n**MANOEL DEODORO DA FONSECA.**\n\nBenjamin Constant Botelho de Magalhães.')

# Decretos de publicação, como estão na fonte. O de 1921 traz a nota depois das assinaturas; o de 1931 não cita nota;
# o de 1955 e o de 1898 dizem que ela os acompanha e a transcrição não a traz.
PUBLICA_COM_NOTA = (
    'DECRETO N. 15.161 – DE 7 DE DEZEMBRO DE 1921\n\nPublica a denuncia, pelos Estados Unidos da America, da Convenção '
    'Sanitaria de Paris, de 1903\n\nO Presidente da Republica dos Estados Unidos do Brasil, faz publica a denuncia, feita '
    'pelo Governo dos Estados Unidos da America, da Convenção Sanitaria Internacional, assignada em Paris a 3 de dezembro '
    'de 1903, conforme communicou ao Ministerio das Relações Exteriores a Embaixada Franceza nesta Capital, por Nota de 29 '
    'de Novembro ultimo, cuja traducção official acompanha o presente decreto.\n\nRio de Janeiro, 7 de Dezembro de 1921, '
    '100º da Independencia e 33º da Republica.\n\nEpitacio pessôa.\n\nAzevedo Marques.\n\nTRADUCÇÃO\n\nEmbaixada da '
    'Republica Franceza no Brasil – Rio de Janeiro, 29 de Novembro de 1921.\n\nSenhor Ministro:\n\nA Embaixada dos Estados '
    'Unidos acaba de participar ao meu Governo que o Governo dos Estados Unidos decidiu denunciar a Convenção Sanitaria '
    'assignada em Paris a 3 de Dezembro de 1903. Aquelle Governo entende que essa Convenção contém muitas lacunas e que não '
    'corresponde mais aos progressos que têm sido feitos, durante os ultimos annos, no dominio da Hygiene publica.\n\n'
    'Essa denuncia produzirá effeito a partir de 22 de Abril de 1922.\n\nQueira acceitar, Senhor Ministro, a segurança da '
    'minha alta consideração.\n\nA. R. Conty.')
PUBLICA_SEM_NOTA = (
    'DECRETO N. 20.287 – DE 11 DE AGOSTO dE 1931\n\nFaz pública a adesão de diversas Colônias, Protetorados e Territórios '
    'sob mandato da Grã-Bretanha, à Convenção Internacional sobre circulação de automoveis, assinada em París a 24 de abril '
    'de 1926\n\nO Chefe do Governo Provisório da República dos Estados Unidos do Brasil faz pública a adesão das Colônias, '
    'Protetorados e Territórios sob o mandato da Grã-Bretanha, abaixo mencionados, à Convenção Internacional relativa à '
    'circulação de automoveis, assinada em París a 24 de abril de 1926, segundo comunicação feita pelo Governo Francês à '
    'Embaixada do Brasil naquela capital; Colônia e Protetorado de Kenya, Protetorado de Uganda, Chipre, Hong-Kong.\n\n'
    'Rio de Janeiro. 11 de agosto de 1931, 110º da Independência e 43º da República.\n\nGetulio Vargas.\n\n'
    'A. de Mello Franco.')
TORNA_PUBLICO_NOTA_AUSENTE = (
    'Decreto nº 37.774, de 18 de agôsto de 1955.\n\nTorna público o depósito dos instrumentos de aceitação, por parte dos '
    'Govêrnos do Paraguai e da Etiópia da Constituição da Organização das Nações Unidas para a Educação, Ciência e Cultura, '
    'concluída em Londres a 16 de novembro de 1945.\n\n**O PRESIDENTE DA REPÚBLICA DOS ESTADOS UNIDOS DO BRASIL**, torna '
    'público que os Govêrnos do Paraguai e da Etiópia depositaram nos arquivos do Govêrno do Reino Unido da Grã-Bretanha e '
    'Irlanda do Norte, a 20 de junho e a 1º de julho de 1955, respectivamente, os Instrumentos de aceitação da Constituição '
    'da Organização das Nações Unidas para a Educação, Ciência e Cultura, assinada em Londres, a 16 de novembro de 1945, nos '
    'têrmos da comunicação feita pela Embaixada da Grã-Bretanha ao Govêrno brasileiro, a 9 de agôsto de 1955, apensa por '
    'cópia ao presente Decreto.\n\nRio de Janeiro, 18 de agôsto de 1955; 134º da Independência e 67º da República.\n\n'
    'João Café Filho\n\nRaul Fernandes')
FAZ_PUBLICA_NOTA_AUSENTE = (
    'DECRETO N. 2909 – DE 13 DE JUNHO DE 1898\n\nPublica a adhesão do Estado Livre de Orange á Convenção Postal Universal de '
    'Washington de 15 de junho de 1897.\n\nO Presidente da Republica dos Estados Unidos do Brazil faz publica a adhesão do '
    'Estado Livre de Orange á Convenção Postal Universal assignada em Washington em 15 de junho de 1897, segundo a '
    'communicação da Legação dos Estados Unidos da America de 8 do corrente ao Ministerio das Relações Exteriores, cuja '
    'traducção official este acompanha.\n\nCapital Federal, 13 de junho de 1898, 10º da Republica.\n\n'
    'PRUDENTE J. DE MORAES BARROS.\n\nDionisio E. de Castro Cerqueira.')


class DecretoDePublicacao(unittest.TestCase):
    def test_entra_com_a_nota_depois_do_fecho_ou_sem_citar_nota(self):
        for corpo, numero, data in [(PUBLICA_COM_NOTA, '15161', '1921-12-07'), (PUBLICA_SEM_NOTA, '20287', '1931-08-11')]:
            with self.subTest(numero):
                self.assertIsNone(f.motivo_texto_parcial_decreto('DEC-n', corpo, numero, data))

    def test_nota_que_acompanha_o_decreto_e_falta_na_transcricao_mantem_a_retencao(self):
        casos = {
            'apensa por cópia ao presente decreto': (TORNA_PUBLICO_NOTA_AUSENTE, '37774', '1955-08-18'),
            'cuja tradução oficial este acompanha': (FAZ_PUBLICA_NOTA_AUSENTE, '2909', '1898-06-13'),
            'nota cortada antes da tradução': (PUBLICA_COM_NOTA.split('\n\nTRADUCÇÃO')[0], '15161', '1921-12-07'),
            'só o rótulo da tradução': (PUBLICA_COM_NOTA.split('\n\nEmbaixada da Republica')[0], '15161', '1921-12-07'),
        }
        for caso, (corpo, numero, data) in casos.items():
            with self.subTest(caso):
                self.assertIn('Sem artigo', f.motivo_texto_parcial_decreto('DEC-n', corpo, numero, data))

    def test_as_demais_exigencias_do_dispositivo_unico_continuam(self):
        casos = {
            'fórmula só na ementa': (PUBLICA_SEM_NOTA.replace('do Brasil faz pública a adesão', 'do Brasil publica a adesão'), '20287', '1931-08-11'),
            'faço saber, da sanção de lei': (PUBLICA_SEM_NOTA.replace('do Brasil faz pública a adesão', 'do Brasil: Faço saber a adesão'), '20287', '1931-08-11'),
            'sem autoridade': (PUBLICA_SEM_NOTA.replace('O Chefe do Governo Provisório da República', 'O Ministro das Relações Exteriores'), '20287', '1931-08-11'),
            'data do fecho diferente da do índice': (PUBLICA_SEM_NOTA, '20287', '1931-08-12'),
            'número da epígrafe diferente do índice': (PUBLICA_SEM_NOTA, '20288', '1931-08-11'),
            'fecho sem a marca da era': (PUBLICA_SEM_NOTA.replace(', 110º da Independência e 43º da República', ''), '20287', '1931-08-11'),
            'sem número e data do índice': (PUBLICA_SEM_NOTA, None, None),
        }
        for caso, (corpo, numero, data) in casos.items():
            with self.subTest(caso):
                self.assertIn('Sem artigo', f.motivo_texto_parcial_decreto('DEC-n', corpo, numero, data))


class DispositivoUnico(unittest.TestCase):
    def test_decretos_de_dispositivo_unico_com_identidade_e_fecho_proprios_entram(self):
        for corpo, numero, data in [(REPUBLICA, '17168', '1925-12-23'), (IMPERIO, '10339', '1889-09-06'),
                                    (PROVISORIO, '1309', '1891-01-17')]:
            with self.subTest(numero):
                self.assertIsNone(f.motivo_texto_parcial_decreto('DEC-n', corpo, numero, data))

    def test_sem_numero_e_data_do_indice_continua_em_revisao(self):
        self.assertIn('Sem artigo', f.motivo_texto_parcial_decreto('DEC-n', REPUBLICA))

    def test_fecho_proprio_com_outro_trecho_depois_continua_valendo(self):
        corpo = REPUBLICA + '\n\nClausulas a que se refere o decreto n. 17.168\n\nI\n\nO pagamento será feito.\n\nRio de Janeiro, 23 de dezembro de 1925. – Annibal Freire.'
        self.assertIsNone(f.motivo_texto_parcial_decreto('DEC-n', corpo, '17168', '1925-12-23'))

    def test_cada_condicao_faltando_mantem_a_retencao(self):
        casos = {
            'data do fecho diferente da do índice': (REPUBLICA, '17168', '1925-12-22'),
            'número da epígrafe diferente do índice': (REPUBLICA, '17169', '1925-12-23'),
            'fecho sem a marca da era': (REPUBLICA.replace(', 104º da Independencia e 37º da Republica', ''), '17168', '1925-12-23'),
            'sem fórmula dispositiva': (REPUBLICA.replace('resolve abrir', 'abre'), '17168', '1925-12-23'),
            'sem autoridade que decreta': (REPUBLICA.replace('O Presidente da Republica dos Estados Unidos do Brasil', 'O Ministro'), '17168', '1925-12-23'),
            'sem epígrafe': (REPUBLICA.split('\n\n', 1)[1], '17168', '1925-12-23'),
            'fórmula só depois do fecho': (IMPERIO.replace('Hei por bem Derogar', 'Fica derogado') + '\n\nHei por bem.', '10339', '1889-09-06'),
        }
        for caso, (corpo, numero, data) in casos.items():
            with self.subTest(caso):
                self.assertIn('Sem artigo', f.motivo_texto_parcial_decreto('DEC-n', corpo, numero, data))

    def test_errata_continua_retida(self):
        corpo = 'DECRETO N. 17.168 – DE 23 DE DEZEMBRO DE 1925\n\nRETIFICAÇÃO\n\nOnde se lê 58:374$918, leia-se 58:374$919.'
        self.assertIn('retificação', f.motivo_texto_parcial_decreto('DEC-n', corpo, '17168', '1925-12-23'))


if __name__ == '__main__':
    unittest.main()
