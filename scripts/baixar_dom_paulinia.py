"""Paulínia (SP) — leis e decretos recortados das edições do Diário Oficial do Município.

Fonte: o portal da Prefeitura (`www.paulinia.sp.gov.br/portal/diario-oficial`), que publica as edições em PDF nascido
digital, lista todas em dados abertos (`/portal/dados-abertos/diario-oficial/<ano>`) e cujo `robots.txt` libera a
coleta. É a publicação oficial dos atos, com as leis e os decretos do Executivo.

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
def palavras_da_edicao(pdf):
    """{página: (largura, altura, [(x0, y0, x1, y1, palavra)])}, numa só chamada do `pdftotext -bbox`."""
    saida = subprocess.run(["pdftotext", "-q", "-bbox", str(pdf), "-"], capture_output=True, timeout=900).stdout
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


TITULO_EDICAO = re.compile(r"Di[áa]rio\s+Oficial\s*-\s*Ano\s+[IVXLC]+\s*-\s*Edi[çc][ãa]o", re.I)
RODAPE = re.compile(r"Di[áa]rio\s+Oficial\s*\|.*Edi[çc][ãa]o", re.I)


NUMERO_DA_EDICAO = re.compile(rf"Edi[çc][ãa]o\s+(\d[\d.]*)\s*(?:[-|]\s*(?:Paul[íi]nia,\s*)?(\d{{1,2}})\s+de\s+({_MES})\s+de\s+(\d{{4}}))?", re.I)


def edicao_impressa(paginas):
    """(número, data ISO ou None) que a própria edição imprime no título da primeira página ou no rodapé corrido;
    (None, None) quando nenhuma linha traz o número. Confere que o PDF baixado é o da edição pedida."""
    for _, (_, altura, palavras) in sorted(paginas.items()):
        for _, _, texto in linhas_da_pagina(palavras):
            if TITULO_EDICAO.search(texto) or RODAPE.search(texto):
                m = NUMERO_DA_EDICAO.search(texto)
                if m:
                    data = data_iso(m.group(2), m.group(3), m.group(4)) if m.group(2) else None
                    return m.group(1).replace(".", ""), data
    return None, None


def mancha(altura, palavras):
    """(topo, base) da área de texto da página, medida nas palavras: abaixo da linha do título da edição (primeira
    página) e acima do expediente ou do rodapé corrido."""
    topo, base = float(TOPO), altura
    for y0, y1, texto in linhas_da_pagina(palavras):
        if y0 < altura * 0.35 and TITULO_EDICAO.search(texto):
            topo = max(topo, y1 + 1)
        elif y0 > altura * 0.6 and (RODAPE.search(texto) or texto.lstrip().startswith("Expediente:")):
            base = min(base, y0 - 1)
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


def fluxo_do_pdf(pdf):
    """Letras e dígitos da edição na ordem do fluxo do PDF (`pdftotext -raw`), sem o rodapé corrido e o expediente:
    uma segunda leitura, independente da geometria, para confrontar com o recorte."""
    bruto = subprocess.run(["pdftotext", "-q", "-raw", "-enc", "UTF-8", str(pdf), "-"], capture_output=True, timeout=900).stdout
    texto = re.sub(r"Di[áa]rio[ \t]+Oficial[ \t]*\|[^\n]*Edi[çc][ãa]o[^\n]*", "", bruto.decode("utf-8", "replace").replace("\f", "\n"))
    return so_letras("\n".join(ln for ln in texto.split("\n") if not ln.startswith("Expediente:")))


def diverge_do_fluxo(corpo, fluxo):
    """Motivo quando algum parágrafo de prosa do corpo não existe, com as mesmas letras e dígitos em sequência, no
    fluxo do PDF. Quadros (blocos pré-formatados) ficam de fora: neles vale o alinhamento, não a ordem de leitura."""
    prosa = re.sub(r"```text\n.*?\n```", "", corpo, flags=re.S)
    ausentes = []
    for paragrafo in prosa.split("\n\n"):
        letras = so_letras(re.sub(r"\\([*_])", r"\1", paragrafo).replace("**", "").lstrip("#"))
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
        self._fluxo = None

    def fluxo(self):
        if self._fluxo is None:
            self._fluxo = fluxo_do_pdf(self.pdf)
        return self._fluxo

    def trechos(self):
        """[(página, texto)] da edição inteira."""
        saida = []
        for n, (largura, altura, palavras) in sorted(self.paginas.items()):
            topo, base = mancha(altura, palavras)
            caixas = [p[:4] for p in palavras if p[1] >= topo]
            for regiao in dom.zonas_da_pagina(largura, altura, caixas, topo, base):
                texto = sem_carimbo(dom.texto_da_regiao(self.pdf, n, *regiao)).rstrip()
                if texto.strip():
                    saida.append((n, texto))
        return saida


# ------------------------------------------------------------------------------------------ recorte dos atos
EPIGRAFE = re.compile(
    r"^[ \t]*(LEI COMPLEMENTAR|LEI|DECRETO LEGISLATIVO|DECRETO|EMENDA À LEI ORGÂNICA)[ \t]+N[º°o.]*[ \t]*(\d[\d.]*)[ \t]*,?[ \t]*DE[ \t]+(\d{1,2})[ \t]*[º°o]?"
    rf"[ \t]+DE[ \t]+((?i:{_MES}))[ \t]+DE[ \t]+(\d\.?\d{{3}})[ \t]*\.?[ \t]*$", re.M)
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


def fim_das_assinaturas(trecho, inicio):
    """Posição em que termina o bloco de assinaturas que começa em `inicio` (fim da linha do signatário): pares de nome
    e cargo, cargos avulsos e a nota de lavratura, que pode ocupar até três linhas (com quebra de coluna no meio) e
    termina em ponto. Nome sem cargo reconhecido na linha seguinte não entra: pode ser o título de outra publicação."""
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


def atos_da_edicao(trechos, data_edicao):
    """[(ato, recorte ou None, motivo ou None)] das leis e decretos da edição. `ato` traz chave, tipo_na_fonte, numero,
    data, pagina e epigrafe; o recorte vai da epígrafe ao fim do bloco de assinaturas."""
    texto, paginas, pos = "", [], 0
    for n, t in trechos:
        paginas.append((pos, n))
        texto += t + "\n\n"
        pos = len(texto)
    achados = []
    for m in EPIGRAFE.finditer(texto):
        chave, tipo_na_fonte = TIPOS[m.group(1)]
        achados.append((m, {"chave": chave, "tipo_na_fonte": tipo_na_fonte, "numero": m.group(2).replace(".", "").lstrip("0") or "0",
                            "data": data_iso(m.group(3), m.group(4), m.group(5)),
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
        saida.append((ato, *recortar(trecho, ato)))
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


def recortar(trecho, ato):
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
    fechos = [f for f in FECHO.finditer(trecho, artigo.end(), signatario.start())]
    if fechos:
        data_fecho = data_iso(*fechos[-1].groups())
        if data_fecho != ato["data"]:
            return None, f"data do fecho ({data_fecho}) difere da data da epígrafe ({ato['data']})"
    fim = fim_das_assinaturas(trecho, signatario.end())
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
def titulo_de(ato):
    ano, mes, dia = (int(x) for x in ato["data"].split("-"))
    numero = f"{int(ato['numero']):,}".replace(",", ".")
    return f"{ato['tipo_na_fonte']} nº {numero}, de {'1º' if dia == 1 else dia} de {NOME_MES[mes]} de {ano}"


def destino_de(ato, edicao):
    pasta, _ = CANONICO[ato["chave"]]
    nome = slugify(f"{ato['chave']}-{ato['numero']}-{ato['data'][:4]}-dom-{edicao['edicao']}")
    return DESTINO / pasta / ato["data"][:4] / (nome + ".md")


def ementa_de(corpo):
    """A ementa, quando o parágrafo que segue a epígrafe (e a nota do projeto) vem entre aspas ou em maiúsculas."""
    paragrafos = [p for p in corpo.split("\n\n") if p.strip()][1:4]
    for p in paragrafos:
        limpo = re.sub(r"\\([*_])", r"\1", p.strip())
        if limpo.startswith("(") and limpo.endswith(")"):
            continue  # "(Projeto de Lei Nº 127/2026 de autoria do Ver. ...)"
        sem_aspas = limpo.strip("“”\"' ")
        if limpo[:1] in "“\"" or (re.search(r"[A-ZÀ-Ú]", limpo) and not re.search(r"[a-zà-ú]", limpo)):
            return " ".join(sem_aspas.split())
        return ""
    return ""


def montar_md(ato, edicao, corpo, tem_quadro, sha_pdf, hoje):
    _, tipo = CANONICO[ato["chave"]]
    titulo = titulo_de(ato)
    notas = [NOTA_DOM] + ([dom.NOTA_QUADRO] if tem_quadro else [])
    dia = dt.date.fromisoformat(edicao["data"]).strftime("%d/%m/%Y")
    meta = [("titulo", titulo), ("tipo", tipo), ("tipo_na_fonte", ato["tipo_na_fonte"]), ("numero", ato["numero"]),
            ("data", ato["data"]), ("municipio", MUNICIPIO), ("uf", UF), ("codigo_ibge", CODIGO_IBGE)]
    ementa = ementa_de(corpo)
    if ementa:
        meta.append(("ementa", ementa))
    meta += [("versao_texto", "texto original (não consolidado); " + "; ".join(notas)),
             ("publicacao", f"Diário Oficial do Município de Paulínia, edição nº {edicao['edicao']}, de {dia}, p. {ato['pagina']}"),
             ("data_publicacao", edicao["data"]),
             ("fonte", f"{BASE}/portal/diario-oficial/ver/{edicao['id']}"),
             ("fonte_texto", edicao["pdf"]),
             ("sha256_fonte", sha_pdf),
             ("sha256_texto", hashlib.sha256(corpo.encode("utf-8")).hexdigest()),
             ("baixado_em", hoje.isoformat())]
    return "---\n" + "\n".join(f"{k}: {yaml_str(v)}" for k, v in meta) + f"\n---\n\n# {titulo}\n\n{corpo}\n"


# ------------------------------------------------------------------------------------------ edições e execução
ITEM = '<div class="dof_publicacao_diario sw_item_listagem">'
MODELO = (722.8, 841.9)  # pt: página do leiaute de duas colunas conferido; outro formato não é lido


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


def baixar_pdf(rede, edicao):
    """(endereço do PDF, arquivo em cache). O link de download responde com um redirecionamento em HTML para /uploads."""
    FONTE.mkdir(parents=True, exist_ok=True)
    em_cache = sorted(FONTE.glob(f"{edicao['id']}-*.pdf"))
    if em_cache and edicao.get("pdf"):
        return edicao["pdf"], em_cache[0]
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


def fora_do_modelo(paginas):
    """Motivo quando alguma página não tem o formato do leiaute conferido."""
    for n, (largura, altura, _) in sorted(paginas.items()):
        if abs(largura - MODELO[0]) > 3 or abs(altura - MODELO[1]) > 3:
            return f"página {n} de {largura:.0f} x {altura:.0f} pt, fora do leiaute de duas colunas conferido"
    return None


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


def executar(de, ate, maximo=0, listar=False, rps=0.5):
    rede = Rede(rps=rps, headers={"Accept-Language": "pt-BR"})
    CACHE.mkdir(parents=True, exist_ok=True)
    arquivo_cache = CACHE / "edicoes.json"
    cache = json.loads(arquivo_cache.read_text(encoding="utf-8")) if arquivo_cache.exists() else {}
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
        falhas = [f for f in falhas if f["edicao"] != edicao["edicao"]]
        try:
            edicao["pdf"], pdf = baixar_pdf(rede, edicao)
            cache[edicao["id"]] = {"edicao": edicao["edicao"], "data": edicao["data"], "pdf": edicao["pdf"]}
            leitura = Edicao(pdf)
            numero, data_impressa = edicao_impressa(leitura.paginas)
            if numero != edicao["edicao"]:
                raise RuntimeError(f"o PDF baixado traz a edição {numero or 'sem número'}, não a {edicao['edicao']}")
            motivo = fora_do_modelo(leitura.paginas)
            if motivo:
                raise RuntimeError(motivo)
            if data_impressa:
                edicao["data"] = data_impressa  # a data impressa na edição vale mais que a de postagem no portal
                cache[edicao["id"]]["data"] = data_impressa
            atos = atos_da_edicao(leitura.trechos(), edicao["data"])
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
                motivo = diverge_do_fluxo(corpo, leitura.fluxo())
            if not motivo and chave in ja and ja[chave] != destino:
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
    a = ap.parse_args()
    if a.despejar:
        for pagina, texto in Edicao(a.despejar).trechos():
            print(f"\n=== página {pagina}\n{texto}")
    elif a.lei_organica:
        print(lei_organica(Rede(rps=a.rps), dt.date.today()))
    elif a.de and a.ate:
        executar(a.de, a.ate, a.max, a.listar, a.rps)
    else:
        ap.error("informe --de e --ate, --lei-organica ou --despejar")
