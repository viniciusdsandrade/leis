"""Leis orgânicas e emendas integrais em SAPLs municipais oficiais; cache retomável."""
import argparse
import datetime as dt
import hashlib
import fcntl
import json
import re
from pathlib import Path
from urllib.parse import urlsplit
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import Rede, decodificar, documento_para_md, normalizar_chave, yaml_str
from granularidade_sapl import EPIGRAFE, EPIGRAFES_ANTIGAS, alertas_multiplos_atos, alertas_outras_publicacoes, classe, numero_base

RAIZ = Path(__file__).resolve().parent.parent / "municipais"
FONTES = [("Lapa", "PR", "sapl.lapa.pr.leg.br"),
          ("Santo Antônio do Paraíso", "PR", "sapl.santoantoniodoparaiso.pr.leg.br"),
          ("Bariri", "SP", "sapl.bariri.sp.leg.br"),
          ("Registro", "SP", "sapl.registro.sp.leg.br"),
          ("Jardinópolis", "SP", "sapl.jardinopolis.sp.leg.br"),
          ("Igarapava", "SP", "sapl.igarapava.sp.leg.br")]


TRAVAS_HOST = {}
REDES_HOST = {}


def rede_host(host, rps):
    if host not in TRAVAS_HOST:
        pasta = RAIZ / "_indice/organicas-sapl/travas"
        pasta.mkdir(parents=True, exist_ok=True)
        trava = (pasta / (host + ".lock")).open("a")
        fcntl.flock(trava, fcntl.LOCK_EX)
        TRAVAS_HOST[host] = trava
    if host not in REDES_HOST:
        REDES_HOST[host] = Rede(rps=rps)
    return REDES_HOST[host]


def salvar_registro(caminho, registro, codigo, host, modo=None):
    with caminho.with_suffix(".lock").open("a") as trava:
        fcntl.flock(trava, fcntl.LOCK_EX)
        atual = json.loads(caminho.read_text()) if caminho.exists() else registro
        linha = atual.setdefault(str(codigo), registro[str(codigo)])
        linha["estado_descoberta"] = registro[str(codigo)]["estado_descoberta"]
        destino = linha.setdefault("fontes", {}).setdefault(host, {})
        recebido = registro[str(codigo)]["fontes"][host]
        for campo in ("identidade", "estado"):
            if campo in recebido:
                destino[campo] = recebido[campo]
        if modo is not None:
            destino.setdefault(modo, {}).update(recebido.get(modo, {}))
        escrever(caminho, json.dumps(atual, ensure_ascii=False).encode())


def https_mesmo_host(url, host):
    partes = urlsplit(url)
    if partes.hostname != host:
        return url
    return "https://" + host + partes.path + (("?" + partes.query) if partes.query else "")


def texto_integral_alternativo(observacao, host):
    """Um único arquivo oficial no mesmo host, apontado no campo observação do SAPL."""
    hrefs = re.findall(r"""href=["'](https?://[^"']+)["']""", observacao or "", re.I)
    oficiais = []
    for href in hrefs:
        partes = urlsplit(href)
        if partes.hostname != host:
            continue
        if not partes.path.lower().endswith((".html", ".htm", ".pdf", ".doc", ".docx", ".rtf", ".odt")):
            continue
        oficiais.append(https_mesmo_host(href, host))
    unicos = list(dict.fromkeys(oficiais))
    return unicos[0] if len(unicos) == 1 else None


def html_sem_imagens(html):
    return re.sub(r"<img\b[^>]*>", "", html, flags=re.I)


def corpo_de_fonte(bruto, url, content_type=""):
    """Converte o anexo oficial; logotipos em HTML do SIREL não são texto da norma."""
    cabeca = bruto.lstrip()[:15].lower()
    if url.lower().endswith((".html", ".htm")) or cabeca.startswith(b"<html") or cabeca.startswith(b"<!doctype"):
        html = html_sem_imagens(decodificar(bruto, content_type))
        return documento_para_md(html.encode("utf-8"), url, "text/html; charset=utf-8")
    return documento_para_md(bruto, url, content_type)


def categoria_norma(tipo, norma=None):
    t = normalizar_chave(tipo)
    if re.search(r"projeto|proposta|requerimento|indicacao|veto|mensagem|parecer", t):
        return None
    if re.search(r"\bleis? delegadas?\b", t):
        return None  # tipo distinto; não rotular silenciosamente como lei ordinária
    if "organica" in t or t == "loman" or t == "emenda a loman":
        return ("emendas-lei-organica", "Emenda à Lei Orgânica") if "emenda" in t else ("lei-organica", "Lei Orgânica")
    if "decreto legislativo" in t:
        return "decretos-legislativos", "Decreto legislativo"
    if re.search(r"decreto[ -]?lei\b", t):
        # municipais do Estado Novo: ficam com os decretos do plano, sem perder o tipo
        return "decretos", "Decreto-Lei"
    if "decreto" in t:
        return "decretos", "Decreto"
    if re.search(r"resoluc(?:ao|oes)", t):  # "Resoluções Até 1948" (Campinas) no plural
        return "resolucoes", "Resolução"
    if re.search(r"\bleis?\b|codigo", t):  # "Leis Até 1948" (Campinas) no plural
        e = normalizar_chave((norma or {}).get("ementa", ""))
        if re.match(r"(?:institui|aprova|dispoe sobre) (?:o |a |um |uma )?(?:novo )?plano diretor", e):
            return "plano-diretor", "Plano diretor"
        if re.match(r"(?:institui|aprova|dispoe sobre) (?:o |a |um |uma )?(?:novo )?codigo tributario", e):
            return "codigo-tributario", "Código tributário"
        if re.match(r"(?:institui|aprova|dispoe sobre) (?:o |a |um |uma )?(?:novo )?codigo (?:de obras|de posturas|de zoneamento)", e):
            return "codigos", "Código municipal"
        return ("leis-complementares", "Lei complementar") if "complementar" in t else ("leis-ordinarias", "Lei ordinária")
    return None


def escrever(p, b):
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_name(p.name + ".tmp")
    tmp.write_bytes(b)
    tmp.replace(p)


# OCR de atos digitalizados: "Artigo 1º -" sai como "Artigo 19 -" ou "Artigo 10-" (decretos legislativos de Campinas,
# 1990 e 1991) e o rótulo às vezes perde letras ("Atigo 1.o -"). Vale só para o primeiro rótulo de artigo do texto,
# logo depois da fórmula de promulgação: um texto que começasse no meio não passaria.
ROTULO_ARTIGO_OCR = re.compile(r"(?i)\b(?:Art(?:igo)?|Atigo|Arigo|Artgo)\W{0,3}(\d{1,2})\s*(?:[º°ª]|\.?\s*o)?\s*[-–—]")
FORMULA_DE_PROMULGACAO = re.compile(r"(?i)promulg|decreta|resolve|sancion|seguinte\s+(?:lei|decreto|resolu)")


def corpo_integral_reconhecivel(corpo, emenda=False):
    # "Arti. 1º" e "Art . 1°" são erros de digitação da fonte; "Art. 10" e "Art. 12" não são o primeiro artigo
    if re.search(r"art(?:i|igo)?\s*\.?\s*1(?:[º°o]|\b)|art(?:igo|\.)\s*[úu]nico", corpo, re.I):
        return True
    if corpo.startswith("> Texto obtido por OCR"):
        rotulo = ROTULO_ARTIGO_OCR.search(corpo)
        if (rotulo and rotulo[1] in ("1", "19", "10")
                and FORMULA_DE_PROMULGACAO.search(corpo[max(0, rotulo.start() - 300):rotulo.start()])):
            return True
    # o OCR de leis digitalizadas lê "Artigo 1º" como "Antigo 1º" (Campinas, 1985 e 1990); só vale como
    # rótulo no começo da linha e seguido do separador do dispositivo, para não confundir com "antigo 1º Distrito"
    if re.search(r"(?m)^\W*Antigo\s*1\s*[º°o]\s*[-–—\u00ad.]", corpo):
        return True
    # Algumas emendas transcrevem primeiro o artigo que alteram; o próprio ato
    # usa PROMULGA/PROMULGAM e traz sua cláusula de vigência, sem um Art. 1º.
    # Não corrige nem adivinha numeração eventualmente reconhecida por OCR.
    promulga = re.search(r"\bpromulg(?:o|a|am|amos)\b", corpo, re.I) if emenda and len(corpo) > 500 else None
    if not promulga:
        return False
    # Sem cláusula de vigência, vale a assinatura de encerramento depois da promulgação
    # (data seguida de Presidente da Mesa): o texto chega ao fim do ato. Citar o
    # Presidente no texto transcrito não basta.
    assinatura = re.search(r"\d{1,2}º?\.? de \w+ de \d[\d.]*\W.{0,120}?\bPresidente\b", corpo[promulga.end():], re.I | re.S)
    return bool(re.search(r"vigorar|vigor", corpo, re.I) or assinatura)


TEXTO_DE_OUTRA_NORMA = Path(__file__).resolve().parent / "dados/sapl-texto-de-outra-norma.json"


def texto_de_outra_norma(host, identificador):
    """PDF anexado à norma errada no SAPL: esta norma usa o texto anexado a outra, conferido pelo SHA-256."""
    if not TEXTO_DE_OUTRA_NORMA.exists():
        return None
    return json.loads(TEXTO_DE_OUTRA_NORMA.read_text()).get(host, {}).get(str(identificador))


def motivo_retencao(cache, identificador, bruto):
    path = cache / "retidos-integralidade.json"
    if not path.exists():
        return None
    registro = json.loads(path.read_text()).get(str(identificador))
    if registro and registro.get("sha256_fonte") == hashlib.sha256(bruto).hexdigest():
        return registro["motivo"]
    return None


def data_diverge_do_ano(norma):
    """A data do cadastro é de outro ano, mas o ano da norma e o da publicação concordam entre si.

    Erro de digitação na data (Campinas: Lei 11.551 "de 05/03/2000", publicada em 13/05/2003 e
    assinada em 12/05/2003): a data e a pasta sairiam erradas. Não corrige; retém para revisão.
    """
    data, ano = norma.get("data") or "", str(norma["ano"])
    return bool(data) and data[:4] != ano and str(norma.get("data_publicacao") or "")[:4] == ano


MESES_PT = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
DATA_POR_EXTENSO = re.compile(r"(?i)\bDE\s+(\d{1,2})[º°o]?\s+DE\s+([A-Za-zÇçÃãÉé]+)\s+DE\s+(\d)\.?(\d{3})\b")


def data_da_epigrafe(corpo, norma):
    """Data por extenso da epígrafe, quando corrige um erro de ano no cadastro.

    Campinas, Lei 11.481: cadastro "2002-03-14", mas a norma é de 2003, a epígrafe diz "DE 14 DE MARÇO DE 2003"
    e a publicação foi em 15/03/2003. Vale a primeira data por extenso do texto, se tem o ano da norma e a
    publicação veio de 0 a 60 dias depois dela; senão None, e a norma continua retida.
    """
    m = DATA_POR_EXTENSO.search(corpo[:800])
    if not m:
        return None
    mes = next((i for i, nome in enumerate(MESES_PT, 1) if normalizar_chave(m[2])[:3] == normalizar_chave(nome)[:3]), None)
    try:
        data = dt.date(int(m[3] + m[4]), mes or 0, int(m[1]))
        publicacao = dt.date.fromisoformat(str(norma.get("data_publicacao") or ""))
    except ValueError:
        return None
    if str(data.year) != str(norma["ano"]) or not 0 <= (publicacao - data).days <= 60:
        return None
    return data.isoformat()


def titulo_com_data(titulo, data_iso):
    """Troca a data do título do SAPL ("Lei nº 11.481, de 14 de março de 2002") pela data corrigida."""
    d = dt.date.fromisoformat(data_iso)
    nova = f", de {d.day:02d} de {MESES_PT[d.month - 1]} de {d.year}"
    padrao = r",\s*de\s+\d{1,2}\s+de\s+\w+\s+de\s+\d{1,4}\s*$"
    return re.sub(padrao, nova, titulo) if re.search(padrao, titulo) else titulo + nova


CARIMBO_CAMPINAS = [
    # nas leis de 2002 a capa ainda não tinha a Diretoria de Gestão Documental
    re.compile(r"(?:CÂMARA MUNICIPAL DE CAMPINAS (?:Estado de São Paulo )?)?(?:Diretoria de Gestão Documental )?Coordenadoria de Biblioteca "
               r"\S+@campinas\.sp\.leg\.br(?: –| -)? ?(?:Ramal:? ?\d+)?"),
    # o OCR lê os travessões como hífen; às vezes sob um fio de sublinhados ("\_\_\_ Avenida...")
    re.compile(r"(?:(?:\\_)+ )?Avenida da Saudade, n[º°] 1\.?004 [–-] Ponte Preta [–-] CEP: 13041-670 [–-] Campinas [–-] SP [–-] PABX: \(19\) 3736- ?1300\.?(?: www\.campinas\.sp\.leg\.br)?"),
]
# a fonte tem erros de grafia nesta linha ("Municipio", "Municípo", "Campina"); a data também varia ("1º de outubro", "novembrode")
AVISO_NAO_SUBSTITUI_CAMPINAS = re.compile(
    r"Texto somente para consulta\. Não substitui o publicado (?:no|na Edição Extra do) Diário Oficial do Munic\w+(?: de Campinas?)? em \d{1,2}º? de \w+ ?de \d{4}")
AVISO_NAO_SUBSTITUI_DOCM_CAMPINAS = re.compile(
    r"Texto somente para consulta\. Não substitui o publicado n[oa] Diário Oficial da Câmara Municipal de Campinas em \d{1,2}º? de \w+ ?de \d{4}")
AVISO_REPRODUZIDO_CAMPINAS = re.compile(
    r"Texto para consulta, reproduzido conforme (?:a )?publicação(?: extra)? (?:no|do) Diário Oficial do Município(?: em \d{1,2}º? de \w+ ?de \d{4})?")
# resolução de 1967: só "Texto para consulta", sem dizer de onde
AVISO_CONSULTA_SO_CAMPINAS = re.compile(r"Texto para consulta\.?")
# resoluções de 2022: reproduzido conforme o Diário Oficial da Câmara, não o do Município
AVISO_REPRODUZIDO_DOCM_CAMPINAS = re.compile(
    r"Texto para consulta, reproduzido conforme (?:a )?publicação (?:no|do) Diário Oficial da Câmara Municipal de Campinas,? em \d{1,2}º? de \w+ ?de \d{4}")
# família geral do aviso de consulta (decretos legislativos de 2021 a 2026): "(re)publicado/(re)publicação",
# "no/na" (que falta em decretos de 2022), edição extra(ordinária) e o Diário Oficial do Município, da Câmara
# ou do Legislativo; só depois das variantes acima, para não mudar as notas que elas já dão
AVISO_CONSULTA_FAMILIA_CAMPINAS = re.compile(
    r"Texto (?:somente )?para consulta[.,] (?P<forma>Não substitui o (?P<re1>re)?publicado|reproduzido conforme (?:a )?(?P<re2>re)?publicação) "
    r"(?:n[oa] )?(?:Edição Extra(?:ordinária)? do )?Diário Oficial (?P<orgao>do Município(?: de Campinas)?|da Câmara(?: Municipal)? de Campinas|do Legislativo),? "
    r"em ?\d{1,2}º? de \w+ ?de \d{4}")


def nota_aviso_consulta(m):
    orgao = "do Município" if m["orgao"].startswith("do Município") else "da Câmara Municipal"
    if m["forma"].startswith("Não substitui"):
        return f"cópia de consulta da Câmara, não substitui o Diário Oficial {orgao}"
    return f"cópia de consulta da Câmara, reproduzida conforme a {'re' if m['re2'] else ''}publicação no Diário Oficial {orgao}"


# nas leis de 1954 o aviso para em "publicação", sem dizer onde
AVISO_REPRODUZIDO_SEM_FONTE_CAMPINAS = re.compile(r"Texto para consulta, reproduzido conforme (?:a )?publicação\.?")
# às vezes sob um fio de sublinhados, que o conversor escapa como "\_"
AVISO_SEM_VALOR_LEGAL_CAMPINAS = re.compile(
    r"(?:(?:\\_)+ )?Texto somente para (?:consulta|leitura), sem valor legal(?:, reproduzido de acordo com a publicação oficial)?\.?")
# nas leis de 1968 o aviso vem colado ao fim do último parágrafo, depois da assinatura
AVISO_COLADO_NO_FIM_CAMPINAS = re.compile(r"\s+Texto somente para consulta, sem valor legal\.?$")
# leis de 1995 copiadas do site da Prefeitura: o aviso diz de onde veio a compilação
AVISO_COMPILADO_PMC_CAMPINAS = re.compile(r"Texto somente para consulta, sem valor legal, COMPILADO do site da P\.M\.C\.?")
# cabeçalho de cada folha dos PDFs antigos; o total some em alguns ("CÂMARA MUNICIPAL DE CAMPINAS 10/") e há folhas sem contador.
# Anexos copiados de suplementos do Diário Oficial trazem o cabeçalho corrente dele, com número de folha e às vezes a data.
PAGINA_CAMPINAS = re.compile(
    r"CÂMARA MUNICIPAL DE CAMPINAS(?: \d+/\d*)?"
    r"|(?:\d+ )?Diário Oficial do Município de Campinas(?: Campinas, \w+-feira, \d{1,2} de \w+ de \d{4})?(?: \d+)?(?: PREF[EI]TURA MUNICIPAL DE CAMPINAS)?")
# Texto tirado do Diário Oficial em PDF: o cabeçalho corrente da folha seguinte ("Campinas, segunda-feira,
# 24 de setembro de 2012 Diário Oficial do Município de Campinas 5") cai no meio da frase que passa de folha
CABECALHO_DOM_NA_FRASE_CAMPINAS = re.compile(
    r"\s*Campinas, \w+-feira, \d{1,2} de \w+ de \d{4} Diário O(?:ﬁ|fi)cial do Município de Campinas \d+(?:\s+|$)")
# com o rodapé tirado como linha repetida, o cabeçalho com contador se cola ao que vem depois na mesma folha
# ("CÂMARA MUNICIPAL DE CAMPINAS 1/18 Publicada no Diário Oficial..."); sem o contador, não há como distinguir do texto
PAGINA_NO_INICIO_CAMPINAS = re.compile(r"CÂMARA MUNICIPAL DE CAMPINAS \d+/\d* (?=\S)")
# número de página de livro de leis impresso, às vezes duas por linha ("- 58 - - 59 -")
MARCA_PAGINA_CAMPINAS = re.compile(r"(?:-\s*\d{1,3}\s*-\s*)+")
SUPLEMENTO_CAMPINAS = re.compile(r"TABELAS? [^.\n]{0,80}PUBLICADAS? EM SUPLEMENTO", re.I)
CONTADOR_FOLHA = re.compile(r"(\d+)/(\d+)")


def contadores_de_folha(paragrafos):
    """Parágrafos que são só o contador de folha ("2/19").

    Em PDFs de 2014 a 2017 o cabeçalho vem como "CÂMARAMUNICIPAL DE CAMPINAS" e o contador na linha de baixo;
    o conversor tira o cabeçalho como linha repetida e o contador fica sozinho. Só conta como contador a
    sequência: dois ou mais, começando em 1, crescentes e com o mesmo total (uma fração solta no texto fica).
    Quando as primeiras folhas trazem o contador colado ao cabeçalho, que sai com ele, a sequência solta começa
    depois ("10/135"); aí valem três ou mais seguidos. Um "1/1" sozinho é a folha única do documento.
    """
    achados = [(i, CONTADOR_FOLHA.fullmatch(p.strip())) for i, p in enumerate(paragrafos)]
    achados = [(i, int(m[1]), int(m[2])) for i, m in achados if m]
    folhas = [k for _, k, _ in achados]
    totais = {t for _, _, t in achados}
    seguidos = all(b == a + 1 for a, b in zip(folhas, folhas[1:]))
    if (len(achados) >= 2 and len(totais) == 1 and folhas[-1] <= min(totais)
            and all(a < b for a, b in zip(folhas, folhas[1:]))
            and (folhas[0] == 1 or len(folhas) >= 3 and seguidos)):
        return {i for i, _, _ in achados}
    if len(achados) == 1 and folhas == [1] and totais == {1}:
        return {achados[0][0]}
    return set()


def frase_continua_na_pagina_seguinte(anterior, proximo):
    """A folha terminou no meio da frase: último termo em minúscula, sem pontuação final, e o próximo não abre dispositivo."""
    termos = anterior.split()
    return bool(termos and re.match(r"[a-zà-ú]", termos[-1]) and not anterior.rstrip().endswith(tuple('.;:!?"”)'))
                and not proximo.startswith(("**", "#")))


def limpar_carimbo_campinas(corpo):
    """Remove só os carimbos da biblioteca da Câmara (parágrafo inteiro, correspondência exata).

    Retorna (corpo, notas): o aviso da cópia de consulta e os anexos em suplemento vão para `versao_texto`.
    Onde o cabeçalho de folha cai no meio de uma frase, ele sai e a frase é reunida.
    """
    mantidos, notas = [], []
    quebra_de_pagina = False
    # espaço de largura zero é artefato de cópia do Word ("\u200bcaput"): invisível, mas quebra a busca.
    # Retorno de carro solto não tem função em Markdown e faz a auditoria em disco (read_text) recalcular outro hash.
    paragrafos = corpo.replace("\u200b", "").replace("\r\n", "\n").replace("\r", "\n").split("\n\n")
    contadores = contadores_de_folha(paragrafos)
    for i, par in enumerate(paragrafos):
        if CABECALHO_DOM_NA_FRASE_CAMPINAS.search(par):
            par = CABECALHO_DOM_NA_FRASE_CAMPINAS.sub(" ", par).strip()
            if not par:
                quebra_de_pagina = True
                continue
        plano = re.sub(r"\s+", " ", par).strip()
        capa = CARIMBO_CAMPINAS[0].match(plano)
        if capa:  # a capa pode vir fundida com o aviso no mesmo parágrafo
            plano = par = plano[capa.end():].strip()
            if not plano:
                continue
        cabecalho = PAGINA_NO_INICIO_CAMPINAS.match(plano)
        if cabecalho:
            plano = par = plano[cabecalho.end():]
            quebra_de_pagina = True
        if PAGINA_CAMPINAS.fullmatch(plano) or i in contadores or MARCA_PAGINA_CAMPINAS.fullmatch(plano):
            quebra_de_pagina = True
            continue
        if AVISO_NAO_SUBSTITUI_CAMPINAS.fullmatch(plano):
            notas.append("cópia de consulta da Câmara, não substitui o Diário Oficial do Município")
        elif AVISO_NAO_SUBSTITUI_DOCM_CAMPINAS.fullmatch(plano):
            notas.append("cópia de consulta da Câmara, não substitui o Diário Oficial da Câmara Municipal")
        elif AVISO_REPRODUZIDO_CAMPINAS.fullmatch(plano):
            notas.append("cópia de consulta da Câmara, reproduzida conforme a publicação no Diário Oficial do Município")
        elif AVISO_CONSULTA_SO_CAMPINAS.fullmatch(plano):
            notas.append("cópia de consulta da Câmara")
        elif AVISO_REPRODUZIDO_DOCM_CAMPINAS.fullmatch(plano):
            notas.append("cópia de consulta da Câmara, reproduzida conforme a publicação no Diário Oficial da Câmara Municipal")
        elif AVISO_REPRODUZIDO_SEM_FONTE_CAMPINAS.fullmatch(plano):
            notas.append("cópia de consulta da Câmara, reproduzida conforme a publicação")
        elif AVISO_SEM_VALOR_LEGAL_CAMPINAS.fullmatch(plano):
            notas.append("cópia de consulta da Câmara, sem valor legal")
        elif AVISO_COMPILADO_PMC_CAMPINAS.fullmatch(plano):
            notas.append("cópia de consulta sem valor legal, compilada do site da Prefeitura Municipal de Campinas")
        elif AVISO_CONSULTA_FAMILIA_CAMPINAS.fullmatch(plano):
            notas.append(nota_aviso_consulta(AVISO_CONSULTA_FAMILIA_CAMPINAS.fullmatch(plano)))
        elif not any(r.fullmatch(plano) for r in CARIMBO_CAMPINAS):
            if quebra_de_pagina and mantidos and frase_continua_na_pagina_seguinte(mantidos[-1], par):
                mantidos[-1] = mantidos[-1] + " " + par
            else:
                mantidos.append(par)
            quebra_de_pagina = False
    colado = AVISO_COLADO_NO_FIM_CAMPINAS.search(mantidos[-1]) if mantidos else None
    if colado and mantidos[-1][:colado.start()].strip():
        mantidos[-1] = mantidos[-1][:colado.start()]
        if "cópia de consulta da Câmara, sem valor legal" not in notas:
            notas.append("cópia de consulta da Câmara, sem valor legal")
    corpo = "\n\n".join(mantidos)
    if SUPLEMENTO_CAMPINAS.search(corpo):
        notas.append("tabelas e anexos publicados em suplemento, ausentes do texto integral")
    return corpo, notas


# Página inteira do Diário Oficial do Município (layout de 2011 em diante) anexada no lugar do ato: traz o
# cabeçalho da edição ("Nº 10.534 - Ano XLII Diário Oficial Quinta-feira, 27 de dezembro de 2012 Prefeitura
# Municipal de Campinas") ou o rodapé do expediente, e outros atos nas colunas. O ato copiado de suplemento do
# DOM traz só o cabeçalho corrente da folha, que limpar_carimbo_campinas já trata.
PAGINA_DOM_CAMPINAS = re.compile(
    r"Ano\s+[XLVI]+\s+Di[áa]rio Oficial\s+\w+-feira,?\s+\d{1,2} de \w+ de \d{4}"
    r"|Di[áa]rio Oficial\s+\w+-feira,?\s+\d{1,2} de \w+ de \d{4}\s+(?:Prefeitura Municipal de Campinas|PODER EXECUTIVO)"
    r"|Recebimento de (?:mat[ée]rias|conte[úu]do) para publica[çc][ãa]o at[ée]")


def pagina_do_diario_oficial_campinas(corpo):
    return bool(PAGINA_DOM_CAMPINAS.search(corpo))


def inicio_do_texto(corpo, n=600):
    """Primeiros n caracteres do corpo, sem o aviso de OCR."""
    texto = re.sub(r"^> Texto obtido por OCR[^\n]*\n+", "", corpo)
    return texto[:n]


def numero_proprio_no_inicio(corpo, numero):
    """O número da norma aparece no começo do texto (identidade do anexo).

    Campinas: o SAPL anexa às vezes o PDF da norma vizinha, ou a página inteira do Diário Oficial, e o OCR de
    scanner em paisagem pode embaralhar a epígrafe ("COCETO SATO N 347" para o Decreto Legislativo 3.472).
    Compara o número sem pontos de milhar com os números do começo do texto; "3.472" e "3472" valem igual.
    """
    base = numero_base(numero)
    if not base:
        return True
    inicio = inicio_do_texto(corpo, 700)
    numeros = {re.sub(r"\.", "", m).lstrip("0") or "0" for m in re.findall(r"\d[\d.]*", inicio)}
    return base in numeros


# a epígrafe de granularidade_sapl só casa no começo da linha; aqui ela é procurada em qualquer posição
EPIGRAFE_SOLTA = re.compile(EPIGRAFE.pattern.replace(r"^(?:\s*[*#]+\s*)?", "", 1), re.I | re.M)


def epigrafe_propria_no_meio_da_frase(corpo, tipo, numero):
    """Página do Diário Oficial em duas colunas entrelaçadas pelo conversor: a epígrafe da própria norma cai no meio
    de uma frase da coluna vizinha ("...fixadas com base nas operações contratadas até a data DECRETO Nº 19.938 DE 25
    DE JUNHO DE 2018 do encaminhamento..."). A nota de publicação, carimbos e contadores antes da epígrafe na mesma
    linha terminam em data ou número, não em palavra minúscula."""
    esperada = (classe(tipo), numero_base(numero))
    inicio = inicio_do_texto(corpo, 700)
    for m in EPIGRAFE_SOLTA.finditer(inicio):
        if (classe(m["tipo"]), numero_base(m["numero"])) == esperada:
            antes = inicio[inicio.rfind("\n\n", 0, m.start()) + 2:m.start()]
            return bool(re.search(r"[a-zà-ú]{2,}\W*$", antes))
    return False


# Recorte de um ato em página de livro de leis (Campinas, até 1948). As páginas trazem o fim do ato anterior, o ato e o
# começo do seguinte; nos livros de 1909 a 1923 o preâmbulo ("O doutor X, Prefeito..., Faço saber que a Camara decretou e
# eu promulgo a seguinte") vem antes da epígrafe, nos de 1931 em diante vem depois dela.
FECHO_DE_LIVRO = re.compile(
    r"(?i)(?:Campinas|Pa[çc]o Municipal|Pal[aá]cio Municipal|Intend[êe]ncia)[^\n]{0,40}?,?\s+(?:aos?\s+|em\s+)?(\d{1,2})\s+de\s+([A-Za-zçÇ]+)\s+de\s+(\d{4})")
# preâmbulo do ato seguinte sem separador antes dele ("O Secretario, Amilar Alves Orosimbo Maia, Prefeito Municipal de
# Campinas, etc. Faco saber..."): não dá para saber onde acaba o nome do secretário, então a página fica retida
PREAMBULO_COLADO = re.compile(r"(?is)\b(?:Prefeito|Intendente|Vice-Prefeito)\s+Municipal\b.{0,200}?(?:saber|seguinte|decret|promulg)")
PREAMBULO_DO_ATO_SEGUINTE = re.compile(
    r"(?is)(?<=[.\n•·])\s*(?:(?:O|A)\s+)?(?:Dr\.?\s+|[Dd]outor\s+|[Cc]idad[ãa]o\s+)?[A-ZÁ-Ú][^.•·,]{0,60}?,?\s*\b(?:Prefeito|Intendente|Vice-Prefeito)\b(?=.{0,200}?(?:saber|seguinte|decret|promulg)).{0,300}$")
# tabela de orçamento da coluna vizinha que vaza para o recorte ("0$000 O DIRETOR, 0$000 ADMAR MAIA 0$000 5$000")
QUANTIA_ANTIGA = re.compile(r"\d+[$S]\d{3}")
ATO_FINANCEIRO = re.compile(r"(?i)or[çc]a|receita|despe[sz]a|cr[eé]dito|imposto|taxa|vencimento|ordenado|sal[aá]rio|aux[ií]lio|subven|pagamento|verba|emprestimo|empr[eé]stimo|cont[ao]s?\b|quantia|r[eé]is")
ROTULO_ARTIGO_DE_LIVRO = re.compile(r"(?m)^\W*\**(?:Art(?:igo)?|Ar[tl])[.,]?\s*(\d{1,2})")
ROTULO_PARAGRAFO_DE_LIVRO = re.compile(r"(?m)^\W*\**§\s*(\d{1,2})")


def epigrafes_da_pagina(corpo):
    """Epígrafes antigas e modernas da página, uma por posição inicial: lista de (inicio, identidade)."""
    por_inicio = {}
    for rx in (EPIGRAFE, *EPIGRAFES_ANTIGAS):
        for m in rx.finditer(corpo):
            por_inicio.setdefault(m.start(), (classe(m["tipo"]), numero_base(m["numero"])))
    return sorted(por_inicio.items())


def data_de_fecho(m):
    mes = next((i for i, nome in enumerate(MESES_PT, 1) if normalizar_chave(m[2])[:3] == normalizar_chave(nome)[:3]), None)
    try:
        return dt.date(int(m[3]), mes or 0, int(m[1])).isoformat()
    except ValueError:
        return None


def recortar_ato_de_livro(corpo, tipo, numero, data_cadastro):
    """Recorta o ato da página de livro de leis: da epígrafe própria até antes da epígrafe do ato seguinte.

    Retém (RuntimeError com o motivo) quando a epígrafe própria não aparece exatamente uma vez, quando não há
    fecho com data dentro do recorte (o ato continua na página seguinte, que não está no PDF), quando a data do
    fecho não bate com o cadastro, ou quando os artigos e parágrafos que abrem parágrafo saem de ordem (OCR que
    entrelaçou as duas colunas da página). O preâmbulo do ato seguinte, quando vem antes da epígrafe dele, é
    aparado. Devolve (recorte, data_do_fecho); o aviso de OCR da página é preservado no começo do recorte.
    """
    aviso = ""
    if corpo.startswith(AVISO_OCR_INICIO):
        aviso, _, corpo = corpo.partition("\n")
        aviso += "\n\n"
        corpo = corpo.lstrip("\n")
    esperada = (classe(tipo), numero_base(numero))
    epigrafes = epigrafes_da_pagina(corpo)
    proprias = [ini for ini, ident in epigrafes if ident == esperada]
    if len(proprias) != 1:
        raise RuntimeError(f"página de livro de leis: a epígrafe da norma aparece {len(proprias)} vez(es) no texto; recorte impossível, revisar")
    ini = proprias[0]
    fim = min((i for i, _ in epigrafes if i > ini), default=len(corpo))
    recorte = corpo[ini:fim]
    fechos = [(m, data_de_fecho(m)) for m in FECHO_DE_LIVRO.finditer(recorte)]
    if not fechos:
        raise RuntimeError("página de livro de leis: sem fecho datado dentro do recorte; o ato continua na página seguinte, que não está no PDF; revisar")
    datas = {d for _, d in fechos if d}
    if data_cadastro and data_cadastro not in datas:
        raise RuntimeError(f"página de livro de leis: data do fecho ({', '.join(sorted(datas)) or '?'}) não bate com o cadastro ({data_cadastro}); revisar")
    artigos = [int(x) for x in ROTULO_ARTIGO_DE_LIVRO.findall(recorte)]
    if artigos != sorted(artigos) or (artigos and artigos[0] != 1):
        raise RuntimeError("página de livro de leis: artigos fora de ordem no recorte (colunas entrelaçadas pelo OCR); revisar")
    paragrafos = [int(x) for x in ROTULO_PARAGRAFO_DE_LIVRO.findall(recorte)]
    if paragrafos != sorted(paragrafos):
        raise RuntimeError("página de livro de leis: parágrafos fora de ordem no recorte (colunas entrelaçadas pelo OCR); revisar")
    ultimo_fecho = fechos[-1][0]
    if artigos:
        ultimo_artigo = list(ROTULO_ARTIGO_DE_LIVRO.finditer(recorte))[-1]
        if ultimo_fecho.start() < ultimo_artigo.start():
            raise RuntimeError("página de livro de leis: fecho antes do último artigo (colunas entrelaçadas pelo OCR); revisar")
    cauda = recorte[ultimo_fecho.end():]
    m = PREAMBULO_DO_ATO_SEGUINTE.search(cauda)
    if m:
        recorte = recorte[:ultimo_fecho.end() + m.start()]
    if PREAMBULO_COLADO.search(recorte[ultimo_fecho.end():]):
        raise RuntimeError("página de livro de leis: preâmbulo do ato seguinte colado ao fecho, sem separador que permita apará-lo; revisar")
    if len(QUANTIA_ANTIGA.findall(recorte)) >= 3 and not ATO_FINANCEIRO.search(recorte):
        raise RuntimeError("página de livro de leis: quantias de tabela da coluna vizinha dentro do recorte de ato sem matéria financeira (colunas entrelaçadas pelo OCR); revisar")
    return aviso + recorte.strip().rstrip(" •·-–—") + "\n", fechos[-1][1]


def abre_com_a_propria_epigrafe(corpo, tipo, numero):
    """Páginas dos livros de leis antigos (Campinas, até 1948): a epígrafe da própria norma tem que abrir a
    página. Se abre com o fim do ato anterior, publicar a página inteira publicaria texto de outra norma."""
    esperada = (classe(tipo), numero_base(numero))
    inicio = inicio_do_texto(corpo, 300)
    for rx in (EPIGRAFE, *EPIGRAFES_ANTIGAS):
        for m in rx.finditer(inicio):
            if (classe(m["tipo"]), numero_base(m["numero"])) == esperada:
                return True
    return False


PALAVRA = re.compile(r"[a-záàâãéêíóôõúüç]{3,}")
AVISO_OCR_INICIO = "> Texto obtido por OCR"


def lexico_do_municipio(pasta_municipio, cache):
    """Palavras dos textos já publicados do município sem OCR, presentes em três ou mais atos; guardado no cache."""
    destino = cache / "lexico-municipio.json"
    if destino.exists():
        return set(json.loads(destino.read_text()))
    docs = {}
    for p in pasta_municipio.glob("**/*.md"):
        corpo = p.read_text().split("\n---\n", 1)[-1]
        if AVISO_OCR_INICIO in corpo:
            continue
        for w in set(PALAVRA.findall(corpo.lower())):
            docs[w] = docs.get(w, 0) + 1
    lexico = sorted(w for w, n in docs.items() if n >= 3)
    escrever(destino, json.dumps(lexico, ensure_ascii=False).encode())
    return set(lexico)


def legibilidade(corpo, lexico):
    """Fração das palavras de quatro ou mais letras do texto que estão no léxico; None com menos de 20 palavras.

    OCR de scanner ruim (Campinas, decretos legislativos de 2011 e 2012) perde artigos inteiros e deixa frases
    sem sentido ("CONCENTRO COMUNARO DA CRANCA"); os textos sem OCR do acervo ficam acima de 0,94 e o OCR limpo
    dos anos 1990 perto de 0,93.
    """
    palavras = [w for w in PALAVRA.findall(corpo.lower()) if len(w) >= 4]
    if len(palavras) < 20:
        return None
    return sum(1 for w in palavras if w in lexico) / len(palavras)


LEGIBILIDADE_MINIMA = 0.85


def esfera_municipal(descricao):
    """Recusa tipos Sirel/federal/estadual misturados em catálogos municipais."""
    tokens = set(normalizar_chave(descricao).split())
    return not tokens.intersection({"sirel", "federal", "estadual"})


def tipo_selecionado(descricao, modo, categorias):
    if not esfera_municipal(descricao):
        return False
    cat = categoria_norma(descricao)
    if not cat:
        return False
    if categorias:
        return cat[0] in categorias
    return modo == "legislacao" or cat[0] in ("lei-organica", "emendas-lei-organica")


def executar(fontes, rps, modo="organicas", max_documentos=0, ano_filtro=None, siglas=(), categorias=None, ano_minimo=0):
    ibge = json.loads((RAIZ / "_indice/ibge-municipios.json").read_text())
    registro_path = RAIZ / "_indice/organicas-sapl/municipios.json"
    registro = json.loads(registro_path.read_text()) if registro_path.exists() else {
        str(x["id"]): {"municipio": x["nome"], "uf": x["regiao-imediata"]["regiao-intermediaria"]["UF"]["sigla"],
                       "estado_descoberta": "fonte ainda não localizada", "fontes": {}} for x in ibge}
    erros = 0
    for nome, uf, host in fontes:
        rede = rede_host(host, rps)
        cache = RAIZ / "_indice/organicas-sapl" / host
        def obter(url, destino):
            if destino.exists():
                return destino.read_bytes()
            st, b, ct = rede.get(url, tentativas=1)
            if st != 200:
                raise RuntimeError(f"HTTP {st}: {url}")
            escrever(destino, b)
            return b
        def api(caminho):
            url = f"https://{host}/api/{caminho}"
            destino = cache / (hashlib.sha256(url.encode()).hexdigest() + ".json")
            d = json.loads(obter(url, destino))
            return d
        try:
            matches = [x for x in ibge if normalizar_chave(x["nome"]) == normalizar_chave(nome) and
                       x["regiao-imediata"]["regiao-intermediaria"]["UF"]["sigla"] == uf]
            if len(matches) != 1:
                raise RuntimeError("identidade municipal IBGE ambígua")
            codigo = matches[0]["id"]
            nome = matches[0]["nome"]
            casa = api("base/casalegislativa/")
            if not any(normalizar_chave(c["municipio"]) == normalizar_chave(nome) and c["uf"] == uf
                       for c in casa["results"]):
                raise RuntimeError("identidade da casa SAPL diverge do município IBGE")
            registro[str(codigo)]["estado_descoberta"] = "fonte oficial identificada"
            registro[str(codigo)]["fontes"].setdefault(host, {"identidade": f"https://{host}/api/base/casalegislativa/",
                                                  "estado": "índice em processamento"})
            salvar_registro(registro_path, registro, codigo, host)
            tipos = []
            tipos_reais = []
            page = 1
            while True:
                d = api(f"norma/tiponormajuridica/?page_size=100&page={page}")
                tipos_reais.extend(d["results"])
                tipos += [t for t in d["results"] if tipo_selecionado(t["descricao"], modo, categorias)
                          and (not siglas or t["sigla"] in siglas)]
                if not d["pagination"].get("next_page"):
                    break
                page += 1
            excluidos_esfera = [{"id": t["id"], "sigla": t.get("sigla"), "descricao": t["descricao"]}
                                for t in tipos_reais if not esfera_municipal(t["descricao"])]
            print(host, "tipos municipais", [(t["id"], t.get("sigla"), t["descricao"]) for t in tipos], flush=True)
            print(host, "excluídos sirel/federal/estadual",
                  [(t["id"], t.get("sigla"), t["descricao"]) for t in excluidos_esfera], flush=True)
            ok = pulado = 0
            indice = []
            eq_path = cache / "equivalencias.json"
            equivalencias = json.loads(eq_path.read_text()) if eq_path.exists() else {}
            pasta_municipio = RAIZ / uf / normalizar_chave(nome).replace(" ", "-")
            lexico = None  # léxico do município, montado só se algum texto vier de OCR
            # Índice local por município: evita reler todos os corpos a cada ato.
            fontes_md = set()
            hashes_md = {}
            for existente in pasta_municipio.glob("**/*.md"):
                texto_existente = existente.read_text()
                m_fonte = re.search(r'^fonte: (".*")$', texto_existente, re.M)
                m_hash = re.search(r'^sha256_texto: "([a-f0-9]{64})"$', texto_existente, re.M)
                if m_fonte:
                    fontes_md.add(json.loads(m_fonte[1]))
                if m_hash:
                    hashes_md.setdefault(m_hash[1], []).append(existente)
            for tipo in tipos:
                page = 1
                vistos = set()
                while True:
                    d = api(f"norma/normajuridica/?tipo={tipo['id']}&page_size=100&page={page}" + (f"&ano={ano_filtro}" if ano_filtro else ""))
                    if any(n["tipo"] != tipo["id"] for n in d["results"]):
                        raise RuntimeError("API ignorou o filtro de tipo; índice não confiável")
                    vistos.update(n["id"] for n in d["results"])
                    indice.extend(d["results"])
                    for n in d["results"]:
                        try:
                            emenda = "emenda" in tipo["descricao"].lower()
                            categoria, tipo_canonico = categoria_norma(tipo["descricao"], n)
                            identity = f"https://{host}/norma/{n['id']}"
                            if identity in fontes_md:
                                pulado += 1
                                continue
                            ano_norma = n.get("ano") or 0
                            try:
                                ano_norma = int(ano_norma)
                            except (TypeError, ValueError):
                                ano_norma = 0
                            if ano_minimo and ano_norma < ano_minimo:
                                pulado += 1
                                continue
                            if max_documentos and ok >= max_documentos:
                                continue
                            troca = texto_de_outra_norma(host, n["id"])
                            url = troca["texto_integral"] if troca else (
                                n.get("texto_integral") or texto_integral_alternativo(n.get("observacao") or "", host))
                            if not url:
                                raise RuntimeError("norma sem texto integral")
                            if urlsplit(url).hostname == host:
                                url = https_mesmo_host(url, host)
                            fonte = RAIZ / "_fonte/organicas-sapl" / host / f"{troca['id_fonte'] if troca else n['id']}.bin"
                            b = obter(url, fonte)
                            if troca and hashlib.sha256(b).hexdigest() != troca["sha256_fonte"]:
                                raise RuntimeError("PDF de outra norma registrado mudou na fonte; revisar a troca")
                            retencao = motivo_retencao(cache, n["id"], b)
                            if retencao:
                                raise RuntimeError("fonte retida para revisão de integralidade: " + retencao)
                            corpo, motivo = corpo_de_fonte(b, url)
                            if motivo:
                                raise RuntimeError(motivo)
                            notas_texto = []
                            if host == "sapl.campinas.sp.leg.br":
                                corpo, notas_texto = limpar_carimbo_campinas(corpo)
                                if pagina_do_diario_oficial_campinas(corpo):
                                    raise RuntimeError("página do Diário Oficial do Município anexada no lugar do ato, com outros atos nas colunas; revisar")
                                if ano_norma and ano_norma <= 1948 and (alertas_multiplos_atos(corpo, tipo["descricao"], n["numero"])
                                                                        or not abre_com_a_propria_epigrafe(corpo, tipo["descricao"], n["numero"])):
                                    corpo, data_fecho = recortar_ato_de_livro(corpo, tipo["descricao"], n["numero"], n.get("data") or "")
                                    notas_texto.append("ato recortado da página do livro de leis anexada no SAPL, que traz mais de um ato; "
                                                       "a página inteira está em fonte_texto")
                                    if not n.get("data"):
                                        n = {**n, "data": data_fecho, "data_do_fecho": True}
                                if not numero_proprio_no_inicio(corpo, n["numero"]):
                                    raise RuntimeError("o número da norma não aparece no começo do texto; conferir a identidade do anexo")
                                if epigrafe_propria_no_meio_da_frase(corpo, tipo["descricao"], n["numero"]):
                                    raise RuntimeError("epígrafe da norma no meio de uma frase: página do Diário Oficial em duas colunas entrelaçadas; revisar")
                                if "1948" in tipo["descricao"] and not abre_com_a_propria_epigrafe(corpo, tipo["descricao"], n["numero"]):
                                    raise RuntimeError("página do livro de leis não abre com a epígrafe da própria norma; recortar o ato antes de publicar")
                                if corpo.startswith(AVISO_OCR_INICIO):
                                    if lexico is None:
                                        lexico = lexico_do_municipio(pasta_municipio, cache)
                                    leg = legibilidade(corpo, lexico)
                                    if leg is not None and leg < LEGIBILIDADE_MINIMA:
                                        raise RuntimeError(f"OCR com baixa legibilidade ({leg:.0%} das palavras conhecidas no acervo do município); revisar")
                            if troca:
                                notas_texto.append(troca["nota"])
                            granularidade = alertas_multiplos_atos(corpo, tipo["descricao"], n["numero"])
                            outras_publicacoes = alertas_outras_publicacoes(corpo)
                            if outras_publicacoes:
                                raise RuntimeError("possível aviso/extrato de outra publicação no anexo; revisar: " + json.dumps(outras_publicacoes, ensure_ascii=False))
                            if granularidade:
                                raise RuntimeError("anexo contém epígrafe de outra norma; revisar granularidade: " +
                                                   json.dumps(granularidade, ensure_ascii=False))
                            if not corpo_integral_reconhecivel(corpo, emenda):
                                raise RuntimeError("texto sem artigo inicial reconhecível; revisar integralidade")
                            # Guarda versões iguais uma vez por município, preservando o índice original.
                            digest = hashlib.sha256(corpo.encode()).hexdigest()
                            iguais = hashes_md.get(digest, [])
                            if iguais:
                                equivalencias[str(n["id"])] = {"arquivo": str(iguais[0].relative_to(RAIZ)),
                                    "fonte": identity, "fonte_texto": url, "sha256_texto": digest}
                                escrever(eq_path, json.dumps(equivalencias, ensure_ascii=False).encode())
                                pulado += 1
                                continue
                            data = n.get("data") or ""
                            data_cadastro = "" if n.get("data_do_fecho") else data
                            ano_documento = str(n["ano"])
                            observacao_data = ""
                            if host == "sapl.lapa.pr.leg.br" and n["id"] == 3799:
                                if "Edifício da Câmara Municipal da Lapa, em 4 de abril de 1990" not in corpo:
                                    raise RuntimeError("assinatura da lei orgânica Lapa não confirmada")
                                data = "1990-04-04"
                                observacao_data = "Data da assinatura no texto integral; cadastro SAPL usa a data da Emenda 01/2020."
                            if host == "sapl.igarapava.sp.leg.br" and n["id"] == 1373:
                                if "Igarapava/SP, ano de 1990." not in corpo:
                                    raise RuntimeError("ano da assinatura de Igarapava não confirmado")
                                data = ""
                                ano_documento = "1990"
                                observacao_data = "Texto integral assinado apenas com ano de 1990; cadastro apresenta 2011-11-04, sem confirmação no documento."
                            if n.get("data_do_fecho"):
                                observacao_data = "Data do fecho no texto integral; o cadastro SAPL não traz data."
                            if not observacao_data and data_diverge_do_ano(n):
                                corrigida = data_da_epigrafe(corpo, n)
                                if not corrigida:
                                    raise RuntimeError(f"data do cadastro ({data}) diverge do ano da norma ({n['ano']}) e da publicação "
                                                       f"({n['data_publicacao']}); revisar")
                                data = corrigida
                                observacao_data = (f"Data da epígrafe no texto integral, confirmada pela publicação em {n['data_publicacao']}; "
                                                   f"o cadastro SAPL traz {data_cadastro}.")
                            ano = data[:4] if data else ano_documento
                            numero = str(n["numero"])
                            titulo = n["__str__"]
                            meta = {"titulo": titulo, "tipo": tipo_canonico, "tipo_na_fonte": tipo["descricao"],
                                    "numero": numero, "data": data, "municipio": nome, "uf": uf,
                                    "codigo_ibge": str(codigo), "versao_texto": "; ".join(filter(None, ["texto integral anexado no SAPL municipal", n.get("observacao", "").strip(), *notas_texto])) if notas_texto else "texto integral anexado no SAPL municipal; " + n.get("observacao", ""),
                                    "fonte": identity, "fonte_texto": url,
                                    "sha256_fonte": hashlib.sha256(b).hexdigest(), "sha256_texto": digest,
                                    "baixado_em": dt.date.today().isoformat()}
                            if data != data_cadastro:
                                meta["data_no_cadastro"] = data_cadastro
                                meta["observacao_data"] = observacao_data
                                meta["ano_na_fonte"] = ano_documento
                                if host == "sapl.lapa.pr.leg.br":
                                    titulo = "Lei Orgânica do Município da Lapa, de 4 de abril de 1990"
                                elif host == "sapl.igarapava.sp.leg.br":
                                    titulo = "Lei Orgânica do Município de Igarapava, de 1990"
                                else:
                                    titulo = titulo_com_data(titulo, data)
                                meta["titulo"] = titulo
                            cab = ["---"] + [f"{k}: {yaml_str(v)}" for k, v in meta.items()] + ["---", "", f"# {titulo}", "", corpo, ""]
                            arq = pasta_municipio / categoria / ano / f"{categoria}-{normalizar_chave(numero)}-{ano}-sapl-{n['id']}.md"
                            escrever(arq, "\n".join(cab).encode())
                            fontes_md.add(identity)
                            hashes_md.setdefault(digest, []).append(arq)
                            ok += 1
                        except Exception as e:
                            erros += 1
                            cache.mkdir(parents=True, exist_ok=True)
                            with (cache / "falhas.jsonl").open("a") as f:
                                f.write(json.dumps({"id": n["id"], "erro": str(e), "quando": dt.datetime.now().isoformat()}) + "\n")
                            print(host, n["id"], "FALHA", e, flush=True)
                    if not d["pagination"].get("next_page"):
                        if len(vistos) != d["pagination"]["total_entries"]:
                            raise RuntimeError("contagem do índice diverge do total oficial")
                        break
                    page += 1
            parcial = bool(ano_filtro or siglas)
            nome_indice = "indice.json" if modo == "organicas" else "indice-legislacao.json"
            if parcial:
                nome_indice = f"indice-legislacao-parcial-{'-'.join(sorted(siglas)) or 'todos'}-{ano_filtro or 'todos'}.json"
            escrever(cache / nome_indice, json.dumps({"fonte": f"https://{host}/api/norma/normajuridica/",
                     "municipio": nome, "uf": uf, "codigo_ibge": codigo, "modo": modo, "tipos_reais": tipos_reais, "tipos": tipos,
                     "tipos_excluidos_esfera": excluidos_esfera, "filtro_esfera": "municipal",
                     "normas": indice, "consultado_em": dt.date.today().isoformat()}, ensure_ascii=False).encode())
            presentes = {n["id"] for n in indice if "https://" + host + "/norma/" + str(n["id"]) in fontes_md}
            if parcial:
                print(host, "IBGE", codigo, "PARCIAL", f"ano={ano_filtro or 'todos'} siglas={','.join(sorted(siglas)) or 'todas'}",
                      "novos", ok, "já existentes", pulado, "índice", len(indice), "com md", len(presentes), flush=True)
                continue
            registro = json.loads(registro_path.read_text())
            estado_indice = ("índice filtrado capturado" if categorias or ano_minimo
                             else "índice de tipos normativos completo capturado")
            registro[str(codigo)]["fontes"][host].setdefault(modo, {}).update({"estado": estado_indice, "limite_textos": max_documentos,
                "filtro_categorias": list(categorias or []), "filtro_esfera": "municipal", "ano_minimo": ano_minimo,
                "registros": len(indice), "textos_md": len(presentes), "ids_equivalentes": list(equivalencias), "ids_sem_md": [n["id"] for n in indice if n["id"] not in presentes and str(n["id"]) not in equivalencias], "normas_distintas": len({(n["tipo"], n["numero"], n["ano"]) for n in indice}),
                "leis_organicas_distintas": len({(n["numero"], n["ano"]) for n in indice if not
                    any(t["id"] == n["tipo"] and "emenda" in t["descricao"].lower() for t in tipos)}),
                "consultado_em": dt.date.today().isoformat()})
            salvar_registro(registro_path, registro, codigo, host, modo)
            print(host, "IBGE", codigo, "novos", ok, "já existentes", pulado, flush=True)
        except Exception as e:
            erros += 1
            cache.mkdir(parents=True, exist_ok=True)
            with (cache / "falhas.jsonl").open("a") as f:
                f.write(json.dumps({"erro": str(e), "quando": dt.datetime.now().isoformat()}) + "\n")
            print(host, "FALHA", e, flush=True)
    return bool(erros)


def catalogo_sigi(rps):
    ibge = json.loads((RAIZ / "_indice/ibge-municipios.json").read_text())
    lookup = {(normalizar_chave(x["nome"]), x["regiao-imediata"]["regiao-intermediaria"]["UF"]["sigla"]): str(x["id"]) for x in ibge}
    rede = Rede(rps=rps)
    pasta = RAIZ / "_indice/organicas-sapl/sigi"
    url = "https://sigi.interlegis.leg.br/api/servicos/"
    registros = []
    pagina = 1
    while url:
        arquivo = pasta / f"pagina-{pagina}.json"
        if arquivo.exists():
            b = arquivo.read_bytes()
        else:
            st, b, _ = rede.get(url, tentativas=1)
            if st != 200:
                raise RuntimeError(f"SIGI HTTP {st}: {url}")
            json.loads(b)
            escrever(arquivo, b)
        d = json.loads(b)
        registros += d["results"]
        url = d["next"]
        pagina += 1
    if len(registros) != d["count"]:
        raise RuntimeError("catálogo SIGI mudou durante paginação; revisão necessária")
    candidatos = []
    nao_vinculados = []
    for r in registros:
        c = r["casa_legislativa"]
        if r["tipo_servico_sigla"] != "SAPL" or c["tipo_orgao_sigla"] != "CM":
            continue
        codigo = lookup.get((normalizar_chave(c["municipio"]), c["uf"]))
        item = {"municipio": c["municipio"], "uf": c["uf"], "url": r["url"],
                "codigo_ibge": codigo, "estado": "candidato oficial SIGI; API municipal ainda não validada"}
        (candidatos if codigo else nao_vinculados).append(item)
    escrever(pasta / "catalogo.json", json.dumps({"fonte": "https://sigi.interlegis.leg.br/api/servicos/",
        "consultado_em": dt.date.today().isoformat(), "total_servicos": len(registros),
        "candidatos_sapl": candidatos, "municipios_nao_vinculados": nao_vinculados}, ensure_ascii=False).encode())
    print("SIGI:", len(registros), "serviços;", len(candidatos), "SAPLs municipais vinculados;",
          len(nao_vinculados), "pendências IBGE", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--catalogo-sigi", action="store_true", help="captura catálogo oficial de candidatos, sem baixar normas")
    ap.add_argument("--rps", type=float, default=1)
    ap.add_argument("--modo", choices=["organicas", "legislacao"], default="organicas")
    ap.add_argument("--max-documentos", type=int, default=0, help="limita novas conversões; índice permanece completo")
    ap.add_argument("--host", help="reexecuta uma fonte já identificada")
    ap.add_argument("--ano", type=int, help="processa só as normas deste ano (coleta em frações; não atualiza o registro de índice completo)")
    ap.add_argument("--siglas", default="", help="siglas de tipo do SAPL separadas por vírgula, p.ex. LEI,LC")
    ap.add_argument("--descobrir", metavar="HOST", help="valida um SAPL oficial e registra sua identidade IBGE")
    ap.add_argument("--categorias", help="filtra categorias canônicas, separadas por vírgula")
    ap.add_argument("--ano-minimo", type=int, default=0, help="não converte normas com ano de cadastro inferior")
    a = ap.parse_args()
    if a.max_documentos < 0:
        ap.error("max-documentos deve ser não negativo")
    if not 0 < a.rps <= 4:
        ap.error("rps deve ser maior que zero e no máximo 4")
    if a.catalogo_sigi:
        catalogo_sigi(a.rps)
        raise SystemExit(0)
    registro_path = RAIZ / "_indice/organicas-sapl/municipios.json"
    fontes = list(FONTES)
    if registro_path.exists():
        for municipio in json.loads(registro_path.read_text()).values():
            fontes.extend((municipio["municipio"], municipio["uf"], host) for host in municipio["fontes"])
    if a.descobrir:
        if not re.fullmatch(r"[a-z0-9.-]+\.(?:leg|gov)\.br", a.descobrir):
            ap.error("informe um host oficial .leg.br ou .gov.br; identidade da casa será confrontada com IBGE")
        url = f"https://{a.descobrir}/api/base/casalegislativa/"
        st, bruto, _ = rede_host(a.descobrir, a.rps).get(url, tentativas=1)
        if st != 200:
            ap.error(f"fonte indisponível: HTTP {st}")
        casas = json.loads(bruto)["results"]
        if len(casas) != 1:
            ap.error("fonte sem identidade única")
        c = casas[0]
        fontes = [(c["municipio"], c["uf"], a.descobrir)]
        escrever(RAIZ / "_indice/organicas-sapl" / a.descobrir / (hashlib.sha256(url.encode()).hexdigest() + ".json"), bruto)
    fontes = list(dict.fromkeys(fontes))
    if a.host and not any(f[2] == a.host for f in fontes):
        ap.error("host não identificado; use --descobrir")
    categorias = [c.strip() for c in (a.categorias or "").split(",") if c.strip()]
    raise SystemExit(executar([f for f in fontes if not a.host or f[2] == a.host], a.rps, a.modo, a.max_documentos,
                              a.ano, tuple(x for x in a.siglas.split(",") if x), categorias, a.ano_minimo))
