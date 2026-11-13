"""Paraná — Sistema Estadual de Legislação (Casa Civil, legislacao.pr.gov.br).

Índice: listarAtosAno.do?action=listarAtos&anoAto=AAAA (POST com codTipoAto), um ano por vez; os decretos,
que a fonte lista por mês, com &mesAto=M (13 é o ano inteiro).
Texto: pesquisarAto.do?action=exibir&codAto=N&tipoVisualizacao=compilado (texto compilado).

Uso: python3 -I scripts/estados/pr.py [--tipo leis-ordinarias] [--anos 2020-2026] [--rps 0.25] [--so-indice] [limite]
     python3 -I scripts/estados/pr.py --tipo decretos --anos 2026 --conferir   (fecha o lote contra o índice)
     python3 -I scripts/estados/pr.py --atos 14467,14471 [--rps 0.2]   (atos que nenhuma listagem entrega)
O índice guarda em _indice cada página por tipo e ano, então uma coleta interrompida retoma de onde parou.
Listagem de ano sem ato algum é falha da fonte (HTTP 200 com página de erro): não é guardada e o ano é pedido
mês a mês; o mês que também falhar é avisado e a execução termina com erro. Os atos desse mês continuam
acessíveis pelo codAto: --atos os pede um a um e tira a epígrafe, o ano e a súmula da página de cada ato.
O servidor recusa (HTTP 403) quem pede demais: a primeira recusa interrompe a coleta inteira, sem registrar
falha para os itens restantes, e a coleta deve recomeçar mais tarde em ritmo menor.
"""
import datetime as dt
import glob
import gzip
import html as htmllib
import http.cookiejar
import json
import os
import re
import sys
import threading
import time
import unicodedata
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
SEM_INDICE = []  # (codTipoAto, ano, mês) cuja listagem a fonte não entregou; ficam fora do recorte e do cache
# O mês sem atos e a página de erro trazem ambos "Nenhum registro encontrado"; só o erro preenche a mensagem AJAX.
SEM_ATOS = "Nenhum registro encontrado"
ERRO_DA_FONTE = "globalAjaxMsgError +="
TODOS_OS_MESES = 13  # nos tipos listados por mês (decretos), a fonte numera assim a opção do ano inteiro
_sessao = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
LINHA = re.compile(
    r"codAto=(\d+)&indice.*?_epigrafeAto\">(.*?)</div>.*?_descricaoItemAto\">(.*?)</div>.*?_dataPublicacao\">(.*?)</div>",
    re.S,
)
def sem_acento(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


MESES = {sem_acento(m): i for i, m in enumerate(
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


def cobertura(ids_indice, ids_md, ids_falha):
    """codAto do índice cobertos por markdown no disco ou por linha em `_falhas.jsonl`."""
    indice = {str(i) for i in ids_indice}
    md = {str(i) for i in ids_md}
    falha = {str(i) for i in ids_falha}
    return {
        "indice": len(indice),
        "md": len(indice & md),
        "falhas": len(indice & falha),
        "faltando": sorted(indice - md - falha, key=lambda s: int(s) if s.isdigit() else s),
    }


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


def pagina_do_indice(pasta, tipo, ano, refazer, mes=None):
    """Listagem do ano, ou de um mês dele, vinda do cache ou da fonte; None quando a fonte devolve erro.
    O ano (sem mês, ou TODOS_OS_MESES) vem da lista de anos com atos, então só vale com atos; o mês também vale
    vazio. Erro não fica no cache."""
    cache = os.path.join(pasta, f"tipo-{tipo}-{ano}{f'-{mes:02d}' if mes else ''}.html")

    def valida(h):
        return bool(LINHA.search(h)) or (mes not in (None, TODOS_OS_MESES) and SEM_ATOS in h and ERRO_DA_FONTE not in h)

    if os.path.exists(cache) and not refazer:
        with open(cache, encoding="utf-8") as f:
            h = f.read()
        if valida(h):
            return h
    h = post(
        f"listarAtosAno.do?action=listarAtos&anoAto={ano}{f'&mesAto={mes}' if mes else ''}&isPaginado=false",
        dict(codTipoAto=tipo, codTipoAtoSelecionado=tipo, codOrgaoUnidade="1100", codOrgaoUnidadeSelecionado="1100",
             pesquisou="", anoAtoPesquisado="0", paginaAtual="", isPaginado="false", site="1"),
    )
    if not valida(h):
        if os.path.exists(cache):
            os.remove(cache)
        return None
    with open(cache, "w", encoding="utf-8") as f:
        f.write(h)
    return h


def recortes_sem_indice():
    """Anos e meses que a fonte não listou, por extenso; o ano com os doze meses em falta aparece uma vez só."""
    por_ano = {}
    for tipo, ano, mes in SEM_INDICE:
        por_ano.setdefault((tipo, ano), []).append(mes)
    return ", ".join(
        f"{TIPOS[t][0]} {a}" + ("" if len(meses) == 12 else " (" + ", ".join(f"mês {m:02d}" for m in meses) + ")")
        for (t, a), meses in por_ano.items())


def listagem_do_ano(pasta, tipo, ano, refazer, meses, tem_listagem_anual, registrar=True):
    """Páginas da listagem de um ano: a do ano inteiro ou, se ela faltar, as dos meses. Sem a listagem do ano, ou
    com ela derrubada por um ato defeituoso (leis ordinárias de 1954), os meses saem um a um: os que a fonte
    anuncia ou, sem anúncio, os doze. O mês que também falhar entra em SEM_INDICE, se `registrar`."""
    if tem_listagem_anual:
        inteiro = pagina_do_indice(pasta, tipo, ano, refazer)
    elif TODOS_OS_MESES in meses:
        inteiro = pagina_do_indice(pasta, tipo, ano, refazer, TODOS_OS_MESES)
    else:
        inteiro = None
    if inteiro is not None:
        return [inteiro]
    paginas = []
    for mes in (m for m in meses if m != TODOS_OS_MESES):
        h = pagina_do_indice(pasta, tipo, ano, refazer, mes)
        if h is not None:
            paginas.append(h)
        elif registrar:
            SEM_INDICE.append((tipo, ano, mes))
    return paginas


def ano_da_epigrafe(epigrafe):
    """Ano da data da epígrafe ("Decreto 12323 - 18 de Dezembro de 2025", "... de 2025 - REPUBLICADO"), ou None."""
    m = re.search(r" de \w+ de (\d{4})\b", epigrafe)
    return m.group(1) if m else None


_LISTADOS = {}  # (codTipoAto, ano) -> codAto que a listagem daquele ano traz
_LISTADOS_TRAVA = threading.Lock()


def listado_em(tipo, ano, cod):
    """A fonte lista o ato `cod` no ano `ano`? Lê a listagem daquele ano, do cache ou da fonte, uma vez só.
    Ano que a fonte não anuncia, ou cuja listagem falha, conta como não listado, sem registrar falha de índice."""
    with _LISTADOS_TRAVA:
        if (tipo, ano) not in _LISTADOS:
            pasta = os.path.join(RAIZ_ESTADUAIS, UF, "_indice")
            html = pagina_de_anos(tipo, pasta, False)
            anuais = {a for _, a in re.findall(r"listarAtos\('(\d{4})', '(\d{4})'\)", html)}
            meses = sorted({int(m) for _, a, m in re.findall(r"listarAtosAnoMes\('(\d{4})', '(\d{4})', '(\d{1,2})'\)", html) if a == ano})
            paginas = listagem_do_ano(pasta, tipo, ano, False, meses or range(1, 13), ano in anuais, registrar=False) if ano in anuais or meses else []
            _LISTADOS[tipo, ano] = {c for c, *_ in LINHA.findall("".join(paginas))}
        return cod in _LISTADOS[tipo, ano]


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
        # Os decretos saem por listarAtosAnoMes: os doze meses e a opção 13, que é o ano inteiro.
        meses_do_tipo = {}
        for _, ano, mes in re.findall(r"listarAtosAnoMes\('(\d{4})', '(\d{4})', '(\d{1,2})'\)", html):
            meses_do_tipo.setdefault(ano, set()).add(int(mes))
        if not anos_do_tipo and not meses_do_tipo and not anos:  # um único ato (Constituição): a página já é o ato
            for cod in dict.fromkeys(re.findall(r'name="codAto" value="(\d+)"', html)):
                itens[cod, None] = {"codAto": cod, "tipo": tipo, "epigrafe": "", "ementa": "", "publicacao": ""}
        for ano in sorted(set(anos_do_tipo) | set(meses_do_tipo), reverse=True):
            if anos and int(ano) not in anos:
                continue
            meses = sorted(meses_do_tipo.get(ano) or range(1, 13))
            paginas = listagem_do_ano(pasta, tipo, ano, refazer, meses, ano in anos_do_tipo)
            # A chave leva o ano porque a fonte lista alguns atos em dois anos (o decreto republicado, no da data
            # e no da republicação); `processar` grava cada um num ano só.
            for cod, epi, ementa, pub in LINHA.findall("".join(paginas)):
                itens[cod, ano] = {"codAto": cod, "tipo": tipo, "ano": ano, "epigrafe": limpar(epi), "ementa": limpar(ementa), "publicacao": limpar(pub)}
        print(f"[{UF}] índice tipo {tipo}: {sum(1 for i in itens.values() if i['tipo'] == tipo)}", flush=True)
    lista = list(itens.values())
    if not tipos and not anos and not SEM_INDICE:
        with open(arq, "w", encoding="utf-8") as f:
            json.dump(lista, f, ensure_ascii=False)
    return lista


def pagina_do_ato(cod):
    """(HTTP, bytes, content-type) da página do ato, do cache de documentos ou da fonte; None quando a fonte
    recusa o acesso (e então liga RECUSADO). Toda resposta 200 fica no cache."""
    cache = os.path.join(RAIZ_ESTADUAIS, UF, "_indice", "documentos", cod + ".html.gz")
    if os.path.exists(cache):
        with open(cache, "rb") as f:
            return 200, gzip.decompress(f.read()), "text/html;charset=UTF-8"
    if RECUSADO.is_set():
        return None
    try:
        st, bruto, ctype = rede.get(f"{B}/exibirAto.do?action=iniciarProcesso&codAto={cod}", timeout=60, tentativas=1)
    except RuntimeError as e:
        if "HTTP Error 429" in str(e):
            RECUSADO.set()
            return None
        raise
    if st in RECUSA_HTTP:
        RECUSADO.set()
        return None
    if st == 200:
        os.makedirs(os.path.dirname(cache), exist_ok=True)
        with open(cache, "wb") as f:
            f.write(gzip.compress(bruto))
    return st, bruto, ctype


def itens_avulsos(cods):
    """Itens de índice montados da página de cada ato, para os que nenhuma listagem entrega (junho de 1954).
    Devolve (itens, codAto sem ato): a fonte responde 200 com a página em branco para o codAto que não existe."""
    itens, sem_ato = [], []
    for cod in cods:
        resposta = pagina_do_ato(cod)
        if resposta is None:
            raise RuntimeError("fonte recusou acesso; coleta interrompida")
        st, bruto, ctype = resposta
        html = decodificar(bruto, ctype) if st == 200 else ""
        tipo = re.search(r'name="codTipoAto" value="(\d+)"', html)
        epigrafe = limpar((re.search(r"<h3>(.*?)</h3>", html, re.S) or ["", ""])[1])
        ano = re.search(r" de (\d{4})$", epigrafe)
        if not tipo or tipo.group(1) not in TIPOS or not ano:
            sem_ato.append(cod)
            continue
        ementa = re.search(r"S[úu]mula:</b>\s*<a[^>]*>(.*?)</a>", html, re.S)
        itens.append({"codAto": cod, "tipo": tipo.group(1), "ano": ano.group(1), "epigrafe": epigrafe,
                      "ementa": limpar(ementa.group(1)) if ementa else "", "publicacao": ""})
    return itens, sem_ato


def processar(it):
    pasta, nome, prefixo = TIPOS[it["tipo"]]
    url = f"{B}/exibirAto.do?action=iniciarProcesso&codAto={it['codAto']}"  # o mesmo endereço pedido em pagina_do_ato
    epi = it.get("epigrafe") or ""
    num = re.search(r"([\d.]+)\s*-\s*(\d{1,2})[º°]? de (\w+) de (\d{4})", epi)  # dia 1º vem com ordinal
    ano = it.get("ano") or (num.group(4) if num else "sem-ano")
    numero = num.group(1).replace(".", "") if num else "sn"
    slug = f"{prefixo}-{numero}-{ano}-id{it['codAto']}"
    md, fonte = caminhos(UF, pasta, ano, slug)
    if os.path.exists(md):
        return "pulado", None
    resposta = pagina_do_ato(it["codAto"])
    if resposta is None:
        return "bloqueado", None
    st, bruto, ctype = resposta
    if st != 200:
        return "sem_texto", {"codAto": it["codAto"], "http": st}
    html = decodificar(bruto, ctype)
    ini = html.find("<h3>")
    fim = html.find("</form>", ini)
    if ini < 0:
        return "sem_texto", {"codAto": it["codAto"], "motivo": "sem texto"}
    trecho = html[ini : fim if fim > 0 else None]
    titulo = limpar(re.search(r"<h3>(.*?)</h3>", trecho, re.S).group(1)) or epi
    do_titulo = ano_da_epigrafe(titulo)
    if it.get("ano") and do_titulo and do_titulo != it["ano"]:
        # A listagem deste ano traz um ato que a própria página data de outro: republicação, ou erro de digitação
        # na listagem (Lei 20941, de 2021, listada também em 2010). Se a fonte o lista no ano da página, é lá que
        # ele entra; se não, fica aqui, a menos que outro ano em que também apareça já o tenha gravado.
        if listado_em(it["tipo"], do_titulo, it["codAto"]):
            return "pulado", None
        if glob.glob(os.path.join(os.path.dirname(os.path.dirname(md)), "*", f"*-id{it['codAto']}.md")):
            return "pulado", None
    if "exibirAnexo(" in trecho:  # a lei remete a anexos em PDF (tabelas, mapas), que não estão no HTML do ato
        return "sem_texto", {"codAto": it["codAto"], "motivo": "anexos em PDF não coletados: o texto do ato ficaria incompleto"}
    corpo = html_para_md(trecho)
    if len(re.sub(r"\W", "", corpo)) < 40:
        return "sem_texto", {"codAto": it["codAto"], "motivo": "texto vazio"}
    data = ""
    m = re.search(r"(\d{1,2})[º°]? de (\w+) de (\d{4})", titulo)
    mes = sem_acento(m.group(2).lower()) if m else ""
    if m and mes in MESES:
        data = f"{m.group(3)}-{MESES[mes]:02d}-{int(m.group(1)):02d}"
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


def conferir(itens):
    """Fecha o recorte contra o índice, sem coletar: cada ato tem de ter markdown, linha de retenção em
    `_falhas.jsonl` ou pertencer a outro ano (ver `processar`). Devolve o relatório; `pendencias` diz se o lote
    ainda não fecha. Lê só o que já está em disco, salvo a listagem de outro ano que ainda não esteja no cache."""
    retidos, erros, repetidas = set(), [], 0
    falhas = os.path.join(RAIZ_ESTADUAIS, UF, "_falhas.jsonl")
    if os.path.exists(falhas):
        with open(falhas, encoding="utf-8") as f:
            for linha in f:
                reg = json.loads(linha) if linha.strip() else {}
                if reg.get("status") == "erro":  # falha de rede: some ao repetir a coleta, não é retenção
                    erros += re.findall(r"'codAto': '(\d+)'", reg.get("item", ""))
                elif reg.get("codAto"):
                    repetidas += reg["codAto"] in retidos
                    retidos.add(reg["codAto"])
    gravados = {}  # codTipoAto -> codAto com markdown, em qualquer ano
    for tipo in {i["tipo"] for i in itens}:
        nomes = glob.glob(os.path.join(RAIZ_ESTADUAIS, UF, TIPOS[tipo][0], "*", "*-id*.md"))
        gravados[tipo] = {n.rsplit("-id", 1)[1][:-3] for n in nomes}
    rel = {"indice": 0, "md": 0, "retidos": 0, "de_outro_ano": [], "faltando": []}
    for cod, tipo, ano in sorted({(i["codAto"], i["tipo"], i.get("ano")) for i in itens}, key=lambda t: int(t[0])):
        rel["indice"] += 1
        if cod in gravados[tipo]:
            rel["md"] += 1
        elif cod in retidos:
            rel["retidos"] += 1
        else:
            cache = os.path.join(RAIZ_ESTADUAIS, UF, "_indice", "documentos", cod + ".html.gz")
            do_titulo = None
            if ano and os.path.exists(cache):
                st, bruto, ctype = pagina_do_ato(cod)
                h3 = re.search(r"<h3>(.*?)</h3>", decodificar(bruto, ctype), re.S)
                do_titulo = ano_da_epigrafe(limpar(h3.group(1))) if h3 else None
            if do_titulo and do_titulo != ano and listado_em(tipo, do_titulo, cod):
                rel["de_outro_ano"].append(cod)
            else:
                rel["faltando"].append(cod)
    do_recorte = {i["codAto"] for i in itens}
    rel["erros_de_rede"] = sorted(set(erros) & do_recorte, key=int)
    rel["retencoes_repetidas"] = repetidas
    rel["pendencias"] = bool(rel["faltando"] or rel["erros_de_rede"])
    return rel


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(description=f"Coletor da legislação de {UF} (Casa Civil)")
    parser.add_argument("--refazer", action="store_true", help="Baixa de novo as páginas do índice")
    parser.add_argument("--tipo", type=str, help="Pasta ou codTipoAto, separados por vírgula, ex: leis-ordinarias ou 1,3")
    parser.add_argument("--anos", type=str, help="Ano ou intervalo, ex: 2024 ou 2020-2026")
    parser.add_argument("--rps", type=float, default=1.0, help="Requisições por segundo (padrão 1)")
    parser.add_argument("--workers", type=int, default=3, help="Textos em paralelo (padrão 3)")
    parser.add_argument("--so-indice", action="store_true", help="Só monta o índice do recorte, sem baixar os textos")
    parser.add_argument("--atos", type=str, help="codAto separados por vírgula, no lugar do índice: atos que a listagem não entrega")
    parser.add_argument("--conferir", action="store_true", help="Não coleta: confere o recorte contra markdown e _falhas.jsonl")
    parser.add_argument("limite", nargs="?", type=int, default=None, help="Máximo de itens a processar")
    args = parser.parse_args(argv)
    if args.rps != 1.0:
        rede.limite = Limitador(args.rps)
    try:
        tipos = codigos_de_tipo(args.tipo) if args.tipo else None
        anos = faixa_de_anos(args.anos) if args.anos else None
    except ValueError as e:
        sys.exit(f"[{UF}] {e}")
    sem_ato = []
    try:
        if args.atos:
            cods = [c.strip() for c in args.atos.split(",") if c.strip()]
            if not all(c.isdigit() for c in cods):
                sys.exit(f"[{UF}] --atos espera codAto numéricos separados por vírgula")
            itens, sem_ato = itens_avulsos(list(dict.fromkeys(cods)))
            itens = filtrar(itens, tipos, anos)
        else:
            itens = indice(refazer=args.refazer, tipos=tipos, anos=anos)
    except (RuntimeError, OSError) as e:  # OSError cobre a fonte fora do ar (HTTP 503, tempo esgotado, DNS)
        sys.exit(f"[{UF}] {e}. O índice guarda as páginas já baixadas: rode de novo mais tarde, com --rps menor.")
    itens.sort(key=lambda i: (i.get("ano") or "", int(i["codAto"])), reverse=True)
    print(f"[{UF}] {len(itens)} normas no recorte do índice", flush=True)
    sem_indice = ""
    if SEM_INDICE:
        sem_indice = (f"[{UF}] a fonte não entregou a listagem de: {recortes_sem_indice()}. Esses recortes ficaram fora do "
                      "índice e não foram guardados em _indice; rode de novo para pedi-los outra vez.")
        if not args.so_indice:
            print(sem_indice, flush=True)
    if args.conferir:
        rel = conferir(itens)
        print(f"[{UF}] conferência: {rel['indice']} atos no índice = {rel['md']} com markdown + {rel['retidos']} retidos em "
              f"_falhas.jsonl + {len(rel['de_outro_ano'])} de outro ano + {len(rel['faltando'])} faltando", flush=True)
        for rotulo, chave in (("faltando", "faltando"), ("de outro ano", "de_outro_ano"), ("com erro de rede em _falhas.jsonl", "erros_de_rede")):
            if rel[chave]:
                print(f"[{UF}] {rotulo}: {', '.join(rel[chave][:40])}{' ...' if len(rel[chave]) > 40 else ''}", flush=True)
        if rel["retencoes_repetidas"]:
            print(f"[{UF}] {rel['retencoes_repetidas']} linha(s) de retenção repetida(s) em _falhas.jsonl", flush=True)
        if rel["pendencias"]:
            sys.exit(f"[{UF}] o recorte não fecha: repita a coleta e tire de _falhas.jsonl as linhas com status 'erro'.")
    elif not args.so_indice:
        if args.limite:
            itens = itens[: args.limite]
        executar(UF, itens, processar, workers=args.workers)
        if RECUSADO.is_set():
            sys.exit(f"[{UF}] a fonte recusou o acesso (HTTP 401, 403 ou 429); coleta interrompida sem registrar falha nos itens "
                     "restantes. Rode de novo mais tarde, com --rps menor.")
    if sem_indice:
        sys.exit(sem_indice)
    if sem_ato:
        sys.exit(f"[{UF}] a fonte não tem ato nestes codAto: {', '.join(sem_ato)}")


if __name__ == "__main__":
    main()
