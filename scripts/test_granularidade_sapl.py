"""Granularidade: referências não equivalem a epígrafes de outros atos."""
from pathlib import Path
import unittest
from granularidade_sapl import alertas_multiplos_atos, alertas_outras_publicacoes


class GranularidadeSAPLTest(unittest.TestCase):
    def test_aviso_edital_caceres_nao_exige_epigrafe_de_lei(self):
        s='Art.111. Outorga de concessão. EDITAL DISPONÍVEL NO SITE DA CÂMARA MUNICIPAL.\nABERTURA DA SESSÃO: dia15.'
        self.assertEqual(len(alertas_outras_publicacoes(s)),2)
        self.assertEqual(alertas_multiplos_atos(s,'Emenda à Lei Orgânica','52'),[])

    def test_referencia_generica_a_edital_nao_e_aviso_especifico(self):
        self.assertEqual(alertas_outras_publicacoes('Art.1º O edital da licitação observará os requisitos legais.'),[])
    def test_propria_epigrafe_repetida_e_pontuacao(self):
        s = 'EMENDA À LOMAN N. 121, DE 13 DE AGOSTO DE 2025\n\nEMENDA À LOMAN Nº 121/2025\n'
        self.assertEqual(alertas_multiplos_atos(s, 'Emenda à Loman', '121'), [])

    def test_referencias_corridas_e_citacoes_nao_sao_epigrafes(self):
        s = 'Conforme a LEI N° 1.265/2008 e a Portaria nº 65/2025.\n\n“LEI Nº 1.265/2008”\n\nA Lei Complementar Nacional nº 101/2000 estabelece limites.'
        self.assertEqual(alertas_multiplos_atos(s, 'Emenda à Lei Orgânica', '121'), [])

    def test_epigrafes_alheias_retem_sem_cortar(self):
        s = 'PORTARIA N° 065/2025\nNomeia servidor.\n\nLEI N. 1.265, DE 10 DE NOVEMBRO DE 2008\nArt. 1º Texto.\n\nPORTARIA N° 065/2025'
        r = alertas_multiplos_atos(s, 'Emenda à Lei Orgânica', '121')
        self.assertEqual([tuple(x['epigrafe_diversa']) for x in r], [('PORTARIA', '65'), ('LEI', '1265')])
        self.assertEqual(s[r[0]['posicao_no_corpo']:][:8], 'PORTARIA')

    def test_epigrafe_sem_marcador_numero_e_municipal(self):
        s = 'LEI MUNICIPAL 1.265, DE 10 DE NOVEMBRO DE 2008\n\nDECRETO MUNICIPAL Nº 65/2025'
        r = alertas_multiplos_atos(s, 'Lei', '1265')
        self.assertEqual([tuple(x['epigrafe_diversa']) for x in r], [('DECRETO', '65')])

    def test_epigrafe_antiga_sem_data_dos_livros_de_campinas(self):
        s = ('LEI N. 287 ( Declara de utilidade publica os predios ns. 77, 79)\n\n**Art. 1.°** — São considerados.\n\n'
             'LEI N. 288 ( Considera feriados os dias 8 e 9 de Setembro)\n\n**Art. 1.°** - Ficam considerados feriados.\n\n'
             'LEI N. 439 DETERNINANDO E\'POCA PARA ARRECADAÇÃO DE IMPOSTOS\n\nLei n. 133 (Creando os impostos)')
        r = alertas_multiplos_atos(s, 'Leis Até 1948', '287')
        self.assertEqual([tuple(x['epigrafe_diversa']) for x in r], [('LEI', '288'), ('LEI', '439'), ('LEI', '133')])
        r = alertas_multiplos_atos('DECRETO N. 121, de 1946 Aprova loteamento de terrenos', 'Decretos Até 1948', '349')
        self.assertEqual([tuple(x['epigrafe_diversa']) for x in r], [('DECRETO', '121')])
        r = alertas_multiplos_atos('Decreto-Lei N. 96 (Dando denominação)\n\nDecreto-Lei N. 97 0$000 Aprova loteamento', 'Decreto-lei', '96')
        self.assertEqual([tuple(x['epigrafe_diversa']) for x in r], [('DECRETO-LEI', '97')])

    def test_epigrafe_antiga_com_n_minusculo(self):
        # livros de 1913 e de 1891: "Lei n. 183", "Resolução n. 45"; a citação moderna usa "nº"
        r = alertas_multiplos_atos('Lei n. 183 Heitor Teixeira Penteado\n\nResolução n. 45 Fica elevado a 2$500', 'Leis Até 1948', '182')
        self.assertEqual([tuple(x['epigrafe_diversa']) for x in r], [('LEI', '183'), ('RESOLUCAO', '45')])
        self.assertEqual(alertas_multiplos_atos('Lei nº 183, de 2 de maio de 1913, e alterações', 'Leis Até 1948', '182'), [])

    def test_tipo_no_plural_e_decreto_lei_tem_identidade_propria(self):
        self.assertEqual(alertas_multiplos_atos('RESOLUÇÃO N. 990 (Faz doação de terreno ao Estado)', 'Resoluções Até 1948', '990'), [])
        r = alertas_multiplos_atos('Decreto-Lei N. 102 (Abrindo créditos)\n\nLEI N. 102 (Orça a receita)', 'Decreto-lei', '102')
        self.assertEqual([tuple(x['epigrafe_diversa']) for x in r], [('LEI', '102')])

    def test_citacao_moderna_em_comeco_de_linha_nao_e_epigrafe_antiga(self):
        s = ('Lei nº 6.309, de 1988, e alterações posteriores) Médico Clínico Geral\n\n'
             'Lei nº 8.666 (Lei de Licitações) e demais normas\n\nDecreto nº 18.757, de 2015, e alterações posteriores')
        self.assertEqual(alertas_multiplos_atos(s, 'Lei Complementar', '677'), [])

    def test_citacao_que_continua_a_frase_do_paragrafo_anterior_nao_e_epigrafe(self):
        s = ('**Art. 2º** - O loteamento é submetido à Lei Federal nº 6.766, de 19 de dezembro de 1979, e\n\n'
             'Lei Municipal nº 10.410 de 17 de janeiro de 2000.\n\n**Art. 3º** - Texto.')
        self.assertEqual(alertas_multiplos_atos(s, 'Decreto', '13781'), [])
        s = 'para fim do disposto no art. 15 do Decreto-\n\nLei nº 3.365, de 21 de junho de 1941.'
        self.assertEqual(alertas_multiplos_atos(s, 'Decreto', '15779'), [])
        s = ('DISPÕE SOBRE AS TABELAS DE PREÇOS PÚBLICOS A QUE SE REFERE O\n\n'
             'DECRETO N° 11.063, DE 30 DE DEZEMBRO DE 1992, QUE APROVA O REGULAMENTO DOS TEATROS')
        self.assertEqual(alertas_multiplos_atos(s, 'Decreto', '14490'), [])

    def test_texto_citado_em_retificacao_nao_e_epigrafe(self):
        s = ('No art.1º, onde se lê:\n\nDecreto nº 13.497, de 4 de dezembro de 2002\n\nLeia-se\n\n'
             'Decreto nº 13.497, de 04 de dezembro de 2000')
        self.assertEqual(alertas_multiplos_atos(s, 'Decreto', '13956'), [])

    def test_lista_de_leis_citadas_em_caixa_mista_sem_abertura_de_ato(self):
        s = ('**Art. 1º** Ficam prorrogados os créditos autorizados pelas seguintes leis:\n\n'
             'Lei nº 3074, de 15 de julho de 1964 – “Cria o Fundo Especial”.\n\n'
             'Lei nº 3404, de 16 de dezembro de 1965 – “Abertura de crédito”.\n\n**Art. 2º** Esta lei entra em vigor.')
        self.assertEqual(alertas_multiplos_atos(s, 'Lei', '3552'), [])

    def test_segundo_ato_continua_retido(self):
        s = ('DECRETO Nº 13.816 DE 14 DE DEZEMBRO DE 2001 DISPÕE SOBRE ABERTURA DE CRÉDITO\n\n**Art. 1º** Fica aberto.\n\n'
             'Campinas, 14 de dezembro de 2001\n\nPrefeito Municipal\n\n'
             'Decreto nº 13.817 de 14 de dezembro de 2001 Permite o uso de bem público\n\nA Prefeita Municipal DECRETA:\n\n'
             '**Art. 1º** Fica permitido.')
        r = alertas_multiplos_atos(s, 'Decreto', '13816')
        self.assertEqual([tuple(x['epigrafe_diversa']) for x in r], [('DECRETO', '13817')])
        # em maiúsculas, o ato seguinte é retido mesmo sem a fórmula de promulgação no trecho
        s2 = 'Prefeito Municipal\n\nDECRETO Nº 13.817 DE 14 DE DEZEMBRO DE 2001 PERMITE O USO DE BEM PÚBLICO'
        self.assertEqual(len(alertas_multiplos_atos(s2, 'Decreto', '13816')), 1)
        # epígrafe dos livros antigos em caixa mista: o ato seguinte da página começa assim
        s3 = 'O Secretario, Amilar Alves.\n\nLei n. 133 (Creando os impostos de metros corridos)'
        self.assertEqual(len(alertas_multiplos_atos(s3, 'Leis Até 1948', '134')), 1)

    def test_epigrafe_com_o_minusculo_no_lugar_do_ordinal(self):
        # OCR das leis de 1973: "LEI N.o 4.264. DE 20 DE MARÇO DE 1.973." abre a página antes da lei própria
        s = 'LEI N.o 4.264. DE 20 DE MARÇO DE 1.973.\n\nLEI N.o 4267, DE 22 DE MARÇO DE 1.973. AUTORIZA A PERMUTA'
        self.assertEqual([tuple(x['epigrafe_diversa']) for x in alertas_multiplos_atos(s, 'Lei', '4267')], [('LEI', '4264')])

    def test_pagina_de_diario_em_duas_colunas_continua_retida(self):
        # a coluna corta a frase antes da epígrafe do ato seguinte, que abre a própria ementa em maiúsculas
        s = ('**Art. 9.º** Este Decreto entra em vigor na data de sua publicação, revogadas as\n\n'
             'DECRETO Nº 17.893 DE 28 DE FEVEREIRO DE 2013 ALTERA A REDAÇÃO DO DECRETO Nº 17.000')
        r = alertas_multiplos_atos(s, 'Decreto', '17892')
        self.assertEqual([tuple(x['epigrafe_diversa']) for x in r], [('DECRETO', '17893')])
        s = 'conforme a ordem de\n\nDECRETO Nº 17.827 DE 27 DE DEZEMBRO DE 2012\n\nDISCIPLINA A REALIZAÇÃO DO CARNAVAL'
        self.assertEqual(len(alertas_multiplos_atos(s, 'Decreto', '17826')), 1)
        # página de livro antigo com OCR: a epígrafe antiga do ato seguinte alerta mesmo depois de frase cortada
        s = 'para regularidade de alinhamento em via publica de\n\nLei n. 334 ( Autorizando a Prefeitura a receber terreno)'
        self.assertEqual(len(alertas_multiplos_atos(s, 'Leis Até 1948', '333')), 1)

    def test_frase_corrida_do_ato_nao_e_aviso_de_outra_publicacao(self):
        s = '**Art. 8º** - Até três dias úteis antes da data fixada para recebimento das propostas, qualquer pessoa poderá impugnar.'
        self.assertEqual(alertas_outras_publicacoes(s), [])
        self.assertEqual(alertas_outras_publicacoes('abertura da sessão, leitura, discussão e votação da ata.'), [])
        self.assertEqual(len(alertas_outras_publicacoes('Recebimento das Propostas dos itens 01 a 10: dia 5.')), 1)

    def test_manaus_121_anexo_real_quando_presente(self):
        p = Path(__file__).resolve().parent.parent / 'municipais/AM/manaus/emendas-lei-organica/2025/emendas-lei-organica-121-2025-sapl-8035.md'
        if not p.exists():
            self.skipTest('captura oficial local não distribuída no Git')
        s = p.read_text().split('\n---\n', 1)[1].lstrip('\n').split('\n\n', 1)[1]
        r = alertas_multiplos_atos(s, 'Emenda à Loman', '121')
        self.assertTrue(any(x['epigrafe_diversa'] == ('PORTARIA', '65') for x in r), r)
        self.assertTrue(all(x['epigrafe_diversa'] != ('EMENDA', '121') for x in r))


if __name__ == '__main__':
    unittest.main()
