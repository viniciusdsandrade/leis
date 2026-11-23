"""Banco Central do Brasil e Conselho Monetário Nacional: os normativos do portal do BC, em Markdown.

Índice: a busca de normativos do portal (`/api/search/app/normativos/buscanormativos`), ordenada por data, 500 linhas
por página: é o teto da API, que devolve 500 mesmo quando se pedem mais. A consulta por tipo casa por frase ("Circular"
também traz as "Carta Circular"), então o tipo exato é filtrado no resultado, e a soma das linhas tem de fechar com o
total que a busca anuncia. O índice fica em reguladores/bcb/_indice/<tipo>.json.

Texto: `/api/conteudo/app/normativos/exibenormativo?p1=<tipo>&p2=<número>`, a versão que o BC mantém no portal, com as
alterações incorporadas e a redação revogada tachada quando houve alteração. O texto antigo vem num <pre> do sistema
anterior (linhas de largura fixa, "RESOLUCAO N. 002682") e passa por `texto_pdf_para_md`, que refaz os parágrafos sem
mexer nas palavras; o atual vem em HTML e passa por `html2md`. Revogação e cancelamento vêm dos campos Revogado e
Cancelado. O campo Documentos lista os PDFs das versões do próprio normativo (`_v1_O.pdf`, `_v2_L.pdf`...), não anexos
à parte.

Retém, com o motivo em reguladores/bcb/_falhas.jsonl: texto só nos PDFs (campo de texto vazio), imagem no texto e
página cujo tipo ou número difere do índice. Pula o que já está no acervo, inclusive o que veio do Diário Oficial da
União desde 2017 (reconhecido pelo título): o mesmo ato não entra duas vezes. Retomável.

Texto só nos PDFs (`--pdf`): refaz os retidos por esse motivo a partir do PDF da versão original (`_v1_O.pdf`), que o
portal serve em /pre/normativos/<série>/<ano>/pdf/. As demais versões ficam em /<site>/Lists/, que o robots.txt
proíbe, e não são baixadas; o texto gravado é o original, sem as alterações posteriores, e o front matter diz isso.
O PDF entra só se o texto vier todo da camada de texto: página com imagem que cobre 10% ou mais da área (anexo,
tabela ou formulário escaneado) retém o normativo, como a imagem no HTML. A espécie e o número no alto do PDF e a
data, quando o PDF a traz junto do número, têm de conferir com o índice e com o portal.

robots.txt de www.bcb.gov.br (conferido em 21/11/2026): permite /api/ e /pre/normativos/; proíbe /*/Lists/. Para na
recusa (HTTP 401, 403 ou 429).

Página em imagem (`--pagina-em-imagem`): refaz os retidos por esse motivo quando o normativo se lê sem ela, isto é, a
primeira página é texto e a página em imagem (o anexo, a tabela ou o formulário escaneado) não tem camada de texto.
Grava o texto das outras páginas, diz no front matter quais páginas ficaram de fora (`paginas_em_imagem`) e anota o
arquivo em reguladores/bcb/_paginas_em_imagem.jsonl, de onde ele vai para o registro de pendências de integralidade:
o texto fica no acervo e não conta no progresso até o conteúdo da imagem vir de outra fonte ou de OCR revisado.

    python3 -I scripts/baixar_bcb.py --so-indice                       # monta o índice dos tipos
    python3 -I scripts/baixar_bcb.py --tipos Resolução --de 1990 --ate 1999
    python3 -I scripts/baixar_bcb.py --tipos "Resolução CMN,Resolução BCB" --rps 1
    python3 -I scripts/baixar_bcb.py --pdf                             # retidos por texto só nos PDFs
    python3 -I scripts/baixar_bcb.py --pagina-em-imagem                # retidos por página em imagem no PDF
"""
import argparse
import collections
import datetime as dt
import gzip
import hashlib
import html as htmllib
import json
import os
import re
import subprocess
import sys
import tempfile
import unicodedata
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import Rede, gravar, texto_pdf_para_md  # noqa: E402
from html2md import convert  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
PASTA = RAIZ / "reguladores" / "bcb"
INDICE = PASTA / "_indice"
FONTE = RAIZ / "reguladores" / "_fonte" / "bcb"
FALHAS = PASTA / "_falhas.jsonl"
BASE = "https://www.bcb.gov.br"
BUSCA = (BASE + "/api/search/app/normativos/buscanormativos?querytext={q}&rowlimit={n}&startrow={i}"
         "&sortlist=Data1OWSDATE:ascending")
DETALHE = BASE + "/api/conteudo/app/normativos/exibenormativo?p1={tipo}&p2={numero}"
PAGINA = BASE + "/estabilidadefinanceira/exibenormativo?tipo={tipo}&numero={numero}"
POR_PAGINA = 500
VERSAO = ("texto mantido pelo Banco Central do Brasil no portal de normativos, com as alterações incorporadas e a "
          "redação revogada tachada quando houve alteração; não substitui a publicação no Diário Oficial da União")
PDF_ORIGINAL = BASE + "/pre/normativos/{serie}/{ano}/pdf/{arquivo}"
VERSAO_PDF = ("original: PDF da versão original (v1) no portal de normativos do Banco Central do Brasil, sem as "
              "alterações posteriores; não substitui a publicação no Diário Oficial da União")
SO_PDF = "texto só nos PDFs das versões: o campo de texto da API está vazio"
IMAGEM_NO_PDF = "página em imagem no PDF (anexo, tabela ou formulário escaneado): o conteúdo visual não entra no Markdown"

# tipo na fonte -> (pasta, tipo canônico, órgão, prefixo do arquivo). Até 2020 o BC publicava as resoluções do CMN
# como "Resolução"; desde então são "Resolução CMN", na mesma numeração, e o BC tem as suas, "Resolução BCB".
TIPOS = {
    "Resolução": ("resolucoes", "Resolução", "Conselho Monetário Nacional", "res-cmn"),
    "Resolução CMN": ("resolucoes", "Resolução", "Conselho Monetário Nacional", "res-cmn"),
    "Resolução BCB": ("resolucoes", "Resolução", "Banco Central do Brasil", "res-bcb"),
    "Resolução Conjunta": ("resolucoes", "Resolução", "Banco Central do Brasil", "res-conjunta"),
    "Circular": ("circulares", "Circular", "Banco Central do Brasil", "circ"),
    "Carta Circular": ("cartas-circulares", "Carta Circular", "Banco Central do Brasil", "carta-circ"),
    "Instrução Normativa BCB": ("instrucoes-normativas", "Instrução Normativa", "Banco Central do Brasil", "in-bcb"),
}
MESES = ("janeiro fevereiro março abril maio junho julho agosto setembro outubro novembro dezembro").split()
GRAVADO = re.compile(r"^(" + "|".join(sorted({p for *_, p in TIPOS.values()}, key=len, reverse=True))
                     + r")-(\d+)-\d{4}\.md$")


class Recusa(RuntimeError):
    pass


def obter(rede, url):
    try:
        status, dados, _ = rede.get(url, accept="application/json")
    except RuntimeError as e:  # Rede devolve o 403, mas repete o 401 e o 429 e então desiste com a mensagem do HTTP
        if re.search(r"HTTP Error (?:401|429)\b", str(e)):
            raise Recusa(f"a fonte recusou o acesso: {url}") from e
        raise
    if status in (401, 403, 429):
        raise Recusa(f"a fonte recusou o acesso (HTTP {status}): {url}")
    if status != 200 or not dados:
        raise RuntimeError(f"HTTP {status} sem conteúdo: {url}")
    return dados


def sem_acento(texto):
    return "".join(c for c in unicodedata.normalize("NFD", texto) if not unicodedata.combining(c))


def visivel(texto_html):
    texto = htmllib.unescape(re.sub(r"<[^>]+>", " ", texto_html or "")).replace("​", "")
    return re.sub(r"\s+", " ", texto).strip()


def nome_do_indice(tipo):
    return re.sub(r"[^a-z0-9]+", "-", sem_acento(tipo).lower()).strip("-") + ".json"


def montar_indice(rede, tipo, refazer=False):
    """Lista do tipo exato, uma entrada por normativo; confere a soma das páginas com o total anunciado."""
    arq = INDICE / nome_do_indice(tipo)
    if arq.exists() and not refazer:
        return json.loads(arq.read_text(encoding="utf-8"))
    consulta = urllib.parse.quote(
        f'ContentType:normativo AND contentSource:normativos AND TipodoNormativoOWSCHCS:"{tipo}"')
    vistos, itens, total, inicio = set(), {}, None, 0
    while total is None or inicio < total:
        pagina = json.loads(obter(rede, BUSCA.format(q=consulta, n=POR_PAGINA, i=inicio)))
        total = int(pagina.get("TotalRows") or 0)
        linhas = pagina.get("Rows") or []
        if not linhas:
            break
        for r in linhas:
            vistos.add(r["listItemId"])
            if r.get("TipodoNormativoOWSCHCS") != tipo:
                continue
            itens[r["listItemId"]] = {
                "id": r["listItemId"], "tipo": tipo, "numero": int(float(r["NumeroOWSNMBR"])),
                "data": (r.get("data") or "")[:10], "titulo": r.get("title") or "",
                "ementa": " ".join((r.get("AssuntoNormativoOWSMTXT") or "").split()),
            }
        inicio += len(linhas)
    if len(vistos) != total:
        raise RuntimeError(f"índice de {tipo} incompleto: {len(vistos)} linhas para {total} anunciadas")
    lista = sorted(itens.values(), key=lambda x: x["numero"])
    repetidos = [n for n, c in collections.Counter(x["numero"] for x in lista).items() if c > 1]
    if repetidos:
        raise RuntimeError(f"índice de {tipo} com números repetidos: {repetidos[:10]}")
    INDICE.mkdir(parents=True, exist_ok=True)
    arq.write_text(json.dumps(lista, ensure_ascii=False, indent=0) + "\n", encoding="utf-8")
    return lista


def serie_do_titulo(titulo, data):
    """(prefixo, número) de um normativo do BC já no acervo, pelo título ("RESOLUÇÃO Nº 4.549, DE 26 DE ...")."""
    t = re.sub(r"\s+", " ", sem_acento(titulo).upper())
    m = re.match(r"^(CARTA CIRCULAR|CIRCULAR|INSTRUCAO NORMATIVA(?: BCB)?|RESOLUCAO(?: CMN| BCB| CONJUNTA)?)"
                 r"\s+N\s*[.ºO°]*\s*([\d.]+)", t)
    if not m:
        return None
    numero = int(m.group(2).replace(".", "") or -1)
    especie = m.group(1)
    if especie == "CARTA CIRCULAR":
        return ("carta-circ", numero)
    if especie == "CIRCULAR":
        return ("circ", numero)
    if especie.startswith("INSTRUCAO NORMATIVA"):
        return ("in-bcb", numero)
    if especie == "RESOLUCAO CONJUNTA":
        return ("res-conjunta", numero)
    if especie == "RESOLUCAO BCB":
        return ("res-bcb", numero)
    if especie == "RESOLUCAO CMN":
        return ("res-cmn", numero)
    # "Resolução" sem a sigla: a do CMN até 2020; depois, a numeração separa as duas séries (CMN acima de 4.800)
    return ("res-cmn", numero) if (data or "") < "2020-08" or numero >= 4000 else ("res-bcb", numero)


def no_acervo():
    """Normativos do BC já gravados: por este coletor (nome do arquivo) e os demais, como os do DOU (título)."""
    existentes = set()
    for md in PASTA.glob("*/*/*.md"):
        m = GRAVADO.match(md.name)
        if m:
            existentes.add((m.group(1), int(m.group(2))))
            continue
        cabecalho = md.read_text(encoding="utf-8").split("\n---\n", 1)[0]
        titulo = re.search(r'^titulo: "(.*)"$', cabecalho, re.M)
        data = re.search(r"^data: (\d{4}-\d{2}-\d{2})$", cabecalho, re.M)
        serie = serie_do_titulo(json.loads(f'"{titulo.group(1)}"') if titulo else "", data.group(1) if data else "")
        if serie:
            existentes.add(serie)
    return existentes


def data_do_normativo(x):
    """Data do ato pelo DataTexto do portal ("21/12/1999 00:00"), na hora de Brasília."""
    m = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})", x.get("DataTexto") or "")
    if not m:
        return ""
    try:
        return dt.date(int(m.group(3)), int(m.group(2)), int(m.group(1))).isoformat()
    except ValueError:
        return ""


def data_da_publicacao(dou):
    m = re.search(r"\bDOU de (\d{1,2})/(\d{1,2})/(\d{4})", dou or "")
    if not m:
        return ""
    try:
        return dt.date(int(m.group(3)), int(m.group(2)), int(m.group(1))).isoformat()
    except ValueError:
        return ""


def titulo_do_normativo(tipo, numero, data):
    ano, mes, dia = (int(p) for p in data.split("-"))
    dia_txt = "1º" if dia == 1 else str(dia)
    return f"{tipo} nº {numero:,}".replace(",", ".") + f", de {dia_txt} de {MESES[mes - 1]} de {ano}"


# "normativo": a nota do portal "o anexo deste normativo encontra-se à disposição dos interessados na Sede do BC"
_ATO = r"(?:resolucao|circular|carta[ -]circular|instrucao normativa|normativo)"
# O designador ("Anexo II") fica dentro da exceção: opcional fora dela, o motor o deixaria de fora para casar.
# Designadores em lista ("Regulamentos Anexos I, II, III e IV à Resolução nº 1.289"), espécie no plural ("às
# Circulares") e partida na quebra de linha dos textos antigos ("à Resolu- ção"): tudo isso é anexo de outro ato.
_DE_OUTRO = (r"(?!(?:\s+(?:[ivxlc]+|\d+)\b(?:\s*(?:,|e)\s*(?:[ivxlc]+|\d+)\b)*)?,?\s+(?:a|ao|aos|as|da|do|das|dos)\s+"
             r"(?:(?:referid|citad|mencionad)[oa]s?\s+)?"
             r"(?:resolu|circular|carta|instruc|leis?\b|decreto|portaria|medida|comunicado))")
# Remissão a anexo do próprio normativo. A de outro ato ("anexo à Resolução nº 2.309") não conta.
_DESIGNADOR = r"(?:\s+(?:[ivxlc]+|\d+)\b)?"  # "Anexo II", "Anexo 3"
ANEXO_PROPRIO = re.compile(
    r"\banex[oa]s?" + _DESIGNADOR + r"\s+(?:desta|deste|a esta|a este|a presente|ao presente|da presente"
    r"|do presente)\s+" + _ATO
    + r"|\b(?:na forma|nos termos|constantes?|conforme|de acordo com|previst[oa]s? n[oa])\s+(?:d?os?|d?as?)\s+anexos?\b"
    + _DE_OUTRO
    # "folhas anexas" são as do manual que a carta-circular atualiza (MCR, MNI): o conteúdo do ato
    + r"|\b(?:tabela|quadro|modelo|formulario|planilha|relac(?:ao|oes)|regulamento|folha|documento|instruc(?:ao|oes)"
      r"|copia|demonstrativo|mapa|ficha)s?\s+anex[oa]s?\b" + _DE_OUTRO
    + r"|\bem anexo\b(?!\s*(?:a|ao|as|aos)\b)")  # "envio, em anexo à documentação": anexado a outra coisa
REGULAMENTO_DE = re.compile(r"\bregulamento anexo" + _DESIGNADOR + r" (?:a|ao) " + _ATO + r" n[º°o.]*\s*([\d.]+)")
SECAO_DE_ANEXO = re.compile(r"(?m)^(?:#+\s*)?(?:\*\*)?\s*(?:anexos?|regulamento anexo|regulamento a que se refere)\b")
FECHO_BRASILIA = re.compile(r"(?m)^brasilia\s*(?:\(df\)|[-/]\s*df)?,?\s+(?:em\s+)?\d{1,2}[º°o]?\s+de\s+[a-z]+\s+de\s+\d{4}\b"
                            r".*$")
TRACOS = re.compile(r"[‐‑‒–—]")  # "CARTA–CIRCULAR", com travessão, nos PDFs
# Folhas do manual (MNI, MCR, MCA) que a carta-circular atualiza, quando vêm no próprio PDF, depois da carta: os
# cabeçalhos "TÍTULO: CAIXAS ECONÔMICAS – 11", "CAPÍTULO: ...", "SEÇÃO: ..." e o rodapé "At. MNI nº 728". A conversão
# para Markdown tira o cabeçalho que se repete nas páginas; por isso a marca é procurada no texto do PDF.
FOLHAS_DE_MANUAL = re.compile(r"(?m)^\s*(?:#+\s*)?(?:\*\*)?\s*(?:titulo|capitulo|secao)\s*:"
                              r"|\bat(?:ualizacao)?\.?\s*(?:mni|mcr|mca)\s+n")
# O cabeçalho de cada folha de manual se repete no alto das páginas; na conversão fica a primeira vez de cada um
CABECALHO_DE_MANUAL = re.compile(r"(?i)^(?:t[íi]tulo|cap[íi]tulo|se[çc][ãa]o)\s*:")


ARTIGO_PRIMEIRO = re.compile(r"(?m)^\W*art(?:igo)?\.?\s*1\s*[º°o.]?(?!\d)")


def anexo_proprio_ausente(corpo, numero, bruto=None):
    """Trecho da remissão a anexo do próprio normativo que não está no texto, ou None.

    O anexo conta como presente quando, depois da primeira remissão, há: uma seção que abre com "Anexo" ou "Regulamento
    anexo"; outro "Art. 1º" (o regulamento ou a política anexa, que o BC põe depois da assinatura sem título); uma
    tabela; ou texto depois do fecho "Brasília, ..." e da assinatura (o regulamento anexo das resoluções antigas vem
    assim). Também quando `bruto`, o texto do PDF antes da conversão, traz duas ou mais marcas das folhas do manual que
    a carta atualiza (FOLHAS_DE_MANUAL). O BC às vezes publica o anexo só no PDF da versão: o texto em Markdown ficaria
    incompleto.
    """
    texto = TRACOS.sub("-", sem_acento(corpo).lower())
    # "à Car- ta-Circular", "à Resolu- ção": a palavra partida na quebra de linha do texto antigo volta a ser uma só
    texto = re.sub(r"(?<=[a-z])-(?:[ \t]+|[ \t]*\n[ \t]*)(?=[a-z])", "", texto)
    # "a Carta-Circular 2.795 e seus respectivos Regulamentos anexos": os anexos são do ato citado antes
    proprias = [m for m in ANEXO_PROPRIO.finditer(texto) if "respectiv" not in texto[max(0, m.start() - 16):m.start()]]
    # "Regulamento anexo à Resolução nº 2.675" é próprio quando o número é o do normativo
    proprias += [m for m in REGULAMENTO_DE.finditer(texto) if int(m.group(1).replace(".", "") or -1) == numero]
    if not proprias:
        return None
    depois = texto[min(m.start() for m in proprias):]
    # dois "Art. 1º": o do normativo e o do anexo (um só pode ser o do próprio ato, depois de remissão no preâmbulo)
    if (SECAO_DE_ANEXO.search(texto) or len(ARTIGO_PRIMEIRO.findall(texto)) >= 2
            or re.search(r"(?m)^\|.*\|\s*$", depois) or "<table" in depois):
        return None
    marcas = TRACOS.sub("-", sem_acento(bruto).lower()) if bruto else depois  # no HTML, o cabeçalho fica no texto
    if len(FOLHAS_DE_MANUAL.findall(marcas)) >= 2:
        return None
    proprias = [m.group(0) for m in sorted(proprias, key=lambda m: m.start())]
    fechos = list(FECHO_BRASILIA.finditer(texto))
    if fechos:
        depois = texto[fechos[-1].end():].strip().split("\n\n", 1)  # a assinatura e, depois, o que vier
        if len(depois) > 1 and len(re.sub(r"\W", "", depois[1])) >= 200:
            return None
    return proprias[0]


def converter(texto_html):
    """Markdown do texto: o do sistema antigo, num <pre>, por `texto_pdf_para_md`; o atual, por `html2md`."""
    pres = re.findall(r"<pre\b[^>]*>(.*?)</pre>", texto_html, re.S | re.I)
    if pres:
        bruto = "\n\n".join(htmllib.unescape(re.sub(r"<[^>]+>", "", p)) for p in pres)
        if len(visivel(bruto)) >= 0.9 * len(visivel(texto_html)):
            return texto_pdf_para_md(bruto)
    return convert(texto_html)


ORIGINAL = re.compile(r"(?<![\w])([a-z]+(?:_[a-z]+)*_\d+_v1_o\.pdf)\b", re.I)
# Como o PDF se identifica no alto: "CARTA-CIRCULAR Nº 1.237", "CARTA-CIRCULAR-N° 1177", "RESOLUÇÃO Nº 580"
ESPECIE_NO_PDF = {
    "Carta Circular": r"CARTA[\s-]*CIRCULAR", "Circular": r"(?<!CARTA)(?<!CARTA )(?<!CARTA-)CIRCULAR",
    "Resolução": r"RESOLUCAO", "Resolução CMN": r"RESOLUCAO(?: CMN)?", "Resolução BCB": r"RESOLUCAO(?: BCB)?",
    "Resolução Conjunta": r"RESOLUCAO CONJUNTA", "Instrução Normativa BCB": r"INSTRUCAO NORMATIVA(?: BCB)?",
}
NUMERO_NO_PDF = r"[\s-]*(?:N\s*[.ºO°]*\s*)?([\d.]*\d)"  # "CIRCULAR 3.377", sem o "Nº", também


def arquivo_original(documentos):
    """Nome do PDF da versão original ("C_Circ_2989_v1_O.pdf") no campo Documentos, ou None."""
    m = ORIGINAL.search(documentos or "")
    return m.group(1) if m else None


def url_do_original(arquivo, ano):
    nome = arquivo.lower()
    return PDF_ORIGINAL.format(serie=re.sub(r"_\d+_v1_o\.pdf$", "", nome), ano=ano, arquivo=nome)


def numero_no_pdf(texto, tipo, numero):
    """O PDF se identifica, no alto, como o normativo do índice: a espécie e o número."""
    plano = TRACOS.sub("-", re.sub(r"\s+", " ", sem_acento(texto).upper())[:600])
    especie = ESPECIE_NO_PDF.get(tipo)
    return bool(especie) and any(int(m.group(1).replace(".", "")) == numero
                                 for m in re.finditer(especie + NUMERO_NO_PDF, plano))


def data_no_pdf(texto, tipo, numero):
    """Datas que o PDF põe junto da espécie e do número ("Carta-Circular nº 701, de 29 de dezembro de 1981", no rodapé
    das páginas), em ISO; vazia quando ele não traz a data assim."""
    plano = TRACOS.sub("-", re.sub(r"\s+", " ", sem_acento(texto).lower()))
    especie = ESPECIE_NO_PDF.get(tipo, "^$").lower()
    meses = "|".join(sem_acento(m) for m in MESES)
    datas = set()
    for m in re.finditer(especie + r"[\s-]*n\s*[.ºo°]*\s*([\d.]*\d),? de (\d{1,2})[º°o]? de (" + meses + r") de (\d{4})",
                         plano):
        if int(m.group(1).replace(".", "")) != numero:
            continue
        try:
            datas.add(dt.date(int(m.group(4)), [sem_acento(x) for x in MESES].index(m.group(3)) + 1,
                              int(m.group(2))).isoformat())
        except ValueError:
            datas.add("inválida")
    return datas


def paginas_em_imagem(lista, info, limiar=0.10):
    """Páginas em que as imagens cobrem `limiar` ou mais da área: página escaneada, anexo, tabela ou formulário em
    imagem, cujo conteúdo a camada de texto não traz. Logotipo e fio de cabeçalho ficam abaixo do limiar.

    `lista` é a saída do `pdfimages -list`; `info`, a do `pdfinfo -f 1 -l 99999`, com o tamanho de cada página. A
    área da imagem na página vem da resolução com que ela foi posta (colunas x-ppi e y-ppi).
    """
    linhas = lista.splitlines()
    if not linhas or not linhas[0].split()[:3] == ["page", "num", "type"]:
        raise RuntimeError("saída do pdfimages -list sem o cabeçalho esperado")
    tamanhos = {int(n): (float(w), float(h)) for n, w, h in
                re.findall(r"^Page\s+(\d+)\s+size:\s+([\d.]+)\s+x\s+([\d.]+)", info, re.M)}
    cobertura = collections.Counter()
    for linha in linhas[2:]:
        c = linha.split()
        if len(c) < 14 or not c[0].isdigit() or c[2] != "image":  # máscaras (smask, stencil) acompanham a imagem
            continue
        pagina, largura, altura = int(c[0]), int(c[3]), int(c[4])
        w, h = tamanhos.get(pagina, (595.0, 842.0))
        try:
            fracao = (largura / float(c[12])) * (altura / float(c[13])) / ((w / 72) * (h / 72))
        except (ValueError, ZeroDivisionError):
            fracao = 1.0  # sem a resolução não dá para medir: conta como página em imagem
        cobertura[pagina] += fracao
    return sorted(p for p, f in cobertura.items() if f >= limiar)


def ler_pdf(pdf):
    """(texto, páginas em imagem) do PDF: `pdftotext -layout`, com as páginas separadas por \\f, e paginas_em_imagem."""
    with tempfile.TemporaryDirectory() as tmp:
        arq = os.path.join(tmp, "a.pdf")
        with open(arq, "wb") as f:
            f.write(pdf)

        def rodar(*args):
            r = subprocess.run(args, capture_output=True, timeout=300)
            if r.returncode != 0:
                raise RuntimeError(f"{args[0]} falhou ({r.returncode}): {r.stderr.decode('utf-8', 'replace')[:200]}")
            return r.stdout.decode("utf-8", "replace")

        texto = rodar("pdftotext", "-q", "-layout", "-enc", "UTF-8", arq, "-")
        return texto, paginas_em_imagem(rodar("pdfimages", "-list", arq), rodar("pdfinfo", "-f", "1", "-l", "99999", arq))


def baixar_pdf(rede, url):
    """Bytes do PDF, ou None quando o portal não o tem (404, 410 ou resposta que não é PDF)."""
    try:
        status, dados, _ = rede.get(url, accept="application/pdf")
    except RuntimeError as e:
        if re.search(r"HTTP Error (?:401|429)\b", str(e)):
            raise Recusa(f"a fonte recusou o acesso: {url}") from e
        raise
    if status in (401, 403, 429):
        raise Recusa(f"a fonte recusou o acesso (HTTP {status}): {url}")
    if status in (400, 404, 410) or (status == 200 and not dados.startswith(b"%PDF")):
        return None
    if status != 200:
        raise RuntimeError(f"HTTP {status}: {url}")
    return dados


def data_do_ato(datas_no_pdf, data_no_portal):
    """A data do ato quando o PDF e o portal divergem, ou None. O ato se data no próprio texto ("Circular nº 3.467, de
    14 de setembro de 2009"); a do portal, quando é de 1 a 30 dias depois, é a da publicação. Duas datas no PDF, ou a do
    PDF depois da do portal, não se resolvem."""
    if len(datas_no_pdf) != 1 or "inválida" in datas_no_pdf:
        return None
    no_pdf = next(iter(datas_no_pdf))
    return no_pdf if 0 < (dt.date.fromisoformat(data_no_portal) - dt.date.fromisoformat(no_pdf)).days <= 30 else None


def texto_sem_paginas_em_imagem(texto, imagens):
    """O texto do PDF sem as páginas em imagem, ou None quando o normativo não se lê sem elas: a primeira página é
    imagem, ou a página em imagem tem camada de texto (OCR da origem, ou página que mistura texto e imagem: tirar o
    texto dela cortaria o normativo), ou o que sobra é curto demais."""
    paginas = texto.split("\f")
    if 1 in imagens or any(len(re.sub(r"\W", "", paginas[n - 1])) >= 200 for n in imagens if n <= len(paginas)):
        return None
    resto = ["" if n in imagens else p for n, p in enumerate(paginas, 1)]
    return "\f".join(resto) if len(re.sub(r"\W", "", "".join(resto))) >= 300 else None


def texto_do_original(rede, item, x, data, cache, pendencia=None):
    """(corpo, url, pdf, None, data do ato) a partir do PDF da versão original, ou (None, url, pdf, retenção, None)
    quando ele não serve. `cache` guarda o PDF baixado, para refazer sem rede. Com `pendencia` (um dicionário), o PDF
    com página em imagem entra sem ela quando `texto_sem_paginas_em_imagem` deixa, e as páginas vão para
    `pendencia["paginas_em_imagem"]`."""
    arquivo = arquivo_original(x.get("Documentos"))
    if not arquivo:
        return None, None, None, {"motivo": "texto só nos PDFs, e o portal não lista o da versão original",
                                  "documentos": x.get("Documentos")}, None
    url = url_do_original(arquivo, (item.get("data") or data)[:4])
    if cache.exists():
        pdf = gzip.decompress(cache.read_bytes())
    else:
        pdf = baixar_pdf(rede, url)
        if pdf is None:
            return None, url, None, {"motivo": "o PDF da versão original não está em /pre/normativos/ (o outro endereço "
                                               "do portal, /Lists/, é proibido pelo robots.txt)", "pdf": url}, None
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_bytes(gzip.compress(pdf))
    texto, imagens = ler_pdf(pdf)
    if imagens:
        sem_imagem = texto_sem_paginas_em_imagem(texto, imagens) if pendencia is not None else None
        if sem_imagem is None:
            return None, url, pdf, {"motivo": IMAGEM_NO_PDF, "paginas_em_imagem": imagens, "pdf": url}, None
        # o pdftotext fecha cada página com \f, inclusive a última
        pendencia.update(paginas_em_imagem=imagens, paginas=texto.count("\f") + (0 if texto.endswith("\f") else 1))
        texto = sem_imagem
    if re.fullmatch(r"\W*n[úu]mero n[ãa]o utilizado\W*", " ".join(texto.split()), re.I):
        return None, url, pdf, {"motivo": "número não utilizado: o PDF do portal só diz isso", "pdf": url}, None
    if not numero_no_pdf(texto, item["tipo"], item["numero"]):
        return None, url, pdf, {"motivo": "espécie ou número no alto do PDF difere do índice", "pdf": url,
                                "inicio_do_pdf": " ".join(texto.split())[:160]}, None
    datas = data_no_pdf(texto, item["tipo"], item["numero"])
    if datas and datas != {data}:
        ato = data_do_ato(datas, data)
        if not ato:
            return None, url, pdf, {"motivo": "data no PDF difere da do portal", "pdf": url,
                                    "datas_no_pdf": sorted(datas), "data_no_portal": data}, None
        data = ato
    corpo = texto_pdf_para_md(texto, manter_primeira=CABECALHO_DE_MANUAL)
    # com o texto do PDF: ver FOLHAS_DE_MANUAL. Com página em imagem de fora, o anexo é a própria pendência.
    remissao = None if imagens else anexo_proprio_ausente(corpo, item["numero"], bruto=texto)
    if remissao:
        return None, url, pdf, {"motivo": "anexo próprio referido e ausente do PDF da versão original", "pdf": url,
                                "remissao": remissao}, None
    return corpo, url, pdf, None, data


def processar(rede, item, existentes, pdf=False, imagem_pendente=False):
    pasta, tipo_canonico, orgao, prefixo = TIPOS[item["tipo"]]
    if (prefixo, item["numero"]) in existentes:
        return "no_acervo", None
    tipo_url = urllib.parse.quote(item["tipo"])
    url_api = DETALHE.format(tipo=tipo_url, numero=item["numero"])
    ano_indice = (item.get("data") or "0000")[:4]
    cache = FONTE / pasta / ano_indice / f"{prefixo}-{item['numero']}-{ano_indice}"  # do modo --pdf, sem extensão
    cache_json = cache.with_name(cache.name + ".json.gz")
    if pdf and cache_json.exists():
        bruto = gzip.decompress(cache_json.read_bytes())
    else:
        bruto = obter(rede, url_api)
    falha = {"tipo": item["tipo"], "numero": item["numero"], "id": item["id"], "fonte": url_api}
    conteudo = json.loads(bruto).get("conteudo") or []
    if not conteudo:
        return "retido", {**falha, "motivo": "a API não devolveu o normativo"}
    x = conteudo[0]
    if x.get("Tipo") != item["tipo"] or int(float(x.get("Numero") or -1)) != item["numero"]:
        return "retido", {**falha, "motivo": "tipo ou número da página difere do índice",
                          "na_pagina": [x.get("Tipo"), x.get("Numero")]}
    data = data_do_normativo(x)
    if not data or data > dt.date.today().isoformat():
        return "retido", {**falha, "motivo": f"data ausente ou futura na fonte: {x.get('DataTexto')!r}"}
    texto_html = x.get("Texto") or ""
    fonte_texto, bruto_fonte, versao, extensao = url_api, bruto, VERSAO, ".json.gz"
    pendencia = {} if imagem_pendente else None
    if len(visivel(texto_html)) < 40:
        if not pdf:
            return "retido", {**falha, "motivo": SO_PDF, "documentos": x.get("Documentos")}
        if not cache_json.exists():  # os metadados do portal ficam, para refazer sem rede
            cache_json.parent.mkdir(parents=True, exist_ok=True)
            cache_json.write_bytes(gzip.compress(bruto))
        corpo, url_pdf, bytes_pdf, retencao, data = texto_do_original(rede, item, x, data,
                                                                      cache.with_name(cache.name + ".pdf.gz"), pendencia)
        if retencao:
            return "retido", {**falha, **retencao}
        fonte_texto, bruto_fonte, versao, extensao = url_pdf, bytes_pdf, VERSAO_PDF, ".pdf.gz"
    else:
        if re.search(r"<img\b", texto_html, re.I):
            return "retido", {**falha, "motivo": "imagem no texto: o conteúdo visual não entra no Markdown"}
        corpo = converter(texto_html)
    if len(re.sub(r"\W", "", corpo)) < 40:
        return "retido", {**falha, "motivo": "texto vazio depois da conversão"}
    remissao = None if versao == VERSAO_PDF else anexo_proprio_ausente(corpo, item["numero"])  # o PDF já passou
    if remissao:
        return "retido", {**falha, "motivo": "anexo próprio referido e ausente do texto (pode estar só no PDF da versão)",
                          "remissao": remissao, "documentos": x.get("Documentos")}
    ano = data[:4]
    slug = f"{prefixo}-{item['numero']}-{ano}"
    titulo = titulo_do_normativo(item["tipo"], item["numero"], data)
    revogado, cancelado = bool(x.get("Revogado")), bool(x.get("Cancelado"))
    publicacao = " ".join((x.get("DOU") or "").split())
    meta = [("titulo", titulo), ("orgao", orgao), ("tipo", tipo_canonico), ("tipo_na_fonte", item["tipo"]),
            ("numero", str(item["numero"])), ("data", data),
            ("ementa", " ".join((x.get("Assunto") or item.get("ementa") or "").split()))]
    if revogado or cancelado:
        meta.append(("situacao", "revogado" if revogado else "cancelado"))
    meta += [("revogada", revogado or cancelado), ("versao_texto", versao)]
    if pendencia:
        meta.append(("paginas_em_imagem", f"{', '.join(map(str, pendencia['paginas_em_imagem']))} de {pendencia['paginas']}: "
                                          "anexo, tabela ou formulário escaneado no PDF, sem transcrição neste arquivo"))
    if publicacao:
        meta.append(("publicacao", publicacao))
        if data_da_publicacao(publicacao):
            meta.append(("data_publicacao", data_da_publicacao(publicacao)))
    meta += [("fonte", PAGINA.format(tipo=tipo_url, numero=item["numero"])), ("fonte_texto", fonte_texto),
             ("sha256_fonte", hashlib.sha256(bruto_fonte).hexdigest())]
    gravar(str(PASTA / pasta / ano / f"{slug}.md"), str(FONTE / pasta / ano / f"{slug}{extensao}"), bruto_fonte, meta,
           f"# {titulo}\n\n{corpo}")
    existentes.add((prefixo, item["numero"]))
    if pendencia:
        return "pendente", {"path": f"reguladores/bcb/{pasta}/{ano}/{slug}.md", "tipo": item["tipo"], "numero": item["numero"],
                            "pdf": fonte_texto, "sha256_pdf": hashlib.sha256(bruto_fonte).hexdigest(), **pendencia}
    return "ok", None


def registrar_falha(falha, ja):
    linha = json.dumps(falha, ensure_ascii=False, sort_keys=True)
    chave = (falha["tipo"], falha["numero"], falha["motivo"])
    if chave in ja:
        return
    ja.add(chave)
    FALHAS.parent.mkdir(parents=True, exist_ok=True)
    with open(FALHAS, "a", encoding="utf-8") as f:
        f.write(linha + "\n")


def ler_falhas():
    if not FALHAS.exists():
        return []
    return [json.loads(l) for l in FALHAS.read_text(encoding="utf-8").splitlines() if l.strip()]


def falhas_registradas():
    return {(d["tipo"], d["numero"], d["motivo"]) for d in ler_falhas()}


def registrar_pendencia(info):
    """Anota em _paginas_em_imagem.jsonl o arquivo gravado sem as páginas em imagem (uma linha por arquivo)."""
    arquivo = PASTA / "_paginas_em_imagem.jsonl"
    linhas = [l for l in arquivo.read_text(encoding="utf-8").splitlines() if l.strip()] if arquivo.exists() else []
    linhas = [l for l in linhas if json.loads(l)["path"] != info["path"]] + [json.dumps(info, ensure_ascii=False, sort_keys=True)]
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    arquivo.write_text("".join(l + "\n" for l in sorted(linhas)), encoding="utf-8")


def tirar_retencoes_resolvidas(resolvidos, motivo=SO_PDF):
    """Tira do _falhas.jsonl a linha do motivo refeito ("texto só nos PDFs", ou a página em imagem) dos normativos que
    o modo de refazer gravou ou reteve por outro motivo (a retenção nova já foi registrada). A de quem deu erro de rede
    fica."""
    if not resolvidos or not FALHAS.exists():
        return
    linhas = [l for l in FALHAS.read_text(encoding="utf-8").splitlines() if l.strip()]
    ficam = [l for l in linhas
             if not ((d := json.loads(l))["motivo"] == motivo and (d["tipo"], d["numero"]) in resolvidos)]
    FALHAS.write_text("".join(l + "\n" for l in ficam), encoding="utf-8")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--tipos", default=",".join(TIPOS), help="tipos na fonte, separados por vírgula")
    ap.add_argument("--de", type=int, default=0, help="ano inicial (pela data do índice)")
    ap.add_argument("--ate", type=int, default=9999, help="ano final (pela data do índice)")
    ap.add_argument("--rps", type=float, default=1.0)
    ap.add_argument("--limite", type=int, default=0)
    ap.add_argument("--so-indice", action="store_true")
    ap.add_argument("--refazer-indice", action="store_true")
    ap.add_argument("--pdf", action="store_true",
                    help="refaz só os retidos por texto só nos PDFs, a partir do PDF da versão original")
    ap.add_argument("--pagina-em-imagem", action="store_true",
                    help="refaz só os retidos por página em imagem no PDF, sem ela, como pendência de integralidade")
    a = ap.parse_args(argv)
    tipos = [t.strip() for t in a.tipos.split(",") if t.strip()]
    desconhecidos = [t for t in tipos if t not in TIPOS]
    if desconhecidos:
        ap.error(f"tipo desconhecido: {', '.join(desconhecidos)} (válidos: {', '.join(TIPOS)})")
    if not 0 < a.rps <= 2:
        ap.error("--rps deve estar entre 0 e 2")
    rede = Rede(a.rps)
    cont = collections.Counter()
    try:
        itens = []
        for tipo in tipos:
            lista = montar_indice(rede, tipo, a.refazer_indice)
            print(f"[BCB] {tipo}: {len(lista)} no índice", flush=True)
            itens += [i for i in lista if a.de <= int(i["data"][:4] or 0) <= a.ate]
        if a.so_indice:
            return 0
        refazer = IMAGEM_NO_PDF if a.pagina_em_imagem else SO_PDF if a.pdf else None
        if refazer:
            alvo = {(d["tipo"], d["numero"]) for d in ler_falhas() if d["motivo"] == refazer}
            itens = [i for i in itens if (i["tipo"], i["numero"]) in alvo]
        itens.sort(key=lambda i: i["data"], reverse=True)  # os mais recentes primeiro: são os mais consultados
        if a.limite:
            itens = itens[: a.limite]
        existentes, ja, resolvidos = no_acervo(), falhas_registradas(), set()
        try:
            for n, item in enumerate(itens, 1):
                try:
                    estado, falha = processar(rede, item, existentes, pdf=bool(refazer),
                                              imagem_pendente=a.pagina_em_imagem)
                except Recusa:
                    raise
                except Exception as e:  # rede ou resposta malformada: registra e segue
                    estado, falha = "erro", {"tipo": item["tipo"], "numero": item["numero"], "id": item["id"],
                                             "motivo": f"erro: {str(e)[:200]}"}
                cont[estado] += 1
                if estado == "pendente":
                    registrar_pendencia(falha)
                elif falha and estado != "erro":
                    registrar_falha(falha, ja)
                # quem continua retido pelo mesmo motivo (a página em imagem que não dá para tirar) fica como está
                if refazer and estado != "erro" and not (estado == "retido" and falha["motivo"] == refazer):
                    resolvidos.add((item["tipo"], item["numero"]))
                if n % 100 == 0 or n == len(itens):
                    print(f"[BCB] {n}/{len(itens)} {dict(cont)}", flush=True)
        finally:
            tirar_retencoes_resolvidas(resolvidos, refazer or SO_PDF)
    except Recusa as e:
        print(f"[BCB] {e}. Coleta interrompida; rode de novo mais tarde, com --rps menor.", flush=True)
        return 2
    print(f"[BCB] FIM {dict(cont)}", flush=True)
    return 1 if cont["erro"] else 0


if __name__ == "__main__":
    sys.exit(main())
