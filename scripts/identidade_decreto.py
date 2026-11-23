"""Confronto conservador da epígrafe própria de decretos federais numerados.

Não usa citações no articulado, ementas ou fechos como identidade substituta.
Ausência de epígrafe inequívoca retorna None, nunca confirmação de identidade.
"""
import datetime as dt
import re
import unicodedata

MESES = {nome: n for n, nome in enumerate(
    ("JANEIRO", "FEVEREIRO", "MARCO", "ABRIL", "MAIO", "JUNHO", "JULHO",
     "AGOSTO", "SETEMBRO", "OUTUBRO", "NOVEMBRO", "DEZEMBRO"), 1)}
EPIGRAFE = re.compile(
    r"^DECRETO\s+(?:N(?:UMERO)?[.º°O\s]*)?"
    r"(?P<numero>\d[\d.,]*(?:\s*[-–]\s*[A-Z])?)"
    r"\s*[,;:.–—-]*\s*(?:DE\s*)?"
    r"(?P<dia>\d{1,2})[º°]?\s*(?:DE\s*)?(?P<mes>JANEIRO|FEVEREIRO|MARCO|ABRIL|MAIO|JUNHO|JULHO|AGOSTO|SETEMBRO|OUTUBRO|NOVEMBRO|DEZEMBRO)\s*[,;]?\s*(?:DE\s*)?"
    r"(?P<ano>[12]\.?\d{3})(?!\d)"
)


# Epígrafe com defeito de grafia na transcrição da fonte. Só é tentada quando nenhum bloco de abertura casa com
# EPIGRAFE, e não afrouxa a identidade: o número e a data inteira continuam tendo de sair da própria epígrafe. Aceita:
# - a palavra "Decreto" com um erro de digitação ("DECRETA Nº", "DECERTO", "DCRETO", "DECRET0", "DECRETONº") ou
#   seguida de "DE" ("DECRETO DE Nº 43.704");
# - a chamada de nota vazia que sobra do "(*)", antes da palavra ou depois do número ("() DECRETO", "N. 3676 () –");
# - o milhar separado por espaço ("81 444", "13. 112");
# - a letra do número sem hífen ("2038 A", "16.015 A"), menos o "O", que na fonte é zero mal digitado;
# - o sinal de ordinal em caractere de uso privado ("N\uf0b0").
# Entre o número e a data tem de haver espaço ou pontuação: "Decreto de 26 de abril de 2000" não vira o nº 2.
# O dia, o mês e o ano continuam literais: data com defeito ("NOVENBRO", "O5 de fevereiro") fica para a revisão com o
# fecho do próprio decreto (identidade_decreto_revisao.py).
EPIGRAFE_GRAFIA = re.compile(
    r"^(?:\(\s*\)\s*)?(?P<palavra>D[A-Z0]{4,8}?)\s*(?:DE\s+)?(?:N(?:UMERO)?\s*[.º°\uf0b0O]{0,3}\s*)?"
    r"(?P<numero>\d{1,3}(?:[.,]?\s?\d{3})+|\d+)"
    r"(?:\s*[-–]?\s*(?P<letra>[A-NP-Z])(?![A-Z0-9]))?(?:\s*\(\s*\))?"
    r"[\s,;:.–—-]+(?:DE\s*)?"
    r"(?P<dia>\d{1,2})[º°]?\s*(?:DE\s*)?(?P<mes>" + "|".join(MESES) + r")\s*[,;]?\s*(?:DE\s*)?"
    r"(?P<ano>[12]\.?\d{3})(?!\d)"
)


def numero_normalizado(numero):
    return re.sub(r"[.,\s]", "", str(numero)).replace("–", "-").upper()


def _a_um_erro(literal, esperado):
    """Um erro de digitação no máximo: uma letra trocada, a mais ou a menos, ou duas vizinhas invertidas."""
    if literal == esperado:
        return True
    if len(literal) == len(esperado):
        dif = [i for i, (a, b) in enumerate(zip(literal, esperado)) if a != b]
        return len(dif) == 1 or (len(dif) == 2 and dif[1] == dif[0] + 1 and literal[dif[0]] == esperado[dif[1]]
                                 and literal[dif[1]] == esperado[dif[0]])
    if abs(len(literal) - len(esperado)) == 1:
        curto, longo = sorted((literal, esperado), key=len)
        return any(longo[:i] + longo[i + 1:] == curto for i in range(len(longo)))
    return False


def _blocos_de_abertura(corpo):
    """Os primeiros blocos, limpos e em maiúsculas sem acento, até o primeiro artigo: citação posterior não é
    epígrafe."""
    for bloco in corpo.split("\n\n")[:8]:
        limpo = re.sub(r"[*_`\\]", "", bloco).lstrip("# \t\n")
        limpo = re.sub(r"\s+", " ", limpo).strip()
        if re.match(r"^(?:Art\.?|Artigo)\s*(?:\d|[úu]nico)", limpo, re.I):
            break
        yield limpo, "".join(c for c in unicodedata.normalize("NFD", limpo.upper()) if not unicodedata.combining(c))


def extrair_epigrafe_decreto(corpo):
    for limpo, normal in _blocos_de_abertura(corpo):
        match = EPIGRAFE.match(normal)
        if not match or match["mes"] not in MESES:
            continue
        try:
            data = dt.date(int(match["ano"].replace(".", "")), MESES[match["mes"]], int(match["dia"]))
        except ValueError:
            continue
        return {"numero": numero_normalizado(match["numero"]), "data": data.isoformat(),
                "epigrafe": limpo}
    for limpo, normal in _blocos_de_abertura(corpo):
        match = EPIGRAFE_GRAFIA.match(normal)
        if not match or not _a_um_erro(match["palavra"].replace("0", "O"), "DECRETO"):
            continue
        try:
            data = dt.date(int(match["ano"].replace(".", "")), MESES[match["mes"]], int(match["dia"]))
        except ValueError:
            continue
        numero = numero_normalizado(match["numero"]) + ("-" + match["letra"] if match["letra"] else "")
        return {"numero": numero, "data": data.isoformat(), "epigrafe": limpo}
    return None


def divergencia_epigrafe_decreto(tipo, numero, data, corpo):
    if tipo != "DEC-n":
        return None
    encontrada = extrair_epigrafe_decreto(corpo)
    if encontrada is None:
        return None  # inconclusivo; não equivale a epígrafe validada
    esperada = {"numero": numero_normalizado(numero), "data": data}
    if all(encontrada[k] == esperada[k] for k in esperada):
        return None
    return {"motivo": "Epígrafe própria diverge do número/data do índice e URN; revisão necessária; fonte preservada",
            "identidade_esperada": esperada, "epigrafe_encontrada": encontrada}
