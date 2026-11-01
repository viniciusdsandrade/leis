"""Emendas sem artigo inicial devem conservar promulgação e vigência explícitas."""
from pathlib import Path
import unittest
import hashlib
import json
import tempfile

from baixar_organicas_sapl import (categoria_norma, corpo_integral_reconhecivel, data_da_epigrafe, data_diverge_do_ano,
                                   motivo_retencao, titulo_com_data)
from comum import documento_para_md


class IntegralidadeSAPLTest(unittest.TestCase):
    def test_alias_loman_e_delegada_nao_vira_ordinaria(self):
        self.assertEqual(categoria_norma('Loman')[0], 'lei-organica')
        self.assertEqual(categoria_norma('Emenda à Loman')[0], 'emendas-lei-organica')
        self.assertIsNone(categoria_norma('Lei Delegada'))
        self.assertIsNone(categoria_norma('Projeto de Lei Ordinária'))
        self.assertEqual(categoria_norma('Leis Até 1948'), ('leis-ordinarias', 'Lei ordinária'))
        self.assertIsNone(categoria_norma('Leis Delegadas'))
        self.assertEqual(categoria_norma('Resoluções Até 1948'), ('resolucoes', 'Resolução'))
        self.assertEqual(categoria_norma('Decreto-lei'), ('decretos', 'Decreto-Lei'))
        self.assertEqual(categoria_norma('Decretos Até 1948'), ('decretos', 'Decreto'))

    def test_retencao_so_se_aplica_aos_bytes_revisados(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp)
            bruto = b'diario com colunas misturadas'
            (cache / 'retidos-integralidade.json').write_text(json.dumps({'1': {
                'sha256_fonte': hashlib.sha256(bruto).hexdigest(), 'motivo': 'rever separação'}}))
            self.assertEqual(motivo_retencao(cache, 1, bruto), 'rever separação')
            self.assertIsNone(motivo_retencao(cache, 1, b'novos bytes oficiais'))
            self.assertIsNone(motivo_retencao(cache, 2, bruto))

    def test_antigo_1_do_ocr_vale_como_rotulo_so_no_comeco_da_linha(self):
        base = "LEI Nº 6283 DE 28 DE SETEMBRO DE 1990\nA Câmara Municipal aprovou e eu, Prefeito, sanciono a seguinte lei:\n"
        self.assertTrue(corpo_integral_reconhecivel(base + "Antigo 1º \u00ad Fica denominada a Rua 96."))
        self.assertTrue(corpo_integral_reconhecivel(base + "Antigo 1º - Fica instituído o Conselho."))
        self.assertFalse(corpo_integral_reconhecivel(base + "Fica criado no antigo 1º - Distrito o posto."))
        self.assertFalse(corpo_integral_reconhecivel(base + "Antigo 1º Distrito de Campinas passa a bairro."))

    def test_texto_de_outra_norma_le_o_registro_por_host_e_id(self):
        import baixar_organicas_sapl as b
        with tempfile.TemporaryDirectory() as tmp:
            reg = Path(tmp) / "reg.json"
            reg.write_text(json.dumps({"sapl.x.leg.br": {"10": {"id_fonte": 11, "texto_integral": "https://sapl.x.leg.br/a.pdf",
                                                                 "sha256_fonte": "ab", "nota": "n"}}}))
            original, b.TEXTO_DE_OUTRA_NORMA = b.TEXTO_DE_OUTRA_NORMA, reg
            try:
                self.assertEqual(b.texto_de_outra_norma("sapl.x.leg.br", 10)["id_fonte"], 11)
                self.assertIsNone(b.texto_de_outra_norma("sapl.x.leg.br", 11))
                self.assertIsNone(b.texto_de_outra_norma("sapl.y.leg.br", 10))
            finally:
                b.TEXTO_DE_OUTRA_NORMA = original

    def test_data_do_cadastro_de_outro_ano_e_retida(self):
        # Campinas, Lei 11.551: data "2000-03-05" no cadastro, ano 2003, publicada em 2003-05-13
        self.assertTrue(data_diverge_do_ano({'data': '2000-03-05', 'ano': 2003, 'data_publicacao': '2003-05-13'}))
        self.assertFalse(data_diverge_do_ano({'data': '2003-05-12', 'ano': 2003, 'data_publicacao': '2003-05-13'}))
        # lei de fim de ano publicada no ano seguinte não é erro
        self.assertFalse(data_diverge_do_ano({'data': '2002-12-30', 'ano': 2002, 'data_publicacao': '2003-01-02'}))
        # sem publicação para confirmar, não há como saber qual campo está errado
        self.assertFalse(data_diverge_do_ano({'data': '2002-03-14', 'ano': 2003, 'data_publicacao': None}))
        self.assertFalse(data_diverge_do_ano({'data': '', 'ano': 1990}))

    def test_rotulo_do_primeiro_artigo_com_erro_de_digitacao(self):
        self.assertTrue(corpo_integral_reconhecivel("DECRETA:\n\nArti. 1º Fica aberto um crédito."))
        self.assertTrue(corpo_integral_reconhecivel("DECRETA:\n\nArt . 1° Ficam revalidadas."))
        self.assertFalse(corpo_integral_reconhecivel("DECRETA:\n\n**Artigo 2º** - O Crédito aberto pelo artigo anterior."))

    def test_ocr_le_artigo_1_como_19_so_depois_da_formula_de_promulgacao(self):
        ocr = "> Texto obtido por OCR a partir de PDF escaneado; pode conter erros de reconhecimento.\n\n"
        base = (ocr + "DECRETO LEGISLATIVO N° 304 DE 11 DE NOVEMBRO DE 1991 CONCEDE A MEDALHA\n\n"
                "A Câmara Municipal aprovou e eu, seu Presidente, promulgo o seguinte Decreto Legislativo:\n\n")
        self.assertTrue(corpo_integral_reconhecivel(base + "Artigo 19 - Fica concedida a Medalha."))
        self.assertTrue(corpo_integral_reconhecivel(base + "Artigo 10- Fica concedida a Medalha."))
        self.assertTrue(corpo_integral_reconhecivel(ocr + "A CAMARA MUNICIPAL RESOLVE: Atigo 1.o - O Artigo 4.o passa a ter nova redação."))
        # sem a fórmula de promulgação antes, ou sem o aviso de OCR, "Artigo 19" é o décimo nono artigo
        self.assertFalse(corpo_integral_reconhecivel(ocr + "CONCEDE A MEDALHA\n\nArtigo 19 - Fica concedida a Medalha."))
        self.assertFalse(corpo_integral_reconhecivel(base.replace(ocr, "") + "Artigo 19 - Fica concedida a Medalha."))
        # texto que começa no meio: o primeiro rótulo é de outro artigo
        self.assertFalse(corpo_integral_reconhecivel(base + "Artigo 12 - Texto.\n\nArtigo 19 - Fica."))

    def test_data_da_epigrafe_corrige_ano_errado_do_cadastro(self):
        corpo = "Publicada no Diário Oficial do Município de Campinas em 15/03/2003\n\nLEI Nº. 11.481 DE 14 DE MARÇO DE 2003 DISPÕE SOBRE"
        norma = {'data': '2002-03-14', 'ano': 2003, 'data_publicacao': '2003-03-15'}
        self.assertEqual(data_da_epigrafe(corpo, norma), '2003-03-14')
        # ano da epígrafe diferente do ano da norma, ou publicação longe da data: não corrige
        self.assertIsNone(data_da_epigrafe(corpo.replace('DE 2003', 'DE 2002'), norma))
        self.assertIsNone(data_da_epigrafe(corpo, {**norma, 'data_publicacao': '2003-09-15'}))
        self.assertIsNone(data_da_epigrafe(corpo, {**norma, 'data_publicacao': None}))
        self.assertIsNone(data_da_epigrafe("Publicada em 15/03/2003\n\nLEI Nº 11.481 DISPÕE SOBRE", norma))
        self.assertEqual(titulo_com_data("Lei nº 11.481, de 14 de março de 2002", "2003-03-14"), "Lei nº 11.481, de 14 de março de 2003")
        self.assertEqual(titulo_com_data("Decreto Legislativo nº 3.591, de 16 de maio de 13", "2013-05-16"),
                         "Decreto Legislativo nº 3.591, de 16 de maio de 2013")

    def test_promulgacao_em_terceira_pessoa_sem_adivinhar_artigo_um(self):
        base = 'EMENDA À LEI ORGÂNICA\nA Mesa PROMULGA a seguinte emenda.\nArt. 29. ' + 'Disposição material. ' * 40 + '\nArt. 2º Esta Emenda entra em vigor na data de publicação.'
        self.assertTrue(corpo_integral_reconhecivel(base, emenda=True))
        self.assertTrue(corpo_integral_reconhecivel(base.replace('PROMULGA', 'PROMULGAM'), emenda=True))
        self.assertFalse(corpo_integral_reconhecivel(base, emenda=False))
        self.assertFalse(corpo_integral_reconhecivel(base.replace('PROMULGA', 'propõe'), emenda=True))
        self.assertFalse(corpo_integral_reconhecivel(base.replace('vigor', 'observação'), emenda=True))

    def test_emenda_63_portovelho_cache_real_quando_disponivel(self):
        p = Path(__file__).resolve().parent.parent / 'municipais/_fonte/organicas-sapl/sapl.portovelho.ro.leg.br/13492.bin'
        if not p.exists():
            self.skipTest('captura oficial local não distribuída no Git')
        corpo, motivo = documento_para_md(p.read_bytes(), 'https://sapl.portovelho.ro.leg.br/media/emenda.pdf')
        self.assertIsNone(motivo)
        self.assertIn('PROMULGA', corpo)
        self.assertTrue(corpo_integral_reconhecivel(corpo, emenda=True))


if __name__ == '__main__':
    unittest.main()
