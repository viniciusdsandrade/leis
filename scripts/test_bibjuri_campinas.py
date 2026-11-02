"""O texto do bibjuri só entra no acervo quando a epígrafe confirma a ficha do SAPL e a página não esconde conteúdo em imagem."""
import datetime as dt
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import baixar_bibjuri_campinas as b  # noqa: E402
from auditar import validar  # noqa: E402

INFO = b.TIPOS["decreto"]
FICHA = {"id": 32979, "numero": "4813", "data": "1975-12-29", "ano": 1975, "texto_integral": ""}
CARTAO = {"id": 100364, "numero": "4813", "data": "1975-12-29", "titulo": "Decreto nº 4.813, de 29/12/1975"}
CORPO_HTML = (
    '<p style="text-align: center;"><strong>DECRETO N&ordm; 4.813 DE 29 DE DEZEMBRO DE 1975</strong></p>'
    '<p style="text-align: center;"><em>(Publica&ccedil;&atilde;o DOM 30/12/1975)</em></p>'
    '<p><strong>FIXA NORMAS PARA A EXECU&Ccedil;&Atilde;O OR&Ccedil;AMENT&Aacute;RIA.</strong></p>'
    '<p>O PREFEITO MUNICIPAL DE CAMPINAS, usando das atribui&ccedil;&otilde;es legais,</p>'
    '<p>DECRETA:</p>'
    '<artigo><p><strong>Art. 1&ordm;</strong> - A execu&ccedil;&atilde;o do Or&ccedil;amento-Programa ser&aacute; realizada '
    'em conformidade com a legisla&ccedil;&atilde;o pertinente e o disposto nas presentes Normas.</p></artigo>'
    '<artigo><p><strong>Art. 2&ordm;</strong> - Este decreto entra em vigor na data de sua publica&ccedil;&atilde;o.</p></artigo>'
    '<p>Pa&ccedil;o Municipal, 29 de dezembro de 1975</p>'
    '<p><strong>DR. LAURO P&Eacute;RICLES GON&Ccedil;ALVES</strong><br>Prefeito Municipal</p>'
)


def pagina(conteudo):
    """Página inteira do bibjuri: cabeçalho do site, bloco da norma e rodapé."""
    return (
        '<html><head><meta charset="iso-8859-1"><title>Biblioteca Jur&iacute;dica</title></head><body>'
        '<img src="/img/logo.png"><a href="/index/visualizaratualizada/id/100364">Texto Consolidado</a>'
        '<div id="div-conteudo-lei"><div style="clear:both;"><p class="container"><span style="color: red;">'
        'Este texto n&atilde;o substitui o publicado no Di&aacute;rio Oficial do Munic&iacute;pio - DOM.</span></p></div>'
        '<div id="principal" style="clear:both;"><!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN"><html><body>'
        + conteudo +
        '</body></html></div></div><h5>Visite tamb&eacute;m:</h5><a href="http://www.campinas.sp.gov.br/diario-oficial/">DOM</a>'
        '<img src="/img/ima.png"></body></html>'
    )


class Bloco(unittest.TestCase):
    def test_isola_o_documento_da_norma(self):
        bloco = b.bloco_conteudo(pagina(CORPO_HTML))
        self.assertIn("DECRETO N&ordm; 4.813", bloco)
        self.assertIn("Prefeito Municipal", bloco)
        self.assertNotIn("Visite tamb", bloco)
        self.assertNotIn("Texto Consolidado", bloco)
        self.assertNotIn("logo.png", bloco)

    def test_pagina_sem_bloco(self):
        self.assertIsNone(b.bloco_conteudo("<html><body><p>Nada aqui</p></body></html>"))

    def test_imagem_so_conta_dentro_do_bloco(self):
        self.assertFalse(b.imagem_embutida(b.bloco_conteudo(pagina(CORPO_HTML))))
        com_figura = CORPO_HTML + '<p><img src="data:image/png;base64,iVBORw0KGgo="></p>'
        self.assertTrue(b.imagem_embutida(b.bloco_conteudo(pagina(com_figura))))

    def test_reconhece_pagina_sem_texto_original(self):
        self.assertTrue(b.sem_original(b.bloco_conteudo(pagina("<p>Este conte&uacute;do n&atilde;o possui Original.</p>"))))
        self.assertFalse(b.sem_original(b.bloco_conteudo(pagina(CORPO_HTML))))

    def test_reconhece_remissao_a_pdf_digitalizado(self):
        stub = ('<p>DECRETO N&ordm; 4.811 DE 22 DE DEZEMBRO DE 1975</p><p>DECRETA:</p>'
                '<p>CONSULTAR TEXTO NA <a href="/images/full/d1787fad.pdf" target="blank">&Iacute;NTEGRA</a></p>')
        self.assertEqual(b.anexo_da_fonte(b.bloco_conteudo(pagina(stub))), "https://bibjuri.campinas.sp.gov.br/images/full/d1787fad.pdf")
        self.assertIsNone(b.anexo_da_fonte(b.bloco_conteudo(pagina(CORPO_HTML))))


class Conversao(unittest.TestCase):
    def test_aviso_e_publicacao_saem_do_corpo(self):
        bloco = b.bloco_conteudo(pagina(CORPO_HTML))
        corpo, publicacao, notas = b.converter(bloco)
        self.assertTrue(corpo.lstrip("*").startswith("DECRETO Nº 4.813 DE 29 DE DEZEMBRO DE 1975"), corpo[:80])
        self.assertNotIn("não substitui", corpo)
        self.assertNotIn("Publicação DOM", corpo)
        self.assertEqual(publicacao, "DOM 30/12/1975")
        self.assertEqual(notas[0], b.NOTA_AVISO)
        self.assertIn("**Art. 1º**", corpo)
        self.assertIn("Prefeito Municipal", corpo)

    def test_publicacao_com_pagina(self):
        html = CORPO_HTML.replace("(Publica&ccedil;&atilde;o DOM 30/12/1975)", "(Publica&ccedil;&atilde;o DOM 28/12/2005 : 01)")
        _, publicacao, _ = b.converter(b.bloco_conteudo(pagina(html)))
        self.assertEqual(publicacao, "DOM 28/12/2005 p.01")


class Identidade(unittest.TestCase):
    def test_aceita_variacoes_de_formatacao(self):
        for epigrafe in ("DECRETO Nº 4.813 DE 29 DE DEZEMBRO DE 1975", "DECRETO N.º 4813, DE 29 DE DEZEMBRO DE 1975",
                         "**DECRETO N° 4.813, de 29 de dezembro de 1975**", "DECRETO No 4.813 - DE 29 DE DEZEMBRO DE 1975",
                         "DECRETO N. º 4.813, DE 29 DE DEZEMBRO DE 1975", "DECRETO N.º 4 813 DE 29 DE DEZEMBRO DE 1 .975",
                         "DECRETO N.º 4.813, DE 29 DE DEZEMBRO DE 1.975.", "DECRETO Nº 4,813, DE 29 DE DEZEMBRO DE 1975",
                         "DECRETO N/4813, DE 29 DE DEZEMBRO DE 1975", "DECRETO Nº 4.813. DE 29 DE DEZEMBRO DE 1975."):
            corpo = epigrafe + "\n\nEmenta.\n\nDECRETA:\n\n**Art. 1º** Texto.\n\nPaço Municipal, 29 de dezembro de 1975"
            self.assertIsNone(b.identidade(corpo, FICHA, INFO), epigrafe)

    def test_dia_primeiro_com_ponto_e_ordinal(self):
        ficha = {"id": 31572, "numero": "3614", "data": "1970-04-01"}
        corpo = "DECRETO N.º 3614 DE 1.º DE ABRIL DE 1970\n\nDECRETA:\n\n**Art. 1º** Texto.\n\nCampinas, 1.º de abril de 1970"
        self.assertIsNone(b.identidade(corpo, ficha, INFO))

    def test_fecho_por_extenso_com_dias_do_mes(self):
        ficha = {"id": 31585, "numero": "3626", "data": "1970-05-05"}
        corpo = "DECRETO N.º 3 626\n\nDECRETA:\n\n**Art. 1º** Texto.\n\nLavrado aos 5 dias do mês de Maio de 1 .970, por mim."
        self.assertIsNone(b.identidade(corpo, ficha, INFO))

    def test_recusa_numero_diferente(self):
        corpo = "DECRETO Nº 4.814 DE 29 DE DEZEMBRO DE 1975\n\nDECRETA:\n\n**Art. 1º** Texto."
        self.assertIn("número da epígrafe (4814)", b.identidade(corpo, FICHA, INFO))

    def test_recusa_data_diferente(self):
        corpo = "DECRETO Nº 4.813 DE 28 DE DEZEMBRO DE 1975\n\nDECRETA:\n\n**Art. 1º** Texto."
        self.assertIn("data da epígrafe (1975-12-28)", b.identidade(corpo, FICHA, INFO))

    def test_recusa_sem_epigrafe_e_nao_confunde_citacao(self):
        citacao = "Altera o Decreto nº 4.813, de 29 de dezembro de 1975.\n\nDECRETA:\n\n**Art. 1º** Texto."
        self.assertIsNone(b.identidade("DECRETO Nº 4.813 DE 29 DE DEZEMBRO DE 1975\n\n" + citacao, FICHA, INFO))
        self.assertIn("epígrafe", b.identidade(citacao, FICHA, INFO))
        self.assertIn("epígrafe", b.identidade("Texto sem cabeçalho.\n\nDECRETA:\n\n**Art. 1º** Texto.", FICHA, INFO))

    def test_epigrafe_antiga_sem_data_confere_o_fecho(self):
        ficha = {"id": 1, "numero": "287", "data": "1900-12-17", "ano": 1900}
        info = b.TIPOS["lei"]
        corpo = "LEI N. 287 (Declara de utilidade publica o terreno.)\n\nA Camara Municipal decreta:\n\n**Art. 1º** Texto.\n\nCampinas, 17 de dezembro de 1900"
        self.assertIsNone(b.identidade(corpo, ficha, info))
        self.assertIn("fecho sem a data", b.identidade(corpo.replace("17 de dezembro de 1900", "18 de dezembro de 1900"), ficha, info))

    def test_decreto_lei_tem_epigrafe_propria(self):
        ficha = {"id": 39737, "numero": "96", "data": "1941-05-13", "ano": 1941}
        resto = "\n\nDECRETA:\n\n**Art. 1º** Texto.\n\nPrefeitura Municipal de Campinas, 13 de maio de 1941"
        for epigrafe in ("DECRETO-LEI Nº 96, DE 13 DE MAIO DE 1941", "DECRETO LEI N. 96, DE 13 DE MAIO DE 1941", "DECRETO-LEI N.º 96"):
            self.assertIsNone(b.identidade(epigrafe + resto, ficha, b.TIPOS["decreto-lei"]), epigrafe)
        # a epígrafe de um decreto-lei não confirma decreto nem lei, e a de um decreto não confirma decreto-lei
        self.assertIn("epígrafe", b.identidade("DECRETO-LEI Nº 96, DE 13 DE MAIO DE 1941" + resto, ficha, b.TIPOS["decreto"]))
        self.assertIn("epígrafe", b.identidade("DECRETO-LEI Nº 96, DE 13 DE MAIO DE 1941" + resto, ficha, b.TIPOS["lei"]))
        self.assertIn("epígrafe", b.identidade("DECRETO Nº 96, DE 13 DE MAIO DE 1941" + resto, ficha, b.TIPOS["decreto-lei"]))


class Integridade(unittest.TestCase):
    CORPO = ("DECRETO Nº 4.813 DE 29 DE DEZEMBRO DE 1975\n\nFixa normas.\n\nO PREFEITO MUNICIPAL DE CAMPINAS,\n\nDECRETA:\n\n"
             "**Art. 1º** - A execução do orçamento será realizada conforme a legislação pertinente.\n\n"
             "**Art. 2º** - Este decreto entra em vigor na data de sua publicação.\n\n"
             "Paço Municipal, 29 de dezembro de 1975\n\n**DR. LAURO PÉRICLES GONÇALVES**  \nPrefeito Municipal")

    def test_texto_integro_passa(self):
        self.assertIsNone(b.integridade(self.CORPO, FICHA, INFO))

    def test_formula_de_decretacao_omitida_na_transcricao_nao_retem(self):
        self.assertIsNone(b.integridade(self.CORPO.replace("\n\nDECRETA:", ""), FICHA, INFO))

    def test_artigo_sem_a_palavra_artigo_na_transcricao(self):
        corpo = self.CORPO.replace("**Art. 1º** - A", "**1º** - A").replace("**Art. 2º** - Este", "**2º** - Este")
        self.assertIsNone(b.integridade(corpo, FICHA, INFO))
        self.assertIn("artigo inicial", b.integridade(corpo.replace("**1º** - A", "1 - A").replace("**2º** - Este", "2 - Este"), FICHA, INFO))

    def test_outra_epigrafe_retem(self):
        corpo = self.CORPO + "\n\nDECRETO Nº 4.814 DE 29 DE DEZEMBRO DE 1975\n\nDECRETA:\n\n**Art. 1º** Outro ato."
        self.assertIn("mais de um ato", b.integridade(corpo, FICHA, INFO))

    def test_ato_nao_articulado_e_apontado_como_tal(self):
        corpo = ("DECRETO Nº 1.533, DE 15 DE FEVEREIRO DE 1960.\n\nAposenta o Sr. João, funcionário.\n\n"
                 "O Prefeito Municipal de Campinas, usando das atribuições que lhe são conferidas por lei,\n\n"
                 "A P O S E N T A, a partir de 29 de dezembro de 1959, o Sr. João no cargo de Chefe do Serviço de Limpeza Pública.\n\n"
                 "Campinas, 15 de fevereiro de 1960\n\n**MIGUEL VICENTE CURY**  \nPrefeito Municipal")
        self.assertTrue(b.integridade(corpo, {"numero": "1533", "data": "1960-02-15"}, INFO).startswith("ato em forma não articulada"))

    def test_sem_fecho_ou_sem_artigo_retem(self):
        self.assertIn("fecho", b.integridade(self.CORPO.split("Paço Municipal")[0] + "Texto final sem assinatura nem local.", FICHA, INFO))
        self.assertIn("artigo inicial", b.integridade(self.CORPO.replace("**Art. 1º**", "Item 1").replace("**Art. 2º**", "Item 2"), FICHA, INFO))


class Avaliacao(unittest.TestCase):
    def test_texto_integro_sem_anexo_passa(self):
        motivo, corpo, publicacao, notas, pdf = b.avaliar(b.bloco_conteudo(pagina(CORPO_HTML)), FICHA, INFO)
        self.assertIsNone(motivo)
        self.assertIsNone(pdf)
        self.assertEqual(publicacao, "DOM 30/12/1975")

    def test_anexo_em_pdf_da_fonte_retem_mesmo_com_texto_integro(self):
        html = CORPO_HTML + '<p>ANEXO: <a href="/images/full/abc.pdf">quadro</a></p>'
        motivo, *_, pdf = b.avaliar(b.bloco_conteudo(pagina(html)), FICHA, INFO)
        self.assertIn("anexo do ato em arquivo digitalizado", motivo)
        self.assertEqual(pdf, "https://bibjuri.campinas.sp.gov.br/images/full/abc.pdf")

    def test_remissao_a_pdf_sem_texto_retem_com_o_endereco(self):
        stub = ('<p>DECRETO N&ordm; 4.813 DE 29 DE DEZEMBRO DE 1975</p><p>DECRETA:</p>'
                '<p>CONSULTAR TEXTO NA <a href="/images/full/d1787fad.pdf">&Iacute;NTEGRA</a></p>')
        motivo, *_, pdf = b.avaliar(b.bloco_conteudo(pagina(stub)), FICHA, INFO)
        self.assertTrue(motivo.startswith("texto não transcrito na fonte"))
        self.assertTrue(pdf.endswith("/images/full/d1787fad.pdf"))

    def test_so_ementa_retem(self):
        motivo, *_ = b.avaliar(b.bloco_conteudo(pagina("<p>Disp&otilde;e sobre abertura de cr&eacute;dito suplementar.</p>")), FICHA, INFO)
        self.assertTrue(motivo.startswith("página sem o texto do ato"))

    def test_texto_de_outro_ato_com_o_mesmo_numero_e_data_retem(self):
        ficha = {**FICHA, "ementa": "AUTORIZA A VENDA DE UM LOTE DE TERRENO PERTECENTE AO PATRIMO NIO MUNICIPAL"}
        motivo, *_ = b.avaliar(b.bloco_conteudo(pagina(CORPO_HTML)), ficha, INFO)
        self.assertTrue(motivo.startswith("ementa da ficha do SAPL não confere com o texto"), motivo)
        ficha["ementa"] = "FIXA NORMAS PARA A EXECUCAO ORCAMENTARIA DO EXERCICIO FINANCEIRO DE 1976 E DA OUTRAS PROVIDENCIAS."
        self.assertIsNone(b.avaliar(b.bloco_conteudo(pagina(CORPO_HTML)), ficha, INFO)[0])


class Ementa(unittest.TestCase):
    """A ementa da ficha do SAPL tem de reaparecer no texto do bibjuri (outro ato sob o mesmo número e data fica retido)."""
    OUTRO_ATO = ("DECRETO-LEI N. 29\n\nDeclara de utilidade pública uma área de terreno, à Rua Barreto Leme.\n\n"
                 "O Prefeito Municipal de Campinas, usando de suas atribuições,\n\nDECRETA:\n\n**Art. 1º** Fica declarada de "
                 "utilidade pública, para ser desapropriada, amigável ou judicialmente, uma área de terreno à rua Barreto Leme.\n\n"
                 "Paço Municipal de Campinas, aos 23 de fevereiro de 1940.")

    def test_grafia_antiga_acentos_e_erros_da_ficha_nao_retem(self):
        corpo = "LEI Nº 42\n\nSOBRE PADARIAS E FÁBRICAS DE BEBIDAS ARTIFICIAIS\n\n**Art. 1º** As padarias e fábricas..."
        self.assertIsNone(b.ementa_diverge(corpo, {"ementa": "SOBRE PADARIAS E FABRICAS DE BEBIDAS ARTIFICIAES."}))
        corpo = "DECRETO-LEI N. 338\n\nDispõe sobre aposentadoria de funcionários contribuintes de Institutos ou Caixas de Aposentadoria e Pensões."
        self.assertIsNone(b.ementa_diverge(corpo, {"ementa": "DISPÕE DA APOSENTADORIA DE FUNCIONÁRIOS CONTRIBUINTES DE INSTITUTOS OU CAXIAS DE APOSENTADORIA E PENSÕES ."}))

    def test_ementa_de_outro_ato_retem(self):
        motivo = b.ementa_diverge(self.OUTRO_ATO, {"ementa": "AUTORIZA A VENDA DE UM LOTE DE TERRENO PERTECENTE AO PATRIMO NIO MUNICIPAL"})
        self.assertEqual(motivo, "ementa da ficha do SAPL não confere com o texto (2 de 7 palavras): "
                                 "AUTORIZA A VENDA DE UM LOTE DE TERRENO PERTECENTE AO PATRIMO NIO MUNICIPAL")

    def test_ementa_curta_ou_ausente_nao_e_conferida(self):
        for ementa in ("", None, "SOBRE TRANSFERÊNCIA DE DOAÇÃO", "DA NOME A RUA"):
            self.assertIsNone(b.ementa_diverge(self.OUTRO_ATO, {"ementa": ementa}), ementa)
        self.assertIsNone(b.ementa_diverge(self.OUTRO_ATO, {}))


class FrontMatter(unittest.TestCase):
    def test_monta_no_molde_dos_lotes_do_sapl(self):
        bruto = pagina(CORPO_HTML).encode("iso-8859-1", errors="replace")
        corpo, publicacao, notas = b.converter(b.bloco_conteudo(bruto.decode("iso-8859-1")))
        hoje = dt.date(2026, 11, 1)
        texto = b.montar_md(FICHA, CARTAO, corpo, publicacao, notas, bruto, INFO, hoje)
        self.assertTrue(texto.startswith('---\ntitulo: "Decreto nº 4.813, de 29 de dezembro de 1975"\ntipo: "Decreto"\n'))
        for linha in ('numero: "4813"', 'data: "1975-12-29"', 'municipio: "Campinas"', 'codigo_ibge: "3509502"',
                      'publicacao: "DOM 30/12/1975"', 'fonte: "https://sapl.campinas.sp.leg.br/norma/32979"',
                      'fonte_texto: "https://bibjuri.campinas.sp.gov.br/index/visualizaroriginal/id/100364"',
                      f'sha256_fonte: "{hashlib.sha256(bruto).hexdigest()}"',
                      f'sha256_texto: "{hashlib.sha256(corpo.encode()).hexdigest()}"', 'baixado_em: "2026-11-01"'):
            self.assertIn(linha + "\n", texto)
        self.assertIn('versao_texto: "texto original (não consolidado); texto da Biblioteca Jurídica', texto)
        self.assertIn("\n---\n\n# Decreto nº 4.813, de 29 de dezembro de 1975\n\n", texto)
        erros, avisos = validar(texto, "municipais/SP/campinas/decretos/1975/decretos-4813-1975-sapl-32979.md", hoje)
        self.assertEqual((erros, avisos), ([], []))

    def test_edicao_consolidada_fica_declarada(self):
        bruto = pagina(CORPO_HTML).encode("iso-8859-1", errors="replace")
        corpo, publicacao, notas = b.converter(b.bloco_conteudo(bruto.decode("iso-8859-1")))
        texto = b.montar_md(FICHA, CARTAO, corpo, publicacao, notas, bruto, INFO, dt.date(2026, 11, 1), edicao="consolidado")
        self.assertIn('versao_texto: "texto consolidado pela fonte, que não publica o texto original desta norma;', texto)
        self.assertIn('fonte_texto: "https://bibjuri.campinas.sp.gov.br/index/visualizaratualizada/id/100364"', texto)

    def test_nome_do_arquivo_segue_o_padrao_das_pastas(self):
        self.assertTrue(str(b.destino_de(FICHA, INFO)).endswith("municipais/SP/campinas/decretos/1975/decretos-4813-1975-sapl-32979.md"))
        ficha = {"id": 7, "numero": "36", "data": "1947-12-30"}
        self.assertTrue(str(b.destino_de(ficha, b.TIPOS["lei"])).endswith("leis-ordinarias/1947/leis-ordinarias-36-1947-sapl-7.md"))
        ficha = {"id": 39737, "numero": "96", "data": "1941-05-13", "tipo": 17}
        self.assertTrue(str(b.destino_de(ficha, b.TIPOS["decreto-lei"])).endswith("decretos/1941/decretos-96-1941-sapl-39737.md"))

    def test_rotulo_do_tipo_vem_da_ficha_do_sapl_como_no_pipeline(self):
        bruto = pagina(CORPO_HTML).encode("iso-8859-1", errors="replace")
        corpo, publicacao, notas = b.converter(b.bloco_conteudo(bruto.decode("iso-8859-1")))
        hoje = dt.date(2026, 11, 2)
        for ficha, info, titulo, tipo, tipo_na_fonte in (
                ({"id": 39940, "numero": "172", "data": "1912-10-29", "tipo": 18}, b.TIPOS["lei"],
                 "Leis Até 1948 nº 172, de 29 de outubro de 1912", "Lei ordinária", "Leis Até 1948"),
                ({"id": 28291, "numero": "303", "data": "1949-12-30", "tipo": 1}, b.TIPOS["lei"],
                 "Lei nº 303, de 30 de dezembro de 1949", "Lei ordinária", "Lei"),
                ({"id": 39748, "numero": "99", "data": "1934-12-31", "tipo": 19}, INFO,
                 "Decretos Até 1948 nº 99, de 31 de dezembro de 1934", "Decreto", "Decretos Até 1948"),
                ({"id": 39823, "numero": "126", "data": "1941-12-31", "tipo": 17}, b.TIPOS["decreto-lei"],
                 "Decreto-lei nº 126, de 31 de dezembro de 1941", "Decreto-Lei", "Decreto-lei"),
                ({**FICHA, "tipo": 4}, INFO, "Decreto nº 4.813, de 29 de dezembro de 1975", "Decreto", "Decreto")):
            texto = b.montar_md(ficha, CARTAO, corpo, publicacao, notas, bruto, info, hoje)
            self.assertIn(f'titulo: "{titulo}"\ntipo: "{tipo}"\ntipo_na_fonte: "{tipo_na_fonte}"\n', texto)
            self.assertIn(f"\n# {titulo}\n", texto)

    def test_observacao_do_anexo_retido_no_front_matter(self):
        bruto = pagina(CORPO_HTML).encode("iso-8859-1", errors="replace")
        corpo, publicacao, notas = b.converter(b.bloco_conteudo(bruto.decode("iso-8859-1")))
        hoje = dt.date(2026, 11, 2)
        ficha = {**FICHA, "tipo": 4, "texto_integral": PDF_SAPL}
        texto = b.montar_md(ficha, CARTAO, corpo, publicacao, notas, bruto, INFO, hoje, retencao=OCR)
        observacao = (f"a ficha do SAPL tem anexo de texto ({PDF_SAPL}), retido por integridade no pipeline do SAPL: {OCR}; "
                      "o texto deste arquivo vem da Biblioteca Jurídica da Prefeitura (fonte_texto)")
        self.assertIn('fonte_texto: "https://bibjuri.campinas.sp.gov.br/index/visualizaroriginal/id/100364"\n'
                      f"observacao_fonte: {json.dumps(observacao, ensure_ascii=False)}\nsha256_fonte:", texto)
        self.assertEqual(validar(texto, "municipais/SP/campinas/decretos/1975/decretos-4813-1975-sapl-32979.md", hoje), ([], []))
        self.assertNotIn("observacao_fonte", b.montar_md(ficha, CARTAO, corpo, publicacao, notas, bruto, INFO, hoje))


class Cartoes(unittest.TestCase):
    PAGINA = ("<p>Exibindo <strong>215</strong> resultado(s)!</p>"
              "<a href='/index/visualizaratualizada/id/100364' title='Decreto n&ordm; 4.813, de 29/12/1975'>x</a>"
              "<a href='/index/visualizaratualizada/id/100363' title='Decreto n&ordm; 4812, de 23/12/1975'>x</a>")

    def test_le_total_id_numero_e_data(self):
        total, cartoes = b.cartoes_da_pagina(self.PAGINA)
        self.assertEqual(total, 215)
        self.assertEqual([(c["id"], c["numero"], c["data"]) for c in cartoes],
                         [(100364, "4813", "1975-12-29"), (100363, "4812", "1975-12-23")])

    def test_casa_por_numero_com_a_mesma_data_primeiro(self):
        _, cartoes = b.cartoes_da_pagina(self.PAGINA)
        cartoes.append({"id": 1, "numero": "4813", "data": "1998-01-01", "titulo": ""})
        self.assertEqual([c["id"] for c in b.casar(FICHA, cartoes)], [100364, 1])
        self.assertEqual(b.casar({"numero": "9999", "data": "1975-01-01"}, cartoes), [])

    def test_zero_a_esquerda_no_cartao_nao_impede_o_casamento(self):
        # cartões de 1892: "Lei nº 07, de 06/11/1892" é a lei 7 da ficha do SAPL
        _, cartoes = b.cartoes_da_pagina("<p>Exibindo <strong>2</strong> resultado(s)!</p>"
                                         "<a href='/index/visualizaratualizada/id/132471' title='Lei n&ordm; 07, de 06/11/1892'>x</a>"
                                         "<a href='/index/visualizaratualizada/id/132472' title='Lei n&ordm; 70, de 06/11/1892'>x</a>")
        self.assertEqual([c["id"] for c in b.casar({"numero": "7", "data": "1892-11-06"}, cartoes)], [132471])
        self.assertEqual([c["id"] for c in b.casar({"numero": "70", "data": "1892-11-06"}, cartoes)], [132472])


PDF_SAPL = "https://sapl.campinas.sp.leg.br/media/sapl/public/normajuridica/1912/39940/39940_texto_integral.pdf"
OCR = "OCR com baixa legibilidade (74% das palavras conhecidas no acervo do município); revisar"


class AnexoRetido(unittest.TestCase):
    """--incluir-retidas: ficha com anexo no SAPL que o pipeline do SAPL reteve por integridade."""

    def test_registro_de_retidos_integralidade_vale_enquanto_o_anexo_e_o_mesmo(self):
        retidos = {"39957": {"sha256_fonte": "aa", "motivo": "página do livro de leis com mais de um ato; revisar"}}
        self.assertEqual(b.retencao_registrada(39957, retidos, {}, sha_anexo="aa"), "página do livro de leis com mais de um ato; revisar")
        self.assertEqual(b.retencao_registrada(39957, retidos, {}), "página do livro de leis com mais de um ato; revisar")
        self.assertIsNone(b.retencao_registrada(39957, retidos, {}, sha_anexo="bb"))  # anexo trocado depois da retenção

    def test_ultima_falha_de_conteudo_conta(self):
        for erro in (OCR, "página de livro de leis: artigos fora de ordem no recorte (colunas entrelaçadas pelo OCR); revisar",
                     "o número da norma não aparece no começo do texto; conferir a identidade do anexo",
                     "página do livro de leis não abre com a epígrafe da própria norma; recortar o ato antes de publicar",
                     "PDF sem texto legível (nem por OCR)", "texto sem artigo inicial reconhecível; revisar integralidade"):
            self.assertEqual(b.retencao_registrada(39940, {}, {39940: {"id": 39940, "erro": erro}}), erro)

    def test_falha_de_rede_de_ferramenta_ou_sem_anexo_nao_conta(self):
        for erro in ("[Errno 2] No such file or directory: 'pdftotext'", "HTTP 404: " + PDF_SAPL, "norma sem texto integral",
                     "Command '['pdftoppm', '-png']' returned non-zero exit status 1.", ""):
            self.assertIsNone(b.retencao_registrada(39940, {}, {39940: {"id": 39940, "erro": erro}}), erro)
        self.assertIsNone(b.retencao_registrada(39940, {}, {}))
        self.assertIsNone(b.retencao_registrada(39940, {}, {1: {"id": 1, "erro": OCR}}))

    def test_duvida_sobre_a_data_do_cadastro_nao_conta(self):
        falha = "data do cadastro (2002-03-14) diverge do ano da norma (2003) e da publicação (2003-03-15); revisar"
        self.assertIsNone(b.retencao_registrada(1, {}, {1: {"id": 1, "erro": falha}}))
        retidos = {"13405": {"sha256_fonte": "aa", "motivo": "data do texto e do cadastro 05/01/1964, mas o cadastro é de 1965; revisar a data"}}
        self.assertIsNone(b.retencao_registrada(13405, retidos, {}, sha_anexo="aa"))

    def test_motivo_sem_prefixo_nem_json_dos_alertas(self):
        falha = 'fonte retida para revisão de integralidade: anexo contém epígrafe de outra norma; revisar granularidade: [{"x": 1}]'
        self.assertEqual(b.retencao_registrada(5, {}, {5: {"id": 5, "erro": falha}}),
                         "anexo contém epígrafe de outra norma; revisar granularidade")
        self.assertLessEqual(len(b.motivo_legivel("revisar " + "x" * 500)), 300)

    def test_registros_leem_a_ultima_falha_de_cada_ficha(self):
        with tempfile.TemporaryDirectory() as tmp:
            pasta = Path(tmp)
            (pasta / "falhas.jsonl").write_text("\n".join([
                json.dumps({"id": 39940, "erro": OCR, "quando": "2026-10-30"}),
                json.dumps({"erro": "falha do município inteiro", "quando": "2026-10-30"}),
                json.dumps({"id": 39940, "erro": "[Errno 2] No such file or directory: 'pdftotext'", "quando": "2026-10-31"}),
                json.dumps({"id": 40141, "erro": "norma sem texto integral", "quando": "2026-10-21"}),
                json.dumps({"id": 40141, "erro": OCR, "quando": "2026-11-01"}),
                '{"id": 1, "erro": "linha trunc']) + "\n")
            (pasta / "retidos-integralidade.json").write_text(json.dumps({"39957": {"sha256_fonte": "aa", "motivo": "x; revisar"}}))
            with mock.patch.object(b, "CACHE_SAPL", pasta):
                retidos, falhas = b.registros_de_retencao()
        self.assertEqual(set(falhas), {39940, 40141})
        self.assertIsNone(b.retencao_registrada(39940, retidos, falhas))  # a última falha foi de ferramenta
        self.assertEqual(b.retencao_registrada(40141, retidos, falhas), OCR)
        self.assertEqual(b.retencao_registrada(39957, retidos, falhas), "x; revisar")

    def test_alvos_com_anexo_so_quando_retido_e_sem_md(self):
        fichas = [{"id": 1, "texto_integral": None}, {"id": 2, "texto_integral": ""},  # sem anexo: 2 já publicada
                  {"id": 3, "texto_integral": PDF_SAPL}, {"id": 4, "texto_integral": PDF_SAPL},  # retidas: 4 já publicada
                  {"id": 5, "texto_integral": PDF_SAPL}]  # anexo não retido
        retencao = {3: OCR, 4: OCR}.get
        self.assertEqual([(n["id"], m) for n, m in b.alvos_do_ano(fichas, {2, 4}, lambda n: retencao(n["id"]))],
                         [(1, None), (3, OCR)])
        self.assertEqual([(n["id"], m) for n, m in b.alvos_do_ano(fichas, {2, 4})], [(1, None)])


class Processar(unittest.TestCase):
    """processar sem rede: a página do bibjuri vem de uma fonte falsa e o .md vai para uma pasta temporária."""

    class FonteFalsa:
        def __init__(self, paginas):
            self.paginas = paginas

        def get(self, url, destino):
            return self.paginas[url], True

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        raiz = Path(self.tmp.name) / "municipais"
        for alvo, valor in (("RAIZ", raiz), ("MUNICIPIO", raiz / "SP/campinas")):
            patcher = mock.patch.object(b, alvo, valor)
            patcher.start()
            self.addCleanup(patcher.stop)
        self.addCleanup(self.tmp.cleanup)
        url = f"{b.BIBJURI}/index/visualizaroriginal/id/{CARTAO['id']}"
        self.fonte = self.FonteFalsa({url: pagina(CORPO_HTML).encode("iso-8859-1", errors="replace")})

    def test_anexo_retido_gera_md_com_observacao_e_a_pagina_nao_serve_a_segunda_ficha(self):
        ficha = {**FICHA, "tipo": 4, "texto_integral": PDF_SAPL}
        usadas = {}
        estado, detalhe = b.processar(self.fonte, ficha, [CARTAO], INFO, dt.date(2026, 11, 2), retencao=OCR, usadas=usadas)
        self.assertEqual(estado, "novo", detalhe)
        texto = (b.RAIZ.parent / detalhe["caminho"]).read_text(encoding="utf-8")
        self.assertIn(f'observacao_fonte: "a ficha do SAPL tem anexo de texto ({PDF_SAPL}), retido por integridade no pipeline do '
                      f'SAPL: {OCR}; o texto deste arquivo vem da Biblioteca Jurídica da Prefeitura (fonte_texto)"\n', texto)
        self.assertEqual(usadas, {CARTAO["id"]: detalhe["caminho"]})
        outra = {**ficha, "id": 32980}
        estado, detalhe = b.processar(self.fonte, outra, [CARTAO], INFO, dt.date(2026, 11, 2), retencao=OCR, usadas=usadas)
        self.assertEqual(estado, "retida")
        self.assertIn("já deu texto a outro .md", detalhe["motivo"])

    def test_ano_do_cadastro_diferente_do_ano_da_data_retem_sem_consultar_a_fonte(self):
        ficha = {"id": 56858, "numero": "335", "data": "1946-06-11", "ano": 1944, "tipo": 17, "texto_integral": None}
        estado, detalhe = b.processar(self.FonteFalsa({}), ficha, [], b.TIPOS["decreto-lei"], dt.date(2026, 11, 2))
        self.assertEqual(estado, "retida")
        self.assertIn("ano do cadastro do SAPL (1944)", detalhe["motivo"])


class FonteTextoCoerente(unittest.TestCase):
    """Regra usada por scripts/municipios/campinas/campinas.py verificar (fora do checkout do CI; a regra fica aqui)."""
    PDF = "https://sapl.campinas.sp.leg.br/media/sapl/public/normajuridica/1975/32979/32979_texto_integral.pdf"
    BIBJURI = "https://bibjuri.campinas.sp.gov.br/index/visualizaroriginal/id/100364"

    def test_anexo_do_sapl_continua_valendo_sem_esquema(self):
        self.assertTrue(b.fonte_texto_coerente(self.PDF, self.PDF))
        self.assertTrue(b.fonte_texto_coerente(self.PDF, self.PDF.replace("https://", "http://")))
        self.assertFalse(b.fonte_texto_coerente(self.PDF.replace("32979", "32978"), self.PDF))

    def test_bibjuri_vale_so_quando_a_ficha_nao_tem_anexo(self):
        self.assertTrue(b.fonte_texto_coerente(self.BIBJURI, ""))
        self.assertTrue(b.fonte_texto_coerente(self.BIBJURI, None))
        self.assertTrue(b.fonte_texto_coerente(self.BIBJURI.replace("visualizaroriginal", "visualizaratualizada"), ""))
        self.assertFalse(b.fonte_texto_coerente(self.BIBJURI, self.PDF))

    def test_outros_enderecos_nao_valem_para_ficha_sem_anexo(self):
        self.assertFalse(b.fonte_texto_coerente("https://bibjuri.campinas.sp.gov.br/images/full/abc.pdf", ""))
        self.assertFalse(b.fonte_texto_coerente("https://outro.sp.gov.br/index/visualizaroriginal/id/1", ""))
        self.assertFalse(b.fonte_texto_coerente("", ""))

    def test_tres_casos_do_bibjuri(self):
        self.assertTrue(b.fonte_texto_coerente(self.BIBJURI, ""))  # ficha sem anexo
        self.assertTrue(b.fonte_texto_coerente(self.BIBJURI, self.PDF, anexo_retido=True))  # anexo retido por integridade
        self.assertTrue(b.fonte_texto_coerente(self.BIBJURI.replace("visualizaroriginal", "visualizaratualizada"), self.PDF, True))
        self.assertFalse(b.fonte_texto_coerente(self.BIBJURI, self.PDF))  # anexo não retido: só ele vale

    def test_anexo_retido_nao_abre_para_outros_enderecos_nem_fecha_o_proprio_anexo(self):
        self.assertTrue(b.fonte_texto_coerente(self.PDF, self.PDF, anexo_retido=True))  # registro de retenção antigo
        self.assertFalse(b.fonte_texto_coerente(self.PDF.replace("32979", "32978"), self.PDF, anexo_retido=True))
        self.assertFalse(b.fonte_texto_coerente("https://bibjuri.campinas.sp.gov.br/images/full/abc.pdf", self.PDF, anexo_retido=True))
        self.assertFalse(b.fonte_texto_coerente("https://outro.sp.gov.br/index/visualizaroriginal/id/1", self.PDF, anexo_retido=True))


if __name__ == "__main__":
    unittest.main()
