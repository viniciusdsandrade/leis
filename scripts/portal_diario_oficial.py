"""Diário Oficial no portal das Prefeituras de Paulínia, Valinhos e Vinhedo (SP), que usam o mesmo sistema.

O portal lista as edições em `/portal/diario-oficial/<página>/<data inicial>/<data final>/<busca>/<edição>/`, da mais
recente para a mais antiga, 50 por página, e as repete nos dados abertos (`/portal/dados-abertos/diario-oficial/<ano>`).
O PDF de cada edição sai de `/portal/download/diario-oficial/<código>/`, que redireciona para `/uploads/<arquivo>.pdf`.

O `robots.txt` dos três portais, conferido em novembro de 2026, libera a listagem e os dados abertos, mas veda
`/portal/download/` e `/uploads/`, os caminhos dos PDFs. Sem autorização, só se leem as edições já em cache. A opção
`--apesar-do-robots` baixa mesmo assim, apenas nos municípios e anos que o mantenedor do acervo autorizou
expressamente (`AUTORIZACOES`): Paulínia, só as edições de 2012 (17/11/2026); Valinhos e Vinhedo, todas as edições
(18/11/2026, autorização confirmada em 19/11/2026). Com ela, o ritmo fica em no máximo uma requisição a cada cinco
segundos. A autorização não vale para nenhum outro município.

Este módulo só lista e guarda as edições: o PDF em `municipais/_fonte/dom-<município>/<id>-<arquivo>.pdf` e o índice em
`municipais/_indice/dom-<município>/edicoes.json`. A leitura dos atos fica no coletor de cada município.

    python3 -I scripts/portal_diario_oficial.py --municipio valinhos --de 2006 --ate 2026 [--listar] [--apesar-do-robots]
"""
import argparse
import html
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import Rede, slugify  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent / "municipais"
RPS_APESAR_DO_ROBOTS = 0.2  # com o download vedado pelo robots.txt, no máximo uma requisição a cada cinco segundos
CAMINHOS = ["/portal/diario-oficial/", "/portal/dados-abertos/", "/portal/download/", "/uploads/"]


@dataclass(frozen=True)
class Municipio:
    chave: str
    nome: str
    codigo_ibge: str
    base: str

    @property
    def fonte(self):
        """Pasta dos PDFs baixados (fora do versionamento)."""
        return RAIZ / "_fonte" / f"dom-{self.chave}"

    @property
    def cache(self):
        """Pasta do índice das edições e dos logs (fora do versionamento)."""
        return RAIZ / "_indice" / f"dom-{self.chave}"


MUNICIPIOS = {m.chave: m for m in (
    Municipio("paulinia", "Paulínia", "3536505", "https://www.paulinia.sp.gov.br"),
    Municipio("valinhos", "Valinhos", "3556206", "https://www.valinhos.sp.gov.br"),
    Municipio("vinhedo", "Vinhedo", "3556701", "https://www.vinhedo.sp.gov.br"),
)}
# autorizações expressas do mantenedor do acervo para baixar os PDFs apesar do robots.txt: (quando, primeiro ano, último
# ano); sem ano, valem para todas as edições do município
AUTORIZACOES = {"paulinia": ("17/11/2026", 2012, 2012),
                "valinhos": ("18/11/2026, confirmada em 19/11/2026", None, None),
                "vinhedo": ("18/11/2026, confirmada em 19/11/2026", None, None)}


def sem_autorizacao(chave, de, ate):
    """Motivo da recusa em baixar apesar do robots.txt; None quando a autorização cobre o município e os anos pedidos."""
    if chave not in AUTORIZACOES:
        return f"não há autorização para baixar os PDFs de {chave} apesar do robots.txt"
    quando, primeiro, ultimo = AUTORIZACOES[chave]
    if (primeiro and de < primeiro) or (ultimo and ate > ultimo):
        return f"a autorização de {quando} para {chave} vale só para as edições de {primeiro} a {ultimo}"
    return None


ITEM = '<div class="dof_publicacao_diario sw_item_listagem">'


def texto_html(bruto):
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", bruto)).split())


def edicoes_da_pagina(pagina_html):
    """[{id, edicao, data, token}] das edições de uma página da listagem do portal; `data` é None quando falta."""
    saida = []
    for bloco in pagina_html.split(ITEM)[1:]:
        ver = re.search(r"/portal/diario-oficial/ver/(\d+)", bloco)
        token = re.search(r"/portal/download/diario-oficial/([^/\"'\s]+)", bloco)  # o código pode ter hífen
        rotulo = texto_html(bloco)
        numero = re.search(r"Edi[çc][ãa]o n[º°o]\s*([\d.]+)", rotulo)
        postagem = re.search(r"Postagem:\s*(\d{2})/(\d{2})/(\d{4})", rotulo)
        if not (ver and token and numero):
            continue
        data = f"{postagem.group(3)}-{postagem.group(2)}-{postagem.group(1)}" if postagem else None
        saida.append({"id": ver.group(1), "edicao": numero.group(1).replace(".", ""), "data": data, "token": token.group(1)})
    return saida


def listar_edicoes(rede, base, de, ate):
    """Edições postadas entre os anos `de` e `ate`, da mais antiga para a mais recente. A listagem vem da mais recente
    para a mais antiga: a leitura para na primeira página toda anterior a `de` ou na primeira sem edição nova (depois
    da última, o portal repete páginas já vistas)."""
    achadas, vistos = [], set()
    for pagina in range(1, 400):
        st, bruto, _ = rede.get(f"{base}/portal/diario-oficial/{pagina}/0/0/0/0")
        if st != 200:
            raise RuntimeError(f"listagem de edições, página {pagina}: HTTP {st}")
        itens = [e for e in edicoes_da_pagina(bruto.decode("utf-8", "replace")) if e["id"] not in vistos]
        if not itens:
            break
        vistos.update(e["id"] for e in itens)
        achadas += itens
        anos = [int(e["data"][:4]) for e in itens if e["data"]]
        if anos and max(anos) < de:
            break
    sem_data = [e["edicao"] for e in achadas if not e["data"]]
    if sem_data:
        print(f"[aviso] edições sem data de postagem na listagem, fora da coleta: {', '.join(sem_data)}", flush=True)
    return sorted((e for e in achadas if e["data"] and de <= int(e["data"][:4]) <= ate),
                  key=lambda e: (e["data"], int(e["edicao"]), int(e["id"])))


def edicoes_dos_dados_abertos(rede, base, ano):
    """Números das edições do ano segundo os dados abertos do portal: confere a listagem. Ano sem edição vem como
    `[["Nenhum registro encontrado."]]`, que conta como vazio."""
    st, bruto, _ = rede.get(f"{base}/portal/dados-abertos/diario-oficial/{ano}", "application/json")
    if st != 200:
        raise RuntimeError(f"dados abertos de {ano}: HTTP {st}")
    return {str(e["edicao"]).replace(".", "") for e in json.loads(bruto)["dados"] if isinstance(e, dict)}


def resumo(numeros, limite=20):
    """Lista de números de edição para o log, cortada em `limite` itens."""
    numeros = sorted(numeros, key=lambda n: (len(n), n))
    return ", ".join(numeros[:limite]) + (f" e mais {len(numeros) - limite}" if len(numeros) > limite else "")


def vedados_pelo_robots(robots, caminhos, agente="*"):
    """Os `caminhos` que o `robots.txt` veda ao `agente`: somados todos os grupos que o nomeiam (RFC 9309, seção 2.2.1),
    vale a regra de caminho mais longo, e Allow vence Disallow no empate."""
    regras, grupo, nomes, em_regras = [], False, [], False
    for linha in robots.splitlines():
        linha = linha.split("#", 1)[0].strip()
        if ":" not in linha:
            continue
        campo, valor = (x.strip() for x in linha.split(":", 1))
        campo = campo.lower()
        if campo == "user-agent":
            if em_regras:
                nomes, em_regras = [], False
            nomes.append(valor.lower())
            grupo = agente.lower() in nomes
        elif campo in ("allow", "disallow"):
            em_regras = True
            if grupo and valor:
                regras.append((len(valor), campo == "allow", valor))
    vedados = []
    for caminho in caminhos:
        casadas = sorted((r for r in regras if caminho.startswith(r[2])), key=lambda r: (r[0], r[1]))
        if casadas and not casadas[-1][1]:
            vedados.append(caminho)
    return vedados


def conferir_robots(rede, municipio, apesar_do_robots, de, ate, rps):
    """Lê o `robots.txt` do portal a cada execução e devolve True quando só o cache pode ser lido. Levanta erro se a
    listagem estiver vedada ou se `apesar_do_robots` pedir o que a autorização não cobre."""
    st, robots, _ = rede.get(f"{municipio.base}/robots.txt")
    vedados = vedados_pelo_robots(robots.decode("utf-8", "replace"), CAMINHOS) if st == 200 else []
    if {"/portal/diario-oficial/", "/portal/dados-abertos/"} & set(vedados):
        raise RuntimeError(f"o robots.txt do portal veda a listagem das edições: {vedados}")
    if vedados and apesar_do_robots:
        motivo = sem_autorizacao(municipio.chave, de, ate)
        if motivo:
            raise RuntimeError(motivo)
        print(f"[aviso] o robots.txt veda {', '.join(vedados)}; baixando mesmo assim (--apesar-do-robots, autorização de "
              f"{AUTORIZACOES[municipio.chave][0]}), a {rps} req/s", flush=True)
    elif vedados:
        print(f"[aviso] o robots.txt veda {', '.join(vedados)}: só as edições já em cache serão lidas", flush=True)
    return bool(vedados) and not apesar_do_robots


def baixar_pdf(rede, base, fonte, edicao, so_cache=False):
    """(endereço do PDF, arquivo em cache). O link de download responde com um redirecionamento em HTML para /uploads.
    Com `so_cache`, a edição fora do cache é um erro, sem nenhum pedido à rede."""
    fonte.mkdir(parents=True, exist_ok=True)
    em_cache = sorted(fonte.glob(f"{edicao['id']}-*.pdf"))
    if em_cache and edicao.get("pdf"):
        return edicao["pdf"], em_cache[0]
    if so_cache:
        raise RuntimeError("PDF fora do cache; o robots.txt do portal veda o download (/portal/download/, /uploads/)")
    url = f"{base}/portal/download/diario-oficial/{edicao['token']}/"
    st, bruto, _ = rede.get(url)
    if st != 200:
        raise RuntimeError(f"download HTTP {st}")
    if not bruto.startswith(b"%PDF"):
        alvo = re.search(rb"url=([^\"'> ]+\.pdf)", bruto, re.I)
        if not alvo:
            raise RuntimeError("página de download sem o endereço do PDF")
        url = base + alvo.group(1).decode("ascii", "replace")
        st, bruto, _ = rede.get(url)
        if st != 200 or not bruto.startswith(b"%PDF"):
            raise RuntimeError(f"PDF da edição: HTTP {st} ou arquivo que não é PDF")
    destino = fonte / f"{edicao['id']}-{slugify(url.rsplit('/', 1)[1])}"
    tmp = destino.with_suffix(".tmp")
    tmp.write_bytes(bruto)
    tmp.replace(destino)
    return url, destino


def ler_indice(municipio):
    arquivo = municipio.cache / "edicoes.json"
    return json.loads(arquivo.read_text(encoding="utf-8")) if arquivo.exists() else {}


def gravar_indice(municipio, novos):
    """Acrescenta ao índice em disco as edições `novos` ({id: {edicao, data, pdf}}). Relê o arquivo antes de gravar: o
    download e a leitura do mesmo município podem rodar juntos, e gravar o índice inteiro de memória apagaria o que o
    outro processo acrescentou nesse meio-tempo."""
    if not novos:
        return
    municipio.cache.mkdir(parents=True, exist_ok=True)
    arquivo = municipio.cache / "edicoes.json"
    indice = {**ler_indice(municipio), **novos}
    tmp = arquivo.with_suffix(f".{os.getpid()}.tmp")
    tmp.write_text(json.dumps(indice, ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.replace(arquivo)


def conferir_dados_abertos(rede, municipio, edicoes, de, ate):
    """Imprime, ano a ano, a contagem da listagem contra a dos dados abertos e o que só um dos dois traz."""
    for ano in range(de, ate + 1):
        na_listagem = {e["edicao"] for e in edicoes if e["data"][:4] == str(ano)}
        abertos = edicoes_dos_dados_abertos(rede, municipio.base, ano)
        print(f"{ano}: {len(na_listagem)} edições na listagem, {len(abertos)} nos dados abertos"
              + (f"; só nos dados abertos: {resumo(abertos - na_listagem)}" if abertos - na_listagem else "")
              + (f"; só na listagem: {resumo(na_listagem - abertos)}" if na_listagem - abertos else ""), flush=True)


def baixar_edicoes(chave, de, ate, apesar_do_robots=False, rps=0.5, listar=False):
    """Lista as edições de `de` a `ate` e guarda o PDF de cada uma, sem ler os atos, da mais recente para a mais antiga
    (a ordem não muda o resultado, e as recentes ficam prontas antes). Retomável: o que está no cache e no índice não é
    pedido de novo. Devolve a contagem."""
    municipio = MUNICIPIOS[chave]
    if apesar_do_robots:
        rps = min(rps, RPS_APESAR_DO_ROBOTS)
    rede = Rede(rps=rps, headers={"Accept-Language": "pt-BR"})
    so_cache = conferir_robots(rede, municipio, apesar_do_robots, de, ate, rps)
    edicoes = listar_edicoes(rede, municipio.base, de, ate)
    conferir_dados_abertos(rede, municipio, edicoes, de, ate)
    contagem = {"edicoes": len(edicoes), "baixadas": 0, "em_cache": 0, "erro": 0}
    if listar:
        return contagem
    indice = ler_indice(municipio)
    for n, edicao in enumerate(reversed(edicoes), 1):
        edicao["pdf"] = (indice.get(edicao["id"]) or {}).get("pdf")
        ja = bool(edicao["pdf"]) and any(municipio.fonte.glob(f"{edicao['id']}-*.pdf"))
        try:
            edicao["pdf"], _ = baixar_pdf(rede, municipio.base, municipio.fonte, edicao, so_cache)
        except Exception as e:  # rede ou arquivo inesperado: registra e segue para a próxima edição
            contagem["erro"] += 1
            print(f"[erro] edição {edicao['edicao']} ({edicao['data']}, id {edicao['id']}): {e}", flush=True)
            continue
        contagem["em_cache" if ja else "baixadas"] += 1
        if not ja:
            gravar_indice(municipio, {edicao["id"]: {"edicao": edicao["edicao"], "data": edicao["data"], "pdf": edicao["pdf"]}})
        if n % 50 == 0:
            print(f"  ... {n}/{len(edicoes)}, edição {edicao['edicao']} ({edicao['data']}): {contagem}", flush=True)
    print(json.dumps(contagem, ensure_ascii=False), flush=True)
    return contagem


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--municipio", required=True, choices=sorted(MUNICIPIOS))
    ap.add_argument("--de", type=int, required=True, help="primeiro ano")
    ap.add_argument("--ate", type=int, required=True, help="último ano, inclusive")
    ap.add_argument("--listar", action="store_true", help="só confere a listagem contra os dados abertos; não baixa PDFs")
    ap.add_argument("--rps", type=float, default=0.5, help="requisições por segundo")
    ap.add_argument("--apesar-do-robots", action="store_true",
                    help="baixa os PDFs mesmo com o robots.txt vedando o download; só onde há autorização (AUTORIZACOES)")
    a = ap.parse_args()
    baixar_edicoes(a.municipio, a.de, a.ate, a.apesar_do_robots, a.rps, a.listar)
