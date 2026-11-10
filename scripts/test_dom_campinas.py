"""Recorte de decretos de Campinas da edição do DOM: geometria das colunas, epígrafe, fim do ato e quadros. Sem rede e
sem pdftotext: os testes usam caixas de palavras e textos sintéticos."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import baixar_dom_campinas as d  # noqa: E402
import baixar_bibjuri_campinas as bib  # noqa: E402

NORMA = {"id": 57000, "numero": "23145", "data": "2024-01-17", "ano": 2024, "texto_integral": "",
         "ementa": "Dispõe sobre abertura de crédito adicional suplementar, no valor de R$ 2.664.000,00"}
DECRETO = """    DECRETO Nº 23.145, DE 17 DE JANEIRO DE 2024

 DISPÕE SOBRE ABERTURA DE CRÉDITO ADICIONAL SUPLEMEN-
TAR, NO VALOR DE R$ 2.664.000,00 (Dois milhões e seiscentos e sessen-
ta e quatro mil reais).
 O Prefeito de Campinas, no uso de suas atribuições legais:
DECRETA:
Artigo 1º - Fica aberto um crédito adicional, no valor de R$ 2.664.000,00, suplementar ao Orçamento-
-Programa vigente, na seguinte classificação:
231000     SECRETARIA MUNICIPAL DO VERDE           339039     R$ 2.664.000,00
23110      GABINETE DO SECRETÁRIO                  01.140.000
Artigo 2º - Este Decreto entra em vigor na data de sua publicação.
Campinas, 17 de janeiro de 2024

DÁRIO SAADI
Prefeito Municipal

AURÍLIO SERGIO COSTA CAIADO
Secretário Municipal de Finanças
"""
NOTA = """
Decreto elaborado no Departamento de Contabilidade e publicado pela Coordenadoria de Expediente.

ADERVAL FERNANDES JUNIOR
Secretário Municipal Chefe de Gabinete do Prefeito
"""
SEGUINTE = """
SECRETARIA DE ADMINISTRAÇÃO
AVISO DE LICITAÇÃO
Pregão nº 005/2024-Eletrônico
"""


class Geometria(unittest.TestCase):
    def caixas(self):
        caixas = []
        for y in range(50, 880, 12):
            if 300 <= y <= 320:
                caixas.append((100.0, float(y), 540.0, y + 9.0))  # faixa cheia: atravessa a calha
                continue
            caixas += [(40.0, float(y), 300.0, y + 9.0), (336.0, float(y), 600.0, y + 9.0)]
        caixas.append((40.0, 18.0, 600.0, 27.0))  # cabeçalho corrido, acima de TOPO
        return caixas

    def test_calha_no_meio(self):
        self.assertTrue(300 < d.calha(637.8, self.caixas()) < 336)

    def test_colunas_e_faixa_cheia_na_ordem_de_leitura(self):
        regioes = d.zonas_da_pagina(637.8, 907.1, self.caixas())
        largura_cheia = [r for r in regioes if r[2] > 600]
        self.assertEqual(len(largura_cheia), 1, regioes)
        cheia = regioes.index(largura_cheia[0])
        self.assertEqual(cheia, 2, "esquerda e direita acima da faixa, faixa, esquerda e direita abaixo")
        self.assertEqual(len(regioes), 5)
        self.assertLess(regioes[0][0], regioes[1][0])
        self.assertTrue(all(r[1] >= d.TOPO for r in regioes))

    def test_pagina_de_uma_coluna_e_lida_inteira(self):
        caixas = [(40.0, float(y), 600.0, y + 9.0) for y in range(50, 880, 12)]
        self.assertEqual(d.zonas_da_pagina(637.8, 907.1, caixas), [(0.0, float(d.TOPO), 637.8, 907.1 - d.TOPO)])


class Recorte(unittest.TestCase):
    def test_epigrafe_com_ordinal_e_ano_com_ponto(self):
        rx = d.epigrafe_rx({"numero": "23440", "data": "2026-09-01"})
        self.assertTrue(rx.search("DECRETO Nº 23.440, DE 1º DE SETEMBRO DE 2026"))
        self.assertTrue(d.epigrafe_rx({"numero": "6883", "data": "1982-01-12"}).search("DECRETO Nº 6.883 DE 12 DE JANEIRO DE 1.982"))
        self.assertFalse(rx.search("DECRETO Nº 23.440, DE 2 DE SETEMBRO DE 2026"))
        self.assertTrue(d.epigrafe_solta(NORMA).search("x DECRETO Nº 23.145, DE 17 DE JANEIRO DE 2024 DISPÕE"))

    def test_fim_na_linha_do_chefe_de_gabinete(self):
        texto, pagina, motivo = d.recortar([(1, "AVISO ANTERIOR\n\n" + DECRETO + NOTA + SEGUINTE)], NORMA)
        self.assertIsNone(motivo)
        self.assertEqual(pagina, 1)
        self.assertTrue(texto.lstrip().startswith("DECRETO Nº 23.145"))
        self.assertIn("Chefe de Gabinete do Prefeito", texto)
        self.assertNotIn("AVISO DE LICITA", texto)
        self.assertNotIn("AVISO ANTERIOR", texto)

    def test_sem_chefe_de_gabinete_para_nas_assinaturas(self):
        texto, _, motivo = d.recortar([(3, DECRETO + SEGUINTE)], NORMA)
        self.assertIsNone(motivo)
        self.assertIn("Secretário Municipal de Finanças", texto)
        self.assertNotIn("SECRETARIA DE ADMINISTRAÇÃO", texto)

    def test_ato_que_continua_na_pagina_seguinte(self):
        parte1, parte2 = DECRETO.split("Artigo 2º")
        texto, pagina, motivo = d.recortar([(4, parte1), (5, "Artigo 2º" + parte2 + NOTA)], NORMA)
        self.assertIsNone(motivo)
        self.assertEqual(pagina, 4)
        self.assertIn("Artigo 2º", texto)

    def test_assinatura_do_prefeito_com_variantes(self):
        for cargo in ("Prefeito Municipal de Campinas", "Prefeita Municipal", "Prefeito Municipal em Exercício",
                      "Vice-Prefeito"):
            with self.subTest(cargo=cargo):
                texto, _, motivo = d.recortar([(1, DECRETO.replace("Prefeito Municipal", cargo))], NORMA)
                self.assertIsNone(motivo)
                self.assertIn(cargo, texto)

    def test_anexo_depois_das_assinaturas_retem(self):
        com_anexo = DECRETO.replace("Artigo 2º", "Parágrafo único. O termo do Anexo Único será assinado pelos pais.\nArtigo 2º")
        _, _, motivo = d.recortar([(1, com_anexo + NOTA + "\nANEXO ÚNICO\nTERMO DE RESPONSABILIDADE\n")], NORMA)
        self.assertTrue(motivo.startswith("anexo do decreto publicado depois"), motivo)
        # sem menção a anexo no corpo, o ANEXO seguinte é de outro ato e o decreto passa
        texto, _, motivo = d.recortar([(1, DECRETO + NOTA + "\nANEXO I DA PORTARIA 10/2024\n")], NORMA)
        self.assertIsNone(motivo)

    def test_sem_assinatura_antes_do_proximo_decreto_retem(self):
        sem_fim = DECRETO.split("Campinas, 17")[0]
        _, _, motivo = d.recortar([(1, sem_fim + "\nDECRETO Nº 23.146, DE 17 DE JANEIRO DE 2024\n" + DECRETO.split("\n", 2)[2])], NORMA)
        self.assertTrue(motivo.startswith("sem a assinatura do Prefeito"), motivo)

    def test_epigrafe_ausente(self):
        _, _, motivo = d.recortar([(1, DECRETO.replace("23.145", "23.999"))], NORMA)
        self.assertTrue(motivo.startswith("epígrafe com o número e a data"), motivo)


class Conversao(unittest.TestCase):
    def test_quadro_vira_bloco_preformatado_e_prosa_sem_hifenizacao(self):
        texto, _, _ = d.recortar([(1, DECRETO + NOTA)], NORMA)
        corpo, quadro = d.para_md(texto)
        self.assertTrue(quadro)
        self.assertIn("```text\n231000     SECRETARIA MUNICIPAL DO VERDE", corpo)
        self.assertIn("SUPLEMENTAR", corpo)
        self.assertIn("seiscentos e sessenta e quatro", corpo)
        self.assertNotIn("SUPLEMEN- TAR", corpo)
        self.assertIn("Orçamento-Programa", corpo)
        self.assertIn("\n\n**Artigo 2º** - Este Decreto", corpo)
        self.assertIn("\n\nDÁRIO SAADI\n\nPrefeito Municipal\n\n", corpo)

    def test_ato_integro_passa_nas_travas_do_bibjuri(self):
        texto, _, _ = d.recortar([(1, DECRETO + NOTA)], NORMA)
        corpo, _ = d.para_md(texto)
        info = bib.TIPOS["decreto"]
        self.assertIsNone(bib.identidade(corpo, NORMA, info))
        self.assertIsNone(bib.integridade(corpo, NORMA, info))
        self.assertIsNone(bib.ementa_diverge(corpo, NORMA))

    def test_trecho_intercalado_e_detectado(self):
        self.assertTrue(d.INTERCALADO.search("DECRETO Nº 1\nPregão nº 347/2025 - Eletrônico - Processo"))
        self.assertFalse(d.INTERCALADO.search("Decreto elaborado com os elementos do Processo nº PMC.2023.00131723-63"))

    def test_cabecalho_de_secao_nao_e_assinatura(self):
        self.assertTrue(d.ASSINATURA.match("DÁRIO SAADI"))
        self.assertTrue(d.ASSINATURA.match("Secretário Municipal de Finanças"))
        self.assertFalse(d.ASSINATURA.match("SECRETARIA DE ADMINISTRAÇÃO"))
        self.assertFalse(d.ASSINATURA.match("DECRETO Nº 23.146, DE 17 DE JANEIRO DE 2024"))


class Paragrafos(unittest.TestCase):
    def test_artigo_depois_de_linha_cheia_abre_paragrafo(self):
        linhas = ["08.100.614 EPI - GERAL - PERMÍNIO MONTEIRO......................................... R$ 45.000,00",
                  "Artigo 2º - O Crédito aberto pelo artigo anterior será coberto com recursos provenientes da",
                  "anulação parcial no referido Orçamento Programa, da seguinte dotação:"]
        paras = d.paragrafos(linhas)
        self.assertEqual(len(paras), 2, paras)
        self.assertTrue(paras[1].startswith("Artigo 2º"))

    def test_rotulo_em_maiusculas_que_quebra_continua(self):
        linhas = ["16110 GABINETE DO SECRETÁRIO DE COOP. NOS ASSUNTOS DE SEGURANÇA",
                  "PÚBLICA",
                  "06.122.1010.1108 AQUISIÇÃO E REFORMA DE BENS MÓVEIS E IMÓVEIS",
                  "Fica aberto um crédito adicional, no valor de R$ 45.000,00 (quarenta e cinco mil reais) suplementar"]
        paras = d.paragrafos(linhas)
        self.assertEqual(paras[0], "16110 GABINETE DO SECRETÁRIO DE COOP. NOS ASSUNTOS DE SEGURANÇA PÚBLICA")
        self.assertTrue(paras[1].startswith("06.122.1010.1108"))

    def test_ano_na_linha_seguinte_continua_a_frase(self):
        linhas = ["O PREFEITO DE CAMPINAS, no uso de suas atribuições legais e de conformidade com o disposto no Artigo 4º,",
                  "§ 1º da Lei Municipal nº 13.988 de 28 de dezembro de",
                  "2010.",
                  "DECRETA:"]
        paras = d.paragrafos(linhas)
        self.assertIn("28 de dezembro de 2010.", paras[0])

    def test_assinatura_nome_e_cargo_separados(self):
        paras = d.paragrafos(["Campinas, 18 de dezembro de 2025", "DÁRIO SAADI", "Prefeito Municipal",
                              "AURÍLIO SERGIO COSTA CAIADO", "Secretário Municipal de Finanças"])
        self.assertEqual(paras, ["Campinas, 18 de dezembro de 2025", "DÁRIO SAADI", "Prefeito Municipal",
                                 "AURÍLIO SERGIO COSTA CAIADO", "Secretário Municipal de Finanças"])

QUADRO_2011 = """Art. 5º Os valores das gratificações são os seguintes:
  DEPARTAMENTO DE TRANSPORTES INTERNOS
                                                                UM MÊS                    561,1135
                 - DETI

        DEPARTAMENTO DE PROTEÇÃO AO

              CONSUMIDOR - PROCON                               UM MÊS                    561,1135

          SUPERVISÕES DEPARTAMENTAIS                            UM MÊS                    336,6814

  COORDENADORIAS DE UNIDADES BÁSICAS DE
                                                                UM MÊS                    308,6246
      SAÚDE E DE MÓDULOS DE SAÚDE

Art. 6º Este Decreto entra em vigor na data de sua publicação."""


class Quadros(unittest.TestCase):
    def test_celula_que_quebra_de_linha_fica_dentro_do_quadro(self):
        corpo, quadro = d.para_md(QUADRO_2011)
        self.assertTrue(quadro)
        bloco = corpo.split("```text\n", 1)[1].split("\n```", 1)[0]
        self.assertIn("DEPARTAMENTO DE TRANSPORTES INTERNOS", bloco)
        self.assertIn("SAÚDE E DE MÓDULOS DE SAÚDE", bloco)
        self.assertLess(bloco.index("COORDENADORIAS DE UNIDADES"), bloco.index("308,6246"))
        self.assertLess(bloco.index("308,6246"), bloco.index("SAÚDE E DE MÓDULOS"))
        self.assertNotIn("Art. 6", bloco)
        self.assertIn("**Art. 6º** Este Decreto entra em vigor", corpo)

    def test_cabecalho_e_rodape_corridos_saem_e_texto_parecido_fica(self):
        texto = "\n".join([
            "2           Diário Oficial do Município de Campinas",
            "Campinas, segunda-feira, 12 de dezembro de 2011",
            "dezembro de 2011                                   www.campinas.sp.gov.br",
            "Sexta-feira, 24 de",
            "pessoalmente, no endereço da sede do PROCON ou no site www.procon.campinas.",
            "V - 08 de junho, sexta-feira, posterior ao feriado de Corpus Christi;",
            "publicadas em Diário Oficial do Município através de Comunicado"])
        self.assertEqual(d.sem_cromo(texto).split("\n"), [
            "pessoalmente, no endereço da sede do PROCON ou no site www.procon.campinas.",
            "V - 08 de junho, sexta-feira, posterior ao feriado de Corpus Christi;",
            "publicadas em Diário Oficial do Município através de Comunicado"])

class Fonte(unittest.TestCase):
    def test_link_do_bibjuri_vira_endereco_final(self):
        bloco = ('<p>TEXTO INTEGRAL <a href="https://portal-api.campinas.sp.gov.br//sites/default/files/publicacoes-dom/'
                 'dom/637215631201563126372118.pdf">aqui</a></p>')
        self.assertEqual(d.link_dom(bloco), "https://portal-adm.campinas.sp.gov.br/sites/default/files/publicacoes-dom/"
                                            "dom/637215631201563126372118.pdf")
        self.assertIsNone(d.link_dom("<p>sem link</p>"))

    def test_publicacao_da_pagina_do_bibjuri(self):
        bloco = "<p><em>(Publica&ccedil;&atilde;o DOM 18/01/2024 p.1)</em></p>"
        self.assertEqual(d.publicacao_do_bloco(bloco), "DOM 18/01/2024 p.1")


if __name__ == "__main__":
    unittest.main()
