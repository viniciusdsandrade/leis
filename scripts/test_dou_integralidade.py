"""A trava de texto externo do DOU não dispara com "íntegra" como adjetivo; a data sai do título mesmo sem o "de" antes do mês."""
import unittest

import baixar_dou as dou
from datas import data_do_texto


class IntegraComoAdjetivo(unittest.TestCase):
    def test_adjetivo_nao_retem(self):
        corpo = ("§ 1º As informações da vistoria serão obrigatoriamente transmitidas pela integradora ao SISV, "
                 "de forma individualizada, íntegra e rastreável.\n\n"
                 "§ 2º O SISV disponibilizará automaticamente aos órgãos ou entidades executivos de trânsito "
                 "as informações e evidências relativas às vistorias.")
        self.assertEqual(dou.pendencia_integralidade(corpo), "")

    def test_substantivo_retem(self):
        for corpo in ("A íntegra desta Resolução encontra-se disponível no sítio eletrônico do Ministério.",
                      "O anexo foi publicado na íntegra no site www.gov.br/transportes.",
                      "O inteiro teor do processo consta da biblioteca digital.",
                      "Íntegra disponível em www.in.gov.br."):
            with self.subTest(corpo=corpo):
                self.assertTrue(dou.pendencia_integralidade(corpo).startswith("texto integral externo"))


class DataDoTituloDOU(unittest.TestCase):
    def test_titulo_sem_de_antes_do_mes(self):
        self.assertEqual(data_do_texto("RESOLUÇÃO CONTRAN Nº 1.032, DE 22 outubro DE 2026", linhas=1), "2026-10-22")
        self.assertEqual(dou.assinatura_do_ato("RESOLUÇÃO CONTRAN Nº 1.033, DE 22 outubro DE 2026", ""), "2026-10-22")

    def test_forma_tradicional_continua(self):
        self.assertEqual(data_do_texto("LEI Nº 14.133, DE 1º DE ABRIL DE 2021", linhas=1), "2021-04-01")
        self.assertIsNone(data_do_texto("RESOLUÇÃO CONTRAN Nº 1.033, DE 22 outubra DE 2026", linhas=1))


if __name__ == "__main__":
    unittest.main()
