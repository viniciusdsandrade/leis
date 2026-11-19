import datetime as dt
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import baixar_dom_vinhedo as vi

base = vi.base

DECRETO = """PODER EXECUTIVO
SECRETARIA MUNICIPAL DE GOVERNO

DECRETO Nº 461, DE 18 DE NOVEMBRO DE 2026.
Dispõe sobre permissão de uso das dependências da Pista Municipal de Atletismo e dá outras
providências.

DARIO PACHECO DE MORAIS, Prefeito Municipal de Vinhedo, Estado de São Paulo, usando de suas atribuições legais;

D E C R E T A:

Art. 1º Fica permitido o uso das dependências do bem público denominado Pista Municipal de Atletismo.
Art. 2.º Este Decreto entra em vigor na data de sua publicação.

Prefeitura Municipal de Vinhedo, aos dezoito dias do mês de novembro de dois mil e vinte e seis.

DARIO PACHECO DE MORAIS
Prefeito Municipal

Publicado e Registrado neste Departamento de Expediente na data supra.

DANIELE AMARAL DE OLIVEIRA
Diretora do Departamento de Expediente

SECRETARIA MUNICIPAL DE ADMINISTRAÇÃO

PORTARIA Nº 1.234, DE 18 DE NOVEMBRO DE 2026.
"""
CABECALHO = "Quarta-feira, 18 de Novembro de 2026 | ANO 11 Edição 2679 - Extra | Distribuição gratuita"
LISTA = """page   num  type   width height color comp bpc  enc interp  object ID x-ppi y-ppi size ratio
--------------------------------------------------------------------------------------------
   1     0 image    2244   262  rgb     3   8  jpeg   no        12  0   206   206 51.4K 1.0%
   2     1 image    1728  2584  rgb     3   8  jpeg   no        20  0   208   208  612K 4.6%
   3     2 image     400   300  rgb     3   8  jpeg   no        25  0   150   150 17.3K 3.9%
"""


def pagina(*linhas, largura=841.9, altura=1190.5):
    palavras = []
    for y0, texto in linhas:
        palavras += [(40.0 + 45 * i, y0, 80.0 + 45 * i, y0 + 8, w) for i, w in enumerate(texto.split())]
    return (largura, altura, palavras)


class LeituraFalsa:
    def __init__(self, paginas, em_imagem):
        self.paginas, self._em_imagem = paginas, set(em_imagem)

    def em_imagem(self, n):
        return n in self._em_imagem


class Leitura(unittest.TestCase):
    PAGINAS = {1: pagina((109.0, CABECALHO), (188.0, "Sumário"), (1151.0, "Boletim Municipal do Município de Vinhedo/SP"),
                         (1166.0, "https://www.vinhedo.sp.gov.br/diario-oficial/2758/")),
               2: pagina((109.0, CABECALHO), (142.0, "PODER EXECUTIVO"), (300.0, "DECRETO Nº 461, DE 18 DE NOVEMBRO DE 2026."),
                         (1151.0, "Boletim Municipal do Município de Vinhedo/SP"))}

    def test_identidade_no_cabecalho_da_primeira_pagina(self):
        self.assertEqual(vi.edicao_impressa(self.PAGINAS), ("2679", "2026-11-18"))
        sem_extra = {1: pagina((80.0, "Quinta-feira, 01 de Junho de 2023 | ANO 11 Edição 1190 | Distribuição gratuita"),
                               largura=595.3, altura=841.9)}
        self.assertEqual(vi.edicao_impressa(sem_extra), ("1190", "2023-06-01"))
        self.assertEqual(vi.edicao_impressa({}), (None, None))

    def test_mancha_entre_o_cabecalho_e_o_rodape(self):
        self.assertEqual(vi.mancha(1190.5, self.PAGINAS[2][2]), (118.0, 1150.0))

    def test_marcas_de_continuacao_do_documento_saem(self):
        texto = "Art. 1º Fica nomeado:\n–\nDecreto nº 460/2026 – folha 2\n–\n1– Titular: Fulano;\nDecreto nº 460/2026"
        self.assertEqual(vi.sem_folhas(texto), "Art. 1º Fica nomeado:\n1– Titular: Fulano;\nDecreto nº 460/2026")
        self.assertEqual(vi.sem_folhas("Lei Complementar n' 200/2023 -- Folha 2\nArt. 2º X."), "Lei Complementar n' 200/2023 -- Folha 2\nArt. 2º X.")

    def test_leiaute_do_boletim_gerado_pelo_sistema(self):
        self.assertIsNone(vi.fora_do_leiaute({1: (595.28, 841.89, []), 2: (841.89, 1190.55, [])}))
        self.assertIn("fora do leiaute conferido", vi.fora_do_leiaute({1: (722.835, 841.89, [])}))  # o jornal até 2021
        self.assertEqual(vi.fora_do_leiaute({}), "PDF sem páginas legíveis")

    def test_cobertura_por_imagem_pela_listagem_do_pdfimages(self):
        paginas = {1: (841.9, 1190.5, []), 2: (595.3, 841.9, []), 3: (595.3, 841.9, [])}
        cobertura = vi.cobertura_da_listagem(LISTA, paginas)
        self.assertLess(cobertura[1], 0.1)    # a faixa do cabeçalho
        self.assertGreater(cobertura[2], 0.9)  # a página do documento escaneado
        self.assertLess(cobertura[3], 0.1)    # uma foto pequena


class Recorte(unittest.TestCase):
    def test_decreto_com_fecho_por_extenso_e_nota_de_publicacao(self):
        (ato, recorte, motivo), = base.atos_da_edicao([(2, DECRETO)], "2026-11-18", perfil=vi.PERFIL)  # a portaria não é lida
        self.assertIsNone(motivo)
        self.assertEqual((ato["numero"], ato["data"]), ("461", "2026-11-18"))
        self.assertTrue(recorte.rstrip().endswith("Diretora do Departamento de Expediente"))
        self.assertNotIn("SECRETARIA MUNICIPAL DE ADMINISTRAÇÃO", recorte)

    def test_cabecalho_ou_rodape_dentro_do_recorte_retem(self):
        for intruso in (CABECALHO, "Boletim Municipal do Município de Vinhedo/SP"):
            texto = DECRETO.replace("Art. 2.º", intruso + "\nArt. 2.º", 1)
            self.assertIn("rodapé da página dentro do recorte", base.atos_da_edicao([(2, texto)], "2026-11-18", perfil=vi.PERFIL)[0][2])

    def test_ato_em_pagina_de_imagem_retem_e_paginas_sem_texto_ficam_na_edicao(self):
        ato = {"pagina": 3}
        self.assertIn("OCR da origem", vi.pagina_em_imagem(LeituraFalsa({}, [3]), ato, ""))
        self.assertIsNone(vi.pagina_em_imagem(LeituraFalsa({}, [2]), ato, ""))
        paginas = {2: pagina((109.0, CABECALHO), (1151.0, "Boletim Municipal do Município de Vinhedo/SP")),
                   3: pagina((109.0, CABECALHO), *[(200.0 + 12 * i, "texto de uma página com OCR da origem " * 3) for i in range(12)])}
        self.assertEqual(vi.paginas_sem_texto(LeituraFalsa(paginas, [2, 3])),
                         ["páginas em imagem, sem texto (2): os atos nelas não são lidos"])
        self.assertEqual(vi.paginas_sem_texto(LeituraFalsa(paginas, [])), [])


class Gravacao(unittest.TestCase):
    def test_md_do_boletim_municipal(self):
        (ato, recorte, _) = base.atos_da_edicao([(2, DECRETO)], "2026-11-18", perfil=vi.PERFIL)[0]
        corpo, tem_quadro = base.dom.para_md(recorte)
        edicao = {"id": "2758", "edicao": "2679", "data": "2026-11-18", "pdf": "https://www.vinhedo.sp.gov.br/uploads/d2026.pdf"}
        cab = vi.montar_md(ato, edicao, corpo, tem_quadro, "a" * 64, dt.date(2026, 11, 19))[4:].split("\n---\n", 1)[0]
        self.assertIn('municipio: "Vinhedo"', cab)
        self.assertIn('codigo_ibge: "3556701"', cab)
        self.assertIn('publicacao: "Boletim Municipal do Município de Vinhedo, edição nº 2679, de 18/11/2026, p. 2"', cab)
        self.assertIn('ementa: "Dispõe sobre permissão de uso das dependências da Pista Municipal de Atletismo', cab)
        self.assertEqual(base.destino_de(ato, edicao, vi.DESTINO).relative_to(base.RAIZ).as_posix(),
                         "SP/vinhedo/decretos/2026/decreto-461-2026-dom-2679.md")


if __name__ == "__main__":
    unittest.main()
