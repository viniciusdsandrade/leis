"""Filtros do coletor do Paraná e parada limpa quando a fonte recusa o acesso; não usam a rede."""
import gzip
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import pr  # noqa: E402

LISTA = [
    {"codAto": "1", "tipo": "1", "ano": "2024"},
    {"codAto": "2", "tipo": "1", "ano": "2019"},
    {"codAto": "3", "tipo": "11", "ano": "2024"},
    {"codAto": "4", "tipo": "10"},  # Constituição: sem ano
]


class Filtros(unittest.TestCase):
    def test_faixa_de_anos(self):
        self.assertEqual(pr.faixa_de_anos("2024"), {2024})
        self.assertEqual(pr.faixa_de_anos("2020-2022"), {2020, 2021, 2022})

    def test_tipo_por_pasta_ou_codigo(self):
        self.assertEqual(pr.codigos_de_tipo("leis-ordinarias"), {"1"})
        self.assertEqual(pr.codigos_de_tipo("1, decretos"), {"1", "11"})
        with self.assertRaises(ValueError):
            pr.codigos_de_tipo("leis-ordinarias,inexistente")

    def test_filtrar(self):
        self.assertEqual([i["codAto"] for i in pr.filtrar(LISTA, {"1"}, None)], ["1", "2"])
        self.assertEqual([i["codAto"] for i in pr.filtrar(LISTA, None, {2024})], ["1", "3"])
        self.assertEqual([i["codAto"] for i in pr.filtrar(LISTA, {"1"}, {2024})], ["1"])
        self.assertEqual(len(pr.filtrar(LISTA)), 4)


class Cobertura(unittest.TestCase):
    def test_fecha_quando_md_ou_falha_cobrem_o_indice(self):
        r = pr.cobertura(["10", "20", "30"], ["10"], ["30"])
        self.assertEqual(r["indice"], 3)
        self.assertEqual(r["md"], 1)
        self.assertEqual(r["falhas"], 1)
        self.assertEqual(r["faltando"], ["20"])

    def test_normaliza_int_e_str_e_ignora_falha_fora_do_indice(self):
        r = pr.cobertura([1, 2], ["1", "2"], ["99"])
        self.assertEqual(r["faltando"], [])
        self.assertEqual(r["falhas"], 0)
        self.assertEqual(r["md"], 2)


class Recusa(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        pr.RECUSADO.clear()
        self.addCleanup(pr.RECUSADO.clear)
        p = patch.object(pr, "RAIZ_ESTADUAIS", self.tmp.name)
        p.start()
        self.addCleanup(p.stop)
        p = patch.object(pr, "caminhos", lambda uf, pasta, ano, slug: (
            os.path.join(self.tmp.name, uf, pasta, str(ano), slug + ".md"),
            os.path.join(self.tmp.name, uf, "_fonte", pasta, str(ano), slug + ".html.gz")))
        p.start()
        self.addCleanup(p.stop)
        self.it = {"codAto": "77", "tipo": "1", "ano": "2024", "epigrafe": "Lei 21.926 - 11 de Abril de 2024", "ementa": "x"}

    def test_primeira_recusa_liga_o_sinal_e_os_demais_nao_vao_a_rede(self):
        chamadas = []

        def get(url, **kw):
            chamadas.append(url)
            return 403, b"", ""

        with patch.object(pr.rede, "get", get):
            self.assertEqual(pr.processar(self.it), ("bloqueado", None))
            self.assertTrue(pr.RECUSADO.is_set())
            self.assertEqual(pr.processar({**self.it, "codAto": "78"}), ("bloqueado", None))
        self.assertEqual(len(chamadas), 1)

    def test_429_tambem_interrompe(self):
        def get(url, **kw):
            raise RuntimeError(f"falhou após 1 tentativas: {url}: HTTP Error 429: Too Many Requests")

        with patch.object(pr.rede, "get", get):
            self.assertEqual(pr.processar(self.it), ("bloqueado", None))
        self.assertTrue(pr.RECUSADO.is_set())

    def test_documento_em_cache_nao_depende_da_rede(self):
        pasta = os.path.join(self.tmp.name, "PR", "_indice", "documentos")
        os.makedirs(pasta)
        html = ("<html><body><h3>Lei 21.926 - 11 de Abril de 2024</h3><p>Art. 1º Esta Lei entra em vigor na data de sua "
                "publicação, revogadas as disposições em contrário.</p></form></body></html>")
        with open(os.path.join(pasta, "77.html.gz"), "wb") as f:
            f.write(gzip.compress(html.encode("utf-8")))
        pr.RECUSADO.set()
        with patch.object(pr.rede, "get", side_effect=AssertionError("não deveria ir à rede")):
            status, extra = pr.processar(self.it)
        self.assertEqual((status, extra), ("ok", None))
        gravado = os.path.join(self.tmp.name, "PR", "leis-ordinarias", "2024", "lei-21926-2024-id77.md")
        self.assertTrue(os.path.exists(gravado))
        with open(gravado, encoding="utf-8") as f:
            texto = f.read()
        self.assertIn("data: 2024-04-11", texto)
        self.assertIn("Esta Lei entra em vigor na data de sua publicação", texto)

    def test_mes_com_acento_historico_preenche_data(self):
        pasta = os.path.join(self.tmp.name, "PR", "_indice", "documentos")
        os.makedirs(pasta)
        html = ("<html><body><h3>Lei 4057 - 28 de Agôsto de 1959</h3><p>Art. 1º Esta Lei entra em vigor na data de sua "
                "publicação, revogadas as disposições em contrário.</p></form></body></html>")
        with open(os.path.join(pasta, "12388.html.gz"), "wb") as f:
            f.write(gzip.compress(html.encode("utf-8")))
        it = {"codAto": "12388", "tipo": "1", "ano": "1959", "epigrafe": "Lei 4057 - 28 de Agôsto de 1959", "ementa": "x"}
        with patch.object(pr.rede, "get", side_effect=AssertionError("não deveria ir à rede")):
            self.assertEqual(pr.processar(it), ("ok", None))
        gravado = os.path.join(self.tmp.name, "PR", "leis-ordinarias", "1959", "lei-4057-1959-id12388.md")
        with open(gravado, encoding="utf-8") as f:
            texto = f.read()
        self.assertIn("data: 1959-08-28", texto)

    def test_dia_primeiro_com_ordinal_mantem_numero_e_data(self):
        pasta = os.path.join(self.tmp.name, "PR", "_indice", "documentos")
        os.makedirs(pasta)
        html = ("<html><body><h3>Lei 23.440 - 1º de setembro de 2026</h3><p>Art. 1º Esta Lei entra em vigor na data de sua "
                "publicação, revogadas as disposições em contrário.</p></form></body></html>")
        with open(os.path.join(pasta, "88.html.gz"), "wb") as f:
            f.write(gzip.compress(html.encode("utf-8")))
        it = {"codAto": "88", "tipo": "1", "ano": "2026", "epigrafe": "Lei 23.440 - 1º de setembro de 2026", "ementa": "x"}
        with patch.object(pr.rede, "get", side_effect=AssertionError("não deveria ir à rede")):
            self.assertEqual(pr.processar(it), ("ok", None))
        gravado = os.path.join(self.tmp.name, "PR", "leis-ordinarias", "2026", "lei-23440-2026-id88.md")
        self.assertTrue(os.path.exists(gravado), os.listdir(os.path.join(self.tmp.name, "PR", "leis-ordinarias", "2026")))
        with open(gravado, encoding="utf-8") as f:
            texto = f.read()
        self.assertIn("data: 2026-09-01", texto)
        self.assertIn('numero: "23.440"', texto)

    def test_lei_com_anexos_em_pdf_fica_fora_com_motivo(self):
        pasta = os.path.join(self.tmp.name, "PR", "_indice", "documentos")
        os.makedirs(pasta)
        html = ("<html><body><h3>Lei 23.390 - 7 de agosto de 2026</h3><p>Art. 1º Os vencimentos são os do Anexo I desta Lei.</p>"
                "ANEXOS: <table><tr><td><a href=\"javascript:exibirAnexo(82480);\"><img src=\"/legislacao/images/icon_exibir.png\"/></a>"
                "</td><td>Anexo I</td></tr></table></form></body></html>")
        with open(os.path.join(pasta, "99.html.gz"), "wb") as f:
            f.write(gzip.compress(html.encode("utf-8")))
        it = {"codAto": "99", "tipo": "1", "ano": "2026", "epigrafe": "Lei 23.390 - 7 de agosto de 2026", "ementa": "x"}
        status, extra = pr.processar(it)
        self.assertEqual(status, "sem_texto")
        self.assertIn("anexos em PDF", extra["motivo"])
        self.assertFalse(os.path.exists(os.path.join(self.tmp.name, "PR", "leis-ordinarias", "2026", "lei-23390-2026-id99.md")))


if __name__ == "__main__":
    unittest.main()
