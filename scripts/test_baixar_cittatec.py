import re
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from baixar_cittatec import separar_dispositivos


class SepararDispositivos(unittest.TestCase):
    def test_abre_paragrafo_antes_de_artigo_inciso_e_alinea(self):
        texto = ("promulgo a seguinte Lei:\nArt. 1º - Fica criado:\nI – o conselho;\nII - o fundo.\n"
                 "a) primeira;\nb) segunda.\n§ 1º Regra.\nParágrafo único. Outra.")
        self.assertEqual(separar_dispositivos(texto),
                         "promulgo a seguinte Lei:\n\nArt. 1º - Fica criado:\n\nI – o conselho;\n\nII - o fundo.\n\n"
                         "a) primeira;\n\nb) segunda.\n\n§ 1º Regra.\n\nParágrafo único. Outra.")

    def test_nao_parte_frase_nem_palavra_em_caixa_alta(self):
        texto = "nos termos do\nArt. 5º da Lei 123.\nconforme a Polícia.\nCIVIL - texto da linha."
        self.assertEqual(separar_dispositivos(texto), texto)

    def test_so_insere_espacos(self):
        texto = "Lei:\nArt. 1º Um.\nArt. 2º Dois.\n\nArt. 3º Três."
        novo = separar_dispositivos(texto)
        self.assertEqual(re.sub(r"\s", "", novo), re.sub(r"\s", "", texto))
        self.assertEqual(separar_dispositivos(novo), novo)


if __name__ == "__main__":
    unittest.main()
