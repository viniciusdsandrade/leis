"""Coletor do CONFAZ: recorte do mapa do site, identidade pela epígrafe, data do ato e retenções."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import baixar_confaz as c

B = c.BASE + "legislacao/"


def pagina(*paragrafos):
    return ('<html><body><div id="content"><div id="parent-fieldname-text">'
            + "\n".join(p if p.startswith("<p") else f"<p>{p}</p>" for p in paragrafos) + "\n</div><div>rodapé</div></div></body></html>")


def item(secao, ano, numero, nome, icm=False):
    return {"secao": secao, "ano": ano, "numero": numero, "icm": icm, "url": f"{B}{secao}/{ano}/{nome}"}


# Como o portal publica: o antigo com a data só no fecho, o recente com a data na epígrafe.
CV_2004 = pagina(
    "<strong>CONVÊNIO ICMS 106/04</strong>", "<strong>Publicado no DOU de 30.09.04.</strong>",
    "<strong>Ratificação Nacional DOU de 19.10.04, pelo Ato Declaratório</strong>", "<strong>06/04.</strong>",
    "<strong>Autoriza o Estado do Piauí a conceder crédito fiscal presumido do ICMS na aquisição de equipamento Emissor "
    "de Cupom Fiscal (ECF).</strong>",
    "O Conselho Nacional de Política Fazendária - CONFAZ, na sua 115ª reunião ordinária, realizada em Aracaju, SE, no dia "
    "24 de setembro de 2004, tendo em vista o disposto na Lei Complementar n° 24, de 7 de janeiro de 1975, resolve "
    "celebrar o seguinte", "CONVÊNIO", "<strong>Cláusula primeira</strong>",
    "Fica o Estado do Piauí autorizado a conceder crédito fiscal presumido do ICMS.", "Cláusula segunda",
    "Este convênio entra em vigor na data da publicação de sua ratificação nacional.", "Aracaju, SE, 24 de setembro de 2004.")
PT_2012 = pagina(
    "PROTOCOLO ICMS 146, DE 28 DE SETEMBRO DE 2012", "· Publicado no DOU de 23.10.12, pelo Despacho 209/12 .",
    "Altera o Protocolo ICMS 11/91, que dispõe sobre a substituição tributária nas operações com cerveja.",
    "<strong>Os Estados do Acre, Alagoas e o Distrito Federal</strong>, neste ato representados pelos seus respectivos "
    "Secretários de Fazenda, resolvem celebrar o seguinte:", "P R O T O C O L O",
    "<strong>Cláusula primeira</strong> Fica acrescentado o § 3º à cláusula quarta do Protocolo ICMS 11/91.",
    "<strong>Cláusula segunda</strong> Este protocolo entra em vigor na data de sua publicação no Diário Oficial da União.")
AJ_2025 = pagina(
    "REVOGADO", "AJUSTE SINIEF Nº 11, DE 29 DE ABRIL DE 2025", "Publicado no DOU de 30.04.25, pelo Despacho 12/25.",
    "Alterado pelos Ajustes SINIEF 30/25, 43/25.", "Revogado, pelo Ajuste SINIEF 12/26, efeitos a partir de 09.04.26.",
    "Altera o Ajuste SINIEF nº 19, de 9 de dezembro de 2016, que institui a Nota Fiscal de Consumidor Eletrônica.",
    "<strong>O Conselho Nacional de Política Fazendária – CONFAZ e a Secretaria Especial da Receita Federal do Brasil"
    "</strong>, na 408ª Reunião Extraordinária do Conselho, realizada em Brasília, DF, no dia 29 de abril de 2025, resolvem "
    "celebrar o seguinte", "AJUSTE", "<strong>Cláusula primeira</strong> O Ajuste SINIEF nº 19 passa a vigorar com alterações.")
CV_1976 = pagina(
    "<strong>CONVÊNIO ICM 16/76</strong>", "<strong>Publicado no DOU de 30.06.76.</strong>",
    "<strong>Revogado pelo Conv. ICMS</strong>", "<strong>60/90, efeitos a partir de 05.10.90.</strong>",
    "<strong>Concede crédito presumido nas entradas de bens de capital de origem estrangeira.</strong>",
    "O Ministro da Fazenda e os Secretários de Fazenda ou Finanças dos Estados e do Distrito Federal, na 5ª Reunião "
    "Ordinária do Conselho de Política Fazendária, realizada em Brasília, DF, no dia 15 de junho de 1976, resolvem celebrar "
    "o seguinte", "CONVÊNIO", "Cláusula primeira", "Fica concedido crédito presumido.", "Brasília, DF, 15 de junho de 1976.")


class Recorte(unittest.TestCase):
    def test_enderecos_regulares_e_fora_do_recorte(self):
        xml = "".join(f"<url><loc>{B}{u}</loc></url>" for u in (
            "convenios/1975/CV013_75", "convenios/1989/CVM021_89", "convenios/1989/CV021_89", "convenios/2026/convenio-icms-122-26",
            "protocolos/2012/pt146_12", "protocolos/2018/protocolo-icms-ndeg-45-18", "ajustes/2014/AJ_014_14",
            "ajustes/2021/ajuste-sinief-48-21", "protocolos/2017-1/pt001_17", "protocolos/2017/pt001_17",
            "convenios/2018/convenio-icms-52-retificacao", "convenios/1975", "convenios/1967/CV_natal1",
            "convenios/1984/conveniosicms_1984", "ajustes/sinief/modelos/sn_70/guia", "convenios/1995/CV049_95an0.pdf/view",
            "ajustes/2005/AJ007_05_anterior", "convenios/1975/CV013_76", "despacho/2020/dp090_20"))
        itens, fora = c.itens_do_sitemap(xml)
        self.assertEqual([(i["secao"], i["ano"], i["numero"], i["icm"]) for i in itens], [
            ("ajustes", 2014, 14, False), ("ajustes", 2021, 48, False), ("convenios", 1975, 13, False),
            ("convenios", 1989, 21, False), ("convenios", 1989, 21, True), ("convenios", 2026, 122, False),
            ("protocolos", 2012, 146, False), ("protocolos", 2017, 1, False), ("protocolos", 2018, 45, False)])
        self.assertEqual({k: len(v) for k, v in fora.items()}, {
            "número repetido no mapa do site": 1, "retificação avulsa": 1, "fora das pastas de ano (modelos, índices, anexos)": 2,
            "convênio sem número (1966 a 1970)": 1, "índice do ano": 1, "arquivo anexo (PDF)": 1,
            "redação anterior ou republicação": 1, "ano do endereço diferente do da pasta": 1})


class Montagem(unittest.TestCase):
    def meta(self, it, html):
        estado, r = c.montar(it, html)
        self.assertEqual(estado, "ok", r)
        return dict(r["meta"]), r

    def test_convenio_antigo_com_a_data_no_fecho(self):
        meta, r = self.meta(item("convenios", 2004, 106, "CV106_04"), CV_2004)
        self.assertEqual((meta["titulo"], meta["tipo"], meta["numero"], meta["data"]),
                         ("Convênio ICMS nº 106, de 24 de setembro de 2004", "Convênio ICMS", "106", "2004-09-24"))
        self.assertEqual((meta["publicacao"], meta["data_publicacao"]), ("Publicado no DOU de 30.09.04.", "2004-09-30"))
        self.assertTrue(meta["ementa"].startswith("Autoriza o Estado do Piauí"))
        self.assertIsNone(meta["revogada"])
        self.assertNotIn("situacao_fonte", meta)
        self.assertEqual(r["slug"], "convenio-icms-106-2004")
        self.assertTrue(r["corpo"].startswith("# Convênio ICMS nº 106, de 24 de setembro de 2004\n\n**CONVÊNIO ICMS 106/04**"))
        self.assertNotIn("rodapé", r["corpo"])

    def test_protocolo_com_a_data_na_epigrafe(self):
        meta, r = self.meta(item("protocolos", 2012, 146, "pt146_12"), PT_2012)
        self.assertEqual((meta["titulo"], meta["data"], meta["data_publicacao"]),
                         ("Protocolo ICMS nº 146, de 28 de setembro de 2012", "2012-09-28", "2012-10-23"))
        self.assertTrue(meta["ementa"].startswith("Altera o Protocolo ICMS 11/91"))
        self.assertEqual(r["slug"], "protocolo-icms-146-2012")

    def test_marca_de_revogado_antes_da_epigrafe_e_nota_de_revogacao(self):
        meta, r = self.meta(item("ajustes", 2025, 11, "AJ011_25"), AJ_2025)
        self.assertEqual((meta["titulo"], meta["revogada"]), ("Ajuste SINIEF nº 11, de 29 de abril de 2025", True))
        self.assertEqual(meta["situacao_fonte"], "Revogado, pelo Ajuste SINIEF 12/26, efeitos a partir de 09.04.26.")
        self.assertTrue(meta["ementa"].startswith("Altera o Ajuste SINIEF nº 19"))

    def test_nota_quebrada_em_dois_blocos_e_convenio_icm(self):
        meta, r = self.meta(item("convenios", 1976, 16, "CV016_76"), CV_1976)
        self.assertEqual((meta["tipo"], meta["data"], meta["revogada"]), ("Convênio ICM", "1976-06-15", True))
        self.assertEqual(meta["situacao_fonte"], "Revogado pelo Conv. ICMS 60/90, efeitos a partir de 05.10.90.")
        self.assertEqual(r["slug"], "convenio-icm-16-1976")

    def test_convenio_ae_da_serie_anterior_ao_confaz(self):
        for epigrafe in ("CONVÊNIO AE 16/76", "CONVÊNIO AE-16/76", "C ONVÊNIO AE 16/76"):
            with self.subTest(epigrafe):
                meta, r = self.meta(item("convenios", 1976, 16, "CV016_76"), CV_1976.replace("CONVÊNIO ICM 16/76", epigrafe))
                self.assertEqual((meta["tipo"], meta["titulo"], r["slug"]),
                                 ("Convênio AE", "Convênio AE nº 16, de 15 de junho de 1976", "convenio-ae-16-1976"))

    def test_revogado_a_partir_de_uma_data_e_do_ato_inteiro(self):
        html = CV_1976.replace("Revogado pelo Conv. ICMS", "Revogado a partir de 02.01.78 pelo Conv. ICM")
        self.assertIs(self.meta(item("convenios", 1976, 16, "CV016_76"), html)[0]["revogada"], True)

    def test_dispositivo_unico_sem_clausula_vale_com_o_verbo_e_o_fecho(self):
        unico = CV_1976.replace("<p>Cláusula primeira</p>", "").replace("Fica concedido crédito presumido.", "Os Estados signatários acordam em conceder crédito presumido.")
        self.assertEqual(self.meta(item("convenios", 1976, 16, "CV016_76"), unico)[0]["data"], "1976-06-15")
        sem_fecho = unico.replace("<p>Brasília, DF, 15 de junho de 1976.</p>", "")
        self.assertEqual(c.montar(item("convenios", 1976, 16, "CV016_76"), sem_fecho)[1]["motivo"], "texto sem cláusula nem artigo")

    def test_revogacao_parcial_e_sem_eficacia_nao_marcam_revogada(self):
        parcial = CV_1976.replace("Revogado pelo Conv. ICMS", "Revogada a cláusula segunda pelo Conv. ICMS")
        self.assertIsNone(self.meta(item("convenios", 1976, 16, "CV016_76"), parcial)[0]["revogada"])
        sem_eficacia = CV_1976.replace("Revogado pelo Conv. ICMS</strong>", "Sem eficácia em virtude de legislação posterior.</strong>") \
            .replace("<p><strong>60/90, efeitos a partir de 05.10.90.</strong></p>", "")
        meta = self.meta(item("convenios", 1976, 16, "CV016_76"), sem_eficacia)[0]
        self.assertEqual((meta["revogada"], meta["situacao_fonte"]), (None, "Sem eficácia em virtude de legislação posterior."))

    def test_epigrafe_em_dois_blocos_e_com_defeito_de_grafia_da_fonte(self):
        for epigrafe, numero, ano, nome, esperado in [
                ("<p><strong>PROTOCOLO ICMS</strong></p><p><strong>21/97</strong></p>", 21, 1997, "pt021_97", "1997-07-16"),
                ("<p>PROTOCOLO ICMS 99, DE 30 DE SETEMBRO DE 200 8</p>", 99, 2008, "pt099_08", "2008-09-30"),
                ("<p>PROTOCOLO ICMS 07, DE27 DE MARÇO DE 1997</p>", 7, 1997, "pt007_97", "1997-03-27"),
                ("<p>PROTOCOLO ICMS 23/19, DE 10 DE OUTUBRO DE 2019</p>", 23, 2019, "pt023_19", "2019-10-10"),
                ("<p>PROTOCOLO ICMS Nº 48, 09 DE DEZEMBRO DE 2021</p>", 48, 2021, "protocolo-icms-48-21", "2021-12-09"),
                ("<p>PROTOCOLO ICMS 3, DE 3 ABRIL DE 2009</p>", 3, 2009, "pt003_09", "2009-04-03"),
                ("<p>PROTOCOLO ICMS 23/17, DE 15 DE DEZEMBRO DE2017</p>", 23, 2017, "pt023_17", "2017-12-15"),
                ("<p>PROTOCOLO ICMS 14 , DE 1º DEABRIL DE 2011</p>", 14, 2011, "pt014_11", "2011-04-01"),
                ("<p>PROTOCOLO ICMS 77/18, DE 05DE JULHO DE 2018</p>", 77, 2018, "pt077_18", "2018-07-05"),
                ("<p>PROTOCOLO ICMS 80/18, DE05DE JULHO DE 2018</p>", 80, 2018, "pt080_18", "2018-07-05"),
                ("<p>PROTOCOLO ICMS 74, DE 04 D E AGOSTO DE 1992</p>", 74, 1992, "pt074_92", "1992-08-04"),
                ("<p>PROTOCOLO ICMS 90, DE 28 DE SETEMBRO D E 2010</p>", 90, 2010, "pt090_10", "2010-09-28"),
                ("<p>PROTOCOLO ICMS 29, DE 3 DE ABRIL 2009</p>", 29, 2009, "pt029_09", "2009-04-03"),
                ("<p>PROTOCOLO ICMS 89, DE 12 DE SETEMBRO DE DE 2016</p>", 89, 2016, "pt089_16", "2016-09-12")]:
            with self.subTest(nome):
                html = PT_2012.replace("<p>PROTOCOLO ICMS 146, DE 28 DE SETEMBRO DE 2012</p>", epigrafe)
                if "/97</strong>" in epigrafe:
                    html = html.replace("</div><div>rodapé", "<p>Salvador, BA, 16 de julho de 1997</p></div><div>rodapé")
                self.assertEqual(self.meta(item("protocolos", ano, numero, nome), html)[0]["data"], esperado)

    def test_epigrafe_de_convenio_com_a_palavra_partida_ou_com_barra(self):
        for bloco, numero in [("CON VÊNIO ICMS 51, DE 26 DE MARÇO DE 2010", 51), ("C ONVÊNIO ICMS 51, DE 26 DE MARÇO DE 2010", 51),
                              ("CONVÊNIO/ICMS Nº 2, DE 26 DE MARÇO DE 2010", 2)]:
            with self.subTest(bloco):
                lida = c.ler_epigrafe([bloco])
                self.assertEqual((lida["especie"], lida["imposto"], lida["numero"], lida["data"]),
                                 ("convenio", "icms", numero, "2010-03-26"))
        # o mês truncado, o ano truncado e a epígrafe sem a espécie continuam sem leitura
        for bloco in ("CONVÊNIO ICMS 183/19, DE 10 DE OUTUBR DE 2019", "ICMS 50/18, DE 05 DE JULHO DE 2018",
                      "CONVÊNIO ICMS 50/20, DE 30 DE JULHO DE 202"):
            with self.subTest(bloco):
                self.assertIsNone(c.ler_epigrafe([bloco]))

    def test_retencoes(self):
        casos = {
            "epígrafe com espécie, número ou ano diferentes": (item("convenios", 2004, 107, "CV107_04"), CV_2004),
            "epígrafe com espécie, número ou ano diferentes dos": (item("convenios", 2005, 106, "CV106_05"), CV_2004),
            "epígrafe com espécie": (item("protocolos", 2004, 106, "pt106_04"), CV_2004),
            "epígrafe com espécie, número": (item("convenios", 1976, 16, "CVM016_76", icm=True), CV_1976.replace("ICM 16/76", "ICMS 16/76")),
            "epígrafe do ato não reconhecida": (item("convenios", 2004, 106, "CV106_04"), CV_2004.replace("CONVÊNIO ICMS 106/04", "RETIFICAÇÃO")),
            "imagem no corpo": (item("convenios", 2004, 106, "CV106_04"), CV_2004.replace("<p>CONVÊNIO</p>", '<p><img src="data:image/png;base64,AAAA"></p>')),
            "fecho e preâmbulo com datas diferentes": (item("convenios", 2004, 106, "CV106_04"), CV_2004.replace("Aracaju, SE, 24 de setembro", "Aracaju, SE, 25 de setembro")),
            "epígrafe e preâmbulo com datas diferentes": (item("ajustes", 2025, 11, "AJ011_25"), AJ_2025.replace("DE 29 DE ABRIL DE 2025", "DE 1º DE MAIO DE 2025")),
            "publicação no DOU anterior à data do ato": (item("protocolos", 2012, 146, "pt146_12"), PT_2012.replace("23.10.12", "23.09.12")),
            "data do ato não encontrada": (item("convenios", 2004, 106, "CV106_04"),
                                           CV_2004.replace("no dia 24 de setembro de 2004", "nesta data").replace("<p>Aracaju, SE, 24 de setembro de 2004.</p>", "")),
            "texto sem cláusula nem artigo": (item("convenios", 2004, 106, "CV106_04"),
                                              CV_2004.replace("Cláusula", "Item").replace("resolve celebrar", "aprova")),
            "página sem o bloco de texto": (item("convenios", 2004, 106, "CV106_04"), "<html><body>Página não encontrada</body></html>"),
        }
        for motivo, (it, html) in casos.items():
            with self.subTest(motivo):
                estado, r = c.montar(it, html)
                self.assertEqual(estado, "retido")
                self.assertIn(motivo, r["motivo"])

    def test_data_de_outro_ano_no_fecho_de_um_anexo_nao_e_a_do_ato(self):
        html = CV_1976.replace("</div><div>rodapé", "<p>Rio de Janeiro, 8 de abril de 1974.</p></div><div>rodapé")
        self.assertEqual(self.meta(item("convenios", 1976, 16, "CV016_76"), html)[0]["data"], "1976-06-15")

    def test_fecho_com_a_uf_entre_parenteses_ou_sem_o_de_antes_do_ano(self):
        sem_preambulo = CV_1976.replace("no dia 15 de junho de 1976", "nesta data")
        for fecho, esperado in [("Rio de Janeiro (GB), 23 de junho de 1976.", "1976-06-23"), ("Teresina, PI, 15 de junho 1976.", "1976-06-15"),
                                ("Brasília, 1º de junho de 1976", "1976-06-01")]:
            with self.subTest(fecho):
                html = sem_preambulo.replace("Brasília, DF, 15 de junho de 1976.", fecho)
                self.assertEqual(self.meta(item("convenios", 1976, 16, "CV016_76"), html)[0]["data"], esperado)

    def test_citacao_de_outro_ato_no_alto_nao_e_epigrafe(self):
        html = CV_2004.replace("<p><strong>CONVÊNIO ICMS 106/04</strong></p>", "<p>Convênio ICMS 106/04, que autoriza o Piauí</p>")
        self.assertEqual(c.montar(item("convenios", 2004, 106, "CV106_04"), html)[1]["motivo"], "epígrafe do ato não reconhecida")

    def test_data_de_publicacao_implausivel_fica_so_no_texto(self):
        for errada in ("30.09.94", "30.09.05"):  # fora do intervalo de anos; mais de 180 dias depois do ato
            with self.subTest(errada):
                meta = self.meta(item("convenios", 2004, 106, "CV106_04"), CV_2004.replace("30.09.04", errada))[0]
                self.assertEqual(meta["publicacao"], f"Publicado no DOU de {errada}.")
                self.assertNotIn("data_publicacao", meta)


if __name__ == "__main__":
    unittest.main()
