"""Refaz o corpo dos .md de Campinas a partir do PDF em cache com o código atual e compara com o gravado.

Usa o mesmo caminho do pipeline (corpo_de_fonte + limpar_carimbo_campinas). Rede não é usada.
uso: python3 campinas_regenerar.py [--mostrar N]
"""
import argparse
import difflib
import hashlib
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]  # raiz do repositório
sys.path.insert(0, str(REPO / "scripts"))
from baixar_organicas_sapl import corpo_de_fonte, limpar_carimbo_campinas, texto_de_outra_norma  # noqa: E402

FONTE = REPO / "municipais/_fonte/organicas-sapl/sapl.campinas.sp.leg.br"


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
    return meta, corpo


ap = argparse.ArgumentParser()
ap.add_argument("--mostrar", type=int, default=10)
a = ap.parse_args()
arquivos = sorted((REPO / "municipais/SP/campinas").glob("**/*.md"))
iguais = sem_cache = 0
difs = []
for i, p in enumerate(arquivos):
    meta, corpo_md = ler_md(p)
    ident = meta["fonte"].rsplit("/", 1)[1]
    troca = texto_de_outra_norma("sapl.campinas.sp.leg.br", ident)
    fonte = FONTE / (str(troca["id_fonte"] if troca else ident) + ".bin")
    if not fonte.exists():
        sem_cache += 1
        print("SEM CACHE", p.relative_to(REPO), flush=True)
        continue
    b = fonte.read_bytes()
    if hashlib.sha256(b).hexdigest() != meta["sha256_fonte"]:
        print("FONTE MUDOU", p.relative_to(REPO), flush=True)
    corpo, motivo = corpo_de_fonte(b, meta["fonte_texto"])
    if motivo:
        difs.append((p, "motivo: " + motivo))
        continue
    corpo, _notas = limpar_carimbo_campinas(corpo)
    if corpo == corpo_md and hashlib.sha256(corpo.encode()).hexdigest() == meta["sha256_texto"]:
        iguais += 1
    else:
        difs.append((p, corpo))
    if (i + 1) % 500 == 0:
        print("...", i + 1, "iguais", iguais, "diferentes", len(difs), flush=True)
print(f"arquivos {len(arquivos)}: iguais {iguais}, diferentes {len(difs)}, sem cache {sem_cache}", flush=True)
for p, novo in difs[:a.mostrar]:
    _, antigo = ler_md(p)
    print("====", p.relative_to(REPO))
    if novo.startswith("motivo: "):
        print(novo)
        continue
    for linha in list(difflib.unified_diff(antigo.split("\n"), novo.split("\n"), lineterm="", n=1))[:30]:
        print(linha[:240])
