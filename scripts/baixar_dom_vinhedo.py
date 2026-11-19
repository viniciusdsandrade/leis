"""Vinhedo (SP) — leis e decretos recortados do Boletim Municipal, o Diário Oficial do Município.

Fonte: o portal da Prefeitura (`www.vinhedo.sp.gov.br/portal/diario-oficial`), o mesmo sistema de Paulínia e Valinhos
(`portal_diario_oficial.py`): listagem, dados abertos e o PDF de cada edição. O `robots.txt` veda os caminhos dos PDFs;
o mantenedor do acervo autorizou baixá-los mesmo assim (18/11/2026, confirmada em 19/11/2026), a no máximo uma
requisição a cada cinco segundos (`--apesar-do-robots`). Sem a opção, só as edições já em cache são lidas.

Leiaute lido: o Boletim que o sistema da Prefeitura gera (PDF do mPDF), em coluna única, página A4 ou A3, com o
cabeçalho "Quarta-feira, 18 de Novembro de 2026 | ANO 11 Edição 2679 - Extra | Distribuição gratuita" e o rodapé
"Boletim Municipal do Município de Vinhedo/SP" com o endereço da edição. As edições anteriores, compostas no InDesign
como jornal (722,8 x 841,9 pt), ficam fora, com o motivo.

Identidade: o número e a data do cabeçalho da primeira página. O número tem de ser o da listagem; a data impressa vale
mais que a de postagem.

Páginas em imagem: o Boletim reproduz parte dos atos como a imagem do documento assinado, às vezes com a camada de texto
de um OCR feito na origem ("ESTADO DESAOPAULO", "N'" no lugar de "Nº"). Esse texto não é nascido digital: o ato que
começa numa página coberta por imagem fica retido, e as páginas em imagem sem texto ficam registradas na edição.

Recorte e travas: os de Paulínia (`baixar_dom_paulinia.py`), com o perfil de Vinhedo, em que o decreto legislativo da
Câmara "DECRETA". Saem do texto as marcas de continuação do documento original ("Decreto nº 460/2026 – folha 3") e a
moldura dos documentos que a Câmara assina digitalmente (timbre, rodapé e o carimbo "Documento assinado digitalmente
por ...", como em Paulínia). O fecho vem por extenso ("aos dezoito dias do mês
de novembro de dois mil e vinte e seis") e não entra na conferência da data. O que falha fica em
`municipais/SP/vinhedo/_falhas.jsonl`, com o motivo.

    python3 -I scripts/baixar_dom_vinhedo.py --de 2023 --ate 2026 [--listar] [--max N] [--apesar-do-robots]
    python3 -I scripts/baixar_dom_vinhedo.py --despejar edicao.pdf     # texto em ordem de leitura, para conferência
"""
import argparse
import datetime as dt
import hashlib
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import baixar_dom_paulinia as base  # noqa: E402
import baixar_dom_valinhos as valinhos  # noqa: E402
import portal_diario_oficial as portal  # noqa: E402
from comum import CANONICO, yaml_str  # noqa: E402

PORTAL = portal.MUNICIPIOS["vinhedo"]
MUNICIPIO, UF, CODIGO_IBGE, BASE = PORTAL.nome, "SP", PORTAL.codigo_ibge, PORTAL.base
DESTINO = portal.RAIZ / UF / "vinhedo"
FALHAS = DESTINO / "_falhas.jsonl"
# pt: A4 e A3, os formatos do Boletim gerado pelo sistema, em pé ou deitados (quadros e anexos)
PAGINAS = [(595.3, 841.9), (841.9, 1190.5), (841.9, 595.3), (1190.5, 841.9)]
PERIODICO = "Boletim Municipal"
NOTA_DOM = ("recortado da edição do Boletim Municipal, o Diário Oficial do Município (PDF do portal da Prefeitura de "
            "Vinhedo); não substitui a publicação oficial")
# a página conta como imagem quando uma só imagem cobre esta fração dela, ou quando as imagens somadas cobrem a segunda
# (o documento escaneado em faixas)
COBERTA, COBERTA_NA_SOMA = 0.35, 0.6
MARCA_DE_IMAGEM = "⟦página {} em imagem⟧"
TEXTO_DE_PAGINA_EM_IMAGEM = 300  # caracteres: menos que isto, além do cabeçalho e do rodapé, é página sem texto
_MES = base._MES
_DIA = r"(?:segunda|terça|terca|quarta|quinta|sexta)(?:-feira)?|s[áa]bado|domingo"
CABECALHO_DA_EDICAO = re.compile(rf"(?:{_DIA}),\s*(\d{{1,2}})\s+de\s+({_MES})\s+de\s+(\d{{4}})\s*\|\s*ANO\s+\d+\s+"
                                 rf"Edi[çc][ãa]o\s+(\d[\d.]*)(?:\s*-\s*Extra)?\s*\|", re.I)
RODAPE_DA_EDICAO = re.compile(r"Boletim Municipal do Munic[íi]pio de Vinhedo|www\.vinhedo\.sp\.gov\.br/diario-oficial/\d+", re.I)
# a marca de continuação do documento original ("Decreto nº 460/2026 – folha 3"), com o travessão às vezes em outra linha
FOLHA = re.compile(r"^\s*[–-]?\s*(?:Decreto|Lei(?:\s+Complementar)?|Portaria|Resolu[çc][ãa]o|Edital|Emenda)\s+n[º°o.'’]*\s*"
                   r"\d[\d.]*\s*/\s*\d{4}\s*[–-]?\s*folha\s+\d+\s*[–-]?\s*$|^\s*[–-]\s*$", re.I)
# a moldura dos documentos que a Câmara assina digitalmente: o timbre e o rodapé de cada página e o carimbo da assinatura
# na margem, às vezes colado ao fim de uma linha do texto ("Publicado e Registrado na data supra. Documento assinado...")
MOLDURA_DA_LINHA = re.compile(r"^\s*(?:Av\.\s*Dois de Abril,\s*78|Centro\s*\|\s*Vinhedo\s*\|\s*SP|13280-077|"
                              r"www\.camaravinhedo\.sp\.gov\.br\s*\|.*|Ouvidoria:\s*\+55.*)\s*$", re.I)
CARIMBO = re.compile(r"[ \t]*(?:Documento assinado digitalmente por [^\n]*?\bem \d{2}/\d{2}/\d{4} \d{2}:\d{2}|"
                     r"Para verificar (?:sua|a) autenticidade, acesse:?[ \t]*\S*|e informe o c[óo]digo:?[ \t]*[0-9A-Z]+)", re.I)
CORRIDO = re.compile(rf"{CABECALHO_DA_EDICAO.pattern}|{RODAPE_DA_EDICAO.pattern}|{FOLHA.pattern}", re.I)

PERFIL = base.Perfil(
    nome=valinhos.PERFIL.nome,
    nao_e_assinatura=re.compile(base.NAO_E_ASSINATURA.pattern.replace("PAUL[ÍI]NIA", "VINHEDO"), re.I),
    cargo=valinhos.PERFIL.cargo,
    nota=valinhos.PERFIL.nota,
    signatario=re.compile(base.SIGNATARIO.pattern.replace("Paul[íi]nia", "Vinhedo"), re.M | re.I),
    fecho=re.compile(rf"Vinhedo[ \t]*,\s*(?:aos[ \t]+)?(\d{{1,2}})[ \t]*[º°o]?[ \t]+de[ \t]+({_MES})[ \t]+de[ \t]+(\d\.?\d{{3}})",
                     re.I),
    # além dos cabeçalhos de Paulínia, os títulos de seção do Boletim ("PODER EXECUTIVO")
    limite=re.compile(base.LIMITE.pattern + r"|^[ \t]*PODER[ \t]+(?:EXECUTIVO|LEGISLATIVO)\b", re.M),
    apenso=re.compile(base.APENSO.pattern.replace("PAUL[ÍI]NIA", "VINHEDO"), re.I),
    corrido=CORRIDO,
    # o decreto legislativo da Câmara de Vinhedo "DECRETA" ("A Câmara de Vereadores de Vinhedo ... DECRETA:")
    formula={**base.FORMULA, "decreto legislativo": re.compile(r"PROMULG|D[ \t]?E[ \t]?C[ \t]?R[ \t]?E[ \t]?T[ \t]?A", re.I)},
)


# ------------------------------------------------------------------------------------------ leitura da edição
def fora_do_leiaute(paginas):
    """Motivo quando alguma página não é do Boletim gerado pelo sistema (A4 ou A3); None quando todas são."""
    if not paginas:
        return "PDF sem páginas legíveis"
    for n, (largura, altura, _) in sorted(paginas.items()):
        if not any(abs(largura - lg) <= 3 and abs(altura - al) <= 3 for lg, al in PAGINAS):
            return f"página {n} de {largura:.0f} x {altura:.0f} pt, fora do leiaute conferido (Boletim gerado pelo sistema, A4 ou A3)"
    return None


def edicao_impressa(paginas):
    """(número, data ISO) do cabeçalho da primeira página; (None, None) sem ele."""
    if not paginas:
        return None, None
    _, altura, palavras = paginas[min(paginas)]
    for y0, _, texto in base.linhas_da_pagina(valinhos.visiveis(palavras)):
        m = CABECALHO_DA_EDICAO.search(texto) if y0 < altura * 0.2 else None
        if m:
            return m.group(4).replace(".", ""), base.data_iso(*m.groups()[:3])
    return None, None


def mancha(altura, palavras):
    """(topo, base) da área de texto: abaixo do cabeçalho da edição e acima do rodapé do Boletim."""
    linhas = base.linhas_da_pagina(valinhos.visiveis(palavras))
    alto = [y1 for y0, y1, texto in linhas if y0 < altura * 0.2 and CABECALHO_DA_EDICAO.search(texto)]
    baixo = [y0 for y0, _, texto in linhas if y0 > altura * 0.8 and RODAPE_DA_EDICAO.search(texto)]
    return (max(alto) + 1 if alto else float(base.TOPO)), (min(baixo) - 1 if baixo else altura)


def sem_moldura(texto):
    """O texto sem a moldura das páginas: as marcas de continuação do documento original, o timbre e o rodapé dos
    documentos da Câmara e o carimbo da assinatura digital (a linha que só tinha o carimbo sai inteira)."""
    saida = []
    for linha in texto.split("\n"):
        if FOLHA.search(linha) or MOLDURA_DA_LINHA.search(linha):
            continue
        limpa = CARIMBO.sub("", linha).rstrip()
        if limpa != linha.rstrip() and not limpa.strip():
            continue
        saida.append(limpa)
    return "\n".join(saida)


def cobertura_por_imagem(pdf, paginas):
    """{página: (maior fração coberta por uma imagem, soma das frações)}, pelo `pdfimages -list` do PDF."""
    saida = subprocess.run(["pdfimages", "-list", str(pdf)], capture_output=True, timeout=300).stdout.decode("utf-8", "replace")
    return cobertura_da_listagem(saida, paginas)


def cobertura_da_listagem(saida, paginas):
    """{página: (fração da área coberta pela maior imagem, soma das frações de todas)}, da saída do `pdfimages -list`: o
    tamanho da imagem em pixels dividido pela resolução dá a área que ela ocupa na página, em pontos."""
    cobertura = {}
    for linha in saida.splitlines():
        campos = linha.split()
        if len(campos) < 14 or not campos[0].isdigit():
            continue
        n, largura_px, altura_px = int(campos[0]), int(campos[3]), int(campos[4])
        try:
            ppi_x, ppi_y = float(campos[12]), float(campos[13])
        except ValueError:
            continue
        if n not in paginas or ppi_x <= 0 or ppi_y <= 0:
            continue
        largura, altura, _ = paginas[n]
        fracao = (largura_px / ppi_x * 72) * (altura_px / ppi_y * 72) / (largura * altura)
        maior, soma = cobertura.get(n, (0.0, 0.0))
        cobertura[n] = (max(maior, fracao), soma + fracao)
    return cobertura


class Edicao(base.Edicao):
    """Uma edição do Boletim: as palavras de todas as páginas, o texto de cada página na ordem de leitura, sem as
    marcas de continuação, o fluxo do PDF (sem cabeçalho, rodapé e marcas) e as páginas cobertas por imagem."""

    def __init__(self, pdf):
        self.pdf = pdf
        self.paginas = base.palavras_da_edicao(pdf)
        self.jornal = False
        self._fluxo = None
        self._cobertura = None

    def cobertura(self):
        if self._cobertura is None:
            self._cobertura = cobertura_por_imagem(self.pdf, self.paginas)
        return self._cobertura

    def em_imagem(self, n):
        maior, soma = self.cobertura().get(n, (0.0, 0.0))
        return maior >= COBERTA or soma >= COBERTA_NA_SOMA

    def fluxo(self):
        if self._fluxo is None:
            bruto = subprocess.run(["pdftotext", "-q", "-raw", "-enc", "UTF-8", str(self.pdf), "-"], capture_output=True,
                                   timeout=900).stdout
            linhas = bruto.decode("utf-8", "replace").replace("\f", "\n").split("\n")
            self._fluxo = base.so_letras("\n".join(ln for ln in linhas if not CORRIDO.search(ln)))
        return self._fluxo

    def trechos(self):
        """O Boletim tem uma coluna só: a mancha inteira de cada página é uma região. A divisão em zonas, que serve aos
        Diários de colunas, acharia calha no recuo das assinaturas e partiria as linhas longas."""
        saida = []
        for n, (largura, altura, palavras) in sorted(self.paginas.items()):
            topo, fundo = mancha(altura, palavras)
            texto = sem_moldura(base.dom.texto_da_regiao(self.pdf, n, 0, topo, largura, fundo - topo)).rstrip()
            if texto.strip() and self.em_imagem(n):
                texto = MARCA_DE_IMAGEM.format(n) + "\n" + texto  # o recorte que passar por esta página fica retido
            if texto.strip():
                saida.append((n, texto))
        return saida


def pagina_em_imagem(leitura, ato, corpo):
    """Retém o ato que começa ou continua numa página coberta por imagem: o texto dela, quando existe, é OCR feito na
    origem. A leitura marca o começo de cada página em imagem (`MARCA_DE_IMAGEM`)."""
    marcadas = [int(n) for n in re.findall(r"⟦página (\d+) em imagem⟧", corpo)]
    if leitura.em_imagem(ato["pagina"]) or marcadas:
        pagina = ato["pagina"] if leitura.em_imagem(ato["pagina"]) else marcadas[0]
        return f"a página {pagina} reproduz o documento como imagem; o texto dela é OCR da origem, não nascido digital"
    return None


def paginas_sem_texto(leitura):
    """Motivo da edição para as páginas em imagem sem texto: os atos nelas não são lidos."""
    vazias = []
    for n, (_, altura, palavras) in sorted(leitura.paginas.items()):
        if not leitura.em_imagem(n):
            continue
        topo, fundo = mancha(altura, palavras)
        if sum(len(p[4]) for p in valinhos.visiveis(palavras) if topo <= p[1] and p[3] <= fundo) < TEXTO_DE_PAGINA_EM_IMAGEM:
            vazias.append(n)
    if not vazias:
        return []
    return [f"páginas em imagem, sem texto ({', '.join(map(str, vazias))}): os atos nelas não são lidos"]


# ------------------------------------------------------------------------------------------ gravação
def montar_md(ato, edicao, corpo, tem_quadro, sha_pdf, hoje):
    _, tipo = CANONICO[ato["chave"]]
    titulo = base.titulo_de(ato)
    notas = [NOTA_DOM] + ([base.dom.NOTA_QUADRO] if tem_quadro else [])
    dia = dt.date.fromisoformat(edicao["data"]).strftime("%d/%m/%Y")
    meta = [("titulo", titulo), ("tipo", tipo), ("tipo_na_fonte", ato["tipo_na_fonte"]), ("numero", ato["numero"]),
            ("data", ato["data"]), ("municipio", MUNICIPIO), ("uf", UF), ("codigo_ibge", CODIGO_IBGE)]
    ementa = base.ementa_de(corpo, caixa_mista=True)
    if ementa:
        meta.append(("ementa", ementa))
    meta += [("versao_texto", "texto original (não consolidado); " + "; ".join(notas)),
             ("publicacao", f"{PERIODICO} do Município de {MUNICIPIO}, edição nº {edicao['edicao']}, de {dia}, p. {ato['pagina']}"),
             ("data_publicacao", edicao["data"]),
             ("fonte", f"{BASE}/portal/diario-oficial/ver/{edicao['id']}"),
             ("fonte_texto", edicao["pdf"]),
             ("sha256_fonte", sha_pdf),
             ("sha256_texto", hashlib.sha256(corpo.encode("utf-8")).hexdigest()),
             ("baixado_em", hoje.isoformat())]
    return "---\n" + "\n".join(f"{k}: {yaml_str(v)}" for k, v in meta) + f"\n---\n\n# {titulo}\n\n{corpo}\n"


# ------------------------------------------------------------------------------------------ execução
VINHEDO = base.Diario(portal=PORTAL, destino=DESTINO, falhas=FALHAS, edicao=Edicao, fora_do_leiaute=fora_do_leiaute,
                      edicao_impressa=edicao_impressa, perfil=PERFIL, montar_md=montar_md, retencao=pagina_em_imagem,
                      notas=paginas_sem_texto)


def executar(de, ate, maximo=0, listar=False, rps=0.5, apesar_do_robots=False):
    """O fluxo comum aos Diários do portal (`baixar_dom_paulinia.executar_diario`) com a leitura de Vinhedo."""
    return base.executar_diario(VINHEDO, de, ate, maximo, listar, rps, apesar_do_robots)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--de", type=int, help="primeiro ano")
    ap.add_argument("--ate", type=int, help="último ano, inclusive")
    ap.add_argument("--max", type=int, default=0, help="limita novas conversões; 0 = sem limite")
    ap.add_argument("--listar", action="store_true", help="só confere a listagem contra os dados abertos; não baixa PDFs")
    ap.add_argument("--rps", type=float, default=0.5, help="requisições por segundo")
    ap.add_argument("--apesar-do-robots", action="store_true",
                    help="baixa os PDFs mesmo com o robots.txt vedando o download (autorização de 18/11/2026)")
    ap.add_argument("--despejar", type=Path, help="mostra o texto de uma edição em ordem de leitura e sai")
    a = ap.parse_args()
    if a.despejar:
        for pagina, texto in Edicao(a.despejar).trechos():
            print(f"\n=== página {pagina}\n{texto}")
    elif a.de and a.ate:
        executar(a.de, a.ate, a.max, a.listar, a.rps, a.apesar_do_robots)
    else:
        ap.error("informe --de e --ate, ou --despejar")
