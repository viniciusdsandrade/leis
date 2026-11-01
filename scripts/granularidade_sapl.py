"""Sinaliza outras epígrafes normativas em anexos atribuídos a uma norma SAPL.

Detector conservador: não recorta, não apaga texto e não trata referência corrida
ou citação entre aspas como nova norma. Alertas exigem revisão do PDF original.
"""
import re
import unicodedata

EPIGRAFE = re.compile(
    r"^(?:\s*[*#]+\s*)?"
    r"(?P<tipo>EMENDA(?:\s+[AÀ]\s+(?:LEI\s+ORG[ÂA]NICA|LOMAN))?|"
    r"LEI(?:\s+(?:COMPLEMENTAR|MUNICIPAL|PROMULGADA))?|DECRETO(?:\s+(?:LEGISLATIVO|MUNICIPAL))?|PORTARIA|RESOLU[ÇC][ÃA]O)"
    r"\s+(?:N(?:[.º°Oo\s])*\s*)?(?P<numero>\d[\d.]*(?:-[A-Z])?)"
    r"(?:\s*/\s*\d{2,4}\b|\s*[,–—-]?\s+DE\s+\d{1,2}(?:[º°])?(?:\s|/))",
    re.I | re.M)
# Livros de leis antigos (Campinas, 1890 a 1948): a epígrafe não tem data; vem com a ementa entre
# parênteses ("LEI N. 287 ( Declara de utilidade publica...)") ou com "N." abreviado ("LEI N. 439
# DETERNINANDO...", "DECRETO N. 121, de 1946"). A citação moderna em começo de linha usa "nº"
# ("Lei nº 6.309, de 1988, e alterações"; "Lei nº 8.666 (Licitações)") e fica de fora.
EPIGRAFES_ANTIGAS = (
    re.compile(r"^(?:\s*[*#]+\s*)?(?P<tipo>LEI|RESOLU[ÇC][ÃA]O|DECRETO(?:[- ]LEI)?|ACTO|ATO)\s+N\.?\s*"
               r"(?P<numero>\d[\d.]*)\s*\(", re.I | re.M),
    re.compile(r"^(?:\s*[*#]+\s*)?(?P<tipo>LEI|RESOLUÇÃO|DECRETO(?:-LEI)?|ACTO|Lei|Resolução|Decreto(?:-Lei)?)\s+N\.\s*"
               r"(?P<numero>\d[\d.]*)\b", re.M),
)


# Citação em começo de linha não é epígrafe de outro ato: a linha do PDF abriu pela norma citada e o
# parágrafo anterior terminou no meio da frase ("...submetido à Lei Federal nº 6.766, e" / "nos termos do Decreto-"
# / "autorizados pelas seguintes leis:"), ou o trecho é o texto citado de uma retificação ("onde se lê:" / "leia-se:").
CONTINUACAO = re.compile(
    r"(?i)(?:\b(?:a|à|o|e|ou|ao|aos|as|os|da|de|do|das|dos|na|no|nas|nos|em|com|pela|pelo|pelas|pelos|que|para|sobre|"
    r"conforme|seguintes?|decreto-?)|[,;:(\-–—])\s*$")
CITADO_EM_RETIFICACAO = re.compile(r"(?i)(?:onde\s+se\s+l[êe]|leia[\s-]*se)\s*[:\-–—]?\s*[\"“”']*\s*$")
# O ato seguinte traz, logo depois da epígrafe e da ementa, a fórmula de promulgação ou o Art. 1º.
ABERTURA_DE_ATO = re.compile(
    r"(?i)\bDECRETA\b|D\s*E\s*C\s*R\s*E\s*T\s*A|\bRESOLVE\b|PROMULG|sancion|\bart(?:igo)?\s*\.?\s*1\s*[º°oa]?(?:\b|\s*[-–—])")


# depois da data da epígrafe, a citação segue a frase (", que dispõe", " e demais leis", " – “Cria"), e a
# epígrafe de um ato abre a ementa ou encerra o parágrafo
FRASE_SEGUE = re.compile(r"[,;)“”\"']|[-–—]\s|(?:e|ou)\s|[a-zà-ú]")


def epigrafe_e_citacao(corpo, m, antiga=False):
    """A epígrafe casada é citação de outra norma dentro do ato, não o começo de outro ato.

    Vale (1) quando vem logo depois de "onde se lê"/"leia-se"; (2) quando o parágrafo anterior termina no
    meio da frase (conectivo, vírgula, dois-pontos ou hífen) e a frase segue depois da data citada ("A QUE
    SE REFERE O / DECRETO N° 11.063, DE 30 DE DEZEMBRO DE 1992, QUE APROVA..."); (3) para a epígrafe moderna
    em caixa mista ("Lei Municipal nº 11.571, de 17 de junho de 2003.") quando a frase segue ou não há fórmula
    de promulgação nem Art. 1º nos 700 caracteres seguintes. Página de Diário Oficial em duas colunas corta
    frases antes das epígrafes dos outros atos: em maiúsculas e abrindo a ementa, elas continuam alertando.
    A epígrafe dos livros antigos ("Lei n. 133 (Creando...") fica fora de (3): o ato seguinte começa assim.
    """
    inicio = corpo.rfind("\n\n", 0, m.start())
    anterior = corpo[max(0, inicio - 160):inicio] if inicio > 0 else corpo[:m.start()]
    fim = corpo.find("\n\n", m.end())
    resto = corpo[m.end():len(corpo) if fim < 0 else fim]
    # a epígrafe casa até o dia; o resto da data ("DE DEZEMBRO DE 1992", "de 2001") não decide nada
    resto_da_data = re.match(r"(?i)\s*(?:(?:de\s+)?[a-zçãé]+\s+de\s+)?\d[\d.]{1,4}", resto)
    resto = resto[resto_da_data.end() if resto_da_data else 0:].lstrip(" \t")
    # "N.o"/"No" do OCR no lugar de "Nº" não torna a epígrafe caixa mista
    trecho = re.sub(r"\bN\.?o\b", "N", corpo[m.start():m.start() + 14])
    maiuscula = trecho == trecho.upper()
    segue = bool(FRASE_SEGUE.match(resto)) or (not maiuscula and resto.startswith("."))
    if anterior.strip() and CITADO_EM_RETIFICACAO.search(anterior):
        return True
    if segue and anterior.strip() and CONTINUACAO.search(anterior):
        return True
    if antiga or maiuscula:
        return False
    return segue or not ABERTURA_DE_ATO.search(corpo[m.end():m.end() + 700])


def normal(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s.upper()) if not unicodedata.combining(c))


def classe(tipo):
    t = normal(tipo)
    if 'EMENDA' in t:
        return 'EMENDA'
    if 'LEI COMPLEMENTAR' in t:
        return 'LEI COMPLEMENTAR'
    if 'DECRETO LEGISLATIVO' in t:
        return 'DECRETO LEGISLATIVO'
    if 'LEI ORGANICA' in t or t == 'LOMAN':
        return 'LEI ORGANICA'
    if re.search(r'DECRETO[- ]LEI', t):
        return 'DECRETO-LEI'
    if 'RESOLUC' in t:  # "Resoluções Até 1948" (Campinas), no plural
        return 'RESOLUCAO'
    for nome in ('LEI', 'DECRETO', 'PORTARIA', 'RESOLUCAO'):
        if nome in t:
            return nome
    return t


def numero_base(numero):
    m = re.match(r'\s*(\d[\d.]*(?:-[A-Z])?)', str(numero), re.I)
    if not m:
        return None
    return m[1].replace('.', '').upper().lstrip('0') or '0'


def alertas_multiplos_atos(corpo, tipo, numero):
    esperada = (classe(tipo), numero_base(numero))
    alertas = []
    vistos = set()
    achados = sorted(((m, rx is not EPIGRAFE) for rx in (EPIGRAFE, *EPIGRAFES_ANTIGAS) for m in rx.finditer(corpo)),
                     key=lambda par: par[0].start())
    for m, antiga in achados:
        identidade = (classe(m['tipo']), numero_base(m['numero']))
        if identidade == esperada or identidade in vistos:
            continue
        if epigrafe_e_citacao(corpo, m, antiga):
            continue
        vistos.add(identidade)
        fim = corpo.find('\n\n', m.start())
        fim = min(len(corpo), m.start() + 350) if fim < 0 else min(fim, m.start() + 350)
        alertas.append({'identidade_esperada': esperada, 'epigrafe_diversa': identidade,
                        'posicao_no_corpo': m.start(), 'trecho': corpo[m.start():fim].strip(),
                        'motivo': 'epígrafe de outra identidade no anexo; possível página/edição com múltiplos atos; revisar sem cortar automaticamente'})
    return alertas


def alertas_outras_publicacoes(corpo):
    """Avisos/extratos de outra coluna podem não conter epígrafe de lei/decreto."""
    padrao = re.compile(
        r'EDITAL\s+DISPON[IÍ]VEL|ABERTURA\s+DA\s+SESS[AÃ]O(?!\s+LEGISLATIVA)|RECEBIMENTO\s+DAS\s+PROPOSTAS|'
        r'PREG[AÃ]O\s+(?:ELETR[OÔ]NICO|PRESENCIAL)\s+N[.º°O\s]*\d|'
        r'EXTRATO\s+(?:DE|DO)\s+(?:CONTRATO|TERMO|DISPENSA|INEXIGIBILIDADE|ATA|ADITIVO)', re.I)
    alertas = []
    for m in padrao.finditer(corpo):
        # frase corrida do próprio ato ("sessão pública para recebimento das propostas"; "abertura da sessão, leitura")
        # não é aviso: o aviso/extrato vem em maiúsculas ou com iniciais maiúsculas ("Pregão Eletrônico nº 093/2018")
        if m.group(0)[0].islower():
            continue
        alertas.append({'offset':m.start(),'trecho':corpo[max(0,m.start()-150):m.end()+300],
             'motivo':'possível aviso/extrato de outra publicação; pode ser citação ou modelo, exige revisão contextual sem corte automático'})
    return alertas
