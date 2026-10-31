"""Citação de outra norma quebrada na linha do PDF não pode abrir parágrafo novo."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import texto_pdf_para_md


class CitacaoQuebradaNaLinha(unittest.TestCase):
    def test_citacao_apos_preposicao_continua_a_frase(self):
        corpo = texto_pdf_para_md("Art. 6º O Conselho deve ser composto, nos termos da\n"
                                  "Lei nº 16.301, de 13 de outubro de 2022, de 24 conselheiros.\n")
        self.assertEqual(corpo.count("\n\n"), 0)
        self.assertIn("nos termos da Lei nº 16.301", corpo)

    def test_lista_de_leis_com_artigo_no_fim_da_linha(self):
        corpo = texto_pdf_para_md("Art. 1º Ficam revogadas a Lei nº 10.266, de 1999; a\n"
                                  "Lei nº 10.525, de 2000; a Lei nº 10.764, de 2001.\n")
        self.assertNotIn("\n\n", corpo.strip())

    def test_epigrafe_depois_de_ponto_final_abre_bloco(self):
        corpo = texto_pdf_para_md("Art. 2º Esta Lei entra em vigor.\nLEI Nº 5, DE 1 DE JANEIRO DE 2000\nArt. 1º Texto.\n")
        self.assertEqual(corpo.strip().count("\n\n"), 2)

    def test_ementa_em_maiusculas_que_termina_em_conectivo_continua(self):
        corpo = texto_pdf_para_md("REVOGA O ITEM 6 DO INCISO XIV DO ART. 27 DA\n"
                                  "LEI Nº 6.031, DE 28 DE DEZEMBRO DE 1988, QUE DISPÕE SOBRE O USO DO SOLO.\n")
        self.assertEqual(corpo.strip().count("\n\n"), 0)

    def test_letra_isolada_em_maiuscula_nao_e_conectivo(self):
        corpo = texto_pdf_para_md("ANEXO A\nANEXO B\n")
        self.assertEqual(corpo.strip().count("\n\n"), 1)

    def test_inciso_terminado_em_e_ainda_abre_novo_bloco(self):
        corpo = texto_pdf_para_md("Art. 3º Compete:\nI - fiscalizar; e\nII - julgar.\n")
        self.assertIn("\n\n", corpo.strip())
        self.assertEqual(corpo.strip().count("\n\n"), 2)


class CabecalhosERodapesBorda(unittest.TestCase):
    def test_cabecalho_repetido_no_topo_e_removido(self):
        corpo = texto_pdf_para_md("CÂMARA MUNICIPAL DE CAMPINAS\nArt. 1º Texto.\n\f"
                                  "CÂMARA MUNICIPAL DE CAMPINAS\nArt. 2º Mais texto.\n")
        self.assertNotIn("CÂMARA MUNICIPAL", corpo)
        self.assertIn("**Art. 1º** Texto.", corpo)
        self.assertIn("**Art. 2º** Mais texto.", corpo)

    def test_epigrafe_repetida_em_republicacao_preserva_primeira_ocorrencia(self):
        corpo = texto_pdf_para_md("LEI Nº 10.680, DE 13 DE NOVEMBRO DE 2000\nArt. 1º A.\n\f"
                                  "LEI Nº 10.680, DE 13 DE NOVEMBRO DE 2000\nArt. 1º A alterado.\n")
        self.assertEqual(corpo.count("LEI Nº 10.680"), 1)
        self.assertIn("**Art. 1º** A.", corpo)
        self.assertIn("**Art. 1º** A alterado.", corpo)

    def test_linha_repetida_no_meio_da_pagina_nao_e_removida(self):
        linhas = [f"Linha {i}" for i in range(12)] + ["Dotação orçamentária 01.02.03"] + [f"Linha {i}" for i in range(12, 24)]
        texto_pag = "\n".join(linhas)
        corpo = texto_pdf_para_md(f"{texto_pag}\n\f{texto_pag}\n")
        self.assertEqual(corpo.count("Dotação orçamentária 01.02.03"), 2)


if __name__ == "__main__":
    unittest.main()
