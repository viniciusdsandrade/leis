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

    def test_fecho_do_texto_da_a_data_quando_o_portal_traz_a_da_publicacao(self):
        fecho = "<p>Brasília, 22 de janeiro de 2020.</p><p>Otávio"
        texto = CIRCULAR_3978["Texto"].replace("<p>Otávio", fecho)
        self.assertEqual(b.processar(RedeFalsa({"exibenormativo": detalhe(**{**CIRCULAR_3978, "Texto": texto})}),
                                     {"id": "1", "tipo": "Circular", "numero": 3978}, set()), ("ok", None))
        md = self.ler("circulares/2020/circ-3978-2020.md")
        for trecho in ['titulo: "Circular nº 3.978, de 22 de janeiro de 2020"', "data: 2020-01-22", 'data_no_portal: "2020-01-23"',
                       "# Circular nº 3.978, de 22 de janeiro de 2020"]:
            self.assertIn(trecho, md)

    def test_fecho_que_nao_resolve_deixa_a_data_do_portal(self):
        casos = {"dois fechos com datas diferentes": "<p>Brasília, 22 de janeiro de 2020.</p><p>Brasília (DF), 20 de janeiro de 2020.</p>",
                 "fecho depois da data do portal": "<p>Brasília, 24 de janeiro de 2020.</p>",
                 "fecho mais de 30 dias antes": "<p>Brasília, 20 de dezembro de 2019.</p>",
                 "fecho na data do portal": "<p>BRASÍLIA (DF), 23 DE JANEIRO DE 2020</p>",
                 "data que não existe": "<p>Brasília, 31 de fevereiro de 2020.</p>"}
        for caso, fecho in casos.items():
            with self.subTest(caso):
                texto = CIRCULAR_3978["Texto"].replace("<p>Otávio", fecho + "<p>Otávio")
                b.processar(RedeFalsa({"exibenormativo": detalhe(**{**CIRCULAR_3978, "Texto": texto})}),
                            {"id": "1", "tipo": "Circular", "numero": 3978}, set())
                md = self.ler("circulares/2020/circ-3978-2020.md")
                self.assertIn("data: 2020-01-23", md)
                self.assertNotIn("data_no_portal", md)
                (b.PASTA / "circulares/2020/circ-3978-2020.md").unlink()

    def test_datas_do_fecho(self):
        self.assertEqual(b.datas_do_fecho("**BRASÍLIA (DF), 27 DE FEVEREIRO DE 1991**\n\nBrasília, 1º de março de 1991.\n\nBrasília-DF, em 2 de março de 1991"),
                         {"1991-02-27", "1991-03-01", "1991-03-02"})
        self.assertEqual(b.datas_do_fecho("em sessão realizada em Brasília no dia 22 de janeiro de 2020"), set())

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
            # Circular 2.389/1993, Resolução 2.772/2000, Circular 283/1975, Resolução 1.819/1991 e Circular 3.258/2004
            "designadores em lista": "**Art. 1º** Recursos ingressados nos termos dos Regulamentos Anexos I, II, III e IV "
                "à Resolução nº 1.289." + self.FIM,
            "designadores ligados por e": "**Art. 1º** Previstos nos Regulamentos Anexos II e IV à Resolução 2.099."
                + self.FIM,
            "espécie no plural": "**Art. 1º** Normas definidas nos Regulamentos anexos às Circulares nºs 251 e 252."
                + self.FIM,
            "espécie partida na linha": "ALTERA OS REGULAMENTOS ANEXOS À RESOLU- ÇÃO Nº 1.289." + self.FIM,
            "respectivos anexos de ato citado": "**Art. 1º** Pela Carta-Circular 2.795 e seus respectivos Regulamentos "
                "anexos." + self.FIM,
            "em anexo a outra coisa": "**Art. 1º** O envio, em anexo à documentação encaminhada." + self.FIM,
            # Circulares 2.782/1997, 2.954/1999 e 218/1973
            "ato referido": "**Art. 5º** Fica incluído no mapa anexo à referida Circular o subtítulo." + self.FIM,
            "carta-circular partida na linha": "**Art. 4º** Ficam excluídos dos documentos Anexos I e II à Car- "
                "ta-Circular nº 2.776." + self.FIM,
            "comunicado": "mediante o preenchimento dos formulários anexos aos Comunicados FIRCE nºs 10 e 11."
                + self.FIM,
        }
        numeros = {"regulamento depois do fecho (2.675/1999)": 2675}
        for caso, corpo in casos.items():
            with self.subTest(caso):
                self.assertIsNone(b.anexo_proprio_ausente(corpo, numeros.get(caso, 1)))

    def test_formas_de_anexo_proprio_ausente(self):
        for trecho in ["Fica aprovado o Regulamento Anexo.", "conforme o modelo anexo.", "constantes do Anexo I desta Resolução.",
                       "nos termos do Regulamento anexo à Resolução nº 2.675.",
                       # Circular 821/1983 e Carta-Circular 1.339/1986: o manual que a carta atualiza vem em folhas anexas
                       "Comunicamos as alterações do MCR, conforme folhas anexas, destinadas à atualização do Manual.",
                       "encontra-se na folha anexa a alteração necessária.", "nos leiautes das instruções anexas.",
                       "Em anexo, encontram-se as folhas.", "conforme tabelas anexas.", "anexa a esta Carta–Circular."]:
            with self.subTest(trecho):
                self.assertIsNotNone(b.anexo_proprio_ausente("**Art. 1º** " + trecho + self.FIM, 2675))

    def test_nota_do_portal_de_anexo_a_disposicao_na_sede(self):
        # Circular 1.307/1988: o texto termina na nota de que o anexo não está no portal
        corpo = ("Comunicamos as alterações no Manual de Crédito Rural.\n\nBrasília-DF, 30 de março de 1988\n\n"
                 "Hélio Ribeiro de Oliveira Diretor\n\nObs: o anexo deste normativo encontra-se à disposição dos "
                 "interessados na Sede do Banco Central do Brasil.")
        self.assertEqual(b.anexo_proprio_ausente(corpo, 1307), "anexo deste normativo")

    def test_folhas_do_manual_no_texto_do_portal(self):
        # Resolução 4.364/2014: as folhas do MCR vêm no próprio texto, com os cabeçalhos do manual
        corpo = ("**Art. 3º** Ficam aprovadas as disposições constantes das folhas anexas.\n\nBrasília, 28 de agosto de "
                 "2014.\n\nAlexandre Antonio Tombini Presidente\n\nTÍTULO : CRÉDITO RURAL\n\nCAPÍTULO: Programa "
                 "Nacional de Fortalecimento da Agricultura Familiar (Pronaf) - 10\n\nSEÇÃO : Créditos - 17")
        self.assertIsNone(b.anexo_proprio_ausente(corpo, 4364))
        self.assertIsNotNone(b.anexo_proprio_ausente(corpo.split("TÍTULO")[0], 4364))

    def test_anexo_depois_do_fecho_com_df(self):
        # Resolução 514/1979: as folhas do MNI vêm depois da assinatura, e o fecho é "Brasília-DF,"
        corpo = ("II - O MNI passa a vigorar com nova redação, constante das folhas anexas.\n\nBrasília-DF, 8 de fevereiro "
                 "de 1979\n\nPaulo H. Pereira Lira Presidente\n\n" + "1 - As operações ficam sujeitas às normas. " * 8)
        self.assertIsNone(b.anexo_proprio_ausente(corpo, 514))
        self.assertIsNone(b.anexo_proprio_ausente(corpo.replace("Brasília-DF,", "Brasília (DF),"), 514))
        self.assertIsNotNone(b.anexo_proprio_ausente(corpo.split("Paulo")[0] + "Paulo H. Pereira Lira Presidente", 514))


# Recortes do PDF da versão original da Carta-Circular 2.989/2001 (pdftotext -layout, 21/11/2026).
CARTA_2989 = dict(Titulo="Carta Circular Nº 2.989", Tipo="Carta Circular", Numero=2989.0, DataTexto="12/12/2001 00:00",
                  Assunto="Divulga os novos padrões de cores a serem utilizados na confecção de etiquetas.",
                  Documentos="C_Circ_2989_v1_O.pdf;16#;C_Circ_2989_v2_L.pdf;18#;", Texto="<div>​</div>")
PDF_2989 = ("                                        CARTA-CIRCULAR Nº 2989\n\n"
            "                                                    Divulga os novos padrões de cores a serem\n"
            "                                                    utilizados na confecção de etiquetas.\n\n"
            "                Tendo em vista a introdução de novas denominações no meio circulante nacional,\n"
            "informamos os novos padrões de cores a serem utilizados na confecção das etiquetas.\n\n"
            "                                        Brasília, 12 de dezembro de 2001.\n")
URL_2989 = "https://www.bcb.gov.br/pre/normativos/c_circ/2001/pdf/c_circ_2989_v1_o.pdf"
# a carta com mais um parágrafo: o modo da página em imagem exige que o texto restante não seja só a epígrafe
PDF_2989_LONGO = PDF_2989.replace("etiquetas.\n\n", "etiquetas.\n\n                As etiquetas confeccionadas nos padrões "
                                  "anteriores poderão ser utilizadas até o esgotamento dos estoques existentes nas "
                                  "instituições, observadas as demais condições da regulamentação em vigor.\n\n", 1)


class PdfOriginal(Base):
    ITEM = {"id": "46990", "tipo": "Carta Circular", "numero": 2989, "data": "2001-12-12"}

    def rede(self, pdf=(200, b"%PDF-1.4 recorte", "application/pdf"), **campos):
        return RedeFalsa({"exibenormativo": detalhe(**{**CARTA_2989, **campos}), "c_circ_2989_v1_o.pdf": pdf})

    def processar(self, rede, texto=PDF_2989, imagens=(), imagem_pendente=False):
        with patch.object(b, "ler_pdf", return_value=(texto, list(imagens))):
            return b.processar(rede, dict(self.ITEM), set(), pdf=True, imagem_pendente=imagem_pendente)

    def test_arquivo_e_endereco_da_versao_original(self):
        self.assertEqual(b.arquivo_original(CARTA_2989["Documentos"]), "C_Circ_2989_v1_O.pdf")
        self.assertIsNone(b.arquivo_original("C_Circ_2989_v2_L.pdf;18#;"))
        self.assertIsNone(b.arquivo_original(None))
        self.assertEqual(b.url_do_original("C_Circ_2989_v1_O.pdf", "2001"), URL_2989)
        self.assertEqual(b.url_do_original("Res_0580_v1_O.pdf", "1979"),
                         "https://www.bcb.gov.br/pre/normativos/res/1979/pdf/res_0580_v1_o.pdf")
        self.assertEqual(b.url_do_original("Circ_3340_v1_O.pdf", "2007"),
                         "https://www.bcb.gov.br/pre/normativos/circ/2007/pdf/circ_3340_v1_o.pdf")

    def test_especie_e_numero_no_alto_do_pdf(self):
        for texto, tipo, numero in ((PDF_2989, "Carta Circular", 2989),
                                    ("        CARTA–CIRCULAR Nº. 1339\nÀs Instituições", "Carta Circular", 1339),
                                    ("CARTA-CIRCULAR-N° 1177\nEm decorrência", "Carta Circular", 1177),
                                    ("CARTA-CIRCULAR Nº 1.237\nEm decorrência", "Carta Circular", 1237),
                                    ("1\nRESOLUÇÃO Nº 580\nO BANCO CENTRAL DO BRASIL", "Resolução", 580),
                                    ("CIRCULAR Nº 3.340\nAltera", "Circular", 3340),
                                    ("CIRCULAR 3.377\nDispõe sobre a remessa de informações", "Circular", 3377)):
            with self.subTest(texto[:40]):
                self.assertTrue(b.numero_no_pdf(texto, tipo, numero))
        for texto, tipo, numero in (("CARTA-CIRCULAR Nº 1.238", "Carta Circular", 1237),
                                    ("CARTA-CIRCULAR Nº 2989", "Circular", 2989),  # carta-circular não é circular
                                    ("CARTA–CIRCULAR Nº 2989", "Circular", 2989),
                                    ("CIRCULAR Nº 2989", "Carta Circular", 2989),
                                    ("x" * 700 + " CIRCULAR Nº 2989", "Circular", 2989)):  # só vale no alto
            with self.subTest(texto[-30:]):
                self.assertFalse(b.numero_no_pdf(texto, tipo, numero))

    def test_data_junto_do_numero(self):
        rodape = "CARTA-CIRCULAR Nº 701\n\nTexto.\n\nCarta-Circular nº 701, de 29 de dezembro de 1981\n\f"
        self.assertEqual(b.data_no_pdf(rodape * 2, "Carta Circular", 701), {"1981-12-29"})
        self.assertEqual(b.data_no_pdf("Resolução nº 580, de 1º de novembro de 1979", "Resolução", 580), {"1979-11-01"})
        self.assertEqual(b.data_no_pdf(PDF_2989, "Carta Circular", 2989), set())  # o fecho não traz o número
        self.assertEqual(b.data_no_pdf("Circular nº 3.341, de 18 de janeiro de 2007", "Circular", 3340), set())

    def test_paginas_em_imagem(self):
        cabecalho = ("page   num  type   width height color comp bpc  enc interp  object ID x-ppi y-ppi size ratio\n"
                     "--------------------------------------------------------------------------------------------\n")
        info = "Page    1 size: 595.32 x 841.92 pts (A4)\nPage    2 size: 595.32 x 841.92 pts (A4)\n"
        logo = "   1     0 image     576    91  rgb     3   8  jpeg   no        10  0   102   102 10.2K 6.6%\n"
        scan = "   2     1 image     618   861  gray    1   8  jpeg   no        15  0    96    96 50.1K 9.6%\n"
        mascara = "   2     2 smask     618   861  gray    1   8  image  no        16  0    96    96 1.0K 1.0%\n"
        self.assertEqual(b.paginas_em_imagem(cabecalho, info), [])
        self.assertEqual(b.paginas_em_imagem(cabecalho + logo, info), [])  # logotipo de 5% da página
        self.assertEqual(b.paginas_em_imagem(cabecalho + logo + scan + mascara, info), [2])
        with self.assertRaises(RuntimeError):
            b.paginas_em_imagem("", info)

    def test_grava_o_texto_do_pdf_original_e_refaz_do_cache(self):
        rede = self.rede()
        self.assertEqual(self.processar(rede), ("ok", None))
        self.assertEqual(rede.pedidos[1], URL_2989)
        md = self.ler("cartas-circulares/2001/carta-circ-2989-2001.md")
        for trecho in ['titulo: "Carta Circular nº 2.989, de 12 de dezembro de 2001"', "data: 2001-12-12",
                       'versao_texto: "original: PDF da versão original (v1)', f'fonte_texto: "{URL_2989}"',
                       "informamos os novos padrões de cores"]:
            self.assertIn(trecho, md)
        for cache in ("carta-circ-2989-2001.pdf.gz", "carta-circ-2989-2001.json.gz"):
            self.assertTrue((b.FONTE / "cartas-circulares/2001" / cache).exists())
        (b.PASTA / "cartas-circulares/2001/carta-circ-2989-2001.md").unlink()
        self.assertEqual(self.processar(RedeFalsa({})), ("ok", None))  # do cache, sem rede

    def test_sem_o_pdf_original_retem(self):
        # de 2016 em diante o PDF não está em /pre/normativos/ (Carta-Circular 3.756/2016, 21/11/2026)
        estado, falha = self.processar(self.rede(pdf=(404, b"", "")))
        self.assertEqual(estado, "retido")
        self.assertIn("não está em /pre/normativos/", falha["motivo"])
        self.assertEqual(falha["pdf"], URL_2989)

    def test_numero_nao_utilizado_retem_com_motivo_proprio(self):
        # Carta-Circular 3.717/2015 e outras: o PDF do portal só diz isso
        estado, falha = self.processar(self.rede(), "Número não utilizado.\n")
        self.assertEqual(estado, "retido")
        self.assertIn("número não utilizado", falha["motivo"])

    def test_data_do_proprio_ato_quando_o_portal_traz_a_da_publicacao(self):
        # Circular 3.467/2009: "de 14 de setembro de 2009" no PDF; o portal, 15/9, a da publicação
        self.assertEqual(b.data_do_ato({"2009-09-14"}, "2009-09-15"), "2009-09-14")
        self.assertIsNone(b.data_do_ato({"2011-04-15", "2011-04-25"}, "2011-04-25"))  # Circular 3.532: duas datas
        self.assertIsNone(b.data_do_ato({"2001-12-13"}, "2001-12-12"))  # o PDF depois do portal
        self.assertIsNone(b.data_do_ato({"2001-10-01"}, "2001-12-12"))  # mais de 30 dias
        self.assertIsNone(b.data_do_ato({"inválida"}, "2001-12-12"))
        texto = PDF_2989 + "\nCarta-Circular nº 2.989, de 11 de dezembro de 2001\n"
        self.assertEqual(self.processar(self.rede(), texto), ("ok", None))
        md = self.ler("cartas-circulares/2001/carta-circ-2989-2001.md")
        self.assertIn('titulo: "Carta Circular nº 2.989, de 11 de dezembro de 2001"', md)
        self.assertIn("data: 2001-12-11", md)

    def test_portal_sem_a_versao_original_retem(self):
        estado, falha = self.processar(self.rede(Documentos="C_Circ_2989_v2_L.pdf;18#;"))
        self.assertIn("não lista o da versão original", falha["motivo"])

    def test_retencoes_do_texto_do_pdf(self):
        rede = self.rede()
        casos = (((PDF_2989, [2, 3]), "página em imagem"),
                 ((PDF_2989.replace("Nº 2989", "Nº 2988"), []), "difere do índice"),
                 ((PDF_2989 + "\nCarta-Circular nº 2.989, de 13 de dezembro de 2001\n", []), "data no PDF difere"),
                 ((PDF_2989.replace("etiquetas.\n\n", "etiquetas, conforme folhas anexas.\n\n", 1), []), "anexo próprio"))
        for (texto, imagens), motivo in casos:
            with self.subTest(motivo):
                estado, falha = self.processar(rede, texto, imagens)
                self.assertEqual(estado, "retido")
                self.assertIn(motivo, falha["motivo"])
        self.assertFalse(list(b.PASTA.glob("*/*/*.md")))

    def test_folhas_do_manual_no_proprio_pdf_contam_como_anexo(self):
        # Carta-Circular 999/1984: a carta remete às folhas do MNI, que vêm nas 16 páginas seguintes do mesmo PDF
        carta = PDF_2989.replace("etiquetas.\n\n", "etiquetas, nas folhas anexas.\n\n", 1)
        folhas = ("\fTÍTULO: CAIXAS ECONÔMICAS – 11\nCAPÍTULO: Operações Ativas e Passivas – 9\n"
                  "SEÇÃO: Depósito à Vista – 12\n1 – As caixas econômicas estaduais não podem manter contas.\n"
                  "Carta-Circular nº 999, de 23.02.84 – At. MNI nº 728\n")
        self.assertEqual(self.processar(self.rede(), carta + folhas), ("ok", None))
        self.assertIn("As caixas econômicas estaduais", self.ler("cartas-circulares/2001/carta-circ-2989-2001.md"))
        (b.PASTA / "cartas-circulares/2001/carta-circ-2989-2001.md").unlink()
        estado, falha = self.processar(self.rede(), carta + "\fTÍTULO: CAIXAS ECONÔMICAS – 11\n")  # uma marca só
        self.assertEqual(estado, "retido")
        self.assertIn("ausente do PDF da versão original", falha["motivo"])

    def test_texto_sem_paginas_em_imagem(self):
        carta, anexo = "Comunicamos " * 30, "\f\f"
        self.assertEqual(b.texto_sem_paginas_em_imagem(carta + anexo, [2, 3]), carta + anexo)
        # a linha de cabeçalho que a página em imagem traz na camada de texto sai com ela
        self.assertEqual(b.texto_sem_paginas_em_imagem(carta + "\fCarta-Circular nº 2.989 - fl. 2\f", [2]), carta + "\f\f")
        self.assertIsNone(b.texto_sem_paginas_em_imagem(carta + anexo, [1, 2]))  # a primeira página é imagem
        self.assertIsNone(b.texto_sem_paginas_em_imagem(carta + "\f" + "texto do OCR da origem " * 20, [2]))
        self.assertIsNone(b.texto_sem_paginas_em_imagem("Comunicamos.\f", [2]))  # sobra curta demais

    def test_pagina_em_imagem_como_pendencia(self):
        carta = PDF_2989_LONGO.replace("etiquetas.\n\n", "etiquetas, conforme modelos anexos.\n\n", 1)
        estado, info = self.processar(self.rede(), carta + "\f\f\f", [2, 3], imagem_pendente=True)
        self.assertEqual(estado, "pendente")
        self.assertEqual({k: info[k] for k in ("path", "tipo", "numero", "paginas_em_imagem", "paginas", "pdf")},
                         {"path": "reguladores/bcb/cartas-circulares/2001/carta-circ-2989-2001.md", "tipo": "Carta Circular",
                          "numero": 2989, "paginas_em_imagem": [2, 3], "paginas": 3, "pdf": URL_2989})
        md = self.ler("cartas-circulares/2001/carta-circ-2989-2001.md")
        self.assertIn('paginas_em_imagem: "2, 3 de 3: anexo, tabela ou formulário escaneado no PDF, sem transcrição', md)
        self.assertIn("conforme modelos anexos", md)  # a remissão ao anexo não retém: o anexo é a pendência

    def test_pagina_em_imagem_que_nao_da_para_tirar_continua_retida(self):
        for caso, (texto, imagens) in {"primeira página": (PDF_2989_LONGO + "\f", [1]),
                                       "camada de texto na imagem": (PDF_2989_LONGO + "\f" + "texto do OCR da origem " * 20, [2]),
                                       "sobra curta": (PDF_2989 + "\f", [2])}.items():
            with self.subTest(caso):
                estado, falha = self.processar(self.rede(), texto, imagens, imagem_pendente=True)
                self.assertEqual((estado, falha["motivo"]), ("retido", b.IMAGEM_NO_PDF))
        # as outras conferências do PDF continuam valendo
        estado, falha = self.processar(self.rede(), PDF_2989_LONGO.replace("Nº 2989", "Nº 2988") + "\f", [2], imagem_pendente=True)
        self.assertIn("difere do índice", falha["motivo"])
        self.assertFalse(list(b.PASTA.glob("*/*/*.md")))

    def test_modo_pagina_em_imagem_troca_a_retencao_e_anota_a_pendencia(self):
        b.INDICE.mkdir(parents=True)
        outro = {"id": "1", "tipo": "Carta Circular", "numero": 2990, "data": "2001-12-13"}
        (b.INDICE / "carta-circular.json").write_text(json.dumps([self.ITEM, outro]), encoding="utf-8")
        linhas = [{"tipo": "Carta Circular", "numero": 2989, "id": "46990", "motivo": b.IMAGEM_NO_PDF},
                  {"tipo": "Carta Circular", "numero": 2990, "id": "1", "motivo": b.IMAGEM_NO_PDF},
                  {"tipo": "Carta Circular", "numero": 7, "id": "7", "motivo": b.SO_PDF}]
        b.FALHAS.write_text("".join(json.dumps(l) + "\n" for l in linhas), encoding="utf-8")
        rede = RedeFalsa({"p2=2989": detalhe(**CARTA_2989), "c_circ_2989_v1_o.pdf": (200, b"%PDF-1.4 a", "application/pdf"),
                          "p2=2990": detalhe(**{**CARTA_2989, "Numero": 2990.0, "DataTexto": "13/12/2001 00:00",
                                                 "Documentos": "C_Circ_2990_v1_O.pdf;16#;"}),
                          "c_circ_2990_v1_o.pdf": (200, b"%PDF-1.4 b", "application/pdf")})
        lidos = iter([(PDF_2989_LONGO.replace("2989", "2990") + "\f", [1]), (PDF_2989_LONGO + "\f", [2])])
        with patch.object(b, "Rede", lambda rps: rede), patch.object(b, "ler_pdf", lambda pdf: next(lidos)):
            self.assertEqual(b.main(["--tipos", "Carta Circular", "--pagina-em-imagem"]), 0)
        # a 2990 (mais recente, processada antes) tem a primeira página em imagem e continua retida; a 7 não é deste modo
        self.assertEqual(sorted((json.loads(l)["numero"], json.loads(l)["motivo"]) for l in b.FALHAS.read_text(encoding="utf-8").splitlines()),
                         [(7, b.SO_PDF), (2990, b.IMAGEM_NO_PDF)])
        pendencias = [json.loads(l) for l in (b.PASTA / "_paginas_em_imagem.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertEqual([(p["numero"], p["paginas_em_imagem"]) for p in pendencias], [(2989, [2])])
        self.assertTrue((b.PASTA / "cartas-circulares/2001/carta-circ-2989-2001.md").exists())

    def test_modo_pdf_troca_so_a_retencao_antiga_do_pdf(self):
        b.INDICE.mkdir(parents=True)
        outro = {"id": "1", "tipo": "Carta Circular", "numero": 1, "data": "1965-01-01"}
        (b.INDICE / "carta-circular.json").write_text(json.dumps([self.ITEM, outro]), encoding="utf-8")
        b.FALHAS.write_text(json.dumps({"tipo": "Carta Circular", "numero": 2989, "id": "46990", "motivo": b.SO_PDF})
                            + "\n" + json.dumps({"tipo": "Carta Circular", "numero": 1, "id": "1",
                                                 "motivo": "imagem no texto: o conteúdo visual não entra no Markdown"})
                            + "\n", encoding="utf-8")
        rede = self.rede()
        with patch.object(b, "Rede", lambda rps: rede), patch.object(b, "ler_pdf", return_value=(PDF_2989, [])):
            self.assertEqual(b.main(["--tipos", "Carta Circular", "--pdf"]), 0)
        self.assertEqual([json.loads(l)["numero"] for l in b.FALHAS.read_text(encoding="utf-8").splitlines()], [1])
        self.assertEqual(len(rede.pedidos), 2)  # a 1 não é refeita: não está retida por texto só nos PDFs
        self.assertTrue((b.PASTA / "cartas-circulares/2001/carta-circ-2989-2001.md").exists())


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
