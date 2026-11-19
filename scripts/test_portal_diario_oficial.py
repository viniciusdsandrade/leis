import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import portal_diario_oficial as portal

ROBOTS = b"User-agent: *\nDisallow: /arquivos/\nDisallow: /uploads/\nDisallow: /portal/download/\n"


class RedeFalsa:
    """Responde de um dicionário {url: (status, corpo)} e guarda os pedidos feitos."""

    def __init__(self, respostas):
        self.respostas, self.pedidos = respostas, []

    def get(self, url, accept="*/*"):
        self.pedidos.append(url)
        st, corpo = self.respostas.get(url, (404, b""))
        return st, corpo, "text/html"


def item(ident, numero, data):
    dia, mes, ano = data[8:], data[5:7], data[:4]
    return (f'<div class="dof_publicacao_diario sw_item_listagem"><a href="/portal/diario-oficial/ver/{ident}">'
            f'Edição nº {numero}</a> Postagem: {dia}/{mes}/{ano} <a data-href="/portal/download/diario-oficial/t{ident}/">'
            f'baixar</a></div>')


class Autorizacao(unittest.TestCase):
    def test_vale_so_onde_o_mantenedor_autorizou(self):
        self.assertIsNone(portal.sem_autorizacao("valinhos", 2006, 2026))
        self.assertIsNone(portal.sem_autorizacao("vinhedo", 2010, 2026))
        self.assertIsNone(portal.sem_autorizacao("paulinia", 2012, 2012))
        self.assertIn("só para as edições de 2012 a 2012", portal.sem_autorizacao("paulinia", 2013, 2013))
        self.assertIn("não há autorização", portal.sem_autorizacao("jarinu", 2020, 2020))

    def test_robots_veda_o_download_e_a_autorizacao_decide(self):
        for chave in ("valinhos", "vinhedo", "paulinia"):
            base = portal.MUNICIPIOS[chave].base
            rede = RedeFalsa({f"{base}/robots.txt": (200, ROBOTS)})
            self.assertTrue(portal.conferir_robots(rede, portal.MUNICIPIOS[chave], False, 2012, 2012, 0.5))  # só cache
            self.assertFalse(portal.conferir_robots(rede, portal.MUNICIPIOS[chave], True, 2012, 2012, 0.2))
        rede = RedeFalsa({f"{portal.MUNICIPIOS['paulinia'].base}/robots.txt": (200, ROBOTS)})
        with self.assertRaisesRegex(RuntimeError, "vale só para as edições de 2012"):
            portal.conferir_robots(rede, portal.MUNICIPIOS["paulinia"], True, 2013, 2026, 0.2)

    def test_listagem_vedada_para_tudo(self):
        base = portal.MUNICIPIOS["vinhedo"].base
        rede = RedeFalsa({f"{base}/robots.txt": (200, b"User-agent: *\nDisallow: /portal/\n")})
        with self.assertRaisesRegex(RuntimeError, "veda a listagem"):
            portal.conferir_robots(rede, portal.MUNICIPIOS["vinhedo"], True, 2020, 2020, 0.2)


class Listagem(unittest.TestCase):
    BASE = "https://www.valinhos.sp.gov.br"

    def test_para_quando_o_portal_repete_paginas_ja_vistas(self):
        pagina = f"{self.BASE}/portal/diario-oficial/%d/0/0/0/0"
        rede = RedeFalsa({pagina % 1: (200, (item(3, "3.071", "2026-11-18") + item(2, "3070", "2026-11-17")).encode()),
                          pagina % 2: (200, item(1, "980", "2006-07-05").encode()),
                          pagina % 3: (200, item(3, "3071", "2026-11-18").encode())})  # depois do fim, o portal repete
        edicoes = portal.listar_edicoes(rede, self.BASE, 2006, 2026)
        self.assertEqual([(e["id"], e["edicao"], e["data"]) for e in edicoes],
                         [("1", "980", "2006-07-05"), ("2", "3070", "2026-11-17"), ("3", "3071", "2026-11-18")])
        self.assertEqual(len(rede.pedidos), 3)
        self.assertEqual([e["data"] for e in portal.listar_edicoes(rede, self.BASE, 2026, 2026)], ["2026-11-17", "2026-11-18"])

    def test_dados_abertos_de_ano_sem_edicao(self):
        url = f"{self.BASE}/portal/dados-abertos/diario-oficial/%d"
        rede = RedeFalsa({url % 2009: (200, json.dumps({"dados": [["Nenhum registro encontrado."]]}).encode()),
                          url % 2010: (200, json.dumps({"dados": [{"edicao": "1.163"}, {"edicao": 1164}]}).encode())})
        self.assertEqual(portal.edicoes_dos_dados_abertos(rede, self.BASE, 2009), set())
        self.assertEqual(portal.edicoes_dos_dados_abertos(rede, self.BASE, 2010), {"1163", "1164"})

    def test_resumo_corta_listas_longas(self):
        self.assertEqual(portal.resumo({"10", "9", "100"}), "9, 10, 100")
        self.assertEqual(portal.resumo({str(n) for n in range(30)}, limite=3), "0, 1, 2 e mais 27")


class Download(unittest.TestCase):
    BASE = "https://www.vinhedo.sp.gov.br"

    def test_segue_o_redirecionamento_para_uploads_e_guarda_pelo_id(self):
        pdf = b"%PDF-1.4 conteudo"
        rede = RedeFalsa({f"{self.BASE}/portal/download/diario-oficial/Ab-c/": (
                              200, b'<meta http-equiv="refresh" content="0; url=/uploads/f00d2026.pdf">'),
                          f"{self.BASE}/uploads/f00d2026.pdf": (200, pdf)})
        with tempfile.TemporaryDirectory() as tmp:
            url, arquivo = portal.baixar_pdf(rede, self.BASE, Path(tmp), {"id": "2711", "token": "Ab-c"})
            self.assertEqual(url, f"{self.BASE}/uploads/f00d2026.pdf")
            self.assertEqual(arquivo.name, "2711-f00d2026.pdf")
            self.assertEqual(arquivo.read_bytes(), pdf)
            # em cache e no índice: nenhum pedido novo
            antes = len(rede.pedidos)
            self.assertEqual(portal.baixar_pdf(rede, self.BASE, Path(tmp), {"id": "2711", "token": "Ab-c", "pdf": url})[1], arquivo)
            self.assertEqual(len(rede.pedidos), antes)

    def test_so_cache_nao_pede_nada(self):
        rede = RedeFalsa({})
        with tempfile.TemporaryDirectory() as tmp, self.assertRaisesRegex(RuntimeError, "robots.txt"):
            portal.baixar_pdf(rede, self.BASE, Path(tmp), {"id": "1", "token": "x"}, so_cache=True)
        self.assertEqual(rede.pedidos, [])

    def test_resposta_que_nao_e_pdf(self):
        rede = RedeFalsa({f"{self.BASE}/portal/download/diario-oficial/x/": (200, b"<html>erro</html>")})
        with tempfile.TemporaryDirectory() as tmp, self.assertRaisesRegex(RuntimeError, "sem o endereço do PDF"):
            portal.baixar_pdf(rede, self.BASE, Path(tmp), {"id": "1", "token": "x"})


if __name__ == "__main__":
    unittest.main()
