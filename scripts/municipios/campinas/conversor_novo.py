"""Rascunho do texto_pdf_para_md com cabeçalho/rodapé só nas bordas da página, para medir contra o atual."""
import collections
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # scripts/
import comum  # noqa: E402

EPIGRAFE_LINHA = re.compile(r"^(?:LEI|DECRETO|RESOLU[ÇC][ÃA]O|PORTARIA|EMENDA|ATO|DELIBERA[ÇC][ÃA]O|INSTRU[ÇC][ÃA]O)\b.{0,40}?\bN", re.I)


def normal(ln):
    return re.sub(r"\s+", " ", ln).strip()


def linhas_sem_cabecalho(texto, topo=8, pe=5):
    paginas = [p.split("\n") for p in texto.split("\f")]
    cheias = [p for p in paginas if any(x.strip() for x in p)]
    bordas = []  # por página: índices das linhas nas bordas
    for p in paginas:
        idx = [i for i, x in enumerate(p) if x.strip()]
        bordas.append(set(idx[:topo] + idx[-pe:]))
    repetidas = set()
    if len(cheias) >= 2:
        freq = collections.Counter(ln for p, b in zip(paginas, bordas) for ln in {normal(p[i]) for i in b} if ln)
        repetidas = {ln for ln, c in freq.items() if c > len(cheias) / 2 and not re.match(r"^(Art|§)", ln)}
    saida, vistas = [], set()
    for p, b in zip(paginas, bordas):
        for i, ln in enumerate(p):
            # como no atual: a contagem usa a linha bruta e a comparação, a linha já sem os fios
            ln = re.sub(r"_{5,}|[-–—=]{8,}", " ", ln).strip()
            n = re.sub(r"\s+", " ", ln)
            if i in b and n in repetidas:
                # a epígrafe que se repete (republicação, retificação) fica na primeira vez
                if EPIGRAFE_LINHA.match(n) and n not in vistas:
                    vistas.add(n)
                else:
                    ln = ""
            saida.append(ln)
    return saida


def texto_pdf_para_md_novo(texto, topo=8, pe=5):
    linhas = ["" if re.fullmatch(r"\d{1,3}", ln) else ln for ln in linhas_sem_cabecalho(texto, topo, pe)]
    return comum_paragrafos(linhas)


def comum_paragrafos(linhas):
    """O resto de comum.texto_pdf_para_md, igual: parágrafos, títulos e rótulos."""
    src = open(comum.__file__).read()
    ini = src.index("    paras, atual = [], []", src.index("def texto_pdf_para_md"))
    fim = src.index('    return "\\n\\n".join(out) + "\\n"', ini)
    corpo = src[ini:fim]
    ns = {"linhas": linhas, "re": re, "FIM_CONECTIVO": comum.FIM_CONECTIVO, "HEADINGS": comum.HEADINGS, "LABEL": comum.LABEL}
    exec("\n".join(l[4:] for l in corpo.split("\n")), ns)
    return "\n\n".join(ns["out"]) + "\n"
