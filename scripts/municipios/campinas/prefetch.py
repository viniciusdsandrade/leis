"""Pré-baixa índice e PDFs de leis de Campinas por ano, nos caminhos de cache de baixar_organicas_sapl.py.
Não gera Markdown. uso: prefetch.py ANO_INI ANO_FIM [TIPO_ID]"""
import hashlib
import json
import sys
from pathlib import Path
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # scripts/
import baixar_organicas_sapl as b

HOST = "sapl.campinas.sp.leg.br"
ini, fim = int(sys.argv[1]), int(sys.argv[2])
tipo = int(sys.argv[3]) if len(sys.argv) > 3 else 1
rede = b.rede_host(HOST, 1)  # mesma trava por host do pipeline
cache = b.RAIZ / "_indice/organicas-sapl" / HOST


def obter(url, destino, tentativas=3):
    if destino.exists():
        return destino.read_bytes(), False
    st, dados, _ = rede.get(url, tentativas=tentativas)
    if st != 200:
        raise RuntimeError(f"HTTP {st}: {url}")
    b.escrever(destino, dados)
    return dados, True


for ano in range(fim, ini - 1, -1):
    page, normas = 1, []
    while True:
        url = f"https://{HOST}/api/norma/normajuridica/?tipo={tipo}&page_size=100&page={page}&ano={ano}"
        d = json.loads(obter(url, cache / (hashlib.sha256(url.encode()).hexdigest() + ".json"))[0])
        normas += d["results"]
        if not d["pagination"].get("next_page"):
            break
        page += 1
    baixados = ja = sem_texto = erros = 0
    for n in normas:
        url = n.get("texto_integral")
        if not url:
            sem_texto += 1
            continue
        if urlsplit(url).hostname == HOST:
            url = "https://" + url.split("://", 1)[1]
        try:
            _, novo = obter(url, b.RAIZ / "_fonte/organicas-sapl" / HOST / f"{n['id']}.bin")
            baixados += novo
            ja += not novo
        except Exception as e:
            erros += 1
            print(ano, n["id"], "ERRO", str(e)[:200], flush=True)
    print(f"{ano}: índice {len(normas)} (oficial {d['pagination']['total_entries']}), baixados {baixados}, "
          f"já em cache {ja}, sem texto {sem_texto}, erros {erros}", flush=True)
print("FIM")
