"""O texto do bibjuri só entra no acervo quando a epígrafe confirma a ficha do SAPL e a página não esconde conteúdo em imagem."""
import datetime as dt
import hashlib
import sys
import unittest
from pathlib import Path

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


if __name__ == "__main__":
    unittest.main()
