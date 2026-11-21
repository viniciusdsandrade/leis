---
titulo: "Carta Circular nº 2.875, de 15 de outubro de 1999"
orgao: "Banco Central do Brasil"
tipo: "Carta Circular"
tipo_na_fonte: "Carta Circular"
numero: "2875"
data: 1999-10-15
ementa: "Esclarece sobre a remessa das informacoes relativas a Circular 2.894, de 27 de maio de 1999 e Carta-Circular 2.866, de 13 de agosto de 1999 - Acompanhamento da Exposicao em Ouro e em Ativos e Passivos referenciados em Variacao Cambial - Anexo II"
situacao: "revogado"
revogada: true
versao_texto: "texto mantido pelo Banco Central do Brasil no portal de normativos, com as alterações incorporadas e a redação revogada tachada quando houve alteração; não substitui a publicação no Diário Oficial da União"
fonte: "https://www.bcb.gov.br/estabilidadefinanceira/exibenormativo?tipo=Carta%20Circular&numero=2875"
fonte_texto: "https://www.bcb.gov.br/api/conteudo/app/normativos/exibenormativo?p1=Carta%20Circular&p2=2875"
sha256_fonte: "a711c243b705c0fcaa5d10ad31fc2cd116e371ebd4d91c51ce7c044a8d566d95"
baixado_em: 2026-11-20
---
# Carta Circular nº 2.875, de 15 de outubro de 1999

CARTA-CIRCULAR N. 002875

Esclarece sobre a remessa das informacoes relativas a Circular 2.894, de 27 de maio de 1999 e Carta-Circular 2.866, de 13 de agosto de 1999 - Acompanhamento da Exposicao em Ouro e em Ativos e Passivos referenciados em Variacao Cambial - Anexo II

Esclarecemos que as informacoes solicitadas no item 6 da Carta-Circular 2.866, de 13.8.1999 devem ser prestadas pelas instituicoes via Internet, na forma das instrucoes em anexo (Anexo A), mediante utilizacao do aplicativo PSTAW10 (intercambio de informacoes), de que trata a Carta-Circular 2.847, de 13 de abril de 1999, disponivel para download na Home Page do Banco Central do Brasil (http://www.bcb.gov.br), a partir de 25.10.1999.

2. Para acesso ao aplicativo PSTAW10, e indispensavel o cadastramento previo da instituicao no Sistema de Informacoes do Banco Central (SISBACEN) e o credenciamento dessa na Transacao PSTA300, cujo pedido deve ser dirigido, conforme a respectiva area de jurisdicao, a Central de Atendimento ao Publico localizada na Sede ou em Gerencia Regional do Banco Central do Brasil.

3. O documento so sera considerado aceito quando a Transacao PESP600 apresentar a mensagem "PROCESSAMENTO EFETUADO SEM ERROS".

4. As instituicoes ou conglomerados cuja exposicao consolidada exceder a 20% do PLA, deverao, excepcionalmente, encaminhar o Anexo II (Demonstrativo da Conciliacao das Posicoes em Ouro e em Ativos e Passivos referenciados em Variacao Cambial), data-base 30.9.1999, ate 29.10.1999.

5. As informacoes a serem prestadas no Anexo II por conglomerados financeiros devem se referir apenas as suas empresas financeiras.

6. A informacao a ser prestada na coluna "VALORES CONTABEIS (3)" do Anexo II da Carta-Circular 2.866 de 1999, deve se referir apenas a parcela dos valores contabeis referenciados em ouro e variacao cambial.

7. A coluna "OBS. (5)" do Anexo II da Carta-Circular 2.866, de 1999, devera ser preenchida com os codigos contidos na Tabela de Motivos de Diferencas entre as informacoes contabeis e extra- contabeis (Anexo B) e os respectivos valores explicativos dessa diferenca, caso necessario.

Brasilia, 15 de outubro de 1999.

DEPARTAMENTO DE FISCALIZACAO DEPARTAMENTO DE CADASTRO E INFORMACOES

Vanio Cesar Pickler Aguiar Lucio Ricardo Rodrigues Oliveira Chefe, em exercicio Chefe, em exercicio

DEPARTAMENTO DE INFORMATICA

Roberto Ozu Chefe

Instrucoes anexas a Carta-Circular

Anexo A

EXPOSICAO CAMBIAL

Os leiautes descritos a seguir sao utilizaveis na geracao de arquivo contendo o documento 2030 \_ EXPOSICAO CAMBIAL (Anexo II de que trata a Carta-Circular 2.866, de 13.08.1999) com as informacoes solicitadas.

O arquivo e composto por um primeiro registro de identificacao, um ou mais registros de dados e um ultimo registro de controle, cujos leiautes podem ser consultados no Sisbacen, atraves da transacao PDIC600.

Os campos numericos:

a) devem ser informados no formato decimal externo ('DISPLAY');

b) devem ser alinhados a direita e completados com zeros a esquerda;

c) os valores deverao ser informados em milhares de Reais;

d) no caso de ausencia da informacao, preencher com zeros. Os campos alfanumericos:

Devem ser alinhados a esquerda e completados com brancos a direita, excecao feita apenas aos campos de C.N.P.J., que devem ser preenchidos com zero (s) a esquerda, quando for o caso.

Eventuais duvidas poderao ser esclarecidas pelos Centros de Servicos de Informatica Regionais e, na Sede, pelo DEINF, telefone (0xx61)414-2156.

Independentemente da manutencao dos dados que deram origem as informacoes, as instituicoes devem manter, pelo prazo minimo de 30 dias, em meio magnetico, copia dos dados informados, de forma a ser possivel pronta reposicao do conteudo primitivo, caso necessario.

As instituicoes devem obter, a partir de 25/10/1999, junto as Gerencias Regionais ou por intermedio da Internet, no endereco http://www.bcb.gov.br, o programa PSTAW10, executavel em ambiente Windows 95, NT ou superior, destinado a cifragem dos dados e transferencia dos arquivos que inclui as instrucoes de instalacao e utilizacao no arquivo LEIAME.TXT.

\* EXPOSICAO CAMBIAL

REGISTRO DE IDENTIFICACAO (LESP0013)

CAMPO POSICOES PICTURE CONTEUDO DE ATE

IDENTIFICACAO 1 3 A(003) #A1 (# = VALOR HEXA '23' EM ASCII E '7B' EM EBCDIC).

CODIGO DO 4 7 N(004) FIXO '2030'. DOCUMENTO

CNPJ DA 8 15 A(008) CNPJ, COM ZEROS A ESQUERDA INSTITUICAO SE FOR O CASO.

MEIO TRANSMISSAO 16 16 A(001) FIXO 'I' (INTERNET).

DATA DE 17 22 N(006) DATA A QUE SE REFERE OS REFERENCIA DADOS \_ FORMATO AAAAMM.

CONTATO 23 52 A(030) NOME DA PESSOA A QUEM O BANCO CENTRAL IRA RECORRER SOLUCIONAR PARA EVENTUAIS PROBLEMAS RELATIVOS AS INFORMACOES PRESTADAS.

TELEFONE 53 60 N(008) TELEFONE PARA CONTATO, COM ZEROS A ESQUERDA SE FOR O CASO.

FILLER 61 285 A(225) ESPACOS EM BRANCO

SEQUENCIAL 286 288 N(003) NUMERO SEQUENCIAL DO REGISTRO. CONTERA 001.

EXPOSICAO CAMBIAL

REGISTRO DE DADOS (LESP0014) REGISTRO TIPO 1 CAMPO POSICOES PICTURE CONTEUDO DE ATE

TIPO DE REGISTRO 1 1 N(001) FIXO "1". IDENTIFICA OS DADOS DO REGISTRO: ATI- VOS, PASSIVOS E PARTICI- PACAO NO PLA.

CODIGO DA 2 8 N(007) CODIGO DA EXPOSICAO A QUE EXPOSICAO SE REFEREM OS VALORES.

EXTRA-CONTAB- 9 17 N(009) VALOR DA EXPOSICAO EM DOLAR-OURO DOLAR E OURO (SEM SINAL).

EXTRA-CONTAB- 18 26 N(009) VALOR DA EXPOSICAO NAS

DEMAIS-MOEDAS DEMAIS MOEDAS (SEM SINAL).

VALOR-CONTABIL 27 35 N(009) VALOR CONTABIL DA EXPO- SICAO (SEM SINAL).

DIFERENCA 36 44 N(009) DIFERENCA ENTRE O VALOR CONTABIL E A SOMA DOS VA- LORES EXTRA-CONTABEIS (SEM SINAL).

SINAL DA 45 45 A(001) "C" SE POSITIVA; "D" SE DIFERENCA NEGATIVA.

MOTIVO DA 46 47 N(002) CODIGO CONFORME TABELA. DIFERENCA

VALOR EXPLICATIVO 48 56 N(009) VALOR (R$ MIL) EXPLICA- TIVO DA DIFERENCA ENTRE O VALOR CONTABIL E A SOMA DOS VALORES EXTRA- CONTABEIS (SEM SINAL).

SINAL DO VALOR 57 57 A(001) "C" SE POSITIVO; "D" SE EXPLICATIVO NEGATIVO.

SEQUENCIAL 286 288 N(003) NUMERO SEQUENCIAL DO REGISTRO.

VEJA ABAIXO OBSERVACAO SOBRE AS POSICOES 58 A 285.

Obs.: O conjunto de campos MOTIVO DA DIFERENCA, VALOR EXPLICATIVO e SINAL DO VALOR EXPLICATIVO se repete mais 19 (dezenove) vezes, nessa mesma ordem, da posicao 58 ate a 285.

Havendo diferenca entre o valor contabil e a soma dos valores extra-contabeis (campo DIFERENCA), preencher este conjunto de campos (MOTIVO DA DIFERENCA, VALOR EXPLICATIVO e SINAL DO VALOR EXPLICATIVO) uma vez para cada codigo de MOTIVO DA DIFERENCA.

EXPOSICAO CAMBIAL

REGISTRO DE DADOS (LESP0014) REGISTRO TIPO 2

CAMPO POSICOES PICTURE CONTEUDO DE ATE

TIPO DE REGISTRO 1 1 N(001) FIXO "2". IDENTIFICA OS DADOS DO REGISTRO: DEMAIS POSICOES ATIVAS E PASSI- VAS.

CODIGO DA 2 8 N(007) CODIGO DA EXPOSICAO A QUE EXPOSICAO SE REFEREM OS VALORES.

EXTRA-CONTAB- 9 17 N(009) VALOR DA EXPOSICAO EM DOLAR-OURO DOLAR E OURO (SEM SINAL).

SINAL DE 18 18 A(001) "C" SE POSITIVA; "D" SE EXTRA-CONTAB- NEGATIVA. DOLAR-OURO

EXTRA-CONTAB- 19 27 N(009) VALOR DA EXPOSICAO NAS DEMAIS-MOEDAS DEMAIS MOEDAS (SEM SINAL)

SINAL DE 28 28 A(001) "C" SE POSITIVA; "D" SE EXTRA-CONTAB- NEGATIVA. DEMAIS-MOEDAS

FILLER 29 285 A(257) ESPACOS EM BRANCO

SEQUENCIAL 286 288 N(003) NUMERO SEQUENCIAL DO RE- GISTRO

EXPOSICAO CAMBIAL

REGISTRO DE CONTROLE FINAL (LESP0015)

CAMPO POSICOES PICTURE CONTEUDO DE ATE

IDENTIFICACAO 1 3 A(003) @10 ('@' = VALOR HEXA '40' EM ASCII E '7C' EM EBCDIC).

CODIGO DO 4 7 N(004) FIXO '2030'. DOCUMENTO

CNPJ DA 8 15 A(008) CNPJ, COM ZEROS A ESQUER- INSTITUICAO DA SE FOR O CASO.

TOTAL DE 16 18 N(003) TOTAL DE REGISTROS REGISTROS GRAVADOS, INCLUSIVE O DE IDENTIFICACAO E ESTE DE CONTROLE FINAL.

FILLER 19 285 A(267) ESPACOS EM BRANCO

SEQUENCIAL 286 288 N(003) NUMERO SEQUENCIAL DO RE- GISTRO. (DEVERA SER IGUAL AO TOTAL DE REGISTROS GRAVADOS)

EXPOSICAO CAMBIAL

TABELA DE CODIGOS DAS EXPOSICOES

CODIGO DESCRICAO

ATIVOS

1.00.00.00 ATIVOS 1.01.00.00 DISPONIBILIDADES 1.02.00.00 APLICACOES INTERFINANCEIRAS DE LIQUIDEZ 1.03.00.00 TITULOS E VALORES MOBILIARIOS 1.03.01.00 NO PAIS 1.03.02.00 NO EXTERIOR 1.04.00.00 RELACOES INTERFINANCEIRAS 1.05.00.00 RELACOES INTERDEPENDENCIAS 1.06.00.00 OPERACOES DE CREDITO 1.07.00.00 ARRENDAMENTO MERCANTIL 1.08.00.00 OUTROS CREDITOS 1.09.00.00 INVESTIMENTOS 1.10.00.00 IMOBILIZADO

PASSIVOS

2.00.00.00 PASSIVOS 2.01.00.00 DEPOSITOS 2.02.00.00 OBRIGACOES POR OPERACOES COMPROMISSADAS 2.03.00.00 RECURSOS DE ACEITES CAMBIAIS 2.04.00.00 RELACOES INTERFINANCEIRAS 2.05.00.00 RELACOES INTERDEPENDENCIAS 2.06.00.00 OBRIGACOES POR EMPRESTIMOS E REPASSES 2.06.01.00 NO PAIS 2.06.02.00 NO EXTERIOR 2.07.00.00 OUTRAS OBRIGACOES 2.07.01.00 NO PAIS 2.07.02.00 NO EXTERIOR 3.00.00.00 PARTICIPACAO NO PLA (ART. 7, CIRC.2894/99)

DEMAIS POSICOES ATIVAS E PASSIVAS

4.00.00.00 DEMAIS POSICOES ATIVAS E PASSIVAS 4.01.00.00 OPERACOES DE MERCADO FUTURO 4.02.00.00 OPERACOES DE SWAPS 4.03.00.00 OPERACOES NO MERCADO A TERMO 4.04.00.00 OPCOES DE COMPRA FLEXIVEIS 4.05.00.00 OPCOES DE VENDA FLEXIVEIS 4.06.00.00 OPCOES DE COMPRA PADRONIZADAS 4.07.00.00 OPCOES DE VENDA PADRONIZADAS 4.08.00.00 OPCOES DE SWAPS 4.09.00.00 OPERACOES DE COMMODITIES CAMBIAIS (FUTURO, TERMO, SWAPS E OPCOES) 4.10.00.00 CARTAS DE CREDITO 4.11.00.00 OUTRAS

Anexo B

EXPOSICAO CAMBIAL

TABELA DE MOTIVOS DE DIFERENCAS ENTRE AS INFORMACOES CONTABEIS E EXTRA-CONTABEIS

CODIGO DESCRICAO DO MOTIVO

01 USO DE MARCACAO A MERCADO 02 DATA DE COTACAO 03 UTILIZACAO DE PTAX DISTINTA 04 APROPRIACAO DE ENCARGOS 05 OPERACOES VINCENDAS EM D + 1 06 OPERACOES VINCENDAS BAIXADAS APENAS NO GERENCIAL 07 CREDITOS NAO IDENTIFICADOS 08 DEBITOS NAO IDENTIFICADOS 09 OPERACOES NAO INFORMADAS 10 OUTRAS 11 RESERVADO 12 RESERVADO 13 RESERVADO 14 RESERVADO 15 RESERVADO 16 RESERVADO 17 RESERVADO 18 RESERVADO 19 RESERVADO 20 RESERVADO
