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
    def test_somente_pdf_direto_sem_stj_tse_stf_nem_cliente_js(self):
        slugs = [s for s, *_ in coletor.REGIMENTOS]
        self.assertEqual(set(slugs), {"tst", "tcu", "stm"})
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


if __name__ == "__main__":
    unittest.main()
