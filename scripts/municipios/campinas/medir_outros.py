"""Compara o conversor atual e o novo (rascunho) nos PDFs de texto em cache fora de Campinas. Sem rede.

Só o passo texto_pdf_para_md: cada coletor tem seu pós-processamento, então isto mede o tamanho do efeito,
não o .md final. PDFs escaneados (que vão para OCR) ficam de fora.
uso: medir_outros.py SAIDA.json
"""
import collections
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]  # raiz do repositório
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(REPO / "scripts"))
import comum  # noqa: E402
import conversor_novo  # noqa: E402

palavras = lambda s: collections.Counter(re.findall(r"\w+", s))
raizes = [REPO / "federal/_fonte", *sorted((REPO / "estaduais").glob("*/_fonte")), REPO / "estaduais/_fonte",
          REPO / "municipais/_fonte/capitais", REPO / "municipais/_fonte/cmrj", REPO / "municipais/_fonte/dioly",
          *[p for p in sorted((REPO / "municipais/_fonte/organicas-sapl").iterdir()) if "campinas.sp" not in p.name]]
cont, saida = collections.Counter(), []
for raiz in raizes:
    for f in sorted(x for x in raiz.rglob("*") if x.is_file()):
        with open(f, "rb") as h:
            if h.read(4) != b"%PDF":
                continue
        r = subprocess.run(["pdftotext", "-q", "-layout", "-enc", "UTF-8", str(f), "-"], capture_output=True, timeout=300)
        texto = r.stdout.decode("utf-8", "replace")
        colecao = str(raiz.relative_to(REPO))
        if comum.pdf_escaneado(texto):
            cont[(colecao, "escaneado (fora)")] += 1
            continue
        a, b = comum.texto_pdf_para_md(texto), conversor_novo.texto_pdf_para_md_novo(texto)
        if a == b:
            cont[(colecao, "igual")] += 1
            continue
        tipo = "só acréscimo" if not (palavras(a) - palavras(b)) else "outra mudança"
        cont[(colecao, tipo)] += 1
        saida.append({"pdf": str(f.relative_to(REPO)), "tipo": tipo, "acrescidas": sum((palavras(b) - palavras(a)).values())})
for k, v in sorted(cont.items()):
    print(k, v)
Path(sys.argv[1]).write_text(json.dumps(saida, ensure_ascii=False, indent=1))
print("FIM")
