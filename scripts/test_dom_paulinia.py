import sys
import pathlib
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import baixar_dom_paulinia as p

LEI = """                         GABINETE DO PREFEITO
                LEI Nº 4.797, DE 13 DE NOVEMBRO DE 2026
       (Projeto de Lei Nº 127/2026 de autoria do Ver. Fulano)

“ESTABELECE DIRETRIZES PARA A LIMPEZA URBANA, E DÁ OUTRAS PRO-
VIDÊNCIAS.”

A Câmara Municipal APROVOU e eu, Prefeito do Município de Paulínia, SANCIO-
NO e PROMULGO a seguinte Lei:

Art. 1º Ficam estabelecidas diretrizes.
Art. 2º Esta Lei entra em vigor na data de sua publicação.
Paulínia, 13 de Novembro de 2026

FULANO DE TAL
Prefeito Municipal

Lavrado e publicado no Gabinete do Prefeito, na data

BELTRANA DA SILVA
Secretária Mun. de Chefia de Gabinete do Prefeito
"""
DECRETO = """               DECRETO Nº9144 DE 13 DE NOVEMBRO DE 2026

“DISPÕE SOBRE TRANSPOSIÇÃO DE RECURSOS.”

FULANO DE TAL, Prefeito Municipal de Paulínia, no uso de suas atribuições. DECRETA:

ARTIGO 1º - Fica adicionado o valor de R$ 4.000,00.
ARTIGO 2º - Este Decreto entrará em vigor na data de sua publicação.

FULANO DE TAL
Prefeito Municipal

Decreto elaborado no Departamento de Orçamentos da Secretaria Municipal de
Finanças e publicado no Gabinete do Prefeito na data supra.
"""
AVISO = """
                   SECRETARIA DE ADMINISTRAÇÃO
                 CONCORRÊNCIA ELETRÔNICA Nº 6/2026

Objeto: obra.
"""


def atos(texto, data_edicao="2026-11-13"):
    return p.atos_da_edicao([(1, texto)], data_edicao)


class Epigrafe(unittest.TestCase):
    def test_reconhece_as_grafias_da_fonte(self):
        casos = {"LEI Nº 4.797, DE 13 DE NOVEMBRO DE 2026": ("LEI", "4.797"),
                 "   DECRETO Nº9144 DE 13 DE NOVEMBRO DE 2026": ("DECRETO", "9144"),
                 "DECRETO Nº 9142, DE 1º DE MARÇO DE 2026.": ("DECRETO", "9142"),
                 "LEI COMPLEMENTAR Nº 145, DE 18 DE SETEMBRO DE 2026": ("LEI COMPLEMENTAR", "145"),
                 "DECRETO LEGISLATIVO Nº 886, DE 10 DE NOVEMBRO DE 2026": ("DECRETO LEGISLATIVO", "886")}
        for linha, esperado in casos.items():
            m = p.EPIGRAFE.search(linha)
            self.assertIsNotNone(m, linha)
            self.assertEqual((m.group(1), m.group(2)), esperado)

    def test_epigrafe_em_versalete_ou_caixa_mista(self):
        casos = {"Lei nº 3691, de 12 de JULHO DE 2019": ("lei ordinaria", "3691", "2019-07-12"),
                 "DECRETO Nº 7.431 de 10 DE JANEIRO DE 2.019.": ("decreto", "7431", "2019-01-10"),
                 "Lei COMPLEMENTAR nº 70 DE 31 DE outubro DE 2019": ("lei complementar", "70", "2019-10-31"),
                 "decreto nº 7724, de 08 de janeiro de 2020": ("decreto", "7724", "2020-01-08")}
        for linha, (chave, numero, data) in casos.items():
            texto = linha + "\n\nFulano, Prefeito, SANCIONA, PROMULGA e DECRETA:\n\nArt. 1º X.\n"
            (ato, _, _), = p.atos_da_edicao([(1, texto)], data)
            self.assertEqual((ato["chave"], ato["numero"], ato["data"]), (chave, numero, data), linha)

    def test_citacao_em_caixa_mista_de_ato_antigo_nao_e_epigrafe(self):
        texto = DECRETO.replace("ARTIGO 2º", "com fundamento na\nLei Complementar nº 16, de 30 de dezembro de 1999.\nARTIGO 2º")
        (ato, recorte, motivo), = atos(texto)
        self.assertEqual(ato["chave"], "decreto")
        self.assertIsNone(motivo)
        self.assertIn("Lei Complementar nº 16, de 30 de dezembro de 1999.", recorte)
        # a mesma citação em maiúsculas segue registrada, como antes
        em_maiusculas = DECRETO.replace("ARTIGO 2º", "LEI COMPLEMENTAR Nº 16, DE 30 DE DEZEMBRO DE 1999.\nARTIGO 2º")
        self.assertEqual(len(atos(em_maiusculas)), 2)

    def test_citacao_no_meio_da_frase_nao_e_epigrafe(self):
        for linha in ("nos termos da Lei nº 4.582 de 07 de julho de 2025, artigo 4º",
                      "LEI MUNICIPAL Nº 3.405, DE 16 DE DEZEMBRO DE 2014, QUE INSTITUI",
                      "LEI Nº 3.405, DE 16 DE DEZEMBRO DE 2014, QUE INSTITUI NO MUNICÍPIO",
                      "PORTARIA Nº 954/2026"):
            self.assertIsNone(p.EPIGRAFE.search(linha), linha)

    def test_data_iso(self):
        self.assertEqual(p.data_iso("13", "Novembro", "2026"), "2026-11-13")
        self.assertEqual(p.data_iso("1", "MARÇO", "2.026"), "2026-03-01")
        self.assertIsNone(p.data_iso("31", "fevereiro", "2026"))


class Recorte(unittest.TestCase):
    def test_lei_vai_da_epigrafe_ao_fim_das_assinaturas(self):
        (ato, recorte, motivo), = atos(LEI + AVISO)
        self.assertIsNone(motivo)
        self.assertEqual((ato["chave"], ato["numero"], ato["data"], ato["pagina"]), ("lei ordinaria", "4797", "2026-11-13", 1))
        self.assertTrue(recorte.lstrip().startswith("LEI Nº 4.797"))
        self.assertTrue(recorte.rstrip().endswith("Secretária Mun. de Chefia de Gabinete do Prefeito"))
        self.assertNotIn("CONCORRÊNCIA", recorte)

    def test_nota_de_lavratura_em_duas_linhas_fecha_o_decreto(self):
        (ato, recorte, motivo), = atos(DECRETO + AVISO)
        self.assertIsNone(motivo)
        self.assertEqual((ato["chave"], ato["numero"]), ("decreto", "9144"))
        self.assertTrue(recorte.rstrip().endswith("publicado no Gabinete do Prefeito na data supra."))

    def test_dois_atos_seguidos_nao_se_misturam(self):
        (a1, r1, m1), (a2, r2, m2) = atos(LEI + "\n" + DECRETO)
        self.assertIsNone(m1)
        self.assertIsNone(m2)
        self.assertNotIn("DECRETO Nº9144", r1)
        self.assertTrue(r2.lstrip().startswith("DECRETO Nº9144"))

    def test_publicacao_sem_cabecalho_conhecido_depois_das_assinaturas_nao_retém(self):
        (_, recorte, motivo), = atos(DECRETO + "\n  ORDEM DOS TRABALHOS PARA A 38ª SESSÃO ORDINÁRIA\n01) Controle de presença.\n")
        self.assertIsNone(motivo)
        self.assertNotIn("ORDEM DOS TRABALHOS", recorte)

    def test_anexo_depois_das_assinaturas_retém(self):
        (_, recorte, motivo), = atos(DECRETO + "\nANEXO I\nTabela de valores\n")
        self.assertIsNone(recorte)
        self.assertIn("anexo", motivo)

    def test_quadro_depois_das_assinaturas_retém(self):
        (_, recorte, motivo), = atos(DECRETO + "\nDESPESA      FUNCIONAL PROGRAMÁTICA      VALOR\n")
        self.assertIsNone(recorte)
        self.assertIn("depois das assinaturas", motivo)

    def test_nome_com_cargo_desconhecido_depois_das_assinaturas_retém(self):
        (_, recorte, motivo), = atos(DECRETO + "\nMARIA DAS DORES PEREIRA\nResponsável pelo setor\n")
        self.assertIsNone(recorte)
        self.assertIn("linha em maiúsculas depois das assinaturas", motivo)

    def test_titulo_de_outra_publicacao_depois_das_assinaturas_fica_fora(self):
        (_, recorte, motivo), = atos(DECRETO + "\nRESUMO DE CONTRATO\nContratante: Prefeitura Municipal de Paulínia\n")
        self.assertIsNone(motivo)
        self.assertNotIn("RESUMO DE CONTRATO", recorte)

    def test_anexo_proprio_citado_e_ausente_retém(self):
        texto = DECRETO.replace("o valor de R$ 4.000,00.", "o valor constante do Anexo I deste Decreto.")
        (_, recorte, motivo), = atos(texto)
        self.assertIsNone(recorte)
        self.assertIn("anexo próprio", motivo)

    def test_artigo_citado_no_preambulo_nao_e_o_primeiro_artigo(self):
        texto = DECRETO.replace("no uso de suas atribuições. DECRETA:", "no uso de suas atribuições e do\nArt. 43, § 1º, da Lei 4.320. DECRETA:")
        (_, recorte, motivo), = atos(texto)
        self.assertIsNone(motivo)
        self.assertIn("Art. 43, § 1º, da Lei 4.320. DECRETA:", recorte)

    def test_artigo_faltando_ou_coluna_fora_de_ordem_retém(self):
        texto = LEI.replace("Art. 2º Esta Lei entra", "Art. 4º Esta Lei entra")
        (_, recorte, motivo), = atos(texto)
        self.assertIsNone(recorte)
        self.assertIn("fora de sequência", motivo)
        self.assertIsNone(p.artigos_fora_de_sequencia("Art. 1º A.\nArt. 2º B:\nArt. 15. transcrito\nArt. 3º C.\n"))
        self.assertIsNone(p.artigos_fora_de_sequencia("Artigo único. A.\n"))
        self.assertIsNotNone(p.artigos_fora_de_sequencia("Art. 1º A.\nArt. 3º C.\nArt. 2º B.\n"))

    def test_ementa_que_quebra_em_palavra_de_cabecalho_nao_corta_o_ato(self):
        texto = DECRETO.replace("“DISPÕE SOBRE TRANSPOSIÇÃO DE RECURSOS.”",
                                "“DISPÕE SOBRE A INDICAÇÃO DOS MEMBROS DO\nCONSELHO DE MEIO AMBIENTE, ALTERA A\n"
                                "LEI COMPLEMENTAR Nº 88, DE 30 DE SETEMBRO DE 2022.”").replace("ARTIGO", "ART.")
        (ato, recorte, motivo), = atos(texto + AVISO)
        self.assertIsNone(motivo)
        self.assertEqual(ato["numero"], "9144")
        self.assertIn("CONSELHO DE MEIO AMBIENTE", recorte)
        self.assertNotIn("CONCORRÊNCIA", recorte)

    def test_sem_assinatura_retém(self):
        texto = DECRETO.split("FULANO DE TAL\nPrefeito Municipal")[0] + AVISO
        (_, recorte, motivo), = atos(texto)
        self.assertIsNone(recorte)
        self.assertIn("sem a assinatura", motivo)

    def test_formula_partida_pela_quebra_de_coluna(self):
        texto = DECRETO.replace("no uso de suas atribuições. DECRETA:", "no uso de suas atribuições. DECRE-\n\n\nTA:")
        (_, recorte, motivo), = atos(texto)
        self.assertIsNone(motivo)

    def test_relacao_de_anexos_da_prefeitura_depois_das_assinaturas_retém(self):
        (_, recorte, motivo), = atos(DECRETO + "\nPREFEITURA DO MUNICÍPIO DE PAULÍNIA\nRELAÇÃO DE ANEXOS\n")
        self.assertIsNone(recorte)
        self.assertIn("anexo publicado depois das assinaturas", motivo)

    def test_sem_formula_de_promulgacao_retém(self):
        (_, recorte, motivo), = atos(DECRETO.replace("DECRETA:", "resolve:"))
        self.assertIsNone(recorte)
        self.assertIn("fórmula", motivo)

    def test_fecho_com_outra_data_retém(self):
        (_, recorte, motivo), = atos(LEI.replace("Paulínia, 13 de Novembro de 2026", "Paulínia, 12 de Novembro de 2026"))
        self.assertIsNone(recorte)
        self.assertIn("data do fecho (2026-11-12)", motivo)

    def test_rodape_da_pagina_dentro_do_recorte_retém(self):
        for rodape in ("Semanário Oficial | Paulínia | Edição 1.712 | Paulínia, 18 de Outubro de 2021 | 3",
                       "Diário Oficial | | Edição 2.881 | Paulínia, 13 de Novembro de 2026 | 2"):
            texto = LEI.replace("Art. 2º Esta Lei", rodape + "\nArt. 2º Esta Lei")
            (_, recorte, motivo), = atos(texto)
            self.assertIsNone(recorte)
            self.assertIn("rodapé da página", motivo)

    def test_outra_publicacao_intercalada_retém(self):
        texto = DECRETO.replace("ARTIGO 2º", "Objeto: aquisição de material.\nARTIGO 2º")
        (_, recorte, motivo), = atos(texto)
        self.assertIsNone(recorte)
        self.assertIn("intercalado", motivo)

    def test_epigrafe_repetida_na_edicao_retém_as_duas(self):
        resultado = atos(DECRETO + "\n" + DECRETO)
        self.assertEqual([r for _, r, _ in resultado], [None, None])
        self.assertTrue(all("repetida" in m for _, _, m in resultado))

    def test_ato_antigo_ou_posterior_a_edicao_retém(self):
        (_, recorte, motivo), = atos(DECRETO, "2027-06-01")
        self.assertIsNone(recorte)
        self.assertIn("republicação ou citação", motivo)
        (_, recorte, motivo), = atos(DECRETO, "2026-11-01")
        self.assertIsNone(recorte)
        self.assertIn("posterior à da edição", motivo)

    def test_decreto_legislativo_assinado_pelo_presidente(self):
        texto = """      DECRETO LEGISLATIVO Nº 886, DE 10 DE NOVEMBRO DE 2026

“DISPÕE SOBRE A CONCESSÃO DO SELO VERDE.”

Faço saber que a Câmara Municipal APROVOU e eu, seu Presidente, PROMUL-
GO o seguinte Decreto Legislativo:

Art. 1º Fica concedido o SELO VERDE.
Art. 2º Este Decreto Legislativo entra em vigor na data de sua publicação.
Prédio Ulysses Guimarães, 10 de novembro de 2026

VEREADOR FULANO
PRESIDENTE

Publicado na Secretaria. Data supra.

BELTRANO DE TAL
DIRETOR DO DEPARTAMENTO LEGISLATIVO
"""
        (ato, recorte, motivo), = atos(texto)
        self.assertIsNone(motivo)
        self.assertEqual(ato["chave"], "decreto legislativo")
        self.assertTrue(recorte.rstrip().endswith("DIRETOR DO DEPARTAMENTO LEGISLATIVO"))


class Assinaturas(unittest.TestCase):
    def test_nota_partida_pela_quebra_de_coluna(self):
        trecho = ("Prefeito Municipal\nLavrado na Secretaria de Segurança Pública e publicado no Gabinete do Prefeito,\n\n"
                  "na data supra.\n\nRODRIGO D. VIEIRA\nComandante da G.M. de Paulínia\n\nTexto de outra coisa: segue.\n")
        fim = p.fim_das_assinaturas(trecho, len("Prefeito Municipal\n"))
        self.assertTrue(trecho[:fim].rstrip().endswith("Comandante da G.M. de Paulínia"))

    def test_cargo_grafado_como_orgao_depois_do_nome(self):
        trecho = ("Prefeito de Paulínia\nLavrado e publicado no Gabinete do Prefeito, na data supra.\n\nRAFAEL GOLIN GALVÃO\n"
                  "Secretaria de Defesa e Desenvolvimento do Meio Ambiente\n\nCOMISSÃO DE AVALIAÇÃO DE DOCUMENTOS E ACESSO\n")
        self.assertIsNotNone(p.SIGNATARIO.match("Prefeito de Paulínia"))
        fim = p.fim_das_assinaturas(trecho, len("Prefeito de Paulínia\n"))
        self.assertTrue(trecho[:fim].rstrip().endswith("do Meio Ambiente"))
        self.assertFalse(p.nome("COMISSÃO DE AVALIAÇÃO DE DOCUMENTOS E ACESSO"))

    def test_cabecalho_de_orgao_nao_e_nome(self):
        self.assertFalse(p.nome("SECRETARIA DE ADMINISTRAÇÃO"))
        self.assertFalse(p.nome("CÂMARA MUNICIPAL"))
        self.assertTrue(p.nome("GABRIEL CURCI TAVARES RISSO"))
        self.assertTrue(p.nome("RODRIGO D. VIEIRA"))


class Gravacao(unittest.TestCase):
    ATO = {"chave": "lei ordinaria", "tipo_na_fonte": "Lei", "numero": "4797", "data": "2026-11-13", "pagina": 1,
           "epigrafe": "LEI Nº 4.797, DE 13 DE NOVEMBRO DE 2026"}
    EDICAO = {"id": "1965", "edicao": "2881", "data": "2026-11-13", "pdf": "https://www.paulinia.sp.gov.br/uploads/2881_x.pdf"}

    def test_titulo(self):
        self.assertEqual(p.titulo_de(self.ATO), "Lei nº 4.797, de 13 de novembro de 2026")
        self.assertEqual(p.titulo_de({**self.ATO, "tipo_na_fonte": "Decreto", "numero": "9121", "data": "2026-10-01"}),
                         "Decreto nº 9.121, de 1º de outubro de 2026")

    def test_destino(self):
        destino = p.destino_de(self.ATO, self.EDICAO)
        self.assertEqual(destino.relative_to(p.RAIZ).as_posix(),
                         "SP/paulinia/leis-ordinarias/2026/lei-ordinaria-4797-2026-dom-2881.md")

    def test_md_tem_os_campos_da_auditoria_e_a_ementa(self):
        import datetime as dt
        (ato, recorte, _), = atos(LEI)
        md = p.montar_md(ato, self.EDICAO, *p.dom.para_md(recorte), "a" * 64, dt.date(2026, 11, 15))
        cab, corpo = md[4:].split("\n---\n", 1)
        for campo in ("titulo", "tipo", "numero", "data", "versao_texto", "fonte", "baixado_em", "municipio", "uf", "codigo_ibge"):
            self.assertRegex(cab, rf"(?m)^{campo}: \".+\"$")
        self.assertIn('ementa: "ESTABELECE DIRETRIZES PARA A LIMPEZA URBANA, E DÁ OUTRAS PROVIDÊNCIAS."', cab)
        self.assertIn('fonte: "https://www.paulinia.sp.gov.br/portal/diario-oficial/ver/1965"', cab)
        self.assertTrue(corpo.lstrip().startswith("# Lei nº 4.797, de 13 de novembro de 2026\n\nLEI Nº 4.797"))
        self.assertIn("SANCIONO e PROMULGO a seguinte Lei:", corpo)  # "SANCIO-" + "NO" rejuntado

    def test_ementa_ausente_quando_o_ato_abre_com_o_preambulo(self):
        self.assertEqual(p.ementa_de("DECRETO Nº 1\n\nFulano, Prefeito, no uso de suas atribuições, DECRETA:\n\nArt. 1º X."), "")

    def test_ementa_partida_em_dois_paragrafos_segue_ate_fechar_as_aspas(self):
        corpo = ("DECRETO Nº 8682 DE 1 DE JULHO DE 2024\n\n“DISPÕE SOBRE A ABERTURA DE CRÉDITO ADICIONAL SUPLEMENTAR À\n\n"
                 "DOTAÇÃO DO ORÇAMENTO VIGENTE, E DÁ OUTRAS PROVIDÊNCIAS”.\n\nO cidadão FULANO, Prefeito, D E C R E T A:\n\nArt. 1º X.")
        self.assertEqual(p.ementa_de(corpo),
                         "DISPÕE SOBRE A ABERTURA DE CRÉDITO ADICIONAL SUPLEMENTAR À DOTAÇÃO DO ORÇAMENTO VIGENTE, E DÁ OUTRAS PROVIDÊNCIAS.")

    def test_ementa_com_aspas_nunca_fechadas_fica_no_primeiro_paragrafo(self):
        corpo = ("DECRETO Nº 1\n\n“DECLARA DE UTILIDADE PÚBLICA A RUA X.\n\n"
                 "O cidadão FULANO, Prefeito Municipal de Paulínia, usando de suas atribuições, DECRETA:\n\nArt. 1º X.")
        self.assertEqual(p.ementa_de(corpo), "DECLARA DE UTILIDADE PÚBLICA A RUA X.")

    def test_ementa_em_caixa_alta_sem_aspas_segue_enquanto_durar_a_caixa_alta(self):
        corpo = ("LEI Nº 1\n\nINSTITUI OS JOGOS MUNICIPAIS ESPORTIVOS DE\n\nAREIA.\n\n"
                 "A Câmara Municipal APROVOU e eu, Prefeito, SANCIONO e PROMULGO a seguinte Lei:\n\nArt. 1º X.")
        self.assertEqual(p.ementa_de(corpo), "INSTITUI OS JOGOS MUNICIPAIS ESPORTIVOS DE AREIA.")

    def test_ementa_depois_da_nota_do_projeto_sem_o_parentese_de_abertura(self):
        corpo = ("LEI Nº 1\n\nProjeto de Lei Nº 67/2025 de autoria do Ver. Fulano)\n\n“DISPÕE SOBRE A PRESENÇA DE DOULA.”\n\n"
                 "A Câmara Municipal APROVOU e eu, Prefeito, SANCIONO e PROMULGO a seguinte Lei:\n\nArt. 1º X.")
        self.assertEqual(p.ementa_de(corpo), "DISPÕE SOBRE A PRESENÇA DE DOULA.")

    def test_ementa_guarda_as_aspas_de_dentro(self):
        corpo = "DECRETO Nº 1\n\n“REGULAMENTA A LEI Nº 2, QUE “DISPÕE SOBRE X”.”\n\nFULANO, Prefeito, DECRETA:\n\nArt. 1º X."
        self.assertEqual(p.ementa_de(corpo), "REGULAMENTA A LEI Nº 2, QUE “DISPÕE SOBRE X”.")

    def test_ementa_cuja_continuacao_traz_so_o_ano_ou_poucas_minusculas(self):
        corpo = ("DECRETO Nº 8662 DE 04 DE JUNHO DE 2024\n\n“DISPÕE SOBRE A REVOGAÇÃO DO DECRETO Nº 8661, DE 28 DE MAIO DE\n\n2024”\n\n"
                 "O cidadão FULANO, Prefeito Municipal de Paulínia, no uso da atribuição, D E C R E T A:\n\nArt. 1º X.")
        self.assertEqual(p.ementa_de(corpo), "DISPÕE SOBRE A REVOGAÇÃO DO DECRETO Nº 8661, DE 28 DE MAIO DE 2024")
        corpo = ("LEI Nº 1\n\n“AUTORIZA O PODER EXECUTIVO A CONCEDER VERBA À TÍTULO DE\n\nSUBVENÇÃO SOCIAL ÀS ASSOCIAÇÕES DE PAIS E MESTRES - APMs\n\n"
                 "DA REDE MUNICIPAL DE ENSINO E DÁ OUTRAS PROVIDÊNCIAS.”\n\nA Câmara Municipal APROVOU e eu, Prefeito, SANCIONO a seguinte Lei:")
        self.assertEqual(p.ementa_de(corpo), "AUTORIZA O PODER EXECUTIVO A CONCEDER VERBA À TÍTULO DE SUBVENÇÃO SOCIAL ÀS ASSOCIAÇÕES "
                                             "DE PAIS E MESTRES - APMs DA REDE MUNICIPAL DE ENSINO E DÁ OUTRAS PROVIDÊNCIAS.")

    def test_ementa_depois_da_nota_do_projeto_sem_o_parentese_de_fecho(self):
        corpo = ("LEI Nº 1\n\n(Projeto de Lei nº 06/2024 de autoria do Ver. Fulano\n\n“DECLARA DE UTILIDADE PÚBLICA O INSTITUTO X.”\n\n"
                 "A Câmara Municipal APROVOU e eu, Prefeito, SANCIONO e PROMULGO a seguinte Lei:\n\nArt. 1º X.")
        self.assertEqual(p.ementa_de(corpo), "DECLARA DE UTILIDADE PÚBLICA O INSTITUTO X.")

    def test_rejunta_o_paragrafo_partido_no_meio_da_frase(self):
        corpo = ("Faço saber que a Câmara Municipal APROVOU e eu, seu Presidente, PROMULGO\n\no seguinte Decreto Legislativo:\n\n"
                 "**Art. 1º** Fica concedido o diploma ao\n\njovem sanfoneiro Fulano, pelos relevantes serviços\n\nprestados.\n\n"
                 "**Art. 2º** Vale:\n\na) a primeira alínea;\n\nb) a segunda\n\nii - item\n\nFULANO\n\nde Tal")
        self.assertEqual(p.rejuntar(corpo),
                         "Faço saber que a Câmara Municipal APROVOU e eu, seu Presidente, PROMULGO o seguinte Decreto Legislativo:\n\n"
                         "**Art. 1º** Fica concedido o diploma ao jovem sanfoneiro Fulano, pelos relevantes serviços prestados.\n\n"
                         "**Art. 2º** Vale:\n\na) a primeira alínea;\n\nb) a segunda\n\nii - item\n\nFULANO de Tal")

    def test_rejuntar_nao_mexe_em_quadro_nem_em_palavra_hifenizada(self):
        corpo = "Valores do\n\n```text\nDESPESA   VALOR\n\nmaterial    10\n```\n\nanexo acima.\n\ncom o depar-\n\ntamento.\n"
        self.assertEqual(p.rejuntar(corpo), corpo)
        self.assertEqual(p.rejuntar("# Título\n\nminúscula"), "# Título\n\nminúscula")

    def test_rejuntar_com_o_fluxo_so_junta_o_que_o_pdf_confirma(self):
        corpo = "**Art. 1º** Fica concedido o diploma ao\n\njovem Fulano\n\npelos serviços."
        fluxo = p.so_letras("Art. 1º Fica concedido o diploma ao jovem Fulano OUTRA COLUNA pelos serviços.")
        self.assertEqual(p.rejuntar(corpo, fluxo), "**Art. 1º** Fica concedido o diploma ao jovem Fulano\n\npelos serviços.")

    def test_republicacao_cede_o_lugar_a_edicao_mais_antiga(self):
        import datetime as dt, tempfile
        (ato, recorte, _), = atos(LEI)
        md = p.montar_md(ato, self.EDICAO, *p.dom.para_md(recorte), "a" * 64, dt.date(2026, 11, 15))
        with tempfile.TemporaryDirectory() as pasta:
            gravado = pathlib.Path(pasta) / "lei-ordinaria-4797-2026-dom-2881.md"
            gravado.write_text(md, encoding="utf-8")
            self.assertEqual(p.edicao_do_arquivo(gravado), 2881)
            falha = p.republicacao(gravado, pathlib.Path("lei-ordinaria-4797-2026-dom-2879.md"), "Lei Ordinária", ato)
        self.assertEqual(falha, {
            "edicao": "2881", "data_edicao": "2026-11-13",
            "fonte": "https://www.paulinia.sp.gov.br/portal/diario-oficial/ver/1965",
            "tipo": "Lei Ordinária", "numero": ato["numero"], "data": ato["data"],
            "motivo": "ato já recortado de outra edição (lei-ordinaria-4797-2026-dom-2879.md); republicação a conferir"})


class DuasLeituras(unittest.TestCase):
    FLUXO = p.so_letras("Art. 1º Fica criado o conselho, com as atri-\nbuições desta Lei.\nArt. 2º Esta Lei entra em vigor.\n"
                        "CARGO JORNADA\nAgente 40h\n")

    def test_paragrafo_rejuntado_bate_com_o_fluxo(self):
        corpo = "**Art. 1º** Fica criado o conselho, com as atribuições desta Lei.\n\n**Art. 2º** Esta Lei entra em vigor."
        self.assertIsNone(p.diverge_do_fluxo(corpo, self.FLUXO))

    def test_colunas_misturadas_divergem(self):
        corpo = "**Art. 1º** Fica criado o conselho, com as atri- Esta Lei entra em vigor.\n\n**Art. 2º** buições desta Lei."
        motivo = p.diverge_do_fluxo(corpo, self.FLUXO)
        self.assertIn("difere do fluxo do PDF em 2 parágrafo(s)", motivo)

    def test_quadro_preformatado_fica_fora_da_conferencia(self):
        corpo = "**Art. 2º** Esta Lei entra em vigor.\n\n```text\nJORNADA   CARGO\n40h       Agente\n```"
        self.assertIsNone(p.diverge_do_fluxo(corpo, self.FLUXO))


class Geometria(unittest.TestCase):
    def test_mancha_da_primeira_pagina_e_das_internas(self):
        primeira = [(200.0, 154.0, 500.0, 168.0, "Diário"), (510.0, 154.0, 560.0, 168.0, "Oficial"), (565.0, 154.0, 570.0, 168.0, "-"),
                    (575.0, 154.0, 600.0, 168.0, "Ano"), (605.0, 154.0, 640.0, 168.0, "XXXIII"), (645.0, 154.0, 650.0, 168.0, "-"),
                    (655.0, 154.0, 700.0, 168.0, "Edição"), (30.0, 200.0, 80.0, 210.0, "LEI"),
                    (30.0, 786.0, 90.0, 795.0, "Expediente:"), (95.0, 786.0, 110.0, 795.0, "A")]
        self.assertEqual(p.mancha(841.9, primeira), (169.0, 785.0))
        interna = [(30.0, 26.0, 80.0, 36.0, "GABRIEL"), (30.0, 801.0, 70.0, 810.0, "Diário"), (75.0, 801.0, 110.0, 810.0, "Oficial"),
                   (115.0, 801.0, 118.0, 810.0, "|"), (125.0, 801.0, 160.0, 810.0, "Edição"), (165.0, 801.0, 190.0, 810.0, "2.881")]
        self.assertEqual(p.mancha(841.9, interna), (15.0, 800.0))

    def test_mancha_para_no_rodape_que_ainda_diz_semanario(self):
        interna = [(30.0, 26.0, 80.0, 36.0, "GABRIEL"), (30.0, 801.0, 70.0, 810.0, "Semanário"), (75.0, 801.0, 110.0, 810.0, "Oficial"),
                   (115.0, 801.0, 118.0, 810.0, "|"), (120.0, 801.0, 150.0, 810.0, "Paulínia"), (152.0, 801.0, 154.0, 810.0, "|"),
                   (160.0, 801.0, 190.0, 810.0, "Edição"), (195.0, 801.0, 220.0, 810.0, "1.712")]
        self.assertEqual(p.mancha(841.9, interna), (15.0, 800.0))

    def test_titulo_e_rodape_do_semanario_oficial(self):
        def pagina(*linhas):  # cada linha vira palavras lado a lado na altura dada
            return {1: (722.8, 841.9, [(30.0 + 40 * i, y, 65.0 + 40 * i, y + 10, w) for y, texto in linhas for i, w in enumerate(texto.split())])}
        casos = {"Semanário Oficial - Ano XXIII - Edição 1.175 - 24 de fevereiro de 2016": ("1175", "2016-02-24"),
                 "Semanário Oﬁ cial - Ano XXIII - Edição 1.236 - 09 de março de 2017": ("1236", "2017-03-09"),
                 "Semanário Oficial EXTRA - Ano XXIV - Edição 1.276 - 20 de novembro de 2017": ("1276", "2017-11-20"),
                 "Semanário Oficial - Ano XXVI - Edição 1.384 - EXTRA - 22 de fevereiro de 2019": ("1384", "2019-02-22"),
                 "Diário Oficial - Ano XXVII - Edição 1.553 - 05 de Novembro de 2020": ("1553", "2020-11-05")}
        for titulo, esperado in casos.items():
            self.assertEqual(p.edicao_impressa(pagina((133.0, titulo))), esperado, titulo)
        # sem título em texto (2013 e 2014), vale o rodapé; a linha de 2015 sem "Edição" não dá o número
        self.assertEqual(p.edicao_impressa(pagina((810.0, "Semanário Oficial | | Edição 1036 | Paulínia, 30 de outubro de 2013"))),
                         ("1036", "2013-10-30"))
        self.assertEqual(p.edicao_impressa(pagina((801.0, "Semanário Oficial | | 1118 | Paulínia, 11 de março de 2015 2"))), (None, None))
        for rodape in ("Semanário Oficial | | 1118 | Paulínia, 11 de março de 2015 2",
                       "Semanário Ofi cial | | Edição 1.236 | Paulínia, 09 de março de 2017 | 2",
                       "Semanário Oficial EXTRA | | Edição 1.276 | Paulínia, 20 de novembro de 2017 | 2"):
            _, altura, palavras = pagina((26.0, "TEXTO"), (801.0, rodape))[1]
            self.assertEqual(p.mancha(altura, palavras), (15.0, 800.0), rodape)

    def test_mancha_deixa_fora_o_numero_da_pagina_composto_acima_do_rodape(self):
        palavras = [(30.0, 26.0, 80.0, 36.0, "TEXTO"), (30.0, 790.0, 80.0, 800.0, "corpo"),
                    (30.0, 807.0, 40.0, 818.0, "2"), (45.0, 807.0, 100.0, 818.0, "PAULÍNIA"),
                    (200.0, 810.0, 260.0, 820.0, "Semanário"), (265.0, 810.0, 300.0, 820.0, "Oficial"), (305.0, 810.0, 308.0, 820.0, "|"),
                    (312.0, 810.0, 315.0, 820.0, "|"), (320.0, 810.0, 350.0, 820.0, "Edição"), (355.0, 810.0, 380.0, 820.0, "1036")]
        self.assertEqual(p.mancha(841.9, palavras), (15.0, 806.0))

    def test_carimbo_da_assinatura_digital_sai_e_o_texto_fica(self):
        texto = ("Prédio Ulysses Guimarães, 19 de fevereiro de 2026\n"
                 "                                                                   Assinado de\n"
                 "VEREADOR FULANO                                                    forma digital por\n"
                 "PRESIDENTE                                                         MUNICIPIO DE\n"
                 "                                                                   PAULINIA:45751\n"
                 "Publicado na Secretaria. Data supra.                               435000106\n"
                 "                                                                   Dados:\n"
                 "BELTRANO DE TAL                                                    2026.02.24\n"
                 "DIRETOR DO DEPARTAMENTO LEGISLATIVO                                17:44:12 -03'00'\n"
                 "Valor total                                                        2026.02.24\n")
        limpo = [ln for ln in p.sem_carimbo(texto).split("\n") if ln.strip()]
        self.assertEqual(limpo, ["Prédio Ulysses Guimarães, 19 de fevereiro de 2026", "VEREADOR FULANO", "PRESIDENTE",
                                 "Publicado na Secretaria. Data supra.", "BELTRANO DE TAL", "DIRETOR DO DEPARTAMENTO LEGISLATIVO",
                                 "Valor total                                                        2026.02.24"])

    def test_sem_carimbo_nada_muda(self):
        texto = "DESPESA      FUNCIONAL PROGRAMÁTICA      VALOR\n1222       02.16.01      4000000\nArt. 2º Texto de 2026.02.24\n"
        self.assertEqual(p.sem_carimbo(texto), texto)

    def test_listagem_do_portal(self):
        pagina = ('x<div class="dof_publicacao_diario sw_item_listagem"><a href="/portal/diario-oficial/ver/1964">'
                  '<span>Edição nº 2880</span></a><a href="/portal/download/diario-oficial/qdxwLj/">Baixar</a>'
                  '<span>Postagem:</span> 12/11/2026 às 17h38</div>'
                  '<div class="dof_publicacao_diario sw_item_listagem"><a href="/portal/diario-oficial/ver/1325">'
                  '<span>Edição nº 2251</span></a><a href="/portal/download/diario-oficial/qsxo/">Baixar</a></div>')
        self.assertEqual(p.edicoes_da_pagina(pagina),
                         [{"id": "1964", "edicao": "2880", "data": "2026-11-12", "token": "qdxwLj"},
                          {"id": "1325", "edicao": "2251", "data": None, "token": "qsxo"}])

    def test_codigo_de_download_com_hifen_vem_inteiro(self):
        pagina = ('<div class="dof_publicacao_diario sw_item_listagem"><a href="/portal/diario-oficial/ver/1820">'
                  '<span>Edição nº 2737</span></a><a href="/portal/download/diario-oficial/ddxz-A/">Baixar</a>'
                  'Postagem: 09/04/2026</div>')
        self.assertEqual(p.edicoes_da_pagina(pagina)[0]["token"], "ddxz-A")

    def test_edicao_impressa_no_titulo_e_no_rodape(self):
        def linha(y, texto):
            return [(10.0 + 40 * i, y, 45.0 + 40 * i, y + 10, w) for i, w in enumerate(texto.split())]
        titulo = {1: (722.8, 841.9, linha(154.0, "Diário Oficial - Ano XXXIII - Edição 2.881 - 13 de Novembro de 2026"))}
        self.assertEqual(p.edicao_impressa(titulo), ("2881", "2026-11-13"))
        rodape = {1: (722.8, 841.9, linha(30.0, "LEI Nº 1")), 2: (722.8, 841.9, linha(801.0, "Diário Oficial | | Edição 2.880 | Paulínia, 12 de Novembro de 2026 | 2"))}
        self.assertEqual(p.edicao_impressa(rodape), ("2880", "2026-11-12"))
        self.assertEqual(p.edicao_impressa({1: (722.8, 841.9, linha(30.0, "Edição 9.999 de outro texto"))}), (None, None))

    def test_formato_fora_do_modelo(self):
        self.assertIsNone(p.fora_do_modelo({1: (722.835, 841.89, [])}))
        self.assertIn("fora do leiaute", p.fora_do_modelo({1: (722.835, 841.89, []), 2: (651.969, 864.567, [])}))


if __name__ == "__main__":
    unittest.main()
