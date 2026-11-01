"""Acha PDFs anexados à norma errada no SAPL de Campinas: o PDF da norma A abre com a epígrafe da norma X.

Para cada X sem .md cujo texto está no PDF de A, confere identidade (número e data da epígrafe contra o
cadastro de X) e as travas do pipeline para X. Sem rede.
uso: trocados.py <retidas.json> <saida.json>
"""
import collections
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]  # raiz do repositório
sys.path.insert(0, str(REPO / "scripts"))
from baixar_organicas_sapl import corpo_de_fonte, corpo_integral_reconhecivel, limpar_carimbo_campinas  # noqa: E402
from granularidade_sapl import EPIGRAFE, alertas_multiplos_atos, alertas_outras_publicacoes, numero_base  # noqa: E402

HOST = "sapl.campinas.sp.leg.br"
CACHE = REPO / "municipais/_indice/organicas-sapl" / HOST
FONTE = REPO / "municipais/_fonte/organicas-sapl" / HOST
MESES = {m: i for i, m in enumerate(["janeiro", "fevereiro", "marco", "abril", "maio", "junho", "julho", "agosto",
                                      "setembro", "outubro", "novembro", "dezembro"], 1)}
DATA_EPIGRAFE = re.compile(r"DE\s+(\d{1,2})[º°o]?\s+DE\s+([A-ZÇÃa-zçã]+)\s+DE\s+(\d)\.?(\d{3})", re.I)


def sem_acento(s):
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFD", s.lower()) if not unicodedata.combining(c))


retidas = {r["id"]: r for r in json.loads(Path(sys.argv[1]).read_text())}
normas, tipos = {}, {}
for f in sorted(CACHE.glob("indice-legislacao-parcial-*.json")):
    d = json.loads(f.read_text())
    for t in d["tipos"]:
        tipos[t["id"]] = t
    for n in d["normas"]:
        normas[n["id"]] = n
por_numero = collections.defaultdict(list)
for i, n in normas.items():
    por_numero[(tipos[n["tipo"]]["sigla"], numero_base(n["numero"]))].append(n)

resultado, contagem = [], collections.Counter()
for a_id, a in sorted(retidas.items()):
    # o PDF é de outra lei quando a primeira epígrafe do documento já é a dela (antes de qualquer artigo)
    if a["motivo"] != "epígrafe de outra norma" or a.get("posicao", 9999) > 300 or a.get("epigrafe_inicial") != numero_base(a["outra"][1]):
        continue
    x_num = numero_base(a["outra"][1])
    candidatos = [n for n in por_numero.get((a["tipo"], x_num), []) if abs(int(n["ano"]) - int(a["ano"])) <= 1]
    if len(candidatos) != 1:
        contagem["X não identificada no cadastro"] += 1
        resultado.append({"pdf_de": a_id, "lei_no_pdf": x_num, "situacao": "X não identificada", "candidatos": len(candidatos)})
        continue
    x = candidatos[0]
    reg = {"pdf_de": a_id, "lei_do_cadastro_A": a["numero"], "x_id": x["id"], "x_numero": x["numero"], "x_data": x.get("data")}
    if x["id"] not in retidas:
        reg["situacao"] = "X já tem .md (PDF de A duplica o texto de X)"
    else:
        rx = retidas[x["id"]]
        b = (FONTE / f"{a_id}.bin").read_bytes()
        corpo, motivo = corpo_de_fonte(b, a["texto_integral"])
        corpo, notas = limpar_carimbo_campinas(corpo)
        tipo = tipos[x["tipo"]]
        problemas = []
        if alertas_multiplos_atos(corpo, tipo["descricao"], x["numero"]):
            problemas.append("outra epígrafe para X")
        if alertas_outras_publicacoes(corpo):
            problemas.append("outra publicação")
        if not corpo_integral_reconhecivel(corpo, "emenda" in tipo["descricao"].lower()):
            problemas.append("sem artigo inicial")
        epi = next(EPIGRAFE.finditer(corpo[:600]))
        md = DATA_EPIGRAFE.search(corpo[epi.start():epi.start() + 200])
        data_txt = None
        # mês pelas três primeiras letras: o próprio documento às vezes erra a grafia ("SETMBRO")
        mes = {m[:3]: i for m, i in MESES.items()}.get(sem_acento(md[2])[:3]) if md else None
        if mes:
            data_txt = "%s%s-%02d-%02d" % (md[3], md[4], mes, int(md[1]))
        reg["data_epigrafe"] = data_txt
        if data_txt != x.get("data"):
            problemas.append(f"data da epígrafe {data_txt} != cadastro de X {x.get('data')}")
        reg["x_motivo"] = rx["motivo"] + ((" / PDF de X abre com a lei " + str(rx.get("outra", [None, None])[1])) if rx.get("outra") else "")
        reg["situacao"] = "recuperável" if not problemas else "X com problema: " + "; ".join(problemas)
        reg["sha256_fonte"] = a["sha256_fonte"]
        reg["texto_integral"] = a["texto_integral"]
    contagem[reg["situacao"].split(":")[0]] += 1
    resultado.append(reg)
Path(sys.argv[2]).write_text(json.dumps(resultado, ensure_ascii=False, indent=1))
print(dict(contagem))
for r in resultado:
    if r["situacao"] == "recuperável" or r["situacao"].startswith("X com problema"):
        print(f"  PDF de {r['pdf_de']} (lei {r.get('lei_do_cadastro_A')}) -> lei {r['x_numero']} (id {r['x_id']}, {r['x_data']}) | {r['situacao']} | X: {r.get('x_motivo','')[:70]}")
