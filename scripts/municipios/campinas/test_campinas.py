"""Ferramentas de Campinas: o pós-processamento de regenerar espelha o pipeline (carimbos e recorte de página de livro).

Fora do CI: scripts/municipios/ não entra no checkout. Rodar com `python3 scripts/municipios/campinas/test_campinas.py`.
"""
import hashlib
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import campinas  # noqa: E402

CAPA = ("CÂMARA MUNICIPAL DE CAMPINAS Estado de São Paulo Diretoria de Gestão Documental "
        "Coordenadoria de Biblioteca cbib@campinas.sp.leg.br – Ramal 1603")
PAGINA_DE_LIVRO = (
    "LEI N. 1 (Declara de utilidade publica um terreno.)\n\n"
    "**Art. 1** - Fica declarado de utilidade publica o terreno da rua Barão de Jaguara.\n\n"
    "**Art. 2** - Revogam-se as disposições em contrário.\n\n"
    "Paço Municipal, 13 de fevereiro de 1918\n\n"
    "LEI N. 2 (Abre credito especial.)\n\n"
    "**Art. 1** - Fica aberto o credito especial de 5:000$000."
)
META = {"tipo_na_fonte": "Leis Até 1948", "numero": "1", "data": "1918-02-13"}
NOTA = "texto integral anexado no SAPL municipal; " + campinas.NOTA_RECORTE + ", que traz mais de um ato; a página inteira está em fonte_texto"
OS_SEIS = [
    "leis-ordinarias/1918/leis-ordinarias-225-1918-sapl-39999.md", "leis-ordinarias/1923/leis-ordinarias-304-1923-sapl-40078.md",
    "leis-ordinarias/1923/leis-ordinarias-309-1923-sapl-40083.md", "leis-ordinarias/1923/leis-ordinarias-310-1923-sapl-40084.md",
    "leis-ordinarias/1924/leis-ordinarias-333-1924-sapl-40110.md", "leis-ordinarias/1929/leis-ordinarias-461-1929-sapl-40240.md",
]


class PosProcessamento(unittest.TestCase):
    def test_sem_a_nota_so_limpa_carimbos(self):
        corpo = campinas.pos_processar(CAPA + "\n\n" + PAGINA_DE_LIVRO, {**META, "versao_texto": "texto integral anexado no SAPL municipal; "})
        self.assertEqual(corpo, PAGINA_DE_LIVRO)

    def test_com_a_nota_recorta_o_ato_proprio_depois_dos_carimbos(self):
        corpo = campinas.pos_processar(CAPA + "\n\n" + PAGINA_DE_LIVRO, {**META, "versao_texto": NOTA})
        self.assertTrue(corpo.startswith("LEI N. 1 (Declara"))
        self.assertIn("13 de fevereiro de 1918", corpo)
        self.assertNotIn("LEI N. 2", corpo)
        self.assertNotIn("CÂMARA MUNICIPAL", corpo)
        self.assertTrue(corpo.endswith("1918\n"))

    def test_recorte_com_data_divergente_e_apontado(self):
        with self.assertRaises(RuntimeError):
            campinas.pos_processar(PAGINA_DE_LIVRO, {**META, "data": "1918-02-14", "versao_texto": NOTA})


class RegenerarOsSeisRecortados(unittest.TestCase):
    """Os seis .md recortados da página de livro voltam a 'iguais' quando a fonte .bin está em cache local."""

    def test_reproduz_sha256_texto(self):
        conferidos = 0
        for rel in OS_SEIS:
            p = campinas.MUN / rel
            if not p.exists():
                continue
            meta, corpo_md, _ = campinas.ler_md(p)
            fonte = campinas.fonte_em_cache(meta)
            if not fonte.exists():
                continue
            corpo, motivo = campinas.corpo_regenerado(meta, fonte.read_bytes())
            self.assertIsNone(motivo, rel)
            self.assertEqual(hashlib.sha256(corpo.encode()).hexdigest(), meta["sha256_texto"], rel)
            self.assertEqual(corpo, corpo_md, rel)
            conferidos += 1
        if not conferidos:
            self.skipTest("fontes .bin dos seis recortes não estão em cache nesta máquina")


if __name__ == "__main__":
    unittest.main()
