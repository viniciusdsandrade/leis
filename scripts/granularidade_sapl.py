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
    r"\s+(?:N(?:[.º°O\s])*\s*)?(?P<numero>\d[\d.]*(?:-[A-Z])?)"
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
    achados = sorted((m for rx in (EPIGRAFE, *EPIGRAFES_ANTIGAS) for m in rx.finditer(corpo)), key=lambda m: m.start())
    for m in achados:
        identidade = (classe(m['tipo']), numero_base(m['numero']))
        if identidade == esperada or identidade in vistos:
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
    return [{'offset':m.start(),'trecho':corpo[max(0,m.start()-150):m.end()+300],
             'motivo':'possível aviso/extrato de outra publicação; pode ser citação ou modelo, exige revisão contextual sem corte automático'}
            for m in padrao.finditer(corpo)]
