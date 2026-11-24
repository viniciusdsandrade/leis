---
titulo: "Convênio ICMS nº 133, de 16 de dezembro de 2005"
orgao: "Conselho Nacional de Política Fazendária (CONFAZ)"
tipo: "Convênio ICMS"
numero: "133"
data: 2005-12-16
ementa: "Altera o Convênio ICMS 115/03, que dispõe sobre a uniformização e disciplina a emissão, escrituração, manutenção e prestação das informações dos documentos fiscais emitidos em via única por sistema eletrônico de processamento de dados para contribuintes prestadores de serviços de comunicação e fornecedores de energia elétrica e dá outras providências."
revogada: null
versao_texto: "texto do portal do CONFAZ (www.confaz.fazenda.gov.br), com as notas de alteração, prorrogação e revogação que o portal acrescenta ao ato; não substitui a publicação no Diário Oficial da União"
publicacao: "Publicado no DOU de 21.12.05."
data_publicacao: "2005-12-21"
fonte: "https://www.confaz.fazenda.gov.br/legislacao/convenios/2005/CV133_05"
sha256_html_fonte: "ae17a0e41ff3a463541925e0146da11a6eb9615283fbf567ae8b0be7fe7988a1"
baixado_em: 2026-11-23
---
# Convênio ICMS nº 133, de 16 de dezembro de 2005

**CONVÊNIO ICMS 133/05**

**Publicado no DOU de 21.12.05.**

**Altera o Convênio ICMS 115/03, que dispõe sobre a uniformização e disciplina a emissão, escrituração, manutenção e prestação das informações dos documentos fiscais emitidos em via única por sistema eletrônico de processamento de dados para contribuintes prestadores de serviços de comunicação e fornecedores de energia elétrica e dá outras providências.**

**O Conselho Nacional de Política Fazendária - CONFAZ,**

na sua 120ª reunião ordinária, realizada em Mata de São João, BA, no dia 16 de dezembro de 2005, tendo em vista o disposto no art. 199 do Código Tributário Nacional (Lei nº 5.172, de 25 de outubro de 1966), resolve celebrar o seguinte

C O N V Ê N I O

**Cláusula primeira**

Os dispositivos adiante indicados do Convênio ICMS 115/03 , de 12 de dezembro de 2003, passam a vigorar com a seguinte redação:

I - o inciso V da cláusula quinta:

"V - na coluna "Observações":

a) o nome do volume do arquivo Mestre de Documento Fiscal e a respectiva chave de codificação digital calculada com base em todas as informações dos documentos fiscais contidos no volume;

b) um resumo com os somatórios dos valores negativos agrupados por espécie, de natureza meramente financeira, que reduzem o valor contábil da prestação ou da operação e não tenham nenhuma repercussão tributária;

c) um resumo, por unidade federada, com o somatório dos valores de base de cálculo do ICMS e valores de ICMS retidos antecipadamente por substituição tributária.";

II - os itens e subitens do Manual de Orientação, Anexo Único:

a) o subitem 4.1.3:

"4.1.3. Tamanho do registro: 254 bytes para os arquivos MESTRE DE DOCUMENTO FISCAL, ITEM DE DOCUMENTO FISCAL e DADOS CADASTRAIS DO DESTINATÁRIO DO DOCUMENTO FISCAL e 797 bytes para arquivo CONTROLE E IDENTIFICAÇÃO, acrescidos de CR/LF (Carriage return/Line Feed) ao final de cada registro;";

b) o subitem 4.2.1:

"4.2.1. Numérico (N), sem sinal, não compactado, alinhado à direita, suprimidos quaisquer caracteres não numéricos, com as posições não significativas preenchidas com zeros. Os valores negativos serão representados com o sinal negativo na primeira posição do campo.";

c) o subitem 4.5:

"4.5. Identificação dos Arquivos

4.5.1. Os arquivos serão identificados no formato:

<table><tr><td colspan="11">            <p>     Nome do Arquivo    </p>   </td>   <td>        </td>   <td colspan="3">            <p>     Extensão    </p>   </td>  </tr><tr><td>            <p>     U    </p>   </td>   <td>            <p>     F    </p>   </td>   <td>            <p>     S    </p>   </td>   <td>            <p>     S    </p>   </td>   <td>            <p>     S    </p>   </td>   <td>            <p>     A    </p>   </td>   <td>            <p>     A    </p>   </td>   <td>            <p>     M    </p>   </td>   <td>            <p>     M    </p>   </td>   <td>            <p>     ST    </p>   </td>   <td>            <p>     T    </p>   </td>   <td>            <p>     ..    </p>   </td>   <td>            <p>     V    </p>   </td>   <td>            <p>     V    </p>   </td>   <td>            <p>     V    </p>   </td>  </tr><tr><td colspan="2">            <p>     UF    </p>   </td>   <td colspan="3">            <p>     série    </p>   </td>   <td colspan="2">            <p>     ano    </p>   </td>   <td colspan="2">            <p>     mês    </p>   </td>   <td>            <p>     Status    </p>   </td>   <td>            <p>     tipo    </p>   </td>   <td>        </td>   <td colspan="3">            <p>     volume    </p>   </td>  </tr></table>

4.5.2. Observações:

4.5.2.1. O nome do arquivo é formado da seguinte maneira:

4.5.2.1.1. UF (UF) - sigla da unidade federada do emitente dos documentos fiscais;

4.5.2.1.2. Série (SSS) - série dos documentos fiscais;

4.5.2.1.3. Ano (AA) - ano do período de apuração dos documentos fiscais;

4.5.2.1.4. Mês (MM) - mês do período de apuração dos documentos fiscais;

4.5.2.1.5. Status (ST) - indica se o arquivo é normal (N) ou substituto (S);

4.5.2.1.6. Tipo (T) - inicial do tipo do arquivo, podendo assumir um dos seguintes valores:

a) ‘M’ - MESTRE DE DOCUMENTO FISCAL;

b) ‘I’ - ITEM DE DOCUMENTO FISCAL;

c) ‘D’ - DADOS CADASTRAIS DO DESTINATÁRIO DO DOCUMENTO FISCAL;

d) ‘C’ - CONTROLE E IDENTIFICAÇÃO.

4.5.2.1.7. Volume (VVV) – número seqüencial do volume, a quantidade de registros do arquivo MESTRE DE DOCUMENTO FISCAL é limitado a 100 (cem) mil ou 1 (um) milhão de documentos fiscais, conforme determinado no item 4.4.1, sempre que alcançado o limite, deverão ser criados arquivos de continuação, cuja numeração será seqüencial e consecutiva, iniciada em 001;";

d) o subitem 5.2.4.1:

"5.2.4.1. Campo 19 – Informar a situação do documento. Este campo deve ser preenchido com "S", em se tratando de documento fiscal cancelado, com "R", em se tratando de documento fiscal emitido em substituição a um documento fiscal cancelado ou anulado, ou "N", caso contrário;";

e) o item 6.2.3.1:

"6.2.3.1. Campo 10 - Informar o CFOP do item do documento fiscal. Para os itens classificados nos grupos 08 e 09 da Tabela de classificação do item de documento fiscal do item 11.5 preencher o campo com zeros;";

f) o item 6.2.5.1:

"6.2.5.1. Campo 26 - Informar a situação do item de fornecimento de energia elétrica ou de prestação de serviços de comunicação/telecomunicação. Este campo deve ser preenchido com "S", em se tratando de documento fiscal cancelado, com "R", em se tratando de documento fiscal emitido em substituição a um documento fiscal cancelado ou anulado, ou "N", caso contrário;";

g) o item 8:

"8. Arquivo de CONTROLE E IDENTIFICAÇÃO

8.1. Para cada volume, deverá ser criado um arquivo de controle e identificação, o qual será composto por um único registro, com as seguintes informações:

<table><tr><td>            <p>     n.º    </p>   </td>   <td>            <p>     Conteúdo    </p>   </td>   <td>            <p>     Tam.    </p>   </td>   <td colspan="2">            <p>     posição    </p>   </td>   <td>            <p>     formato    </p>   </td>  </tr><tr><td>        </td>   <td>        </td>   <td>        </td>   <td>            <p>     Inicial    </p>   </td>   <td>            <p>     Final    </p>   </td>   <td>        </td>  </tr><tr><td>            <p>     1    </p>   </td>   <td>            <p>     CNPJ    </p>   </td>   <td>            <p>     18    </p>   </td>   <td>            <p>     1    </p>   </td>   <td>            <p>     18    </p>   </td>   <td>            <p>     X    </p>   </td>  </tr><tr><td>            <p>     2    </p>   </td>   <td>            <p>     IE    </p>   </td>   <td>            <p>     15    </p>   </td>   <td>            <p>     19    </p>   </td>   <td>            <p>     33    </p>   </td>   <td>            <p>     X    </p>   </td>  </tr><tr><td>            <p>     3    </p>   </td>   <td>            <p>     Razão Social    </p>   </td>   <td>            <p>     50    </p>   </td>   <td>            <p>     34    </p>   </td>   <td>            <p>     83    </p>   </td>   <td>            <p>     X    </p>   </td>  </tr><tr><td>            <p>     4    </p>   </td>   <td>            <p>     Endereço    </p>   </td>   <td>            <p>     50    </p>   </td>   <td>            <p>     84    </p>   </td>   <td>            <p>     133    </p>   </td>   <td>            <p>     X    </p>   </td>  </tr><tr><td>            <p>     5    </p>   </td>   <td>            <p>     CEP    </p>   </td>   <td>            <p>     9    </p>   </td>   <td>            <p>     134    </p>   </td>   <td>            <p>     142    </p>   </td>   <td>            <p>     X    </p>   </td>  </tr><tr><td>            <p>     6    </p>   </td>   <td>            <p>     Bairro    </p>   </td>   <td>            <p>     30    </p>   </td>   <td>            <p>     143    </p>   </td>   <td>            <p>     172    </p>   </td>   <td>            <p>     X    </p>   </td>  </tr><tr><td>            <p>     7    </p>   </td>   <td>            <p>     Município    </p>   </td>   <td>            <p>     30    </p>   </td>   <td>            <p>     173    </p>   </td>   <td>            <p>     202    </p>   </td>   <td>            <p>     X    </p>   </td>  </tr><tr><td>            <p>     8    </p>   </td>   <td>            <p>     UF    </p>   </td>   <td>            <p>     2    </p>   </td>   <td>            <p>     203    </p>   </td>   <td>            <p>     204    </p>   </td>   <td>            <p>     X    </p>   </td>  </tr><tr><td>            <p>     9    </p>   </td>   <td>            <p>     Responsável pela apresentação    </p>   </td>   <td>            <p>     30    </p>   </td>   <td>            <p>     205    </p>   </td>   <td>            <p>     234    </p>   </td>   <td>            <p>     X    </p>   </td>  </tr><tr><td>            <p>     10    </p>   </td>   <td>            <p>     Cargo    </p>   </td>   <td>            <p>     20    </p>   </td>   <td>            <p>     235    </p>   </td>   <td>            <p>     254    </p>   </td>   <td>            <p>     X    </p>   </td>  </tr><tr><td>            <p>     11    </p>   </td>   <td>            <p>     Telefone    </p>   </td>   <td>            <p>     12    </p>   </td>   <td>            <p>     255    </p>   </td>   <td>            <p>     266    </p>   </td>   <td>            <p>     N    </p>   </td>  </tr><tr><td>            <p>     12    </p>   </td>   <td>            <p>     e-mail    </p>   </td>   <td>            <p>     40    </p>   </td>   <td>            <p>     267    </p>   </td>   <td>            <p>     306    </p>   </td>   <td>            <p>     X    </p>   </td>  </tr><tr><td>            <p>     13    </p>   </td>   <td>            <p>     Quantidade de registros do arquivo Mestre do Documento Fiscal    </p>   </td>   <td>            <p>     7    </p>   </td>   <td>            <p>     307    </p>   </td>   <td>            <p>     313    </p>   </td>   <td>            <p>     N    </p>   </td>  </tr><tr><td>            <p>     14    </p>   </td>   <td>            <p>     Quantidade de notas fiscais canceladas    </p>   </td>   <td>            <p>     7    </p>   </td>   <td>            <p>     314    </p>   </td>   <td>            <p>     320    </p>   </td>   <td>            <p>     N    </p>   </td>  </tr><tr><td>            <p>     15    </p>   </td>   <td>            <p>     Data de emissão do primeiro documento fiscal    </p>   </td>   <td>            <p>     8    </p>   </td>   <td>            <p>     321    </p>   </td>   <td>            <p>     328    </p>   </td>   <td>            <p>     N    </p>   </td>  </tr><tr><td>            <p>     16    </p>   </td>   <td>            <p>     Data de emissão do último documento fiscal    </p>   </td>   <td>            <p>     8    </p>   </td>   <td>            <p>     329    </p>   </td>   <td>            <p>     336    </p>   </td>   <td>            <p>     N    </p>   </td>  </tr><tr><td>            <p>     17    </p>   </td>   <td>            <p>     Número do primeiro documento fiscal    </p>   </td>   <td>            <p>     9    </p>   </td>   <td>            <p>     337    </p>   </td>   <td>            <p>     345    </p>   </td>   <td>            <p>     N    </p>   </td>  </tr><tr><td>            <p>     18    </p>   </td>   <td>            <p>     Número do último documento fiscal    </p>   </td>   <td>            <p>     9    </p>   </td>   <td>            <p>     346    </p>   </td>   <td>            <p>     354    </p>   </td>   <td>            <p>     N    </p>   </td>  </tr><tr><td>            <p>     19    </p>   </td>   <td>            <p>     Valor Total (com 2 decimais)    </p>   </td>   <td>            <p>     14    </p>   </td>   <td>            <p>     355    </p>   </td>   <td>            <p>     368    </p>   </td>   <td>            <p>     N    </p>   </td>  </tr><tr><td>            <p>     20    </p>   </td>   <td>            <p>     BC ICMS (com 2 decimais)    </p>   </td>   <td>            <p>     14    </p>   </td>   <td>            <p>     369    </p>   </td>   <td>            <p>     382    </p>   </td>   <td>            <p>     N    </p>   </td>  </tr><tr><td>            <p>     21    </p>   </td>   <td>            <p>     ICMS (com 2 decimais)    </p>   </td>   <td>            <p>     14    </p>   </td>   <td>            <p>     383    </p>   </td>   <td>            <p>     396    </p>   </td>   <td>            <p>     N    </p>   </td>  </tr><tr><td>            <p>     22    </p>   </td>   <td>            <p>     Operações Isentas ou não tributadas (com 2 decimais)    </p>   </td>   <td>            <p>     14    </p>   </td>   <td>            <p>     397    </p>   </td>   <td>            <p>     410    </p>   </td>   <td>            <p>     N    </p>   </td>  </tr><tr><td>            <p>     23    </p>   </td>   <td>            <p>     Outros valores que não compõe a BC do ICMS (com 2 decimais)    </p>   </td>   <td>            <p>     14    </p>   </td>   <td>            <p>     411    </p>   </td>   <td>            <p>     424    </p>   </td>   <td>            <p>     N    </p>   </td>  </tr><tr><td>            <p>     24    </p>   </td>   <td>            <p>     Nome do Arquivo Mestre do Documento Fiscal    </p>   </td>   <td>            <p>     15    </p>   </td>   <td>            <p>     425    </p>   </td>   <td>            <p>     439    </p>   </td>   <td>            <p>     X    </p>   </td>  </tr><tr><td>            <p>     25    </p>   </td>   <td>            <p>     Status de retificação ou substituição do arquivo    </p>   </td>   <td>            <p>     1    </p>   </td>   <td>            <p>     440    </p>   </td>   <td>            <p>     440    </p>   </td>   <td>            <p>     X    </p>   </td>  </tr><tr><td>            <p>     26    </p>   </td>   <td>            <p>     Código de Autenticação Digital do arquivo Mestre do Documento Fiscal    </p>   </td>   <td>            <p>     32    </p>   </td>   <td>            <p>     441    </p>   </td>   <td>            <p>     472    </p>   </td>   <td>            <p>     X    </p>   </td>  </tr><tr><td>            <p>     27    </p>   </td>   <td>            <p>     Quantidade de registros do arquivo Item de Documento Fiscal    </p>   </td>   <td>            <p>     9    </p>   </td>   <td>            <p>     473    </p>   </td>   <td>            <p>     481    </p>   </td>   <td>            <p>     N    </p>   </td>  </tr><tr><td>            <p>     28    </p>   </td>   <td>            <p>     Quantidade de itens cancelados    </p>   </td>   <td>            <p>     7    </p>   </td>   <td>            <p>     482    </p>   </td>   <td>            <p>     488    </p>   </td>   <td>            <p>     N    </p>   </td>  </tr><tr><td>            <p>     29    </p>   </td>   <td>            <p>     Data de emissão do primeiro documento fiscal    </p>   </td>   <td>            <p>     8    </p>   </td>   <td>            <p>     489    </p>   </td>   <td>            <p>     496    </p>   </td>   <td>            <p>     N    </p>   </td>  </tr><tr><td>            <p>     30    </p>   </td>   <td>            <p>     Data de emissão do último documento fiscal    </p>   </td>   <td>            <p>     8    </p>   </td>   <td>            <p>     497    </p>   </td>   <td>            <p>     504    </p>   </td>   <td>            <p>     N    </p>   </td>  </tr><tr><td>            <p>     31    </p>   </td>   <td>            <p>     Número do primeiro documento fiscal    </p>   </td>   <td>            <p>     9    </p>   </td>   <td>            <p>     505    </p>   </td>   <td>            <p>     513    </p>   </td>   <td>            <p>     N    </p>   </td>  </tr><tr><td>            <p>     32    </p>   </td>   <td>            <p>     Número do último documento fiscal    </p>   </td>   <td>            <p>     9    </p>   </td>   <td>            <p>     514    </p>   </td>   <td>            <p>     522    </p>   </td>   <td>            <p>     N    </p>   </td>  </tr><tr><td>            <p>     33    </p>   </td>   <td>            <p>     Total (com 2 decimais)    </p>   </td>   <td>            <p>     14    </p>   </td>   <td>            <p>     523    </p>   </td>   <td>            <p>     536    </p>   </td>   <td>            <p>     N    </p>   </td>  </tr><tr><td>            <p>     34    </p>   </td>   <td>            <p>     Descontos (com 2 decimais)    </p>   </td>   <td>            <p>     14    </p>   </td>   <td>            <p>     537    </p>   </td>   <td>            <p>     550    </p>   </td>   <td>            <p>     N    </p>   </td>  </tr><tr><td>            <p>     35    </p>   </td>   <td>            <p>     Acréscimos e Despesas Acessórias (com 2 decimais)    </p>   </td>   <td>            <p>     14    </p>   </td>   <td>            <p>     551    </p>   </td>   <td>            <p>     564    </p>   </td>   <td>            <p>     N    </p>   </td>  </tr><tr><td>            <p>     36    </p>   </td>   <td>            <p>     BC ICMS (com 2 decimais)    </p>   </td>   <td>            <p>     14    </p>   </td>   <td>            <p>     565    </p>   </td>   <td>            <p>     578    </p>   </td>   <td>            <p>     N    </p>   </td>  </tr><tr><td>            <p>     37    </p>   </td>   <td>            <p>     ICMS (com 2 decimais)    </p>   </td>   <td>            <p>     14    </p>   </td>   <td>            <p>     579    </p>   </td>   <td>            <p>     592    </p>   </td>   <td>            <p>     N    </p>   </td>  </tr><tr><td>            <p>     38    </p>   </td>   <td>            <p>     Operações Isentas ou não tributadas (com 2 decimais)    </p>   </td>   <td>            <p>     14    </p>   </td>   <td>            <p>     593    </p>   </td>   <td>            <p>     606    </p>   </td>   <td>            <p>     N    </p>   </td>  </tr><tr><td>            <p>     39    </p>   </td>   <td>            <p>     Outros valores que não compõe a BC do ICMS (com 2 decimais)    </p>   </td>   <td>            <p>     14    </p>   </td>   <td>            <p>     607    </p>   </td>   <td>            <p>     620    </p>   </td>   <td>            <p>     N    </p>   </td>  </tr><tr><td>            <p>     40    </p>   </td>   <td>            <p>     Nome do Arquivo Item do Documento Fiscal    </p>   </td>   <td>            <p>     15    </p>   </td>   <td>            <p>     621    </p>   </td>   <td>            <p>     635    </p>   </td>   <td>            <p>     X    </p>   </td>  </tr><tr><td>            <p>     41    </p>   </td>   <td>            <p>     Status de retificação ou substituição do arquivo    </p>   </td>   <td>            <p>     1    </p>   </td>   <td>            <p>     636    </p>   </td>   <td>            <p>     636    </p>   </td>   <td>            <p>     X    </p>   </td>  </tr><tr><td>            <p>     42    </p>   </td>   <td>            <p>     Código de Autenticação Digital do arquivo Item de Documento Fiscal    </p>   </td>   <td>            <p>     32    </p>   </td>   <td>            <p>     637    </p>   </td>   <td>            <p>     668    </p>   </td>   <td>            <p>     X    </p>   </td>  </tr><tr><td>            <p>     43    </p>   </td>   <td>            <p>     Quantidade de registros do arquivo Dados Cadastrais do Destinatário do Documento Fiscal    </p>   </td>   <td>            <p>     7    </p>   </td>   <td>            <p>     669    </p>   </td>   <td>            <p>     675    </p>   </td>   <td>            <p>     N    </p>   </td>  </tr><tr><td>            <p>     44    </p>   </td>   <td>            <p>     Nome do Arquivo Dados Cadastrais do Destinatário do Documento Fiscal    </p>   </td>   <td>            <p>     15    </p>   </td>   <td>            <p>     676    </p>   </td>   <td>            <p>     690    </p>   </td>   <td>            <p>     X    </p>   </td>  </tr><tr><td>            <p>     45    </p>   </td>   <td>            <p>     Status de retificação ou substituição do arquivo    </p>   </td>   <td>            <p>     1    </p>   </td>   <td>            <p>     691    </p>   </td>   <td>            <p>     691    </p>   </td>   <td>            <p>     X    </p>   </td>  </tr><tr><td>            <p>     46    </p>   </td>   <td>            <p>     Código de Autenticação Digital do arquivo Dados Cadastrais do Destinatário do Documento Fiscal    </p>   </td>   <td>            <p>     32    </p>   </td>   <td>            <p>     692    </p>   </td>   <td>            <p>     723    </p>   </td>   <td>            <p>     X    </p>   </td>  </tr><tr><td>            <p>     47    </p>   </td>   <td>            <p>     Versão do programa Validador utilizado na validação    </p>   </td>   <td>            <p>     3    </p>   </td>   <td>            <p>     724    </p>   </td>   <td>            <p>     726    </p>   </td>   <td>            <p>     N    </p>   </td>  </tr><tr><td>            <p>     48    </p>   </td>   <td>            <p>     Chave de Controle do Recibo de Entrega    </p>   </td>   <td>            <p>     9    </p>   </td>   <td>            <p>     727    </p>   </td>   <td>            <p>     732    </p>   </td>   <td>            <p>     X    </p>   </td>  </tr><tr><td>            <p>     49    </p>   </td>   <td>            <p>     Quantidade de Advertências encontradas    </p>   </td>   <td>            <p>     9    </p>   </td>   <td>            <p>     733    </p>   </td>   <td>            <p>     741    </p>   </td>   <td>            <p>     N    </p>   </td>  </tr><tr><td>            <p>     50    </p>   </td>   <td>            <p>     Brancos - reservado para uso futuro    </p>   </td>   <td>            <p>     24    </p>   </td>   <td>            <p>     742    </p>   </td>   <td>            <p>     765    </p>   </td>   <td>            <p>     X    </p>   </td>  </tr><tr><td>            <p>     51    </p>   </td>   <td>            <p>     Código de Autenticação Digital do registro    </p>   </td>   <td>            <p>     32    </p>   </td>   <td>            <p>     766    </p>   </td>   <td>            <p>     797    </p>   </td>   <td>            <p>     X    </p>   </td>  </tr><tr><td>        </td>   <td>            <p>     Total    </p>   </td>   <td>            <p>     797    </p>   </td>   <td>        </td>   <td>        </td>   <td>        </td>  </tr></table>

8.2. Observações

8.2.1. Identificação do Estabelecimento Informante

8.2.1.1. Campo 01 - CPNJ, no formato 99.999.999/9999-99

8.2.1.2. Campo 02 - Inscrição Estadual, no formato utilizado pela unidade federada

8.2.1.3. Campo 03 - Razão Social ou Denominação

8.2.1.4. Campo 04 - Endereço completo

8.2.1.5. Campo 05 - CEP, no formato 99999-999

8.2.1.6. Campo 06 - Bairro

8.2.1.7. Campo 07 - Município

8.2.1.8. Campo 08 - Sigla da unidade da federação

8.2.2. Identificação da pessoa responsável pelas informações

8.2.2.1. Campo 09 - Nome

8.2.2.2. Campo 10 - Cargo

8.2.2.3. Campo 11 - Telefone de contato

8.2.2.4. Campo 12 - e-mail de contato

8.2.3. Informações relativas ao Arquivo MESTRE DE DOCUMENTO FISCAL

8.2.3.1. Campo 13 - Quantidade de registros do arquivo MESTRE DE DOCUMENTO FISCAL

8.2.3.2. Campo 14 - Quantidade de documentos fiscais cancelados

8.2.3.3. Campo 15 - Data de emissão do primeiro documento fiscal

8.2.3.4. Campo 16 - Data de emissão do último documento fiscal

8.2.3.5. Campo 17 - Número do primeiro documento fiscal

8.2.3.6. Campo 18 - Número do último documento fiscal

8.2.3.7. Campo 19 - Somatório do Valor Total (campo 14 do arquivo MESTRE DE DOCUMENTO FISCAL), não incluir os valores dos documentos fiscais cancelados

8.2.3.8. Campo 20 - Somatório da BC ICMS (campo 15 do arquivo MESTRE DE DOCUMENTO FISCAL), não incluir os valores dos documentos fiscais cancelados;

8.2.3.9. Campo 21 - Somatório do ICMS (campo 16 do arquivo MESTRE DE DOCUMENTO FISCAL), não incluir os valores dos documentos fiscais cancelados

8.2.3.10. Campo 22 - Somatório das Operações isentas ou não tributadas (campo 17 do arquivo MESTRE DE DOCUMENTO FISCAL), não incluir os valores dos documentos fiscais cancelados

8.2.3.11. Campo 23 - Somatório dos Outros valores que não compõe a BC do ICMS (campo 18 do arquivo MESTRE DE DOCUMENTO FISCAL), não incluir os valores dos documentos fiscais cancelados

8.2.3.12. Campo 24 - Nome do arquivo MESTRE DE DOCUMENTO FISCAL

8.2.3.13. Campo 25 - Indicador do Status do arquivo: normal (N) ou substituto (S)

8.2.3.14. Campo 26 - Código de autenticação digital obtido através da aplicação do algoritmo MD5 (Message Digest 5, vide item 11.7) no arquivo MESTRE DE DOCUMENTO FISCAL

8.2.4. Informações relativas ao arquivo ITEM DE DOCUMENTO FISCAL

8.2.4.1. Campo 27 - Quantidade de registros do arquivo ITEM DE DOCUMENTO FISCAL

8.2.4.2. Campo 28 - Quantidade de registro de Item de Documento Fiscal cancelados

8.2.4.3. Campo 29 - Data de emissão do primeiro documento fiscal

8.2.4.4. Campo 30 - Data de emissão do último documento fiscal

8.2.4.5. Campo 31 - Número do primeiro documento fiscal

8.2.4.6. Campo 32 - Número do último documento fiscal

8.2.4.7. Campo 33 - Somatório do Total (campo 18 do arquivo ITEM DE DOCUMENTO FISCAL), não incluir os valores dos itens cancelados

8.2.4.8. Campo 34 - Somatório dos Descontos (campo 19 do arquivo ITEM DE DOCUMENTO FISCAL), não incluir os valores dos itens cancelados

8.2.4.9. Campo 35 - Somatório dos Acréscimos e Despesas Acessórias (campo 20 do arquivo ITEM DE DOCUMENTO FISCAL), não incluir os valores dos itens cancelados

8.2.4.10. Campo 36 - Somatório da BC ICMS (campo 21 do arquivo ITEM DE DOCUMENTO FISCAL), não incluir os valores dos itens cancelados

8.2.4.11. Campo 37 - Somatório do ICMS (campo 22 do arquivo ITEM DE DOCUMENTO FISCAL), não incluir os valores dos itens cancelados

8.2.4.12. Campo 38 - Somatório das Operações isentas ou não tributadas (campo 23 do arquivo ITEM DE DOCUMENTO FISCAL), não incluir os valores dos itens cancelados

8.2.4.13. Campo 39 - Somatório dos Outros valores que não compõe a BC do ICMS (campo 24 do arquivo ITEM DE DOCUMENTO FISCAL), não incluir os valores dos itens cancelados

8.2.4.14. Campo 40 - Nome do arquivo ITEM DE DOCUMENTO FISCAL

8.2.4.15. Campo 41 - Indicador do Status do arquivo: normal (N) ou substituto (S)

8.2.4.16. Campo 42 - Código de autenticação digital obtido através da aplicação do algoritmo MD5 (Message Digest 5, vide item 11.7) no arquivo ITEM DE DOCUMENTO FISCAL

8.2.5. Informações relativas ao arquivo DADOS CADASTRAIS DO DESTINATÁRIO DO DOCUMENTO FISCAL

8.2.5.1. Campo 43 - Quantidade de registros do arquivo DADOS CADASTRAIS DO DESTINATÁRIO DO DOCUMENTO FISCAL

8.2.5.2. Campo 44 - Nome do arquivo Dados Cadastrais do Destinatário do Documento Fiscal

8.2.5.3. Campo 45 - Indicador do Status do arquivo: normal (N) ou substituto (S)

8.2.5.4. Campo 46 - Código de autenticação digital obtido através da aplicação do algoritmo MD5 (Message Digest 5) no arquivo DADOS CADASTRAIS DO DESTINATÁRIO DO DOCUMENTO FISCAL

8.2.6. Informações de Controle

8.2.6.1. Campo 47 - Versão do programa Validador utilizado para gerar o arquivo de CONTROLE E IDENTIFICAÇÃO

8.2.6.2. Campo 48 - Chave de Controle do Recibo de Entrega

8.2.6.3. Campo 49 - Quantidade de Advertências encontradas na validação

8.2.6.4. Campo 50 - brancos - reservado para uso futuro

8.2.6.5. Campo 51 - Informar o Código de autenticação digital obtido através da aplicação do algoritmo MD5 (Message Digest 5, vide item 11.7) de 128 bits na cadeia de caracteres formado pelos campos 01 a 51.";

h) o subitem 11.5:

"11.5. Tabela de Classificação do Item de Documento Fiscal:

<table><tr><td>            <p>     Grupo    </p>   </td>   <td>            <p>     Código    </p>   </td>   <td>            <p>     Descrição    </p>   </td>  </tr><tr><td>            <p>     01. Assinatura    </p>   </td>   <td>            <p>     0101    </p>   </td>   <td>            <p>     Assinatura de serviços de telefonia    </p>   </td>  </tr><tr><td>        </td>   <td>            <p>     0102    </p>   </td>   <td>            <p>     Assinatura de serviços de comunicação de dados    </p>   </td>  </tr><tr><td>        </td>   <td>            <p>     0103    </p>   </td>   <td>            <p>     Assinatura de serviços de TV por Assinatura    </p>   </td>  </tr><tr><td>        </td>   <td>            <p>     0104    </p>   </td>   <td>            <p>     Assinatura de serviços de provimento à internet    </p>   </td>  </tr><tr><td>        </td>   <td>            <p>     0105    </p>   </td>   <td>            <p>     Assinatura de outros serviços de multimídia    </p>   </td>  </tr><tr><td>        </td>   <td>            <p>     0199    </p>   </td>   <td>            <p>     Assinatura de outros serviços    </p>   </td>  </tr><tr><td>            <p>     02. Habilitação    </p>   </td>   <td>            <p>     0201    </p>   </td>   <td>            <p>     Habilitação de serviços de telefonia    </p>   </td>  </tr><tr><td>        </td>   <td>            <p>     0202    </p>   </td>   <td>            <p>     Habilitação de serviços de comunicação de dados    </p>   </td>  </tr><tr><td>        </td>   <td>            <p>     0203    </p>   </td>   <td>            <p>     Habilitação de TV por Assinatura    </p>   </td>  </tr><tr><td>        </td>   <td>            <p>     0204    </p>   </td>   <td>            <p>     Habilitação de serviços de provimento à internet    </p>   </td>  </tr><tr><td>        </td>   <td>            <p>     0205    </p>   </td>   <td>            <p>     Habilitação de outros serviços multimídia    </p>   </td>  </tr><tr><td>        </td>   <td>            <p>     0299    </p>   </td>   <td>            <p>     Habilitação de outros serviços    </p>   </td>  </tr><tr><td rowspan="16">            <p>     03. Serviço Medido    </p>   </td>   <td>            <p>     0301    </p>   </td>   <td>            <p>     Serviço Medido - chamadas locais    </p>   </td>  </tr><tr><td>            <p>     0302    </p>   </td>   <td>            <p>     Serviço Medido - chamadas interurbanas no Estado    </p>   </td>  </tr><tr><td>            <p>     0303    </p>   </td>   <td>            <p>     Serviço Medido - chamadas interurbanas para fora do Estado    </p>   </td>  </tr><tr><td>            <p>     0304    </p>   </td>   <td>            <p>     Serviço Medido - chamadas internacionais    </p>   </td>  </tr><tr><td>            <p>     0305    </p>   </td>   <td>            <p>     Serviço Medido - Números Especiais (0300/0500/0600/0800/etc.)    </p>   </td>  </tr><tr><td>            <p>     0306    </p>   </td>   <td>            <p>     Serviço Medido - comunicação de dados    </p>   </td>  </tr><tr><td>            <p>     0307    </p>   </td>   <td>            <p>     Serviço Medido - chamadas originadas em Roaming    </p>   </td>  </tr><tr><td>            <p>     0308    </p>   </td>   <td>            <p>     Serviço Medido - chamadas recebidas em Roaming    </p>   </td>  </tr><tr><td>            <p>     0309    </p>   </td>   <td>            <p>     Serviço Medido - adicional de chamada    </p>   </td>  </tr><tr><td>            <p>     0310    </p>   </td>   <td>            <p>     Serviço Medido - provimento de acesso à Internet    </p>   </td>  </tr><tr><td>            <p>     0311    </p>   </td>   <td>            <p>     Serviço Medido - pay-per-view (programação TV)    </p>   </td>  </tr><tr><td>            <p>     0312    </p>   </td>   <td>            <p>     Serviço Medido - Mensagem SMS    </p>   </td>  </tr><tr><td>            <p>     0313    </p>   </td>   <td>            <p>     Serviço Medido - Mensagem MMS    </p>   </td>  </tr><tr><td>            <p>     0314    </p>   </td>   <td>            <p>     Serviço Medido - outros mensagens    </p>   </td>  </tr><tr><td>            <p>     0315    </p>   </td>   <td>            <p>     Serviço Medido - serviço multimídia    </p>   </td>  </tr><tr><td>            <p>     0399    </p>   </td>   <td>            <p>     Serviço Medido - outros serviços    </p>   </td>  </tr><tr><td rowspan="8">            <p>     04. Serviço pré-pago    </p>   </td>   <td>            <p>     0401    </p>   </td>   <td>            <p>     Cartão Telefônico - Telefonia Fixa    </p>   </td>  </tr><tr><td>            <p>     0402    </p>   </td>   <td>            <p>     Cartão Telefônico - Telefonia Móvel    </p>   </td>  </tr><tr><td>            <p>     0403    </p>   </td>   <td>            <p>     Cartão de Provimento de acesso à internet    </p>   </td>  </tr><tr><td>            <p>     0404    </p>   </td>   <td>            <p>     Ficha Telefônica    </p>   </td>  </tr><tr><td>            <p>     0405    </p>   </td>   <td>            <p>     Recarga de Créditos - Telefonia Fixa    </p>   </td>  </tr><tr><td>            <p>     0406    </p>   </td>   <td>            <p>     Recarga de Créditos - Telefonia Móvel    </p>   </td>  </tr><tr><td>            <p>     0407    </p>   </td>   <td>            <p>     Recarga de Créditos - Provimento de acesso à Internet    </p>   </td>  </tr><tr><td>            <p>     0499    </p>   </td>   <td>            <p>     Outras cobranças realizadas de assinantes de plano serviço pré-pago    </p>   </td>  </tr><tr><td>            <p>     05. Outros Serviços    </p>   </td>   <td>            <p>     0501    </p>   </td>   <td>            <p>     Serviço Adicional (substituição de número, troca de aparelho, emissão de 2ª via de conta, conta detalhada, etc.)    </p>   </td>  </tr><tr><td>        </td>   <td>            <p>     0502    </p>   </td>   <td>            <p>     Serviço Facilidades (identificador de chamadas, caixa postal, transferência temporária, não-perturbe, etc.)    </p>   </td>  </tr><tr><td>        </td>   <td>            <p>     0599    </p>   </td>   <td>            <p>     Outros Serviços    </p>   </td>  </tr><tr><td rowspan="11">            <p>     06. Energia Elétrica    </p>   </td>   <td>            <p>     0601    </p>   </td>   <td>            <p>     Energia Elétrica - Consumo    </p>   </td>  </tr><tr><td>            <p>     0602    </p>   </td>   <td>            <p>     Energia Elétrica - Demanda    </p>   </td>  </tr><tr><td>            <p>     0603    </p>   </td>   <td>            <p>     Energia Elétrica - Serviços (Vistoria de unidade consumidora, Aferição de Medidor, Ligação, Religação, Troca de medidor, etc.)    </p>   </td>  </tr><tr><td>            <p>     0604    </p>   </td>   <td>            <p>     Energia Elétrica - Encargos Emergenciais    </p>   </td>  </tr><tr><td>            <p>     0605    </p>   </td>   <td>            <p>     Tarifa de Uso dos Sistemas de Distribuição de Energia Elétrica - TUSD - Consumidor Cativo    </p>   </td>  </tr><tr><td>            <p>     0606    </p>   </td>   <td>            <p>     Tarifa de Uso dos Sistemas de Distribuição de Energia Elétrica - TUSD - Consumidor Livre    </p>   </td>  </tr><tr><td>            <p>     0607    </p>   </td>   <td>            <p>     Encargos de Conexão    </p>   </td>  </tr><tr><td>            <p>     0608    </p>   </td>   <td>            <p>     Tarifa de Uso dos Sistemas de Transmissão de Energia Elétrica - TUST - Consumidor Cativo    </p>   </td>  </tr><tr><td>            <p>     0609    </p>   </td>   <td>            <p>     Tarifa de Uso dos Sistemas de Transmissão de Energia Elétrica - TUST - Consumidor Livre    </p>   </td>  </tr><tr><td>            <p>     0610    </p>   </td>   <td>            <p>     Subvenção econômica para consumidores da subclasse "baixa renda"    </p>   </td>  </tr><tr><td>            <p>     0699    </p>   </td>   <td>            <p>     Energia Elétrica - Outros    </p>   </td>  </tr><tr><td rowspan="10">            <p>     07. Disponibilização de meios ou equipamentos    </p>   </td>   <td>            <p>     0701    </p>   </td>   <td>            <p>     de Aparelho Telefônico    </p>   </td>  </tr><tr><td>            <p>     0702    </p>   </td>   <td>            <p>     de Aparelho Identificador de chamadas    </p>   </td>  </tr><tr><td>            <p>     0703    </p>   </td>   <td>            <p>     de Modem    </p>   </td>  </tr><tr><td>            <p>     0704    </p>   </td>   <td>            <p>     de Rack    </p>   </td>  </tr><tr><td>            <p>     0705    </p>   </td>   <td>            <p>     de Sala/Recinto    </p>   </td>  </tr><tr><td>            <p>     0706    </p>   </td>   <td>            <p>     de Roteador    </p>   </td>  </tr><tr><td>            <p>     0707    </p>   </td>   <td>            <p>     de Servidor    </p>   </td>  </tr><tr><td>            <p>     0708    </p>   </td>   <td>            <p>     de Multiplexador    </p>   </td>  </tr><tr><td>            <p>     0709    </p>   </td>   <td>            <p>     de Decodificador/Conversor    </p>   </td>  </tr><tr><td>            <p>     0799    </p>   </td>   <td>            <p>     Outras disponibilizações    </p>   </td>  </tr><tr><td>            <p>     08. Cobranças    </p>   </td>   <td>            <p>     0801    </p>   </td>   <td>            <p>     Cobrança de Serviços de Terceiros    </p>   </td>  </tr><tr><td>        </td>   <td>            <p>     0802    </p>   </td>   <td>            <p>     Cobrança de Seguros    </p>   </td>  </tr><tr><td>        </td>   <td>            <p>     0803    </p>   </td>   <td>            <p>     Cobrança de Financiamento de Aparelho/Serviços    </p>   </td>  </tr><tr><td>        </td>   <td>            <p>     0804    </p>   </td>   <td>            <p>     Cobrança de Juros de Mora    </p>   </td>  </tr><tr><td>        </td>   <td>            <p>     0805    </p>   </td>   <td>            <p>     Cobrança de Multa de Mora    </p>   </td>  </tr><tr><td>        </td>   <td>            <p>     0806    </p>   </td>   <td>            <p>     Cobrança de Conta de meses anteriores    </p>   </td>  </tr><tr><td>        </td>   <td>            <p>     0807    </p>   </td>   <td>            <p>     Cobrança de Taxa Iluminação Pública    </p>   </td>  </tr><tr><td>        </td>   <td>            <p>     0808    </p>   </td>   <td>            <p>     Retenção de ICMS-ST    </p>   </td>  </tr><tr><td>        </td>   <td>            <p>     0899    </p>   </td>   <td>            <p>     Outras Cobranças    </p>   </td>  </tr><tr><td>            <p>     09. Deduções    </p>   </td>   <td>            <p>     0901    </p>   </td>   <td>            <p>     Dedução relativa a impugnação de serviços    </p>   </td>  </tr><tr><td>        </td>   <td>            <p>     0902    </p>   </td>   <td>            <p>     Dedução referente ajuste de conta    </p>   </td>  </tr><tr><td>        </td>   <td>            <p>     0903    </p>   </td>   <td>            <p>     Redutor – Energia Elétrica - In Nº 306/2003    </p>    <p>     (PIS/COFINS/IRPJ/CSLL)    </p>   </td>  </tr><tr><td>        </td>   <td>            <p>     0904    </p>   </td>   <td>            <p>     Dedução relativa à multa pela interrupção de fornecimento    </p>   </td>  </tr><tr><td>        </td>   <td>            <p>     0905    </p>   </td>   <td>            <p>     Dedução relativa à distribuição de dividendos Eletrobrás    </p>   </td>  </tr><tr><td>        </td>   <td>            <p>     0906    </p>   </td>   <td>            <p>     Dedução relativa à subvenção econômica para consumidores da subclasse "baixa renda"    </p>   </td>  </tr><tr><td>        </td>   <td>            <p>     0999    </p>   </td>   <td>            <p>     Outras deduções    </p>   </td>  </tr><tr><td>            <p>     10. Serviço não medido    </p>   </td>   <td>            <p>     1001    </p>   </td>   <td>            <p>     Serviço não medido de serviços de telefonia    </p>   </td>  </tr><tr><td>        </td>   <td>            <p>     1002    </p>   </td>   <td>            <p>     Serviço não medido de serviços de comunicação de dados    </p>   </td>  </tr><tr><td>        </td>   <td>            <p>     1003    </p>   </td>   <td>            <p>     Serviço não medido de serviços de TV por Assinatura    </p>   </td>  </tr><tr><td>        </td>   <td>            <p>     1004    </p>   </td>   <td>            <p>     Serviço não medido de serviços de provimento à internet    </p>   </td>  </tr><tr><td>        </td>   <td>            <p>     1005    </p>   </td>   <td>            <p>     Serviço não medido de outros serviços de multimídia    </p>   </td>  </tr><tr><td>        </td>   <td>            <p>     1099    </p>   </td>   <td>            <p>     Serviço não medido de outros serviços"    </p>   </td>  </tr></table>

**Cláusula segunda**

Fica acrescentado o parágrafo único à cláusula oitava do Convênio ICMS 115/03 , com a seguinte redação:

"Parágrafo Único. A unidade federada que adotar o Leiaute Fiscal de Processamento de Dados aprovado pelo Ato Cotepe nº 34/05 poderá, a seu critério, dispensar a geração dos registros C500, C510, C520, C530, C540, D200, D210, D220, D230 e D240 para os documentos fiscais emitidos em via única, nos termos deste convênio.".

Cláusula terceira

Ficam acrescentados os subitens a seguir indicados ao Manual de Orientação, Anexo Único do Convênio ICMS 115/03 , com as seguintes redações:

I - o subitem 4.4.3:

"4.4.3. O conjunto de arquivos MESTRE DE DOCUMENTO FISCAL, ITEM DE DOCUMENTO FISCAL, DADOS CADASTRAIS DO DESTINATÁRIO DO DOCUMENTO FISCAL e CONTROLE E IDENTIFICAÇÃO pertencentes ao mesmo volume devem ser gravados em um único CD-R ou DVD-R, ficando a critério do contribuinte a gravação de mais de um conjunto de arquivos na mesma mídia.";

II - o subitem 4.4. 4:

"4.4.4. A versão atual do programa de consulta de notas fiscais eNotaFiscal.exe deverá ser gravada em cada CD-R ou DVD-R utilizado na geração dos arquivos.".

Cláusula quarta

A classificação prevista no Grupo 10 da Tabela de Classificação de Item de Documento Fiscal, exceto em relação ao código 1002, do Manual de Orientação, Anexo Único do Convênio ICMS 115/03 , não se aplica aos Estados do Amazonas, Goiás, Mato Grosso, Mato Grosso do Sul e Tocantins e ao Distrito Federal.

Cláusula quinta

Este convênio entra em vigor na data de sua publicação no Diário Oficial da União, e a gravação dos arquivos magnéticos na forma estabelecida por este convênio será obrigatória em relação aos fatos geradores ocorridos a partir de:

I - 1 º de julho de 2006, para o Estado do Espírito Santo;

II - 1 º de janeiro de 2006, para os demais Estados.

Mata de São João, BA, 16 de dezembro de 2005.
