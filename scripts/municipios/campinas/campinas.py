"""Verificações dos lotes de Campinas (SAPL e bibjuri): identidade contra a API, carimbos residuais e regeneração.

Testes: test_campinas.py nesta pasta (fora do CI, que não faz checkout de scripts/municipios/).
"""
import argparse
import collections
import difflib
import hashlib
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]  # raiz do repositório
sys.path.insert(0, str(REPO / "scripts"))
from baixar_bibjuri_campinas import fonte_texto_coerente  # noqa: E402

HOST = "sapl.campinas.sp.leg.br"
MUN = REPO / "municipais/SP/campinas"
CACHE = REPO / "municipais/_indice/organicas-sapl" / HOST
FONTE = REPO / "municipais/_fonte/organicas-sapl" / HOST


def ler_md(p):
    texto = p.read_text()
    cab, _, resto = texto[4:].partition("\n---\n")
    meta = {}
    for linha in cab.splitlines():
        k, _, v = linha.partition(": ")
        meta[k] = json.loads(v)
    m = re.match(r"\n# [^\n]*\n\n", resto)
    corpo = resto[m.end():] if m else None
    if corpo is not None and corpo.endswith("\n"):
        corpo = corpo[:-1]
    return meta, corpo, texto


def todos_md():
    return sorted(MUN.glob("**/*.md"))


def id_sapl(meta):
    return int(meta["fonte"].rsplit("/", 1)[1])


def ultima_falha():
    """Última falha por id: falhas.jsonl do pipeline SAPL e, por cima, retidos e fichas sem cartão do coletor bibjuri."""
    out = {}
    f = CACHE / "falhas.jsonl"
    if f.exists():
        for linha in f.read_text().splitlines():
            r = json.loads(linha)
            if "id" in r:
                out[r["id"]] = r
    bibjuri = REPO / "municipais/_indice/bibjuri-campinas"
    for nome, rotulo in (("sem-cartao.json", "bibjuri sem cartão"), ("retidos.json", "bibjuri retido")):
        caminho = bibjuri / nome
        if caminho.exists():
            for chave, r in json.loads(caminho.read_text()).items():
                out[int(chave)] = {"id": int(chave), "erro": f"{rotulo}: {r.get('motivo', '')}"}
    return out


# tipos da API do SAPL de Campinas (tiponormajuridica), pela sigla usada nos índices parciais do pipeline
SIGLA_TIPO = {"LEI": 1, "LC": 2, "DEC": 4, "DL": 7, "RES": 8, "ELO": 9, "DEL": 17, "L48": 18, "D48": 19, "R48": 20, "LO": 21}


def normas_do_ano(siglas, ano):
    """Fichas do ano: índice parcial do pipeline SAPL ou, para os lotes do bibjuri, as páginas da API em cache
    (mesma URL e mesmo nome que baixar_bibjuri_campinas.py e cobertura.py gravam). Sem rede."""
    nome = f"indice-legislacao-parcial-{'-'.join(sorted(siglas))}-{ano}.json"
    if (CACHE / nome).exists():
        return json.loads((CACHE / nome).read_text())["normas"]
    normas = []
    for sigla in siglas:
        page = 1
        while True:
            url = f"https://{HOST}/api/norma/normajuridica/?tipo={SIGLA_TIPO[sigla]}&page_size=100&page={page}&ano={ano}"
            pagina = CACHE / (hashlib.sha256(url.encode()).hexdigest() + ".json")
            if not pagina.exists():
                raise SystemExit(f"{ano} {sigla}: sem índice parcial nem páginas da API em cache; rode cobertura.py ou o coletor antes")
            dados = json.loads(pagina.read_bytes())
            normas += dados["results"]
            if not dados["pagination"].get("next_page"):
                break
            page += 1
    return normas


def verificar(siglas, anos):
    por_id = collections.defaultdict(list)
    for p in todos_md():
        meta, _, _ = ler_md(p)
        por_id[id_sapl(meta)].append((p, meta))
    dup = {k: v for k, v in por_id.items() if len(v) > 1}
    equiv = json.loads((CACHE / "equivalencias.json").read_text()) if (CACHE / "equivalencias.json").exists() else {}
    falhas = ultima_falha()
    total = {"indice": 0, "md": 0, "equivalentes": 0, "sem_md": 0, "divergencias": 0}
    sem_md = []
    for ano in anos:
        normas = normas_do_ano(siglas, ano)
        ids = [n["id"] for n in normas]
        if len(ids) != len(set(ids)):
            print(ano, "ÍNDICE COM IDS REPETIDOS")
        n_md = n_eq = 0
        for n in normas:
            total["indice"] += 1
            achados = por_id.get(n["id"], [])
            if not achados:
                if str(n["id"]) in equiv:
                    n_eq += 1
                    total["equivalentes"] += 1
                    continue
                total["sem_md"] += 1
                f = falhas.get(n["id"], {}).get("erro", "(sem registro de falha)")
                sem_md.append((ano, n["id"], n["numero"], n["data"], f))
                continue
            n_md += 1
            total["md"] += 1
            p, meta = achados[0]
            erros = []
            if meta["numero"] != str(n["numero"]):
                erros.append(f"numero {meta['numero']} != {n['numero']}")
            if meta["data"] != (n.get("data") or ""):
                erros.append(f"data {meta['data']} != {n.get('data')}")
            pasta_ano = p.parent.name
            if pasta_ano != (meta["data"][:4] if meta["data"] else str(n["ano"])):
                erros.append(f"pasta {pasta_ano} != ano da data {meta['data']}")
            if str(n["ano"]) != pasta_ano:
                erros.append(f"ano do cadastro {n['ano']} != pasta {pasta_ano}")
            from baixar_organicas_sapl import texto_de_outra_norma
            troca = texto_de_outra_norma(HOST, n["id"])
            esperado = troca["texto_integral"] if troca else (n.get("texto_integral") or "")
            if not fonte_texto_coerente(meta["fonte_texto"], esperado):
                erros.append("fonte_texto difere do texto_integral do cadastro"
                             + ("" if esperado else " (ficha sem anexo: só página do bibjuri vale)"))
            if meta["codigo_ibge"] != "3509502" or meta["municipio"] != "Campinas" or meta["uf"] != "SP":
                erros.append("identidade municipal")
            if not p.name.endswith(f"-sapl-{n['id']}.md"):
                erros.append(f"nome {p.name}")
            if erros:
                total["divergencias"] += 1
                print("DIVERGÊNCIA", ano, n["id"], p.relative_to(REPO), "; ".join(erros))
        print(f"{ano}: índice {len(normas)}, com md {n_md}, equivalentes {n_eq}, sem md {len(normas) - n_md - n_eq}")
    print("TOTAL", json.dumps(total))
    print("ids com mais de um md em Campinas:", len(dup))
    for k, v in list(dup.items())[:20]:
        print("  DUPLICADO", k, [str(p.relative_to(REPO)) for p, _ in v])
    print("--- sem md (retidas ou falhas):")
    for linha in sem_md:
        print("  ", *linha[:4], "|", linha[4][:300])
    return total


PADROES = [
    ("cabecalho_folha", re.compile(r"CÂMARA MUNICIPAL DE CAMPINAS\s*\d+\s*/")),
    ("camara_maiusc_paragrafo", re.compile(r"(?m)^CÂMARA MUNICIPAL DE CAMPINAS\s*$")),
    ("biblioteca", re.compile(r"Diretoria de Gestão Documental|Coordenadoria de Biblioteca|cbib@campinas")),
    ("endereco", re.compile(r"Avenida da Saudade, n")),
    ("aviso_consulta", re.compile(r"Texto (?:somente )?para consulta")),
    ("sem_valor_legal", re.compile(r"sem valor legal", re.I)),
    ("dom_cabecalho", re.compile(r"(?m)^(?:\d+ )?Diário Oficial do Município de Campinas(?: \d+)?\s*$")),
    ("largura_zero", re.compile("​")),
    ("cr", re.compile("\r")),
    ("pagina_n_de_m", re.compile(r"(?mi)^\s*(?:p[áa]g(?:ina)?\.?\s*)?\d+\s*(?:de|/)\s*\d+\s*$")),
]


def carimbos(arquivos, min_freq):
    contagem = collections.Counter()
    exemplos = collections.defaultdict(list)
    freq_par = collections.Counter()
    ex_par = {}
    for p in arquivos:
        _, corpo, _ = ler_md(p)
        for nome, rx in PADROES:
            m = rx.search(corpo)
            if m:
                contagem[nome] += 1
                if len(exemplos[nome]) < 5:
                    ini = max(0, m.start() - 60)
                    exemplos[nome].append((str(p.relative_to(REPO)), corpo[ini:m.end() + 60].replace("\n", "⏎")))
        vistos = set()
        for par in corpo.split("\n\n"):
            chave = re.sub(r"\d+", "#", re.sub(r"\s+", " ", par).strip())
            if 8 <= len(chave) <= 400 and chave not in vistos:
                vistos.add(chave)
                freq_par[chave] += 1
                ex_par.setdefault(chave, str(p.relative_to(REPO)))
    print("arquivos:", len(arquivos))
    for nome, _ in PADROES:
        print(f"{nome}: {contagem[nome]}")
        for ex in exemplos[nome]:
            print("    ", ex[0], "::", ex[1][:220])
    print(f"--- parágrafos repetidos em >= {min_freq} arquivos (candidatos a carimbo):")
    for chave, n in freq_par.most_common():
        if n < min_freq:
            break
        print(f"{n:5d}  {chave[:200]}   [{ex_par[chave]}]")


# nota que o pipeline grava em versao_texto quando recorta o ato de uma página de livro de leis (Campinas, até 1948)
NOTA_RECORTE = "ato recortado da página do livro de leis anexada no SAPL"
FONTE_BIBJURI = REPO / "municipais/_fonte/bibjuri-campinas"


def pos_processar(corpo, meta):
    """Pós-processamento do pipeline SAPL para Campinas, na mesma ordem: carimbos da biblioteca da Câmara e, quando o
    .md anota o recorte, o ato próprio da página de livro de leis (recortar_ato_de_livro, que pode levantar RuntimeError)."""
    from baixar_organicas_sapl import limpar_carimbo_campinas, recortar_ato_de_livro
    corpo, _notas = limpar_carimbo_campinas(corpo)
    if NOTA_RECORTE in (meta.get("versao_texto") or ""):
        corpo, _data_fecho = recortar_ato_de_livro(corpo, meta["tipo_na_fonte"], meta["numero"], meta.get("data") or "")
    return corpo


def corpo_regenerado(meta, bruto):
    """Corpo do .md refeito a partir da fonte em cache com o código atual. Devolve (corpo, motivo)."""
    from baixar_organicas_sapl import corpo_de_fonte
    if "bibjuri.campinas.sp.gov.br" in meta["fonte_texto"]:
        import baixar_bibjuri_campinas as bibjuri
        from comum import decodificar
        info = next(i for i in bibjuri.TIPOS.values() if i["tipo"] == meta["tipo"])
        bloco = bibjuri.bloco_conteudo(decodificar(bruto, "text/html; charset=iso-8859-1"))
        motivo, corpo, _publicacao, _notas, _pdf = bibjuri.avaliar(bloco, {"numero": meta["numero"], "data": meta["data"]}, info)
        return corpo, motivo
    corpo, motivo = corpo_de_fonte(bruto, meta["fonte_texto"])
    if motivo:
        return None, motivo
    try:
        return pos_processar(corpo, meta), None
    except RuntimeError as e:
        return None, str(e)


def fonte_em_cache(meta):
    """Arquivo bruto da fonte: .bin do pipeline SAPL ou a página HTML do bibjuri (original ou consolidada)."""
    if "bibjuri.campinas.sp.gov.br" in meta["fonte_texto"]:
        ident = meta["fonte_texto"].rsplit("/", 1)[1]
        return FONTE_BIBJURI / (f"{ident}.html" if "visualizaroriginal" in meta["fonte_texto"] else f"{ident}-consolidado.html")
    return FONTE / f"{id_sapl(meta)}.bin"


def regenerar(arquivos, mostrar):
    iguais = sem_cache = 0
    lista_difs = []
    for i, p in enumerate(arquivos):
        meta, corpo_md, _ = ler_md(p)
        fonte = fonte_em_cache(meta)
        if not fonte.exists():
            sem_cache += 1
            print("SEM CACHE", p.relative_to(REPO))
            continue
        b = fonte.read_bytes()
        if hashlib.sha256(b).hexdigest() != meta["sha256_fonte"]:
            print("FONTE MUDOU", p.relative_to(REPO))
        corpo, motivo = corpo_regenerado(meta, b)
        if motivo:
            lista_difs.append((p, "motivo: " + motivo))
            continue
        if hashlib.sha256(corpo.encode()).hexdigest() == meta["sha256_texto"] and corpo == corpo_md:
            iguais += 1
        else:
            lista_difs.append((p, corpo))
        if (i + 1) % 500 == 0:
            print("...", i + 1, flush=True)
    print(f"iguais {iguais}, diferentes {len(lista_difs)}, sem cache {sem_cache}")
    for p, novo in lista_difs[:mostrar]:
        _, antigo, _ = ler_md(p)
        print("====", p.relative_to(REPO))
        if novo.startswith("motivo: "):
            print(novo)
            continue
        for linha in list(difflib.unified_diff(antigo.split("\n"), novo.split("\n"), lineterm="", n=1))[:40]:
            print(linha[:240])
    return len(lista_difs)


def arquivos_de(a):
    if a.pasta:
        return sorted(p.resolve() for pasta in a.pasta for p in Path(pasta).resolve().glob("**/*.md"))
    return [Path(x).resolve() for x in a.arquivos]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("verificar")
    v.add_argument("--siglas", default="LEI")
    v.add_argument("--anos", nargs="+", type=int, required=True)
    for nome in ("carimbos", "regenerar"):
        s = sub.add_parser(nome)
        s.add_argument("arquivos", nargs="*")
        s.add_argument("--pasta", nargs="*")
        s.add_argument("--min-freq", type=int, default=5)
        s.add_argument("--mostrar", type=int, default=15)
    a = ap.parse_args()
    if a.cmd == "verificar":
        t = verificar(a.siglas.split(","), a.anos)
        raise SystemExit(1 if t["divergencias"] else 0)
    if a.cmd == "carimbos":
        carimbos(arquivos_de(a), a.min_freq)
    if a.cmd == "regenerar":
        raise SystemExit(1 if regenerar(arquivos_de(a), a.mostrar) else 0)
