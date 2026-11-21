"""Conselho Nacional do Meio Ambiente (CONAMA): resoluções anteriores a 2017, em Markdown.

EXCEÇÃO AO robots.txt, AUTORIZADA PELO MANTENEDOR (20/11/2026). O `robots.txt` de conama.mma.gov.br traz
`Disallow: /`. Nenhuma fonte oficial sem bloqueio tem o texto dessas resoluções: o Diário Oficial da União em texto
(in.gov.br, `leiturajornal`) começa em 2/1/2017, antes disso só há a imagem das páginas; o acervo do IBAMA
(ibama.gov.br/sophia) veda robôs de IA no robots.txt e responde com desafio do Cloudflare; e a página de legislação do
MMA no gov.br só aponta para o portal do CONAMA. O mantenedor autorizou, em 20/11/2026, baixar deste portal apesar do
robots.txt, só nele, a no máximo 0,2 requisição por segundo, com flag explícita e registro aqui e no README. Por isso:

- a coleta exige `--apesar-do-robots` e recusa os anos de 2017 em diante, que o DOU cobre (`baixar_dou.py`);
- a taxa é fixa: uma requisição a cada cinco segundos, sem paralelismo;
- `--despejar` mostra o que a listagem e um PDF trazem, sem gravar nada, para conferir o leiaute antes de coletar.

Índice: `?option=com_sisconama&task=atosnormativos.getList&tipo=1&ano=<ano>`, a listagem paginada do portal (número,
ano, ementa, situação e o arquivo de cada resolução). Texto: `?option=com_sisconama&task=arquivo.download&id=<aid>`,
o PDF que o portal serve, em geral a página do "Livro das Resoluções do CONAMA" do MMA ou a do DOU. O PDF nascido
digital passa por `pdftotext -layout` e `texto_pdf_para_md`; o escaneado fica retido (exige OCR). Retém também, com o
motivo em reguladores/conama/_falhas.jsonl: arquivo ausente ou que não é PDF, e epígrafe que não confere com o número
e o ano da listagem.

    python3 -I scripts/baixar_conama.py --apesar-do-robots --despejar --de 1986 --ate 1986
    python3 -I scripts/baixar_conama.py --apesar-do-robots --de 1984 --ate 2016
"""
import argparse
import collections
import datetime as dt
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import Rede, extrair_texto, gravar, texto_pdf_para_md  # noqa: E402

AUTORIZACAO = {
    "host": "conama.mma.gov.br",
    "data": "2026-11-20",
    "motivo": "robots.txt com Disallow: /, sem fonte oficial sem bloqueio para o texto das resoluções anteriores a 2017",
    "escopo": "resoluções do CONAMA de 1984 a 2016",
    "rps": 0.2,
}
ULTIMO_ANO = 2016  # de 2017 em diante, o DOU em texto (baixar_dou.py)
RAIZ = Path(__file__).resolve().parent.parent
PASTA = RAIZ / "reguladores" / "conama" / "resolucoes"
FONTE = RAIZ / "reguladores" / "_fonte" / "conama"
INDICE = RAIZ / "reguladores" / "conama" / "_indice"
FALHAS = RAIZ / "reguladores" / "conama" / "_falhas.jsonl"
BASE = "https://conama.mma.gov.br/"
LISTA = BASE + "?option=com_sisconama&task=atosnormativos.getList&tipo=1&ano={ano}&offset={inicio}&limit={n}"
ARQUIVO = BASE + "?option=com_sisconama&task=arquivo.download&id={aid}"
POR_PAGINA = 30
MESES = "janeiro fevereiro marco abril maio junho julho agosto setembro outubro novembro dezembro".split()
MESES_RE = "|".join(MESES)
VERSAO = ("texto do PDF que o CONAMA disponibiliza em conama.mma.gov.br (em geral a página do Livro das Resoluções do "
          "CONAMA, do MMA, ou a do Diário Oficial da União); não substitui a publicação oficial")


class Recusa(RuntimeError):
    pass


def sem_acento(texto):
    return "".join(c for c in unicodedata.normalize("NFD", texto) if not unicodedata.combining(c))


def obter(rede, url):
    try:
        status, dados, tipo = rede.get(url)
    except RuntimeError as e:
        if re.search(r"HTTP Error (?:401|429)\b", str(e)):
            raise Recusa(f"a fonte recusou o acesso: {url}") from e
        raise
    if status in (401, 403, 429):
        raise Recusa(f"a fonte recusou o acesso (HTTP {status}): {url}")
    if status != 200:
        raise RuntimeError(f"HTTP {status}: {url}")
    return dados, tipo


def listar_ano(rede, ano):
    """Resoluções de um ano na listagem do portal; confere a soma das páginas com o total anunciado."""
    linhas, total, inicio = [], None, 0
    while total is None or inicio < total:
        dados, _ = obter(rede, LISTA.format(ano=ano, inicio=inicio, n=POR_PAGINA))
        pagina = (json.loads(dados).get("data") or {})
        total = int(pagina.get("total") or 0)
        novas = pagina.get("rows") or []
        if not novas:
            break
        linhas += novas
        inicio += len(novas)
    if len(linhas) != total:
        raise RuntimeError(f"listagem de {ano} incompleta: {len(linhas)} de {total}")
    itens = []
    for r in linhas:
        if r.get("nomeato") != "Resolução" or str(r.get("ano")) != str(ano):
            continue
        itens.append({"numero": int(r["numero"]), "ano": int(r["ano"]), "ementa": " ".join((r.get("descricao") or "").split()),
                      "situacao": " ".join((r.get("status") or "").split()), "aid": r.get("aid"), "arquivo": r.get("anome")})
    return sorted(itens, key=lambda i: i["numero"])


# Cabeçalho e rodapé das páginas do Livro das Resoluções do CONAMA ("LICENCIAMENTO AMBIENTAL – Normas e procedimentos
#      RESOLUÇÃO CONAMA nº 1 de 1986"; "RESOLUÇÕES DO CONAMA 639", com o número da página): não são texto da norma.
CABECALHO_LIVRO = re.compile(r"^\s*\S.*?\s{3,}RESOLU[ÇC][ÃA]O CONAMA n[º°o]\s*\d+\s+de\s+\d{4}\s*$")
RODAPE_LIVRO = re.compile(r"^\s*(?:RESOLU[ÇC][ÕO]ES DO CONAMA\s+\d+|\d+\s+RESOLU[ÇC][ÕO]ES DO CONAMA)\s*$")


def limpar_livro(texto):
    return "\n".join(("\f" if l.startswith("\f") else "") if CABECALHO_LIVRO.match(l) or RODAPE_LIVRO.match(l) else l
                     for l in texto.split("\n"))


def epigrafe(texto, numero, ano):
    """Data ISO da epígrafe "RESOLUÇÃO CONAMA nº 1, de 23 de janeiro de 1986" do próprio ato, ou ""."""
    plano = re.sub(r"\s+", " ", sem_acento(texto).lower())
    for m in re.finditer(r"resolucao(?: conama)?\s+n[º°o.]*\s*0*(\d+)\s*,?\s*de\s+(\d{1,2})[º°o]?\s+de\s+(" + MESES_RE
                         + r")\s+de\s+(\d{4})", plano):
        if int(m.group(1)) == numero and int(m.group(4)) == ano:
            try:
                return dt.date(ano, MESES.index(m.group(3)) + 1, int(m.group(2))).isoformat()
            except ValueError:
                return ""
    return ""


def publicacao(texto):
    """("Publicada no DOU, de 17 de fevereiro de 1986, Seção 1, páginas 2548-2549", "1986-02-17"), pela linha do PDF."""
    for linha in texto.split("\n"):
        linha = re.sub(r"\s+", " ", linha).strip()
        m = re.search(r"Publicad[ao] no D\.?O\.?U\.?,?\s+(?:n[º°o.]*\s*[\d.]+,?\s+)?(?:de\s+)?(\d{1,2})[º°o]?\s+de\s+"
                      r"([A-Za-zçÇ]+)\s+de\s+(\d{4}).*$", linha)
        if not m:
            continue
        mes, data = sem_acento(m.group(2)).lower(), ""
        if mes in MESES:
            try:
                data = dt.date(int(m.group(3)), MESES.index(mes) + 1, int(m.group(1))).isoformat()
            except ValueError:
                data = ""
        return m.group(0).strip(" ."), data
    return "", ""


def titulo(numero, data):
    ano, mes, dia = (int(p) for p in data.split("-"))
    nome_mes = ("janeiro fevereiro março abril maio junho julho agosto setembro outubro novembro dezembro").split()[mes - 1]
    return f"Resolução CONAMA nº {numero}, de {'1º' if dia == 1 else dia} de {nome_mes} de {ano}"


def processar(rede, item):
    slug = f"res-conama-{item['numero']}-{item['ano']}"
    md = PASTA / str(item["ano"]) / f"{slug}.md"
    if md.exists():
        return "pulado", None
    falha = {"numero": item["numero"], "ano": item["ano"], "aid": item["aid"]}
    if not item["aid"]:
        return "retido", {**falha, "motivo": "a listagem não traz arquivo para a resolução"}
    url = ARQUIVO.format(aid=item["aid"])
    bruto, _ = obter(rede, url)
    if bruto[:4] != b"%PDF":
        return "retido", {**falha, "motivo": "o arquivo servido não é PDF", "inicio": bruto[:40].decode("latin-1")}
    _, texto = extrair_texto(bruto, url)
    if len(re.sub(r"\W", "", texto or "")) < 300:
        return "retido", {**falha, "motivo": "PDF escaneado, sem camada de texto: exige OCR"}
    texto = limpar_livro(texto)
    data = epigrafe(texto, item["numero"], item["ano"])
    if not data:
        return "retido", {**falha, "motivo": "epígrafe com o número e o ano da listagem não encontrada no PDF"}
    corpo = texto_pdf_para_md(texto)
    pub, data_pub = publicacao(texto)
    nome = titulo(item["numero"], data)
    meta = [("titulo", nome), ("orgao", "Conselho Nacional do Meio Ambiente"), ("tipo", "Resolução"),
            ("numero", str(item["numero"])), ("data", data), ("ementa", item["ementa"])]
    if item["situacao"]:
        meta.append(("situacao", item["situacao"]))
    meta += [("revogada", bool(re.match(r"(?i)revogad", item["situacao"]))), ("versao_texto", VERSAO)]
    if pub:
        meta.append(("publicacao", pub))
        if data_pub:
            meta.append(("data_publicacao", data_pub))
    meta += [("fonte", url), ("sha256_fonte", hashlib.sha256(bruto).hexdigest())]
    gravar(str(md), str(FONTE / str(item["ano"]) / f"{slug}.pdf.gz"), bruto, meta, f"# {nome}\n\n{corpo}")
    return "ok", None


def registrar(falha, ja):
    chave = (falha["numero"], falha["ano"], falha["motivo"])
    if chave in ja:
        return
    ja.add(chave)
    FALHAS.parent.mkdir(parents=True, exist_ok=True)
    with open(FALHAS, "a", encoding="utf-8") as f:
        f.write(json.dumps(falha, ensure_ascii=False, sort_keys=True) + "\n")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--apesar-do-robots", action="store_true",
                    help=f"obrigatória: o robots.txt veda o portal; exceção autorizada em {AUTORIZACAO['data']}")
    ap.add_argument("--de", type=int, default=1984)
    ap.add_argument("--ate", type=int, default=ULTIMO_ANO)
    ap.add_argument("--despejar", action="store_true", help="mostra a listagem e o primeiro PDF, sem gravar")
    ap.add_argument("--limite", type=int, default=0)
    a = ap.parse_args(argv)
    if not a.apesar_do_robots:
        ap.error("o robots.txt de conama.mma.gov.br veda a coleta; a exceção autorizada exige --apesar-do-robots")
    if a.ate > ULTIMO_ANO or a.de > a.ate:
        ap.error(f"a exceção cobre só {AUTORIZACAO['escopo']}; de 2017 em diante use baixar_dou.py")
    rede = Rede(AUTORIZACAO["rps"])
    cont, ja = collections.Counter(), set()
    if FALHAS.exists():
        ja = {(d["numero"], d["ano"], d["motivo"]) for d in map(json.loads, FALHAS.read_text(encoding="utf-8").splitlines())}
    try:
        for ano in range(a.de, a.ate + 1):
            itens = listar_ano(rede, ano)
            print(f"[CONAMA] {ano}: {len(itens)} resoluções na listagem", flush=True)
            if a.despejar:
                for i in itens[:5]:
                    print("   ", json.dumps(i, ensure_ascii=False))
                if itens and itens[0]["aid"]:
                    bruto, _ = obter(rede, ARQUIVO.format(aid=itens[0]["aid"]))
                    _, texto = extrair_texto(bruto, "x.pdf") if bruto[:4] == b"%PDF" else (None, "")
                    print(f"    PDF de {itens[0]['numero']}/{ano}: {len(bruto)} bytes, {len(texto or '')} caracteres de "
                          f"texto, epígrafe {epigrafe(texto or '', itens[0]['numero'], ano) or 'não achada'}, "
                          f"publicação {publicacao(texto or '')}")
                continue
            INDICE.mkdir(parents=True, exist_ok=True)
            (INDICE / f"{ano}.json").write_text(json.dumps(itens, ensure_ascii=False, indent=0) + "\n", encoding="utf-8")
            for item in itens[: a.limite or None]:
                try:
                    estado, falha = processar(rede, item)
                except Recusa:
                    raise
                except Exception as e:  # rede ou arquivo malformado: conta e segue
                    estado, falha = "erro", None
                    print(f"[CONAMA] erro em {item['numero']}/{ano}: {str(e)[:200]}", flush=True)
                cont[estado] += 1
                if falha:
                    registrar(falha, ja)
            print(f"[CONAMA] até {ano}: {dict(cont)}", flush=True)
    except Recusa as e:
        print(f"[CONAMA] {e}. Coleta interrompida.", flush=True)
        return 2
    print(f"[CONAMA] FIM {dict(cont)}", flush=True)
    return 1 if cont["erro"] else 0


if __name__ == "__main__":
    sys.exit(main())
