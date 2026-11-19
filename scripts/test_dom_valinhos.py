import datetime as dt
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import baixar_dom_valinhos as v

base = v.base

LEI = """Mens. 77/26 – P.L. 264/26 – Aut. 172/26 – Prot. Leg. 8.008/26

LEI Nº 7.015, DE 18 DE NOVEMBRO DE 2026
Altera a Lei nº 6.964/2026, para autorizar a entrega de bens imóveis em pagamento das dívi-
das previdenciárias do Município de Valinhos com a União, e dá outras providências.

FRANKLIN DUARTE DE LIMA, Prefeito do Município de Valinhos, no uso das atribuições que lhe são conferidas
pelo art. 80, inciso III, da Lei Orgânica do Município,

FAZ SABER que a Câmara Municipal aprovou e ele sanciona e promulga a seguinte Lei:

Art. 1º A ementa da Lei nº 6.964, de 26 de agosto de 2026, passa a vigorar com a seguinte redação.
Art. 2º Esta Lei entra em vigor na data de sua publicação.

Prefeitura do Município de Valinhos,
18 de novembro de 2026, 130° do Distrito de Paz,
71° do Município e 21° da Comarca.

FRANKLIN DUARTE DE LIMA
Prefeito Municipal

THIAGO EDUARDO GALVÃO CAPELLATO
Secretário de Assuntos Jurídicos

Conferida, numerada e datada neste Departamento, na forma regulamentar, em
conformidade com o Memorando/CI nº 5.434/2026 e Processo Administrativo nº
14.172/26 – PMV.

Evandro Régis Zani
Subchefe do Gabinete da Prefeita
Respondendo pelo Depto. Técnico-Legislativo/SAJI

Projeto de Lei de iniciativa do Poder Executivo.

Mens. 72/26 – P.L. 257/26 – Aut. 171/26 – Prot. Leg. 7.798/26

LEI Nº 7.016, DE 18 DE NOVEMBRO DE 2026
Dispõe sobre os procedimentos para a operacionalização das emendas individuais impositivas.

FRANKLIN DUARTE DE LIMA, Prefeito do Município de Valinhos, no uso das atribuições,

FAZ SABER que a Câmara Municipal aprovou e ele sanciona e promulga a seguinte Lei:

Art. 1º Ficam instituídos os procedimentos.
Art. 2º Esta Lei entra em vigor na data de sua publicação.

Prefeitura do Município de Valinhos,
18 de novembro de 2026, 130° do Distrito de Paz,
71° do Município e 21° da Comarca.

FRANKLIN DUARTE DE LIMA
Prefeito Municipal
"""
LEI_DA_CAMARA = """LEI Nº 6.948, DE 21 DE JULHO DE 2026.
Dispõe sobre os critérios de controle da emissão de ruídos de motocicletas.

O PRESIDENTE DA CÂMARA MUNICIPAL DE VALINHOS faz saber que a Câmara aprovou e ele promulga a seguinte Lei:

Art. 1º Fica estabelecido o limite.
Art. 2º Esta Lei entra em vigor na data de sua publicação.

Câmara Municipal de Valinhos, aos 21 de julho de 2026.
Publique-se.

Israel Scupenaro
Presidente

Jairo Ribeiro Passos
1º Secretário

José Henrique Conti
2º Secretário

Publicado no local de costume e enviado para publicação na Imprensa Oficial do Mu-
nicípio.

Geraldo Norberto Bueno
Diretor Legislativo e de Expediente em substituição
"""


def atos(texto, data="2026-11-18"):
    return base.atos_da_edicao([(1, texto)], data, perfil=v.PERFIL)


def pagina(*linhas, largura=637.8, altura=907.1):
    """Página com as linhas dadas, cada palavra lado a lado na altura indicada: (y0, texto) ou (y0, y1, texto)."""
    palavras = []
    for linha in linhas:
        y0, y1, texto = linha if len(linha) == 3 else (linha[0], linha[0] + 10, linha[1])
        palavras += [(40.0 + 45 * i, y0, 80.0 + 45 * i, y1, w) for i, w in enumerate(texto.split())]
    return (largura, altura, palavras)


class Recorte(unittest.TestCase):
    def test_lei_vai_da_epigrafe_a_assinatura_de_quem_confere_a_numeracao(self):
        (ato, recorte, motivo), (ato2, recorte2, motivo2) = atos(LEI)
        self.assertIsNone(motivo)
        self.assertEqual((ato["numero"], ato["data"]), ("7015", "2026-11-18"))
        self.assertTrue(recorte.startswith("LEI Nº 7.015"))
        self.assertTrue(recorte.rstrip().endswith("Respondendo pelo Depto. Técnico-Legislativo/SAJI"))
        self.assertNotIn("Mens. 72/26", recorte)  # a linha da mensagem abre a publicação seguinte
        self.assertNotIn("Projeto de Lei de iniciativa", recorte)
        self.assertIsNone(motivo2)
        self.assertTrue(recorte2.rstrip().endswith("Prefeito Municipal"))

    def test_lei_promulgada_pela_camara_com_a_mesa_e_a_nota_de_publicacao(self):
        (ato, recorte, motivo), = atos(LEI_DA_CAMARA, "2026-07-21")
        self.assertIsNone(motivo)
        for trecho in ("1º Secretário", "2º Secretário", "Publicado no local de costume", "Diretor Legislativo"):
            self.assertIn(trecho, recorte)

    def test_fecho_com_outra_data_retem(self):
        texto = LEI.replace("Prefeitura do Município de Valinhos,\n18 de novembro de 2026", "Prefeitura do Município de Valinhos,\n17 de novembro de 2026", 1)
        self.assertIn("data do fecho (2026-11-17)", atos(texto)[0][2])

    def test_cabecalho_corrido_dentro_do_recorte_retem(self):
        texto = LEI.replace("Art. 2º Esta Lei", "Valinhos, quarta-feira, 18 de novembro de 2026\nArt. 2º Esta Lei", 1)
        self.assertIn("rodapé da página dentro do recorte", atos(texto)[0][2])
        texto = LEI.replace("Art. 2º Esta Lei", "Atos Oficiais\nArt. 2º Esta Lei", 1)
        self.assertIn("rodapé da página dentro do recorte", atos(texto)[0][2])

    def test_citacao_dos_atos_oficiais_no_texto_nao_e_cabecalho(self):
        texto = LEI.replace("passa a vigorar com a seguinte redação.", "será publicada nos Atos Oficiais do Município.", 1)
        self.assertIsNone(atos(texto)[0][2])

    def test_nome_em_caixa_mista_sem_cargo_depois_das_assinaturas_retem(self):
        texto = LEI_DA_CAMARA + "\nMaria Aparecida Souza\n"
        texto = texto.replace("Geraldo Norberto Bueno\nDiretor Legislativo e de Expediente em substituição\n", "")
        self.assertIn("linha em maiúsculas depois das assinaturas", atos(texto, "2026-07-21")[0][2])


class Leitura(unittest.TestCase):
    CAPA = pagina((3.0, 18.1, "Assinado de forma digital por MUNICIPIO DE"), (29.0, 119.1, "ATOS OFICIAIS"),
                  (109.0, "Nº 3071 - Ano XXXVII Prefeitura Municipal de Valinhos"),
                  (110.0, "Quarta-feira, 18 de novembro de 2026"), (121.0, 130.4, "www.valinhos.sp.gov.br"),
                  (138.0, "ATOS DO EXECUTIVO"), (164.0, 163.9, "Sexta-feira, 08 de junho de 2018Valinhos,"))
    INTERNA = pagina((16.0, 35.1, "2"), (23.0, 33.5, "Atos Oficiais"), (25.0, 36.0, "Valinhos, quarta-feira, 18 de novembro de 2026"),
                     (48.0, "dores, demonstrando o quantitativo"))

    def test_identidade_no_titulo_da_primeira_pagina(self):
        self.assertEqual(v.edicao_impressa({1: self.CAPA, 2: self.INTERNA}), ("3071", "2026-11-18"))
        sem_dia = pagina((109.0, "Terça, 1 de junho de 2021 Prefeitura Municipal de Valinhos"), (110.0, "Nº 2.120 - Ano XXXII"))
        self.assertEqual(v.edicao_impressa({1: sem_dia}), ("2120", "2021-06-01"))
        self.assertEqual(v.edicao_impressa({1: pagina((300.0, "Nº 3071 - Ano XXXVII"))}), (None, None))  # fora do título

    def test_mancha_abaixo_do_titulo_e_do_cabecalho_corrido(self):
        self.assertEqual(v.mancha(1, 907.1, self.CAPA[2]), (131.4, 907.1))
        self.assertEqual(v.mancha(2, 907.1, self.INTERNA[2]), (37.0, 907.1))

    def test_texto_oculto_do_modelo_nao_conta(self):
        visiveis = v.visiveis(self.CAPA[2])
        self.assertFalse(any(w[4].startswith("Sexta-feira") for w in visiveis))
        self.assertTrue(any(w[4] == "ATOS" for w in visiveis))

    def test_leiaute_dos_atos_oficiais(self):
        self.assertIsNone(v.fora_do_leiaute({1: (637.795, 907.087, []), 2: (637.8, 907.1, [])}))
        self.assertIn("fora do leiaute conferido", v.fora_do_leiaute({1: (723.0, 842.0, [])}))  # o jornal de 2014
        self.assertIn("fora do leiaute conferido", v.fora_do_leiaute({1: (637.8, 907.1, []), 2: (842.0, 1191.0, [])}))
        self.assertEqual(v.fora_do_leiaute({}), "PDF sem páginas legíveis")


class Gravacao(unittest.TestCase):
    EDICAO = {"id": "2329", "edicao": "3071", "data": "2026-11-18", "pdf": "https://www.valinhos.sp.gov.br/uploads/x2026.pdf"}

    def test_md_tem_os_campos_da_auditoria_e_a_ementa_em_caixa_mista(self):
        (ato, recorte, _), _ = atos(LEI)
        corpo, tem_quadro = base.dom.para_md(recorte)
        md = v.montar_md(ato, self.EDICAO, corpo, tem_quadro, "a" * 64, dt.date(2026, 11, 19))
        cab = md[4:].split("\n---\n", 1)[0]
        for campo in ("titulo", "tipo", "numero", "data", "versao_texto", "fonte", "baixado_em", "municipio", "uf", "codigo_ibge"):
            self.assertRegex(cab, rf"(?m)^{campo}: \".+\"$")
        self.assertIn('municipio: "Valinhos"', cab)
        self.assertIn('codigo_ibge: "3556206"', cab)
        self.assertIn('publicacao: "Atos Oficiais do Município de Valinhos, edição nº 3071, de 18/11/2026, p. 1"', cab)
        self.assertIn('ementa: "Altera a Lei nº 6.964/2026, para autorizar a entrega de bens imóveis', cab)
        self.assertEqual(base.destino_de(ato, self.EDICAO, v.DESTINO).relative_to(base.RAIZ).as_posix(),
                         "SP/valinhos/leis-ordinarias/2026/lei-ordinaria-7015-2026-dom-3071.md")

    def test_sem_verbo_de_ementa_nao_ha_ementa(self):
        self.assertEqual(v.ementa_de("DECRETO Nº 1, DE 2 DE MAIO DE 2026\n\nFULANO, Prefeito, DECRETA:\n\n**Art. 1º** X."), "")


if __name__ == "__main__":
    unittest.main()
