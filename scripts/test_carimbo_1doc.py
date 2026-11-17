"""Testes do carimbo de assinatura 1Doc (comum.texto_pdf_sem_carimbo_1doc) e da identidade do anexo em Jarinu.

Os PDFs são montados aqui mesmo: corpo em linhas horizontais e o carimbo em texto girado 90 graus na margem direita,
como a plataforma 1Doc o imprime. Precisa do `pdftotext` (poppler-utils).
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comum  # noqa: E402
import baixar_organicas_sapl as sapl  # noqa: E402

CORPO = [
    "LEI N 2.480 DE 09 DE OUTUBRO DE 2026",
    "Dispoe sobre abertura de Credito Suplementar por Anulacao de Dotacao",
    "FULANA DE TAL, Prefeita do Municipio de Jarinu, faz saber que a Camara Municipal aprovou e ela sanciona e promulga a",
    "presente Lei:",
    "Art. 1. Fica aberto um credito suplementar no valor de quinze mil reais as dotacoes do orcamento vigente.",
    "Art. 2. Esta Lei entra em vigor na data de sua publicacao.",
]
CARIMBO = [
    "Assinado por 2 pessoas: FULANO DE TAL e FULANA DE TAL",
    "Para verificar a validade das assinaturas, acesse https://jarinu.1doc.com.br/verificacao/9829-CFDB-A882-5954 e "
    "informe o codigo 9829-CFDB-A882-5954",
]


def pdf(linhas_corpo, linhas_carimbo, x_corpo=40, avulsas=()):
    """Uma página A4: o corpo em Helvetica 9 a partir de x_corpo, cada linha do carimbo girada 90 graus perto da borda
    direita, subindo de baixo para cima, e as palavras `avulsas` (x, y, texto) na horizontal onde se pedir."""
    def esc(t):
        return t.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    partes = ["BT /F1 9 Tf"]
    y = 780
    for linha in linhas_corpo:
        partes.append(f"1 0 0 1 {x_corpo} {y} Tm ({esc(linha)}) Tj")
        y -= 14
    for x, y_avulsa, texto in avulsas:
        partes.append(f"1 0 0 1 {x} {y_avulsa} Tm ({esc(texto)}) Tj")
    for i, linha in enumerate(linhas_carimbo):
        partes.append(f"/F1 6 Tf 0 1 -1 0 {560 + 9 * i} 60 Tm ({esc(linha)}) Tj /F1 9 Tf")
    partes.append("ET")
    fluxo = "\n".join(partes).encode("latin-1")
    objetos = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595.32 841.92] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>",
        b"<< /Length " + str(len(fluxo)).encode() + b" >>\nstream\n" + fluxo + b"\nendstream",
    ]
    saida = bytearray(b"%PDF-1.4\n")
    posicoes = []
    for n, obj in enumerate(objetos, 1):
        posicoes.append(len(saida))
        saida += f"{n} 0 obj\n".encode() + obj + b"\nendobj\n"
    xref = len(saida)
    saida += f"xref\n0 {len(objetos) + 1}\n0000000000 65535 f \n".encode()
    for p in posicoes:
        saida += f"{p:010d} 00000 n \n".encode()
    saida += f"trailer\n<< /Size {len(objetos) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
    return bytes(saida)


class Carimbo1Doc(unittest.TestCase):
    def test_carimbo_sai_e_o_paragrafo_fica_inteiro(self):
        corpo, motivo = comum.documento_para_md(pdf(CORPO, CARIMBO), "lei.pdf", carimbo_1doc=True)
        self.assertIsNone(motivo)
        self.assertNotIn("Assinado por", corpo)
        self.assertNotIn("1doc", corpo)
        self.assertIn("ela sanciona e promulga a presente Lei:", corpo)
        self.assertIn("Art. 2.", corpo)

    def test_carimbo_do_sistema_da_camara_tambem_sai(self):
        camara = ["ASSINADO POR $ASSINANTE$ - $DATAHORAASSINATURA$ - 703F-05ZZ-3B0X-1MVE"]
        corpo, motivo = comum.documento_para_md(pdf(CORPO, camara), "lei.pdf", carimbo_1doc=True)
        self.assertIsNone(motivo)
        self.assertNotIn("ASSINANTE", corpo)
        self.assertIn("ela sanciona e promulga a presente Lei:", corpo)

    def test_sem_a_opcao_nada_muda(self):
        corpo, motivo = comum.documento_para_md(pdf(CORPO, CARIMBO), "lei.pdf")
        self.assertIsNone(motivo)
        self.assertIn("1doc.com.br/verificacao", corpo)

    def test_documento_sem_carimbo_passa_igual(self):
        com, _ = comum.documento_para_md(pdf(CORPO, []), "lei.pdf", carimbo_1doc=True)
        sem, _ = comum.documento_para_md(pdf(CORPO, []), "lei.pdf")
        self.assertEqual(com, sem)

    def test_corpo_que_invade_a_faixa_do_carimbo_e_recusado(self):
        corpo, motivo = comum.documento_para_md(pdf(CORPO, CARIMBO, avulsas=[(552, 700, "palavra")]), "lei.pdf", carimbo_1doc=True)
        self.assertIsNone(corpo)
        self.assertIn("faixa do carimbo 1Doc", motivo)


class IdentidadeDoAnexo(unittest.TestCase):
    def test_jarinu_exige_a_epigrafe_propria(self):
        self.assertIn("sapl.jarinu.sp.leg.br", sapl.HOSTS_EPIGRAFE_PROPRIA)
        self.assertIn("sapl.jarinu.sp.leg.br", sapl.HOSTS_CARIMBO_1DOC)
        lei = "LEI N° 2.480 DE 09 DE OUTUBRO DE 2026\n\nDispõe sobre abertura de Crédito Suplementar\n"
        self.assertTrue(sapl.abre_com_a_propria_epigrafe(lei, "Lei Ordinária", "2480"))
        # a ficha do Decreto Legislativo 17/2026 anexava o Ofício Legislativo nº 17/2026
        oficio = "Câmara Municipal de Jarinu\n\nOfício Legislativo n° 17/2026\n\nJarinu, em 3 de junho de 2026\n"
        self.assertFalse(sapl.abre_com_a_propria_epigrafe(oficio, "Decreto Legislativo", "17"))

    def test_ficha_importada_com_data_provisoria(self):
        importada = {"ementa": "Documento importado do acervo historico - Decreto Legislativo 24/2026", "data": "2026-01-01"}
        self.assertTrue(sapl.ficha_importada_com_data_provisoria(importada))
        self.assertTrue(sapl.ficha_importada_com_data_provisoria({"ementa": "Aprova as contas", "observacao": "Importado de DL4_2025.pdf",
                                                                   "data": "2025-01-01"}))
        # importada, mas com data real: segue para as outras conferências
        self.assertFalse(sapl.ficha_importada_com_data_provisoria({**importada, "data": "2026-06-02"}))
        self.assertFalse(sapl.ficha_importada_com_data_provisoria({"ementa": "Autoriza o pacto de amizade", "data": "2026-01-01"}))


if __name__ == "__main__":
    unittest.main()
