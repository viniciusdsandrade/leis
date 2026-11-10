"""Decretos de Campinas/SP sem texto no SAPL nem no bibjuri, recortados da edição do Diário Oficial do Município.

Alvos: fichas de decreto do SAPL sem texto integral, ainda sem .md, cuja página no bibjuri (já em cache, gravada por
baixar_bibjuri_campinas.py) não transcreve o ato e aponta "TEXTO INTEGRAL" para o PDF da edição do DOM no portal da
Prefeitura. O vínculo entre a ficha e a edição vem, portanto, da própria Prefeitura.

Leitura: o PDF do DOM é nascido digital, em duas colunas, com faixas de largura total (cabeçalho, quadros largos).
O texto corrido do pdftotext mistura as colunas (-layout) ou, em ordem de leitura, às vezes intercala blocos de outros
atos. Por isso a leitura segue a geometria: em cada página, as faixas cujas palavras cruzam a calha são lidas
inteiras e, entre elas, a coluna esquerda antes da direita, cada região com `pdftotext -layout` recortado, o que
mantém o alinhamento dos quadros. O cabeçalho corrido (acima de TOPO) sai.

Recorte: da epígrafe com o número e a data da ficha até o bloco de assinaturas (Prefeito, secretários e a nota de
publicação, até a linha do Chefe de Gabinete). Travas: epígrafe única na edição; as travas de identidade, integridade
e ementa de baixar_bibjuri_campinas.py; nenhum trecho de licitação, extrato ou aviso intercalado; recorte de tamanho
plausível. Quadros (linhas com colunas alinhadas) entram como texto pré-formatado. O que falha fica em
municipais/_indice/dom-campinas/retidos.json, com o motivo.

    python3 -I scripts/baixar_dom_campinas.py --de 2023 --ate 2026 [--listar] [--max N] [--rps 0.5]
"""
import argparse
import datetime as dt
import hashlib
import html
import re
import subprocess
import sys
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import baixar_bibjuri_campinas as bib  # noqa: E402
from comum import decodificar, texto_pdf_para_md, yaml_str  # noqa: E402

CACHE = bib.RAIZ / "_indice/dom-campinas"
FONTE = bib.RAIZ / "_fonte/dom-campinas"
HOST_DOM = "portal-adm.campinas.sp.gov.br"
LINK_DOM = re.compile(
    r'href=["\'](https?://portal-(?:api|adm)\.campinas\.sp\.gov\.br/+sites/default/files/publicacoes-dom/[^"\']+?\.pdf)["\']', re.I)
TOPO = 40  # pt: acima fica o cabeçalho corrido (data, título do DOM e número da página)
FAIXA_MINIMA = 30  # pt: zona de duas colunas mais baixa que isto, entre faixas cheias, é lida inteira (linha de quadro)
TAMANHO_MAXIMO = 120_000
NOTA_DOM = ("recortado da edição do Diário Oficial do Município (PDF do portal da Prefeitura de Campinas), lida coluna a "
            "coluna; não substitui a publicação oficial")
NOTA_QUADRO = "quadros preservados como texto pré-formatado, no alinhamento do PDF"
MES_RX = {1: "JANEIRO", 2: "FEVEREIRO", 3: "MAR[ÇC]O", 4: "ABRIL", 5: "MAIO", 6: "JUNHO", 7: "JULHO", 8: "AGOSTO",
          9: "SETEMBRO", 10: "OUTUBRO", 11: "NOVEMBRO", 12: "DEZEMBRO"}
PROXIMO_DECRETO = re.compile(r"^[ \t]*DECRETO\s+N[º°o.]?\s*\d", re.M)
PREFEITO = re.compile(r"^[ \t]*(?:VICE-)?PREFEIT[OA](?:\s+MUNICIPAL)?(?:\s+DE\s+CAMPINAS)?(?:\s+EM\s+EXERC[ÍI]CIO)?[ \t]*$",
                      re.M | re.I)
CHEFE_GABINETE = re.compile(r"^[^\n]*Chefe\s+de\s+Gabinete\s+do\s+Prefeito[^\n]*$", re.M | re.I)
# nome em maiúsculas ou cargo de quem referenda o ato; cabeçalho de seção (SECRETARIA..., GABINETE...) não é assinatura
ASSINATURA = re.compile(
    r"^[ \t]*(?:(?!SECRETARIA|GABINETE|COORDENADORIA|DEPARTAMENTO|ATOS?\b|EXPEDIENTE|FUNDA[ÇC][ÃA]O|EMPRESA|INSTITUTO|"
    r"CONSELHO|COMISS|AUTARQUIA|SERVI[ÇC]O|DECRETO|LEI\b|PORTARIA|RESOLU)[A-ZÀ-Ú][A-ZÀ-Ú'. -]{3,70}|"
    r"(?:Secret[áa]ri[oa]|Procurador|Diretor|Respondendo|Prefeit)[^\n]{0,90})[ \t]*$")
INTERCALADO = re.compile(
    r"^[ \t]*(?:Preg[ãa]o\s+(?:n|eletr)|Processo\s+Administrativo\s*:|Interessad[oa]\s*:|Objeto\s*:|AVISO\s+DE\s+LICITA|"
    r"EXTRATO\s+D|EDITAL\s+D|ADJUDICA[ÇC][ÃA]O|HOMOLOGA[ÇC][ÃA]O|COMUNICADO\b|PORTARIA\b)", re.M | re.I)
TABULAR = re.compile(r"\S {3,}\S.*\S {3,}\S")
_MES = r"(?:janeiro|fevereiro|mar[çc]o|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)"
_DIA_SEMANA = r"(?:segunda|ter[çc]a|quarta|quinta|sexta)-feira"
# cabeçalho e rodapé corridos que caem dentro das regiões (modelos de 2011 e 2012 em papel ofício): só linhas inteiras
CROMO = re.compile(
    r"(?:\d{1,3}\s+)?Di[áa]rio\s+Oficial\s+do\s+Munic[íi]pio\s+de\s+Campinas(?:\s+\d{1,3})?|"
    rf"(?:\d{{1,3}}\s+)?(?:Campinas,\s*)?{_DIA_SEMANA},\s*\d{{1,2}}\s+de\s+{_MES}\s+de\s+\d{{4}}(?:\s+\d{{1,3}})?|"
    rf"(?:Campinas,\s*)?{_DIA_SEMANA},\s*\d{{1,2}}(?:\s+de)?|"
    rf"(?:{_MES}\s+de\s+\d{{4}}\s+)?(?:https?://)?www\.campinas\.sp\.gov\.br/?", re.I)
DISPOSITIVO = re.compile(r"(?:Artigo|Art\.)\s*(?:\d|único)|§\s*\d|Parágrafo único|[IVXLC]+\s*[-–—]\s|[a-z]\)\s", re.I)
EPIGRAFE_DECRETO = re.compile(r"DECRETO\s+N[º°o.]?\s*\d")
CONTINUA = re.compile(r"(?:\b(?:a|o|ao|de|da|do|das|dos|e|em|no|na|nos|nas|com|pela|pelo|nº|n°|R\$|Lei|Decreto|Artigo|art\.)|,)$", re.I)


# ------------------------------------------------------------------------------------------ geometria da edição
def palavras_por_pagina(pdf):
    """{página: (largura, altura, [(x0, y0, x1, y1)], palavras em sequência)}, numa só chamada do `pdftotext -bbox`."""
    saida = subprocess.run(["pdftotext", "-q", "-bbox", str(pdf), "-"], capture_output=True, timeout=600).stdout
    saida = saida.decode("utf-8", "replace")
    paginas = {}
    for n, m in enumerate(re.finditer(r'<page width="([\d.]+)" height="([\d.]+)">(.*?)</page>', saida, re.S), 1):
        palavras = re.findall(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</word>', m.group(3))
        caixas = [tuple(map(float, c[:4])) for c in palavras]
        paginas[n] = (float(m.group(1)), float(m.group(2)), caixas, " ".join(html.unescape(c[4]) for c in palavras))
    return paginas


def calha(largura, caixas):
    """x da calha: entre 40% e 60% da largura, o ponto coberto pelo menor número de palavras (mais perto do centro no
    empate). None quando nenhum ponto fica quase livre, isto é, a página não tem duas colunas."""
    corpo = [c for c in caixas if c[1] >= TOPO]
    if not corpo:
        return None
    melhor = None
    for x in range(int(largura * 0.4), int(largura * 0.6) + 1):
        n = sum(1 for x0, _, x1, _ in corpo if x0 < x < x1)
        chave = (n, abs(x - largura / 2))
        if melhor is None or chave < melhor[0]:
            melhor = (chave, x)
    n, _ = melhor[0]
    linhas = len({round(c[1]) for c in corpo})
    return None if n > max(8, linhas * 0.3) else float(melhor[1])


def zonas_da_pagina(largura, altura, caixas):
    """Regiões da página na ordem de leitura: [(x, y, w, h)]. Faixas que cruzam a calha são lidas inteiras; entre
    elas, a coluna esquerda e depois a direita."""
    g = calha(largura, caixas)
    if g is None:
        return [(0.0, float(TOPO), largura, altura - TOPO)]
    cruzam = sorted((y0, y1) for x0, y0, x1, y1 in caixas if y0 >= TOPO and x0 < g - 1 and x1 > g + 1)
    faixas = []
    for y0, y1 in cruzam:
        if faixas and y0 <= faixas[-1][1] + 6:
            faixas[-1][1] = max(faixas[-1][1], y1)
        else:
            faixas.append([y0, y1])
    zonas, y = [], float(TOPO)
    for y0, y1 in faixas:
        if y0 - 1 > y:
            zonas.append(["colunas", y, y0 - 1])
        zonas.append(["cheia", max(y, y0 - 1), y1 + 1])
        y = y1 + 1
    if altura > y:
        zonas.append(["colunas", y, altura])
    # zona curta de duas colunas presa entre faixas cheias é linha de quadro sem célula na calha: lê-se inteira
    for i, z in enumerate(zonas):
        if z[0] == "colunas" and z[2] - z[1] < FAIXA_MINIMA and 0 < i < len(zonas) - 1 \
                and zonas[i - 1][0] == "cheia" and zonas[i + 1][0] == "cheia":
            z[0] = "cheia"
    fundidas = []
    for z in zonas:
        if fundidas and z[0] == "cheia" and fundidas[-1][0] == "cheia":
            fundidas[-1][2] = z[2]
        else:
            fundidas.append(list(z))
    regioes = []
    for tipo, y0, y1 in fundidas:
        if y1 - y0 <= 0:
            continue
        if tipo == "cheia":
            regioes.append((0.0, y0, largura, y1 - y0))
        else:
            regioes += [(0.0, y0, g, y1 - y0), (g, y0, largura - g, y1 - y0)]
    return regioes


def texto_da_regiao(pdf, pagina, x, y, w, h):
    args = ["pdftotext", "-q", "-layout", "-enc", "UTF-8", "-f", str(pagina), "-l", str(pagina),
            "-x", str(int(x)), "-y", str(int(y)), "-W", str(int(w + 0.999)), "-H", str(int(h + 0.999)), str(pdf), "-"]
    return subprocess.run(args, capture_output=True, timeout=300).stdout.decode("utf-8", "replace")


def sem_cromo(texto):
    """Tira as linhas que são inteiras cabeçalho ou rodapé corrido do DOM."""
    return "\n".join(ln for ln in texto.split("\n") if not CROMO.fullmatch(re.sub(r"\s+", " ", ln.strip())))


class Edicao:
    """Uma edição do DOM: as palavras de todas as páginas (uma leitura) e, sob demanda, o texto de cada página em ordem
    de leitura, região por região: [(página, texto)]."""

    def __init__(self, pdf):
        self.pdf = pdf
        self.paginas = palavras_por_pagina(pdf)
        self._trechos = {}

    def trechos(self, primeira, ultima):
        saida = []
        for n in range(primeira, min(ultima, max(self.paginas)) + 1):
            if n not in self._trechos:
                largura, altura, caixas, _ = self.paginas[n]
                textos = (sem_cromo(texto_da_regiao(self.pdf, n, *r)).rstrip()
                          for r in zonas_da_pagina(largura, altura, caixas))
                self._trechos[n] = [(n, t) for t in textos if t.strip()]
            saida += self._trechos[n]
        return saida

    def paginas_com(self, rx):
        """Páginas cujo texto corrido (palavras em sequência) casa com `rx`, e o total de ocorrências na edição."""
        achadas = {n: len(rx.findall(p[3])) for n, p in self.paginas.items()}
        return sorted(n for n, k in achadas.items() if k), sum(achadas.values())


# ------------------------------------------------------------------------------------------ recorte do ato
def epigrafe_rx(norma):
    numero = int(re.sub(r"\D", "", str(norma["numero"])))
    milhar = f"{numero:,}".replace(",", r"\.?")
    ano, mes, dia = norma["data"].split("-")
    return re.compile(rf"^[ \t]*DECRETO\s+N[º°o.]?\s*{milhar}\s*,?\s+DE\s+0?{int(dia)}\s*[º°]?\s+DE\s+{MES_RX[int(mes)]}\s+DE\s+"
                      rf"{ano[0]}\.?{ano[1:]}\b", re.M | re.I)


def epigrafe_solta(norma):
    """A epígrafe no texto corrido das palavras do -bbox, sem âncora de linha: localiza a página e conta repetições."""
    return re.compile(epigrafe_rx(norma).pattern.replace("^[ \\t]*", ""), re.I)


def recortar(trechos, norma):
    """(texto do ato, página, motivo): o ato da ficha, da epígrafe ao bloco de assinaturas."""
    texto, paginas, pos = "", [], 0
    for n, t in trechos:
        paginas.append((pos, n))
        texto += t + "\n\n"
        pos = len(texto)
    achados = list(epigrafe_rx(norma).finditer(texto))
    if not achados:
        return None, None, "epígrafe com o número e a data da ficha ausente da edição do DOM"
    if len(achados) > 1:
        return None, None, "epígrafe repetida na edição do DOM (republicação ou retificação)"
    inicio = achados[0].start()
    pagina = max(n for p, n in paginas if p <= inicio)
    prox = PROXIMO_DECRETO.search(texto, achados[0].end())
    limite = prox.start() if prox else len(texto)
    trecho = texto[inicio:limite]
    artigo = bib.ARTIGO.search(trecho)
    pref = PREFEITO.search(trecho, artigo.end()) if artigo else None
    if not pref:
        return None, pagina, "sem a assinatura do Prefeito antes do próximo ato da edição"
    fim = pref.end()
    chefe = CHEFE_GABINETE.search(trecho, fim)
    if chefe and chefe.start() - fim < 2500:
        fim = chefe.end()
    else:
        # nomes e cargos que seguem a assinatura do Prefeito (secretários que referendam o ato)
        for linha in re.finditer(r"[^\n]*\n?", trecho[fim:]):
            conteudo = linha.group(0).strip()
            if linha.end() == linha.start() or (conteudo and not ASSINATURA.match(conteudo)):
                break
            fim += len(linha.group(0))
            if fim - pref.end() > 900:
                break
    # anexo do próprio decreto publicado depois das assinaturas: o limite do anexo não é seguro; retém
    if re.search(r"^[ \t]*ANEXO\b", trecho[fim:fim + 2000], re.M | re.I) and re.search(r"\banexo\b", trecho[:fim], re.I):
        return None, pagina, "anexo do decreto publicado depois das assinaturas; o recorte do anexo não está implementado"
    return trecho[:fim].strip("\n") + "\n", pagina, None


def so_maiusculas(texto):
    return bool(re.search(r"[A-ZÀ-Ú]", texto)) and not re.search(r"[a-zà-ú]", texto)


def fecha_paragrafo(linha, seguinte, medida, largura):
    """A linha `linha` (sem recuo; `medida` conta o recuo do PDF) encerra o parágrafo? Só linha curta pode encerrar, e nunca a que termina em
    hífen. Encerra quando termina em pontuação final, quando a seguinte abre com número ou §, quando uma das duas está
    toda em maiúsculas (nome de assinatura, epígrafe) ou quando é bem curta e a seguinte abre com maiúscula."""
    if seguinte is None:
        return True
    if linha.endswith("-"):
        return False
    if EPIGRAFE_DECRETO.match(linha) or (DISPOSITIVO.match(seguinte) and not CONTINUA.search(linha)):
        return True  # artigo, parágrafo ou inciso abre parágrafo mesmo depois de linha cheia (pontilhado de valor)
    caixa_alta, seguinte_alta = so_maiusculas(linha), so_maiusculas(seguinte)
    if caixa_alta != seguinte_alta:
        return True  # nome de quem assina e cargo; epígrafe ou ementa em maiúsculas e o texto
    if medida >= largura * 0.8:
        return False
    if re.search(r"[.:;!?)]$", linha):
        return True
    if re.match(r"[\d§\"“]", seguinte) and not CONTINUA.search(linha):
        return True  # item de classificação ou de lista; "de dezembro de" + "2010." continua
    if caixa_alta:
        return medida < largura * 0.6  # rótulo em maiúsculas que quebrou de linha continua
    return medida < largura * 0.6 and seguinte[:1].isupper()


def paragrafos(linhas):
    """Parágrafos do texto justificado de uma coluna, com a palavra partida no fim da linha rejuntada."""
    uteis, medidas, em_branco_depois = [], [], []
    for i, ln in enumerate(linhas):
        if ln.strip():
            uteis.append(ln.strip())
            medidas.append(len(ln.rstrip()))
            em_branco_depois.append(i + 1 < len(linhas) and not linhas[i + 1].strip())
    if not uteis:
        return []
    largura = max(medidas)
    saida, atual = [], ""
    for i, texto in enumerate(uteis):
        seguinte = uteis[i + 1] if i + 1 < len(uteis) else None
        if em_branco_depois[i] and not texto.endswith("-"):
            seguinte = None  # linha em branco no PDF separa parágrafos (ou regiões da página)
        if not atual:
            atual = texto
        elif re.search(r"[A-Za-zÀ-ú]-$", atual) and re.match(r"[A-Za-zÀ-ú]", texto) \
                and atual[-2].islower() == texto[0].islower():
            atual = atual[:-1] + texto  # "SUPLEMEN-" + "TAR", "Mu-" + "nicipal"
        elif atual.endswith("-") and texto.startswith("-"):
            atual = atual + texto[1:]  # "Orçamento-" + "-Programa"
        else:
            atual += " " + texto
        if seguinte is None or fecha_paragrafo(texto, seguinte, medidas[i], largura):
            saida.append(atual)
            atual = ""
    if atual:
        saida.append(atual)
    return saida


def zonas_de_quadro(linhas):
    """Faixas [i, j) de linhas que formam um quadro: partem das linhas com colunas alinhadas e se estendem, para cima e
    para baixo, sobre linhas em branco e linhas recuadas (célula que quebrou de linha, valor sozinho na linha); param na
    linha de prosa, que no recorte da coluna começa na margem. Quadro precisa de duas linhas alinhadas ou mais."""
    def recuada(ln):
        # em branco, recuada ou com um espaçamento largo entre duas células (cabeçalho de colunas que quebrou de linha)
        if not ln.strip():
            return True
        if DISPOSITIVO.match(ln.strip()):
            return False
        return len(ln) - len(ln.lstrip()) >= 2 or bool(re.search(r"\S {3,}\S", ln))
    zonas = []
    for i, ln in enumerate(linhas):
        if not TABULAR.search(ln) or (zonas and i < zonas[-1][1]):
            continue
        a, b = i, i + 1
        while a > 0 and recuada(linhas[a - 1]):
            a -= 1
        while b < len(linhas) and (recuada(linhas[b]) or TABULAR.search(linhas[b])):
            b += 1
        while a < i and not linhas[a].strip():
            a += 1
        while b > i + 1 and not linhas[b - 1].strip():
            b -= 1
        if sum(1 for ln in linhas[a:b] if TABULAR.search(ln)) >= 2:
            zonas.append((a, b))
    return zonas


def para_md(texto):
    """Markdown do recorte: parágrafos reconstruídos pelo comprimento das linhas e formatados pelo conversor de PDF do
    acervo; quadros em bloco pré-formatado, no alinhamento do PDF. Devolve (corpo, tem_quadro)."""
    linhas = texto.split("\n")
    partes, i = [], 0
    def prosa(trecho):
        paras = paragrafos(trecho)
        if paras:
            md = texto_pdf_para_md("\n\n".join(paras)).strip()
            # "Artigo 2º -" ganha o mesmo destaque que "Art. 2º" recebe no conversor
            md = re.sub(r"(?m)^(Artigo \d+[ºo°]?(?:-[A-Z])?|Artigo único|Parágrafo único)(?=\s*[-–—.:])", r"**\1**", md)
            partes.append(md)
    zonas = zonas_de_quadro(linhas)
    for a, b in zonas:
        prosa(linhas[i:a])
        quadro = [ln.rstrip() for ln in linhas[a:b]]
        recuo = min(len(ln) - len(ln.lstrip()) for ln in quadro if ln.strip())
        partes.append("```text\n" + "\n".join(ln[recuo:] for ln in quadro) + "\n```")
        i = b
    prosa(linhas[i:])
    return "\n\n".join(partes), bool(zonas)  # sem a quebra final, como o corpo do bibjuri


def avaliar(edicao, norma, info):
    """(motivo ou None, corpo, página, tem_quadro). Lê só a página da epígrafe e as seguintes, até o fim do ato."""
    paginas, ocorrencias = edicao.paginas_com(epigrafe_solta(norma))
    if not paginas:
        numero = f"{int(re.sub(r'[^0-9]', '', str(norma['numero']))):,}".replace(",", r"\.?")
        outra_data = re.compile(rf"DECRETO\s+N[º°o.]?\s*{numero}\s*,?\s+DE\s+(\d{{1,2}}\s*[º°]?\s+DE\s+\w+\s+DE\s+\d\.?\d{{3}})", re.I)
        for _, (_, _, _, texto) in sorted(edicao.paginas.items()):
            m = outra_data.search(texto)
            if m:
                return (f"data da epígrafe no DOM ({m.group(1).lower()}) difere da ficha do SAPL ({norma['data']})",
                        None, None, False)
        return "epígrafe com o número e a data da ficha ausente da edição do DOM", None, None, False
    if ocorrencias > 1:
        return "epígrafe repetida na edição do DOM (republicação ou retificação)", None, paginas[0], False
    recorte = None
    for alcance in (2, 8):
        recorte, pagina, motivo = recortar(edicao.trechos(paginas[0], paginas[0] + alcance), norma)
        if not motivo or not motivo.startswith("sem a assinatura"):
            break
    if motivo:
        return motivo, None, pagina, False
    if len(recorte) > TAMANHO_MAXIMO:
        return f"recorte longo demais ({len(recorte)} caracteres) para um decreto; conferir os limites do ato", None, pagina, False
    m = INTERCALADO.search(recorte)
    if m:
        return "trecho de outra publicação intercalado no recorte: " + m.group(0).strip()[:80], None, pagina, False
    corpo, tem_quadro = para_md(recorte)
    motivo = bib.identidade(corpo, norma, info) or bib.integridade(corpo, norma, info) or bib.ementa_diverge(corpo, norma)
    return motivo, corpo, pagina, tem_quadro


# ------------------------------------------------------------------------------------------ alvos e gravação
def url_canonica(href):
    """O bibjuri aponta portal-api, que redireciona para portal-adm; o .md guarda o endereço final."""
    return f"https://{HOST_DOM}/" + re.sub(r"^/+", "", urllib.parse.urlsplit(href).path)


def link_dom(bloco):
    m = LINK_DOM.search(bloco or "")
    return url_canonica(m.group(1)) if m else None


def publicacao_do_bloco(bloco):
    plano = html.unescape(re.sub(r"<[^>]+>", " ", bloco or ""))
    m = bib.PUBLICACAO.search(plano)
    return ("DOM " + re.sub(r"\s+", " ", m.group("texto")).strip()) if m else ""


def montar_md(norma, info, corpo, url, bruto, publicacao, pagina, tem_quadro, hoje):
    titulo = bib.titulo_de(norma, info)
    notas = [NOTA_DOM] + ([NOTA_QUADRO] if tem_quadro else [])
    meta = [("titulo", titulo), ("tipo", info["tipo"]), ("tipo_na_fonte", bib.rotulo_sapl(norma, info, "tipo_na_fonte")),
            ("numero", str(norma["numero"])), ("data", norma["data"]), *bib.IDENTIDADE,
            ("versao_texto", "texto original (não consolidado); " + "; ".join(notas)),
            ("publicacao", publicacao or (f"DOM, p. {pagina}" if pagina else "")),
            ("fonte", f"https://{bib.HOST_SAPL}/norma/{norma['id']}"),
            ("fonte_texto", url),
            ("sha256_fonte", hashlib.sha256(bruto).hexdigest()),
            ("sha256_texto", hashlib.sha256(corpo.encode("utf-8")).hexdigest()),
            ("baixado_em", hoje.isoformat())]
    return "---\n" + "\n".join(f"{k}: {yaml_str(v)}" for k, v in meta) + f"\n---\n\n# {titulo}\n\n{corpo}\n"


def pdf_em_cache(url):
    return FONTE / url.rsplit("/", 1)[1]


def alvos_do_ano(fonte, info, ano, publicados, retidos_bibjuri):
    """Fichas do ano sem texto no SAPL, sem .md, retidas pelo bibjuri e com link do DOM na página do bibjuri."""
    alvos = []
    for t in info["sapl"]:
        for n in bib.fichas_sapl(fonte, t, ano):
            if n.get("texto_integral") or n["id"] in publicados:
                continue
            reg = retidos_bibjuri.get(str(n["id"])) or {}
            ident = reg.get("bibjuri_id")
            if not isinstance(ident, int):
                continue
            pagina = bib.FONTE / f"{ident}.html"
            if not pagina.exists():
                continue
            bloco = bib.bloco_conteudo(decodificar(pagina.read_bytes(), "text/html; charset=iso-8859-1"))
            url = link_dom(bloco)
            if url:
                alvos.append((n, url, publicacao_do_bloco(bloco)))
    return sorted(alvos, key=lambda a: (a[1], a[0]["id"]))  # uma leitura por edição


def executar(de, ate, maximo=0, listar=False, rps=0.5):
    info = bib.TIPOS["decreto"]
    fonte = bib.Fonte(rps)
    publicados = bib.ids_publicados()
    retidos_bibjuri = bib.ler_json(bib.CACHE / "retidos.json", {})
    retidos = bib.ler_json(CACHE / "retidos.json", {})
    hoje = dt.date.today()
    edicoes, novos_total = {}, 0
    for ano in range(de, ate + 1):
        alvos = alvos_do_ano(fonte, info, ano, publicados, retidos_bibjuri)
        if listar:
            print(f"{ano}: alvos {len(alvos)}, edições {len({u for _, u, _ in alvos})}", flush=True)
            continue
        contagem = {"novo": 0, "com_quadro": 0, "retida": 0, "erro": 0}
        motivos = {}
        for norma, url, publicacao in alvos:
            if maximo and novos_total >= maximo:
                break
            chave = str(norma["id"])
            registro = {"numero": str(norma["numero"]), "data": norma.get("data"), "ano": ano, "dom": url, "em": hoje.isoformat()}
            try:
                if norma.get("data") and norma["data"][:4] != str(norma.get("ano") or norma["data"][:4]):
                    motivo = f"ano do cadastro do SAPL ({norma['ano']}) difere do ano da data da ficha ({norma['data']})"
                    corpo = pagina = None
                    bruto = b""
                else:
                    bruto, _ = fonte.get(url, pdf_em_cache(url))
                    if url not in edicoes:
                        edicoes.clear()  # uma edição por vez na memória; os alvos vêm ordenados por edição
                        edicoes[url] = Edicao(pdf_em_cache(url))
                    motivo, corpo, pagina, tem_quadro = avaliar(edicoes[url], norma, info)
            except Exception as e:  # rede ou PDF inesperado: segue para a próxima ficha
                motivo, corpo = f"erro: {str(e)[:200]}", None
                contagem["erro"] += 1
            if motivo:
                if not motivo.startswith("erro"):
                    contagem["retida"] += 1
                retidos[chave] = {**registro, "motivo": motivo}
                motivos[motivo.split(":")[0][:90]] = motivos.get(motivo.split(":")[0][:90], 0) + 1
                continue
            destino = bib.destino_de(norma, info)
            if destino.exists():
                continue
            bib.escrever(destino, montar_md(norma, info, corpo, url, bruto, publicacao, pagina, tem_quadro, hoje))
            retidos.pop(chave, None)
            publicados.add(norma["id"])
            contagem["novo"] += 1
            contagem["com_quadro"] += int(tem_quadro)
            novos_total += 1
            if sum(contagem.values()) % 25 == 0:
                bib.gravar_json(CACHE / "retidos.json", retidos)
                print(f"  ... {ano}: {contagem}", flush=True)
        bib.gravar_json(CACHE / "retidos.json", retidos)
        print(f"{ano}: alvos {len(alvos)} -> {contagem}" + (f"; motivos {motivos}" if motivos else ""), flush=True)
        if maximo and novos_total >= maximo:
            print(f"limite de {maximo} novas conversões atingido", flush=True)
            break
    return novos_total


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--de", type=int, required=True, help="primeiro ano")
    ap.add_argument("--ate", type=int, required=True, help="último ano, inclusive")
    ap.add_argument("--max", type=int, default=0, help="limita novas conversões; 0 = sem limite")
    ap.add_argument("--listar", action="store_true", help="só conta alvos e edições; não baixa PDFs")
    ap.add_argument("--rps", type=float, default=0.5, help="requisições por segundo por host")
    a = ap.parse_args()
    executar(a.de, a.ate, a.max, a.listar, a.rps)
