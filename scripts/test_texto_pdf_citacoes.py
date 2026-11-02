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


class RotacaoDasPaginas(unittest.TestCase):
    """Scanner em paisagem grava a página com /Rotate 90: o OCR tem que ler a página girada como o leitor a vê."""
    PDF = (b"%%PDF-1.4\n1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n"
           b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n"
           b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] %s >> endobj\n"
           b"trailer << /Root 1 0 R >>\n%%%%EOF\n")

    def test_pdfinfo_informa_a_rotacao_de_cada_pagina(self):
        import os
        import shutil
        import tempfile
        from comum import rotacao_das_paginas
        if not shutil.which("pdfinfo"):
            self.skipTest("pdfinfo ausente")
        with tempfile.TemporaryDirectory() as tmp:
            for rotate, esperado in ((b"/Rotate 90", [90]), (b"", [0])):
                pdf = os.path.join(tmp, "a.pdf")
                with open(pdf, "wb") as f:
                    f.write(self.PDF % rotate)
                self.assertEqual(rotacao_das_paginas(pdf), esperado)


class ColunasDaPagina(unittest.TestCase):
    """Páginas de livro digitalizadas em dupla: duas colunas de texto separadas por uma calha, com ou sem sombra."""

    @staticmethod
    def pagina(largura=400, altura=600, colunas=((20, 180), (220, 380)), calha_cinza=255, cabecalho=None):
        """PGM sintético: linhas de texto são faixas de 4 px alternando tinta e papel, com letras simuladas por
        pixels alternados; `cabecalho` = (y0, y1) de uma faixa que atravessa a página inteira."""
        pixels = bytearray(b"\xff" * (largura * altura))
        for y in range(altura):
            for x0, x1 in colunas:
                if 40 <= y < altura - 40 and (y // 4) % 2 == 0:
                    for x in range(x0, x1):
                        pixels[y * largura + x] = 0 if (x // 3) % 2 == 0 else 255
            if cabecalho and cabecalho[0] <= y < cabecalho[1] and (y // 2) % 2 == 0:
                for x in range(10, largura - 10):
                    pixels[y * largura + x] = 0
        if calha_cinza != 255:
            for y in range(altura):
                for x in range(colunas[0][1] + 5, colunas[1][0] - 5):
                    pixels[y * largura + x] = calha_cinza
        return b"P5\n# teste\n%d %d\n255\n" % (largura, altura) + bytes(pixels)

    def test_le_pgm_binario(self):
        from comum import ler_pgm
        largura, altura, pixels = ler_pgm(self.pagina(largura=40, altura=30, colunas=((2, 18), (22, 38))))
        self.assertEqual((largura, altura, len(pixels)), (40, 30, 1200))

    def test_duas_colunas_com_calha_clara(self):
        from comum import detectar_colunas
        layout = detectar_colunas(self.pagina())
        self.assertIsNotNone(layout)
        x0, x1 = layout["calha"]
        self.assertTrue(175 <= x0 <= 185 and 215 <= x1 <= 225, layout)
        self.assertEqual((layout["topo"], layout["base"]), (0, 600))

    def test_sombra_da_encadernacao_na_calha_nao_atrapalha(self):
        from comum import detectar_colunas
        layout = detectar_colunas(self.pagina(calha_cinza=40))
        self.assertIsNotNone(layout)
        self.assertTrue(175 <= layout["calha"][0] <= 190 and 210 <= layout["calha"][1] <= 225, layout)

    def test_cabecalho_que_atravessa_as_colunas_fica_fora(self):
        from comum import detectar_colunas
        layout = detectar_colunas(self.pagina(cabecalho=(12, 28)))
        self.assertIsNotNone(layout)
        self.assertTrue(28 <= layout["topo"] <= 40, layout)

    def test_numero_de_pagina_na_borda_da_coluna_sai(self):
        from comum import sem_numero_de_pagina_nas_bordas
        self.assertEqual(sem_numero_de_pagina_nas_bordas("— 43 —\nArt. 1.° — Texto.\nCampinas, 1909.\n- 44 -\n"), "Art. 1.° — Texto.\nCampinas, 1909.")
        # no meio do texto a linha fica: pode ser dispositivo ou valor
        self.assertEqual(sem_numero_de_pagina_nas_bordas("Art. 1.° — Texto.\n- 44 -\nArt. 2.° — Mais."), "Art. 1.° — Texto.\n- 44 -\nArt. 2.° — Mais.")

    def test_uma_coluna_so_e_texto_atravessando_o_meio_nao_sao_colunas(self):
        from comum import detectar_colunas
        self.assertIsNone(detectar_colunas(self.pagina(colunas=((20, 380),))))
        # metade das linhas atravessa a calha: não é layout de duas colunas
        self.assertIsNone(detectar_colunas(self.pagina(cabecalho=(100, 400))))
        # texto só de um lado
        self.assertIsNone(detectar_colunas(self.pagina(colunas=((20, 180),))))


if __name__ == "__main__":
    unittest.main()
