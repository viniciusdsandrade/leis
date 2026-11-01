"""O cabeçalho institucional das páginas da ALESP sai do corpo, inclusive o link para a outra versão do texto."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import sp  # noqa: E402
from comum import html_para_md  # noqa: E402

PAGINA = ("<html><body><a href='https://www.al.sp.gov.br'>Assembleia Legislativa do Estado de S&atilde;o Paulo</a> "
          "<a href='/norma/201949'>Ficha informativa</a><br /> <a href='constituicao-0-09.07.1947.html'>{versao}</a> "
          "<h1>CONSTITUI&Ccedil;&Atilde;O ESTADUAL, DE 09 DE JULHO DE 1947</h1> "
          "<p>O povo paulista decreta e promulga a seguinte Constitui&ccedil;&atilde;o.</p></body></html>")


class CabecalhoAlesp(unittest.TestCase):
    def test_remove_cabecalho_com_link_para_outra_versao(self):
        for versao in ("Texto com alterações", "Texto compilado"):
            with self.subTest(versao=versao):
                corpo = html_para_md(PAGINA.format(versao=versao), sp.CABECALHO)
                self.assertNotIn("Ficha informativa", corpo)
                self.assertNotIn(versao, corpo)
                self.assertNotIn("Assembleia Legislativa do Estado de São Paulo\n", corpo)
                self.assertTrue(corpo.lstrip("# ").startswith("CONSTITUIÇÃO ESTADUAL, DE 09 DE JULHO DE 1947"), corpo[:120])
                self.assertIn("O povo paulista decreta", corpo)


if __name__ == "__main__":
    unittest.main()
