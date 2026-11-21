"""Coletor do Banco Central (baixar_bcb.py): índice, conversão, retenções e deduplicação; não usa a rede."""
import json
import os
import sys
import tempfile
import unittest
import urllib.parse
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import baixar_bcb as b  # noqa: E402


class RedeFalsa:
    """Responde pelo trecho da URL; falha alto se pedirem o que não foi previsto."""

    def __init__(self, respostas):
        self.respostas, self.pedidos = respostas, []

    def get(self, url, accept="*/*", **_):
        self.pedidos.append(url)
        for trecho, resposta in self.respostas.items():
            if trecho in urllib.parse.unquote(url):
                return resposta(url) if callable(resposta) else resposta
        raise AssertionError(f"pedido inesperado: {url}")


def detalhe(**campos):
    base = {"Titulo": "", "Tipo": "", "Numero": 0, "DataTexto": "", "Assunto": "", "Revogado": False,
            "Cancelado": False, "DOU": None, "Documentos": None, "Texto": ""}
    return (200, json.dumps({"conteudo": [{**base, **campos}]}).encode("utf-8"), "application/json")


# Recortes das respostas reais (20/11/2026).
CIRCULAR_3978 = dict(Titulo="Circular N° 3.978", Tipo="Circular", Numero=3978.0, DataTexto="23/1/2020 10:30",
                     Assunto="Dispõe sobre a política de prevenção à lavagem de dinheiro.",
                     DOU="Publicada no DOU de 24/1/2020, Seção 1, p. 24-28.",
                     Documentos="Circ_3978_v1_O.pdf;705#;Circ_3978_v2_L.pdf;705#;",
                     Texto='<div><p style="text-indent&#58;2.5cm;">A Diretoria Colegiada do Banco Central do Brasil, em '
                           'sessão realizada em 22 de janeiro de 2020, resolve:</p><p><strong>Art. 70.</strong> Esta '
                           'Circular entra em vigor em 1º de julho de 2020.</p><p>Otávio Ribeiro Damaso<br>Diretor de '
                           'Regulação</p></div>')
RESOLUCAO_2682 = dict(Titulo="Resolução Nº 2.682", Tipo="Resolução", Numero=2682.0, DataTexto="21/12/1999 00:00",
                      Assunto="Dispõe sobre critérios de classificação das operações de crédito.", Revogado=True,
                      Texto='<div class="ExternalClassA"><pre>                        RESOLUCAO N. 002682\n'
                            '                        -------------------\n\n'
                            '                                   Dispõe sobre  critérios de classi-\n'
                            '                                   ficação das operações de crédito.\n\n'
                            '         O BANCO CENTRAL DO BRASIL, na forma do art. 9º da Lei nº 4.595, de 31 de\n'
                            '         dezembro de 1964, torna público que o CONSELHO MONETÁRIO NACIONAL\n'
                            '         R E S O L V E U:\n\n'
                            '         Art. 1º  Determinar que as instituições financeiras devem classificar\n'
                            '         as operações de crédito nos seguintes níveis:\n'
                            '         I - nível AA;\n'
                            '         II - nível A;\n\n'
                            '         Art. 2º  Esta Resolução entra em vigor na data de sua publicação.\n'
                            '</pre></div>')


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        raiz = Path(self.tmp.name)
        for nome, valor in (("PASTA", raiz / "reguladores" / "bcb"), ("INDICE", raiz / "reguladores" / "bcb" / "_indice"),
                            ("FONTE", raiz / "reguladores" / "_fonte" / "bcb"),
                            ("FALHAS", raiz / "reguladores" / "bcb" / "_falhas.jsonl")):
            p = patch.object(b, nome, valor)
            p.start()
            self.addCleanup(p.stop)

    def ler(self, relativo):
        return (b.PASTA / relativo).read_text(encoding="utf-8")


class Indice(Base):
    def paginas(self, linhas, total):
        def resposta(url):
            inicio = int(urllib.parse.parse_qs(urllib.parse.urlparse(url).query)["startrow"][0])
            return 200, json.dumps({"TotalRows": total, "Rows": linhas[inicio:inicio + 2]}).encode(), ""
        return resposta

    def linha(self, i, tipo, numero):
        return {"listItemId": str(i), "TipodoNormativoOWSCHCS": tipo, "NumeroOWSNMBR": f"{numero}.000000000000",
                "data": "1999-12-21T02:00:00Z", "title": f"{tipo} Nº {numero}", "AssuntoNormativoOWSMTXT": " Ementa. "}

    def test_filtra_o_tipo_exato_e_pagina_pelo_que_veio(self):
        linhas = [self.linha(1, "Circular", 2), self.linha(2, "Carta Circular", 1), self.linha(3, "Circular", 1),
                  self.linha(4, "Carta Circular", 2), self.linha(5, "Circular", 3)]
        rede = RedeFalsa({"buscanormativos": self.paginas(linhas, 5)})
        lista = b.montar_indice(rede, "Circular")
        self.assertEqual([x["numero"] for x in lista], [1, 2, 3])
        self.assertEqual({x["tipo"] for x in lista}, {"Circular"})
        self.assertEqual([urllib.parse.parse_qs(urllib.parse.urlparse(u).query)["startrow"][0] for u in rede.pedidos],
                         ["0", "2", "4"])
        self.assertEqual(lista[0]["ementa"], "Ementa.")
        self.assertTrue((b.INDICE / "circular.json").exists())

    def test_indice_que_nao_fecha_com_o_total_anunciado_falha(self):
        linhas = [self.linha(1, "Circular", 1), self.linha(2, "Circular", 2), self.linha(3, "Circular", 3)]
        with self.assertRaisesRegex(RuntimeError, "incompleto"):
            b.montar_indice(RedeFalsa({"buscanormativos": self.paginas(linhas, 4)}), "Circular")
        self.assertFalse((b.INDICE / "circular.json").exists())


class Conversao(Base):
    def test_texto_atual_em_html(self):
        rede = RedeFalsa({"exibenormativo": detalhe(**CIRCULAR_3978)})
        item = {"id": "1", "tipo": "Circular", "numero": 3978}
        self.assertEqual(b.processar(rede, item, set()), ("ok", None))
        texto = self.ler("circulares/2020/circ-3978-2020.md")
        for trecho in ['titulo: "Circular nº 3.978, de 23 de janeiro de 2020"', 'orgao: "Banco Central do Brasil"',
                       'tipo: "Circular"', 'numero: "3978"', "data: 2020-01-23", "revogada: false",
                       'publicacao: "Publicada no DOU de 24/1/2020, Seção 1, p. 24-28."', 'data_publicacao: "2020-01-24"',
                       "fonte: \"https://www.bcb.gov.br/estabilidadefinanceira/exibenormativo?tipo=Circular&numero=3978\"",
                       "# Circular nº 3.978, de 23 de janeiro de 2020", "**Art. 70.** Esta Circular entra em vigor"]:
            self.assertIn(trecho, texto)
        self.assertNotIn("situacao:", texto)
        self.assertTrue((b.FONTE / "circulares/2020/circ-3978-2020.json.gz").exists())

    def test_texto_antigo_em_pre_refaz_paragrafos(self):
        rede = RedeFalsa({"exibenormativo": detalhe(**RESOLUCAO_2682)})
        item = {"id": "2", "tipo": "Resolução", "numero": 2682}
        self.assertEqual(b.processar(rede, item, set()), ("ok", None))
        texto = self.ler("resolucoes/1999/res-cmn-2682-1999.md")
        self.assertIn('titulo: "Resolução nº 2.682, de 21 de dezembro de 1999"', texto)
        self.assertIn('orgao: "Conselho Monetário Nacional"', texto)
        self.assertIn('situacao: "revogado"', texto)
        self.assertIn("revogada: true", texto)
        self.assertNotIn("-------", texto)
        self.assertRegex(texto, r"\n\*\*Art\. 1º\*\* +Determinar que as instituições")
        self.assertIn("\n\nI - nível AA;\n\nII - nível A;\n\n", texto)
        self.assertIn("Dispõe sobre critérios de classi- ficação", texto)  # as palavras ficam como na fonte

    def test_dia_primeiro_no_titulo(self):
        self.assertEqual(b.titulo_do_normativo("Resolução", 1, "1965-06-01"), "Resolução nº 1, de 1º de junho de 1965")


class Retencoes(Base):
    def reter(self, motivo, **campos):
        rede = RedeFalsa({"exibenormativo": detalhe(**{**CIRCULAR_3978, **campos})})
        estado, falha = b.processar(rede, {"id": "1", "tipo": "Circular", "numero": 3978}, set())
        self.assertEqual(estado, "retido")
        self.assertIn(motivo, falha["motivo"])
        self.assertFalse(list(b.PASTA.glob("*/*/*.md")))
        return falha

    def test_texto_so_nos_pdfs(self):
        falha = self.reter("texto só nos PDFs", Texto="<div>\u200b</div>", Documentos="C_Circ_0001_v1_O.pdf;57#;")
        self.assertEqual(falha["documentos"], "C_Circ_0001_v1_O.pdf;57#;")

    def test_imagem_no_texto(self):
        self.reter("imagem no texto", Texto=CIRCULAR_3978["Texto"] + '<p><img src="/x.png"></p>')

    def test_numero_ou_tipo_diferente_do_indice(self):
        self.reter("difere do índice", Numero=3979.0)
        self.reter("difere do índice", Tipo="Carta Circular")

    def test_data_futura(self):
        self.reter("data ausente ou futura", DataTexto="1/1/2999 00:00")

    def test_falha_igual_nao_se_repete_no_registro(self):
        falha = {"tipo": "Circular", "numero": 1, "id": "9", "motivo": "texto só nos PDFs"}
        ja = b.falhas_registradas()
        b.registrar_falha(falha, ja)
        b.registrar_falha(dict(falha), ja)
        b.registrar_falha(falha, b.falhas_registradas())
        self.assertEqual(len(b.FALHAS.read_text(encoding="utf-8").splitlines()), 1)


class Deduplicacao(Base):
    def test_ato_que_veio_do_dou_nao_entra_de_novo(self):
        dou = b.PASTA / "resolucoes" / "2017" / "resolucao-n-4-549-de-26-de-janeiro-de-2017-20359790.md"
        dou.parent.mkdir(parents=True)
        dou.write_text('---\ntitulo: "RESOLUÇÃO Nº 4.549, DE 26 DE JANEIRO DE 2017"\ntipo: "Resolução"\nnumero: "4549"\n'
                       'data: 2017-01-26\n---\n# RESOLUÇÃO Nº 4.549\n\nTexto.\n', encoding="utf-8")
        existentes = b.no_acervo()
        self.assertIn(("res-cmn", 4549), existentes)
        rede = RedeFalsa({})
        self.assertEqual(b.processar(rede, {"id": "3", "tipo": "Resolução", "numero": 4549}, existentes),
                         ("no_acervo", None))
        self.assertEqual(rede.pedidos, [])

    def test_gravado_por_este_coletor_conta_pelo_nome(self):
        md = b.PASTA / "cartas-circulares" / "1968" / "carta-circ-12-1968.md"
        md.parent.mkdir(parents=True)
        md.write_text("---\n---\n", encoding="utf-8")
        self.assertIn(("carta-circ", 12), b.no_acervo())

    def test_serie_pelo_titulo(self):
        casos = {
            ("RESOLUÇÃO BCB Nº 96, DE 19 DE MAIO DE 2021", "2021-05-19"): ("res-bcb", 96),
            ("RESOLUÇÃO Nº 96, DE 19 DE MAIO DE 2021", "2021-05-19"): ("res-bcb", 96),
            ("RESOLUÇÃO Nº 96, DE 10 DE JUNHO DE 1968", "1968-06-10"): ("res-cmn", 96),
            ("RESOLUÇÃO CMN Nº 4.966, DE 25 DE NOVEMBRO DE 2021", "2021-11-25"): ("res-cmn", 4966),
            ("RESOLUÇÃO Nº 4.838, DE 21 DE JULHO DE 2020", "2020-07-21"): ("res-cmn", 4838),
            ("CARTA CIRCULAR Nº 4.076, DE 1º DE OUTUBRO DE 2026", "2026-10-01"): ("carta-circ", 4076),
            ("CIRCULAR Nº 3.821, DE 20 DE JANEIRO DE 2017", "2017-01-20"): ("circ", 3821),
            ("INSTRUÇÃO NORMATIVA BCB Nº 763, DE 1º DE JUNHO DE 2026", "2026-06-01"): ("in-bcb", 763),
            ("PORTARIA Nº 100, DE 1º DE JUNHO DE 2026", "2026-06-01"): None,
        }
        for (titulo, data), esperado in casos.items():
            with self.subTest(titulo):
                self.assertEqual(b.serie_do_titulo(titulo, data), esperado)


class AnexoProprio(Base):
    FIM = "\n\nBrasília, 11 de novembro de 1999\n\nArminio Fraga Neto Presidente"

    def test_anexo_desta_resolucao_ausente_retem(self):
        # Resolução 2.666/1999: o texto da API termina na assinatura, sem o anexo que cita.
        texto = RESOLUCAO_2682["Texto"].replace("nos seguintes níveis:", "com títulos tipificados no anexo desta Resolução:")
        rede = RedeFalsa({"exibenormativo": detalhe(**{**RESOLUCAO_2682, "Texto": texto})})
        estado, falha = b.processar(rede, {"id": "2", "tipo": "Resolução", "numero": 2682}, set())
        self.assertEqual(estado, "retido")
        self.assertIn("anexo próprio", falha["motivo"])
        self.assertEqual(falha["remissao"], "anexo desta resolucao")

    def test_anexo_presente_ou_de_outro_ato_nao_retem(self):
        casos = {
            "regulamento depois do fecho (2.675/1999)": "**Art. 1º** Consolidar, nos termos do Regulamento anexo, as normas."
                + self.FIM + "\n\nRegulamento anexo à Resolução nº 2.675, de 21 de dezembro de 1999\n\n**Art. 1º** "
                + "Subordinam-se às normas deste Regulamento as operações com títulos de renda fixa." * 3,
            "seção do regulamento (Circular 4.027)": "**Art. 2º** Fica aprovado o Regulamento Anexo.\n\nDiretor\n\n"
                "REGULAMENTO ANEXO À CIRCULAR Nº 4.027, DE 12 DE JUNHO DE 2020\n\n**Art. 1º** Sujeitam-se.",
            "anexo de outro ato, com designador (2.674/1999)": "**Art. 1º** Os limites do Regulamento Anexo II à "
                "Resolução nº 2.099, de 17 de agosto de 1994." + self.FIM,
            "anexo de outra circular": "**Art. 1º** Nos termos do Anexo III da Circular nº 3.100." + self.FIM,
        }
        numeros = {"regulamento depois do fecho (2.675/1999)": 2675}
        for caso, corpo in casos.items():
            with self.subTest(caso):
                self.assertIsNone(b.anexo_proprio_ausente(corpo, numeros.get(caso, 1)))

    def test_formas_de_anexo_proprio_ausente(self):
        for trecho in ["Fica aprovado o Regulamento Anexo.", "conforme o modelo anexo.", "constantes do Anexo I desta Resolução.",
                       "nos termos do Regulamento anexo à Resolução nº 2.675."]:
            with self.subTest(trecho):
                self.assertIsNotNone(b.anexo_proprio_ausente("**Art. 1º** " + trecho + self.FIM, 2675))


class Recusa(unittest.TestCase):
    def test_403_interrompe(self):
        with self.assertRaises(b.Recusa):
            b.obter(RedeFalsa({"bcb": (403, b"", "")}), "https://www.bcb.gov.br/api/x")

    def test_429_depois_das_tentativas_interrompe(self):
        class Rede429:
            def get(self, url, accept="*/*"):
                raise RuntimeError(f"falhou após 4 tentativas: {url}: HTTP Error 429: Too Many Requests")
        with self.assertRaises(b.Recusa):
            b.obter(Rede429(), "https://www.bcb.gov.br/api/x")

    def test_outro_erro_de_rede_nao_e_recusa(self):
        class RedeFora:
            def get(self, url, accept="*/*"):
                raise RuntimeError(f"falhou após 4 tentativas: {url}: timed out")
        with self.assertRaises(RuntimeError) as ctx:
            b.obter(RedeFora(), "https://www.bcb.gov.br/api/x")
        self.assertNotIsInstance(ctx.exception, b.Recusa)


if __name__ == "__main__":
    unittest.main()
