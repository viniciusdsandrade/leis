"""CONFAZ: convênios ICM/ICMS, protocolos e ajustes SINIEF do portal oficial, em Markdown.

Fonte: www.confaz.fazenda.gov.br/legislacao, o portal do Conselho Nacional de Política Fazendária. O `robots.txt`
permite tudo (`User-agent: *` com `Disallow:` vazio, conferido em 23/11/2026). A coleta usa um cliente só, a meia
requisição por segundo.

Índice: `sitemap.xml.gz`, o mapa do site que o próprio `robots.txt` aponta; em 1975 e 2015 ele traz exatamente os atos
que a página de índice do ano lista. Entram os endereços regulares de três seções:

    /legislacao/convenios/<ano>/CV013_75, CVM021_89, convenio-icms-122-26
    /legislacao/protocolos/<ano>/pt146_12, protocolo-icms-51-18
    /legislacao/ajustes/<ano>/AJ_014_14, AJ029_22, ajuste-sinief-48-21

Ficam fora do recorte, listados em reguladores/confaz/_indice/fora-do-recorte.json: retificações avulsas, redações
anteriores, índices de ano, anexos em PDF, modelos de documentos e os convênios sem número de 1966 a 1970.

O texto é o que o portal publica: o ato com as notas de alteração, prorrogação e revogação que o CONFAZ acrescenta
("Revogado pelo Conv. ICMS 12/90", "Nova redação dada à cláusula ..."). O arquivo só é gravado quando, todos juntos:

- a epígrafe do próprio texto traz a espécie, o número e o ano do endereço ("CONVÊNIO ICMS 106/04", "PROTOCOLO ICMS
  146, DE 28 DE SETEMBRO DE 2012");
- a data do ato sai da epígrafe ou, nos antigos, do fecho ("Aracaju, SE, 24 de setembro de 2004.") ou do preâmbulo
  ("realizada em Brasília, DF, no dia 15 de julho de 1975"), no ano do endereço; a data do preâmbulo, quando existe,
  tem de ser a mesma, e a da publicação no DOU não pode ser anterior;
- o corpo tem cláusula ou artigo (ou, no ato antigo de dispositivo único, o verbo de quem celebra e o fecho com a
  data do ato) e não traz imagem (a tabela ou o modelo em imagem não vira texto).

O que não passa fica em reguladores/confaz/_falhas.jsonl, com o motivo.

    python3 -I scripts/baixar_confaz.py --indice
    python3 -I scripts/baixar_confaz.py --secoes convenios --de 1975 --ate 1975 --despejar
    python3 -I scripts/baixar_confaz.py --de 1966 --ate 2026
"""
import argparse
import collections
import datetime as dt
import gzip
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import Rede, gravar  # noqa: E402
from html2md import convert  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
PASTA = RAIZ / "reguladores" / "confaz"
FONTE = RAIZ / "reguladores" / "_fonte" / "confaz"
INDICE = PASTA / "_indice"
FALHAS = PASTA / "_falhas.jsonl"
BASE = "https://www.confaz.fazenda.gov.br/"
SITEMAP = BASE + "sitemap.xml.gz"
RPS = 0.5
ORGAO = "Conselho Nacional de Política Fazendária (CONFAZ)"
VERSAO = ("texto do portal do CONFAZ (www.confaz.fazenda.gov.br), com as notas de alteração, prorrogação e revogação "
          "que o portal acrescenta ao ato; não substitui a publicação no Diário Oficial da União")
MESES = "janeiro fevereiro marco abril maio junho julho agosto setembro outubro novembro dezembro".split()
MESES_RE = "|".join(MESES)
NOMES_MES = "janeiro fevereiro março abril maio junho julho agosto setembro outubro novembro dezembro".split()
# seção do portal -> (pasta do acervo, espécie básica)
SECOES = {"convenios": "Convênio", "protocolos": "Protocolo", "ajustes": "Ajuste SINIEF"}
# Endereço regular: a sigla (ou o nome por extenso), o número e os dois algarismos do ano. "CVM" é o Convênio ICM de
# 1989, quando a numeração do ICM e a do ICMS correram juntas.
ENDERECO = {
    "convenios": re.compile(r"(?:cvm?[-_]?|convenio-icms-)0*(\d{1,4})[-_](\d\d)"),
    "protocolos": re.compile(r"(?:pt[-_]?|protocolo-icms-(?:ndeg-)?)0*(\d{1,4})[-_](\d\d)"),
    "ajustes": re.compile(r"(?:aj[-_]?|ajuste-sinief-)0*(\d{1,4})[-_](\d\d)"),
}


class Recusa(RuntimeError):
    pass


def sem_acento(texto):
    return "".join(c for c in unicodedata.normalize("NFD", texto) if not unicodedata.combining(c))


def plano(bloco):
    """O bloco do Markdown sem ênfase, sem acento e com um espaço só."""
    bloco = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", bloco)
    return re.sub(r"\s+", " ", sem_acento(re.sub(r"[*_\\`#]", "", bloco))).strip()


def itens_do_sitemap(xml):
    """(itens regulares, endereços fora do recorte por motivo) das três seções, a partir do mapa do site."""
    itens, fora, vistos = [], collections.defaultdict(list), {}
    for url in re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", xml):
        m = re.match(re.escape(BASE) + r"legislacao/(convenios|protocolos|ajustes)/(.+)$", url)
        if not m:
            continue
        secao, resto = m.group(1), m.group(2)
        partes = resto.split("/")
        pasta = re.fullmatch(r"(\d{4})(?:-\d)?", partes[0])
        if pasta and ".pdf" in resto.lower():
            fora["arquivo anexo (PDF)"].append(url)
            continue
        if not pasta or len(partes) != 2:
            fora["fora das pastas de ano (modelos, índices, anexos)"].append(url)
            continue
        ano, nome = int(pasta.group(1)), partes[1].lower()
        regular = ENDERECO[secao].fullmatch(nome)
        if not regular:
            motivo = ("retificação avulsa" if re.search(r"ret[ie][fg]", nome) else
                      "índice do ano" if re.fullmatch(r"(?:convenios?|protocolos?)_?(?:icms)?_?\d{4}|\d{4}", nome) else
                      "redação anterior ou republicação" if re.search(r"anterior|republic", nome) else
                      "convênio sem número (1966 a 1970)" if re.match(r"cv_[a-z]", nome) else
                      "endereço fora do padrão")
            fora[motivo].append(url)
            continue
        numero = int(regular.group(1))
        if int(regular.group(2)) != ano % 100:
            fora["ano do endereço diferente do da pasta"].append(url)
            continue
        icm = secao == "convenios" and nome.startswith("cvm")
        chave = (secao, ano, numero, icm)
        if chave in vistos:
            # a pasta "2017-1" repete atos de 2017: vale o primeiro endereço, na ordem do mapa
            fora["número repetido no mapa do site"].append(url)
            continue
        vistos[chave] = url
        itens.append({"secao": secao, "ano": ano, "numero": numero, "icm": icm, "url": url})
    return sorted(itens, key=lambda i: (i["secao"], i["ano"], i["numero"], i["icm"])), dict(fora)


def corpo_da_pagina(html):
    """O `<div id="parent-fieldname-text">` da página do Plone, inteiro, ou ""."""
    inicio = html.find('<div id="parent-fieldname-text"')
    if inicio < 0:
        return ""
    nivel = 0
    for m in re.finditer(r"<(/?)div\b[^>]*>", html[inicio:]):
        nivel += -1 if m.group(1) else 1
        if nivel == 0:
            return html[inicio:inicio + m.end()]
    return ""


def _data(dia, mes, ano):
    try:
        return dt.date(int(re.sub(r"\s", "", ano)), MESES.index(mes) + 1, int(dia)).isoformat()
    except ValueError:
        return ""


# "CONVÊNIO AE 01/70" e "CONVÊNIO AE-1/73" (a série de 1970 a 1974, antes do CONFAZ), "CONVÊNIO ICM 13/75", "CONVÊNIO ICMS 106/04",
# "PROTOCOLO 02/68", "AJUSTE SINIEF 07/71", "PROTOCOLO ICMS 146, DE 28 DE
# SETEMBRO DE 2012", "CONVÊNIO ICMS Nº 122, DE 23 DE OUTUBRO DE 2026", "AJUSTE SINIEF 23/19, DE 10 DE OUTUBRO DE 2019",
# "AJUSTE SINIEF Nº 48, 09 DE DEZEMBRO DE 2021" (sem o "DE"), "CONVÊNIO ICMS 07, DE27 DE MARÇO DE 1997" e
# "PROTOCOLO ICMS 99, DE 30 DE SETEMBRO DE 200 8" (espaço no meio do ano, da fonte), "AJUSTE SINIEF 3, DE 3 ABRIL DE
# 2009" e "AJUSTE SINIEF 23/17, DE 15 DE DEZEMBRO DE2017" (sem o "de" ou sem o espaço), "CONVÊNIO ICMS 14 , DE 1º DEABRIL
# DE 2011", "CONVÊNIO ICMS 80/18, DE05DE JULHO DE 2018", "CONVÊNIO ICMS 29, DE 3 DE ABRIL 2009", "CONVÊNIO ICMS 89, DE 12
# DE SETEMBRO DE DE 2016" e "CONVÊNIO/ICMS Nº 2, DE 24 DE JANEIRO DE 2023". O número e a data inteira continuam tendo de
# sair da epígrafe, e a data ainda é confrontada com a do preâmbulo.
EPIGRAFE = re.compile(
    r"^(?P<especie>convenio|protocolo|ajuste sinief)(?:[ /](?P<imposto>icms?|ae))?[ -]?(?:n[º°o.]* ?)?0*(?P<numero>\d{1,4}) ?"
    r"(?:/ ?(?P<aa>\d{2}|\d{4}))? ?"
    r"(?:,? ?(?:de ?)?(?P<dia>\d{1,2})[º°o]? ?(?:de ?)?(?P<mes>" + MESES_RE + r") (?:de ?)*(?P<ano>\d ?\d ?\d ?\d))?\b")


def ler_epigrafe(blocos):
    """A epígrafe do ato nos primeiros blocos: espécie, imposto, número, ano e, quando ela a traz, a data.

    O portal às vezes quebra a epígrafe em dois blocos ("PROTOCOLO ICMS" e "21/97") ou põe antes dela a marca
    "REVOGADO": vale o primeiro bloco, ou par de blocos vizinhos, que casa inteiro com a forma da epígrafe.
    """
    # "C ONVÊNIO AE 10/72" e "CON VÊNIO ICMS 51": o começo da palavra solto; "04 D E AGOSTO": o "de" partido. Da fonte.
    planos = [re.sub(r"\bd e\b", "de", re.sub(r"^(c|con) (?=[a-z]{4})", r"\1", plano(b).lower())) for b in blocos[:6]]
    for i, bloco in enumerate(planos):
        for candidato in (bloco, bloco + " " + planos[i + 1] if i + 1 < len(planos) else ""):
            m = EPIGRAFE.match(candidato)
            if not m or not (m["aa"] or m["ano"]):
                continue
            resto = candidato[m.end():].strip(" .")
            if resto:  # "Convênio ICMS 12/90, que dispõe sobre..." é citação, não epígrafe
                continue
            ano = int(re.sub(r"\s", "", m["ano"])) if m["ano"] else None
            if m["aa"]:
                aa = int(m["aa"])
                if ano is not None and aa % 100 != ano % 100:
                    continue
                if ano is None:
                    ano = aa if aa > 99 else None
            return {"especie": m["especie"], "imposto": m["imposto"] or "", "numero": int(m["numero"]),
                    "aa": int(m["aa"]) % 100 if m["aa"] else None, "ano": ano,
                    "data": _data(m["dia"], m["mes"], m["ano"]) if m["ano"] else "", "bloco": i}
    return None


# "Aracaju, SE, 24 de setembro de 2004.", "Brasília, 31 de março de 1970.", "Rio de Janeiro (GB), 23 de novembro de
# 1972." e "Teresina, PI, 15 de dezembro 2000." (sem o "de" antes do ano, da fonte).
FECHO = re.compile(r"^[a-z][a-z .'()-]{2,40},(?: ?[a-z]{2} ?,)?(?: em)? ?(\d{1,2})[º°o]? (?:de )?(" + MESES_RE
                   + r") (?:de )?(\d{4}) ?\.?$")
PREAMBULO = re.compile(r"\b(?:no|em|do) dia (\d{1,2})[º°o]? de (" + MESES_RE + r") de (\d{4})\b")


def datas_do_texto(blocos, ano):
    """(datas dos fechos, datas dos preâmbulos), só as do ano do ato, na ordem do texto."""
    fechos, preambulos = [], []
    for n, bloco in enumerate(blocos):
        p = plano(bloco).lower()
        m = FECHO.match(p)
        if m and int(m.group(3)) == ano and _data(*m.groups()):
            fechos.append(_data(*m.groups()))
        if n < 14:  # o preâmbulo vem no alto; "no dia" mais abaixo é o texto de uma cláusula
            for m in PREAMBULO.finditer(p):
                if int(m.group(3)) == ano and _data(*m.groups()) and re.search(r"\breuni|\brealizad|\bcelebra", p):
                    preambulos.append(_data(*m.groups()))
    return fechos, preambulos


PUBLICACAO = re.compile(r"(?i)^[·•\s]*(Publica(?:d[oa]|[çc][ãa]o)\s+(?:n[oa]\s+)?D\.?O\.?U\.?.*)$")


def ler_publicacao(blocos, ano):
    """("Publicado no DOU de 30.09.04.", "2004-09-30") pelo bloco do alto do texto; a data quando é uma data."""
    for bloco in blocos[:9]:
        limpo = re.sub(r"\s+", " ", re.sub(r"[*_\\]", "", bloco)).strip()
        m = PUBLICACAO.match(limpo)
        if not m:
            continue
        texto, data = m.group(1).strip(), ""
        d = re.search(r"D\.?O\.?U\.?,?\s*(?:de|em)?\s*(\d{1,2})[./](\d{1,2})[./](\d{4}|\d{2})\b", texto)
        if d:
            aaaa = int(d.group(3))
            if aaaa < 100:
                aaaa += 1900 if aaaa >= 66 else 2000
            if ano <= aaaa <= ano + 2:
                try:
                    data = dt.date(aaaa, int(d.group(2)), int(d.group(1))).isoformat()
                except ValueError:
                    data = ""
        return texto, data
    return "", ""


INICIO_DO_TEXTO = re.compile(r"^(?:o|a|os|as) (?:conselho|ministr|secretari|estado|govern|conferencia|representante|uniao|distrito)")
NOTA = re.compile(r"(?i)^[·•\s]*(?:publica|ratifica|revogad|sem efic[áa]cia|rejeitad|prorrogad|alterad|vide\b|adesão|adesao|"
                  r"aderid|retifica|republica|dispensad|efeitos|nova reda|reda[çc][ãa]o|exclu[íi]d|inclu[íi]d|denunci|"
                  r"convalida|manifesta|ver\b|\(?a ementa n[ãa]o consta)")


def ler_cabecalho(blocos, inicio):
    """(ementa, notas de situação) entre a epígrafe e o preâmbulo.

    A ementa é o bloco logo antes do preâmbulo ("O Conselho Nacional de Política Fazendária...", "Os Estados de...");
    as notas de situação são as que o portal põe no alto ("Revogado pelo Conv. ICMS 12/90", "Sem eficácia...").
    """
    fim = None
    for n in range(inicio + 1, min(len(blocos), inicio + 30)):
        if INICIO_DO_TEXTO.match(plano(blocos[n]).lower()):
            fim = n
            break
    if fim is None:
        return "", []
    cabecalho = []
    for bloco in blocos[inicio + 1:fim]:
        limpo = re.sub(r"\s+", " ", re.sub(r"[*_\\]", "", bloco)).strip(" ·•")
        # o portal quebra a nota antes do número do ato: "Revogado pelo Conv. ICMS" e, no bloco seguinte, "12/90."
        if cabecalho and re.match(r"^\d{1,4}/\d{2}\b", limpo):
            cabecalho[-1] += " " + limpo
        elif limpo:
            cabecalho.append(limpo)
    ementa = ""
    if cabecalho and not NOTA.match(cabecalho[-1]) and len(cabecalho[-1]) > 25 and not re.match(r"^\d", cabecalho[-1]):
        ementa = cabecalho[-1].strip()
    situacao = [re.sub(r" +([.,;])", r"\1", c) for c in cabecalho if re.match(r"(?i)^(?:revogad|sem efic[áa]cia|rejeitad)", c)]
    return ementa, situacao


def nome_do_tipo(epigrafe, item):
    if epigrafe["especie"] == "ajuste sinief":
        return "Ajuste SINIEF"
    imposto = epigrafe["imposto"].upper()
    return (epigrafe["especie"].replace("convenio", "Convênio").replace("protocolo", "Protocolo")
            + (" " + imposto if imposto else ""))


def montar(item, html):
    """("ok", dados do arquivo) ou ("retido", motivo e detalhe), a partir do HTML da página."""
    corpo_html = corpo_da_pagina(html)
    if not corpo_html:
        return "retido", {"motivo": "página sem o bloco de texto do ato"}
    if re.search(r"<img\b", corpo_html, re.I):
        return "retido", {"motivo": "imagem no corpo do ato: tabela ou modelo que não vira texto"}
    try:
        corpo = convert(corpo_html).strip()
    except ValueError as e:
        return "retido", {"motivo": "o conversor recusou a página", "detalhe": str(e)[:160]}
    blocos = [b for b in corpo.split("\n\n") if b.strip()]
    epigrafe = ler_epigrafe(blocos)
    if not epigrafe:
        return "retido", {"motivo": "epígrafe do ato não reconhecida", "inicio": plano(" / ".join(blocos[:3]))[:160]}
    ano = epigrafe["ano"] or (item["ano"] if epigrafe["aa"] == item["ano"] % 100 else None)
    if (epigrafe["especie"] != sem_acento(SECOES[item["secao"]]).lower() or epigrafe["numero"] != item["numero"]
            or ano != item["ano"] or (item["icm"] and epigrafe["imposto"] != "icm")):
        return "retido", {"motivo": "epígrafe com espécie, número ou ano diferentes dos do endereço",
                          "inicio": plano(blocos[epigrafe["bloco"]])[:160]}
    fechos, preambulos = datas_do_texto(blocos, ano)
    data = epigrafe["data"]
    # o portal erra a data na epígrafe ou no fecho ("DE 1º DE JULHO DE 2022" num ajuste da reunião de 13 de junho,
    # publicado em 14 de junho): as datas que o texto traz têm de concordar
    if data and preambulos and data != preambulos[0]:
        return "retido", {"motivo": "epígrafe e preâmbulo com datas diferentes", "epigrafe": data, "preambulo": preambulos[0]}
    if not data:
        if fechos and preambulos and fechos[0] != preambulos[0]:
            return "retido", {"motivo": "fecho e preâmbulo com datas diferentes", "fecho": fechos[0],
                              "preambulo": preambulos[0]}
        data = (fechos or preambulos or [""])[0]
    if not data:
        return "retido", {"motivo": "data do ato não encontrada na epígrafe, no fecho nem no preâmbulo"}
    publicacao, data_publicacao = ler_publicacao(blocos, ano)
    if data_publicacao and data_publicacao < data:
        return "retido", {"motivo": "publicação no DOU anterior à data do ato", "data": data, "publicacao": publicacao}
    if data_publicacao and (dt.date.fromisoformat(data_publicacao) - dt.date.fromisoformat(data)).days > 180:
        data_publicacao = ""  # "Publicado no DOU 17.12.04" num ajuste de 12.12.03: fica só o texto da nota
    # O ato antigo de dispositivo único não tem cláusula ("Os Estados signatários acordam em conceder suspensão de
    # ICM..."): vale quando o preâmbulo traz o verbo de quem celebra e o fecho repete a data do ato.
    limpo = re.sub(r"[*_\\]", "", corpo)
    unico = data in fechos and re.search(r"(?i)\b(?:resolvem?|acordam|convencionam|celebram)\b", limpo)
    if not re.search(r"(?im)^\W*(?:cl[áa]usula|art(?:igo)?\.?)\s", limpo) and not unico:
        return "retido", {"motivo": "texto sem cláusula nem artigo"}
    tipo = nome_do_tipo(epigrafe, item)
    a, m, d = (int(p) for p in data.split("-"))
    titulo = f"{tipo} nº {item['numero']}, de {'1º' if d == 1 else d} de {NOMES_MES[m - 1]} de {a}"
    ementa, situacao = ler_cabecalho(blocos, epigrafe["bloco"])
    marca = any(plano(b).upper() in ("REVOGADO", "REVOGADA") for b in blocos[:epigrafe["bloco"]])
    # "Revogado pelo Conv. ICMS 60/90" e "Revogado a partir de 02.01.78 pelo Conv. ICM 01/78" são do ato inteiro;
    # "Revogada a cláusula segunda pelo..." é parcial
    revogada = True if marca or any(re.match(r"(?i)^revogad[oa](?:[\s,.]|$)(?! *(?:a|o|as|os) (?!partir\b))", s)
                                    for s in situacao) else None
    meta = [("titulo", titulo), ("orgao", ORGAO), ("tipo", tipo), ("numero", str(item["numero"])), ("data", data)]
    if ementa:
        meta.append(("ementa", ementa))
    meta.append(("revogada", revogada))
    if situacao:
        meta.append(("situacao_fonte", " ".join(situacao)))
    meta.append(("versao_texto", VERSAO))
    if publicacao:
        meta.append(("publicacao", publicacao))
        if data_publicacao:
            meta.append(("data_publicacao", data_publicacao))
    meta += [("fonte", item["url"]), ("sha256_html_fonte", hashlib.sha256(html.encode("utf-8")).hexdigest())]
    slug = f"{sem_acento(tipo).lower().replace(' ', '-')}-{item['numero']}-{ano}"
    return "ok", {"slug": slug, "meta": meta, "corpo": f"# {titulo}\n\n{corpo}\n"}


def caminho_md(item, slug):
    return PASTA / item["secao"] / str(item["ano"]) / f"{slug}.md"


def slugs_possiveis(item):
    """Os nomes de arquivo que o ato pode ter, para pular o que já está no acervo sem ir à rede."""
    base = {"convenios": ["convenio-icm"] if item["icm"] else ["convenio-icms", "convenio-icm", "convenio-ae", "convenio"],
            "protocolos": ["protocolo-icms", "protocolo-icm", "protocolo"], "ajustes": ["ajuste-sinief"]}[item["secao"]]
    return [f"{b}-{item['numero']}-{item['ano']}" for b in base]


def obter(rede, url):
    status, dados, _ = rede.get(url, accept="text/html")
    if status in (401, 403, 429):
        raise Recusa(f"a fonte recusou o acesso (HTTP {status}): {url}")
    return status, dados


def processar(rede, item):
    falha = {"secao": item["secao"], "ano": item["ano"], "numero": item["numero"], "url": item["url"]}
    # a numeração do ICM e a do ICMS correram juntas em 1989: o arquivo que já existe só dispensa a rede quando é
    # deste endereço
    for slug in slugs_possiveis(item):
        md = caminho_md(item, slug)
        if md.exists():
            cabecalho = md.read_text(encoding="utf-8").split("\n---\n", 1)[0].lower()
            if item["url"].lower().rstrip("/") in cabecalho or item["secao"] != "convenios" or item["ano"] != 1989:
                return "pulado", None
    cache = FONTE / item["secao"] / str(item["ano"]) / (item["url"].rsplit("/", 1)[1].lower() + ".html.gz")
    if cache.exists():
        html = gzip.open(cache).read().decode("utf-8", "replace")
    else:
        status, dados = obter(rede, item["url"])
        if status != 200:
            return "retido", {**falha, "motivo": f"a página respondeu HTTP {status}"}
        html = dados.decode("utf-8", "replace")
    estado, r = montar(item, html)
    if estado != "ok":
        cache.parent.mkdir(parents=True, exist_ok=True)
        with gzip.open(cache, "wb") as f:
            f.write(html.encode("utf-8"))
        return "retido", {**falha, **r}
    md = caminho_md(item, r["slug"])
    if md.exists():
        return "retido", {**falha, "motivo": "outro endereço do portal já deu origem ao arquivo deste número"}
    gravar(str(md), str(cache), html.encode("utf-8"), r["meta"], r["corpo"])
    return "ok", None


def registrar(falha, ja):
    chave = (falha["url"], falha["motivo"])
    if chave in ja:
        return
    ja.add(chave)
    FALHAS.parent.mkdir(parents=True, exist_ok=True)
    with open(FALHAS, "a", encoding="utf-8") as f:
        f.write(json.dumps(falha, ensure_ascii=False, sort_keys=True) + "\n")


def carregar_indice(rede, baixar):
    arquivo = INDICE / "sitemap.xml.gz"
    if baixar or not arquivo.exists():
        status, dados = obter(rede, SITEMAP)
        if status != 200:
            raise RuntimeError(f"mapa do site: HTTP {status}")
        INDICE.mkdir(parents=True, exist_ok=True)
        arquivo.write_bytes(dados if dados[:2] == b"\x1f\x8b" else gzip.compress(dados))
    itens, fora = itens_do_sitemap(gzip.open(arquivo).read().decode("utf-8", "replace"))
    (INDICE / "itens.json").write_text(json.dumps(itens, ensure_ascii=False, indent=0) + "\n", encoding="utf-8")
    (INDICE / "fora-do-recorte.json").write_text(json.dumps(fora, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return itens, fora


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--indice", action="store_true", help="baixa o mapa do site de novo e mostra o recorte, sem coletar")
    ap.add_argument("--secoes", default="convenios,protocolos,ajustes")
    ap.add_argument("--de", type=int, default=1966)
    ap.add_argument("--ate", type=int, default=dt.date.today().year)
    ap.add_argument("--despejar", action="store_true", help="mostra o que sairia de cada página, sem gravar o acervo")
    ap.add_argument("--limite", type=int, default=0)
    a = ap.parse_args(argv)
    secoes = [s for s in a.secoes.split(",") if s]
    if any(s not in SECOES for s in secoes):
        ap.error(f"seções válidas: {', '.join(SECOES)}")
    rede = Rede(RPS)
    try:
        itens, fora = carregar_indice(rede, a.indice)
        por_secao = collections.Counter(i["secao"] for i in itens)
        print(f"[CONFAZ] mapa do site: {dict(por_secao)}; fora do recorte: { {k: len(v) for k, v in fora.items()} }", flush=True)
        if a.indice:
            return 0
        alvo = [i for i in itens if i["secao"] in secoes and a.de <= i["ano"] <= a.ate][: a.limite or None]
        cont, ja = collections.Counter(), set()
        if FALHAS.exists():
            ja = {(d.get("url"), d.get("motivo")) for d in map(json.loads, FALHAS.read_text(encoding="utf-8").splitlines())}
        for n, item in enumerate(alvo, 1):
            try:
                if a.despejar:
                    status, dados = obter(rede, item["url"])
                    estado, r = montar(item, dados.decode("utf-8", "replace")) if status == 200 else ("retido", {"motivo": f"HTTP {status}"})
                    print(f"    {item['url'].split('/legislacao/')[1]}: {estado} "
                          + (json.dumps(dict(r["meta"]), ensure_ascii=False)[:420] if estado == "ok" else json.dumps(r, ensure_ascii=False)), flush=True)
                    cont[estado] += 1
                    continue
                estado, falha = processar(rede, item)
            except Recusa:
                raise
            except Exception as e:  # rede ou página malformada: conta e segue
                estado, falha = "erro", None
                print(f"[CONFAZ] erro em {item['url']}: {str(e)[:200]}", flush=True)
            cont[estado] += 1
            if falha:
                registrar(falha, ja)
            if n % 100 == 0 or n == len(alvo):
                print(f"[CONFAZ] {n}/{len(alvo)} {dict(cont)}", flush=True)
    except Recusa as e:
        print(f"[CONFAZ] {e}. Coleta interrompida.", flush=True)
        return 2
    print(f"[CONFAZ] FIM {dict(cont)}", flush=True)
    return 1 if cont["erro"] else 0


if __name__ == "__main__":
    sys.exit(main())
