"""O caminho PDF dos regimentos aceita `%PDF` com REGIMENTO e recusa casca JS."""
import contextlib
import io
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import baixar_jurisprudencia as coletor  # noqa: E402


class SemEspera:
    def esperar(self):
        pass


def pdf_com_texto(texto):
    """PDF mínimo cujo `pdftotext -layout` devolve `texto`. Sem dependência extra.

    A página é alta para o texto inteiro caber no MediaBox: o coletor usa `-layout`,
    que descarta o que cai fora de uma carta.
    """
    ops = ["BT", "/F1 10 Tf", "12 TL", "40 19900 Td"]
    for i in range(0, len(texto), 80):
        piece = texto[i:i + 80].replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        ops.append(f"({piece}) Tj")
        ops.append("T*")
    ops.append("ET")
    stream = ("\n".join(ops) + "\n").encode("latin-1", "replace")
    out = bytearray(b"%PDF-1.4\n")
    offsets = [0]

    def add(content):
        offsets.append(len(out))
        n = len(offsets) - 1
        out.extend(f"{n} 0 obj\n".encode())
        out.extend(content)
        if not content.endswith(b"\n"):
            out.extend(b"\n")
        out.extend(b"endobj\n")
        return n

    add(b"<< /Type /Catalog /Pages 2 0 R >>")
    add(b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>")
    add(b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 20000] /Contents 4 0 R "
        b"/Resources << /Font << /F1 5 0 R >> >> >>")
    add(b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"endstream")
    add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    xref = len(out)
    out.extend(f"xref\n0 {len(offsets)}\n".encode())
    out.extend(b"0000000000 65535 f \n")
    for off in offsets[1:]:
        out.extend(f"{off:010d} 00000 n \n".encode())
    out.extend(f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode())
    return bytes(out)


class RegimentosPdfTest(unittest.TestCase):
    def test_somente_pdf_direto_sem_stj_tse_nem_cliente_js(self):
        slugs = [s for s, *_ in coletor.REGIMENTOS]
        self.assertEqual(set(slugs), {"tst", "tcu", "stm", "stf"})
        with open(coletor.__file__, encoding="utf-8") as f:
            baixo = f.read().lower()
        self.assertNotIn("playwright", baixo)
        self.assertNotIn("selenium", baixo)
        self.assertNotIn("stealth", baixo)


    def test_pdf_com_regimento_longo_e_aceito(self):
        corpo = ("REGIMENTO INTERNO DO SUPERIOR TRIBUNAL MILITAR. " * 250)
        pdf = pdf_com_texto(corpo)
        self.assertTrue(pdf.startswith(b"%PDF"))
        stm = [f for f in coletor.REGIMENTOS if f[0] == "stm"]
        js = b"<!DOCTYPE html><html><script>challenge()</script></html>"

        def urlopen(req, timeout=0):
            url = req.full_url if hasattr(req, "full_url") else req
            if "stm.jus.br" in str(url):
                return io.BytesIO(pdf)
            return io.BytesIO(js)

        with tempfile.TemporaryDirectory() as tmp, \
                patch.object(coletor, "RAIZ", tmp), \
                patch.object(coletor, "REGIMENTOS", stm), \
                patch.object(coletor.urllib.request, "urlopen", urlopen):
            self.assertEqual(coletor.regimentos(SemEspera()), {"ok": 1, "pulado": 0})
            destino = os.path.join(tmp, "regimentos", "regimento-stm.md")
            with open(destino, encoding="utf-8") as f:
                texto = f.read()
            self.assertIn("REGIMENTO", texto.upper())
            self.assertGreater(len(texto), 10000)
            self.assertIn("dspace.stm.jus.br", texto)
            cache = os.path.join(tmp, "_fonte", "regimentos", "regimento-stm.pdf")
            with open(cache, "rb") as f:
                self.assertTrue(f.read().startswith(b"%PDF"))

    def test_casca_js_nao_e_pdf_e_nao_grava_markdown(self):
        js = b"<!DOCTYPE html><html><head><script>window.location='/challenge'</script></head>" \
             b"<body>Enable JavaScript</body></html>"
        stm = [f for f in coletor.REGIMENTOS if f[0] == "stm"]
        def urlopen(req, timeout=0):
            return io.BytesIO(js)

        with tempfile.TemporaryDirectory() as tmp, \
                patch.object(coletor, "RAIZ", tmp), \
                patch.object(coletor, "REGIMENTOS", stm), \
                patch.object(coletor.urllib.request, "urlopen", urlopen):
            with self.assertRaises(RuntimeError) as ctx:
                coletor.baixar_pdf(stm[0][3], os.path.join(tmp, "x.pdf"), SemEspera())
            self.assertIn("não é PDF", str(ctx.exception))
            self.assertIn(str(len(js)), str(ctx.exception))
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                self.assertEqual(coletor.regimentos(SemEspera()), {"ok": 0, "pulado": 0})
            saida = buf.getvalue()
            self.assertIn("não é PDF", saida)
            self.assertIn(str(len(js)), saida)
            self.assertFalse(os.path.exists(os.path.join(tmp, "regimentos", "regimento-stm.md")))
            with open(os.path.join(tmp, "_falhas.jsonl"), encoding="utf-8") as f:
                falhas = f.read()
            self.assertIn("regimento/stm", falhas)
            self.assertIn("não é PDF", falhas)


# Recorte do `pdftohtml -xml` da edição de 2023 do RISTF (páginas 22 e 26): a redação revogada sai na
# cor #7b7879, que a página imprime tachada; a nota "(Revogado pela...)" que a segue vem em preto.
XML_STF = """<pdf2xml producer="poppler" version="26.10.0">
<page number="22" position="absolute" top="0" left="0" height="892" width="654">
	<fontspec id="0" size="14" family="ESJKVA+ArnoPro-Caption" color="#2a8a49"/>
	<fontspec id="4" size="17" family="RPIXVA+ArnoPro-SmText" color="#231f20"/>
	<fontspec id="5" size="17" family="PSDNTE+ArnoPro-SmbdItalicSmText" color="#2a8a49"/>
	<fontspec id="7" size="15" family="PSDNTE+ArnoPro-SmbdItalicSmText" color="#7b7879"/>
	<fontspec id="8" size="15" family="NIRORI+ArnoPro" color="#7b7879"/>
	<fontspec id="9" size="17" family="XCXNBO+ArnoPro-SmbdSmText" color="#231f20"/>
	<fontspec id="10" size="14" family="JKZONQ+ArnoPro" color="#231f20"/>
<text top="45" left="290" width="74" height="17" font="0"><i>Art. 2º, caput</i></text>
<text top="820" left="306" width="43" height="17" font="0">— 21 —</text>
<text top="493" left="82" width="41" height="21" font="5"><i>Art. 3º</i></text>
<text top="494" left="123" width="390" height="21" font="4">  São órgãos do Tribunal o Plenário, as Turmas e o Presidente.</text>
<text top="540" left="82" width="43" height="21" font="5"><i>Art. 4º</i></text>
<text top="540" left="125" width="304" height="21" font="4">  As Turmas são constituídas de cinco Ministros.</text>
<text top="564" left="82" width="21" height="19" font="7"><i>§ 1º</i></text>
<text top="564" left="103" width="361" height="19" font="8"><i>  O Ministro mais antigo, integrante da Turma, é o seu Presidente.</i></text>
<text top="586" left="82" width="23" height="21" font="9">§ 1º</text>
<text top="586" left="105" width="471" height="21" font="4">  A Turma é presidida pelo Ministro mais antigo dentre seus membros, por </text>
<text top="609" left="99" width="476" height="21" font="4">um período de um ano, vedada a recondução.  </text>
<text top="658" left="99" width="368" height="17" font="10"><i>(Redação dada pela<a href="ristf.html#232"> Emenda Regimental n.&#160;25, de 26 de junho de 2008</a></i><i>)</i></text>
</page>
<page number="26" position="absolute" top="0" left="0" height="892" width="654">
<text top="45" left="300" width="54" height="17" font="0"><i>Art. 5º, x</i></text>
<text top="726" left="99" width="13" height="19" font="7"><i>f )</i></text>
<text top="726" left="117" width="265" height="19" font="8"><i>a extradição requisitada por Estado estrangeiro;</i></text>
<text top="728" left="385" width="190" height="17" font="10"><i>(Revogado pela Emenda Regimental</i></text>
<text top="820" left="306" width="43" height="17" font="0">— 25 —</text>
</page>
</pdf2xml>"""


class TachadoPelaCorTest(unittest.TestCase):
    def setUp(self):
        self.linhas = coletor.texto_do_xml_com_tachados(XML_STF, coletor.TACHADO_POR_COR["stf"]).split("\n")

    def test_redacao_revogada_sai_tachada_e_a_vigente_nao(self):
        self.assertIn("~~§ 1º O Ministro mais antigo, integrante da Turma, é o seu Presidente.~~", self.linhas)
        self.assertIn("§ 1º A Turma é presidida pelo Ministro mais antigo dentre seus membros, por", self.linhas)
        self.assertIn("(Redação dada pela Emenda Regimental n. 25, de 26 de junho de 2008)", self.linhas)

    def test_linha_mista_tacha_so_o_trecho_revogado(self):
        self.assertIn("~~f ) a extradição requisitada por Estado estrangeiro;~~ (Revogado pela Emenda Regimental", self.linhas)

    def test_cabecalho_e_rodape_corridos_ficam_de_fora(self):
        texto = "\n".join(self.linhas)
        self.assertNotIn("caput", texto)
        self.assertNotIn("— 21 —", texto)
        self.assertNotIn("Art. 5º, x", texto)

    def test_salto_maior_que_a_entrelinha_abre_paragrafo_e_cada_marca_fecha_na_linha(self):
        i = self.linhas.index("Art. 3º São órgãos do Tribunal o Plenário, as Turmas e o Presidente.")
        self.assertEqual(self.linhas[i + 1], "")
        self.assertEqual(self.linhas[i + 2], "Art. 4º As Turmas são constituídas de cinco Ministros.")
        self.assertTrue(all(linha.count("~~") % 2 == 0 for linha in self.linhas))

    def test_sem_a_cor_nada_e_tachado(self):
        self.assertNotIn("~~", coletor.texto_do_xml_com_tachados(XML_STF, "#000000"))


if __name__ == "__main__":
    unittest.main()
