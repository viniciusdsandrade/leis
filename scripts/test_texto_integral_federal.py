"""Evita publicar errata avulsa como se fosse a norma integral."""
from pathlib import Path
import sys
import unittest
import tempfile
import gzip
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
            'sem fórmula dispositiva': (REPUBLICA.replace('resolve abrir', 'faz publico ter aberto'), '17168', '1925-12-23'),
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
