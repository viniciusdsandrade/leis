"""Paulínia (SP) — leis e decretos recortados das edições do Diário Oficial do Município.

Fonte: o portal da Prefeitura (`www.paulinia.sp.gov.br/portal/diario-oficial`), que publica as edições em PDF nascido
digital e lista todas em dados abertos (`/portal/dados-abertos/diario-oficial/<ano>`). É a publicação oficial dos atos,
com as leis e os decretos do Executivo. O `robots.txt` libera a listagem, mas em novembro de 2026 traz um segundo grupo
`User-agent: *` que veda `/portal/download/` e `/uploads/`, os caminhos dos PDFs: o coletor lê o `robots.txt` a cada
execução, somando os grupos do mesmo agente (RFC 9309), e, com o download vedado, só lê as edições já em cache.

As outras duas rotas de Paulínia não entram, e o motivo fica registrado para quem tentar: o sistema legislativo da
Câmara (`paulinia.siscam.com.br`) só admite no `robots.txt` os buscadores que nomeia e entrega as leis como PDF
digitalizado; o portal de textos compilados (`legislacaodigital.com.br`) responde 403 com desafio do Cloudflare a
clientes automáticos.

Leitura: a edição tem duas colunas, com faixas de largura total (quadros, cabeçalho da primeira página). Vale a
leitura pela geometria de `baixar_dom_campinas.py`: faixas que cruzam a calha são lidas inteiras e, entre elas, a
coluna esquerda antes da direita. A mancha de cada página é medida nas próprias palavras: na primeira, entre a linha
do título ("Diário Oficial - Ano ... - Edição ...") e o expediente; nas demais, acima do rodapé corrido.

Recorte: da epígrafe ("LEI Nº 4.797, DE 13 DE NOVEMBRO DE 2026") ao bloco de assinaturas que segue o fecho
("Paulínia, 13 de novembro de 2026"). Travas: epígrafe única na edição, fórmula de promulgação e artigo presentes,
data do fecho igual à da epígrafe, assinatura do Prefeito, artigos em sequência, nenhum trecho de outra publicação
intercalado, anexo depois das assinaturas retido. Por fim, a leitura por colunas é confrontada com a ordem do fluxo do
próprio PDF (`pdftotext -raw`): parágrafo que não aparece inteiro nas duas leituras retém o ato (quadro lido como
prosa, coluna fora de ordem). O número da edição impresso no PDF tem de ser o da edição pedida. O que falha fica em
`municipais/SP/paulinia/_falhas.jsonl`, com o motivo.

    python3 -I scripts/baixar_dom_paulinia.py --de 2026 --ate 2026 [--listar] [--max N] [--rps 0.5]
    python3 -I scripts/baixar_dom_paulinia.py --despejar edicao.pdf     # texto em ordem de leitura, para conferência
    python3 -I scripts/baixar_dom_paulinia.py --lei-organica            # texto compilado que a Câmara publica em PDF

A Lei Orgânica vem do site da própria Câmara (`camarapaulinia.sp.gov.br`, PDF gerado no Word, com texto), na versão
compilada que o arquivo declara ("Atualizada até a Emenda nº ...").
"""
import argparse
import datetime as dt
import hashlib
import html
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import baixar_dom_campinas as dom  # noqa: E402
from comum import CANONICO, Rede, documento_para_md, slugify, yaml_str  # noqa: E402

MUNICIPIO, UF, CODIGO_IBGE = "Paulínia", "SP", "3536505"
BASE = "https://www.paulinia.sp.gov.br"
RAIZ = Path(__file__).resolve().parent.parent / "municipais"
DESTINO = RAIZ / UF / "paulinia"
CACHE = RAIZ / "_indice" / "dom-paulinia"
FONTE = RAIZ / "_fonte" / "dom-paulinia"
FALHAS = DESTINO / "_falhas.jsonl"
LEI_ORGANICA_PDF = "https://www.camarapaulinia.sp.gov.br/wp-content/uploads/2023/11/Lei-Organica.pdf"
TOPO = 15  # pt: as páginas internas não têm cabeçalho corrido; o texto começa perto da borda
TAMANHO_MAXIMO = 150_000
NOTA_DOM = ("recortado da edição do Diário Oficial do Município (PDF do portal da Prefeitura de Paulínia), lida coluna a "
            "coluna; não substitui a publicação oficial")
MESES = {"janeiro": 1, "fevereiro": 2, "marco": 3, "março": 3, "abril": 4, "maio": 5, "junho": 6, "julho": 7,
         "agosto": 8, "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12}
NOME_MES = ["", "janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro",
            "novembro", "dezembro"]
_MES = r"(?:janeiro|fevereiro|mar[çc]o|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)"
# rótulo da epígrafe -> (chave de comum.CANONICO, tipo como a fonte escreve)
TIPOS = {"LEI COMPLEMENTAR": ("lei complementar", "Lei Complementar"), "LEI": ("lei ordinaria", "Lei"),
         "DECRETO": ("decreto", "Decreto"), "DECRETO LEGISLATIVO": ("decreto legislativo", "Decreto Legislativo"),
         "EMENDA À LEI ORGÂNICA": ("emenda a lei organica", "Emenda à Lei Orgânica")}


# ------------------------------------------------------------------------------------------ geometria da edição
def palavras_da_edicao(pdf, ate=None):
    """{página: (largura, altura, [(x0, y0, x1, y1, palavra)])}, numa só chamada do `pdftotext -bbox`; com `ate`, só
    as primeiras páginas."""
    limite = ["-l", str(ate)] if ate else []
    saida = subprocess.run(["pdftotext", "-q", "-bbox", *limite, str(pdf), "-"], capture_output=True, timeout=900).stdout
    saida = saida.decode("utf-8", "replace")
    paginas = {}
    for n, m in enumerate(re.finditer(r'<page width="([\d.]+)" height="([\d.]+)">(.*?)</page>', saida, re.S), 1):
        achadas = re.findall(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</word>', m.group(3))
        paginas[n] = (float(m.group(1)), float(m.group(2)),
                      [(float(a), float(b), float(c), float(d), html.unescape(w)) for a, b, c, d, w in achadas])
    return paginas


def linhas_da_pagina(palavras):
    """[(y do topo, y da base, texto)] das linhas da página: palavras de mesma altura, da esquerda para a direita."""
    grupos = {}
    for x0, y0, _, y1, w in palavras:
        grupos.setdefault(round(y0), []).append((x0, y1, w))
    return [(float(y), max(p[1] for p in ps), " ".join(p[2] for p in sorted(ps))) for y, ps in sorted(grupos.items())]


# o nome do periódico: "Semanário Oficial" até 2020 (e ainda no rodapé de edições de 2021 e 2022), depois "Diário
# Oficial"; com "EXTRA" nas edições extras e, em 2017, com a ligadura partida ("Oﬁ cial", "Ofi cial")
_OFICIAL = r"(?:Di[áa]rio|Seman[áa]rio)[ \t]+O(?:fi|ﬁ)[ \t]?cial(?:[ \t]+EXTRA)?"
TITULO_EDICAO = re.compile(rf"{_OFICIAL}[ \t]*-[ \t]*Ano[ \t]+[IVXLC]+[ \t]*-[ \t]*Edi[çc][ãa]o", re.I)
# a linha corrida do pé da página: "Semanário Oficial | | Edição 1.175 | Paulínia, 24 de fevereiro de 2016 | 2"; em
# 2015 sem a palavra "Edição" ("Semanário Oficial | | 1118 | Paulínia, 11 de março de 2015 2")
_RODAPE = rf"{_OFICIAL}[ \t]*\|[^\n]*(?:Edi[çc][ãa]o|Paul[íi]nia,)"
RODAPE = re.compile(_RODAPE, re.I)


# o formato de jornal (2012 a agosto de 2013): página dupla, quatro colunas por página, e o rodapé "Paulínia, 27 de
# fevereiro de 2013 Semanário Oficial - Edição 998" (em espelho na página da direita)
RODAPE_DE_JORNAL = re.compile(rf"Seman[áa]rio[ \t]*Oficial[ \t]*-[ \t]*Edi[çc][ãa]o[ \t]*(\d[\d.]*)", re.I)
DATA_DO_RODAPE_DE_JORNAL = re.compile(rf"Paul[íi]nia,[ \t]*(\d{{1,2}})[ \t]+de[ \t]+({_MES})[ \t]+de[ \t]+(\d{{4}})", re.I)
JORNAL = "jornal"
NUMERO_DA_EDICAO = re.compile(rf"Edi[çc][ãa]o\s+(\d[\d.]*)\s*(?:-\s*EXTRA\s*)?(?:[-|]\s*(?:Paul[íi]nia,\s*)?(\d{{1,2}})\s+de\s+({_MES})\s+de\s+(\d{{4}}))?", re.I)


def edicao_impressa(paginas):
    """(número, data ISO ou None) que a própria edição imprime no título da primeira página ou no rodapé corrido;
    (None, None) quando nenhuma linha traz o número. Confere que o PDF baixado é o da edição pedida."""
    for _, (_, altura, palavras) in sorted(paginas.items()):
        for y0, _, texto in linhas_da_pagina(palavras):
            if TITULO_EDICAO.search(texto) or RODAPE.search(texto):
                m = NUMERO_DA_EDICAO.search(texto)
                if m:
                    data = data_iso(m.group(2), m.group(3), m.group(4)) if m.group(2) else None
                    return m.group(1).replace(".", ""), data
            jornal = RODAPE_DE_JORNAL.search(texto) if y0 > altura * 0.9 else None
            if jornal:
                data = DATA_DO_RODAPE_DE_JORNAL.search(texto)
                return jornal.group(1).replace(".", ""), data_iso(*data.groups()) if data else None
    return None, None


def periodico(paginas):
    """Nome que a edição dá a si mesma, "Semanário Oficial" (até 2020) ou "Diário Oficial": o do título da primeira
    página; sem título em texto, o do rodapé."""
    for criterio in (TITULO_EDICAO, RODAPE, RODAPE_DE_JORNAL):
        for _, (_, _, palavras) in sorted(paginas.items()):
            for _, _, texto in linhas_da_pagina(palavras):
                m = criterio.search(texto)
                if m:
                    return "Semanário Oficial" if m.group(0)[:1] in "Ss" else "Diário Oficial"
    return "Diário Oficial"


def mancha_de_jornal(altura, palavras):
    """(topo, base) no formato de jornal: acima do rodapé, do número da página e do nome da cidade."""
    base = altura
    linhas = linhas_da_pagina(palavras)
    for y0, _, texto in linhas:
        if y0 > altura * 0.9 and RODAPE_DE_JORNAL.search(texto):
            base = min(base, y0 - 1)
    for y0, y1, _ in linhas:
        if y0 > altura * 0.9 and y0 <= base < y1:
            base = y0 - 1
    return float(TOPO), base


def colunas_de_jornal(palavras, topo, base, calha=5.0):
    """[(x0, topo, x1, base)] das regiões de leitura da página, coluna por coluna, da esquerda para a direita e de cima
    para baixo. As colunas são os intervalos ocupados por palavras do corpo do texto, separados por faixas verticais
    vazias de pelo menos `calha` pt; as palavras em corpo maior (títulos de seção, mais de 1,35 vez a altura mais comum)
    não entram na medida. O título que cruza a calha entre colunas fica fora da leitura: as colunas que ele atravessa
    se dividem acima e abaixo dele. A ordem entre as partes de colunas vizinhas a conferência com o fluxo do PDF julga."""
    dentro = [p for p in palavras if p[1] >= topo and p[3] <= base]
    if not dentro:
        return []
    alturas = {}
    for _, y0, _, y1, _ in dentro:
        alturas[round(y1 - y0, 1)] = alturas.get(round(y1 - y0, 1), 0) + 1
    corpo = max(alturas, key=alturas.get)
    grandes = [p for p in dentro if p[3] - p[1] > corpo * 1.35]
    colunas = []
    for x0, x1 in sorted((p[0], p[2]) for p in dentro if p[3] - p[1] <= corpo * 1.35):
        if colunas and x0 - colunas[-1][1] < calha:
            colunas[-1][1] = max(colunas[-1][1], x1)
        else:
            colunas.append([x0, x1])
    # as linhas de título (palavras grandes na mesma altura) que cruzam alguma calha
    linhas = {}
    for p in grandes:
        linhas.setdefault(round(p[1]), []).append(p)
    cortes = []
    for ps in linhas.values():
        x0, x1 = min(p[0] for p in ps), max(p[2] for p in ps)
        tocadas = [i for i, (c0, c1) in enumerate(colunas) if c0 < x1 and x0 < c1]
        if len(tocadas) > 1:
            cortes.append((min(p[1] for p in ps) - 1, max(p[3] for p in ps) + 1, set(tocadas)))
    regioes = []
    for i, (x0, x1) in enumerate(colunas):
        faixas = sorted((a, b) for a, b, tocadas in cortes if i in tocadas)
        y = topo
        for a, b in faixas:
            if a > y:
                regioes.append((x0, y, x1, a))
            y = max(y, b)
        if base > y:
            regioes.append((x0, y, x1, base))
    return regioes


def mancha(altura, palavras):
    """(topo, base) da área de texto da página, medida nas palavras: abaixo da linha do título da edição (primeira
    página) e acima do expediente ou do rodapé corrido."""
    topo, base = float(TOPO), altura
    linhas = linhas_da_pagina(palavras)
    for y0, y1, texto in linhas:
        if y0 < altura * 0.35 and TITULO_EDICAO.search(texto):
            topo = max(topo, y1 + 1)
        elif y0 > altura * 0.6 and (RODAPE.search(texto) or texto.lstrip().startswith("Expediente:")):
            base = min(base, y0 - 1)
    # o número da página e o nome da cidade, compostos na mesma faixa do rodapé mas alguns pontos acima dele
    for y0, y1, _ in linhas:
        if y0 > altura * 0.9 and y0 <= base < y1:
            base = y0 - 1
    return topo, base


# carimbo da assinatura digital da edição, sobreposto à última coluna: "Assinado de forma digital por MUNICIPIO DE
# PAULINIA:45751435000106 Dados: 2026.02.24 17:44:12 -03'00'", partido em linhas curtas à direita do texto
PALAVRA_DO_CARIMBO = re.compile(r"Assinado|de|forma|digital|por|MUNICIPIO|DE|PAULINIA:\d+|\d{5,}|Dados:|\d{4}\.\d{2}\.\d{2}|"
                                r"\d{2}:\d{2}:\d{2}|-\d{2}'\d{2}'")


def sem_carimbo(texto):
    """Tira o carimbo da assinatura digital: a partir da linha que termina em "Assinado de" (ou "Assinado de forma
    digital"), o segmento final de cada linha, depois de um vão de espaços, formado só por palavras do carimbo."""
    saida, restam = [], 0
    for linha in texto.split("\n"):
        partes = re.split(r"[ \t]{3,}", linha.rstrip())
        segmento = partes[-1].strip()
        carimbo = bool(segmento) and all(PALAVRA_DO_CARIMBO.fullmatch(w) for w in segmento.split())
        if carimbo and segmento.startswith("Assinado"):
            restam = 10
        if restam and carimbo:
            linha = linha.rstrip()[:len(linha.rstrip()) - len(partes[-1])].rstrip()
            restam = 0 if re.search(r"-\d{2}'\d{2}'$", segmento) else restam - 1
        elif restam and segmento:
            restam -= 1
        saida.append(linha)
    return "\n".join(saida)


def so_letras(texto):
    return re.sub(r"[^0-9a-zà-ú]", "", texto.lower())


def fluxo_do_pdf(pdf, jornal=False):
    """Letras e dígitos da edição na ordem do fluxo do PDF (`pdftotext -raw`), sem o rodapé corrido e o expediente:
    uma segunda leitura, independente da geometria, para confrontar com o recorte."""
    bruto = subprocess.run(["pdftotext", "-q", "-raw", "-enc", "UTF-8", str(pdf), "-"], capture_output=True, timeout=900).stdout
    texto = re.sub(_RODAPE + r"[^\n]*", "", bruto.decode("utf-8", "replace").replace("\f", "\n"), flags=re.I)
    if jornal:  # "7 6 7 SemanárioOficial Paulínia, 27 defevereirode2013 -Edição998 PAULÍNIA Semanário Oficial ..."
        texto = "\n".join(ln for ln in texto.split("\n")
                          if not (re.search(r"Seman[áa]rio[ \t]*Oficial", ln, re.I) and re.search(r"Edi[çc][ãa]o[ \t]*\d", ln, re.I)))
    return so_letras("\n".join(ln for ln in texto.split("\n") if not ln.startswith("Expediente:")))


def diverge_do_fluxo(corpo, fluxo):
    """Motivo quando algum parágrafo de prosa do corpo não existe, com as mesmas letras e dígitos em sequência, no
    fluxo do PDF. Quadros (blocos pré-formatados) ficam de fora: neles vale o alinhamento, não a ordem de leitura."""
    prosa = re.sub(r"```text\n.*?\n```", "", corpo, flags=re.S)
    ausentes = []
    for paragrafo in prosa.split("\n\n"):
        letras = _letras_do_paragrafo(paragrafo)
        if len(letras) >= 8 and letras not in fluxo:
            ausentes.append(" ".join(paragrafo.split())[:60])
    if ausentes:
        return (f"leitura por colunas difere do fluxo do PDF em {len(ausentes)} parágrafo(s), a começar por "
                f"\"{ausentes[0]}\"; conferir quadro lido como prosa ou ordem das colunas")
    return None


class Edicao:
    """Uma edição do Diário: as palavras de todas as páginas (uma leitura), o texto de cada página em ordem de
    leitura, região por região, e o fluxo do PDF para a conferência."""

    def __init__(self, pdf):
        self.pdf = pdf
        self.paginas = palavras_da_edicao(pdf)
        self.jornal = leiaute(self.paginas) == JORNAL
        self._fluxo = None

    def fluxo(self):
        if self._fluxo is None:
            self._fluxo = fluxo_do_pdf(self.pdf, self.jornal)
        return self._fluxo

    def trechos(self):
        """[(página, texto)] da edição inteira."""
        saida = []
        for n, (largura, altura, palavras) in sorted(self.paginas.items()):
            if self.jornal:
                topo, base = mancha_de_jornal(altura, palavras)
                for x0, y0, x1, y1 in colunas_de_jornal(palavras, topo, base):
                    texto = dom.texto_da_regiao(self.pdf, n, x0 - 2, y0, x1 - x0 + 4, y1 - y0).rstrip()
                    if texto.strip():
                        saida.append((n, texto))
                continue
            topo, base = mancha(altura, palavras)
            caixas = [p[:4] for p in palavras if p[1] >= topo]
            for regiao in dom.zonas_da_pagina(largura, altura, caixas, topo, base):
                texto = sem_carimbo(dom.texto_da_regiao(self.pdf, n, *regiao)).rstrip()
                if texto.strip():
                    saida.append((n, texto))
        return saida


# ------------------------------------------------------------------------------------------ recorte dos atos
# a epígrafe em linha própria. Em maiúsculas na maior parte das edições; em versalete ou caixa mista em outras ("Lei nº
# 3691, de 12 de JULHO DE 2019", "DECRETO Nº 7.431 de 10 DE JANEIRO DE 2.019."), por isso sem distinção de caixa
_EPIGRAFE = (r"^[ \t]*(LEI COMPLEMENTAR|LEI|DECRETO LEGISLATIVO|DECRETO|EMENDA À LEI ORGÂNICA)[ \t]+N[º°o.]*[ \t]*(\d[\d.]*)[ \t]*,?[ \t]*DE[ \t]+(\d{1,2})[ \t]*[º°o]?"
             rf"[ \t]+DE[ \t]+((?i:{_MES}))[ \t]+DE[ \t]+(\d\.?\d{{3}})[ \t]*\.?[ \t]*$")
EPIGRAFE = re.compile(_EPIGRAFE, re.M | re.I)
EPIGRAFE_EM_MAIUSCULAS = re.compile(_EPIGRAFE, re.M)
# no formato de jornal a coluna é estreita e a epígrafe quebra a linha ("DECRETO Nº 6.433," / "DE 25 DE FEVEREIRO DE
# 2013."): ali cada espaço interno da epígrafe pode ser também uma quebra de linha (nunca uma linha em branco); as
# pontas continuam presas ao começo e ao fim de linha
_ESPACO_OU_QUEBRA = {"+": r"(?:[ \t]*\n[ \t]*|[ \t]+)", "*": r"[ \t]*(?:\n[ \t]*)?"}
_EPIGRAFE_DE_JORNAL = (r"^[ \t]*" + re.sub(r"\[ \\t\]([+*])", lambda m: _ESPACO_OU_QUEBRA[m.group(1)],
                                           _EPIGRAFE[len(r"^[ \t]*"):-len(r"[ \t]*\.?[ \t]*$")])
                       + r"[ \t]*\.?[ \t]*$")
EPIGRAFE_DE_JORNAL = re.compile(_EPIGRAFE_DE_JORNAL, re.M | re.I)
EPIGRAFE_DE_JORNAL_EM_MAIUSCULAS = re.compile(_EPIGRAFE_DE_JORNAL, re.M)
# onde outra publicação começa: epígrafe de outro ato, título de aviso ou cabeçalho de órgão, sempre em maiúsculas
LIMITE = re.compile(
    r"^[ \t]*(?:(?:LEI COMPLEMENTAR|LEI|DECRETO LEGISLATIVO|DECRETO|PORTARIA|RESOLU[ÇC][ÃA]O|EMENDA|ATO|INSTRU[ÇC][ÃA]O)[ \t]+"
    r"(?:[A-ZÀ-Ú]+[ \t]+){0,4}N[º°o.]|SECRETARIA\b|GABINETE\b|C[ÂA]MARA MUNICIPAL\b|PROCURADORIA\b|EDITAL\b|EXTRATO\b|"
    r"AVISO\b|PREG[ÃA]O\b|CONCORR[ÊE]NCIA\b|COMUNICADO\b|ERRATA\b|RETIFICA[ÇC][ÃA]O\b|CONVOCA[ÇC][ÃA]O\b|"
    r"PAUL[ÍI]NIA PREVI\b|INSTITUTO\b|CONSELHO\b)", re.M)
# o primeiro artigo do ato; "Art. 43, § 1º ... da Lei 4.320" no começo de uma linha do preâmbulo não é
ARTIGO = re.compile(r"^[ \t]*(?:Art\.?|ART\.?|ARTIGO|Artigo)[ \t]*(?:1[ \t]*[ºo°]|1\.|[Úú]nico|ÚNICO)", re.M)
SIGNATARIO = re.compile(
    r"^[ \t]*(?:(?:Vice-)?Prefeit[oa](?:[ \t]+Municipal)?(?:[ \t]+d[eo][ \t]+(?:Munic[íi]pio(?:[ \t]+de[ \t]+Paul[íi]nia)?|Paul[íi]nia))?"
    r"(?:[ \t]+em[ \t]+exerc[íi]cio)?|Presidente(?:[ \t]+da[ \t]+C[âa]mara(?:[ \t]+Municipal)?)?)[ \t.]*$", re.M | re.I)
NAO_E_ASSINATURA = re.compile(
    r"(?:SECRETARIA|GABINETE|COORDENADORIA|DEPARTAMENTO|ATOS?|EXPEDIENTE|FUNDA[ÇC][ÃA]O|EMPRESA|INSTITUTO|CONSELHO|"
    r"COMISS[ÃA]O|AUTARQUIA|SERVI[ÇC]O|DECRETO|LEI|PORTARIA|RESOLU[ÇC][ÃA]O|C[ÂA]MARA|PROCURADORIA|PREG[ÃA]O|"
    r"CONCORR[ÊE]NCIA|EDITAL|EXTRATO|AVISO|ANEXO|PAUL[ÍI]NIA|PREFEITURA|TOMADA|CHAMAMENTO|DISPENSA|CONVOCA[ÇC][ÃA]O|"
    r"COMUNICADO|ERRATA|ATA|TABELA|QUADRO|TOTAL|ORDEM|PAUTA|RESUMO|TERMO|RELAT[ÓO]RIO)\b")
NOME = re.compile(r"[A-ZÀ-Ú][A-ZÀ-Ú'.]*(?:[ \t]+[A-ZÀ-Ú][A-ZÀ-Ú'.]*){1,8}")
# cargo de quem assina; "Secretária" sim, "Secretaria" (o órgão) não
CARGO = re.compile(r"(?:Vice-)?(?:Prefeit[oa]|Secret(?:ári[oa]|ario)|Subsecret(?:ári[oa]|ario)|Procurador|Diretor|Chefe|Presidente|"
                   r"Respondendo|Superintendente|Controlador|Coordenador|Vereador|Comandante|Assessor|Gestor|Ouvidor|"
                   r"Corregedor)[^\n]{0,90}(?<![:;,])", re.I)
# nota de lavratura e publicação que fecha o ato: "Lavrado e publicado no Gabinete do Prefeito, na data supra.",
# "Decreto elaborado no Departamento de Orçamentos ... e publicado no Gabinete do Prefeito na data supra."
NOTA = re.compile(r"(?:[A-Za-zÀ-ú]+[ \t]+){0,2}(?:lavrad|elaborad|publicad|registrad)[oa]\b", re.I)
FECHO = re.compile(rf"(?:Paul[íi]nia|Pr[ée]dio[ \t]+Ulysses[ \t]+Guimar[ãa]es)[ \t]*,[ \t]*(?:aos[ \t]+)?(\d{{1,2}})[ \t]*[º°o]?[ \t]+de[ \t]+"
                   rf"({_MES})[ \t]+de[ \t]+(\d\.?\d{{3}})", re.I)
# no jornal o fecho é o do Palácio e a data pode quebrar a linha ("Palácio 28 de Fevereiro, 24 de abril de" / "2013")
FECHO_DE_JORNAL = re.compile(rf"(?:Paul[íi]nia|Pr[ée]dio\s+Ulysses\s+Guimar[ãa]es|Pal[áa]cio\s+28\s+de\s+Fevereiro)\s*,\s*(?:aos\s+)?"
                             rf"(\d{{1,2}})[ \t]*[º°o]?\s+de\s+({_MES})\s+de\s+(\d\.?\d{{3}})", re.I)
FORMULA = {"lei ordinaria": re.compile(r"SANCION|PROMULG", re.I), "lei complementar": re.compile(r"SANCION|PROMULG", re.I),
           "decreto": re.compile(r"D[ \t]?E[ \t]?C[ \t]?R[ \t]?E[ \t]?T[ \t]?A"), "decreto legislativo": re.compile(r"PROMULG", re.I),
           "emenda a lei organica": re.compile(r"PROMULG", re.I)}
INTERCALADO = re.compile(
    r"^[ \t]*(?:PORTARIA[ \t]+N|EXTRATO[ \t]+D|EDITAL[ \t]+D|AVISO[ \t]+D|PREG[ÃA]O[ \t]|CONCORR[ÊE]NCIA[ \t]|COMUNICADO\b|"
    r"ERRATA\b|RETIFICA[ÇC][ÃA]O\b|Processo[ \t]+Administrativo[ \t]*:|Interessad[oa][ \t]*:|Objeto[ \t]*:)", re.M)
ANEXO = re.compile(r"^[ \t]*ANEXO\b", re.M)
APENSO = re.compile(r"[ \t]*(?:ANEXO|TABELA|QUADRO|DEMONSTRATIVO|RELA[ÇC][ÃA]O|MEMORIAL|PLANTA|PLANILHA|"
                    r"PREFEITURA[ \t]+(?:DO[ \t]+MUNIC[ÍI]PIO|MUNICIPAL)[ \t]+DE[ \t]+PAUL[ÍI]NIA)\b", re.I)
ANEXO_PROPRIO = re.compile(
    r"\bAnexos?[ \t]+(?:[IVX]+|[ÚU]nico|\d+)\b[^.;\n]{0,60}?\b(?:dest[ea]|d[oa][ \t]+presente)[ \t]+(?:Lei|Decreto)|"
    r"\b(?:constantes?|na[ \t]+forma|nos[ \t]+termos|conforme|de[ \t]+acordo[ \t]+com|integrante)[ \t]+(?:d?[eo]s?|n?os?|o)?[ \t]*Anexos?\b|"
    r"\bAnexos?[ \t]+(?:[ÚU]nico|[IVX]+)[^.;\n]{0,40}?\b(?:que|parte)[ \t]+(?:integra|integrante)", re.I)
PRAZO_DE_PUBLICACAO = 120  # dias: ato mais antigo que isto na edição é republicação ou citação, não publicação original


def data_iso(dia, mes, ano):
    """'13', 'Novembro', '2.026' -> '2026-11-13'; None quando a data não existe."""
    try:
        return dt.date(int(str(ano).replace(".", "")), MESES[mes.lower()], int(dia)).isoformat()
    except (KeyError, ValueError):
        return None


def nome(conteudo):
    """Linha com o nome de quem assina: maiúsculas, sem dígitos nem colunas, e não um cabeçalho de órgão ou de publicação."""
    return (len(conteudo) <= 70 and bool(NOME.fullmatch(conteudo)) and not NAO_E_ASSINATURA.match(conteudo)
            and not re.search(r"\S[ \t]{3,}\S", conteudo))


def fim_das_assinaturas(trecho, inicio, jornal=False):
    """Posição em que termina o bloco de assinaturas que começa em `inicio` (fim da linha do signatário): pares de nome
    e cargo, cargos avulsos e a nota de lavratura, que pode ocupar até três linhas (com quebra de coluna no meio) e
    termina em ponto. Nome sem cargo reconhecido na linha seguinte não entra: pode ser o título de outra publicação.
    Com `jornal`, a coluna estreita parte o nome em duas linhas ("DR. WASHINGTON CARLOS" / "RIBEIRO SOARES"): vale
    também o nome de duas linhas seguido do cargo."""
    linhas = [(m.end(), m.group(0).strip()) for m in re.finditer(r"[^\n]*\n?", trecho[inicio:]) if m.group(0)]
    fim, nota, i = inicio, 0, 0
    while i < len(linhas) and fim - inicio <= 1500:
        ate, conteudo = linhas[i]
        if not conteudo:
            i += 1
            continue
        seguinte = next((k for k in range(i + 1, len(linhas)) if linhas[k][1]), None)
        # depois do nome, o cargo também aparece grafado como o órgão ("Secretaria de Defesa e ... do Meio Ambiente")
        par = nome(conteudo) and seguinte is not None and bool(
            CARGO.fullmatch(linhas[seguinte][1]) or re.fullmatch(r"Secretaria [^\n]{3,90}(?<![:;,.])", linhas[seguinte][1]))
        if not par and jornal and nome(conteudo) and seguinte is not None and nome(linhas[seguinte][1]):
            terceira = next((k for k in range(seguinte + 1, len(linhas)) if linhas[k][1]), None)
            if terceira is not None and CARGO.fullmatch(linhas[terceira][1]):
                par, seguinte = True, terceira
        if par:
            fim, nota, i = inicio + linhas[seguinte][0], 0, seguinte + 1
        elif CARGO.fullmatch(conteudo):
            fim, nota, i = inicio + ate, 0, i + 1
        elif nota:
            if nota >= 3:
                break  # a nota não fechou com ponto: o que segue não é assinatura
            fim, nota, i = inicio + ate, (0 if conteudo.endswith(".") else nota + 1), i + 1
        elif NOTA.match(conteudo) and not nome(conteudo):
            fim, nota, i = inicio + ate, (0 if conteudo.endswith(".") else 1), i + 1
        else:
            break
    return fim


def atos_da_edicao(trechos, data_edicao, jornal=False):
    """[(ato, recorte ou None, motivo ou None)] das leis e decretos da edição. `ato` traz chave, tipo_na_fonte, numero,
    data, pagina e epigrafe; o recorte vai da epígrafe ao fim do bloco de assinaturas. Com `jornal`, a epígrafe pode
    vir partida em mais de uma linha."""
    epigrafe, em_maiusculas = (EPIGRAFE_DE_JORNAL, EPIGRAFE_DE_JORNAL_EM_MAIUSCULAS) if jornal else (EPIGRAFE, EPIGRAFE_EM_MAIUSCULAS)
    texto, paginas, pos = "", [], 0
    for n, t in trechos:
        paginas.append((pos, n))
        texto += t + "\n\n"
        pos = len(texto)
    achados = []
    for m in epigrafe.finditer(texto):
        chave, tipo_na_fonte = TIPOS[" ".join(m.group(1).upper().split())]
        data = data_iso(m.group(3), m.group(4), m.group(5))
        if not em_maiusculas.match(m.group(0)):
            # em caixa mista a linha também pode ser a citação de outro ato no meio de um texto: só vale como
            # epígrafe a que tem data de publicação possível nesta edição
            atraso = (dt.date.fromisoformat(data_edicao) - dt.date.fromisoformat(data)).days if data and data_edicao else -1
            if not 0 <= atraso <= PRAZO_DE_PUBLICACAO:
                continue
        achados.append((m, {"chave": chave, "tipo_na_fonte": tipo_na_fonte, "numero": m.group(2).replace(".", "").lstrip("0") or "0",
                            "data": data,
                            "pagina": max(n for p, n in paginas if p <= m.start()),
                            "epigrafe": " ".join(m.group(0).split())}))
    vezes = {}
    for _, ato in achados:
        vezes[(ato["chave"], ato["numero"])] = vezes.get((ato["chave"], ato["numero"]), 0) + 1
    saida = []
    for i, (m, ato) in enumerate(achados):
        if vezes[(ato["chave"], ato["numero"])] > 1:
            saida.append((ato, None, "epígrafe repetida na edição (republicação, retificação ou citação em linha própria)"))
            continue
        if not ato["data"]:
            saida.append((ato, None, "data da epígrafe inválida"))
            continue
        if data_edicao:
            atraso = (dt.date.fromisoformat(data_edicao) - dt.date.fromisoformat(ato["data"])).days
            if atraso < 0:
                saida.append((ato, None, f"data da epígrafe posterior à da edição ({data_edicao})"))
                continue
            if atraso > PRAZO_DE_PUBLICACAO:
                saida.append((ato, None, f"ato de {ato['data']} em edição de {data_edicao}: republicação ou citação, a conferir"))
                continue
        # o trecho vai até a publicação seguinte; o cabeçalho dela só é procurado depois do primeiro artigo, porque a
        # ementa em maiúsculas quebra linhas em "CONSELHO DE ...", "LEI COMPLEMENTAR Nº 88 ..." ou "SECRETARIA ..."
        teto = achados[i + 1][0].start() if i + 1 < len(achados) else len(texto)
        artigo = ARTIGO.search(texto, m.end(), teto)
        prox = LIMITE.search(texto, artigo.end(), teto) if artigo else None
        trecho = texto[m.start():prox.start() if prox else teto]
        if jornal:  # a epígrafe partida pela coluna estreita volta a ser uma linha só
            trecho = " ".join(m.group(0).split()) + trecho[len(m.group(0)):]
        saida.append((ato, *recortar(trecho, ato, jornal)))
    return saida


NUMERO_DO_ARTIGO = re.compile(r"^[ \t]*(?:Art\.?|ART\.?|ARTIGO|Artigo)[ \t]*(\d+)", re.M)


def artigos_fora_de_sequencia(recorte):
    """Motivo quando a numeração dos artigos do recorte não fecha: os artigos do ato formam a cadeia 1, 2, 3..., o
    último artigo antes das assinaturas tem de ser o fim dela e o artigo seguinte ao fim não pode ter aparecido antes
    (coluna fora de ordem). Artigo de outra lei transcrito no meio, com outro número, não quebra a cadeia."""
    numeros = [int(n) for n in NUMERO_DO_ARTIGO.findall(recorte)]
    if not numeros:
        return None  # "Artigo único"
    esperado, fora = 1, set()
    for n in numeros:
        if n == esperado:
            esperado += 1
        else:
            fora.add(n)
    if numeros[-1] != esperado - 1 or esperado in fora:
        return (f"numeração dos artigos fora de sequência (cadeia até o art. {esperado - 1}, último artigo no recorte: "
                f"{numeros[-1]}); conferir a ordem das colunas")
    return None


def recortar(trecho, ato, jornal=False):
    """(recorte, None) ou (None, motivo) para o trecho que vai da epígrafe do ato até a publicação seguinte."""
    artigo = ARTIGO.search(trecho)
    if not artigo:
        return None, "sem artigo entre a epígrafe e a publicação seguinte"
    if not FORMULA[ato["chave"]].search(re.sub(r"-[ \t]*\n\s*", "", trecho[:artigo.start()])):  # "PROMUL-" + "GO"
        return None, "fórmula de promulgação ausente antes do primeiro artigo"
    signatario = None
    for s in SIGNATARIO.finditer(trecho, artigo.end()):
        signatario = s  # o último antes da publicação seguinte: regulamento em anexo também traz artigos
        break
    if not signatario:
        return None, "sem a assinatura do Prefeito ou do Presidente da Câmara antes da publicação seguinte"
    fechos = [f for f in (FECHO_DE_JORNAL if jornal else FECHO).finditer(trecho, artigo.end(), signatario.start())]
    if fechos:
        data_fecho = data_iso(*fechos[-1].groups())
        if data_fecho != ato["data"]:
            return None, f"data do fecho ({data_fecho}) difere da data da epígrafe ({ato['data']})"
    fim = fim_das_assinaturas(trecho, signatario.end(), jornal)
    recorte, resto = trecho[:fim], trecho[fim:]
    # o que segue as assinaturas é outra publicação, salvo anexo, quadro ou frase que continua: aí o limite não é seguro
    seguinte = next((ln for ln in resto.split("\n") if ln.strip()), "")
    if ANEXO.search(resto[:2500]) or APENSO.match(seguinte):
        return None, "anexo publicado depois das assinaturas; o limite do anexo não é seguro"
    if seguinte.strip()[:1].islower() or re.search(r"\S[ \t]{3,}\S", seguinte.strip()):
        return None, "texto ou quadro depois das assinaturas e antes da publicação seguinte; conferir os limites do ato"
    if nome(seguinte.strip()):
        return None, "linha em maiúsculas depois das assinaturas (assinatura com cargo não reconhecido ou outro título); a conferir"
    if ANEXO_PROPRIO.search(recorte) and not ANEXO.search(recorte):
        return None, "o ato cita anexo próprio que não está no recorte"
    if any(RODAPE.search(linha) for linha in recorte.split("\n")):
        return None, "rodapé da página dentro do recorte; a área de texto da página não foi delimitada"
    intercalado = INTERCALADO.search(recorte, len(ato["epigrafe"]))
    if intercalado:
        return None, "trecho de outra publicação intercalado no recorte: " + intercalado.group(0).strip()[:80]
    sequencia = artigos_fora_de_sequencia(recorte)
    if sequencia:
        return None, sequencia
    if len(recorte) > TAMANHO_MAXIMO:
        return None, f"recorte longo demais ({len(recorte)} caracteres); conferir os limites do ato"
    return recorte.strip("\n") + "\n", None


# ------------------------------------------------------------------------------------------ gravação
_QUADRO = re.compile(r"(```text\n.*?\n```)", re.S)


def _letras_do_paragrafo(paragrafo):
    return so_letras(re.sub(r"\\([*_])", r"\1", paragrafo).replace("**", "").lstrip("#"))


def rejuntar(corpo, fluxo=None):
    """Desfaz a quebra de parágrafo no meio da frase: o diário às vezes espaça as linhas de um mesmo período, e a
    leitura as devolve como parágrafos ("... eu, seu Presidente, PROMULGO" / "o seguinte Decreto Legislativo:").
    Junta o parágrafo que começa em minúscula ao anterior que não termina em pontuação; quadros ficam como estão.
    Com o fluxo do PDF, só junta o que ele confirma como texto contínuo; o resto fica em dois parágrafos."""
    saida = []
    for trecho in _QUADRO.split(corpo):
        if trecho.startswith("```text"):
            saida.append(trecho)
            continue
        juntos = []
        for paragrafo in trecho.split("\n\n"):
            anterior = juntos[-1].rstrip() if juntos else ""
            if (anterior and re.match(r"[a-zà-ú]", paragrafo) and not re.match(r"[a-z]{1,4}[ \t]*[)\-–.]", paragrafo)
                    and not anterior.lstrip().startswith("#") and not re.search(r"[.:;!?”\")\-–]$", anterior)
                    and (fluxo is None or _letras_do_paragrafo(anterior + " " + paragrafo) in fluxo)):
                juntos[-1] = anterior + " " + paragrafo
            else:
                juntos.append(paragrafo)
        saida.append("\n\n".join(juntos))
    return "".join(saida)


def titulo_de(ato):
    ano, mes, dia = (int(x) for x in ato["data"].split("-"))
    numero = f"{int(ato['numero']):,}".replace(",", ".")
    return f"{ato['tipo_na_fonte']} nº {numero}, de {'1º' if dia == 1 else dia} de {NOME_MES[mes]} de {ano}"


def destino_de(ato, edicao):
    pasta, _ = CANONICO[ato["chave"]]
    nome = slugify(f"{ato['chave']}-{ato['numero']}-{ato['data'][:4]}-dom-{edicao['edicao']}")
    return DESTINO / pasta / ato["data"][:4] / (nome + ".md")


_FECHA_ASPAS = re.compile(r"[”\"]\s*\.?\s*$")
_NOTA_DO_PROJETO = re.compile(r"^\(?\s*Projeto de (?:Lei|Decreto|Emenda|Resolução)\b.{0,200}$", re.I | re.S)
_PREAMBULO = re.compile(r"^(?:O|A)\s+(?:CIDADÃO|CIDADÃ|PREFEIT|PRESIDENTE|MESA|CÂMARA)|\b(?:DECRETA|PROMULG[AO]|SANCIONO)\b", re.I)


def _caixa_alta(texto):
    return bool(re.search(r"[A-ZÀ-Ú]", texto)) and not re.search(r"[a-zà-ú]", texto)


def _continua_em_caixa_alta(texto):
    """Continuação de ementa em maiúsculas: sem minúsculas ou com poucas ("APMs", "MUNICíPIO", "(Matrícula 17.527)")."""
    minusculas, maiusculas = len(re.findall(r"[a-zà-ú]", texto)), len(re.findall(r"[A-ZÀ-Ú]", texto))
    return minusculas <= 0.4 * (minusculas + maiusculas)


def ementa_de(corpo):
    """A ementa, quando o parágrafo que segue a epígrafe (e a nota do projeto) vem entre aspas ou em maiúsculas.

    O diário às vezes parte a ementa em mais de um parágrafo: a leitura segue até o parágrafo que fecha as aspas (ou,
    sem aspas, enquanto durar a caixa alta). Sem fecho à vista, vale só o primeiro parágrafo."""
    paragrafos = [re.sub(r"\\([*_])", r"\1", p.strip()) for p in corpo.split("\n\n") if p.strip()][1:9]
    while paragrafos and (_NOTA_DO_PROJETO.match(paragrafos[0]) or (paragrafos[0].startswith("(") and paragrafos[0].endswith(")"))):
        paragrafos.pop(0)  # "(Projeto de Lei Nº 127/2026 de autoria do Ver. ...)"
    if not paragrafos:
        return ""
    primeiro, partes = paragrafos[0], [paragrafos[0]]
    alta = _caixa_alta(primeiro)
    if primeiro[:1] in "“\"":
        if not _FECHA_ASPAS.search(primeiro[1:]):
            for p in paragrafos[1:5]:
                if ARTIGO.match(p) or _PREAMBULO.search(p) or (alta and not _continua_em_caixa_alta(p)):
                    partes = [primeiro]
                    break
                partes.append(p)
                if _FECHA_ASPAS.search(p):
                    break
            else:
                partes = [primeiro]
    elif alta:
        if not primeiro.endswith("."):
            for p in paragrafos[1:5]:
                if not _continua_em_caixa_alta(p) or ARTIGO.match(p) or _PREAMBULO.search(p):
                    break
                partes.append(p)
                if p.rstrip("”\" ").endswith("."):
                    break
    else:
        return ""
    ementa = " ".join(" ".join(partes).strip("“”\"' ").split())
    fecho = re.search(r"[”\"]\s*\.$", ementa)
    if fecho and (ementa.count("”") > ementa.count("“") or ementa.count('"') % 2):
        ementa = ementa[:fecho.start()] + "."  # aspas de fora fechadas antes do ponto final: `...PROVIDÊNCIAS”.`
    return ementa


def montar_md(ato, edicao, corpo, tem_quadro, sha_pdf, hoje):
    _, tipo = CANONICO[ato["chave"]]
    titulo = titulo_de(ato)
    jornal = edicao.get("periodico") or "Diário Oficial"
    notas = [NOTA_DOM.replace("Diário Oficial", jornal)] + ([dom.NOTA_QUADRO] if tem_quadro else [])
    dia = dt.date.fromisoformat(edicao["data"]).strftime("%d/%m/%Y")
    meta = [("titulo", titulo), ("tipo", tipo), ("tipo_na_fonte", ato["tipo_na_fonte"]), ("numero", ato["numero"]),
            ("data", ato["data"]), ("municipio", MUNICIPIO), ("uf", UF), ("codigo_ibge", CODIGO_IBGE)]
    ementa = ementa_de(corpo)
    if ementa:
        meta.append(("ementa", ementa))
    meta += [("versao_texto", "texto original (não consolidado); " + "; ".join(notas)),
             ("publicacao", f"{jornal} do Município de Paulínia, edição nº {edicao['edicao']}, de {dia}, p. {ato['pagina']}"),
             ("data_publicacao", edicao["data"]),
             ("fonte", f"{BASE}/portal/diario-oficial/ver/{edicao['id']}"),
             ("fonte_texto", edicao["pdf"]),
             ("sha256_fonte", sha_pdf),
             ("sha256_texto", hashlib.sha256(corpo.encode("utf-8")).hexdigest()),
             ("baixado_em", hoje.isoformat())]
    return "---\n" + "\n".join(f"{k}: {yaml_str(v)}" for k, v in meta) + f"\n---\n\n# {titulo}\n\n{corpo}\n"


# ------------------------------------------------------------------------------------------ edições e execução
ITEM = '<div class="dof_publicacao_diario sw_item_listagem">'
MODELO = (722.8, 841.9)  # pt: página do leiaute de duas colunas conferido
JORNAL_PAGINAS = [(652.0, 892.9), (1303.9, 892.9)]  # pt: o formato de jornal, página simples e dupla; outro não é lido


def texto_html(bruto):
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", bruto)).split())


def edicoes_da_pagina(pagina_html):
    """[{id, edicao, data, token}] das edições de uma página da listagem do portal; `data` é None quando falta."""
    saida = []
    for bloco in pagina_html.split(ITEM)[1:]:
        ver = re.search(r"/portal/diario-oficial/ver/(\d+)", bloco)
        token = re.search(r"/portal/download/diario-oficial/([^/\"'\s]+)", bloco)  # o código pode ter hífen
        rotulo = texto_html(bloco)
        numero = re.search(r"Edi[çc][ãa]o n[º°o]\s*([\d.]+)", rotulo)
        postagem = re.search(r"Postagem:\s*(\d{2})/(\d{2})/(\d{4})", rotulo)
        if not (ver and token and numero):
            continue
        data = f"{postagem.group(3)}-{postagem.group(2)}-{postagem.group(1)}" if postagem else None
        saida.append({"id": ver.group(1), "edicao": numero.group(1).replace(".", ""), "data": data, "token": token.group(1)})
    return saida


def listar_edicoes(rede, de, ate):
    """Edições postadas entre os anos `de` e `ate`, da mais antiga para a mais recente. A listagem vem da mais recente
    para a mais antiga: a leitura para na primeira página toda anterior a `de`."""
    achadas, vistos = [], set()
    for pagina in range(1, 400):
        st, bruto, _ = rede.get(f"{BASE}/portal/diario-oficial/{pagina}/0/0/0/0")
        if st != 200:
            raise RuntimeError(f"listagem de edições, página {pagina}: HTTP {st}")
        itens = [e for e in edicoes_da_pagina(bruto.decode("utf-8", "replace")) if e["id"] not in vistos]
        if not itens:
            break
        vistos.update(e["id"] for e in itens)
        achadas += itens
        anos = [int(e["data"][:4]) for e in itens if e["data"]]
        if anos and max(anos) < de:
            break
    sem_data = [e["edicao"] for e in achadas if not e["data"]]
    if sem_data:
        print(f"[aviso] edições sem data de postagem na listagem, fora da coleta: {', '.join(sem_data)}", flush=True)
    return sorted((e for e in achadas if e["data"] and de <= int(e["data"][:4]) <= ate),
                  key=lambda e: (e["data"], int(e["edicao"]), int(e["id"])))


def edicoes_dos_dados_abertos(rede, ano):
    """Números das edições do ano segundo os dados abertos do portal: confere a listagem."""
    st, bruto, _ = rede.get(f"{BASE}/portal/dados-abertos/diario-oficial/{ano}", "application/json")
    if st != 200:
        raise RuntimeError(f"dados abertos de {ano}: HTTP {st}")
    return {str(e["edicao"]).replace(".", "") for e in json.loads(bruto)["dados"]}


def vedados_pelo_robots(robots, caminhos, agente="*"):
    """Os `caminhos` que o `robots.txt` veda ao `agente`: somados todos os grupos que o nomeiam (RFC 9309, seção 2.2.1),
    vale a regra de caminho mais longo, e Allow vence Disallow no empate."""
    regras, grupo, nomes, em_regras = [], False, [], False
    for linha in robots.splitlines():
        linha = linha.split("#", 1)[0].strip()
        if ":" not in linha:
            continue
        campo, valor = (x.strip() for x in linha.split(":", 1))
        campo = campo.lower()
        if campo == "user-agent":
            if em_regras:
                nomes, em_regras = [], False
            nomes.append(valor.lower())
            grupo = agente.lower() in nomes
        elif campo in ("allow", "disallow"):
            em_regras = True
            if grupo and valor:
                regras.append((len(valor), campo == "allow", valor))
    vedados = []
    for caminho in caminhos:
        casadas = sorted((r for r in regras if caminho.startswith(r[2])), key=lambda r: (r[0], r[1]))
        if casadas and not casadas[-1][1]:
            vedados.append(caminho)
    return vedados


def baixar_pdf(rede, edicao, so_cache=False):
    """(endereço do PDF, arquivo em cache). O link de download responde com um redirecionamento em HTML para /uploads.
    Com `so_cache`, a edição fora do cache é um erro, sem nenhum pedido à rede."""
    FONTE.mkdir(parents=True, exist_ok=True)
    em_cache = sorted(FONTE.glob(f"{edicao['id']}-*.pdf"))
    if em_cache and edicao.get("pdf"):
        return edicao["pdf"], em_cache[0]
    if so_cache:
        raise RuntimeError("PDF fora do cache; o robots.txt do portal veda o download (/portal/download/, /uploads/)")
    url = f"{BASE}/portal/download/diario-oficial/{edicao['token']}/"
    st, bruto, _ = rede.get(url)
    if st != 200:
        raise RuntimeError(f"download HTTP {st}")
    if not bruto.startswith(b"%PDF"):
        alvo = re.search(rb"url=([^\"'> ]+\.pdf)", bruto, re.I)
        if not alvo:
            raise RuntimeError("página de download sem o endereço do PDF")
        url = BASE + alvo.group(1).decode("ascii", "replace")
        st, bruto, _ = rede.get(url)
        if st != 200 or not bruto.startswith(b"%PDF"):
            raise RuntimeError(f"PDF da edição: HTTP {st} ou arquivo que não é PDF")
    destino = FONTE / f"{edicao['id']}-{slugify(url.rsplit('/', 1)[1])}"
    tmp = destino.with_suffix(".tmp")
    tmp.write_bytes(bruto)
    tmp.replace(destino)
    return url, destino


def _do_formato(largura, altura, formatos):
    return any(abs(largura - lg) <= 3 and abs(altura - al) <= 3 for lg, al in formatos)


def leiaute(paginas):
    """JORNAL quando todas as páginas são do formato de jornal (simples ou duplas); "modelo" quando todas são do leiaute
    de duas colunas; None quando a edição mistura formatos ou tem outro."""
    medidas = [(largura, altura) for largura, altura, _ in paginas.values()]
    if medidas and all(_do_formato(lg, al, JORNAL_PAGINAS) for lg, al in medidas):
        return JORNAL
    if medidas and all(_do_formato(lg, al, [MODELO]) for lg, al in medidas):
        return "modelo"
    return None


def fora_do_modelo(paginas):
    """Motivo quando a edição não está toda num dos dois leiautes conferidos (duas colunas ou jornal)."""
    if leiaute(paginas):
        return None
    for n, (largura, altura, _) in sorted(paginas.items()):
        if not _do_formato(largura, altura, [MODELO, *JORNAL_PAGINAS]):
            return f"página {n} de {largura:.0f} x {altura:.0f} pt, fora dos leiautes conferidos (duas colunas e jornal)"
    return "edição que mistura o leiaute de duas colunas e o de jornal"


def publicados():
    """{(chave, número, ano): arquivo} dos atos já gravados, pelo nome do arquivo."""
    saida = {}
    for chave in {c for c, _ in TIPOS.values()}:
        pasta, _ = CANONICO[chave]
        for md in (DESTINO / pasta).glob("*/*.md"):
            m = re.fullmatch(rf"{re.escape(slugify(chave))}-(\d+)-(\d{{4}})-dom-\d+", md.stem)
            if m:
                saida[(chave, m.group(1), m.group(2))] = md
    return saida


def ler_falhas():
    if not FALHAS.exists():
        return []
    return [json.loads(ln) for ln in FALHAS.read_text(encoding="utf-8").splitlines() if ln.strip()]


def gravar_falhas(registros):
    def ordem(r):
        return (int(r["edicao"]), r.get("tipo", ""), int(r.get("numero") or 0))
    FALHAS.parent.mkdir(parents=True, exist_ok=True)
    tmp = FALHAS.with_suffix(".tmp")
    tmp.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in sorted(registros, key=ordem)), encoding="utf-8")
    tmp.replace(FALHAS)


def edicao_do_arquivo(arquivo):
    """Número da edição de onde o arquivo foi recortado (`...-dom-<edição>.md`)."""
    return int(arquivo.stem.rsplit("-", 1)[1])


def republicacao(gravado, destino, tipo, ato):
    """Retenção do arquivo `gravado`, que cede o lugar ao mesmo ato recortado de edição anterior (`destino`)."""
    texto = gravado.read_text(encoding="utf-8")

    def campo(nome):
        m = re.search(rf'^{nome}: "([^"]*)"', texto, re.M)
        return m.group(1) if m else ""

    return {"edicao": str(edicao_do_arquivo(gravado)), "data_edicao": campo("data_publicacao"), "fonte": campo("fonte"),
            "tipo": tipo, "numero": ato["numero"], "data": ato["data"],
            "motivo": f"ato já recortado de outra edição ({destino.name}); republicação a conferir"}


def executar(de, ate, maximo=0, listar=False, rps=0.5):
    rede = Rede(rps=rps, headers={"Accept-Language": "pt-BR"})
    CACHE.mkdir(parents=True, exist_ok=True)
    arquivo_cache = CACHE / "edicoes.json"
    cache = json.loads(arquivo_cache.read_text(encoding="utf-8")) if arquivo_cache.exists() else {}
    st, robots, _ = rede.get(f"{BASE}/robots.txt")
    vedados = vedados_pelo_robots(robots.decode("utf-8", "replace"), ["/portal/diario-oficial/", "/portal/dados-abertos/",
                                                                      "/portal/download/", "/uploads/"]) if st == 200 else []
    if {"/portal/diario-oficial/", "/portal/dados-abertos/"} & set(vedados):
        raise RuntimeError(f"o robots.txt do portal veda a listagem das edições: {vedados}")
    so_cache = bool(vedados)
    if so_cache:
        print(f"[aviso] o robots.txt veda {', '.join(vedados)}: só as edições já em cache serão lidas", flush=True)
    edicoes = listar_edicoes(rede, de, ate)
    for ano in range(de, ate + 1):
        na_listagem = {e["edicao"] for e in edicoes if e["data"][:4] == str(ano)}
        abertos = edicoes_dos_dados_abertos(rede, ano)
        print(f"{ano}: {len(na_listagem)} edições na listagem, {len(abertos)} nos dados abertos"
              + (f"; só nos dados abertos: {sorted(abertos - na_listagem)}" if abertos - na_listagem else "")
              + (f"; só na listagem: {sorted(na_listagem - abertos)}" if na_listagem - abertos else ""), flush=True)
    if listar:
        return 0
    ja = publicados()
    falhas = ler_falhas()
    hoje = dt.date.today()
    contagem = {"edicoes": 0, "novo": 0, "pulado": 0, "retida": 0, "republicada": 0, "erro": 0}
    motivos = {}
    for edicao in edicoes:
        if maximo and contagem["novo"] >= maximo:
            print(f"limite de {maximo} novas conversões atingido", flush=True)
            break
        edicao["pdf"] = (cache.get(edicao["id"]) or {}).get("pdf")
        base = {"edicao": edicao["edicao"], "data_edicao": edicao["data"],
                "fonte": f"{BASE}/portal/diario-oficial/ver/{edicao['id']}"}
        # pela página da edição, não pelo número: a listagem do portal repete alguns números em edições diferentes
        falhas = [f for f in falhas if f["fonte"] != base["fonte"]]
        try:
            edicao["pdf"], pdf = baixar_pdf(rede, edicao, so_cache)
            cache[edicao["id"]] = {"edicao": edicao["edicao"], "data": edicao["data"], "pdf": edicao["pdf"]}
            leitura = Edicao(pdf)
            motivo = fora_do_modelo(leitura.paginas)
            if motivo:
                raise RuntimeError(motivo)
            numero, data_impressa = edicao_impressa(leitura.paginas)
            if numero != edicao["edicao"]:
                raise RuntimeError(f"o PDF baixado traz a edição {numero or 'sem número'}, não a {edicao['edicao']}")
            if data_impressa:
                edicao["data"] = data_impressa  # a data impressa na edição vale mais que a de postagem no portal
                cache[edicao["id"]]["data"] = data_impressa
            edicao["periodico"] = periodico(leitura.paginas)
            atos = atos_da_edicao(leitura.trechos(), edicao["data"], leitura.jornal)
            sha_pdf = hashlib.sha256(pdf.read_bytes()).hexdigest()
        except Exception as e:  # rede ou PDF inesperado: registra e segue para a próxima edição
            contagem["erro"] += 1
            falhas.append({**base, "motivo": f"erro: {str(e)[:200]}"})
            print(f"[erro] edição {edicao['edicao']}: {e}", flush=True)
            continue
        contagem["edicoes"] += 1
        base["data_edicao"] = edicao["data"]
        for ato, recorte, motivo in atos:
            _, tipo = CANONICO[ato["chave"]]
            registro = {**base, "tipo": tipo, "numero": ato["numero"], "data": ato["data"], "pagina": ato["pagina"]}
            chave = (ato["chave"], ato["numero"], (ato["data"] or "0000")[:4])
            destino = destino_de(ato, edicao) if ato["data"] else None
            corpo = tem_quadro = None
            if not motivo:
                corpo, tem_quadro = dom.para_md(recorte)
                corpo = rejuntar(corpo, leitura.fluxo())
                motivo = diverge_do_fluxo(corpo, leitura.fluxo())
            if not motivo and chave in ja and ja[chave] != destino:
                if edicao_do_arquivo(ja[chave]) > int(edicao["edicao"]):
                    # a edição mais antiga é a publicação original: o arquivo da mais nova sai e vira a republicação
                    falhas.append(republicacao(ja[chave], destino, tipo, ato))
                    ja.pop(chave).unlink()
                    contagem["republicada"] += 1
                else:
                    motivo = f"ato já recortado de outra edição ({ja[chave].name}); republicação a conferir"
                    contagem["republicada"] += 1
            elif motivo:
                contagem["retida"] += 1
            if motivo:
                falhas.append({**registro, "motivo": motivo})
                motivos[motivo.split(":")[0].split("(")[0].strip()[:70]] = motivos.get(motivo.split(":")[0].split("(")[0].strip()[:70], 0) + 1
                continue
            if destino.exists():
                contagem["pulado"] += 1
                continue
            destino.parent.mkdir(parents=True, exist_ok=True)
            tmp = destino.with_suffix(".tmp")
            tmp.write_text(montar_md(ato, edicao, corpo, tem_quadro, sha_pdf, hoje), encoding="utf-8")
            tmp.replace(destino)
            ja[chave] = destino
            contagem["novo"] += 1
        if contagem["edicoes"] % 20 == 0:
            gravar_falhas(falhas)
            arquivo_cache.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
            print(f"  ... edição {edicao['edicao']} ({edicao['data']}): {contagem}", flush=True)
    gravar_falhas(falhas)
    arquivo_cache.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"contagem": contagem, "motivos": motivos}, ensure_ascii=False), flush=True)
    return contagem["novo"]


def regravar_periodico(gravar=False):
    """Confere, em cada ato já gravado, o nome do periódico em `publicacao` e em `versao_texto` contra o que a edição em
    cache imprime ("Semanário Oficial" até 2020) e, com `gravar`, corrige os dois campos. O corpo do ato não muda, e
    com ele o `sha256_texto`. Devolve {"conferidos", "corrigidos", "sem_pdf"}."""
    nomes, contagem = {}, {"conferidos": 0, "corrigidos": 0, "sem_pdf": 0}
    for md in sorted(DESTINO.glob("*/*/*.md")):
        texto = md.read_text(encoding="utf-8")
        fonte = re.search(r'^fonte: ".*/portal/diario-oficial/ver/(\d+)"$', texto, re.M)
        if not fonte:
            continue  # a Lei Orgânica, que não vem do Diário
        ident = fonte.group(1)
        if ident not in nomes:
            pdf = next(iter(sorted(FONTE.glob(f"{ident}-*.pdf"))), None)
            nomes[ident] = periodico(palavras_da_edicao(pdf, ate=3)) if pdf else None
        nome_certo = nomes[ident]
        if not nome_certo:
            contagem["sem_pdf"] += 1
            continue
        contagem["conferidos"] += 1
        outro = "Diário Oficial" if nome_certo == "Semanário Oficial" else "Semanário Oficial"
        novo = re.sub(rf'^(publicacao: "){outro}( do Município de Paulínia,)', rf"\g<1>{nome_certo}\2", texto, flags=re.M)
        novo = re.sub(rf'^(versao_texto: "[^"\n]*recortado da edição do ){outro}( do Município)', rf"\g<1>{nome_certo}\2",
                      novo, flags=re.M)
        if novo != texto:
            contagem["corrigidos"] += 1
            if gravar:
                tmp = md.with_suffix(".tmp")
                tmp.write_text(novo, encoding="utf-8")
                tmp.replace(md)
    return contagem


def lei_organica(rede, hoje):
    """Grava a Lei Orgânica compilada do site da Câmara. Devolve o arquivo; levanta erro quando o PDF não é o esperado."""
    st, bruto, tipo = rede.get(LEI_ORGANICA_PDF)
    if st != 200 or not bruto.startswith(b"%PDF"):
        raise RuntimeError(f"Lei Orgânica: HTTP {st} ou arquivo que não é PDF")
    corpo, motivo = documento_para_md(bruto, LEI_ORGANICA_PDF, tipo)
    if motivo:
        raise RuntimeError(f"Lei Orgânica: {motivo}")
    corpo = corpo.strip()
    inicio = " ".join(corpo[:800].split())
    cabecalho = re.search(rf"LEI ORG[ÂA]NICA DO MUNIC[ÍI]PIO DE PAUL[ÍI]NIA DE (\d{{1,2}}) DE ({_MES}) DE (\d{{4}})", inicio, re.I)
    data = data_iso(*cabecalho.groups()) if cabecalho else None
    if not data:
        raise RuntimeError("Lei Orgânica: cabeçalho com o nome e a data não reconhecido no início do texto")
    versao = "texto compilado pela Câmara Municipal de Paulínia (PDF do site da Câmara)"
    emenda = re.search(rf"Atualizada até a Emenda n[º°o]\s*(\d+), de (\d{{1,2}}) de ({_MES}) de (\d{{4}})", inicio, re.I)
    if emenda:
        versao += (f", atualizado até a Emenda nº {emenda.group(1)}, de {int(emenda.group(2))} de "
                   f"{emenda.group(3).lower()} de {emenda.group(4)}, conforme o próprio arquivo")
    ano, mes, dia = (int(x) for x in data.split("-"))
    titulo = f"Lei Orgânica do Município de Paulínia, de {'1º' if dia == 1 else dia} de {NOME_MES[mes]} de {ano}"
    meta = [("titulo", titulo), ("tipo", "Lei Orgânica"), ("tipo_na_fonte", "Lei Orgânica"), ("numero", ""), ("data", data),
            ("municipio", MUNICIPIO), ("uf", UF), ("codigo_ibge", CODIGO_IBGE), ("versao_texto", versao),
            ("fonte", LEI_ORGANICA_PDF), ("sha256_fonte", hashlib.sha256(bruto).hexdigest()),
            ("sha256_texto", hashlib.sha256(corpo.encode("utf-8")).hexdigest()), ("baixado_em", hoje.isoformat())]
    destino = DESTINO / "lei-organica" / str(ano) / f"lei-organica-{ano}-camara.md"
    destino.parent.mkdir(parents=True, exist_ok=True)
    FONTE.mkdir(parents=True, exist_ok=True)
    (FONTE / "lei-organica.pdf").write_bytes(bruto)
    tmp = destino.with_suffix(".tmp")
    tmp.write_text("---\n" + "\n".join(f"{k}: {yaml_str(v)}" for k, v in meta) + f"\n---\n\n# {titulo}\n\n{corpo}\n", encoding="utf-8")
    tmp.replace(destino)
    return destino


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--de", type=int, help="primeiro ano")
    ap.add_argument("--ate", type=int, help="último ano, inclusive")
    ap.add_argument("--max", type=int, default=0, help="limita novas conversões; 0 = sem limite")
    ap.add_argument("--listar", action="store_true", help="só confere a listagem contra os dados abertos; não baixa PDFs")
    ap.add_argument("--rps", type=float, default=0.5, help="requisições por segundo")
    ap.add_argument("--despejar", type=Path, help="mostra o texto de uma edição em ordem de leitura e sai")
    ap.add_argument("--lei-organica", action="store_true", help="grava a Lei Orgânica compilada do site da Câmara e sai")
    ap.add_argument("--periodico", action="store_true",
                    help="confere o nome do periódico nos atos gravados contra as edições em cache e sai")
    ap.add_argument("--gravar", action="store_true", help="com --periodico, corrige os arquivos")
    a = ap.parse_args()
    if a.despejar:
        for pagina, texto in Edicao(a.despejar).trechos():
            print(f"\n=== página {pagina}\n{texto}")
    elif a.periodico:
        print(json.dumps(regravar_periodico(a.gravar), ensure_ascii=False))
    elif a.lei_organica:
        print(lei_organica(Rede(rps=a.rps), dt.date.today()))
    elif a.de and a.ate:
        executar(a.de, a.ate, a.max, a.listar, a.rps)
    else:
        ap.error("informe --de e --ate, --lei-organica ou --despejar")
