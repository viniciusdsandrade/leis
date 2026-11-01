"""Regenera os .md de Campinas com o conversor novo (rascunho) e classifica o que muda. Sem rede.
uso: medir_conversor.py SAIDA.json"""
import collections
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]  # raiz do repositório
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(REPO / "scripts"))
import comum  # noqa: E402
import conversor_novo  # noqa: E402
comum.texto_pdf_para_md = conversor_novo.texto_pdf_para_md_novo
from baixar_organicas_sapl import corpo_de_fonte, limpar_carimbo_campinas, texto_de_outra_norma  # noqa: E402

FONTE = REPO / "municipais/_fonte/organicas-sapl/sapl.campinas.sp.leg.br"
RUIDO = re.compile(r"Ramal:? ?1603|Estado de São Paulo|Coordenadoria de Biblioteca|Diretoria de Gestão Documental|Avenida da Saudade|www\.campinas\.sp\.leg\.br|Texto (?:somente )?para consulta|CÂMARA MUNICIPAL DE CAMPINAS")
palavras = lambda s: collections.Counter(re.findall(r"\w+", s))
saida, cont = [], collections.Counter()
arquivos = sorted((REPO / "municipais/SP/campinas").glob("**/*.md"))
for k, p in enumerate(arquivos):
    texto = p.read_text()
    cab, _, resto = texto[4:].partition("\n---\n")
    meta = {a: json.loads(b) for a, _, b in (l.partition(": ") for l in cab.splitlines())}
    m = re.match(r"\n# [^\n]*\n\n", resto)
    antigo = resto[m.end():][:-1]
    ident = meta["fonte"].rsplit("/", 1)[1]
    troca = texto_de_outra_norma("sapl.campinas.sp.leg.br", ident)
    b = (FONTE / f"{troca['id_fonte'] if troca else ident}.bin").read_bytes()
    corpo, motivo = corpo_de_fonte(b, meta["fonte_texto"])
    if motivo:
        cont["motivo"] += 1
        continue
    novo, _ = limpar_carimbo_campinas(corpo)
    if novo == antigo:
        cont["igual"] += 1
    else:
        faltam = palavras(antigo) - palavras(novo)
        tipo = "só acréscimo" if not faltam else "outra mudança"
        cont[tipo] += 1
        ruido = sum(len(RUIDO.findall(x)) for x in [novo]) - len(RUIDO.findall(antigo))
        cont["com ruído de carimbo a mais"] += ruido > 0
        saida.append({"arquivo": str(p.relative_to(REPO)), "tipo": tipo, "ruido": ruido, "acrescidas": sum((palavras(novo) - palavras(antigo)).values()),
                      "faltam": dict(faltam.most_common(8))})
    if (k + 1) % 2000 == 0:
        print("...", k + 1, dict(cont), flush=True)
print("FIM", dict(cont), flush=True)
Path(sys.argv[1]).write_text(json.dumps(saida, ensure_ascii=False, indent=1))
