"""Texto integral de normas de Campinas/SP que o SAPL cadastra sem anexo, a partir da Biblioteca Jurídica da Prefeitura.

Por que esta fonte entra
    O SAPL da Câmara (sapl.campinas.sp.leg.br) é a fonte do acervo de Campinas, mas 8.983 dos 24.434 decretos e
    443 das 562 leis anteriores a 1949 são só ficha: número, data e ementa, sem PDF do texto. A Biblioteca Jurídica
    da Procuradoria-Geral do Município (bibjuri.campinas.sp.gov.br) publica o texto dessas normas em HTML, em duas
    páginas por norma: "Texto Original" (a redação publicada) e "Texto Consolidado" (com notas de alteração e
    revogação). A sondagem de 01/11/2026 achou página para 99% dos decretos sem texto de 1955 em diante
    (211/211 em 1975, 310/326 em 1965, 298/300 em 1998, 253/254 em 2012). A ficha do SAPL continua sendo a
    identidade da norma no acervo; o bibjuri entra só como origem do texto, sempre a versão original.

Como funciona
    1. Fichas: a API do SAPL (normajuridica, por tipo e ano) lista as normas; ficam só as sem `texto_integral` e
       sem `.md` já publicado em municipais/SP/campinas (qualquer subpasta, qualquer origem). Com `--incluir-retidas`
       entram também as fichas COM anexo e sem `.md` cujo anexo o pipeline do SAPL reteve por integridade
       (retidos-integralidade.json ou última falha de conteúdo em falhas.jsonl, no cache de baixar_organicas_sapl.py):
       páginas de livro digitalizadas com vários atos, OCR ilegível, artigos fora de ordem. O `.md` declara isso em
       `observacao_fonte`, com o motivo registrado; `fonte` continua sendo a ficha do SAPL.
    2. Cartões: a busca avançada do bibjuri, paginada por ano e tipo (10 por página), dá id, número e data de
       cada norma. Quem não aparece na listagem do ano é procurado por número e ano.
    3. Texto: a página "Texto Original" é baixada, o bloco `div#div-conteudo-lei` é isolado e convertido com
       `comum.html_para_md`; o aviso "não substitui o publicado no DOM" vira nota em `versao_texto` e a linha
       "(Publicação DOM ...)" vira o campo `publicacao`. Quando a Biblioteca não publica o texto original de uma
       norma ("Este conteúdo não possui Original"), entra o "Texto Consolidado", identificado como tal em
       `versao_texto` e em `fonte_texto`, com as notas de alteração e revogação da fonte mantidas no corpo
       (`--sem-consolidado` desliga esse recurso e retém a norma). Páginas que só remetem a um PDF digitalizado
       ("CONSULTAR TEXTO NA ÍNTEGRA") são retidas com o endereço do PDF anotado.
    4. Travas: a epígrafe do texto tem de trazer o mesmo número e a mesma data da ficha do SAPL (só a formatação
       pode variar); o texto precisa de artigo inicial e fecho reconhecíveis; páginas com
       imagem embutida (quadros e anexos em PNG), com epígrafe de outra norma (`granularidade_sapl`) ou com
       aviso de outra publicação são retidas com o motivo em municipais/_indice/bibjuri-campinas/retidos.json.
       Também ficam retidas a página cujo texto não traz a ementa da ficha (outro ato sob o mesmo número e data), a
       ficha cujo ano de cadastro difere do ano da data (a pasta sairia errada) e a página do bibjuri que já deu
       texto a outro `.md` (duas fichas para o mesmo ato).
    5. Gravação: `municipais/SP/campinas/<pasta>/<ano>/<pasta>-<numero>-<ano>-sapl-<id>.md`, mesmo nome e mesmo
       front matter dos lotes do SAPL, com `fonte` no registro do SAPL, `fonte_texto` na página original do
       bibjuri, `publicacao` do DOM e `sha256_fonte` do HTML baixado. O título e `tipo_na_fonte` usam o nome do
       tipo na ficha do SAPL, como o pipeline do SAPL ("Leis Até 1948", "Decretos Até 1948", "Decreto-lei").
       Nenhum arquivo existente é alterado.

    Respostas da busca ficam em municipais/_indice/bibjuri-campinas/, páginas de norma em
    municipais/_fonte/bibjuri-campinas/ (bytes originais), páginas da API do SAPL no cache de
    baixar_organicas_sapl.py. Nada é baixado duas vezes. Uma requisição por segundo por host, trava por host.

Uso
    python3 -I scripts/baixar_bibjuri_campinas.py --tipo decreto --de 1970 --ate 1979 --listar   # só conta
    python3 -I scripts/baixar_bibjuri_campinas.py --tipo decreto --de 1975 --ate 1975 --max 20
    python3 -I scripts/baixar_bibjuri_campinas.py --tipo lei --de 1892 --ate 1948 --incluir-retidas
    python3 -I scripts/baixar_bibjuri_campinas.py --tipo decreto-lei --de 1940 --ate 1947 --incluir-retidas
"""
import argparse
import datetime as dt
import fcntl
import gzip
import hashlib
import html as html_mod
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import Rede, decodificar, html_para_md, yaml_str  # noqa: E402
from granularidade_sapl import alertas_multiplos_atos, alertas_outras_publicacoes, normal  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent / "municipais"
MUNICIPIO = RAIZ / "SP/campinas"
BIBJURI = "https://bibjuri.campinas.sp.gov.br"
HOST_SAPL = "sapl.campinas.sp.leg.br"
CACHE = RAIZ / "_indice/bibjuri-campinas"
FONTE = RAIZ / "_fonte/bibjuri-campinas"
CACHE_SAPL = RAIZ / "_indice/organicas-sapl" / HOST_SAPL
FONTE_SAPL = RAIZ / "_fonte/organicas-sapl" / HOST_SAPL
IDENTIDADE = (("municipio", "Campinas"), ("uf", "SP"), ("codigo_ibge", "3509502"))
# tipo da linha de comando -> tipos do SAPL (ids da API), tipo da busca do bibjuri, pasta e rótulos do acervo; os
# decretos até 1948 (19) e os decretos-leis (17) vão para a pasta dos decretos, como no pipeline do SAPL
TIPOS = {
    "decreto": {"sapl": (4, 19), "bibjuri": 57, "sigla": "DEC", "pasta": "decretos", "tipo": "Decreto",
                "tipo_na_fonte": "Decreto", "epigrafe": "DECRETO", "titulo": "Decreto"},
    "decreto-lei": {"sapl": (17,), "bibjuri": 93, "sigla": "DEL", "pasta": "decretos", "tipo": "Decreto-Lei",
                    "tipo_na_fonte": "Decreto-lei", "epigrafe": "DECRETO-LEI", "titulo": "Decreto-lei"},
    "lei": {"sapl": (1, 18), "bibjuri": 55, "sigla": "LEI", "pasta": "leis-ordinarias", "tipo": "Lei ordinária",
            "tipo_na_fonte": "Lei", "epigrafe": "LEI", "titulo": "Lei"},
}
# nome do tipo na API do SAPL (tiponormajuridica), que o pipeline do SAPL grava em tipo_na_fonte e no título (__str__)
ROTULO_SAPL = {1: "Lei", 4: "Decreto", 17: "Decreto-lei", 18: "Leis Até 1948", 19: "Decretos Até 1948"}
# Anexo retido pelo pipeline do SAPL (--incluir-retidas). Conta a recusa do texto lido do anexo ("...; revisar",
# "conferir a identidade do anexo", "recortar o ato antes de publicar", "PDF sem texto legível (nem por OCR)", "texto
# possivelmente incompleto"); não contam falha de rede ou de ferramenta ("[Errno 2] ... 'pdftotext'", "HTTP 404"), ficha
# que não tinha anexo na época ("norma sem texto integral") nem dúvida sobre a data do cadastro, que o texto de outra
# fonte não resolve.
RETENCAO_DE_CONTEUDO = re.compile(r"\brevis(?:ar|ão)\b|conferir a identidade|recortar o ato|nem por OCR|possivelmente incompleto", re.I)
RETENCAO_DE_DATA = re.compile(r"data do (?:cadastro|texto e do cadastro)|revisar a data", re.I)
PREFIXO_RETENCAO = "fonte retida para revisão de integralidade: "
MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro",
         "novembro", "dezembro"]
MES_NUMERO = {normal(m): i + 1 for i, m in enumerate(MESES)}
# "DECRETO Nº 4.813 DE 29 DE DEZEMBRO DE 1975", "DECRETO N.º 2.740, DE 30 DE DEZEMBRO DE 1965", "LEI N. 287 (": a data
# é opcional porque os livros de leis antigos não a trazem na epígrafe; nesse caso ela é conferida no fecho.
# Só formatação varia na transcrição: "N. º", "N.º", "No", "N/"; "3 626", "3.626" e "1,674"; "1.º DE ABRIL"; ano "1.970" ou "1 .970".
# "DECRETO-LEI Nº 96" (ou "DECRETO LEI") é epígrafe de decreto-lei, nunca de decreto nem de lei.
EPIGRAFE = re.compile(
    r"(?P<tipo>DECRETO[- ]LEI|DECRETO|LEI)\s+N(?:\s*[.º°o/])*\s*(?P<numero>\d(?:[\d., ]*\d)?(?:-[A-Z])?)"
    r"(?:\s*[,.–—-]?\s*(?:DE\s+)?(?P<dia>\d{1,2})\s*[º°.]*\s*(?:DE\s+)?(?P<mes>[A-ZÇÃa-zçã]{4,9})\s*(?:DE\s+)?(?P<ano>\d\s*\.?\s*\d{3}))?",
    re.I)
# "Campinas, 29 de dezembro de 1975", "aos 15 dias de maio de 1.970", "aos 5 dias do mês de Maio de 1.970"
DATA_EXTENSO = re.compile(r"(?P<dia>\d{1,2})\s*[º°.]*\s*(?:dias?\s+)?(?:do\s+m[êe]s\s+)?de\s+(?P<mes>[A-ZÇÃa-zçã]{4,9})\s+de\s+(?P<ano>\d\s*\.?\s*\d{3})", re.I)
PUBLICACAO = re.compile(r"\(\s*Publica[çc][ãa]o\s+DOM\s*[:\-]?\s*(?P<texto>[^)]*)\)", re.I)
AVISO = re.compile(r"Este texto n[ãa]o substitui o publicado no Di[áa]rio Oficial do Munic[íi]pio(?:\s*-\s*DOM)?\.?", re.I)
NOTA_AVISO = "texto da Biblioteca Jurídica da Prefeitura de Campinas (bibjuri), que não substitui o publicado no Diário Oficial do Município"
# fecho: local e data ("Paço Municipal, 29 de dezembro de 1975"), linha de assinatura ("Prefeito Municipal") ou a nota
# de publicação ("publicado no Departamento do Expediente"), procurados depois do último artigo
FECHO = re.compile(r"Pa[çc]o Municipal|Pal[áa]cio dos Jequitib[áa]s|(?:Prefeitura Municipal de )?Campinas,\s*(?:aos\s+)?\d{1,2}\s*(?:de|º|°)|"
                   r"^\W*Prefeit[oa](?:\s+(?:Municipal|de Campinas|em exerc[íi]cio))?\W*$|publicad[oa] n[oa] (?:Departamento|mesma data|Di[áa]rio)",
                   re.I | re.M)
# "Art. 1º", "Artigo 1º", "Art. único" e, nas transcrições que perderam a palavra "Artigo", a linha "1º - Fica ..."
ARTIGO = re.compile(r"(?m)^\W{0,4}Art(?:igo|\.)?\s*(?:1|único|unico)\b|\bArt(?:igo|\.)\s*1\s*[ºo°.]|^\W{0,4}1\s*[ºo°]\s*[-–—.]\s*[A-ZÀ-Ú]", re.I)
ARTIGO_QUALQUER = re.compile(r"(?m)^\W{0,4}Art(?:igo|\.)\s*\d")
# decretos de pessoal dos anos 1960 em forma não articulada: "A P O S E N T A, a partir de...", "NOMEIA", "EXONERA"
FORMULA_DIRETA = re.compile(r"(?m)^\W*(?:A\s*P\s*O\s*S\s*E\s*N\s*T\s*A|NOMEIA|EXONERA|DESIGNA|DISPENSA|REMOVE|PROMOVE|READMITE|REVERTE|TRANSFERE|DEMITE)\b")
# A ementa da ficha do SAPL tem de reaparecer no texto: palavras de 4 letras ou mais, sem acento, comparadas pelos 5
# primeiros caracteres (a ficha antiga vem em maiúsculas, com grafia antiga e erros de digitação: "PERTECENTE",
# "PATRIMO NIO", "CAXIAS"). Calibração em 02/11/2026 nos 2.915 textos do bibjuri no acervo: 2.782 com 100%, 112 de
# 60% a 99%, 18 com ementa curta demais e só 3 abaixo de 40% (0%, 8% e 29%), os três com o texto de outro ato sob o
# mesmo número e a mesma data (DEL 29/1940 com a ementa do 28/1940 do bibjuri; decretos 3.360/1969 e 3.779/1971).
# Ementa com menos de 3 palavras úteis não é conferida.
EMENTA_MINIMA = 0.4
PALAVRAS_VAZIAS = frozenset("PARA PELO PELA PELOS PELAS COMO DESDE SOBRE ENTRE ESTE ESTA ESSE ESSA ESTES ESTAS QUAL "
                            "QUAIS UMAS OUTRA OUTRO OUTRAS OUTROS DEMAIS PROVIDENCIAS".split())
FIM_DO_CONTEUDO = ("Visite tamb", 'id="footer"', "Coordenadoria de Estudos Jur")
SEM_ORIGINAL = re.compile(r"Este conte[úu]do n[ãa]o possui Original", re.I)
ANEXO_DA_FONTE = re.compile(r'href=["\x27](/images/full/[^"\x27]+)["\x27]', re.I)
EDICOES = {
    "original": ("texto original (não consolidado)", "visualizaroriginal"),
    "consolidado": ("texto consolidado pela fonte, que não publica o texto original desta norma; notas de alteração e "
                    "revogação da fonte permanecem no corpo", "visualizaratualizada"),
}


# ------------------------------------------------------------------------------------------ rede e cache
class Fonte:
    """Rede com limite por host, trava por host entre processos e cache bruto em disco."""

    def __init__(self, rps=1.0):
        self.rps = rps
        self.redes, self.travas = {}, {}

    def rede(self, host):
        if host not in self.redes:
            pasta = CACHE / "travas" if host != HOST_SAPL else RAIZ / "_indice/organicas-sapl/travas"
            pasta.mkdir(parents=True, exist_ok=True)
            trava = (pasta / (host + ".lock")).open("a")
            fcntl.flock(trava, fcntl.LOCK_EX)
            self.travas[host] = trava
            self.redes[host] = Rede(rps=self.rps)
        return self.redes[host]

    def get(self, url, destino):
        """GET com cache: devolve (bytes, veio_do_cache)."""
        if destino.exists():
            return destino.read_bytes(), True
        status, dados, _ = self.rede(urllib.parse.urlsplit(url).hostname).get(url)
        if status != 200:
            raise RuntimeError(f"HTTP {status}: {url}")
        escrever(destino, dados)
        return dados, False

    def post(self, url, campos, destino, tentativas=4):
        """POST de formulário com cache; mesmo limite de taxa e mesmo User-Agent do GET."""
        if destino.exists():
            return destino.read_bytes(), True
        rede = self.rede(urllib.parse.urlsplit(url).hostname)
        corpo = urllib.parse.urlencode(campos).encode()
        ultimo = None
        for n in range(tentativas):
            rede.limite.esperar()
            req = urllib.request.Request(url, data=corpo, headers={**rede.headers, "Accept": "text/html"})
            try:
                with urllib.request.urlopen(req, timeout=120) as r:
                    dados = r.read()
                    if r.headers.get("Content-Encoding") == "gzip":
                        dados = gzip.decompress(dados)
                break
            except urllib.error.HTTPError as e:
                if e.code in (400, 403, 404, 410):
                    raise RuntimeError(f"HTTP {e.code}: {url}") from e
                ultimo = e
            except Exception as e:  # rede, timeout
                ultimo = e
            time.sleep(2 * (n + 1) ** 2)
        else:
            raise RuntimeError(f"falhou após {tentativas} tentativas: {url}: {ultimo}")
        escrever(destino, dados)
        return dados, False


def escrever(caminho, dados):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    temporario = caminho.with_name(caminho.name + ".tmp")
    temporario.write_bytes(dados if isinstance(dados, bytes) else dados.encode("utf-8"))
    temporario.replace(caminho)


def ler_json(caminho, padrao):
    return json.loads(caminho.read_text(encoding="utf-8")) if caminho.exists() else padrao


def gravar_json(caminho, dados):
    escrever(caminho, json.dumps(dados, ensure_ascii=False, indent=1, sort_keys=True))


# ------------------------------------------------------------------------------------------ SAPL
def fichas_sapl(fonte, tipo_sapl, ano):
    """Normas de um tipo e ano na API do SAPL; páginas no cache de baixar_organicas_sapl.py (mesma URL, mesmo nome)."""
    normas, page = [], 1
    while True:
        url = f"https://{HOST_SAPL}/api/norma/normajuridica/?tipo={tipo_sapl}&page_size=100&page={page}&ano={ano}"
        dados, _ = fonte.get(url, CACHE_SAPL / (hashlib.sha256(url.encode()).hexdigest() + ".json"))
        pagina = json.loads(dados)
        normas += pagina["results"]
        if not pagina["pagination"].get("next_page"):
            return normas
        page += 1


def ids_publicados():
    """Ids do SAPL com .md em qualquer subpasta de Campinas, mais as equivalências registradas pelo pipeline."""
    ids = set()
    for p in MUNICIPIO.glob("**/*.md"):
        m = re.search(r"-sapl-(\d+)\.md$", p.name)
        if m:
            ids.add(int(m.group(1)))
    for chave in ler_json(CACHE_SAPL / "equivalencias.json", {}):
        if str(chave).isdigit():
            ids.add(int(chave))
    return ids


def paginas_bibjuri_usadas():
    """Páginas do bibjuri (id da norma) que já deram texto a um .md de Campinas: id -> caminho relativo."""
    usadas = {}
    for p in MUNICIPIO.glob("**/*-sapl-*.md"):
        with p.open("rb") as f:
            cabecalho = f.read(8192).decode("utf-8", errors="replace").split("\n---\n", 1)[0]
        m = re.search(r'^fonte_texto: "https?://bibjuri\.campinas\.sp\.gov\.br/index/visualizar(?:original|atualizada)/id/(\d+)"',
                      cabecalho, re.M)
        if m:
            usadas[int(m.group(1))] = str(p.relative_to(RAIZ.parent))
    return usadas


# ------------------------------------------------------------------------------------------ anexo retido no SAPL
def registros_de_retencao():
    """retidos-integralidade.json e a última falha de cada ficha em falhas.jsonl, ambos do pipeline do SAPL."""
    falhas = {}
    caminho = CACHE_SAPL / "falhas.jsonl"
    if caminho.exists():
        for linha in caminho.read_text(encoding="utf-8").splitlines():
            try:
                registro = json.loads(linha)
            except ValueError:  # linha truncada por interrupção do pipeline
                continue
            if isinstance(registro, dict) and "id" in registro:
                falhas[int(registro["id"])] = registro  # o arquivo só cresce: a última linha da ficha é a última falha
    return ler_json(CACHE_SAPL / "retidos-integralidade.json", {}), falhas


def motivo_legivel(motivo):
    """Motivo do pipeline do SAPL sem o prefixo de retenção, sem o JSON dos alertas e com no máximo 300 caracteres."""
    motivo = re.sub(r"\s+", " ", motivo).strip()
    if motivo.startswith(PREFIXO_RETENCAO):
        motivo = motivo[len(PREFIXO_RETENCAO):]
    motivo = re.split(r":\s*[\[{]", motivo, maxsplit=1)[0].strip(" ;:")
    return motivo if len(motivo) <= 300 else motivo[:297].rstrip() + "..."


def retencao_registrada(ident, retidos, falhas, sha_anexo=None):
    """Motivo pelo qual o pipeline do SAPL reteve por integridade o anexo da ficha `ident`, ou None.

    Vale o registro em retidos-integralidade.json, se o anexo em cache ainda é o mesmo (SHA-256) que foi retido; sem
    registro, vale a última falha da ficha em falhas.jsonl quando é recusa do conteúdo lido do anexo. Retenção por data
    do cadastro em dúvida não conta: a página de outra fonte não confirma a data da ficha."""
    registro = retidos.get(str(ident))
    if registro:
        if sha_anexo and registro.get("sha256_fonte") and registro["sha256_fonte"] != sha_anexo:
            return None  # o anexo mudou depois da retenção: o pipeline do SAPL precisa reavaliá-lo
        motivo = registro.get("motivo") or ""
    else:
        motivo = (falhas.get(int(ident)) or {}).get("erro") or ""
        if not RETENCAO_DE_CONTEUDO.search(motivo):
            return None
    if not motivo.strip() or RETENCAO_DE_DATA.search(motivo):
        return None
    return motivo_legivel(motivo)


def retencao_do_anexo(norma, registros):
    """retencao_registrada para uma ficha com anexo, conferindo o SHA-256 do anexo no cache do pipeline do SAPL."""
    if not norma.get("texto_integral"):
        return None
    anexo = FONTE_SAPL / f"{norma['id']}.bin"
    sha = hashlib.sha256(anexo.read_bytes()).hexdigest() if anexo.exists() else None
    return retencao_registrada(norma["id"], *registros, sha_anexo=sha)


def observacao_de_retencao(norma, motivo):
    """Texto de `observacao_fonte`: o anexo do SAPL existe, foi retido por integridade, e o texto vem do bibjuri."""
    return (f"a ficha do SAPL tem anexo de texto ({norma['texto_integral']}), retido por integridade no pipeline do "
            f"SAPL: {motivo}; o texto deste arquivo vem da Biblioteca Jurídica da Prefeitura (fonte_texto)")


def alvos_do_ano(fichas, publicados, retencao=None):
    """Fichas a converter, como (ficha, motivo da retenção do anexo ou None): as sem anexo e sem .md e, quando
    `retencao` (ficha -> motivo ou None) é dada, as com anexo retido por integridade e sem .md."""
    alvos = [(n, None) for n in fichas if not n.get("texto_integral") and n["id"] not in publicados]
    if retencao:
        for n in fichas:
            if n.get("texto_integral") and n["id"] not in publicados:
                motivo = retencao(n)
                if motivo:
                    alvos.append((n, motivo))
    return alvos


# ------------------------------------------------------------------------------------------ bibjuri
def cartoes_da_pagina(pagina):
    """Cartões de uma página de resultados: id, número (só dígitos), data ISO e título literal."""
    cartoes = []
    for ident, titulo in re.findall(r"<a href='/index/visualizar\w+/id/(\d+)' title='([^']*)'>", pagina):
        titulo = html_mod.unescape(titulo)
        numero = re.search(r"n[º°.o]*\s*([\d.]+(?:-[A-Z])?)", titulo, re.I)
        data = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", titulo)
        cartoes.append({"id": int(ident), "titulo": titulo,
                        "numero": numero.group(1).replace(".", "") if numero else None,
                        "data": f"{data.group(3)}-{int(data.group(2)):02d}-{int(data.group(1)):02d}" if data else None})
    total = re.search(r"Exibindo\s*<strong>([\d.]+)</strong>", pagina)
    if not total:  # sem o contador de resultados a página não é a de busca (erro, bloqueio ou resposta truncada)
        return None, cartoes
    return int(total.group(1).replace(".", "")), cartoes


def buscar(fonte, tipo_bibjuri, ano, numero=None, start=1):
    campos = [("checkbox-rapida-search", "true"), ("palavra_chave", ""), ("numero", str(numero or "")),
              ("ano", str(ano)), ("tipo_conteudo", str(tipo_bibjuri)), ("tipo_conteudo_list[]", str(tipo_bibjuri)),
              ("data_inicio", ""), ("data_fim", ""), ("join_mode", "0"), ("order", "2"), ("start", str(start)),
              ("limit", "10"), ("autor", ""), ("indices_list", "")]
    nome = f"{tipo_bibjuri}-{ano}-{'n' + str(numero) if numero else 'ano'}-p{start}.html"
    dados, _ = fonte.post(BIBJURI + "/index/pesquisaavancada/", campos, CACHE / "busca" / nome)
    return cartoes_da_pagina(decodificar(dados, "text/html; charset=iso-8859-1"))


def cartoes_do_ano(fonte, info, ano):
    """Listagem completa de um ano e tipo no bibjuri, paginada de 10 em 10; guardada em cartoes-<sigla>-<ano>.json."""
    caminho = CACHE / f"cartoes-{info['sigla']}-{ano}.json"
    indice = ler_json(caminho, None)
    if indice and indice.get("completo"):
        return indice["cartoes"]
    cartoes, start, total = [], 1, None
    while True:
        total, pagina = buscar(fonte, info["bibjuri"], ano, start=start)
        if total is None:
            raise RuntimeError(f"página de busca inesperada para {info['sigla']} {ano}, página {start}")
        cartoes += pagina
        if not pagina or len(cartoes) >= total or start >= 500:
            break
        start += 1
    gravar_json(caminho, {"ano": ano, "tipo": info["bibjuri"], "total_exibido": total, "cartoes": cartoes,
                          "completo": len(cartoes) >= total, "capturado_em": dt.date.today().isoformat()})
    return cartoes


def casar(norma, cartoes):
    """Cartões com o mesmo número da ficha ("07" no cartão de 1892 é a lei 7); os de mesma data vêm primeiro."""
    numero = so_digitos(norma["numero"])
    iguais = [c for c in cartoes if c["numero"] and so_digitos(c["numero"]) == numero]
    return sorted(iguais, key=lambda c: c["data"] != norma.get("data"))


def pagina_bibjuri(fonte, ident, edicao="original"):
    """Página da norma em bytes originais: <id>.html para o texto original, <id>-consolidado.html para o consolidado."""
    nome = f"{ident}.html" if edicao == "original" else f"{ident}-consolidado.html"
    return fonte.get(f"{BIBJURI}/index/{EDICOES[edicao][1]}/id/{ident}", FONTE / nome)


def sem_original(bloco):
    """A Biblioteca não publica o texto original: o bloco só diz "Este conteúdo não possui Original"."""
    return bool(SEM_ORIGINAL.search(html_mod.unescape(re.sub(r"<[^>]+>", " ", bloco))))


def anexo_da_fonte(bloco):
    """Arquivo da própria Biblioteca (PDF digitalizado) ao qual a página remete em vez de transcrever o texto."""
    m = ANEXO_DA_FONTE.search(bloco)
    return BIBJURI + m.group(1) if m else None


# ------------------------------------------------------------------------------------------ texto e travas
def bloco_conteudo(pagina):
    """O documento HTML da norma dentro de div#div-conteudo-lei, sem o restante da página."""
    m = re.search(r'<div id="div-conteudo-lei"[^>]*>(.*)', pagina, re.S)
    if not m:
        return None
    bloco = m.group(1)
    cortes = [i for i in (bloco.find(marca) for marca in FIM_DO_CONTEUDO) if i > 0]
    if cortes:
        bloco = bloco[:min(cortes)]
    m = re.search(r'<div id="principal"[^>]*>(.*)', bloco, re.S)
    return m.group(1) if m else bloco


def imagem_embutida(bloco):
    return bool(re.search(r"<img\b", bloco, re.I))


def converter(bloco):
    """HTML do bibjuri -> (corpo em Markdown, publicacao, notas). O aviso e a linha de publicação saem do corpo."""
    notas = []
    anexos = sorted(set(re.findall(r'href=["\x27](https?://[^"\x27]+\.pdf)["\x27]', bloco, re.I)))
    if anexos:
        notas.append("a página aponta a edição do DOM em PDF: " + anexos[0])
    bloco = re.sub(r"(?i)</?(artigo|paragrafo)[^>]*>", "\n", bloco)  # tags do editor, só agrupam dispositivos
    corpo = html_para_md(bloco).replace("​", "").replace("\r", "")
    paragrafos, publicacao = [], None
    for par in corpo.split("\n\n"):
        plano = re.sub(r"\s+", " ", re.sub(r"[*_\\]+", "", par)).strip()
        if not plano:
            continue
        if AVISO.fullmatch(plano):
            notas.insert(0, NOTA_AVISO)
            continue
        m = PUBLICACAO.fullmatch(plano)
        if m and publicacao is None:
            texto = re.sub(r"\s*:\s*(\d+)\s*$", r" p.\1", re.sub(r"\s+", " ", m.group("texto")).strip(" :;,"))
            publicacao = ("DOM " + texto).strip()
            continue
        paragrafos.append(par.strip())
    if NOTA_AVISO not in notas:
        notas.insert(0, NOTA_AVISO)
    return "\n\n".join(paragrafos), publicacao, notas


def texto_plano(corpo):
    return re.sub(r"[*_#>]+", "", corpo).replace("\xa0", " ")


def data_iso(dia, mes, ano):
    numero = MES_NUMERO.get(normal(mes))
    if not numero:
        return None
    ano = int(re.sub(r"\D", "", ano))  # "1.970" e "1 .970" na transcrição
    return f"{ano:04d}-{numero:02d}-{int(dia):02d}"


def so_digitos(numero):
    """Número sem pontos de milhar, espaços da transcrição ou zeros à esquerda; sufixo de letra fica ("3626-A")."""
    return re.sub(r"[ .,]", "", str(numero)).strip().upper().lstrip("0") or "0"


def identidade(corpo, norma, info):
    """None quando a epígrafe traz o número e a data da ficha do SAPL; senão, o motivo da retenção."""
    plano = texto_plano(corpo)
    inicio = plano[:800]
    achado = None
    for m in EPIGRAFE.finditer(inicio):
        # a epígrafe abre um parágrafo e vem em maiúsculas; "Altera o Decreto nº 4.813, de ..." é citação
        antes = inicio[inicio.rfind("\n", 0, m.start()) + 1:m.start()]
        tipo = re.sub(r"[- ]+", "-", normal(m.group("tipo")))
        if m.group("tipo").isupper() and tipo == info["epigrafe"] and not re.search(r"\w", antes):
            achado = m
            break
    if not achado:
        return "epígrafe do ato não reconhecida no início do texto"
    numero, esperado = so_digitos(achado.group("numero")), so_digitos(norma["numero"])
    if numero != esperado:
        return f"número da epígrafe ({numero}) difere da ficha do SAPL ({esperado})"
    if not norma.get("data"):
        return "ficha do SAPL sem data; identidade não conferível"
    if achado.group("dia"):
        data = data_iso(achado.group("dia"), achado.group("mes"), achado.group("ano"))
        if data != norma["data"]:
            return f"data da epígrafe ({data or achado.group(0)}) difere da ficha do SAPL ({norma['data']})"
        return None
    datas = {data_iso(m.group("dia"), m.group("mes"), m.group("ano")) for m in DATA_EXTENSO.finditer(plano[-1500:])}
    if norma["data"] in datas:
        return None
    return "epígrafe sem data e fecho sem a data da ficha do SAPL" + (f" ({', '.join(sorted(d for d in datas if d))})" if datas else "")


def integridade(corpo, norma, info):
    """Fórmula, artigo inicial e fecho; outras epígrafes e avisos de outra publicação retêm."""
    plano = texto_plano(corpo)
    if len(re.sub(r"\W", "", plano)) < 150:
        return "texto curto demais para ser o ato integral"
    if not ARTIGO.search(plano):
        if FORMULA_DIRETA.search(plano):
            return "ato em forma não articulada (fórmula direta: APOSENTA, NOMEIA...), sem artigo inicial reconhecível"
        return "texto sem artigo inicial reconhecível"
    outros = alertas_multiplos_atos(corpo, info["tipo"], str(norma["numero"]))
    if outros:
        return "mais de um ato na página: " + outros[0]["trecho"][:120]
    avisos = alertas_outras_publicacoes(corpo)
    if avisos:
        return "possível aviso ou extrato de outra publicação: " + avisos[0]["trecho"][:120]
    ultimo = None
    for m in ARTIGO_QUALQUER.finditer(plano):
        ultimo = m
    cauda = plano[ultimo.start():] if ultimo else plano[-1500:]
    if not FECHO.search(cauda):
        return "texto sem fecho reconhecível (local e data, assinatura ou nota de publicação) depois do último artigo"
    return None


def rotulo_sapl(norma, info, campo="titulo"):
    """Nome do tipo como a ficha do SAPL o dá ("Leis Até 1948", "Decreto-lei"); sem o tipo na ficha, o rótulo de `info`."""
    return ROTULO_SAPL.get(norma.get("tipo"), info[campo])


def radicais(texto):
    """Palavras de 4 letras ou mais, sem acento e sem as vazias, pelos 5 primeiros caracteres."""
    return {p[:5] for p in re.findall(r"[A-Z0-9]+", normal(texto)) if len(p) >= 4 and not p.isdigit() and p not in PALAVRAS_VAZIAS}


def ementa_diverge(corpo, norma):
    """None quando a ementa da ficha do SAPL reaparece no texto (EMENTA_MINIMA) ou é curta demais para conferir; senão o
    motivo. Pega o texto de outro ato com o mesmo número e a mesma data (numeração divergente entre as fontes)."""
    ementa = radicais(norma.get("ementa") or "")
    if len(ementa) < 3:
        return None
    achadas = ementa & radicais(texto_plano(corpo))
    if len(achadas) / len(ementa) >= EMENTA_MINIMA:
        return None
    return (f"ementa da ficha do SAPL não confere com o texto ({len(achadas)} de {len(ementa)} palavras): "
            + re.sub(r"\s+", " ", norma["ementa"]).strip()[:120])


def titulo_de(norma, info):
    """Título no formato do __str__ da ficha do SAPL: "Decreto nº 4.813, de 29 de dezembro de 1975"."""
    data = dt.date.fromisoformat(norma["data"])
    numero = str(norma["numero"]).strip()
    if numero.isdigit():
        numero = f"{int(numero):,}".replace(",", ".")
    return f"{rotulo_sapl(norma, info)} nº {numero}, de {data.day:02d} de {MESES[data.month - 1]} de {data.year}"


def montar_md(norma, cartao, corpo, publicacao, notas, bruto, info, hoje, edicao="original", retencao=None):
    """Texto completo do .md: front matter nos moldes dos lotes do SAPL de Campinas, H1 e corpo. `retencao` é o motivo
    pelo qual o pipeline do SAPL reteve o anexo da ficha; entra em `observacao_fonte`."""
    titulo = titulo_de(norma, info)
    rotulo, rota = EDICOES[edicao]
    meta = [("titulo", titulo), ("tipo", info["tipo"]), ("tipo_na_fonte", rotulo_sapl(norma, info, "tipo_na_fonte")),
            ("numero", str(norma["numero"])), ("data", norma["data"]), *IDENTIDADE,
            ("versao_texto", rotulo + "; " + "; ".join(notas)),
            ("publicacao", publicacao or ""),
            ("fonte", f"https://{HOST_SAPL}/norma/{norma['id']}"),
            ("fonte_texto", f"{BIBJURI}/index/{rota}/id/{cartao['id']}"),
            *((("observacao_fonte", observacao_de_retencao(norma, retencao)),) if retencao else ()),
            ("sha256_fonte", hashlib.sha256(bruto).hexdigest()),
            ("sha256_texto", hashlib.sha256(corpo.encode("utf-8")).hexdigest()),
            ("baixado_em", hoje.isoformat())]
    return "---\n" + "\n".join(f"{k}: {yaml_str(v)}" for k, v in meta) + f"\n---\n\n# {titulo}\n\n{corpo}\n"


def avaliar(bloco, norma, info):
    """Aplica as travas ao bloco da norma. Devolve (motivo ou None, corpo, publicacao, notas, pdf da fonte ou None)."""
    if not bloco:
        return "página sem o bloco de conteúdo da norma", None, None, None, None
    pdf = anexo_da_fonte(bloco)
    if imagem_embutida(bloco):
        return "imagem embutida no texto (quadro ou anexo em figura)", None, None, None, pdf
    corpo, publicacao, notas = converter(bloco)
    motivo = identidade(corpo, norma, info) or integridade(corpo, norma, info) or ementa_diverge(corpo, norma)
    if motivo and pdf:
        motivo = "texto não transcrito na fonte, que remete a arquivo digitalizado; " + motivo
    elif (motivo and motivo.startswith(("epígrafe do ato não reconhecida", "texto curto demais", "texto sem artigo"))
          and not ARTIGO.search(texto_plano(corpo)) and len(re.sub(r"\W", "", texto_plano(corpo))) < 400):
        motivo = "página sem o texto do ato (só ementa, cabeçalho ou nota de publicação); " + motivo
    elif pdf:  # o texto passa, mas parte do ato (anexo, quadro) está só no arquivo digitalizado
        motivo = "anexo do ato em arquivo digitalizado da fonte, não representado no texto"
    return motivo, corpo, publicacao, notas, pdf


def fonte_texto_coerente(fonte_texto, texto_integral, anexo_retido=False):
    """Regra de `campinas.py verificar`: o texto do .md tem de vir do anexo da ficha do SAPL (mesma URL, sem esquema)
    ou de uma página de norma do bibjuri (texto original ou consolidado), mas o bibjuri só vale quando a ficha não tem
    anexo ou quando o anexo foi retido por integridade (`anexo_retido`: registro do pipeline do SAPL e
    `observacao_fonte` no .md, conferidos por quem chama)."""
    sem_esquema = (fonte_texto or "").split("://", 1)[-1]
    if texto_integral and sem_esquema == texto_integral.split("://", 1)[-1]:
        return True
    if texto_integral and not anexo_retido:
        return False
    partes = urllib.parse.urlsplit(fonte_texto or "")
    return (partes.hostname == urllib.parse.urlsplit(BIBJURI).hostname
            and bool(re.fullmatch(r"/index/visualizar(?:original|atualizada)/id/\d+", partes.path)))


def destino_de(norma, info):
    ano = norma["data"][:4]
    numero = re.sub(r"[^\w.-]+", "-", str(norma["numero"]).strip())
    return MUNICIPIO / info["pasta"] / ano / f"{info['pasta']}-{numero}-{ano}-sapl-{norma['id']}.md"


def processar(fonte, norma, cartoes, info, hoje, consolidado=True, retencao=None, usadas=None):
    """Devolve (estado, detalhe): "novo" com o caminho, "retida"/"sem_cartao" com o motivo, "existente".

    `retencao`: motivo pelo qual o pipeline do SAPL reteve o anexo da ficha (vai para observacao_fonte).
    `usadas`: páginas do bibjuri que já deram texto a um .md (id -> caminho); atualizado a cada novo .md."""
    if norma.get("data") and norma["data"][:4] != str(norma.get("ano") or norma["data"][:4]):
        # a pasta sai do ano da data; campinas.py verificar exige o ano do cadastro igual ao da pasta
        return "retida", {"motivo": f"ano do cadastro do SAPL ({norma['ano']}) difere do ano da data da ficha ({norma['data']})"}
    candidatos = casar(norma, cartoes)
    if not candidatos:
        total, achados = buscar(fonte, info["bibjuri"], int(norma["data"][:4]) if norma.get("data") else norma["ano"],
                                numero=str(norma["numero"]).replace(".", "").strip())
        if total is None:
            raise RuntimeError("página de busca por número inesperada")
        candidatos = casar(norma, achados)
    if not candidatos:
        return "sem_cartao", {"motivo": "sem cartão com este número no bibjuri"}
    if len({c["id"] for c in candidatos if c["data"] == norma.get("data")}) > 1:
        return "retida", {"motivo": "mais de um cartão no bibjuri com o mesmo número e data",
                          "bibjuri_id": [c["id"] for c in candidatos]}
    cartao = candidatos[0]
    edicao = "original"
    bruto, _ = pagina_bibjuri(fonte, cartao["id"], edicao)
    bloco = bloco_conteudo(decodificar(bruto, "text/html; charset=iso-8859-1"))
    if bloco and sem_original(bloco):
        if not consolidado:
            return "retida", {"motivo": "a fonte não publica o texto original desta norma (só o consolidado)",
                              "bibjuri_id": cartao["id"], "sha256_fonte": hashlib.sha256(bruto).hexdigest()}
        edicao = "consolidado"
        bruto, _ = pagina_bibjuri(fonte, cartao["id"], edicao)
        bloco = bloco_conteudo(decodificar(bruto, "text/html; charset=iso-8859-1"))
    registro = {"bibjuri_id": cartao["id"], "sha256_fonte": hashlib.sha256(bruto).hexdigest(), "edicao": edicao}
    motivo, corpo, publicacao, notas, pdf = avaliar(bloco, norma, info)
    if pdf:
        registro["pdf"] = pdf
    if motivo:
        return "retida", {"motivo": motivo, **registro}
    destino = destino_de(norma, info)
    caminho = str(destino.relative_to(RAIZ.parent))
    if destino.exists():
        return "existente", {"caminho": caminho, **registro}
    if usadas is not None and usadas.get(cartao["id"], caminho) != caminho:
        return "retida", {"motivo": f"a página do bibjuri já deu texto a outro .md ({usadas[cartao['id']]}): duas fichas para o mesmo ato?",
                          **registro}
    escrever(destino, montar_md(norma, cartao, corpo, publicacao, notas, bruto, info, hoje, edicao, retencao))
    if usadas is not None:
        usadas[cartao["id"]] = caminho
    return "novo", {"caminho": caminho, **registro}


# ------------------------------------------------------------------------------------------ execução
def executar(tipo, de, ate, maximo=0, listar=False, rps=1.0, consolidado=True, incluir_retidas=False):
    info = TIPOS[tipo]
    fonte = Fonte(rps)
    CACHE.mkdir(parents=True, exist_ok=True)
    publicados = ids_publicados()
    retidos = ler_json(CACHE / "retidos.json", {})
    sem_cartao = ler_json(CACHE / "sem-cartao.json", {})
    retencao = None
    if incluir_retidas:
        registros = registros_de_retencao()
        retencao = lambda n: retencao_do_anexo(n, registros)  # noqa: E731
    usadas = None if listar else paginas_bibjuri_usadas()
    hoje = dt.date.today()
    novos_total = 0
    for ano in range(de, ate + 1):
        fichas = [n for t in info["sapl"] for n in fichas_sapl(fonte, t, ano)]
        sem_texto = [n for n in fichas if not n.get("texto_integral")]
        alvos = alvos_do_ano(fichas, publicados, retencao)
        n_retidas = sum(1 for _, motivo in alvos if motivo)
        descricao = (f"fichas {len(fichas)}, sem texto {len(sem_texto)}, já publicadas {sum(1 for n in sem_texto if n['id'] in publicados)}, "
                     f"alvos {len(alvos)}" + (f" (com anexo retido no SAPL {n_retidas})" if incluir_retidas else ""))
        cartoes = cartoes_do_ano(fonte, info, ano)
        if listar:
            com_cartao = sum(1 for n, _ in alvos if casar(n, cartoes))
            retidas_com_cartao = sum(1 for n, motivo in alvos if motivo and casar(n, cartoes))
            print(f"{ano}: {descricao}, com cartão no bibjuri {com_cartao}"
                  + (f" (com anexo retido {retidas_com_cartao})" if incluir_retidas else "")
                  + f", cartões no ano {len(cartoes)}", flush=True)
            continue
        contagem = {"novo": 0, "novo_consolidado": 0, "novo_anexo_retido": 0, "retida": 0, "sem_cartao": 0, "existente": 0, "erro": 0}
        motivos = {}
        for n, anexo_retido in alvos:
            if maximo and novos_total >= maximo:
                break
            chave = str(n["id"])
            try:
                estado, detalhe = processar(fonte, n, cartoes, info, hoje, consolidado, anexo_retido, usadas)
            except Exception as e:  # rede ou página inesperada: segue para a próxima ficha
                estado, detalhe = "erro", {"motivo": f"erro: {str(e)[:200]}"}
                print(f"  ERRO {ano} {n['numero']} (sapl {n['id']}): {e}", flush=True)
            contagem[estado] += 1
            if estado == "novo" and detalhe.get("edicao") == "consolidado":
                contagem["novo_consolidado"] += 1
            if estado == "novo" and anexo_retido:
                contagem["novo_anexo_retido"] += 1
            registro = {"numero": str(n["numero"]), "data": n.get("data"), "ano": ano, "tipo": tipo, "em": hoje.isoformat(), **detalhe}
            if anexo_retido:
                registro["anexo_sapl_retido"] = anexo_retido
            if estado in ("retida", "erro"):
                retidos[chave] = registro
                motivos[detalhe["motivo"].split(":")[0]] = motivos.get(detalhe["motivo"].split(":")[0], 0) + 1
            elif estado == "sem_cartao":
                sem_cartao[chave] = registro
            else:
                retidos.pop(chave, None)
                sem_cartao.pop(chave, None)
                if estado == "novo":
                    novos_total += 1
            if sum(contagem.values()) % 50 == 0:
                gravar_json(CACHE / "retidos.json", retidos)
                gravar_json(CACHE / "sem-cartao.json", sem_cartao)
                print(f"  ... {ano}: {sum(contagem.values())}/{len(alvos)} {contagem}", flush=True)
        gravar_json(CACHE / "retidos.json", retidos)
        gravar_json(CACHE / "sem-cartao.json", sem_cartao)
        print(f"{ano}: {descricao} -> {contagem}" + (f"; motivos {motivos}" if motivos else ""), flush=True)
        if maximo and novos_total >= maximo:
            print(f"limite de {maximo} novas conversões atingido", flush=True)
            break
    return novos_total


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--tipo", choices=sorted(TIPOS), required=True)
    ap.add_argument("--de", type=int, required=True, help="primeiro ano")
    ap.add_argument("--ate", type=int, required=True, help="último ano, inclusive")
    ap.add_argument("--max", type=int, default=0, help="limita novas conversões; 0 = sem limite")
    ap.add_argument("--listar", action="store_true", help="só conta fichas, alvos e cartões; não baixa textos")
    ap.add_argument("--rps", type=float, default=1.0, help="requisições por segundo por host")
    ap.add_argument("--sem-consolidado", action="store_true",
                    help="retém as normas sem texto original em vez de usar o texto consolidado da fonte")
    ap.add_argument("--incluir-retidas", action="store_true",
                    help="toma também as fichas com anexo no SAPL retido por integridade (retidos-integralidade.json ou "
                         "última falha de conteúdo em falhas.jsonl) e sem .md; o .md declara isso em observacao_fonte")
    a = ap.parse_args()
    executar(a.tipo, a.de, a.ate, a.max, a.listar, a.rps, consolidado=not a.sem_consolidado, incluir_retidas=a.incluir_retidas)
