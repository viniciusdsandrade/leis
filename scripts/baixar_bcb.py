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

robots.txt de www.bcb.gov.br (conferido em 20/11/2026): permite /api/. Para na recusa (HTTP 401, 403 ou 429).

    python3 -I scripts/baixar_bcb.py --so-indice                       # monta o índice dos tipos
    python3 -I scripts/baixar_bcb.py --tipos Resolução --de 1990 --ate 1999
    python3 -I scripts/baixar_bcb.py --tipos "Resolução CMN,Resolução BCB" --rps 1
"""
import argparse
import collections
import datetime as dt
import hashlib
import html as htmllib
import json
import re
import sys
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


_ATO = r"(?:resolucao|circular|carta[ -]circular|instrucao normativa)"
# O designador ("Anexo II") fica dentro da exceção: opcional fora dela, o motor o deixaria de fora para casar.
_DE_OUTRO = (r"(?!(?:\s+(?:[ivxlc]+|\d+)\b)?\s+(?:a|ao|aos|as|da|do|das|dos)\s+(?:resolucao|circular|carta|instrucao"
             r"|lei|decreto|portaria|medida)\b)")
# Remissão a anexo do próprio normativo. A de outro ato ("anexo à Resolução nº 2.309") não conta.
_DESIGNADOR = r"(?:\s+(?:[ivxlc]+|\d+)\b)?"  # "Anexo II", "Anexo 3"
ANEXO_PROPRIO = re.compile(
    r"\banex[oa]s?" + _DESIGNADOR + r"\s+(?:desta|deste|a esta|a este|a presente|ao presente|da presente"
    r"|do presente)\s+" + _ATO
    + r"|\b(?:na forma|nos termos|constantes?|conforme|de acordo com|previst[oa]s? n[oa])\s+(?:d?os?|d?as?)\s+anexos?\b"
    + _DE_OUTRO
    + r"|\b(?:tabela|quadro|modelo|formulario|planilha|relacao|regulamento)\s+anex[oa]s?\b" + _DE_OUTRO)
REGULAMENTO_DE = re.compile(r"\bregulamento anexo" + _DESIGNADOR + r" (?:a|ao) " + _ATO + r" n[º°o.]*\s*([\d.]+)")
SECAO_DE_ANEXO = re.compile(r"(?m)^(?:#+\s*)?(?:\*\*)?\s*(?:anexos?|regulamento anexo|regulamento a que se refere)\b")
FECHO_BRASILIA = re.compile(r"(?m)^brasilia,?\s+(?:em\s+)?\d{1,2}[º°o]?\s+de\s+[a-z]+\s+de\s+\d{4}\b.*$")


ARTIGO_PRIMEIRO = re.compile(r"(?m)^\W*art(?:igo)?\.?\s*1\s*[º°o.]?(?!\d)")


def anexo_proprio_ausente(corpo, numero):
    """Trecho da remissão a anexo do próprio normativo que não está no texto, ou None.

    O anexo conta como presente quando, depois da primeira remissão, há: uma seção que abre com "Anexo" ou "Regulamento
    anexo"; outro "Art. 1º" (o regulamento ou a política anexa, que o BC põe depois da assinatura sem título); uma
    tabela; ou texto depois do fecho "Brasília, ..." e da assinatura (o regulamento anexo das resoluções antigas vem
    assim). O BC às vezes publica o anexo só no PDF da versão: o texto em Markdown ficaria incompleto.
    """
    texto = sem_acento(corpo).lower()
    proprias = [m for m in ANEXO_PROPRIO.finditer(texto)]
    # "Regulamento anexo à Resolução nº 2.675" é próprio quando o número é o do normativo
    proprias += [m for m in REGULAMENTO_DE.finditer(texto) if int(m.group(1).replace(".", "") or -1) == numero]
    if not proprias:
        return None
    depois = texto[min(m.start() for m in proprias):]
    # dois "Art. 1º": o do normativo e o do anexo (um só pode ser o do próprio ato, depois de remissão no preâmbulo)
    if (SECAO_DE_ANEXO.search(texto) or len(ARTIGO_PRIMEIRO.findall(texto)) >= 2
            or re.search(r"(?m)^\|.*\|\s*$", depois) or "<table" in depois):
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


def processar(rede, item, existentes):
    pasta, tipo_canonico, orgao, prefixo = TIPOS[item["tipo"]]
    if (prefixo, item["numero"]) in existentes:
        return "no_acervo", None
    tipo_url = urllib.parse.quote(item["tipo"])
    url_api = DETALHE.format(tipo=tipo_url, numero=item["numero"])
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
    if len(visivel(texto_html)) < 40:
        return "retido", {**falha, "motivo": "texto só nos PDFs das versões: o campo de texto da API está vazio",
                          "documentos": x.get("Documentos")}
    if re.search(r"<img\b", texto_html, re.I):
        return "retido", {**falha, "motivo": "imagem no texto: o conteúdo visual não entra no Markdown"}
    corpo = converter(texto_html)
    if len(re.sub(r"\W", "", corpo)) < 40:
        return "retido", {**falha, "motivo": "texto vazio depois da conversão"}
    remissao = anexo_proprio_ausente(corpo, item["numero"])
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
    meta += [("revogada", revogado or cancelado), ("versao_texto", VERSAO)]
    if publicacao:
        meta.append(("publicacao", publicacao))
        if data_da_publicacao(publicacao):
            meta.append(("data_publicacao", data_da_publicacao(publicacao)))
    meta += [("fonte", PAGINA.format(tipo=tipo_url, numero=item["numero"])), ("fonte_texto", url_api),
             ("sha256_fonte", hashlib.sha256(bruto).hexdigest())]
    gravar(str(PASTA / pasta / ano / f"{slug}.md"), str(FONTE / pasta / ano / f"{slug}.json.gz"), bruto, meta,
           f"# {titulo}\n\n{corpo}")
    existentes.add((prefixo, item["numero"]))
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


def falhas_registradas():
    if not FALHAS.exists():
        return set()
    return {(d["tipo"], d["numero"], d["motivo"])
            for d in (json.loads(l) for l in FALHAS.read_text(encoding="utf-8").splitlines() if l.strip())}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--tipos", default=",".join(TIPOS), help="tipos na fonte, separados por vírgula")
    ap.add_argument("--de", type=int, default=0, help="ano inicial (pela data do índice)")
    ap.add_argument("--ate", type=int, default=9999, help="ano final (pela data do índice)")
    ap.add_argument("--rps", type=float, default=1.0)
    ap.add_argument("--limite", type=int, default=0)
    ap.add_argument("--so-indice", action="store_true")
    ap.add_argument("--refazer-indice", action="store_true")
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
        itens.sort(key=lambda i: i["data"], reverse=True)  # os mais recentes primeiro: são os mais consultados
        if a.limite:
            itens = itens[: a.limite]
        existentes, ja = no_acervo(), falhas_registradas()
        for n, item in enumerate(itens, 1):
            try:
                estado, falha = processar(rede, item, existentes)
            except Recusa:
                raise
            except Exception as e:  # rede ou resposta malformada: registra e segue
                estado, falha = "erro", {"tipo": item["tipo"], "numero": item["numero"], "id": item["id"],
                                         "motivo": f"erro: {str(e)[:200]}"}
            cont[estado] += 1
            if falha and estado != "erro":
                registrar_falha(falha, ja)
            if n % 100 == 0 or n == len(itens):
                print(f"[BCB] {n}/{len(itens)} {dict(cont)}", flush=True)
    except Recusa as e:
        print(f"[BCB] {e}. Coleta interrompida; rode de novo mais tarde, com --rps menor.", flush=True)
        return 2
    print(f"[BCB] FIM {dict(cont)}", flush=True)
    return 1 if cont["erro"] else 0


if __name__ == "__main__":
    sys.exit(main())
