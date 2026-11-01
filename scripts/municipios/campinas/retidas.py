"""Lista as normas de Campinas sem .md nos índices parciais do pipeline e classifica o motivo.

Sem rede. Saída: JSON com uma linha por norma retida e um resumo por motivo.
uso: retidas.py <saida.json>
"""
import collections
import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

REPO = Path(__file__).resolve().parents[3]  # raiz do repositório
sys.path.insert(0, str(REPO / "scripts"))
from baixar_organicas_sapl import (corpo_de_fonte, corpo_integral_reconhecivel, data_diverge_do_ano,  # noqa: E402
                                   limpar_carimbo_campinas, motivo_retencao)
from granularidade_sapl import EPIGRAFE, alertas_multiplos_atos, alertas_outras_publicacoes, numero_base  # noqa: E402

HOST = "sapl.campinas.sp.leg.br"
CACHE = REPO / "municipais/_indice/organicas-sapl" / HOST
FONTE = REPO / "municipais/_fonte/organicas-sapl" / HOST

ids_md = set()
for p in (REPO / "municipais/SP/campinas").glob("**/*.md"):
    m = re.search(r'^fonte: "https://sapl\.campinas\.sp\.leg\.br/norma/(\d+)"', p.read_text()[:3000], re.M)
    if m:
        ids_md.add(int(m[1]))
equiv = json.loads((CACHE / "equivalencias.json").read_text()) if (CACHE / "equivalencias.json").exists() else {}
normas, tipos = {}, {}
for f in sorted(CACHE.glob("indice-legislacao-parcial-*.json")):
    d = json.loads(f.read_text())
    for t in d["tipos"]:
        tipos[t["id"]] = t
    for n in d["normas"]:
        normas[n["id"]] = n
saida, resumo = [], collections.Counter()
for i, n in sorted(normas.items()):
    if i in ids_md or str(i) in equiv:
        continue
    tipo = tipos[n["tipo"]]
    r = {"id": i, "tipo": tipo["sigla"], "numero": n["numero"], "ano": n["ano"], "data": n.get("data")}
    url = n.get("texto_integral")
    fonte = FONTE / f"{i}.bin"
    if not url:
        r["motivo"] = "sem texto integral"
    elif not fonte.exists():
        r["motivo"] = "pdf fora do cache"
    else:
        b = fonte.read_bytes()
        r["sha256_fonte"] = hashlib.sha256(b).hexdigest()
        if urlsplit(url).hostname == HOST:
            url = "https://" + url.split("://", 1)[1]
        r["texto_integral"] = url
        retido = motivo_retencao(CACHE, i, b)
        if retido:
            r["motivo"] = "registro de retenção: " + retido
        elif data_diverge_do_ano(n):
            r["motivo"] = "data diverge do ano"
        else:
            corpo, motivo = corpo_de_fonte(b, url)
            if motivo:
                r["motivo"] = "conversão: " + motivo
            else:
                corpo, _ = limpar_carimbo_campinas(corpo)
                emenda = "emenda" in tipo["descricao"].lower()
                gran = alertas_multiplos_atos(corpo, tipo["descricao"], n["numero"])
                outras = alertas_outras_publicacoes(corpo)
                # epígrafe que abre o texto: de que lei o PDF realmente é
                cab = corpo.lstrip("> \n")
                cab = re.sub(r"^Texto obtido por OCR[^\n]*\n+", "", cab)
                primeira = next((m for m in EPIGRAFE.finditer(corpo[:600])), None)
                if primeira:
                    r["epigrafe_inicial"] = numero_base(primeira["numero"])
                    r["epigrafe_trecho"] = primeira.group(0)[:80]
                if gran:
                    r["motivo"] = "epígrafe de outra norma"
                    r["outra"] = gran[0]["epigrafe_diversa"]
                    r["posicao"] = gran[0]["posicao_no_corpo"]
                elif outras:
                    r["motivo"] = "outra publicação"
                elif not corpo_integral_reconhecivel(corpo, emenda):
                    r["motivo"] = "sem artigo inicial"
                    r["antigo"] = bool(re.search(r"(?m)^\W*Antigo\s*1\s*[º°o]", corpo))
                    r["inicio"] = corpo[:160].replace("\n", " ")
                else:
                    r["motivo"] = "passa nas travas (verificar)"
    resumo[r["motivo"].split(":")[0]] += 1
    saida.append(r)
Path(sys.argv[1]).write_text(json.dumps(saida, ensure_ascii=False, indent=1))
print(len(saida), "sem .md;", dict(resumo))
print("sem artigo com 'Antigo 1º':", sum(1 for r in saida if r.get("antigo")))
