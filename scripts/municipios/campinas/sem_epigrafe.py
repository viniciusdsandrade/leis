"""Lista os .md de Campinas cujo corpo não traz a epígrafe da própria norma (tipo e número). Sem rede.
uso: sem_epigrafe.py SAIDA.json"""
import collections
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]  # raiz do repositório
sys.path.insert(0, str(REPO / "scripts"))
from granularidade_sapl import EPIGRAFE, classe, numero_base  # noqa: E402

saida, cont = [], collections.Counter()
for p in sorted((REPO / "municipais/SP/campinas").glob("**/*.md")):
    texto = p.read_text()
    cab, _, corpo = texto[4:].partition("\n---\n")
    # o título "# Decreto nº ..." é gerado do cadastro; a epígrafe tem de estar no texto da fonte
    corpo = re.sub(r"^\n# [^\n]*\n\n", "", corpo)
    meta = {k: json.loads(v) for k, _, v in (l.partition(": ") for l in cab.splitlines())}
    propria = (classe(meta["tipo_na_fonte"]), numero_base(meta["numero"]))
    pos = next((m.start() for m in EPIGRAFE.finditer(corpo) if (classe(m["tipo"]), numero_base(m["numero"])) == propria), None)
    serie = p.relative_to(REPO / "municipais/SP/campinas").parts[0]
    cont[(serie, "com epígrafe" if pos is not None else "SEM epígrafe")] += 1
    if pos is None:
        ocr = "Texto obtido por OCR" in corpo[:300]
        saida.append({"arquivo": str(p.relative_to(REPO)), "ocr": ocr, "inicio": corpo[:200].replace("\n", " ")})
for k in sorted(cont):
    print(k, cont[k])
print("sem epígrafe com OCR:", sum(s["ocr"] for s in saida), "| sem OCR:", sum(not s["ocr"] for s in saida))
Path(sys.argv[1]).write_text(json.dumps(saida, ensure_ascii=False, indent=1))
