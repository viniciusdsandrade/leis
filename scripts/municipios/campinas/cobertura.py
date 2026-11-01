"""Mede, por ano, quantas normas de um tipo do SAPL de Campinas têm texto integral. Só lista o índice.

Grava as páginas da API no cache de baixar_organicas_sapl.py (mesma URL, mesma trava por host).
uso: cobertura.py ANO_INI ANO_FIM TIPO_ID SAIDA.json
"""
import hashlib
import json
import sys
from pathlib import Path
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # scripts/
import baixar_organicas_sapl as b

HOST = "sapl.campinas.sp.leg.br"
ini, fim, tipo, saida = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
rede = b.rede_host(HOST, 1)
cache = b.RAIZ / "_indice/organicas-sapl" / HOST


def obter(url):
    destino = cache / (hashlib.sha256(url.encode()).hexdigest() + ".json")
    if destino.exists():
        return json.loads(destino.read_bytes())
    st, dados, _ = rede.get(url, tentativas=3)
    if st != 200:
        raise RuntimeError(f"HTTP {st}: {url}")
    b.escrever(destino, dados)
    return json.loads(dados)


por_ano = {}
for ano in range(fim, ini - 1, -1):
    page, normas = 1, []
    while True:
        d = obter(f"https://{HOST}/api/norma/normajuridica/?tipo={tipo}&page_size=100&page={page}&ano={ano}")
        normas += d["results"]
        if not d["pagination"].get("next_page"):
            break
        page += 1
    if not normas:
        continue
    com = [n for n in normas if n.get("texto_integral")]
    hosts = {}
    for n in com:
        h = urlsplit(n["texto_integral"]).hostname
        hosts[h] = hosts.get(h, 0) + 1
    por_ano[ano] = {"total": len(normas), "oficial": d["pagination"]["total_entries"], "com_texto": len(com),
                    "hosts": hosts, "ids_com_texto": [n["id"] for n in com]}
    print(f"{ano}: {len(normas)} normas, {len(com)} com texto integral ({100 * len(com) / len(normas):.0f}%)", flush=True)
    with open(saida, "w") as f:
        json.dump(por_ano, f, ensure_ascii=False, indent=1)
print("FIM", sum(v["total"] for v in por_ano.values()), "normas,", sum(v["com_texto"] for v in por_ano.values()), "com texto")
