---
titulo: "Convênio ICMS nº 65, de 26 de julho de 2013"
orgao: "Conselho Nacional de Política Fazendária (CONFAZ)"
tipo: "Convênio ICMS"
numero: "65"
data: 2013-07-26
ementa: "Altera o Convênio ICMS 09/09, que estabelece normas relativas ao equipamento Emissor de Cupom Fiscal (ECF) e ao Programa Aplicativo Fiscal - ECF (PAF-ECF) aplicáveis ao fabricante ou importador de ECF, ao contribuinte usuário de ECF, às empresas interventoras e às empresas desenvolvedoras de PAF-ECF."
revogada: null
versao_texto: "texto do portal do CONFAZ (www.confaz.fazenda.gov.br), com as notas de alteração, prorrogação e revogação que o portal acrescenta ao ato; não substitui a publicação no Diário Oficial da União"
publicacao: "Publicado no DOU de 30.07.13, pelo Despacho 153/13 ."
data_publicacao: "2013-07-30"
fonte: "https://www.confaz.fazenda.gov.br/legislacao/convenios/2013/CV065_13"
sha256_html_fonte: "49def4bbbf761ad1686f759ca08443499bd83c71c0a6140ba11280747a987b5e"
baixado_em: 2026-11-23
---
# Convênio ICMS nº 65, de 26 de julho de 2013

CONVÊNIO ICMS 65, DE 26 DE JULHO DE 2013

Publicado no DOU de 30.07.13, pelo Despacho 153/13 .

Altera o Convênio ICMS 09/09, que estabelece normas relativas ao equipamento Emissor de Cupom Fiscal (ECF) e ao Programa Aplicativo Fiscal - ECF (PAF-ECF) aplicáveis ao fabricante ou importador de ECF, ao contribuinte usuário de ECF, às empresas interventoras e às empresas desenvolvedoras de PAF-ECF.

**O Conselho Nacional de Política Fazendária - CONFAZ,** na sua 150ª reunião ordinária, realizada em Natal, RN, no dia 26 de julho de 2013, tendo em vista o disposto no artigo 199 do Código Tributário Nacional (Lei Federal nº 5.172/66), resolve celebrar o seguinte:

CONVÊNIO

**Cláusula primeira** Fica acrescido o § 5º à cláusula trigésima quinta do Convênio ICMS 09/09 , de 3 de abril de 2009, com a seguinte redação:

“§ 5º No procedimento de instalação do PAF-ECF a empresa desenvolvedora deverá configurá-lo com o Perfil de Requisitos, exigido ou aceito pela unidade federada do domicilio do estabelecimento usuário, definido na Especificação de Requisitos (ER-PAF-ECF) estabelecida em Ato COTEPE/ICMS.”

**Cláusula segunda** O Anexo II do Convênio ICMS 09/09 , de 3 de abril de 2009, passa a vigorar com a seguinte redação:

“ANEXO II

DADOS TÉCNICOS PARA GERAÇÃO DO ARQUIVO ELETRÔNICO A QUE SE REFERE O INCISO IV DA CLÁUSULA DÉCIMA PRIMEIRA

ARQUIVO ELETRÔNICO DE SENHAS DE INCIALIZAÇÃO GERADAS

1 - ARQUIVO:

1.1 - tipo: texto não delimitado;

1.2 - codificação: ASCII;

1.3 - organização: seqüencial;

1.4 - tamanho do registro: indeterminado, acrescido de CR/LF (Carriage return/Line feed) ao final de cada registro;

2 - FORMATO DOS CAMPOS:

2.1 - Numérico (N): sem sinal, não compactado e suprimido a vírgula e os pontos decimais;

2.2 - Alfanumérico (X): alinhado à esquerda, com as posições não significativas em branco;

3 - PREENCHIMENTO DOS CAMPOS:

3.1 - sem máscaras de edição;

3.2 - tratando-se de informação de data, deve ser expressa no formato ano, mês e dia (AAAAMMDD);

3.3 - numérico: na ausência de informação, os campos deverão ser preenchidos com zeros;

3.4 - alfanumérico: na ausência de informação, os campos deverão ser preenchidos com brancos;

4 - ESTRUTURA DO ARQUIVO ELETRÔNICO:

O arquivo eletrônico compõe-se dos seguintes tipos de registros:

4.1 - tipo S1 - registro destinado à identificação do estabelecimento fabricante de ECF informante;

4.2 - tipo S2 - registro destinado à identificação dos equipamentos ECF e respectivo usuário para os quais foram geradas senhas de inicialização

4.3 - tipo S9 - registro destinado à totalização da quantidade de registros existentes no arquivo.

5 - MONTAGEM DO ARQUIVO ELETRÔNICO:

5.1 - O arquivo deverá ser composto pelos seguintes conjuntos de registros, classificados na ordem abaixo:

<table><tbody><tr><td> <p>Tipo de Registro</p> </td> <td> <p>Nome do Registro</p> </td> <td> <p>Denominação dos Campos de Classificação</p> </td> <td> <p>A/D*</p> </td> </tr><tr><td> <p>S1</p> </td> <td> <p>Identificação do fabricante de ECF informante</p> </td> <td> <p>1º registro (único)</p> </td> <td> <p>------</p> </td> </tr><tr><td> <p>S2</p> </td> <td> <p>Relação dos Equipamentos ECF para os quais foram geradas Senhas de Inicialização</p> </td> <td> <p>Tipo de registro</p> <p>Código Nacional de Identificação do ECF</p> <p>Nº de Fabricação</p> </td> <td> <p>A</p> <p>A</p> <p>A</p> <p> </p> </td> </tr><tr><td> <p>S9</p> </td> <td> <p>Totalização de Registros</p> </td> <td> <p>Último registro (único)</p> </td> <td> <p>------</p> </td> </tr></tbody></table>

\* A indicação “A/D” significa ascendente/descendente

5.2 - REGISTRO TIPO S1 - IDENTIFICAÇÃO DO ESTABELECIMENTO FABRICANTE DE ECF INFORMANTE:

<table><tbody><tr><td> <p>Nº</p> </td> <td> <p>Denominação do Campo</p> </td> <td> <p>Conteúdo</p> </td> <td> <p>Tamanho</p> </td> <td colspan="2"> <p>Posição</p> </td> <td> <p>Formato</p> </td> </tr><tr><td> <p>01</p> </td> <td> <p>Tipo de registro</p> </td> <td> <p>“S1”</p> </td> <td> <p>02</p> </td> <td> <p>01</p> </td> <td> <p>02</p> </td> <td> <p>X</p> </td> </tr><tr><td> <p>02</p> </td> <td> <p>CNPJ</p> </td> <td> <p>CNPJ da empresa informante</p> </td> <td> <p>14</p> </td> <td> <p>03</p> </td> <td> <p>16</p> </td> <td> <p>N</p> </td> </tr><tr><td> <p>03</p> </td> <td> <p>Razão Social</p> </td> <td> <p>Razão Social da empresa informante</p> </td> <td> <p>50</p> </td> <td> <p>17</p> </td> <td> <p>66</p> </td> <td> <p>X</p> </td> </tr><tr><td> <p>04</p> </td> <td> <p>Endereço</p> </td> <td> <p>Endereço do estabelecimento informante</p> </td> <td> <p>50</p> </td> <td> <p>67</p> </td> <td> <p>116</p> </td> <td> <p>X</p> </td> </tr><tr><td> <p>05</p> </td> <td> <p>UF</p> </td> <td> <p>Sigla da Unidade da Federação de domicílio do informante</p> </td> <td> <p>02</p> </td> <td> <p>117</p> </td> <td> <p>118</p> </td> <td> <p>X</p> </td> </tr><tr><td> <p>06</p> </td> <td> <p>Mês de referência</p> </td> <td> <p>Mês a que se refere as informações prestadas, no formato MM</p> </td> <td> <p>02</p> </td> <td> <p>119</p> </td> <td> <p>120</p> </td> <td> <p>N</p> </td> </tr><tr><td> <p>07</p> </td> <td> <p>Ano de referência</p> </td> <td> <p>Ano a que se refere as informações prestadas, no formato AAAA</p> </td> <td> <p>04</p> </td> <td> <p>121</p> </td> <td> <p>124</p> </td> <td> <p>N</p> </td> </tr><tr><td> <p>08</p> </td> <td> <p>Responsável pelas informações</p> </td> <td> <p>Nome da pessoa responsável pelas informações prestadas</p> </td> <td> <p>50</p> </td> <td> <p>125</p> </td> <td> <p>174</p> </td> <td> <p>X</p> </td> </tr><tr><td> <p>09</p> </td> <td> <p>Código de identificação da estrutura do arquivo</p> </td> <td> <p>Código de identificação da estrutura do arquivo conforme tabela abaixo</p> </td> <td> <p>01</p> </td> <td> <p>175</p> </td> <td> <p>175</p> </td> <td> <p>N</p> </td> </tr></tbody></table>

5.2.1 - Observações:

5.2.1.1 - Deve ser criado somente um registro tipo S1 para cada arquivo.

5.2.1.2 - Campo 09: Informar o código de identificação da estrutura do arquivo, conforme a tabela abaixo:

Tabela de Códigos de Identificação da Estrutura do Arquivo:

<table><tbody><tr><td> <p>Código  </p><p></p>  </td> <td> <p>Descrição da Identificação da Estrutura do Arquivo  </p><p></p>  </td> </tr><tr><td> <p>1  </p><p></p>  </td> <td> <p>Estrutura conforme Anexo II deste Convênio na versão original.</p> </td> </tr><tr><td> <p>...</p> </td> <td> <p>...</p> </td> </tr></tbody></table>

5.3 - REGISTRO TIPO S2 - RELAÇÃO DOS EQUIPAMENTOS PARA OS QUAIS FORAM GERADAS SENHAS DE INICIALIZAÇÃO:

<table><tbody><tr><td> <p>Nº</p> </td> <td> <p>Denominação do Campo</p> </td> <td> <p>Conteúdo</p> </td> <td> <p>Tamanho</p> </td> <td colspan="2"> <p>Posição</p> </td> <td> <p>Formato</p> </td> </tr><tr><td> <p>01</p> </td> <td> <p>Tipo de registro</p> </td> <td> <p>“S2”</p> </td> <td> <p>02</p> </td> <td> <p>01</p> </td> <td> <p>02</p> </td> <td> <p>X</p> </td> </tr><tr><td> <p>02</p> </td> <td> <p>Código Nacional de Identificação de Equipamento ECF</p> </td> <td> <p>Código de identificação do tipo, marca, modelo e versão do ECF</p> </td> <td> <p>06</p> </td> <td> <p>03</p> </td> <td> <p>08</p> </td> <td> <p>X</p> </td> </tr><tr><td> <p>03</p> </td> <td> <p>Número de Fabricação</p> </td> <td> <p>Número de série de fabricação do ECF</p> </td> <td> <p>20</p> </td> <td> <p>09</p> </td> <td> <p>28</p> </td> <td> <p>X</p> </td> </tr><tr><td> <p>04</p> </td> <td> <p>CNPJ do estabelecimento usuário</p> </td> <td> <p>CNPJ do estabelecimento usuário do ECF para o qual foi gerada a senha de inicialização</p> </td> <td> <p>14</p> </td> <td> <p>29</p> </td> <td> <p>42</p> </td> <td> <p>N</p> </td> </tr><tr><td> <p>05</p> </td> <td> <p>IE do estabelecimento usuário</p> </td> <td> <p>Inscrição Estadual do estabelecimento usuário do ECF para o qual foi gerada a senha de inicialização</p> </td> <td> <p>15</p> </td> <td> <p>43</p> </td> <td> <p>57</p> </td> <td> <p>X</p> </td> </tr><tr><td> <p>06</p> </td> <td> <p>IM do estabelecimento usuário</p> </td> <td> <p>Inscrição Municipal do estabelecimento usuário do ECF para o qual foi gerada a senha de inicialização</p> </td> <td> <p>15</p> </td> <td> <p>58</p> </td> <td> <p>72</p> </td> <td> <p>X</p> </td> </tr><tr><td> <p>07</p> </td> <td> <p>CNPJ da empresa interventora</p> </td> <td> <p>CNPJ da empresa interventora para a qual a senha foi inofrmada</p> </td> <td> <p>14</p> </td> <td> <p>73</p> </td> <td> <p>86</p> </td> <td> <p>N</p> </td> </tr><tr><td> <p>08</p> </td> <td> <p>IE da empresa interventora</p> </td> <td> <p>Inscrição Estadual da empresa interventora para a qual a senha foi informada</p> </td> <td> <p>15</p> </td> <td> <p>87</p> </td> <td> <p>101</p> </td> <td> <p>X</p> </td> </tr><tr><td> <p>09</p> </td> <td> <p>Razão Social/Nome</p> </td> <td> <p>Razão Social/Nome da empresa interventora para a qual a senha foi informada</p> </td> <td> <p>40</p> </td> <td> <p>102</p> </td> <td> <p>141</p> </td> <td> <p>X</p> </td> </tr><tr><td> <p>10</p> </td> <td> <p>UF do estabelecimento usuário</p> </td> <td> <p>Unidade federada onde se localiza o estabelecimento usuário do ECF</p> </td> <td> <p>02</p> </td> <td> <p>142</p> </td> <td> <p>143</p> </td> <td> <p>X</p> </td> </tr></tbody></table>

5.3.1 - Observações:

5.3.1.1 - Deve ser criado um registro tipo S2 para cada ECF cuja senha de inicialização tenha sido gerada.

5.3.1.2 - Campo 02: Informar o Código Nacional de Identificação de Equipamento ECF relativo ao tipo, marca, modelo e versão do ECF em conformidade com o código constante em tabela publicada por meio de Despacho do Secretário Executivo do CONFAZ, ou com o código constante no Ato de Registro do ECF.

5.3.1.3 - Campos 04 e 07: Informar o CNPJ com 14 dígitos sem mascaras de edição.

5.4. REGISTRO TIPO S9 - TOTALIZAÇÃO DO ARQUIVO

<table><tbody><tr><td> <p>Nº</p> </td> <td> <p>Denominação do campo</p> </td> <td> <p>Conteúdo</p> </td> <td> <p>Tamanho</p> </td> <td colspan="2"> <p>Posição</p> </td> <td> <p>Formato</p> </td> </tr><tr><td> <p>01</p> </td> <td> <p>Tipo</p> </td> <td> <p>“S9”</p> </td> <td> <p>02</p> </td> <td> <p>01</p> </td> <td> <p>02</p> </td> <td> <p>N</p> </td> </tr><tr><td> <p>02</p> </td> <td> <p>CNPJ</p> </td> <td> <p>CNPJ da empresa informante</p> </td> <td> <p>14</p> </td> <td> <p>03</p> </td> <td> <p>16</p> </td> <td> <p>N</p> </td> </tr><tr><td> <p>03</p> </td> <td> <p>Indicador de movimento</p> </td> <td> <p>“SIM” quando houver movimento ou “NÃO” quando não houver movimento</p> </td> <td> <p>03</p> </td> <td> <p>17</p> </td> <td> <p>19</p> </td> <td> <p>X</p> </td> </tr><tr><td> <p>04</p> </td> <td> <p>Total de registros tipo S2</p> </td> <td> <p>Quantidade de registros tipo S2 informados no arquivo</p> </td> <td> <p>06</p> </td> <td> <p>20</p> </td> <td> <p>25</p> </td> <td> <p>N</p> </td> </tr></tbody></table>

5.4.1 - OBSERVAÇÕES:

5.4.1.1 - Deve ser criado um único registro tipo S9 para informar o total de registros tipo S2 constantes do arquivo;

5.4.1.2 - Campo 03: Informar “SIM” quando houver senhas geradas no período e registros tipo S2 no arquivo e “NÃO” quando não houver senhas geradas no período e registros tipo S2;

5.4.1.3 - Campo 04: Informar a quantidade de registros tipo S2 constantes no arquivo. Caso não haja registros tipo S2, preencher com zeros.”

6 - ENTREGA:

6.1 - O arquivo eletrônico deverá ser validado pelo programa aplicativo “Validador ECF” disponibilizado pela Secretaria de Estado de Fazenda de Minas Gerais em seu endereço eletrônico na internet e transmitido pelo programa “TED - Transmissor Eletrônico de Documentos” disponibilizado pela Secretaria da Fazenda do Estado do Rio Grande do Sul em seu endereço eletrônico na internet, ou por meio de outro recurso de transmissão definido pela unidade federada.

6.2 - O Recibo de Entrega será emitido pelo programa transmissor TED - Transmissor Eletrônico de Documentos, quando o arquivo for por ele transmitido.

6.3 - O arquivo eletrônico será recebido condicionalmente e submetido a teste de consistência. Constatada a inobservância das especificações previstas neste Manual de Orientação, o arquivo eletrônico será devolvido ao informante para correção, sendo desconsiderada a entrega do mesmo, para os efeitos previstos na legislação vigente.”

**Cláusula terceira** O Anexo V do Convênio ICMS 09/09 , de 3 de abril de 2009, passa a vigorar com a seguinte redação:

“ANEXO V

DADOS TÉCNICOS PARA GERAÇÃO DO ARQUIVO ELETRÔNICO A QUE SE REFEREM INCISO II DA CLÁUSULA DÉCIMA SEGUNDA, A CLÁUSULA VIGÉSIMA QUARTA E A CLÁUSULA TRIGÉSIMA PRIMEIRA

ARQUIVO ELETRÔNICO DE INICIALIZAÇÃO DE ECF

1 - ARQUIVO:

1.1 - tipo: texto não delimitado;

1.2 - codificação: ASCII;

1.3 - organização: seqüencial;

1.4 - tamanho do registro: indeterminado, acrescido de CR/LF (Carriage return/Line feed) ao final de cada registro;

2 - FORMATO DOS CAMPOS:

2.1 - Numérico (N): sem sinal, não compactado e suprimido a vírgula e os pontos decimais;

2.2 - Alfanumérico (X): alinhado à esquerda, com as posições não significativas em branco;

3 - PREENCHIMENTO DOS CAMPOS:

3.1 - sem máscaras de edição;

3.2 - tratando-se de informação de data, deve ser expressa no formato ano, mês e dia (AAAAMMDD);

3.3 - numérico: na ausência de informação, os campos deverão ser preenchidos com zeros;

3.4 - alfanumérico: na ausência de informação, os campos deverão ser preenchidos com brancos;

4 - ESTRUTURA DO ARQUIVO ELETRÔNICO:

O arquivo eletrônico compõe-se dos seguintes tipos de registros:

4.1 - tipo I1 - registro destinado à identificação do estabelecimento fabricante de ECF ou empresa interventora informante;

4.2 - tipo I2 - registro destinado à identificação dos equipamentos ECF inicializados no período e respectivo usuário;

4.3 - tipo I9 - registro destinado à totalização da quantidade de registros existentes no arquivo.

5 - MONTAGEM DO ARQUIVO ELETRÔNICO:

5.1 - O arquivo deverá ser composto pelos seguintes conjuntos de registros, classificados na ordem abaixo:

<table><tbody><tr><td> <p>Tipo de Registro</p> </td> <td> <p>Nome do Registro</p> </td> <td> <p>Denominação dos Campos de Classificação</p> </td> <td> <p>A/D*</p> </td> </tr><tr><td> <p>I1</p> </td> <td> <p>Identificação do fabricante ou interventora informante</p> </td> <td> <p>1º registro (único)</p> </td> <td> <p>------</p> </td> </tr><tr><td> <p>I2</p> </td> <td> <p>Relação dos Equipamentos ECF inicializados</p> </td> <td> <p>Tipo de registro</p> <p>Código Nacional de Identificação do ECF</p> <p>Nº de Fabricação</p> </td> <td> <p>A</p> <p>A</p> <p>A</p> </td> </tr><tr><td> <p>I9</p> </td> <td> <p>Totalização de Registros</p> </td> <td> <p>Último registro (único)</p> </td> <td> <p>------</p> </td> </tr></tbody></table>

\* A indicação “A/D” significa ascendente/descendente

5.2 - REGISTRO TIPO I1 - IDENTIFICAÇÃO DO ESTABELECIMENTO FABRICANTE DE ECF OU EMPRESA INTERVENTORA INFORMANTE:

<table><tbody><tr><td> <p>Nº</p> </td> <td> <p>Denominação do Campo</p> </td> <td> <p>Conteúdo</p> </td> <td> <p>Tamanho</p> </td> <td colspan="2"> <p>Posição</p> </td> <td> <p>Formato</p> </td> </tr><tr><td> <p>01</p> </td> <td> <p>Tipo de registro</p> </td> <td> <p>“I1”</p> </td> <td> <p>02</p> </td> <td> <p>01</p> </td> <td> <p>02</p> </td> <td> <p>X</p> </td> </tr><tr><td> <p>02</p> </td> <td> <p>Tipo de informante</p> </td> <td> <p>Código do tipo de informante, conforme tabela abaixo</p> </td> <td> <p>01</p> </td> <td> <p>03</p> </td> <td> <p>03</p> </td> <td> <p>N</p> </td> </tr><tr><td> <p>03</p> </td> <td> <p>CNPJ</p> </td> <td> <p>CNPJ da empresa informante</p> </td> <td> <p>14</p> </td> <td> <p>04</p> </td> <td> <p>17</p> </td> <td> <p>N</p> </td> </tr><tr><td> <p>04</p> </td> <td> <p>Razão Social</p> </td> <td> <p>Razão Social da empresa informante</p> </td> <td> <p>50</p> </td> <td> <p>18</p> </td> <td> <p>67</p> </td> <td> <p>X</p> </td> </tr><tr><td> <p>05</p> </td> <td> <p>Endereço</p> </td> <td> <p>Endereço do estabelecimento informante</p> </td> <td> <p>50</p> </td> <td> <p>68</p> </td> <td> <p>117</p> </td> <td> <p>X</p> </td> </tr><tr><td> <p>06</p> </td> <td> <p>UF</p> </td> <td> <p>Sigla da Unidade da Federação de domicílio do informante</p> </td> <td> <p>02</p> </td> <td> <p>118</p> </td> <td> <p>119</p> </td> <td> <p>X</p> </td> </tr><tr><td> <p>07</p> </td> <td> <p>Mês de referência</p> </td> <td> <p>Mês a que se refere as informações prestadas, no formato MM</p> </td> <td> <p>02</p> </td> <td> <p>120</p> </td> <td> <p>121</p> </td> <td> <p>N</p> </td> </tr><tr><td> <p>08</p> </td> <td> <p>Ano de referência</p> </td> <td> <p>Ano a que se refere as informações prestadas, no formato AAAA</p> </td> <td> <p>04</p> </td> <td> <p>122</p> </td> <td> <p>125</p> </td> <td> <p>N</p> </td> </tr><tr><td> <p>09</p> </td> <td> <p>Responsável pelas informações</p> </td> <td> <p>Nome da pessoa responsável pelas informações prestadas</p> </td> <td> <p>50</p> </td> <td> <p>126</p> </td> <td> <p>175</p> </td> <td> <p>X</p> </td> </tr><tr><td> <p>10</p> </td> <td> <p>Código de identificação da estrutura do arquivo</p> </td> <td> <p>Código de identificação da estrutura do arquivo conforme tabela abaixo</p> </td> <td> <p>01</p> </td> <td> <p>176</p> </td> <td> <p>176</p> </td> <td> <p>N</p> </td> </tr></tbody></table>

5.2.1 - Observações:

5.2.1.1 - Deve ser criado somente um registro tipo I1 para cada arquivo.

5.2.1.2 - Campo 02: Informar o código do tipo de informante conforme tabela abaixo:

Tabela de Tipos de Informante:

<table><tbody><tr><td> <p>Código</p> </td> <td> <p>Tipo de Informante</p> </td> </tr><tr><td> <p>1</p> </td> <td> <p>Estabelecimento Fabricante de ECF</p> </td> </tr><tr><td> <p>2</p> </td> <td> <p>Empresa Interventora Credenciada</p> </td> </tr></tbody></table>

5.2.1.3 - Campo 10: Informar o código de identificação da estrutura do arquivo, conforme a tabela abaixo:

Tabela de Códigos de Identificação da Estrutura do Arquivo:

<table><tbody><tr><td> <p>Código  </p><p></p>  </td> <td> <p>Descrição da Identificação da Estrutura do Arquivo  </p><p></p>  </td> </tr><tr><td> <p>1</p> </td> <td> <p>Estrutura conforme Anexo V deste Convênio na versão original.</p> </td> </tr><tr><td> <p>...</p> </td> <td> <p>...</p> </td> </tr></tbody></table>

5.3 - REGISTRO TIPO I2 - RELAÇÃO DOS EQUIPAMENTOS ECF INICIALIZADOS:

<table><tbody><tr><td> <p>Nº</p> </td> <td> <p>Denominação do Campo</p> </td> <td> <p>Conteúdo</p> </td> <td> <p>Tamanho</p> </td> <td colspan="2"> <p>Posição</p> </td> <td> <p>Formato</p> </td> </tr><tr><td> <p>01</p> </td> <td> <p>Tipo de registro</p> </td> <td> <p>“I2”</p> </td> <td> <p>02</p> </td> <td> <p>01</p> </td> <td> <p>02</p> </td> <td> <p>X</p> </td> </tr><tr><td> <p>02</p> </td> <td> <p>Código Nacional de Identificação de Equipamento ECF</p> </td> <td> <p>Código de identificação do tipo, marca, modelo e versão do ECF</p> </td> <td> <p>06</p> </td> <td> <p>03</p> </td> <td> <p>08</p> </td> <td> <p>X</p> </td> </tr><tr><td> <p>03</p> </td> <td> <p>Número de Fabricação</p> </td> <td> <p>Número de série de fabricação do ECF</p> </td> <td> <p>20</p> </td> <td> <p>09</p> </td> <td> <p>28</p> </td> <td> <p>X</p> </td> </tr><tr><td> <p>04</p> </td> <td> <p>CNPJ do estabelecimento usuário</p> </td> <td> <p>CNPJ do estabelecimento usuário do ECF para o qual foi inicializado</p> </td> <td> <p>14</p> </td> <td> <p>29</p> </td> <td> <p>42</p> </td> <td> <p>N</p> </td> </tr><tr><td> <p>05</p> </td> <td> <p>IE do estabelecimento usuário</p> </td> <td> <p>Inscrição Estadual do estabelecimento usuário do ECF para o qual foi inicializado</p> </td> <td> <p>15</p> </td> <td> <p>43</p> </td> <td> <p>57</p> </td> <td> <p>X</p> </td> </tr><tr><td> <p>06</p> </td> <td> <p>IM do estabelecimento usuário</p> </td> <td> <p>Inscrição Municipal do estabelecimento usuário do ECF para o qual foi inicializado</p> </td> <td> <p>15</p> </td> <td> <p>58</p> </td> <td> <p>72</p> </td> <td> <p>X</p> </td> </tr><tr><td> <p>07</p> </td> <td> <p>Chave Pública da Assinatura Digital de documentos emitidos</p> </td> <td> <p>Chave Pública da Assinatura Digital de documentos emitidos pelo ECF inicializado</p> </td> <td> <p>256</p> </td> <td> <p>73</p> </td> <td> <p>328</p> </td> <td> <p>X</p> </td> </tr><tr><td> <p>08</p> </td> <td> <p>Chave Pública da Assinatura Digital de Arquivos Eletrônicos</p> </td> <td> <p>Chave Pública da Assinatura Digital de arquivos eletrônicos gerados pelo     ECF inicializado</p> </td> <td> <p>256</p> </td> <td> <p>329</p> </td> <td> <p>584</p> </td> <td> <p>X</p> </td> </tr><tr><td> <p>09</p> </td> <td> <p>UF do estabelecimento usuário</p> </td> <td> <p>Unidade federada onde se localiza o estabelecimento usuário do ECF</p> </td> <td> <p>02</p> </td> <td> <p>585</p> </td> <td> <p>586</p> </td> <td> <p>X</p> </td> </tr></tbody></table>

5.3.1 - Observações:

5.3.1.1 - Deve ser criado um registro tipo I2 para cada ECF inicializado no período.

5.3.1.2 - Campo 02: Informar o Código Nacional de Identificação de Equipamento ECF relativo ao tipo, marca, modelo e versão do ECF em conformidade com o código constante em tabela publicada por meio de Despacho do Secretário Executivo do CONFAZ, ou com o código constante no Ato de Registro do ECF.

5.3.1.3 - Campo 04: Informar o CNPJ com 14 dígitos sem mascaras de edição.

5.3.1.4 - Campos 07 e 08 (Chave Pública da Assinatura Digital) No caso de ECF sem Módulo Fiscal Blindado, deixar este campo em branco, caso o mesmo não contenha recurso de assinatura digital. No caso de ECF com Módulo Fiscal Blindado este campo deve ser obrigatoriamente informado.

5.4. REGISTRO TIPO I9 - TOTALIZAÇÃO DO ARQUIVO

<table><tbody><tr><td> <p>Nº</p> </td> <td> <p>Denominação do campo</p> </td> <td> <p>Conteúdo</p> </td> <td> <p>Tamanho</p> </td> <td colspan="2"> <p>Posição</p> </td> <td> <p>Formato</p> </td> </tr><tr><td> <p>01</p> </td> <td> <p>Tipo</p> </td> <td> <p>“I9”</p> </td> <td> <p>02</p> </td> <td> <p>01</p> </td> <td> <p>02</p> </td> <td> <p>N</p> </td> </tr><tr><td> <p>02</p> </td> <td> <p>CNPJ</p> </td> <td> <p>CNPJ da empresa informante</p> </td> <td> <p>14</p> </td> <td> <p>03</p> </td> <td> <p>16</p> </td> <td> <p>N</p> </td> </tr><tr><td> <p>03</p> </td> <td> <p>Indicador de movimento</p> </td> <td> <p>“SIM” quando houver movimento ou “NÃO” quando não houver movimento</p> </td> <td> <p>03</p> </td> <td> <p>17</p> </td> <td> <p>19</p> </td> <td> <p>X</p> </td> </tr><tr><td> <p>04</p> </td> <td> <p>Total de registros tipo I2</p> </td> <td> <p>Quantidade de registros tipo I2 informados no arquivo</p> </td> <td> <p>06</p> </td> <td> <p>20</p> </td> <td> <p>25</p> </td> <td> <p>N</p> </td> </tr></tbody></table>

5.4.1 - OBSERVAÇÕES:

5.4.1.1 - Deve ser criado um único registro tipo I9 para informar o total de registros tipo I2 constantes do arquivo;

5.4.1.2 - Campo 03: Informar “SIM” quando houver senhas geradas no período e registros tipo I2 no arquivo e “NÃO” quando não houver senhas geradas no período e registros tipo I2;

5.4.1.3 - Campo 04: Informar a quantidade de registros tipo I2 constantes no arquivo. Caso não haja registros tipo I2, preencher com zeros.”

6 - ENTREGA:

6.1 - O arquivo eletrônico deverá ser validado pelo programa aplicativo “Validador ECF” disponibilizado pela Secretaria de Estado de Fazenda de Minas Gerais em seu endereço eletrônico na internet e transmitido pelo programa “TED - Transmissor Eletrônico de Documentos” disponibilizado pela Secretaria da Fazenda do Estado do Rio Grande do Sul em seu endereço eletrônico na internet, ou por meio de outro recurso de transmissão definido pela unidade federada.

6.2 - O Recibo de Entrega será emitido pelo programa transmissor TED - Transmissor Eletrônico de Documentos, quando o arquivo for por ele transmitido.

6.3 - O arquivo eletrônico será recebido condicionalmente e submetido a teste de consistência. Constatada a inobservância das especificações previstas neste Manual de Orientação, o arquivo eletrônico será devolvido ao informante para correção, sendo desconsiderada a entrega do mesmo, para os efeitos previstos na legislação vigente.

**Cláusula quarta** Este convênio entra em vigor na data da sua publicação no Diário Oficial da União, produzindo efeitos a partir do primeiro dia do segundo mês subsequente ao da publicação.
