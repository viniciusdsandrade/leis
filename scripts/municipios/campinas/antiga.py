"""Testa a epígrafe antiga ("LEI N. 287 (", "DECRETO N. 121, de 1946") contra o acervo municipal SAPL. Sem rede."""
import collections
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]  # raiz do repositório
sys.path.insert(0, str(REPO / "scripts"))
from granularidade_sapl import classe, numero_base  # noqa: E402

ANTIGAS = [
    # "LEI N. 287 ( Declara de utilidade publica...)", "Lei N. 259 (Proroga...)"
    re.compile(r"^(?:\s*[*#]+\s*)?(?P<tipo>LEI|RESOLU[ÇC][ÃA]O|DECRETO(?:[- ]LEI)?|ACTO|ATO)\s+N\s*[.º°o]*\s*(?P<numero>\d[\d.]*)\s*\(", re.M | re.I),
    # "LEI N. 439 DETERNINANDO...", "DECRETO N. 121, de 1946": maiúsculas e "N." com ponto, a abreviatura dos livros antigos
    re.compile(r"^(?:\s*[*#]+\s*)?(?P<tipo>LEI|RESOLUÇÃO|DECRETO(?:-LEI)?|ACTO|Lei|Resolução|Decreto(?:-Lei)?)\s+N\.\s*(?P<numero>\d[\d.]*)\b", re.M),
]
saida = collections.defaultdict(list)
for p in sorted((REPO / "municipais").glob("*/*/**/*.md")):
    if any(x.startswith(("_", ".")) for x in p.relative_to(REPO / "municipais").parts):
        continue
    texto = p.read_text()
    if "sapl" not in p.name:
        continue
    cab, _, corpo = texto[4:].partition("\n---\n")
    corpo = re.sub(r"^\n# [^\n]*\n\n", "", corpo)
    meta = {k: json.loads(v) for k, _, v in (l.partition(": ") for l in cab.splitlines()) if v}
    propria = (classe(meta.get("tipo_na_fonte", meta.get("tipo", ""))), numero_base(meta.get("numero", "")))
    outras = sorted({(classe(m["tipo"]), numero_base(m["numero"])) for rx in ANTIGAS for m in rx.finditer(corpo)} - {propria})
    if outras:
        grupo = "campinas<=1948" if "/campinas/" in str(p) and meta.get("data", "9")[:4] <= "1948" else ("campinas" if "/campinas/" in str(p) else "outros")
        saida[grupo].append((str(p.relative_to(REPO / "municipais")), outras))
for g, l in saida.items():
    print(g, len(l))
    if g != "campinas<=1948":
        for a, o in l: print("   ", a, o[:4])
json.dump(saida, open(sys.argv[1], "w"), ensure_ascii=False, indent=1)
