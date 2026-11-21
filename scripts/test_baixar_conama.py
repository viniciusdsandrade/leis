"""Coletor do CONAMA (baixar_conama.py): salvaguardas da exceção ao robots.txt, listagem, conversão e retenções.

Não usa a rede: a listagem e o PDF vêm de recortes das respostas reais de conama.mma.gov.br (20/11/2026).
"""
import json
import os
import sys
import tempfile
import unittest
import urllib.parse
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import baixar_conama as c  # noqa: E402

# pdftotext -layout do PDF da Resolução 1/1986 (página do Livro das Resoluções do CONAMA), recortado.
TEXTO_1986 = (
    "      LICENCIAMENTO AMBIENTAL – Normas e procedimentos                          RESOLUÇÃO CONAMA nº 1 de 1986\n\n\n"
    "                         RESOLUÇÃO CONAMA nº 1, de 23 de janeiro de 1986\n"
    "               Publicada no DOU, de 17 de fevereiro de 1986, Seção 1, páginas 2548-2549\n\n"
    "                                             Dispõe sobre critérios básicos e diretrizes gerais para a\n"
    "                                             avaliação de impacto ambiental\n\n"
    "          O CONSELHO NACIONAL DO MEIO AMBIENTE - CONAMA, no uso das atribuições que\n"
    "      lhe confere o artigo 48 do Decreto nº 88.351, de 1º de junho de 1983, resolve:\n\n"
    "         Art. 1o Para efeito desta Resolução, considera-se impacto ambiental qualquer alteração\n"
    "      das propriedades físicas, químicas e biológicas do meio ambiente, que afetam:\n"
    "         I - a saúde, a segurança e o bem-estar da população;\n"
    "         II - as atividades sociais e econômicas;\n\n"
    "                                                                          RESOLUÇÕES DO CONAMA 637\n"
    "\f      LICENCIAMENTO AMBIENTAL – Normas e procedimentos                          RESOLUÇÃO CONAMA nº 1 de 1986\n\n"
    "         Art. 12. Esta Resolução entra em vigor na data de sua publicação.\n\n"
    "                        FLÁVIO PEIXOTO DA SILVEIRA - Presidente do Conselho\n\n"
    "         Este texto não substitui o publicado no DOU, de 17 de fevereiro de 1986.\n\n"
    "      638 RESOLUÇÕES DO CONAMA\n")
LINHA_1986 = {"numero": 1, "ano": 1986, "ementa": "Dispõe sobre critérios básicos e diretrizes gerais para a avaliação de "
              "impacto ambiental", "situacao": "Alterada pelas Resoluções nºs 11/1986, 05/1987, 237/1997 e 494/2020",
              "aid": "745", "arquivo": "Resol01_86.pdf"}
PDF = b"%PDF-1.6 recorte"


class RedeFalsa:
    def __init__(self, respostas):
        self.respostas, self.pedidos = respostas, []

    def get(self, url, accept="*/*", **_):
        self.pedidos.append(url)
        for trecho, resposta in self.respostas.items():
            if trecho in url:
                return resposta(url) if callable(resposta) else resposta
        raise AssertionError(f"pedido inesperado: {url}")


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        raiz = Path(self.tmp.name)
        for nome, valor in (("PASTA", raiz / "conama" / "resolucoes"), ("FONTE", raiz / "_fonte" / "conama"),
                            ("INDICE", raiz / "conama" / "_indice"), ("FALHAS", raiz / "conama" / "_falhas.jsonl")):
            p = patch.object(c, nome, valor)
            p.start()
            self.addCleanup(p.stop)


class Salvaguardas(Base):  # Base: as pastas do coletor apontam para um diretório temporário, nunca para o acervo
    def test_sem_a_flag_nao_roda(self):
        with patch.object(c, "Rede", side_effect=AssertionError("não deveria ir à rede")):
            with self.assertRaises(SystemExit):
                c.main([])

    def test_anos_cobertos_pelo_dou_ficam_fora_da_excecao(self):
        with patch.object(c, "Rede", side_effect=AssertionError("não deveria ir à rede")):
            for args in (["--apesar-do-robots", "--ate", "2017"], ["--apesar-do-robots", "--de", "2020", "--ate", "2026"]):
                with self.subTest(args), self.assertRaises(SystemExit):
                    c.main(args)

    def test_taxa_da_excecao(self):
        self.assertEqual(c.AUTORIZACAO["rps"], 0.2)
        self.assertEqual(c.AUTORIZACAO["host"], urllib.parse.urlparse(c.BASE).hostname)
        criadas = []
        with patch.object(c, "Rede", side_effect=lambda rps: criadas.append(rps) or RedeFalsa(
                {"atosnormativos.getList": (200, json.dumps({"data": {"total": 0, "rows": []}}).encode(), "")})):
            self.assertEqual(c.main(["--apesar-do-robots", "--de", "1984", "--ate", "1984"]), 0)
        self.assertEqual(criadas, [0.2])
        self.assertTrue(str(c.INDICE).startswith(self.tmp.name))  # o índice vazio do teste não toca o do acervo


class Listagem(Base):
    def linha(self, numero, ano="1986", nome="Resolução"):
        return {"numero": f"{numero:03d}", "ano": ano, "descricao": " Ementa  dela. ", "status": None, "aid": str(numero),
                "anome": f"Resolução {numero}.pdf", "nomeato": nome, "usuario": "nome de servidor que não entra"}

    def test_pagina_ate_o_total_e_filtra_resolucoes_do_ano(self):
        linhas = [self.linha(3), self.linha(1), self.linha(9, nome="Moção"), self.linha(2, ano="1987")]

        def resposta(url):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
            inicio = int(q["offset"][0])
            return 200, json.dumps({"data": {"total": len(linhas), "rows": linhas[inicio:inicio + 2]}}).encode(), ""
        with patch.object(c, "POR_PAGINA", 2):
            itens = c.listar_ano(RedeFalsa({"atosnormativos.getList": resposta}), 1986)
        self.assertEqual([i["numero"] for i in itens], [1, 3])
        self.assertEqual(itens[0]["ementa"], "Ementa dela.")
        self.assertNotIn("usuario", itens[0])

    def test_listagem_que_nao_fecha_falha(self):
        resposta = (200, json.dumps({"data": {"total": 5, "rows": [self.linha(1)]}}).encode(), "")
        rede = RedeFalsa({"offset=0": resposta, "offset=1": (200, json.dumps({"data": {"total": 5, "rows": []}}).encode(), "")})
        with self.assertRaisesRegex(RuntimeError, "incompleta"):
            c.listar_ano(rede, 1986)


class Conversao(Base):
    def test_pdf_do_livro_vira_markdown_sem_cabecalho_e_rodape(self):
        rede = RedeFalsa({"arquivo.download&id=745": (200, PDF, "application/pdf")})
        with patch.object(c, "extrair_texto", return_value=(None, TEXTO_1986)):
            self.assertEqual(c.processar(rede, LINHA_1986), ("ok", None))
        texto = (c.PASTA / "1986" / "res-conama-1-1986.md").read_text(encoding="utf-8")
        for trecho in ['titulo: "Resolução CONAMA nº 1, de 23 de janeiro de 1986"', 'orgao: "Conselho Nacional do Meio Ambiente"',
                       'tipo: "Resolução"', 'numero: "1"', "data: 1986-01-23", "revogada: false",
                       'situacao: "Alterada pelas Resoluções nºs 11/1986, 05/1987, 237/1997 e 494/2020"',
                       'publicacao: "Publicada no DOU, de 17 de fevereiro de 1986, Seção 1, páginas 2548-2549"',
                       'data_publicacao: "1986-02-17"', 'fonte: "https://conama.mma.gov.br/?option=com_sisconama&task=arquivo.download&id=745"',
                       "**Art. 1o** Para efeito desta Resolução", "\n\nI - a saúde, a segurança", "**Art. 12.** Esta Resolução"]:
            self.assertIn(trecho, texto)
        for fora in ("LICENCIAMENTO AMBIENTAL – Normas", "RESOLUÇÕES DO CONAMA 637", "638 RESOLUÇÕES DO CONAMA"):
            self.assertNotIn(fora, texto)
        self.assertTrue((c.FONTE / "1986" / "res-conama-1-1986.pdf.gz").exists())

    def test_revogada_pela_situacao(self):
        rede = RedeFalsa({"arquivo.download": (200, PDF, "application/pdf")})
        linha = {**LINHA_1986, "situacao": "Revogada pela Resolução nº 237, de 1997."}
        with patch.object(c, "extrair_texto", return_value=(None, TEXTO_1986)):
            c.processar(rede, linha)
        self.assertIn("revogada: true", (c.PASTA / "1986" / "res-conama-1-1986.md").read_text(encoding="utf-8"))

    def test_revogada_no_meio_da_situacao_e_revogacao_parcial(self):
        # Resolução 20/1986 na listagem: alterada e depois revogada
        casos = {"Alterada pela Resolução nº 274, de 2000. Revogada pela Resolução nº 357, de 2005.": "revogada: true",
                 "Alterada pela Resolução nº 237/97 (revogados os art. 3º e 7º)": "revogada: false"}
        for situacao, esperado in casos.items():
            with self.subTest(situacao):
                for md in c.PASTA.glob("*/*.md"):
                    md.unlink()
                with patch.object(c, "extrair_texto", return_value=(None, TEXTO_1986)):
                    c.processar(RedeFalsa({"arquivo.download": (200, PDF, "application/pdf")}), {**LINHA_1986, "situacao": situacao})
                self.assertIn(esperado, (c.PASTA / "1986" / "res-conama-1-1986.md").read_text(encoding="utf-8"))

    def test_ementa_sem_metadados_e_publicacao_da_listagem(self):
        descricao = ("Dispõe sobre a classificação das águas doces, salobras e salinas do Território Nacional . - Data da "
                     "legislação: 18/06/1986 - Publicação DOU , de 30/07/1986, págs. 11356-11361")
        self.assertEqual(c.ementa_e_publicacao(descricao), (
            "Dispõe sobre a classificação das águas doces, salobras e salinas do Território Nacional",
            "Publicada no DOU, de 30/07/1986, págs. 11356-11361", "1986-07-30"))
        self.assertEqual(c.ementa_e_publicacao('"Dispõe sobre transporte de produtos perigosos" - Data da legislação: '
                                               '23/01/1986 - Publicação DOU nº 043, de 05/03/1993, págs. 2653')[1:],
                         ("Publicada no DOU nº 043, de 05/03/1993, págs. 2653", "1993-03-05"))
        sem_pub = TEXTO_1986.replace("Publicada no DOU, de 17 de fevereiro de 1986, Seção 1, páginas 2548-2549", "")
        with patch.object(c, "extrair_texto", return_value=(None, sem_pub)):
            c.processar(RedeFalsa({"arquivo.download": (200, PDF, "application/pdf")}), {**LINHA_1986, "ementa": descricao})
        texto = (c.PASTA / "1986" / "res-conama-1-1986.md").read_text(encoding="utf-8")
        self.assertIn('ementa: "Dispõe sobre a classificação das águas doces, salobras e salinas do Território Nacional"', texto)
        self.assertIn('publicacao: "Publicada no DOU, de 30/07/1986, págs. 11356-11361"', texto)
        self.assertIn('data_publicacao: "1986-07-30"', texto)


class Retencoes(Base):
    def test_numero_repetido_na_listagem_de_outro_registro_fica_retido(self):
        rede = RedeFalsa({"arquivo.download": (200, PDF, "application/pdf")})
        with patch.object(c, "extrair_texto", return_value=(None, TEXTO_1986)):
            self.assertEqual(c.processar(rede, LINHA_1986), ("ok", None))
            self.assertEqual(c.processar(rede, LINHA_1986), ("pulado", None))  # o mesmo registro: já gravado
            estado, falha = c.processar(rede, {**LINHA_1986, "aid": "809", "arquivo": "CONAMA_RES_CONS_1986_01A.pdf"})
        self.assertEqual(estado, "retido")
        self.assertIn("número repetido", falha["motivo"])
        self.assertEqual(len(rede.pedidos), 1)


    def reter(self, motivo, linha=LINHA_1986, bruto=PDF, texto=TEXTO_1986):
        rede = RedeFalsa({"arquivo.download": (200, bruto, "application/pdf")})
        with patch.object(c, "extrair_texto", return_value=(None, texto)):
            estado, falha = c.processar(rede, linha)
        self.assertEqual(estado, "retido")
        self.assertIn(motivo, falha["motivo"])
        self.assertFalse(list(c.PASTA.glob("*/*.md")))

    def test_arquivo_que_nao_e_pdf(self):
        self.reter("não é PDF", bruto=b"<html>erro</html>")

    def test_pdf_escaneado(self):
        self.reter("exige OCR", texto="\f\f  ")

    def test_epigrafe_de_outro_numero_ou_ano(self):
        self.reter("epígrafe", linha={**LINHA_1986, "numero": 2})
        self.reter("epígrafe", linha={**LINHA_1986, "ano": 1987})

    def test_sem_arquivo_na_listagem(self):
        self.reter("não traz arquivo", linha={**LINHA_1986, "aid": None})


if __name__ == "__main__":
    unittest.main()
