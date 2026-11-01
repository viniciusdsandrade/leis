"""Simula a conversão de um ano de leis de Campinas a partir do cache, sem gravar nada.
uso: simular_ano.py ANO [ANO...] [--tipo 1] [--min-freq 4] [--json J]"""
import argparse
import collections
import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # scripts/
sys.path.insert(0, str(Path(__file__).resolve().parent))
from baixar_organicas_sapl import (RAIZ, corpo_de_fonte, corpo_integral_reconhecivel, data_diverge_do_ano,  # noqa: E402
                                   limpar_carimbo_campinas)
from granularidade_sapl import alertas_multiplos_atos, alertas_outras_publicacoes  # noqa: E402
from campinas import PADROES  # noqa: E402

HOST = "sapl.campinas.sp.leg.br"
CACHE = RAIZ / "_indice/organicas-sapl" / HOST


def normas_do_ano(ano, tipo):
    page, out = 1, []
    while True:
        url = f"https://{HOST}/api/norma/normajuridica/?tipo={tipo}&page_size=100&page={page}&ano={ano}"
        f = CACHE / (hashlib.sha256(url.encode()).hexdigest() + ".json")
        if not f.exists():
            return None
        d = json.loads(f.read_text())
        out += d["results"]
        if not d["pagination"].get("next_page"):
            return out
        page += 1


ap = argparse.ArgumentParser()
ap.add_argument("anos", nargs="+", type=int)
ap.add_argument("--tipo", type=int, default=1)
ap.add_argument("--descricao", default="Lei", help="descrição do tipo para a trava de epígrafe")
ap.add_argument("--min-freq", type=int, default=4)
ap.add_argument("--json")
a = ap.parse_args()
resumo, retidas = collections.Counter(), []
padroes, exemplos = collections.Counter(), collections.defaultdict(list)
freq, ex_par = collections.Counter(), {}
for ano in a.anos:
    normas = normas_do_ano(ano, a.tipo)
    if normas is None:
        print(ano, "índice fora do cache")
        continue
    for n in normas:
        url = n.get("texto_integral")
        if not url:
            resumo["sem texto integral"] += 1
            retidas.append((ano, n["id"], n["numero"], "norma sem texto integral"))
            continue
        if urlsplit(url).hostname == HOST:
            url = "https://" + url.split("://", 1)[1]
        fonte = RAIZ / "_fonte/organicas-sapl" / HOST / f"{n['id']}.bin"
        if not fonte.exists():
            resumo["pdf fora do cache"] += 1
            continue
        if data_diverge_do_ano(n):
            resumo["retida: data diverge do ano"] += 1
            retidas.append((ano, n["id"], n["numero"], f"data {n.get('data')} de outro ano"))
            continue
        corpo, motivo = corpo_de_fonte(fonte.read_bytes(), url)
        if motivo:
            resumo["falha de conversão"] += 1
            retidas.append((ano, n["id"], n["numero"], motivo))
            continue
        corpo, notas = limpar_carimbo_campinas(corpo)
        outras = alertas_outras_publicacoes(corpo)
        gran = alertas_multiplos_atos(corpo, a.descricao, n["numero"])
        if outras or gran:
            resumo["retida: granularidade/outra publicação"] += 1
            retidas.append((ano, n["id"], n["numero"], json.dumps(outras or gran, ensure_ascii=False)[:300]))
            continue
        if not corpo_integral_reconhecivel(corpo, "emenda" in a.descricao.lower()):
            resumo["retida: sem artigo inicial"] += 1
            retidas.append((ano, n["id"], n["numero"], "sem artigo inicial: " + corpo[:200].replace("\n", "⏎")))
            continue
        resumo["ok"] += 1
        for nome, rx in PADROES:
            m = rx.search(corpo)
            if m:
                padroes[nome] += 1
                if len(exemplos[nome]) < 4:
                    exemplos[nome].append((n["id"], corpo[max(0, m.start() - 50):m.end() + 60].replace("\n", "⏎")))
        vistos = set()
        for par in corpo.split("\n\n"):
            chave = re.sub(r"\d+", "#", re.sub(r"\s+", " ", par).strip())
            if 8 <= len(chave) <= 400 and chave not in vistos:
                vistos.add(chave)
                freq[chave] += 1
                ex_par.setdefault(chave, n["id"])
print("resumo:", dict(resumo))
for r in retidas:
    print("  RETIDA", *r[:3], "|", r[3][:260])
for nome, _ in PADROES:
    if padroes[nome]:
        print(f"  {nome}: {padroes[nome]}", *[f"\n      {i} :: {t[:200]}" for i, t in exemplos[nome]])
print(f"--- parágrafos repetidos em >= {a.min_freq} leis:")
for chave, k in freq.most_common():
    if k < a.min_freq:
        break
    print(f"  {k:4d}  {chave[:170]}  [{ex_par[chave]}]")
if a.json:
    Path(a.json).write_text(json.dumps({"resumo": resumo, "retidas": retidas}, ensure_ascii=False, indent=1))
