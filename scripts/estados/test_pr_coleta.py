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


ANOS_HTML = "<a href=\"javascript:listarAtos('1955', '1955')\">1955</a><a href=\"javascript:listarAtos('1955', '1954')\">1954</a>"
# Recortes das respostas reais da fonte (13/11/2026). A página de erro também diz "Nenhum registro encontrado";
# o que a separa do mês sem atos é a mensagem atribuída a globalAjaxMsgError.
ERRO_HTML = """<script type="text/javascript">
		globalAjaxMsgError = '<table align="center"><tr>';
		globalAjaxMsgError += '<td><img src="/legislacao/images/icon_msg_aviso.png"></td>';
		globalAjaxMsgError += '<td class="msg_aviso">gov.pr.celepar.framework.exception.ApplicationException: Sistema temporariamente indisponível. Aguarde alguns instantes e tente novamente.</td>';
		globalAjaxMsgError += '</tr></table>';
</script>
		<div width="100%" align="center"><i>Nenhum registro encontrado.</i></div>
<script type="text/javascript">
	if( (typeof globalAjaxMsgError) != "undefined" && globalAjaxMsgError != null && trimStr(globalAjaxMsgError) != "" ) { sysmsg.innerHTML = globalAjaxMsgError; }
</script>"""
VAZIO_HTML = """<br>
		<div width="100%" align="center"><i>Nenhum registro encontrado.</i></div>
<script type="text/javascript">
	if( (typeof globalAjaxMsgError) != "undefined" && globalAjaxMsgError != null && trimStr(globalAjaxMsgError) != "" ) { sysmsg.innerHTML = globalAjaxMsgError; }
</script>"""


def listagem(cod, epigrafe):
    return (f"<a href=\"JavaScript:exibir('/legislacao/listarAtosAno.do?action=exibir&codAto={cod}&indice=1&totalRegistros=1');\"></a>"
            f"<div id=\"{cod}_epigrafeAto\">{epigrafe}</div><div id=\"{cod}_descricaoItemAto\">Ementa.<br/></div>"
            f"<div id=\"{cod}_dataPublicacao\">04/01/1955</div>")


class IndiceComErroDaFonte(unittest.TestCase):
    """A Casa Civil responde HTTP 200 com página de erro na listagem de 1954 das leis ordinárias; por mês,
    só junho falha e outubro vem vazio. As respostas abaixo reproduzem esse quadro."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        p = patch.object(pr, "RAIZ_ESTADUAIS", self.tmp.name)
        p.start()
        self.addCleanup(p.stop)
        pr.SEM_INDICE.clear()
        self.addCleanup(pr.SEM_INDICE.clear)
        self.pasta = os.path.join(self.tmp.name, "PR", "_indice")
        os.makedirs(self.pasta)
        with open(os.path.join(self.pasta, "tipo-1-anos.html"), "w", encoding="utf-8") as f:
            f.write(ANOS_HTML)
        self.respostas = {("1955", None): listagem("15000", "Lei 2500 - 3 de Janeiro de 1955"), ("1954", None): ERRO_HTML,
                          ("1954", "6"): ERRO_HTML, ("1954", "10"): VAZIO_HTML}
        for mes in (1, 2, 3, 4, 5, 7, 8, 9, 11, 12):
            self.respostas[("1954", str(mes))] = listagem(str(14000 + mes), f"Lei {1600 + mes} - 5 do mês {mes} de 1954")
        self.pedidos = []

    def post(self, caminho, dados, tentativas=4):
        query = dict(par.split("=") for par in caminho.split("?")[1].split("&"))
        self.pedidos.append((query["anoAto"], query.get("mesAto")))
        return self.respostas[self.pedidos[-1]]

    def cache(self, recorte):
        return os.path.join(self.pasta, f"tipo-1-{recorte}.html")

    def test_ano_com_erro_sai_mes_a_mes_e_so_o_mes_com_erro_fica_de_fora(self):
        with patch.object(pr, "post", self.post):
            itens = pr.indice(tipos={"1"}, anos={1954, 1955})
        self.assertEqual(sorted(i["codAto"] for i in itens),
                         ["14001", "14002", "14003", "14004", "14005", "14007", "14008", "14009", "14011", "14012", "15000"])
        self.assertEqual({i["ano"] for i in itens if i["codAto"] != "15000"}, {"1954"})
        self.assertEqual(pr.SEM_INDICE, [("1", "1954", 6)])
        self.assertEqual(pr.recortes_sem_indice(), "leis-ordinarias 1954 (mês 06)")
        self.assertTrue(os.path.exists(self.cache("1955")))
        self.assertTrue(os.path.exists(self.cache("1954-01")))
        self.assertTrue(os.path.exists(self.cache("1954-10")), "mês sem atos é resposta válida e fica no cache")
        self.assertFalse(os.path.exists(self.cache("1954")), "página de erro do ano não vira cache")
        self.assertFalse(os.path.exists(self.cache("1954-06")), "página de erro do mês não vira cache")

    def test_retomada_so_pede_de_novo_o_que_falhou(self):
        with patch.object(pr, "post", self.post):
            pr.indice(tipos={"1"}, anos={1954})
            self.pedidos.clear()
            pr.SEM_INDICE.clear()
            itens = pr.indice(tipos={"1"}, anos={1954})
        self.assertEqual(self.pedidos, [("1954", None), ("1954", "6")])
        self.assertEqual(len(itens), 10)
        self.assertEqual(pr.SEM_INDICE, [("1", "1954", 6)])

    def test_erro_ja_guardado_por_coleta_antiga_e_pedido_de_novo_e_removido(self):
        with open(self.cache("1954"), "w", encoding="utf-8") as f:
            f.write(ERRO_HTML)
        with patch.object(pr, "post", self.post):
            pr.indice(tipos={"1"}, anos={1954})
        self.assertEqual(self.pedidos[0], ("1954", None))
        self.assertFalse(os.path.exists(self.cache("1954")))

    def test_erro_ja_guardado_e_substituido_quando_a_fonte_volta(self):
        with open(self.cache("1954"), "w", encoding="utf-8") as f:
            f.write(ERRO_HTML)
        self.respostas[("1954", None)] = listagem("15500", "Lei 2000 - 5 de Março de 1954")
        with patch.object(pr, "post", self.post):
            itens = pr.indice(tipos={"1"}, anos={1954})
        self.assertEqual([i["codAto"] for i in itens], ["15500"])
        self.assertEqual(self.pedidos, [("1954", None)])
        self.assertEqual(pr.SEM_INDICE, [])
        with open(self.cache("1954"), encoding="utf-8") as f:
            self.assertIn("15500_epigrafeAto", f.read())

    def test_ano_sem_nenhum_mes_listado_aparece_uma_vez_no_aviso(self):
        for mes in range(1, 13):
            self.respostas[("1954", str(mes))] = ERRO_HTML
        with patch.object(pr, "post", self.post):
            itens = pr.indice(tipos={"1"}, anos={1954})
        self.assertEqual(itens, [])
        self.assertEqual(len(pr.SEM_INDICE), 12)
        self.assertEqual(pr.recortes_sem_indice(), "leis-ordinarias 1954")

    def test_listagem_valida_em_cache_nao_vai_a_rede(self):
        with open(self.cache("1955"), "w", encoding="utf-8") as f:
            f.write(self.respostas[("1955", None)])
        with patch.object(pr, "post", side_effect=AssertionError("não deveria ir à rede")):
            itens = pr.indice(tipos={"1"}, anos={1955})
        self.assertEqual(len(itens), 1)

    def test_indice_completo_nao_grava_atos_json_com_recorte_faltando(self):
        with patch.object(pr, "post", self.post), patch.object(pr, "TIPOS", {"1": pr.TIPOS["1"]}):
            pr.indice()
        self.assertFalse(os.path.exists(os.path.join(self.pasta, "atos.json")))

    def test_fonte_fora_do_ar_no_indice_termina_com_mensagem_e_sem_cache(self):
        def fora_do_ar(caminho, dados, tentativas=4):
            raise pr.urllib.error.HTTPError(caminho, 503, "Service Unavailable", None, None)

        with patch.object(pr, "post", fora_do_ar), self.assertRaises(SystemExit) as saida:
            pr.main(["--tipo", "leis-ordinarias", "--anos", "1954", "--so-indice"])
        self.assertIn("503", str(saida.exception.code))
        self.assertIn("rode de novo mais tarde", str(saida.exception.code))
        self.assertFalse(os.path.exists(self.cache("1954")))

    def decretos(self):
        """Recorte da página real dos decretos (tipo 11): só listarAtosAnoMes, com a opção 13 para o ano inteiro."""
        with open(os.path.join(self.pasta, "tipo-11-anos.html"), "w", encoding="utf-8") as f:
            f.write("".join(f"<a href=\"javascript:listarAtosAnoMes('2026', '{a}', '{m}')\">x</a>"
                            for a, m in (("2026", 1), ("2026", 2), ("2026", 13), ("1894", 11), ("1894", 13))))
        jan = listagem("90001", "Decreto 12001 - 5 de Janeiro de 2026")
        fev = listagem("90002", "Decreto 12050 - 3 de Fevereiro de 2026")
        de1894 = listagem("90003", "Decreto 1 - 20 de Novembro de 1894")
        self.respostas.update({("2026", "1"): jan, ("2026", "2"): fev, ("2026", "13"): jan + fev,
                               ("1894", "11"): de1894, ("1894", "13"): de1894})

    def test_tipo_listado_por_mes_pede_o_ano_inteiro_pela_opcao_13(self):
        self.decretos()
        with patch.object(pr, "post", self.post):
            itens = pr.indice(tipos={"11"})
        self.assertEqual(self.pedidos, [("2026", "13"), ("1894", "13")])
        self.assertEqual([(i["codAto"], i["tipo"], i["ano"]) for i in itens],
                         [("90001", "11", "2026"), ("90002", "11", "2026"), ("90003", "11", "1894")])
        self.assertEqual(pr.SEM_INDICE, [])
        self.assertTrue(os.path.exists(os.path.join(self.pasta, "tipo-11-2026-13.html")))

    def test_ano_inteiro_com_erro_cai_nos_meses_anunciados(self):
        self.decretos()
        self.respostas[("2026", "13")] = ERRO_HTML
        self.respostas[("2026", "2")] = ERRO_HTML
        with patch.object(pr, "post", self.post):
            itens = pr.indice(tipos={"11"}, anos={2026})
        self.assertEqual(self.pedidos, [("2026", "13"), ("2026", "1"), ("2026", "2")])
        self.assertEqual([i["codAto"] for i in itens], ["90001"])
        self.assertEqual(pr.SEM_INDICE, [("11", "2026", 2)])
        self.assertEqual(pr.recortes_sem_indice(), "decretos 2026 (mês 02)")
        self.assertFalse(os.path.exists(os.path.join(self.pasta, "tipo-11-2026-13.html")))

    def test_ano_inteiro_vazio_nao_vale_como_resposta(self):
        self.decretos()
        self.respostas[("1894", "13")] = VAZIO_HTML
        with patch.object(pr, "post", self.post):
            itens = pr.indice(tipos={"11"}, anos={1894})
        self.assertEqual(self.pedidos, [("1894", "13"), ("1894", "11")])
        self.assertEqual(len(itens), 1)

    def test_execucao_termina_com_erro_e_nomeia_o_recorte(self):
        with patch.object(pr, "post", self.post), self.assertRaises(SystemExit) as saida:
            pr.main(["--tipo", "leis-ordinarias", "--anos", "1954-1955", "--so-indice"])
        self.assertIn("leis-ordinarias 1954 (mês 06)", str(saida.exception.code))
        self.assertNotIn("1955", str(saida.exception.code))


def pagina_de_ato(titulo):
    return (f"<html><body><form><h3>{titulo}</h3><p>Art. 1º Fica aberto um crédito suplementar ao orçamento do Estado, "
            "na forma deste Decreto, que entra em vigor na data de sua publicação.</p></form></body></html>")


class AtoListadoEmDoisAnos(unittest.TestCase):
    """Quadro real dos decretos de 2025 republicados em 9/2/2026: a fonte lista o mesmo codAto em 2025, com a
    data do decreto, e em 2026, com a da republicação; a página do ato é que diz de quando ele é. O mesmo vale
    para a Lei 20941, de 2021, que a listagem de 2010 traz com o ano errado."""

    LISTAGENS = {
        "2026": listagem("384881", "Decreto 12323 - 9 de Fevereiro de 2026")
        + listagem("400001", "Decreto 12500 - 9 de Janeiro de 2026")
        + listagem("258039", "Decreto 941 - 20 de Dezembro de 2026"),
        "2025": listagem("384881", "Decreto 12323 - 18 de Dezembro de 2025")
        + listagem("400002", "Decreto 12501 - 9 de Janeiro de 2026")
        + listagem("258039", "Decreto 941 - 20 de Dezembro de 2025"),
    }
    PAGINAS = {
        "384881": "Decreto 12323 - 18 de Dezembro de 2025",  # das duas listagens, vale a de 2025
        "400001": "Decreto 12500 - 9 de Janeiro de 2026",
        "400002": "Decreto 12501 - 9 de Janeiro de 2026",  # só a listagem de 2025 o traz: fica em 2025
        "258039": "Decreto 941 - 20 de Dezembro de 2010",  # a página dá um ano que a fonte nem lista
    }

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        for limpar in (pr.RECUSADO.clear, pr.SEM_INDICE.clear, pr._LISTADOS.clear):
            limpar()
            self.addCleanup(limpar)
        p = patch.object(pr, "RAIZ_ESTADUAIS", self.tmp.name)
        p.start()
        self.addCleanup(p.stop)
        p = patch.object(pr, "caminhos", lambda uf, pasta, ano, slug: (
            os.path.join(self.tmp.name, uf, pasta, str(ano), slug + ".md"),
            os.path.join(self.tmp.name, uf, "_fonte", pasta, str(ano), slug + ".html.gz")))
        p.start()
        self.addCleanup(p.stop)
        indice = os.path.join(self.tmp.name, "PR", "_indice")
        os.makedirs(indice)
        with open(os.path.join(indice, "tipo-11-anos.html"), "w", encoding="utf-8") as f:
            f.write("".join(f"<a href=\"javascript:listarAtosAnoMes('2026', '{a}', '13')\">x</a>" for a in self.LISTAGENS))
        self.pedidos = []
        p = patch.object(pr, "post", self.post)
        p.start()
        self.addCleanup(p.stop)
        p = patch.object(pr.rede, "get", lambda url, **kw: (
            200, pagina_de_ato(self.PAGINAS[url.split("codAto=")[1]]).encode("utf-8"), "text/html;charset=UTF-8"))
        p.start()
        self.addCleanup(p.stop)

    def post(self, caminho, dados, tentativas=4):
        ano = caminho.split("anoAto=")[1].split("&")[0]
        self.pedidos.append(ano)
        return self.LISTAGENS[ano]

    def gravados(self):
        raiz = os.path.join(self.tmp.name, "PR", "decretos")
        if not os.path.isdir(raiz):
            return []
        return sorted(os.path.join(ano, f) for ano in os.listdir(raiz) for f in os.listdir(os.path.join(raiz, ano)))

    ESPERADO = ["2025/dec-12323-2025-id384881.md", "2025/dec-12501-2025-id400002.md",
                "2026/dec-12500-2026-id400001.md", "2026/dec-941-2026-id258039.md"]

    def test_indice_guarda_uma_entrada_por_ano_em_que_a_fonte_lista_o_ato(self):
        itens = pr.indice(tipos={"11"})
        self.assertEqual(sorted(i["ano"] for i in itens if i["codAto"] == "384881"), ["2025", "2026"])
        self.assertEqual(len(itens), 6)

    def test_coleta_completa_grava_cada_ato_num_ano_so(self):
        pr.main(["--tipo", "decretos", "--workers", "1"])
        self.assertEqual(self.gravados(), self.ESPERADO)
        with open(os.path.join(self.tmp.name, "PR", "decretos", "2025", "dec-12323-2025-id384881.md"), encoding="utf-8") as f:
            self.assertIn("data: 2025-12-18", f.read())

    def test_lotes_anuais_dao_o_mesmo_resultado_em_qualquer_ordem(self):
        for ordem in (("2026", "2025"), ("2025", "2026")):
            with self.subTest(ordem=ordem):
                for arquivo in self.gravados():
                    os.remove(os.path.join(self.tmp.name, "PR", "decretos", arquivo))
                pr._LISTADOS.clear()
                for ano in ordem:
                    pr.main(["--tipo", "decretos", "--anos", ano, "--workers", "1"])
                # o ato cuja página dá um ano que a fonte não lista fica no primeiro lote que o grava
                esperado = [e for e in self.ESPERADO if "id258039" not in e] + [f"{ordem[0]}/dec-941-{ordem[0]}-id258039.md"]
                self.assertEqual(self.gravados(), sorted(esperado))

    def test_lote_de_um_ano_consulta_a_listagem_do_outro_sem_trazer_os_atos_dele(self):
        pr.main(["--tipo", "decretos", "--anos", "2026", "--workers", "1"])
        self.assertEqual(self.gravados(), ["2026/dec-12500-2026-id400001.md", "2026/dec-941-2026-id258039.md"])
        self.assertEqual(self.pedidos, ["2026", "2025"])
        self.assertEqual(pr.SEM_INDICE, [])

    def test_conferencia_fecha_o_lote_contando_o_ato_de_outro_ano(self):
        pr.main(["--tipo", "decretos", "--anos", "2026", "--workers", "1"])
        rel = pr.conferir(pr.indice(tipos={"11"}, anos={2026}))
        self.assertEqual((rel["indice"], rel["md"], rel["retidos"]), (3, 2, 0))
        self.assertEqual(rel["de_outro_ano"], ["384881"])
        self.assertEqual(rel["faltando"], [])
        self.assertFalse(rel["pendencias"])
        pr.main(["--tipo", "decretos", "--anos", "2026", "--conferir"])  # lote fechado: termina sem erro

    def test_conferencia_aponta_ato_sem_arquivo_retencao_e_erro_de_rede(self):
        pr.main(["--tipo", "decretos", "--anos", "2026", "--workers", "1"])
        os.remove(os.path.join(self.tmp.name, "PR", "decretos", "2026", "dec-12500-2026-id400001.md"))
        itens = pr.indice(tipos={"11"}, anos={2026})
        self.assertEqual(pr.conferir(itens)["faltando"], ["400001"])
        with self.assertRaises(SystemExit):
            pr.main(["--tipo", "decretos", "--anos", "2026", "--conferir"])
        falhas = os.path.join(self.tmp.name, "PR", "_falhas.jsonl")
        with open(falhas, "a", encoding="utf-8") as f:
            f.write('{"codAto": "400001", "motivo": "anexos em PDF não coletados", "status": "sem_texto"}\n')
        rel = pr.conferir(itens)
        self.assertEqual((rel["retidos"], rel["faltando"], rel["pendencias"]), (1, [], False))
        with open(falhas, "a", encoding="utf-8") as f:
            f.write('{"item": "{\'codAto\': \'258039\', \'tipo\': \'11\'}", "erro": "The read operation timed out", "status": "erro"}\n')
            f.write('{"item": "{\'codAto\': \'999999\', \'tipo\': \'11\'}", "erro": "de outro lote", "status": "erro"}\n')
        rel = pr.conferir(itens)
        self.assertEqual(rel["erros_de_rede"], ["258039"])
        self.assertTrue(rel["pendencias"])

    def test_listagem_do_outro_ano_fora_do_ar_nao_interrompe_e_o_ato_fica_onde_foi_visto(self):
        with patch.dict(self.LISTAGENS, {"2025": ERRO_HTML}):
            pr.main(["--tipo", "decretos", "--anos", "2026", "--workers", "1"])
        self.assertIn("2026/dec-12323-2026-id384881.md", self.gravados())
        self.assertEqual(pr.SEM_INDICE, [])


# Recortes das páginas reais de exibirAto.do: a Lei 1918 (codAto 14467, junho de 1954) e o codAto 14469, sem ato.
ATO_HTML = """<form name="exibirAtoForm" method="post" action="/legislacao/exibirAto.do">
		<input type="hidden" name="codAto" value="14467">
		<input type="hidden" name="codTipoAto" value="1">
		<input type="hidden" name="dataAto" value="04/06/1954">
		<input type="hidden" name="nroAto" value="1918">
		<h3>Lei 1918 - 04 de Junho de 1954</h3>
		<br>
		Publicado no Di&aacute;rio Oficial n<sup>o</sup>. 76 de 7 de Junho de 1954
		<br><br>
					<p>
						<b class="labelAto">Súmula:</b>
						<a id='150308'>Abre à Secretaria de Educação e Cultura um crédito especial de Cr$ 200.000,00, como auxílio à Prefeitura de Morretes.<br/></a>
					</p>
					<p>
						<b class="labelAto"></b>
						<a id='150312'>Art. 1º. Fica aberto à Secretaria de Educação e Cultura, um crédito especial de Cr$ 200.000,00 (duzentos mil cruzeiros).<br/></a>
					</p>
</form>"""
SEM_ATO_HTML = """<form name="exibirAtoForm" method="post" action="/legislacao/exibirAto.do">
		<input type="hidden" name="codAto" value="">
		<input type="hidden" name="codTipoAto" value="">
		<h3></h3>
</form>"""


class AtosAvulsos(unittest.TestCase):
    """Junho de 1954 não sai em listagem alguma, mas cada lei abre pelo codAto."""

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
        self.pedidos = []

    def get(self, url, **kw):
        cod = url.split("codAto=")[1]
        self.pedidos.append(cod)
        return 200, (ATO_HTML if cod == "14467" else SEM_ATO_HTML).encode("utf-8"), "text/html;charset=UTF-8"

    def test_item_sai_da_pagina_do_ato_e_codato_vazio_e_apontado(self):
        with patch.object(pr.rede, "get", self.get):
            itens, sem_ato = pr.itens_avulsos(["14467", "14469"])
        self.assertEqual(sem_ato, ["14469"])
        self.assertEqual(len(itens), 1)
        self.assertEqual(itens[0]["codAto"], "14467")
        self.assertEqual(itens[0]["tipo"], "1")
        self.assertEqual(itens[0]["ano"], "1954")
        self.assertEqual(itens[0]["epigrafe"], "Lei 1918 - 04 de Junho de 1954")
        self.assertTrue(itens[0]["ementa"].startswith("Abre à Secretaria de Educação e Cultura"))
        self.assertTrue(itens[0]["ementa"].endswith("Prefeitura de Morretes."))

    def test_recusa_da_fonte_interrompe_sem_inventar_item(self):
        with patch.object(pr.rede, "get", lambda url, **kw: (403, b"", "")), self.assertRaises(RuntimeError):
            pr.itens_avulsos(["14467"])
        self.assertTrue(pr.RECUSADO.is_set())

    def test_execucao_grava_o_ato_pede_cada_pagina_uma_vez_e_termina_com_erro_pelo_codato_vazio(self):
        with patch.object(pr.rede, "get", self.get), self.assertRaises(SystemExit) as saida:
            pr.main(["--atos", "14467,14469", "--workers", "1"])
        self.assertIn("14469", str(saida.exception.code))
        self.assertNotIn("14467", str(saida.exception.code))
        self.assertEqual(sorted(self.pedidos), ["14467", "14469"])
        gravado = os.path.join(self.tmp.name, "PR", "leis-ordinarias", "1954", "lei-1918-1954-id14467.md")
        with open(gravado, encoding="utf-8") as f:
            texto = f.read()
        self.assertIn("data: 1954-06-04", texto)
        self.assertIn('ementa: "Abre à Secretaria de Educação e Cultura', texto)
        self.assertIn("exibirAto.do?action=iniciarProcesso&codAto=14467", texto)
        self.assertIn("Fica aberto à Secretaria de Educação e Cultura, um crédito especial de Cr$ 200.000,00", texto)

    def test_filtro_de_ano_vale_para_os_avulsos(self):
        with patch.object(pr.rede, "get", self.get), patch.object(pr, "executar") as executar:
            pr.main(["--atos", "14467", "--anos", "1955"])
        self.assertEqual(executar.call_args.args[1], [])


if __name__ == "__main__":
    unittest.main()
