"""Captura documentos estruturantes das capitais em publicações oficiais identificadas.

Catálogo explícito de fontes: não adivinha URLs, datas ou números. Preserva os
binários, o corte da compilação e anexos, sem contar cada anexo como nova norma.

Itens `extrator=dioly-raw` saem de `pdftotext -raw` no DOM/Dioly (histórias InDesign),
com recorte da lei e limpeza do chrome do jornal; rps ≤ 2. Itens `formato=html` vêm do
Domino da CMRJ (cmrj.py); `.doc` OLE (CMBH, SIREL) passam por textutil, antiword ou
catdoc; URLs http do catálogo são tentadas antes em https.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import Rede, documento_para_md, html_para_md, normalizar_chave, texto_pdf_para_md, yaml_str
from baixar_dioly import juntar_hifen, texto_raw, url_segura

RAIZ = Path(__file__).resolve().parent.parent
API_DIOLY = "https://portal-api.dioly.com.br/api/diarios/"
EPIGRAFE_LEI = re.compile(
    r"LEI\s+N[ºo°. ]?\s*(?P<num>\d{1,3}(?:\.\d{3})*)/(?P<ano>\d{4})", re.I)
COLOFON = re.compile(r"Criado pelo art\.\s*82 da Lei n", re.I)
COLOFON_BLOCO = re.compile(
    r"Criado pelo art\.\s*82 da Lei n[ºo°.].{0,120}\n(?:.*\n){0,22}?"
    r"(?:Chefe de Gabinete do Prefeito, em exercício|CEP:\s*40\.020-000)[^\n]*\n?",
    re.I)
CHROME_DOM = re.compile(
    r"^(?:DI[AÁ]RIO OFICIAL DO(?:\s+MUNIC[IÍ]PIO(?:\s+DO\s+SALVADOR)?)?|"
    r"SALVADOR[-–—• ]+BAHIA|SALVADOR-BAHIA|"
    r"ANO\s+[IVXLC]+\s*\|?\s*N\s*[ºo°.]?\s*[\d.]+(?:\s+\d{1,3})?|"
    r"(?:Segunda|Ter[cç]a|Quarta|Quinta|Sexta)-feira|S[aá]bado|Domingo|"
    r"[0-3]?\d DE (?:JANEIRO|FEVEREIRO|MAR[CÇ]O|ABRIL|MAIO|JUNHO|JULHO|"
    r"AGOSTO|SETEMBRO|OUTUBRO|NOVEMBRO|DEZEMBRO) DE 20\d{2}|"
    r"Ouvidoria Geral do Munic[ií]pio|"
    r"Disque Salvador|"
    r"Di[aá]rio Oficial do Munic[ií]pio - Edi[cç][oõ]es Anteriores|"
    r"CEP:\s*40\.020-000|"
    r"Coordenador de Tecnologia|"
    r"www\.(?:ouvidoria|disquesalvador|dom)\.|"
    r"atendimento 24h\.?|"
    r"E\s*D\s*I[CÇ]\s*[AÃ]\s*O\s*E\s*X\s*T\s*R\s*A"
    r")\s*$", re.I)
LETRA_VERTICAL = re.compile(r"^[EDIÇÃOEXTRAÇÃOedicaoextra]{1}$")
ASSINATURA_GABINETE = re.compile(
    r"GABINETE DO PREFEITO MUNICIPAL DO SALVADOR,\s*em\s+"
    r"(?P<dia>\d{1,2})\s+de\s+(?P<mes>\w+)\s+de\s+(?P<ano>\d{4})", re.I)

OLE = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"
REFERER_CMBH = {"Referer": "https://www.cmbh.mg.gov.br/atividade-legislativa/pesquisar-legislacao"}

CATALOGO = [{
    'municipio': 'Recife', 'uf': 'PE', 'codigo_ibge': '2611606',
    'tipo': 'Lei Orgânica', 'categoria': 'lei-organica', 'numero': '', 'data': '1990-04-04',
    'titulo': 'Lei Orgânica do Município do Recife, de 4 de abril de 1990',
    'slug': 'lei-organica-recife-1990', 'cache': 'recife-organica.pdf',
    'fonte': 'https://transparencia.recife.pe.leg.br/institucional/competencias/lei-organica_atualizada-em-08-04-2024.pdf',
    'fonte_texto': 'https://transparencia.recife.pe.leg.br/institucional/competencias/lei-organica_atualizada-em-08-04-2024.pdf/@@download/file',
    'versao_texto': 'compilação oficial atualizada em 08/04/2024, com emendas anexas; não certifica atualização posterior',
    'marcas_obrigatorias': ['LEI ORGÂNICA DO MUNICÍPIO DO RECIFE', 'Promulgada em 4 de abril de 1990',
                           'Atualizada em 08 de abril de 2024'],
}, {
    'municipio': 'São Paulo', 'uf': 'SP', 'codigo_ibge': '3550308',
    'tipo': 'Lei Orgânica', 'categoria': 'lei-organica', 'numero': '', 'data': '1990-04-04',
    'titulo': 'Lei Orgânica do Município de São Paulo, de 4 de abril de 1990',
    'slug': 'lei-organica-sao-paulo-1990', 'cache': 'sao-paulo-organica.pdf',
    'fonte': 'https://www.saopaulo.sp.leg.br/lei-organica/',
    'fonte_texto': 'https://www.saopaulo.sp.leg.br/wp-content/uploads/2022/09/LOMC.pdf',
    'versao_texto': 'compilação oficial, edição 2026 atualizada até a Emenda 44/25; índice remissivo preservado',
    'marcas_obrigatorias': ['LEI ORGÂNICA DO MUNICÍPIO DE SÃO PAULO', 'Atualizada até a Emenda 44/25',
                           'São Paulo, 4 de abril de 1990'],
}, {
    'municipio': 'Salvador', 'uf': 'BA', 'codigo_ibge': '2927408',
    'tipo': 'Lei Orgânica', 'categoria': 'lei-organica', 'numero': '', 'data': '1990-04-05',
    'titulo': 'Lei Orgânica do Município de Salvador, de 5 de abril de 1990',
    'slug': 'lei-organica-salvador-1990', 'cache': 'salvador-organica.pdf',
    'fonte': 'https://www.cms.ba.gov.br/lei-organica',
    'fonte_texto': 'https://www.cms.ba.gov.br/uploads/3bdae368d1a3e255c81b7f262ba1bbf6_1709038424.pdf',
    'versao_texto': 'compilação oficial da Câmara Municipal de Salvador, edição consolidada até a Emenda nº 41/2024; a edição não imprime a data de promulgação original; não certifica atualização posterior',
    'marcas_obrigatorias': ['Lei Orgânica do Município de Salvador', 'Edição consolidada até a Emenda nº 41',
                           'O Município de Salvador, Capital do Estado da Bahia'],
}, {
    'municipio': 'Salvador', 'uf': 'BA', 'codigo_ibge': '2927408',
    'tipo': 'Plano diretor', 'tipo_na_fonte': 'Lei', 'categoria': 'plano-diretor',
    'numero': '9069', 'data': '2016-06-30',
    'titulo': 'Lei nº 9.069, de 30 de junho de 2016',
    'slug': 'plano-diretor-9069-2016', 'cache': 'dom-6620-2016-06-30.pdf',
    'fonte': 'https://portal-api.dioly.com.br/uploads/pdfs/59331b95-e95d-401a-8fef-80b5220dc737_dom-6620-30-06-2016.pdf',
    'fonte_texto': 'https://portal-api.dioly.com.br/uploads/pdfs/59331b95-e95d-401a-8fef-80b5220dc737_dom-6620-30-06-2016.pdf',
    'publicacao': 'DOM nº 6620 de 30/06/2016',
    'data_publicacao': '2016-06-30',
    'codigo_identificador': 'DOM-6620-LEI-9069',
    'extrator': 'dioly-raw-v2',
    'versao_texto': 'publicação original no Diário Oficial do Município (CMS/Dioly), edição extra nº 6620; anexos tipográficos da mesma edição; mapas raster do Anexo 03 permanecem no PDF-fonte e não contam como norma nova; PDF CMS pdducorpodalei.pdf é o PL 396/2015 e foi descartado; não certifica atualização posterior',
    'marcas_obrigatorias': [
        'LEI Nº 9.069/2016',
        'Plano Diretor de Desenvolvimento Urbano',
        'GABINETE DO PREFEITO MUNICIPAL DO SALVADOR, em 30 de junho de 2016',
    ],
}, {
    'municipio': 'Salvador', 'uf': 'BA', 'codigo_ibge': '2927408',
    'tipo': 'Código municipal', 'tipo_na_fonte': 'Lei', 'categoria': 'codigos',
    'numero': '9148', 'data': '2016-09-08',
    'titulo': 'Lei nº 9.148, de 8 de setembro de 2016',
    'slug': 'louos-9148-2016', 'cache': 'dom-6672-2016-09-08.pdf',
    'fonte': 'https://portal-api.dioly.com.br/uploads/pdfs/be6cece9-e772-4a09-bfe4-5f71ae42d328_dom-6672-08-09-2016.pdf',
    'fonte_texto': 'https://portal-api.dioly.com.br/uploads/pdfs/be6cece9-e772-4a09-bfe4-5f71ae42d328_dom-6672-08-09-2016.pdf',
    'publicacao': 'DOM nº 6672 de 08/09/2016',
    'data_publicacao': '2016-09-08',
    'codigo_identificador': 'DOM-6672-LEI-9148',
    'extrator': 'dioly-raw-v2',
    'versao_texto': 'publicação original no Diário Oficial do Município (CMS/Dioly), edição nº 6672; anexos tipográficos da mesma edição; mapas raster permanecem no PDF-fonte e não contam como norma nova; PDF CMS louoscorpodalei.pdf não imprime o número 9.148 e não foi usado como texto; não certifica atualização posterior',
    'marcas_obrigatorias': [
        'LEI Nº 9.148/2016',
        'Ordenamento do Uso e da Ocupação do Solo',
        'GABINETE DO PREFEITO MUNICIPAL DO SALVADOR, em 08 de setembro de 2016',
    ],}, {
    'municipio': 'Rio de Janeiro', 'uf': 'RJ', 'codigo_ibge': '3304557',
    'tipo': 'Lei Orgânica', 'categoria': 'lei-organica', 'numero': '', 'data': '1990-04-05',
    'titulo': 'Lei Orgânica do Município do Rio de Janeiro, de 5 de abril de 1990',
    'slug': 'lei-organica-rio-de-janeiro-1990', 'cache': 'rio-de-janeiro-organica.pdf',
    'fonte': 'https://www.camara.rio/atividade-parlamentar/legislacao/lei-organica-do-municipio',
    'fonte_texto': 'https://www.rio.rj.gov.br/dlstatic/10112/4946719/4136646/Lei_Organica_MRJ_comaltdo205_2303.pdf',
    'versao_texto': 'compilação oficial da PGM/Prefeitura do Rio de Janeiro, 2ª edição revista e ampliada (2010), com alterações e revogações assinaladas no texto, atualizada até a Emenda nº 20/2009; o PDF imprime o fecho "Cidade do Rio de Janeiro, 5 de abril de 1990"; Last-Modified 23 Mar 2015; não certifica atualização posterior',
    'marcas_obrigatorias': ['LEI ORGÂNICA DO MUNICÍPIO DO RIO DE JANEIRO',
                           'Texto atualizado até a Emenda n.º 20/2009',
                           'O Município do Rio de Janeiro é a expressão e o instrumento da soberania do povo carioca'],
}, {
    'municipio': 'Rio de Janeiro', 'uf': 'RJ', 'codigo_ibge': '3304557',
    'tipo': 'Plano diretor', 'tipo_na_fonte': 'Lei Complementar',
    'categoria': 'plano-diretor', 'numero': '270', 'data': '2024-01-16',
    'titulo': 'Lei Complementar nº 270, de 16 de janeiro de 2024',
    'slug': 'plano-diretor-270-2024', 'cache': 'lc-270-2024.html', 'formato': 'html',
    'anexos': True,
    'fonte': 'https://aplicnt.camara.rj.gov.br/APL/Legislativos/contlei.nsf/0/0274835DDBC09B5303258AA700487674?OpenDocument',
    'fonte_texto': 'https://aplicnt.camara.rj.gov.br/APL/Legislativos/contlei.nsf/0/0274835DDBC09B5303258AA700487674?OpenDocument',
    'versao_texto': 'texto integral HTML da Câmara Municipal do Rio de Janeiro (Domino/contlei.nsf); republicação após rejeição de vetos parciais na sessão de 14/03/2024; anexos PDF oficiais do mesmo documento preservados à parte, sem contar como normas novas; a fonte declara que o texto não substitui o Diário Oficial',
    'marcas_obrigatorias': ['LEI COMPLEMENTAR Nº 270',
                           'Plano Diretor de Desenvolvimento Urbano Sustentável',
                           'institui a revisão do Plano Diretor'],
}, {
    'municipio': 'Rio de Janeiro', 'uf': 'RJ', 'codigo_ibge': '3304557',
    'tipo': 'Código municipal', 'tipo_na_fonte': 'Lei Complementar',
    'categoria': 'codigos', 'numero': '198', 'data': '2019-01-14',
    'titulo': 'Lei Complementar nº 198, de 14 de janeiro de 2019',
    'slug': 'codigo-obras-edificacoes-198-2019', 'cache': 'lc-198-2019.html', 'formato': 'html',
    'fonte': 'https://aplicnt.camara.rj.gov.br/APL/Legislativos/contlei.nsf/0/B004AA9E75ADFF0483258386005166C9?OpenDocument',
    'fonte_texto': 'https://aplicnt.camara.rj.gov.br/APL/Legislativos/contlei.nsf/0/B004AA9E75ADFF0483258386005166C9?OpenDocument',
    'versao_texto': 'texto integral HTML da Câmara Municipal do Rio de Janeiro (Domino/contlei.nsf); Código de Obras e Edificações Simplificado (COES); a fonte declara que o texto não substitui o Diário Oficial',
    'marcas_obrigatorias': ['LEI COMPLEMENTAR Nº 198',
                           'Código de Obras e Edificações Simplificado',
                           'COES'],
}, {
    'municipio': 'Rio de Janeiro', 'uf': 'RJ', 'codigo_ibge': '3304557',
    'tipo': 'Código municipal', 'tipo_na_fonte': 'Lei Complementar',
    'categoria': 'codigos', 'numero': '197', 'data': '2018-12-27',
    'titulo': 'Lei Complementar nº 197, de 27 de dezembro de 2018',
    'slug': 'codigo-vigilancia-sanitaria-197-2018', 'cache': 'lc-197-2018.html', 'formato': 'html',
    'fonte': 'https://aplicnt.camara.rj.gov.br/APL/Legislativos/contlei.nsf/0/CFDE3DDFD5DA93BC8325837600642FBE?OpenDocument',
    'fonte_texto': 'https://aplicnt.camara.rj.gov.br/APL/Legislativos/contlei.nsf/0/CFDE3DDFD5DA93BC8325837600642FBE?OpenDocument',
    'versao_texto': 'texto integral HTML da Câmara Municipal do Rio de Janeiro (Domino/contlei.nsf); Código de Vigilância Sanitária, Vigilância de Zoonoses e de Inspeção Agropecuária; a fonte declara que o texto não substitui o Diário Oficial',
    'marcas_obrigatorias': ['LEI COMPLEMENTAR Nº 197',
                           'Código de Vigilância Sanitária',
                           'Vigilância de Zoonoses'],
}]

PULAR = [{
    'municipio': 'Salvador', 'uf': 'BA', 'codigo_ibge': '2927408',
    'tipo': 'Código tributário', 'numero': '7186', 'ano': '2006',
    'status': 'sem_fonte_https',
    'motivo': 'Lei 7.186/2006: índice Dioly DOM sem edições de 2006–2007 (acervo começa ~2010/11); busca q="Codigo Tributario" devolve só DOM 6937/2017 e 8910/2024; ocorrências de 7.186 são citações posteriores, não a promulgação; leismunicipais (Cloudflare) e flipbook http cmsba.dyndns.org fora do escopo',
}]


def numero_epigrafe(numero):
    s = re.sub(r"\D", "", str(numero or ""))
    if not s:
        return ""
    s = s.lstrip("0") or "0"
    if len(s) > 3:
        s = s[:-3] + "." + s[-3:]
    return s


def recortar_lei_dom(texto, numero, ano):
    """Recorta a lei numerada no DOM extra; não corta no colofão precoce do InDesign."""
    alvo = re.sub(r"\D", "", str(numero)).lstrip("0") or "0"
    inicio = None
    for m in EPIGRAFE_LEI.finditer(texto):
        n = re.sub(r"\D", "", m.group("num")).lstrip("0") or "0"
        if n == alvo and m.group("ano") == str(ano):
            inicio = m.start()
            break
    if inicio is None:
        raise ValueError("epígrafe da lei %s/%s ausente" % (numero, ano))
    corpo = texto[inicio:]
    gab = ASSINATURA_GABINETE.search(corpo)
    fins = list(COLOFON.finditer(corpo))
    if fins:
        ultimo = fins[-1]
        depois = corpo[ultimo.end():]
        if (gab is None or ultimo.start() > gab.start()) and not re.search(
                r"Art\.|ANEXO|QUADRO", depois, re.I):
            corpo = corpo[:ultimo.start()]
    return corpo.strip() + "\n"


def limpar_chrome_dom(texto):
    """Remove masthead, colofão e EDIÇÃO EXTRA vertical; preserva a assinatura do gabinete."""
    texto = COLOFON_BLOCO.sub("\n", texto)
    linhas = []
    for ln in texto.splitlines():
        s = ln.strip()
        if not s:
            linhas.append("")
            continue
        if LETRA_VERTICAL.match(s):
            continue
        if CHROME_DOM.match(s):
            continue
        if re.fullmatch(r"\d{1,3}", s):
            continue
        linhas.append(ln)
    return re.sub(r"\n{3,}", "\n\n", "\n".join(linhas)).strip() + "\n"


CHROME_MD = re.compile(
    r"DI[AÁ]RIO OFICIAL DO(?:\s+SALVADOR-BAHIA)?|"
    r"ANO\s+[IVXLC]+\s*\|\s*N\s*[ºo°.]?\s*[\d.]+(?:\s+\d{1,3})?",
    re.I)


def limpar_chrome_md(md):
    md = CHROME_MD.sub("", md)
    md = re.sub(r"[ \t]{2,}", " ", md)
    md = re.sub(r"\n[ \t]+", "\n", md)
    md = re.sub(r"\n{3,}", "\n\n", md)
    return md.strip() + "\n"


def corpo_dom_raw(pdf, numero, ano):
    bruto = texto_raw(pdf)
    recorte = recortar_lei_dom(bruto, numero, ano)
    limpo = limpar_chrome_dom(recorte)
    return limpar_chrome_md(texto_pdf_para_md(juntar_hifen(limpo)))


def campos_meta(item):
    chaves = ['titulo', 'tipo', 'tipo_na_fonte', 'numero', 'data', 'municipio', 'uf',
              'codigo_ibge', 'versao_texto', 'fonte', 'fonte_texto', 'publicacao',
              'data_publicacao', 'codigo_identificador', 'extrator']
    return {k: item[k] for k in chaves if k in item and (item[k] not in (None, "") or k == "numero")}


def gravar_markdown(destino, item, corpo, sha_fonte, baixado_em):
    meta = campos_meta(item)
    meta.update({
        'sha256_fonte': sha_fonte,
        'sha256_texto': hashlib.sha256(corpo.encode()).hexdigest(),
        'baixado_em': baixado_em,
    })
    linhas = ["---"]
    for k, v in meta.items():
        linhas.append("%s: %s" % (k, yaml_str(v)))
    linhas += ["revogada: null", "---", "", "# " + item["titulo"], "", corpo]
    if not corpo.endswith("\n"):
        linhas.append("")
    texto = "\n".join(linhas)
    if not texto.endswith("\n"):
        texto += "\n"
    destino.parent.mkdir(parents=True, exist_ok=True)
    with destino.open("x") as f:
        f.write(texto)
    return texto


def conferir_marcas(corpo, item):
    normal = normalizar_chave(corpo)
    for marca in item["marcas_obrigatorias"]:
        if normalizar_chave(marca) not in normal:
            raise ValueError("marca de identidade/data ausente: " + marca)
    if not re.search(r"Art\.?\s*1[º°]", corpo, re.I):
        raise ValueError("artigo inicial não reconhecido")
    if item.get("extrator") == "dioly-raw-v2" and not ASSINATURA_GABINETE.search(corpo):
        raise ValueError("assinatura do gabinete ausente")


def preferir_https(url):
    if url.startswith("http://"):
        return "https://" + url.split("://", 1)[1]
    return url


def documento_oficial(bruto):
    cabeca = bruto.lstrip()[:15].lower()
    return (bruto.startswith(b"%PDF") or bruto.startswith(OLE) or bruto[:2] == b"PK"
            or cabeca.startswith(b"<html") or cabeca.startswith(b"<!doctype"))


def fonte_valida(bruto, item):
    if item.get("formato") == "html":
        return bool(bruto.strip())
    return documento_oficial(bruto)


def candidatos_url(item):
    """Pares (URL pedida, URL registrada); http do catálogo é tentado antes em https."""
    url = item["fonte_texto"]
    if item.get("extrator") == "dioly-raw-v2":
        return [(url_segura(url), url)]
    https = preferir_https(url)
    return [(https, https), (url, url)] if https != url else [(url, url)]


def url_registrada(item, fonte):
    """URL efetivamente usada na captura em cache, conforme o recibo .fonte.json."""
    recibo = fonte.with_name(fonte.stem + ".fonte.json")
    if recibo.exists():
        url = json.loads(recibo.read_text()).get("url")
        if url in {u for _, u in candidatos_url(item)}:
            return url
    return item["fonte_texto"]


def baixar_fonte(rede, item, destino, so_cache):
    if destino.exists() and destino.stat().st_size > 32:
        bruto = destino.read_bytes()
        if fonte_valida(bruto, item):
            return bruto, url_registrada(item, destino)
    if so_cache:
        raise ValueError("fonte ausente no cache: " + str(destino))
    st = 0
    for pedida, registrada in candidatos_url(item):
        st, bruto, _ = rede.get(pedida, tentativas=4, timeout=180)
        if st == 200 and fonte_valida(bruto, item):
            break
    else:
        raise ValueError("fonte indisponível ou formato não reconhecido: HTTP %s %s" % (st, item["fonte_texto"]))
    destino.parent.mkdir(parents=True, exist_ok=True)
    tmp = destino.with_suffix(destino.suffix + ".tmp")
    tmp.write_bytes(bruto)
    tmp.replace(destino)
    return bruto, registrada


def baixar_binario(rede, url, destino, timeout=300):
    if destino.exists() and destino.stat().st_size > 32:
        return destino.read_bytes()
    st, bruto, _ = rede.get(url, tentativas=2, timeout=timeout)
    if st != 200 or not documento_oficial(bruto):
        raise ValueError("anexo indisponível ou não é PDF/DOC/XLS oficial: HTTP " + str(st) + " " + url)
    destino.parent.mkdir(parents=True, exist_ok=True)
    with destino.open("xb") as f:
        f.write(bruto)
    return bruto


def ole_doc_para_md(bruto):
    """Converte o .doc OLE oficial (ex.: LOMBH-atual.doc) sem inventar PDF derivado."""
    with tempfile.TemporaryDirectory() as tmp:
        src = os.path.join(tmp, "a.doc")
        with open(src, "wb") as f:
            f.write(bruto)
        if shutil.which("textutil"):
            r = subprocess.run(["textutil", "-convert", "html", "-stdout", src],
                               capture_output=True, timeout=300)
            corpo = html_para_md(r.stdout.decode("utf-8", "replace"))
        elif shutil.which("antiword"):
            r = subprocess.run(["antiword", "-w", "0", src], capture_output=True, timeout=300)
            if r.returncode != 0 or not r.stdout.strip():
                return None, "antiword não extraiu o DOC oficial"
            corpo = texto_pdf_para_md(r.stdout.decode("utf-8", "replace"))
        elif shutil.which("catdoc"):
            r = subprocess.run(["catdoc", "-w", src], capture_output=True, timeout=300)
            if r.returncode != 0 or not r.stdout.strip():
                return None, "catdoc não extraiu o DOC oficial"
            corpo = texto_pdf_para_md(r.stdout.decode("utf-8", "replace"))
        else:
            return None, "sem conversor de DOC (textutil, antiword ou catdoc)"
        if len(re.sub(r"\W", "", corpo)) < 80:
            return None, "DOC sem texto legível"
        return corpo, None


def corpo_do_item(item, bruto, fonte, url):
    """Converte a fonte conforme o catálogo; devolve (corpo, html) — html só no Domino da CMRJ."""
    if item.get("extrator") == "dioly-raw-v2":
        return corpo_dom_raw(fonte, item["numero"], item["data"][:4]), None
    if item.get("formato") == "html":
        from cmrj import corpo_documento, data_do_documento
        corpo, html = corpo_documento(bruto, "text/html; charset=UTF-8")
        data_doc = data_do_documento(html, corpo)
        if item["data"] and data_doc and data_doc != item["data"]:
            raise ValueError("data do documento " + data_doc + " diverge do catálogo " + item["data"])
        return corpo, html
    if bruto.startswith(OLE):
        corpo, motivo = ole_doc_para_md(bruto)
    else:
        corpo, motivo = documento_para_md(bruto, url)
    if motivo:
        raise ValueError(motivo)
    return corpo, None


def baixar_anexos(rede, item, html, pasta):
    """Preserva os anexos oficiais da mesma norma como binários; não cria norma nova."""
    lista = []
    anexos = item.get("anexos")
    if anexos is True:
        from cmrj import anexos_pdf
        unid = item["fonte_texto"].rstrip("=").rsplit("/", 1)[-1].split("?")[0]
        destino_anexos = pasta / (item["slug"] + "-anexos")
        for url, nome in anexos_pdf(html or "", unid):
            seguro = re.sub(r"[^\w.\- ]+", "_", nome).strip() or "anexo.pdf"
            bruto = baixar_binario(rede, url, destino_anexos / seguro)
            lista.append({"arquivo": str((destino_anexos / seguro).relative_to(RAIZ)), "nome": nome,
                          "url": url, "sha256": hashlib.sha256(bruto).hexdigest(), "bytes": len(bruto)})
            print("anexo", nome, len(bruto), flush=True)
        if not lista:
            raise ValueError("anexos PDF oficiais não localizados no HTML")
    for anexo in anexos if isinstance(anexos, list) else []:
        arq = pasta / anexo["cache"]
        bruto = baixar_binario(rede, anexo["fonte_texto"], arq)
        lista.append({**anexo, "arquivo_fonte": str(arq.relative_to(RAIZ)),
                      "sha256_fonte": hashlib.sha256(bruto).hexdigest(), "bytes": len(bruto)})
        print("anexo", arq.name, len(bruto), flush=True)
    return lista


def processar_item(item, ibge, ibge_path, rede_para, so_cache, hoje):
    municipio = ibge[item["codigo_ibge"]]
    uf = municipio["regiao-imediata"]["regiao-intermediaria"]["UF"]["sigla"]
    if municipio["nome"] != item["municipio"] or uf != item["uf"]:
        raise ValueError("identidade IBGE diverge do catálogo")
    slug_mun = normalizar_chave(municipio["nome"]).replace(" ", "-")
    destino = RAIZ / "municipais" / uf / slug_mun / item["categoria"] / item["data"][:4] / (item["slug"] + ".md")
    if destino.exists():
        print("já existente", destino, flush=True)
        return None
    # Códigos e planos podem ser vários por município; a Lei Orgânica é uma só.
    if item["categoria"] == "lei-organica":
        outros = list(destino.parent.parent.glob("**/*.md"))
        if outros:
            raise ValueError("categoria já contém publicação; revisar versão antes de criar duplicata: " + str(outros))
    pasta = RAIZ / "municipais/_fonte/capitais" / slug_mun
    pasta.mkdir(parents=True, exist_ok=True)
    fonte = pasta / item["cache"]
    rede = rede_para(item["fonte_texto"])
    bruto, url = baixar_fonte(rede, item, fonte, so_cache)
    corpo, html = corpo_do_item(item, bruto, fonte, url)
    conferir_marcas(corpo, item)
    anexos = baixar_anexos(rede, item, html, pasta)
    sha_fonte = hashlib.sha256(bruto).hexdigest()
    texto = gravar_markdown(destino, {**item, "fonte_texto": url}, corpo, sha_fonte, hoje)
    observacao = item.get("observacao") or (
        "%d anexos oficiais preservados como binários da mesma norma, sem contar cada anexo como norma nova."
        % len(anexos) if anexos else
        "Compilação individual oficial; emendas anexas preservadas no mesmo documento, sem aumento artificial da contagem.")
    comprovacao = {k: v for k, v in item.items() if k != "anexos"}
    comprovacao.update({"arquivo": str(destino.relative_to(RAIZ)), "fonte_texto": url,
                        "sha256": hashlib.sha256(texto.encode()).hexdigest(),
                        "arquivo_fonte": str(fonte.relative_to(RAIZ)), "sha256_fonte": sha_fonte,
                        "sha256_corpo": hashlib.sha256(corpo.encode()).hexdigest(),
                        "ibge_sha256": hashlib.sha256(ibge_path.read_bytes()).hexdigest(),
                        "verificado_em": dt.datetime.now().isoformat(),
                        "anexos_baixados": anexos, "observacao": observacao})
    with (pasta / (item["slug"] + ".manifesto.json")).open("w") as f:
        json.dump(comprovacao, f, ensure_ascii=False, indent=2)
        f.write("\n")
    recibo = fonte.with_name(fonte.stem + ".fonte.json")
    if not recibo.exists():
        recibo.write_text(json.dumps({
            "url": url, "url_catalogo": item["fonte_texto"], "pagina_catalogo": item["fonte"],
            "sha256": sha_fonte, "http_status": 200, "content_length": len(bruto),
            "obtido_em": dt.datetime.now(dt.timezone.utc).isoformat(),
        }, ensure_ascii=False, indent=2) + "\n")
    print("gravado", destino, flush=True)
    return str(destino.relative_to(RAIZ))


def gravar_lote(arquivos, pular, hoje):
    lote = RAIZ / "municipais/_lotes/20261028-salvador-planos"
    lote.mkdir(parents=True, exist_ok=True)
    manifesto = {
        "municipio": "Salvador", "uf": "BA", "codigo_ibge": "2927408",
        "fonte_api": API_DIOLY, "rps_max": 2, "extrator": "dioly-raw-v2",
        "arquivos": arquivos, "pular": pular, "baixado_em": hoje,
        "observacao": (
            "PDDU Lei 9.069/2016 = DOM extra 6620 (30/06/2016). "
            "LOUOS Lei 9.148/2016 = DOM 6672 (08/09/2016). "
            "CMS /uploads/pddu/pdducorpodalei.pdf é PL 396/2015, não a lei sancionada. "
            "Mapas SSA_PDDU_15 e flipbook http cmsba.dyndns.org não usados. "
            "Anexos tipográficos entram no mesmo .md; mapas raster ficam no PDF-fonte. "
            "Código tributário 7.186/2006 sem PDF oficial HTTPS."
        ),
    }
    (lote / "manifesto.json").write_text(json.dumps(manifesto, ensure_ascii=False, indent=2) + "\n")
    (lote / "lista.txt").write_text("\n".join(arquivos) + ("\n" if arquivos else ""))
    falhas = lote / "falhas.jsonl"
    with falhas.open("w", encoding="utf-8") as f:
        for item in pular:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    return lote


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--so-cache", action="store_true",
                    help="não baixa; exige a fonte já gravada em municipais/_fonte/capitais/")
    ap.add_argument("--rps", type=float, default=1)
    a = ap.parse_args(argv)
    if not 0 < a.rps <= 2:
        ap.error("--rps máximo 2")
    ibge_path = RAIZ / "municipais/_indice/ibge-municipios.json"
    ibge = {str(x["id"]): x for x in json.loads(ibge_path.read_text())}
    redes = {}

    def rede_para(url):
        # O download do SIL da CMBH exige o Referer da página de pesquisa.
        chave = "cmbh" if (urlsplit(url).hostname or "").endswith("cmbh.mg.gov.br") else ""
        if chave not in redes:
            redes[chave] = Rede(rps=a.rps, headers=REFERER_CMBH if chave else None)
        return redes[chave]

    hoje = dt.date.today().isoformat()
    gravados = []
    for item in CATALOGO:
        path = processar_item(item, ibge, ibge_path, rede_para, a.so_cache, hoje)
        if path:
            gravados.append(path)
    salvador = [p for p in gravados if p.startswith("municipais/BA/salvador/")]
    if salvador:
        lote = gravar_lote(salvador, PULAR, hoje)
        print("lote", lote, "novos", len(salvador), "pular", len(PULAR), flush=True)
    print("novos", len(gravados), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
