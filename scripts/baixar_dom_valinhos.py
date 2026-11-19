"""Valinhos (SP) — leis e decretos recortados dos Atos Oficiais, o Diário Oficial do Município.

Fonte: o portal da Prefeitura (`www.valinhos.sp.gov.br/portal/diario-oficial`), o mesmo sistema de Paulínia e Vinhedo
(`portal_diario_oficial.py`): listagem, dados abertos e o PDF de cada edição. O `robots.txt` veda os caminhos dos
PDFs; o mantenedor do acervo autorizou baixá-los mesmo assim (18/11/2026, confirmada em 19/11/2026), a no máximo uma
requisição a cada cinco segundos (`--apesar-do-robots`). Sem a opção, só as edições já em cache são lidas.

Leiaute lido: os Atos Oficiais compostos no InDesign, em páginas de 637,8 x 907,1 pt, com duas colunas e faixas de
largura total. A leitura por geometria é a de `baixar_dom_campinas.py`, a mesma de Paulínia: as faixas que cruzam a
calha são lidas inteiras e, entre elas, a coluna esquerda antes da direita. As edições em outro leiaute (o jornal de
notícias e atos, em A3 e depois em 723 x 842 pt) ficam fora, com o motivo.

Identidade: o número e a data do título da primeira página ("Nº 3071 - Ano XXXVII", "Quarta-feira, 18 de novembro de
2026"). O número tem de ser o da listagem; a data impressa vale mais que a de postagem.

Mancha: na primeira página, abaixo do bloco do título, que termina no endereço do portal; nas demais, abaixo do
cabeçalho corrido ("2   Atos Oficiais   Valinhos, quarta-feira, 18 de novembro de 2026"). As palavras de altura nula ou
negativa (texto oculto do modelo, como a data de outra edição atrás do título) não entram na medida; se uma delas cair
dentro de um recorte, o ato fica retido pela trava da linha corrida.

Recorte e travas: os de Paulínia (`baixar_dom_paulinia.py`), com o perfil de Valinhos: o fecho "Prefeitura do
Município de Valinhos, 18 de novembro de 2026, 130° do Distrito de Paz..." ou "Valinhos, 18 de novembro de 2026.", a
nota "Conferida, numerada e datada neste Departamento..." ou "Redigido e lavrado..." com a assinatura do diretor, que
vem em caixa mista, e a linha "Mens. 77/26 – P.L. 264/26 – ..." que abre a publicação seguinte. O que falha fica em
`municipais/SP/valinhos/_falhas.jsonl`, com o motivo.

    python3 -I scripts/baixar_dom_valinhos.py --de 2018 --ate 2026 [--listar] [--max N] [--apesar-do-robots]
    python3 -I scripts/baixar_dom_valinhos.py --despejar edicao.pdf     # texto em ordem de leitura, para conferência
"""
import argparse
import datetime as dt
import hashlib
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import baixar_dom_paulinia as base  # noqa: E402
import portal_diario_oficial as portal  # noqa: E402
from comum import CANONICO, yaml_str  # noqa: E402

PORTAL = portal.MUNICIPIOS["valinhos"]
MUNICIPIO, UF, CODIGO_IBGE, BASE = PORTAL.nome, "SP", PORTAL.codigo_ibge, PORTAL.base
DESTINO = portal.RAIZ / UF / "valinhos"
FALHAS = DESTINO / "_falhas.jsonl"
PAGINA = (637.8, 907.1)  # pt: os Atos Oficiais compostos no InDesign
PERIODICO = "Atos Oficiais"
NOTA_DOM = ("recortado da edição dos Atos Oficiais, o Diário Oficial do Município (PDF do portal da Prefeitura de "
            "Valinhos), lida coluna a coluna; não substitui a publicação oficial")
FIM_DO_TITULO = 140  # pt: o bloco do título da primeira página termina no endereço do portal, por volta de 131 pt
ALTO_DO_CABECALHO = 45  # pt: o cabeçalho corrido das páginas internas fica entre 16 e 37 pt
_MES = base._MES
_DIA = r"(?:segunda|terça|terca|quarta|quinta|sexta)(?:-feira)?|s[áa]bado|domingo"
_DATA_CORRIDA = rf"Valinhos,\s*(?:{_DIA}),\s*\d{{1,2}}\s+de\s+{_MES}\s+de\s+\d{{4}}"
# "Nº 3071 - Ano XXXVII"; no caderno dois da edição (relatórios fiscais), "Nº 3004 caderno dois - Ano XXXVII" ou, com o
# erro da fonte, "Nº 2961 Cadeno Dois - Ano XXXVII": o número é o da edição do dia, como na listagem
NUMERO_DO_TITULO = re.compile(r"\bN[º°o]\s*(\d[\d.]*)\s*(?:-?\s*Car?der?no\s+Dois\s*)?-\s*Ano\s+[IVXLC]+\b", re.I)
DATA_DO_TITULO = re.compile(rf"\b(?:{_DIA}),\s*(\d{{1,2}})\s+de\s+({_MES})\s+de\s+(\d{{4}})", re.I)
TITULO = re.compile(rf"ATOS OFICIAIS|\bAno\s+[IVXLC]+\b|Prefeitura Municipal de Valinhos|www\.valinhos|{DATA_DO_TITULO.pattern}",
                    re.I)
# a linha do cabeçalho corrido das páginas internas: só o número da página, "Atos Oficiais" e a data com o dia da semana
CABECALHO = re.compile(rf"(?:\s*(?:\d{{1,3}}|Atos Oficiais|{_DATA_CORRIDA}))+\s*", re.I)
# o mesmo cabeçalho dentro de um recorte ou do fluxo do PDF: a linha "Atos Oficiais" sozinha ou a data corrida
CORRIDO = re.compile(rf"^\s*(?:\d{{1,3}}\s+)?Atos Oficiais\s*$|{_DATA_CORRIDA}", re.I)

PERFIL = base.Perfil(
    # nome de quem assina: em maiúsculas, como o Prefeito, ou em caixa mista, como o diretor que confere a numeração
    nome=re.compile(r"[A-ZÀ-Ú][A-ZÀ-Ú'.]*(?:[ \t]+[A-ZÀ-Ú][A-ZÀ-Ú'.]*){1,8}|"
                    r"[A-ZÀ-Ú][a-zà-ú'.]+(?:[ \t]+(?:d[aeo]s?|e|[A-ZÀ-Ú][a-zà-ú'.]*)){1,8}"),
    nao_e_assinatura=re.compile(base.NAO_E_ASSINATURA.pattern.replace("PAUL[ÍI]NIA", "VALINHOS"), re.I),
    # os cargos de Paulínia, mais o "Subchefe do Gabinete" e os secretários da Mesa da Câmara ("1º Secretário")
    cargo=re.compile(r"(?:\d{1,2}[º°ª][ \t]+)?" + base.CARGO.pattern.replace("|Chefe|", "|Chefe|Subchefe|"), re.I),
    nota=re.compile(r"(?:[A-Za-zÀ-ú]+[ \t,]+){0,2}(?:lavrad|elaborad|publicad|registrad|conferid|redigid)[oa]\b", re.I),
    signatario=re.compile(base.SIGNATARIO.pattern.replace("Paul[íi]nia", "Valinhos"), re.M | re.I),
    # "Prefeitura do Município de Valinhos," e a data na linha seguinte, ou "Valinhos, 18 de novembro de 2026."
    fecho=re.compile(rf"Valinhos[ \t]*,\s*(?:aos[ \t]+)?(\d{{1,2}})[ \t]*[º°o]?[ \t]+de[ \t]+({_MES})[ \t]+de[ \t]+(\d\.?\d{{3}})",
                     re.I),
    # além dos cabeçalhos de Paulínia: a linha da mensagem e do projeto que antecede a epígrafe e os títulos de seção
    limite=re.compile(base.LIMITE.pattern + r"|^[ \t]*Mens\.[ \t]*\d"
                      r"|^[ \t]*(?:LEIS|DECRETOS|PORTARIAS|EDITAIS|RESOLU[ÇC][ÕO]ES|ATOS[ \t][^\n]*)[ \t]*$", re.M),
    apenso=re.compile(base.APENSO.pattern.replace("PAUL[ÍI]NIA", "VALINHOS"), re.I),
    corrido=CORRIDO,
)
# ------------------------------------------------------------------------------------------ leitura da edição
def visiveis(palavras):
    """As palavras de altura positiva: o modelo das edições guarda texto oculto (yMax menor que yMin)."""
    return [p for p in palavras if p[3] > p[1]]


def fora_do_leiaute(paginas):
    """Motivo quando alguma página não é do leiaute dos Atos Oficiais; None quando todas são."""
    if not paginas:
        return "PDF sem páginas legíveis"
    for n, (largura, altura, _) in sorted(paginas.items()):
        if abs(largura - PAGINA[0]) > 3 or abs(altura - PAGINA[1]) > 3:
            return f"página {n} de {largura:.0f} x {altura:.0f} pt, fora do leiaute conferido (Atos Oficiais, 638 x 907 pt)"
    return None


def edicao_impressa(paginas):
    """(número, data ISO) que o título da primeira página imprime; (None, None) sem número, e data None sem data."""
    if not paginas:
        return None, None
    _, _, palavras = paginas[min(paginas)]
    numero = data = None
    for y0, _, texto in base.linhas_da_pagina(visiveis(palavras)):
        if y0 > FIM_DO_TITULO:
            break
        m = NUMERO_DO_TITULO.search(texto)
        if m and not numero:
            numero = m.group(1).replace(".", "")
        d = DATA_DO_TITULO.search(texto)
        if d and not data:
            data = base.data_iso(*d.groups())
    return numero, data


def mancha(n, altura, palavras):
    """(topo, base) da área de texto da página: abaixo do bloco do título (primeira) ou do cabeçalho corrido."""
    linhas = base.linhas_da_pagina(visiveis(palavras))
    if n == 1:
        alto = [y1 for y0, y1, texto in linhas if y0 < FIM_DO_TITULO and TITULO.search(texto)]
    else:
        alto = [y1 for y0, y1, texto in linhas if y0 < ALTO_DO_CABECALHO and CABECALHO.fullmatch(texto)]
    return (max(alto) + 1 if alto else float(base.TOPO)), altura


class Edicao(base.Edicao):
    """Uma edição dos Atos Oficiais: as palavras de todas as páginas, o texto de cada página em ordem de leitura,
    região por região, e o fluxo do PDF (sem o cabeçalho corrido) para a conferência."""

    def __init__(self, pdf):
        self.pdf = pdf
        self.paginas = base.palavras_da_edicao(pdf)
        self.jornal = False
        self._fluxo = None

    def fluxo(self):
        if self._fluxo is None:
            bruto = subprocess.run(["pdftotext", "-q", "-raw", "-enc", "UTF-8", str(self.pdf), "-"], capture_output=True,
                                   timeout=900).stdout
            linhas = bruto.decode("utf-8", "replace").replace("\f", "\n").split("\n")
            self._fluxo = base.so_letras("\n".join(ln for ln in linhas if not CORRIDO.search(ln)))
        return self._fluxo

    def trechos(self):
        saida = []
        for n, (largura, altura, palavras) in sorted(self.paginas.items()):
            topo, fundo = mancha(n, altura, palavras)
            caixas = [p[:4] for p in visiveis(palavras) if p[1] >= topo]
            for regiao in base.dom.zonas_da_pagina(largura, altura, caixas, topo, fundo):
                texto = base.dom.texto_da_regiao(self.pdf, n, *regiao).rstrip()
                if texto.strip():
                    saida.append((n, texto))
        return saida


# ------------------------------------------------------------------------------------------ gravação
def montar_md(ato, edicao, corpo, tem_quadro, sha_pdf, hoje):
    _, tipo = CANONICO[ato["chave"]]
    titulo = base.titulo_de(ato)
    notas = [NOTA_DOM] + ([base.dom.NOTA_QUADRO] if tem_quadro else [])
    dia = dt.date.fromisoformat(edicao["data"]).strftime("%d/%m/%Y")
    meta = [("titulo", titulo), ("tipo", tipo), ("tipo_na_fonte", ato["tipo_na_fonte"]), ("numero", ato["numero"]),
            ("data", ato["data"]), ("municipio", MUNICIPIO), ("uf", UF), ("codigo_ibge", CODIGO_IBGE)]
    ementa = base.ementa_de(corpo, caixa_mista=True)
    if ementa:
        meta.append(("ementa", ementa))
    meta += [("versao_texto", "texto original (não consolidado); " + "; ".join(notas)),
             ("publicacao", f"{PERIODICO} do Município de {MUNICIPIO}, edição nº {edicao['edicao']}, de {dia}, p. {ato['pagina']}"),
             ("data_publicacao", edicao["data"]),
             ("fonte", f"{BASE}/portal/diario-oficial/ver/{edicao['id']}"),
             ("fonte_texto", edicao["pdf"]),
             ("sha256_fonte", sha_pdf),
             ("sha256_texto", hashlib.sha256(corpo.encode("utf-8")).hexdigest()),
             ("baixado_em", hoje.isoformat())]
    return "---\n" + "\n".join(f"{k}: {yaml_str(v)}" for k, v in meta) + f"\n---\n\n# {titulo}\n\n{corpo}\n"


# ------------------------------------------------------------------------------------------ execução
VALINHOS = base.Diario(portal=PORTAL, destino=DESTINO, falhas=FALHAS, edicao=Edicao, fora_do_leiaute=fora_do_leiaute,
                       edicao_impressa=edicao_impressa, perfil=PERFIL, montar_md=montar_md)


def executar(de, ate, maximo=0, listar=False, rps=0.5, apesar_do_robots=False):
    """O fluxo comum aos Diários do portal (`baixar_dom_paulinia.executar_diario`) com a leitura de Valinhos."""
    return base.executar_diario(VALINHOS, de, ate, maximo, listar, rps, apesar_do_robots)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--de", type=int, help="primeiro ano")
    ap.add_argument("--ate", type=int, help="último ano, inclusive")
    ap.add_argument("--max", type=int, default=0, help="limita novas conversões; 0 = sem limite")
    ap.add_argument("--listar", action="store_true", help="só confere a listagem contra os dados abertos; não baixa PDFs")
    ap.add_argument("--rps", type=float, default=0.5, help="requisições por segundo")
    ap.add_argument("--apesar-do-robots", action="store_true",
                    help="baixa os PDFs mesmo com o robots.txt vedando o download (autorização de 18/11/2026)")
    ap.add_argument("--despejar", type=Path, help="mostra o texto de uma edição em ordem de leitura e sai")
    a = ap.parse_args()
    if a.despejar:
        for pagina, texto in Edicao(a.despejar).trechos():
            print(f"\n=== página {pagina}\n{texto}")
    elif a.de and a.ate:
        executar(a.de, a.ate, a.max, a.listar, a.rps, a.apesar_do_robots)
    else:
        ap.error("informe --de e --ate, ou --despejar")
