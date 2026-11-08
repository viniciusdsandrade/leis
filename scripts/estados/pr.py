"""Paraná — Sistema Estadual de Legislação (Casa Civil, legislacao.pr.gov.br).

Índice: listarAtosAno.do?action=listarAtos&anoAto=AAAA (POST com codTipoAto), um ano por vez.
Texto: pesquisarAto.do?action=exibir&codAto=N&tipoVisualizacao=compilado (texto compilado).

Uso: python3 -I scripts/estados/pr.py [--tipo leis-ordinarias] [--anos 2020-2026] [--rps 0.25] [--so-indice] [limite]
O índice guarda em _indice cada página por tipo e ano, então uma coleta interrompida retoma de onde parou.
O servidor recusa (HTTP 403) quem pede demais: a primeira recusa interrompe a coleta inteira, sem registrar
falha para os itens restantes, e a coleta deve recomeçar mais tarde em ritmo menor.
"""
import datetime as dt
import gzip
import html as htmllib
import http.cookiejar
import json
import os
import re
import sys
import threading
import time
import urllib.parse
import urllib.request
import urllib.error

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from comum import RAIZ_ESTADUAIS, UA, Limitador, Rede, caminhos, decodificar, executar, gravar, html_para_md  # noqa: E402

UF = "PR"
B = "https://www.legislacao.pr.gov.br/legislacao"
# codTipoAto do sistema da Casa Civil -> (pasta, tipo canônico, prefixo do arquivo). O seletor da
# pesquisa oferece sete tipos; o infralegal entra junto, como nos demais estados.
TIPOS = {
    "10": ("constituicao", "Constituição Estadual", "ce"),
    "9": ("emendas-constitucionais", "Emenda Constitucional", "ec"),
    "3": ("leis-complementares", "Lei Complementar", "lc"),
    "1": ("leis-ordinarias", "Lei Ordinária", "lei"),
    "11": ("decretos", "Decreto", "dec"),
    "13": ("resolucoes", "Resolução", "res"),
    "14": ("portarias", "Portaria", "port"),
}
rede = Rede(rps=1)  # o WAF já devolveu 403 a partir da segunda requisição; mantém-se devagar
RECUSA_HTTP = (401, 403, 429)
RECUSADO = threading.Event()  # ligado na primeira recusa da fonte; os demais itens não vão à rede
_sessao = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
LINHA = re.compile(
    r"codAto=(\d+)&indice.*?_epigrafeAto\">(.*?)</div>.*?_descricaoItemAto\">(.*?)</div>.*?_dataPublicacao\">(.*?)</div>",
    re.S,
)
MESES = {m: i for i, m in enumerate(
    "janeiro fevereiro março abril maio junho julho agosto setembro outubro novembro dezembro".split(), 1)}


def limpar(s):
    return " ".join(htmllib.unescape(re.sub(r"<[^>]+>", " ", s)).split())


def post(caminho, dados, tentativas=4):
    req = urllib.request.Request(f"{B}/{caminho}", data=urllib.parse.urlencode(dados).encode(), headers={"User-Agent": UA})
    for n in range(tentativas):
        rede.limite.esperar()
        try:
            with _sessao.open(req, timeout=300) as r:
                return decodificar(r.read(), r.headers.get("Content-Type") or "")
        except urllib.error.HTTPError as e:
            if e.code in (401, 403, 429):
                raise RuntimeError(f"fonte recusou acesso (HTTP {e.code}); coleta interrompida") from e
            if n == tentativas - 1:
                raise
            time.sleep(30 * (n + 1))
        except Exception:
            if n == tentativas - 1:
                raise
            time.sleep(30 * (n + 1))


def faixa_de_anos(txt):
    """'2024' ou '2020-2026' em conjunto de anos."""
    if "-" in txt:
        ini, fim = txt.split("-")
        return set(range(int(ini), int(fim) + 1))
    return {int(txt)}


def codigos_de_tipo(txt):
    """Pastas (leis-ordinarias) ou codTipoAto (1), separados por vírgula, em conjunto de codTipoAto."""
    pedidos = {t.strip() for t in txt.split(",") if t.strip()}
    cods = {c for c, (pasta, _, _) in TIPOS.items() if c in pedidos or pasta in pedidos}
    desconhecidos = pedidos - cods - {TIPOS[c][0] for c in cods}
    if desconhecidos:
        raise ValueError(f"tipo desconhecido: {', '.join(sorted(desconhecidos))}; válidos: {', '.join(sorted(t[0] for t in TIPOS.values()))}")
    return cods


def filtrar(lista, tipos=None, anos=None):
    return [i for i in lista
            if (not tipos or i["tipo"] in tipos)
            and (not anos or ((i.get("ano") or "").isdigit() and int(i["ano"]) in anos))]


def pagina_de_anos(tipo, pasta, refazer):
    """Página de pesquisa do tipo, que lista os anos com atos; fica em _indice para a retomada."""
    cache = os.path.join(pasta, f"tipo-{tipo}-anos.html")
    if os.path.exists(cache) and not refazer:
        with open(cache, encoding="utf-8") as f:
            return f.read()
    st, dados, ctype = rede.get(f"{B}/listarAtosAno.do?action=iniciarProcesso&tipoAto={tipo}&orgaoUnidade=1100&retiraLista=true&site=1")
    if st in RECUSA_HTTP:
        raise RuntimeError(f"fonte recusou acesso (HTTP {st}); coleta interrompida")
    if st != 200:
        raise RuntimeError(f"índice tipo {tipo}: HTTP {st}")
    html = decodificar(dados, ctype)
    with open(cache, "w", encoding="utf-8") as f:
        f.write(html)
    return html


def indice(refazer=False, tipos=None, anos=None):
    """Índice dos atos. `tipos` (codTipoAto) e `anos` (conjunto) limitam as páginas pedidas à fonte;
    só o índice completo é gravado em atos.json."""
    pasta = os.path.join(RAIZ_ESTADUAIS, UF, "_indice")
    arq = os.path.join(pasta, "atos.json")
    if os.path.exists(arq) and not refazer:
        return filtrar(json.load(open(arq, encoding="utf-8")), tipos, anos)
    itens = {}
    os.makedirs(pasta, exist_ok=True)
    for tipo in TIPOS:
        if tipos and tipo not in tipos:
            continue
        html = pagina_de_anos(tipo, pasta, refazer)
        anos_do_tipo = sorted({a for _, a in re.findall(r"listarAtos\('(\d{4})', '(\d{4})'\)", html)}, reverse=True)
        if not anos_do_tipo and not anos:  # tipo com um único ato (Constituição): a página já é o próprio ato
            for cod in dict.fromkeys(re.findall(r'name="codAto" value="(\d+)"', html)):
                itens[cod] = {"codAto": cod, "tipo": tipo, "epigrafe": "", "ementa": "", "publicacao": ""}
        for ano in anos_do_tipo:
            if anos and int(ano) not in anos:
                continue
            cache = os.path.join(pasta, f"tipo-{tipo}-{ano}.html")
            if os.path.exists(cache) and not refazer:
                with open(cache, encoding="utf-8") as f:
                    h = f.read()
            else:
                h = post(
                    f"listarAtosAno.do?action=listarAtos&anoAto={ano}&isPaginado=false",
                    dict(codTipoAto=tipo, codTipoAtoSelecionado=tipo, codOrgaoUnidade="1100", codOrgaoUnidadeSelecionado="1100",
                         pesquisou="", anoAtoPesquisado="0", paginaAtual="", isPaginado="false", site="1"),
                )
                with open(cache, "w", encoding="utf-8") as f:
                    f.write(h)
            for cod, epi, ementa, pub in LINHA.findall(h):
                itens[cod] = {"codAto": cod, "tipo": tipo, "ano": ano, "epigrafe": limpar(epi), "ementa": limpar(ementa), "publicacao": limpar(pub)}
        print(f"[{UF}] índice tipo {tipo}: {sum(1 for i in itens.values() if i['tipo'] == tipo)}", flush=True)
    lista = list(itens.values())
    if not tipos and not anos:
        with open(arq, "w", encoding="utf-8") as f:
            json.dump(lista, f, ensure_ascii=False)
    return lista


def processar(it):
    pasta, nome, prefixo = TIPOS[it["tipo"]]
    url = f"{B}/exibirAto.do?action=iniciarProcesso&codAto={it['codAto']}"
    epi = it.get("epigrafe") or ""
    num = re.search(r"([\d.]+)\s*-\s*(\d{1,2})[º°]? de (\w+) de (\d{4})", epi)  # dia 1º vem com ordinal
    ano = it.get("ano") or (num.group(4) if num else "sem-ano")
    numero = num.group(1).replace(".", "") if num else "sn"
    slug = f"{prefixo}-{numero}-{ano}-id{it['codAto']}"
    md, fonte = caminhos(UF, pasta, ano, slug)
    if os.path.exists(md):
        return "pulado", None
    cache = os.path.join(RAIZ_ESTADUAIS, UF, "_indice", "documentos", it["codAto"] + ".html.gz")
    if os.path.exists(cache):
        st, bruto, ctype = 200, gzip.decompress(open(cache, "rb").read()), "text/html;charset=UTF-8"
    else:
        if RECUSADO.is_set():
            return "bloqueado", None
        try:
            st, bruto, ctype = rede.get(url, timeout=60, tentativas=1)
        except RuntimeError as e:
            if "HTTP Error 429" in str(e):
                RECUSADO.set()
                return "bloqueado", None
            raise
        if st in RECUSA_HTTP:
            RECUSADO.set()
            return "bloqueado", None
    if st != 200:
        return "sem_texto", {"codAto": it["codAto"], "http": st}
    os.makedirs(os.path.dirname(cache), exist_ok=True)
    with open(cache, "wb") as f:
        f.write(gzip.compress(bruto))
    html = decodificar(bruto, ctype)
    ini = html.find("<h3>")
    fim = html.find("</form>", ini)
    if ini < 0:
        return "sem_texto", {"codAto": it["codAto"], "motivo": "sem texto"}
    trecho = html[ini : fim if fim > 0 else None]
    if "exibirAnexo(" in trecho:  # a lei remete a anexos em PDF (tabelas, mapas), que não estão no HTML do ato
        return "sem_texto", {"codAto": it["codAto"], "motivo": "anexos em PDF não coletados: o texto do ato ficaria incompleto"}
    titulo = limpar(re.search(r"<h3>(.*?)</h3>", trecho, re.S).group(1)) or epi
    corpo = html_para_md(trecho)
    if len(re.sub(r"\W", "", corpo)) < 40:
        return "sem_texto", {"codAto": it["codAto"], "motivo": "texto vazio"}
    data = ""
    m = re.search(r"(\d{1,2})[º°]? de (\w+) de (\d{4})", titulo)
    if m and m.group(2).lower() in MESES:
        data = f"{m.group(3)}-{MESES[m.group(2).lower()]:02d}-{int(m.group(1)):02d}"
    if data:
        try:
            if dt.date.fromisoformat(data) > dt.date.today():
                data = ""
        except ValueError:
            data = ""
    meta = [
        ("titulo", titulo),
        ("uf", UF),
        ("tipo", nome),
        ("numero", num.group(1) if num else ""),
        ("data", data),
        ("ementa", it.get("ementa") or ""),
        ("versao_texto", "compilada (Casa Civil do Paraná)"),
        ("fonte", url),
    ]
    gravar(md, fonte, trecho, meta, f"# {titulo}\n\n{corpo}")
    return "ok", None


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(description=f"Coletor da legislação de {UF} (Casa Civil)")
    parser.add_argument("--refazer", action="store_true", help="Baixa de novo as páginas do índice")
    parser.add_argument("--tipo", type=str, help="Pasta ou codTipoAto, separados por vírgula, ex: leis-ordinarias ou 1,3")
    parser.add_argument("--anos", type=str, help="Ano ou intervalo, ex: 2024 ou 2020-2026")
    parser.add_argument("--rps", type=float, default=1.0, help="Requisições por segundo (padrão 1)")
    parser.add_argument("--workers", type=int, default=3, help="Textos em paralelo (padrão 3)")
    parser.add_argument("--so-indice", action="store_true", help="Só monta o índice do recorte, sem baixar os textos")
    parser.add_argument("limite", nargs="?", type=int, default=None, help="Máximo de itens a processar")
    args = parser.parse_args(argv)
    if args.rps != 1.0:
        rede.limite = Limitador(args.rps)
    try:
        tipos = codigos_de_tipo(args.tipo) if args.tipo else None
        anos = faixa_de_anos(args.anos) if args.anos else None
    except ValueError as e:
        sys.exit(f"[{UF}] {e}")
    try:
        itens = indice(refazer=args.refazer, tipos=tipos, anos=anos)
    except RuntimeError as e:
        sys.exit(f"[{UF}] {e}. O índice guarda as páginas já baixadas: rode de novo mais tarde, com --rps menor.")
    itens.sort(key=lambda i: (i.get("ano") or "", int(i["codAto"])), reverse=True)
    print(f"[{UF}] {len(itens)} normas no recorte do índice", flush=True)
    if args.so_indice:
        return
    if args.limite:
        itens = itens[: args.limite]
    executar(UF, itens, processar, workers=args.workers)
    if RECUSADO.is_set():
        sys.exit(f"[{UF}] a fonte recusou o acesso (HTTP 401, 403 ou 429); coleta interrompida sem registrar falha nos itens restantes. "
                 "Rode de novo mais tarde, com --rps menor.")


if __name__ == "__main__":
    main()
