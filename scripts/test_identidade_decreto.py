"""Regressões das identidades divergentes encontradas nos lotes DEC de 1945."""
import gzip
import hashlib
import json
from pathlib import Path
import tempfile
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import unittest
from unittest.mock import patch

import baixar_federal as coletor
from html2md import convert
from identidade_decreto import divergencia_epigrafe_decreto, extrair_epigrafe_decreto

RAIZ = Path(__file__).resolve().parent.parent
CASOS_REAIS = [
    ("17453", "1945-12-28", "DECRETO N. 17.453 – DE 28 DE DEZEMBRO DE 1944", "17453", "1944-12-28"),
    ("17424", "1945-12-26", "DECRETO N. 17.424 – DE 26 DE DEZEMBRO DE 1944", "17424", "1944-12-26"),
    ("20215", "1945-12-17", "DECRETO Nº 20.251, DE 17 DE DEZEMBRO DE 1945.", "20251", "1945-12-17"),
]


class IdentidadeDecretoTest(unittest.TestCase):
    def test_discrepancias_reais(self):
        for numero, data, epigrafe, encontrado, data_encontrada in CASOS_REAIS:
            with self.subTest(numero=numero):
                erro = divergencia_epigrafe_decreto("DEC-n", numero, data, epigrafe)
                self.assertEqual(erro["identidade_esperada"], {"numero": numero, "data": data})
                self.assertEqual(erro["epigrafe_encontrada"]["numero"], encontrado)
                self.assertEqual(erro["epigrafe_encontrada"]["data"], data_encontrada)

    def test_pontuacao_mes_ordinal_e_complemento(self):
        for epigrafe, numero, data in [
            ("**DECRETO N.º 20.289, DE 31 DE DEZEMBRO DE 1945.**", "20289", "1945-12-31"),
            ("Decreto n° 1.234-A — de 1º de março de 1.945", "1234-A", "1945-03-01"),
            ("DECRETO N. 19.533-A – DE 30 DE AGÔSTO DE 1945", "19533-A", "1945-08-30"),
            ("DECRETO 123, DE 2 DE janeiro DE 2000", "123", "2000-01-02"),
            ("DECRETO Nº 3.413, DE 14 ABRIL DE 2000.", "3413", "2000-04-14"),
            ("DECRETO Nº20,194, DE13DEDEZEMBRODE1945", "20194", "1945-12-13"),
            ("DECRETO Nº 20.110, DE 4DE DEZEMBRO DE 1945", "20110", "1945-12-04"),
        ]:
            with self.subTest(epigrafe=epigrafe):
                extraida = extrair_epigrafe_decreto(epigrafe)
                self.assertIsNotNone(extraida)
                self.assertEqual((extraida["numero"], extraida["data"]), (numero, data))
                self.assertIsNone(divergencia_epigrafe_decreto("DEC-n", numero, data, epigrafe))

    def test_inconclusivo_nao_confirma_por_citacao_ou_dado_parcial(self):
        for texto in [
            "O Presidente cita o DECRETO Nº 123, DE 2 DE JANEIRO DE 2000.",
            "**Art. 1º** Fica alterado o seguinte:\n\nDECRETO Nº 123, DE 2 DE JANEIRO DE 2000.",
            "DECRETO Nº 123, DE JANEIRO DE 2000.",
            "DECRETO Nº 123, DE 31 DE FEVEREIRO DE 2000.",
            "DECRETO-LEI Nº 123, DE 2 DE JANEIRO DE 2000.",
            "DECRETO LEGISLATIVO Nº 123, DE 2 DE JANEIRO DE 2000.",
        ]:
            with self.subTest(texto=texto):
                self.assertIsNone(extrair_epigrafe_decreto(texto))
        self.assertIsNone(divergencia_epigrafe_decreto("LEI-n", "99", "1900-01-01", CASOS_REAIS[0][2]))
        self.assertIsNone(divergencia_epigrafe_decreto("DEC-sn", "99", "1900-01-01", CASOS_REAIS[0][2]))

    def test_grafia_defeituosa_da_fonte_com_numero_e_data_inteiros(self):
        # Epígrafes reais dos decretos retidos como "inconclusivos" em federal/_falhas.jsonl.
        for epigrafe, numero, data in [
            ("Decreto nº 81 444, de 14 de março de 1978.", "81444", "1978-03-14"),
            ("DECRETO N. 13. 112 – DE 5 DE AGOSTO DE 1943", "13112", "1943-08-05"),
            ("decreto nº 42. 977, de 31 de dezembro de 1957.", "42977", "1957-12-31"),
            ("Decreto nº 82 815 de 06 de dezembro de 1978", "82815", "1978-12-06"),
            ("DECRETO N. 2038 A – DE 8 DE JULHO DE 1895", "2038-A", "1895-07-08"),
            ("decreto n. 563 A - de 10 de julho de 1890", "563-A", "1890-07-10"),
            ("DECRETO N. 16.015 A – DE 23 DE ABRIL DE 1923", "16015-A", "1923-04-23"),
            ("DECRETO N. 3676 () – DE 9 DE JUNHO DE 1900", "3676", "1900-06-09"),
            ("() DECRETO Nº 53.554, DE 7 DE FEVEREIRO DE 1964.", "53554", "1964-02-07"),
            ("()DECRETO Nº 51.669, DE 17 DE JANEIRO DE 1963.", "51669", "1963-01-17"),
            ("() Decreto nº 51.769, de 1º de MARÇO de 1963.", "51769", "1963-03-01"),
            ("DECRETa Nº 39.735, DE 8 DE AGÔSTO DE 1956", "39735", "1956-08-08"),
            ("DECRETONº 47.092, DE 24 DE OUTUBRO DE 1959.", "47092", "1959-10-24"),
            ("DECERTO Nº 40.703, DE 31 DE DEZEMBRO DE 1956.", "40703", "1956-12-31"),
            ("DCRETO Nº 24.925, DE 7 DE MAIO DE 1948.", "24925", "1948-05-07"),
            ("DECRET0 Nº 67.624, DE 19 DE NOVEMBRO 1970.", "67624", "1970-11-19"),
            ("DCERETO Nº 26.490,DE 19 DE março DE 1949.", "26490", "1949-03-19"),
            ("Decrete nº 90.400, de 07 de novembro de 1984", "90400", "1984-11-07"),
            ("DECRETO DE Nº 43.704, DE 9 DE MAIO DE 1958.", "43704", "1958-05-09"),
            ("DECRETO N\uf0b0 21.694, DE 21 DE AGÔSTO DE 1946.", "21694", "1946-08-21"),
            ("1\n\nDECRETO N° 97 916, DE 6 de JULHO DE 1989", "97916", "1989-07-06"),
        ]:
            with self.subTest(epigrafe=epigrafe):
                extraida = extrair_epigrafe_decreto(epigrafe)
                self.assertIsNotNone(extraida)
                self.assertEqual((extraida["numero"], extraida["data"]), (numero, data))
                self.assertIsNone(divergencia_epigrafe_decreto("DEC-n", numero, data, epigrafe))

    def test_grafia_defeituosa_nao_inventa_numero_nem_data(self):
        for texto in [
            "DECRETO N° 94O, DE 27 DE SETEMBRO DE 1993",          # letra O no número: é o 940, não o 94-O
            "decreto de 26 de abril de 2000.",                     # decreto sem número
            "DECRETO-LEI N. 21.410 – DE 12 DE JULHO DE 1946",      # outra espécie
            "DECRETO Nº 41.057, DE FEVEREIRO DE 1957.",            # sem o dia
            "DECRETO Nº 38.755, DE 30 DE FEVEREIRO DE 1956.",      # data impossível
            "DECRETO Nº 17.425, DE 26 DE DEZEMBRO DE 19446.",      # ano com um dígito a mais
            "DECRETO Nº 40.379, DE 19 DE NOVENBRO DE 1956.",       # mês com erro: fica para a revisão com o fecho
            "DECRETa Nº 19.850, DE 22 DE outobro DE 1945.",        # idem, mesmo com a palavra tolerada
            "Decreto nº 90.906, de O5 de fevereiro de 1985",       # letra O no dia
            "DECLARO Nº 100, DE 2 DE JUNHO DE 1950.",              # a palavra não é "Decreto" com um erro
            "DECRETO N. 10.335 – DE 25 DE AGOSTO DE l942",         # letra no ano
            "O Presidente cita o DECRETA Nº 123, DE 2 DE JANEIRO DE 2000.",
            "**Art. 1º** Fica alterado:\n\nDECRETO Nº 81 444, DE 14 DE MARÇO DE 1978.",
        ]:
            with self.subTest(texto=texto):
                self.assertIsNone(extrair_epigrafe_decreto(texto))

    def test_grafia_defeituosa_divergente_continua_retida_e_a_regular_tem_precedencia(self):
        # O dia da epígrafe (7) não é o do índice (4): a grafia tolerada não vira confirmação.
        erro = divergencia_epigrafe_decreto("DEC-n", "48736", "1960-08-04", "DECRERTO Nº 48.736, DE 7 DE agôsto DE 1960.")
        self.assertEqual(erro["epigrafe_encontrada"]["data"], "1960-08-07")
        # Havendo uma epígrafe regular nos blocos de abertura, é ela que vale, mesmo depois de uma defeituosa.
        corpo = "DECRETA Nº 11, DE 1 DE MAIO DE 1950.\n\nDECRETO Nº 22, DE 2 DE MAIO DE 1950."
        self.assertEqual(extrair_epigrafe_decreto(corpo)["numero"], "22")

    def test_processar_retem_markdown_preserva_cache_e_retorna_pendencia(self):
        for numero, data, epigrafe, _, _ in CASOS_REAIS:
            with self.subTest(numero=numero), tempfile.TemporaryDirectory() as tmp:
                bruto = ("<p>" + epigrafe + "</p><p>Art. 1º Regra.</p>").encode()
                d = {"tipo": "DEC-n", "numero": numero, "dataassinatura": "/".join(reversed(data.split("-"))),
                     "id": "teste", "norma": "DEC-" + numero, "normaNome": "Decreto " + numero}
                meta = {"encoding": {"contentUrl": "https://example.invalid/api/binario/teste", "version": "Original"}}
                with patch.object(coletor, "RAIZ", tmp), patch.object(coletor, "obter_metadados", return_value=(coletor.montar(d)["urn"], meta)), patch.object(coletor, "http_get", return_value=(200, bruto)):
                    info = coletor.montar(d)
                    status, slug, extra = coletor.processar(d)
                self.assertEqual(status, "sem_texto")
                self.assertEqual(slug, info["slug"])
                self.assertIn("Epígrafe própria diverge", extra["motivo"])
                self.assertFalse(Path(info["md"]).exists())
                self.assertEqual(bruto, gzip.decompress(Path(info["fonte"]).read_bytes()))

    def test_processar_identidade_valida_grava_normalmente(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(coletor, "RAIZ", tmp):
            bruto = b'<p>DECRETO N. 20.289 - DE 31 DE DEZEMBRO DE 1945.</p><p>Art. 1 Regra.</p>'
            d = {"tipo": "DEC-n", "numero": "20289", "dataassinatura": "31/12/1945", "id": "teste",
                 "norma": "DEC-20289-1945-12-31", "normaNome": "Decreto 20289"}
            meta = coletor.MetadadosFonte(encoding={"contentUrl": "https://example.invalid/api/binario/teste", "version": "Original"})
            path = Path(tmp) / "metadata.json.gz"
            path.write_bytes(gzip.compress(b'{}'))
            meta.captura = {"path": str(path), "sha256": hashlib.sha256(b'{}').hexdigest()}
            info = coletor.montar(d)
            with patch.object(coletor, "obter_metadados", return_value=(info["urn"], meta)), patch.object(coletor, "http_get", return_value=(200, bruto)):
                self.assertEqual("ok", coletor.processar(d)[0])
            self.assertIn("DECRETO N. 20.289", Path(info["md"]).read_text())

    def test_caches_reais_e_manifesto_quando_disponiveis(self):
        manifesto = RAIZ / "federal/_lote_dec1945_20261020.json"
        caches = [RAIZ / f"federal/_fonte/decretos/1945/dec-{n}-{data}.html.gz"
                  for n, data, *_ in CASOS_REAIS]
        if not manifesto.exists() or not all(p.exists() for p in caches):
            self.skipTest("capturas locais de auditoria não distribuídas no acervo Git")
        retidos = json.loads(manifesto.read_text())["retidos"]
        for caso, cache in zip(CASOS_REAIS, caches):
            numero, data, epigrafe, _, _ = caso
            corpo = convert(gzip.decompress(cache.read_bytes()).decode("utf-8", "replace"))
            erro = divergencia_epigrafe_decreto("DEC-n", numero, data, corpo)
            self.assertEqual(erro["epigrafe_encontrada"]["epigrafe"], epigrafe)
            if numero in {"17453", "17424"}:
                registro = next(r for r in retidos if r["urn"].endswith(";" + numero))
                self.assertEqual(registro["epigrafe"], epigrafe)
                self.assertEqual(registro["fonte_html_sha256"], hashlib.sha256(gzip.decompress(cache.read_bytes())).hexdigest())


if __name__ == "__main__":
    unittest.main()
