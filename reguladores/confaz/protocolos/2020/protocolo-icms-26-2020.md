---
titulo: "Protocolo ICMS nº 26, de 19 de outubro de 2020"
orgao: "Conselho Nacional de Política Fazendária (CONFAZ)"
tipo: "Protocolo ICMS"
numero: "26"
data: 2020-10-19
ementa: "Altera o Protocolo ICMS 20/05, que dispõe sobre a substituição tributária nas operações com sorvetes e com preparados para fabricação de sorvete em máquina."
revogada: null
versao_texto: "texto do portal do CONFAZ (www.confaz.fazenda.gov.br), com as notas de alteração, prorrogação e revogação que o portal acrescenta ao ato; não substitui a publicação no Diário Oficial da União"
publicacao: "Publicado no DOU de 22.10.2020, pelo Despacho 79/20."
data_publicacao: "2020-10-22"
fonte: "https://www.confaz.fazenda.gov.br/legislacao/protocolos/2020/pt026_20"
sha256_html_fonte: "50998b9287ed1e3b87bd819a301fc3cc4ebd9196b014526cb520183b2b591544"
baixado_em: 2026-11-24
---
# Protocolo ICMS nº 26, de 19 de outubro de 2020

PROTOCOLO ICMS 26/20, DE 19 DE OUTUBRO DE 2020.

Publicado no DOU de 22.10.2020, pelo Despacho 79/20.

Altera o Protocolo ICMS 20/05, que dispõe sobre a substituição tributária nas operações com sorvetes e com preparados para fabricação de sorvete em máquina.

**Os Estados de Acre, Alagoas, Amapá, Amazonas, Bahia, Espírito Santo, Goiás, Maranhão, Mato Grosso, Mato Grosso do Sul, Minas Gerais, Pará, Paraíba, Paraná, Pernambuco, Piauí, Rio de Janeiro, Rio Grande do Norte, Rio Grande do Sul, Rondônia, Roraima, Santa Catarina, São Paulo, Sergipe, Tocantins e o Distrito Federal**, neste ato representados pelos Secretários de Fazenda, Economia, Finanças, Receita ou Tributação, considerando o disposto nos arts. 102 e 199 do Código Tributário Nacional, Lei nº 5.172, de 25 de outubro de 1966, no art. 9º da Lei Complementar nº 87, de 13 de setembro de 1996 e no Convênio ICMS 142/18, de 14 de dezembro de 2018, resolvemp celebrar o seguinte

P R O T O C O L O

**Cláusula primeira** Fica alterado o inciso I do § 3º da cláusula segunda do Protocolo ICMS 20/05, de 11 de julho de 2005, que passa a vigorar com a seguinte redação:

“I - o fabricante ou importador fica responsável por enviar diretamente, ou através de suas entidades representativas, ao setor responsável das Secretarias de Fazenda das unidades federadas signatárias de destino, a lista de preço final sugerido a consumidor nos termos do inciso IV da cláusula vigésima primeira do Convênio ICMS 142/18, de 14 de dezembro de 2018, no formato do Anexo Único deste protocolo;”.

**Cláusula segunda** Fica acrescido o Anexo Único ao Protocolo ICMS 20/05, com a seguinte redação:

“ANEXO ÚNICO

Leiaute do arquivo XML para “Lista de Preço Final a Consumidor Sugerido pelo Fabricante ou Importador – Versão 1.0”

Schema XML: envPSCF\_v9.99.xsd

<table><tbody><tr><td> <p>#</p> </td> <td> <p>Campo</p> </td> <td> <p>Ele </p> </td> <td> <p>Pai</p> </td> <td> <p>Tipo </p> </td> <td colspan="2"> <p>Ocorr</p> </td> <td> <p>Tam </p> </td> <td> <p>Dec </p> </td> <td> <p>Descrição/Observação</p> </td> </tr><tr><td> <p>A01</p> </td> <td> <p>enviPSCF</p> </td> <td> <p>Raiz</p> </td> <td> <p>-</p> </td> <td> <p>-</p> </td> <td> <p>-</p> </td> <td colspan="2"> <p>-</p> </td> <td> <p>-</p> </td> <td> <p>TAG raiz do documento</p> </td> </tr><tr><td> <p>A02</p> </td> <td> <p>Versão</p> </td> <td> <p>A</p> </td> <td> <p>A01</p> </td> <td> <p>N</p> </td> <td> <p>1-1</p> </td> <td colspan="2"> <p>1-4</p> </td> <td> <p>2 </p> </td> <td> <p>Versão do leiaute do arquivo.</p> </td> </tr><tr><td> <p>B01</p> </td> <td> <p>dadosDeclarante</p> </td> <td> <p>G</p> </td> <td> <p>A01</p> </td> <td></td> <td> <p>1-1</p> </td> <td colspan="2"></td> <td> <p> </p> </td> <td> <p>Dados do declarante do arquivo de produtos.</p> </td> </tr><tr><td> <p>C01</p> </td> <td> <p>CNPJ</p> </td> <td> <p>E</p> </td> <td> <p>B01</p> </td> <td> <p>N</p> </td> <td> <p>1-1</p> </td> <td colspan="2"> <p>14</p> </td> <td></td> <td> <p>CNPJ do declarante.</p> </td> </tr><tr><td> <p>C02</p> </td> <td> <p>IEST</p> </td> <td> <p>E</p> </td> <td> <p>B01</p> </td> <td> <p>N</p> </td> <td> <p>0-1</p> </td> <td colspan="2"> <p>2-14</p> </td> <td></td> <td> <p>Inscrição Estadual de Substituto Tributário na UF de destino.</p> </td> </tr><tr><td> <p>C03</p> </td> <td> <p>xNome</p> </td> <td> <p>E</p> </td> <td> <p>B01</p> </td> <td> <p>C</p> </td> <td> <p>1-1</p> </td> <td colspan="2"> <p>3-100</p> </td> <td></td> <td> <p>Razão social do declarante.</p> </td> </tr><tr><td> <p>D01</p> </td> <td> <p>listaProdutos</p> </td> <td> <p>G</p> </td> <td> <p>A01</p> </td> <td></td> <td> <p>1-1</p> </td> <td colspan="2"></td> <td></td> <td> <p>Lista de produtos.</p> </td> </tr><tr><td> <p>E01</p> </td> <td> <p>Produtos</p> </td> <td> <p>G</p> </td> <td> <p>D01</p> </td> <td></td> <td> <p>1-N</p> </td> <td colspan="2"></td> <td></td> <td> <p>TAG de grupo do detalhamento das informações de produtos.</p> </td> </tr><tr><td> <p>F01</p> </td> <td> <p>cProd</p> </td> <td> <p>E</p> </td> <td> <p>E01</p> </td> <td> <p>C</p> </td> <td> <p>1-1</p> </td> <td colspan="2"> <p>1-60</p> </td> <td></td> <td> <p>Código do produto conforme informado na Nota Fiscal Eletrônica – NF-e, modelo 55.</p> </td> </tr><tr><td> <p>F02</p> </td> <td> <p>xProd</p> </td> <td> <p>E</p> </td> <td> <p>E01</p> </td> <td> <p>C</p> </td> <td> <p>1-1</p> </td> <td colspan="2"> <p>1-120</p> </td> <td></td> <td> <p>Descrição completa do item como adotada na NF-e.</p> </td> </tr><tr><td> <p>F03</p> </td> <td> <p>CEST</p> </td> <td> <p>E</p> </td> <td> <p>E01</p> </td> <td> <p>N</p> </td> <td> <p>1-1</p> </td> <td colspan="2"> <p>7</p> </td> <td></td> <td> <p>Código CEST do produto declarado.</p> </td> </tr><tr><td> <p>F04</p> </td> <td> <p>NCM</p> </td> <td> <p>E</p> </td> <td> <p>E01</p> </td> <td> <p>N</p> </td> <td> <p>1-1</p> </td> <td colspan="2"> <p>2-8</p> </td> <td></td> <td> <p>Código NCM/SH do produto.</p> </td> </tr><tr><td> <p>F05</p> </td> <td> <p>cEAN</p> </td> <td> <p>E</p> </td> <td> <p>E01</p> </td> <td> <p>N</p> </td> <td> <p>0-1</p> </td> <td colspan="2"> <p>0,8,12 13,14</p> </td> <td></td> <td> <p>GTIN (Global Trade Item Number) do produto, antigo código EAN Comercial ou código de barras, conforme informada na NF-e.</p> </td> </tr><tr><td> <p>F06</p> </td> <td> <p>cEANTrib</p> </td> <td> <p>E</p> </td> <td> <p>E01</p> </td> <td> <p>N</p> </td> <td> <p>0-1</p> </td> <td colspan="2"> <p>0,8,12 13,14</p> </td> <td></td> <td> <p>GTIN (Global Trade Item Number) do produto, antigo código EAN Tributário ou código de barras, conforme informada na NF-e.</p> </td> </tr><tr><td> <p>F07</p> </td> <td> <p>uCom</p> </td> <td> <p>E</p> </td> <td> <p>E01</p> </td> <td> <p>C</p> </td> <td> <p>1-1</p> </td> <td colspan="2"> <p>2</p> </td> <td></td> <td> <p>Unidade de comercialização do produto, conforme informada na NF-e.</p> </td> </tr><tr><td> <p>F08</p> </td> <td> <p>uTrib</p> </td> <td> <p>E</p> </td> <td> <p>E01</p> </td> <td> <p>C</p> </td> <td> <p>1.1</p> </td> <td colspan="2"> <p>2</p> </td> <td></td> <td> <p>Unidade Tributária do produto, conforme informada na NF-e.</p> </td> </tr><tr><td> <p>F09</p> </td> <td> <p>cUF</p> </td> <td> <p>E</p> </td> <td> <p>E01</p> </td> <td> <p>C</p> </td> <td> <p>1-1</p> </td> <td colspan="2"> <p>2</p> </td> <td></td> <td> <p>Sigla da UF de destino.</p> </td> </tr><tr><td> <p>F10</p> </td> <td> <p>vUnTrib</p> </td> <td> <p>E</p> </td> <td> <p>E01</p> </td> <td> <p>N</p> </td> <td> <p>1-1</p> </td> <td colspan="2"> <p>10</p> </td> <td> <p>2</p> </td> <td> <p>Preço final a consumidor sugerido pelo fabricante ou importador conforme Unidade Tributária definida em F08.</p> </td> </tr><tr><td> <p>F11</p> </td> <td> <p>INIC_TAB</p> </td> <td> <p>D</p> </td> <td> <p>E01</p> </td> <td> <p>C</p> </td> <td> <p>1-1</p> </td> <td colspan="2"> <p>2-8</p> </td> <td></td> <td> <p>Data de início da vigência do preço final a consumidor sugerido pelo fabricante ou importador - lista atual. Formato: AAAA-MM-DD</p> </td> </tr><tr><td> <p>F12</p> </td> <td> <p>INIC_TAB_ANTERIOR</p> </td> <td> <p>D</p> </td> <td> <p>E01</p> </td> <td> <p>C</p> </td> <td> <p>1-1</p> </td> <td colspan="2"> <p>2-8</p> </td> <td></td> <td> <p>Data de início da vigência do preço final a consumidor sugerido pelo fabricante ou importador – lista anterior. Formato: AAAA-MM-DD</p> </td> </tr><tr><td></td> <td></td> <td></td> <td></td> <td></td> <td></td> <td></td> <td></td> <td></td> <td></td> </tr></tbody></table>

FORMATOS DOS CAMPOS:

<table><tbody><tr><td> <p>Tipo</p> </td> <td> <p>N → Indica campo numérico</p> <p>C → Indica campo alfanumérico</p> <p>D → Indica campo de data</p> </td> </tr><tr><td> <p>Ocorr.</p> </td> <td> <p>Campo Ocorrência iniciado com 1 → Indica que o campo de é preenchimento obrigatório</p> <p>Campo Ocorrência iniciado com 0 → Indica que o campo só será preenchido se houver a informação</p> </td> </tr><tr><td> <p>Tam.</p> </td> <td> <p>Tamanho do campo (1-n) → pode ter de 1 a “n” caracteres</p> <p>Tamanho do campo (n) → deve ter “n” caracteres</p> <p>Tamanho do campo (n, n’, n”, n’”...) → pode ter n, n”, n”’... caracteres</p> </td> </tr><tr><td> <p>Dec.</p> </td> <td> <p>Quantidade de casas decimais do campo numérico</p> </td> </tr></tbody></table>

.”.

**Cláusula terceira** Este protocolo entra em vigor na data da sua publicação no Diário Oficial da União, produzindo efeitos a partir do primeiro dia do terceiro mês subsequente ao da sua publicação.
