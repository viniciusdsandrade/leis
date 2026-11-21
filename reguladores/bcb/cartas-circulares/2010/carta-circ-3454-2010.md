---
titulo: "Carta Circular nº 3.454, de 14 de junho de 2010"
orgao: "Banco Central do Brasil"
tipo: "Carta Circular"
tipo_na_fonte: "Carta Circular"
numero: "3454"
data: 2010-06-14
ementa: "Divulga leiaute das informações de que trata a Circular nº 3.290, de 5 de setembro de 2005."
revogada: false
versao_texto: "texto mantido pelo Banco Central do Brasil no portal de normativos, com as alterações incorporadas e a redação revogada tachada quando houve alteração; não substitui a publicação no Diário Oficial da União"
fonte: "https://www.bcb.gov.br/estabilidadefinanceira/exibenormativo?tipo=Carta%20Circular&numero=3454"
fonte_texto: "https://www.bcb.gov.br/api/conteudo/app/normativos/exibenormativo?p1=Carta%20Circular&p2=3454"
sha256_fonte: "73299a4f630a02bd4c9588bff1a8c289c309dc3d0c497e567b63492409213a93"
baixado_em: 2026-11-20
---
# Carta Circular nº 3.454, de 14 de junho de 2010

CARTA-CIRCULAR N. 003454

Divulga leiaute das informações de que trata a Circular nº 3.290, de 5 de setembro de 2005.

Em conformidade com o contido no parágrafo único do artigo 5º da Circular nº 3.290, de 5 de setembro de 2005, divulgamos leiaute a ser adotado para prestação de informações às autoridades competentes, quando solicitadas, observadas as disposições da Circular nº 3.461, de 24 de julho de 2009.

2. As informações devem ser prestadas em cinco arquivos eletrônicos, denominados:

I - "AGENCIAS": deve conter os dados das agências da instituição financeira mantenedoras das contas investigadas, das agências mantenedoras das contas com as quais foram realizadas transações e das agências nas quais ocorreram as transações entre as citadas contas;

II - "CONTAS": deve identificar as contas bancárias que tiveram o sigilo bancário afastado nos termos da Lei Complementar nº 105, de 10 de janeiro de 2001, abrangendo as contas bancárias investigadas e aquelas com as quais foram realizadas transações;

III - "TITULARES": deve identificar as pessoas, naturais ou jurídicas, titulares, representantes legais e procuradores das contas bancárias que tiveram o sigilo bancário afastado nos termos da Lei Complementar nº 105, de 2001, abrangendo as contas bancárias investigadas e aquelas com as quais foram realizadas transações;

IV - "EXTRATO": deve identificar os lançamentos relacionados às contas investigadas; e

V - "ORIGEM\_DESTINO": deve identificar a(s) origem(ns) ou o(s) destino(s) de recursos relacionados a um lançamento informado no arquivo "EXTRATO".

3. O arquivo "AGENCIAS" deve ser composto pelos campos descritos a seguir:

I - campo "NUMERO\_BANCO":

a) tipo: numérico;

b) tamanho: 3 caracteres;

c) descrição: código COMPE da instituição financeira;

II - campo "NUMERO\_AGENCIA":

a) tipo: numérico;

b) tamanho: 4 caracteres;

c) descrição: número da agência sem dígito verificador;

III - campo "NOME\_AGENCIA":

a) tipo: texto;

b) tamanho: 50 caracteres;

c) descrição: nome da agência;

IV - campo "ENDERECO\_LOGRADOURO":

a) tipo: texto;

b) tamanho: 80 caracteres;

c) descrição: endereço e complemento da agência;

V - campo "ENDERECO\_CIDADE":

a) tipo: texto;

b) tamanho: 40 caracteres;

c) descrição: nome da cidade em que a agência está situada;

VI - campo "ENDERECO\_UF":

a) tipo: texto;

b) tamanho: 2 caracteres;

c) descrição: sigla da Unidade da Federação em que a agência está situada;

VII - campo "ENDERECO\_PAIS":

a) tipo: texto;

b) tamanho: 40 caracteres;

c) descrição: nome do país em que a agência está situada;

VIII - campo "ENDERECO\_CEP":

a) tipo: texto;

b) tamanho: 8 caracteres;

c) descrição: CEP da agência no formato 99999999;

IX - campo "TELEFONE\_AGENCIA":

a) tipo: texto;

b) tamanho: 20 caracteres;

c) descrição: número de telefone da agência;

X - campo "DATA\_ABERTURA\_AGENCIA":

a) tipo: data;

b) tamanho: 8 caracteres;

c) descrição: data de abertura da agência;

XI - campo "DATA\_FECHAMENTO\_AGENCIA":

a) tipo: data;

b) tamanho: 8 caracteres;

c) descrição: data de fechamento da agência.

4. O arquivo "CONTAS" deve ser composto pelos campos descritos a seguir:

I - campo "NUMERO\_BANCO":

a) tipo: numérico;

b) tamanho: 3 caracteres;

c) descrição: código COMPE da instituição financeira;

II - campo "NUMERO\_AGENCIA":

a) tipo: numérico;

b) tamanho: 4 caracteres;

c) descrição: número da agência sem dígito verificador;

III - campo "NUMERO\_CONTA":

a) tipo: texto;

b) tamanho: 20 caracteres;

c) descrição: número da conta com o dígito verificador. Não usar separadores, tais como ponto, barra, traço ou outro caractere de formatação;

IV - campo "TIPO\_CONTA":

a) tipo: numérico;

b) tamanho: 1 caractere;

c) descrição: utilizar os seguintes códigos: "1" para conta corrente, "2" para conta de poupança, "3" para conta investimento, "4" para outros casos;

V - campo "DATA\_ABERTURA\_CONTA":

a) tipo: data;

b) tamanho: 8 caracteres;

c) descrição: data de abertura da conta;

VI - campo "DATA\_ENCERRAMENTO\_CONTA":

a) tipo: data;

b) tamanho: 8 caracteres;

c) descrição: data de encerramento da conta;

VII - campo "MOVIMENTACAO\_CONTA":

a) tipo: numérico;

b) tamanho: 1 caractere;

c) descrição: utilizar os seguintes códigos: "1" para conta investigada com movimentação bancária no período de afastamento do sigilo bancário, "2" para conta investigada sem movimentação no período, "3" quando tratar-se de conta da mesma instituição financeira que efetuou transação bancária com uma conta investigada.

5. O arquivo "TITULARES" deve ser composto pelos campos descritos a seguir:

I - campo "NUMERO\_BANCO":

a) tipo: numérico;

b) tamanho: 3 caracteres;

c) descrição: código COMPE da instituição financeira;

II - campo "NUMERO\_AGENCIA":

a) tipo: numérico;

b) tamanho: 4 caracteres;

c) descrição: número da agência sem dígito verificador;

III - campo "NUMERO\_CONTA":

a) tipo: texto;

b) tamanho: 20 caracteres;

c) descrição: número da conta com o dígito verificador;

IV - campo "TIPO\_CONTA":

a) tipo: numérico;

b) tamanho: 1 caractere;

c) descrição: utilizar os seguintes códigos: "1" para conta corrente, "2" para conta de poupança, "3" para conta investimento, "4" para outros casos;

V - campo "TIPO\_TITULAR":

a) tipo: texto;

b) tamanho: 1 caractere;

c) descrição: informa o tipo de vínculo na conta: utilizar "T" para o titular, "1" para o primeiro cotitular, "2" para o segundo cotitular e assim consecutivamente; ou "R" para representante, "L" para representante legal, "P" para procurador, "O" para outros;

VI - campo "PESSOA\_INVESTIGADA":

a) tipo: numérico;

b) tamanho: 1 caractere;

c) descrição: indica se a pessoa, natural ou jurídica, teve ou não o sigilo bancário afastado (conforme determinação judicial). Utilizar "0" se não teve o sigilo afastado ou "1" se teve o sigilo afastado;

VII - campo "TIPO\_PESSOA\_TITULAR":

a) tipo: numérico;

b) tamanho: 1 caractere;

c) descrição: indica se é pessoa natural ou jurídica. Utilizar "1" para pessoa natural ou "2" para pessoa jurídica;

VIII - campo "CPF\_CNPJ\_TITULAR":

a) tipo: texto;

b) tamanho: 14 caracteres;

c) descrição: número da inscrição no Cadastro de Pessoas Físicas (CPF) ou no Cadastro Nacional da Pessoa Jurídica (CNPJ), de acordo com o TIPO\_PESSOA\_TITULAR. Utilizar somente números, sem separadores;

IX - campo "NOME\_TITULAR":

a) tipo: texto;

b) tamanho: 80 caracteres;

c) descrição: nome completo da pessoa;

X - campo "NOME\_DOC\_IDENTIFICACAO":

a) tipo: texto;

b) tamanho: 50 caracteres;

c) descrição: nome informado no documento de identificação, que não seja CPF ou CNPJ. Exemplos: RG, Carteira de Trabalho, Identidade Funcional, qualquer documento que constitua a pessoa jurídica;

XI - campo "NUMERO\_DOC\_IDENTIFICACAO":

a) tipo: texto;

b) tamanho: 20 caracteres;

c) descrição: número e complemento do documento de identificação, conforme registrado pela instituição financeira, podendo conter formatação. Exemplos: RG 123456 SSP/DF, OAB 1234-DF;

XII - campo "ENDERECO\_LOGRADOURO":

a) tipo: texto;

b) tamanho: 80 caracteres;

c) descrição: endereço de domicílio da pessoa e complemento;

XIII - campo "ENDERECO\_CIDADE":

a) tipo: texto;

b) tamanho: 40 caracteres;

c) descrição: nome da cidade de domicílio da pessoa;

XIV - campo "ENDERECO\_UF":

a) tipo: texto;

b) tamanho: 2 caracteres;

c) descrição: sigla da Unidade da Federação de domicílio da pessoa;

XV - campo "ENDERECO\_PAIS":

a) tipo: texto;

b) tamanho: 40 caracteres;

c) descrição: nome do país de domicílio da pessoa;

XVI - campo "ENDERECO\_CEP":

a) tipo: texto;

b) tamanho: 8 caracteres;

c) descrição CEP da pessoa no formato 99999999;

XVII - campo "TELEFONE\_PESSOA":

a) tipo: texto;

b) tamanho: 20 caracteres;

c) descrição: número de telefone da pessoa;

XVIII - campo "VALOR\_RENDA":

a) tipo: numérico;

b) tamanho: 14 caracteres;

c) descrição: valor da renda declarada pelo correntista à instituição financeira;

XIX - campo "DATA\_ATUALIZACAO\_RENDA":

a) tipo: data;

b) tamanho: 8 caracteres;

c) descrição: data da última atualização do valor da renda declarada pelo correntista à instituição financeira;

XX - campo DATA\_INICIO\_RELACIONAMENTO\_CONTA

a) tipo: data;

b) tamanho: 8 caracteres;

c) descrição: data de início de relacionamento com a conta;

XXI - campo DATA\_FIM\_RELACIONAMENTO\_CONTA

a) tipo: data;

b) tamanho: 8 caracteres;

c) descrição: data de fim de relacionamento com a conta.

6. O arquivo "EXTRATO" deve ser composto pelos campos descritos a seguir:

I - campo "CODIGO\_CHAVE\_EXTRATO":

a) tipo: numérico;

b) tamanho: 18 caracteres;

c) descrição: número sequencial gerado pela instituição financeira para identificação dos lançamentos. Este código não pode ser repetido neste arquivo, portanto, individualiza e vincula cada registro do arquivo "EXTRATO" aos seus correspondentes registros no arquivo "ORIGEM\_DESTINO";

II - campo "NUMERO\_BANCO":

a) tipo: numérico;

b) tamanho: 3 caracteres;

c) descrição: código COMPE da instituição financeira na qual o investigado possui conta;

III - campo "NUMERO\_AGENCIA":

a) tipo: numérico;

b) tamanho: 4 caracteres;

c) descrição: número da agência, sem dígito verificador, na qual o investigado possui conta;

IV - campo "NUMERO\_CONTA":

a) tipo: texto;

b) tamanho: 20 caracteres;

c) descrição: número da conta investigada com o dígito verificador;

V - campo "TIPO\_CONTA":

a) tipo: numérico;

b) tamanho: 1 caractere;

c) descrição: utilizar os seguintes códigos: "1" para conta corrente, "2" para conta de poupança, "3" para conta investimento,"4" para outros casos;

VI - campo "DATA\_LANCAMENTO":

a) tipo: data;

b) tamanho: 8 caracteres;

c) descrição: data em que foi realizado o lançamento;

VII - campo "NUMERO\_DOCUMENTO":

a) tipo: texto;

b) tamanho: 20 caracteres;

c) descrição: código do documento utilizado pela instituição financeira para identificar o lançamento;

VIII - campo "DESCRICAO\_LANCAMENTO":

a) tipo: texto;

b) tamanho: 50 caracteres;

c) descrição: histórico da transação, descrição do tipo de lançamento realizado;

IX - campo "TIPO\_LANCAMENTO":

a) tipo: numérico;

b) tamanho: 3 caracteres;

c) descrição: preencher com o código do tipo da transação, conforme Anexo desta carta-circular;

X - campo "VALOR\_LANCAMENTO":

a) tipo: numérico;

b) tamanho: 14 caracteres;

c) descrição: valor do lançamento;

XI - campo "NATUREZA\_LANCAMENTO":

a) tipo: texto;

b) tamanho: 1 caractere;

c) descrição: informar natureza do lançamento: "C" para Crédito, "D" para Débito, sinal asterisco "\*" para Outros (Exemplos: bloqueios, provisões, lançamentos futuros);

XII - campo "VALOR\_SALDO":

a) tipo: numérico;

b) tamanho: 14 caracteres;

c) descrição: valor do saldo da conta após o lançamento;

XIII - campo "NATUREZA\_SALDO":

a) tipo: texto;

b) tamanho: 1 caractere;

c) descrição: informar a natureza do saldo:"C" para Credor, "D" para Devedor;

XIV - campo "LOCAL\_TRANSACAO":

a) tipo: texto;

b) tamanho: 80 caracteres;

c) descrição: local de realização da transação (Agência, Caixa Eletrônico, PAB, Loja, Mercado, etc.). Dados: Nome do Local - Cidade/UF e qualquer outra referência de localização. As transações realizadas em pontos virtuais (internet banking, internet de celular) podem ser identificadas com o texto "Internet". As transações realizadas por telefone podem ser identificadas com o texto "Telefone". Exemplos: Extra 3422 - Brasília/DF; Agência Cruzeiro - Vitória/ES; PAB Infraero Aeroporto - Brasília/DF; Internet; Telefone.

7. O arquivo "ORIGEM\_DESTINO" deve ser composto pelos campos descritos a seguir:

I - campo "CODIGO\_CHAVE\_OD":

a) tipo: numérico;

b) tamanho: 18 caracteres;

c) descrição: número sequencial gerado pela instituição financeira para identificação dos registros de ORIGEM\_DESTINO. Este código não pode ser repetido no ar- quivo;

II - campo "CODIGO\_CHAVE\_EXTRATO":

a) tipo: numérico;

b) tamanho: 18 caracteres;

c) descrição: código relacionado ao campo "CODIGO\_CHAVE\_EXTRATO" no arquivo EXTRATO. Para cada registro no arquivo "EXTRATO" sempre haverá um ou mais registros correspondentes no arquivo "ORIGEM\_DESTINO";

III - campo "VALOR\_TRANSACAO":

a) tipo: numérico;

b) tamanho: 14 caracteres;

c) descrição: valor individual de cada documento da transa- ção;

IV - campo "NUMERO\_DOCUMENTO\_TRANSACAO":

a) tipo: texto;

b) tamanho: 20 caracteres;

c) descrição: número do documento usado pela instituição financeira para identificar a transação;

V - campo "NUMERO\_BANCO\_OD":

a) tipo: número;

b) tamanho: 3 caracteres;

c) descrição: código COMPE da instituição financeira que enviou ou recebeu recursos da conta investigada;

VI - campo "NUMERO\_AGENCIA\_OD":

a) tipo: número;

b) tamanho: 4 caracteres;

c) descrição: número da agência, sem dígito verificador, que enviou ou recebeu recursos da conta investigada;

VII - campo "NUMERO\_CONTA\_OD":

a) tipo: texto;

b) tamanho: 20 caracteres;

c) descrição: número, com o dígito verificador, da conta que enviou ou recebeu recursos da conta investigada;

VIII - campo "TIPO\_CONTA\_OD":

a) tipo: número;

b) tamanho: 1 caractere;

c) descrição: utilizar os seguintes códigos: "1" para conta corrente, "2" para conta de poupança, "3" para conta investimento, "4" para outros casos;

IX - campo "TIPO\_PESSOA\_OD":

a) tipo: número;

b) tamanho: 1 caractere;

c) descrição: utilizar os seguintes códigos para o tipo de pessoa que participou da transação como ordenante ou como beneficiária de recursos: "1" para Natural, "2" para Jurídica;

X - campo "CPF\_CNPJ\_OD":

a) tipo: texto;

b) tamanho: 14 caracteres;

c) descrição: número do CPF ou CNPJ da pessoa que efetuou a transação como ordenante ou como beneficiária de recursos. Nos casos de endosso, preencher o CPF/CNPJ do beneficiário final que recebeu o cheque endossado (endossatário), constante no verso do cheque;

XI - campo "NOME\_PESSOA\_OD":

a) tipo: texto;

b) tamanho: 80 caracteres;

c) descrição: nome da pessoa que efetuou a transação com o investigado, como ordenante ou como beneficiária final de recursos. Nos casos de endosso, preencher o nome do beneficiário final que recebeu o cheque endossado (endossatário), constante no verso do cheque;

XII - campo "NOME\_DOC\_IDENTIFICACAO\_OD":

a) tipo: texto;

b) tamanho: 50 caracteres;

c) descrição: nome do documento de identificação do ordenante ou beneficiário final usado na transação, que não seja CPF. Exemplos: RG, Carteira de Trabalho, Identidade Funcional, entre outros;

XIII - campo "NUMERO\_DOC\_IDENTIFICACAO\_OD":

a) tipo: texto;

b) tamanho: 20 caracteres;

c) descrição: número e complemento do documento de identificação do ordenante ou beneficiário final conforme registrado pela instituição financeira, podendo conter caractere de formatação. Exemplos: RG 123456 SSP/DF, OAB 1234-DF;

XIV - campo "CODIGO\_DE\_BARRAS":

a) tipo: texto;

b) tamanho: 100 caracteres;

c) descrição: números que compõem o código de barras (incluindo o DV) de um documento de compensação (boleto). Devem ser usados caracteres de separação, tais como ponto, barra, traço ou outro caractere de formatação;

XV - campo "NOME\_ENDOSSANTE\_CHEQUE":

a) tipo: texto;

b) tamanho: 80 caracteres;

c) descrição: nos casos de endosso, neste campo deve constar o nome da pessoa natural ou jurídica para quem o cheque foi nominado, localizado no anverso do documento, ou seja, o emissor do endosso (endossante);

XVI - campo "DOC\_ENDOSSANTE\_CHEQUE":

a) tipo: texto;

b) tamanho: 50 caracteres;

c) descrição: nome, número e complemento do documento de identificação da pessoa natural ou jurídica para quem o cheque foi nominado,localizado no anverso do documento, ou seja, o emissor do endosso (endossante) usado na transação. Exemplos: CPF 99999999999, RG 123456 SSP/DF, OAB 1234-DF, Identidade Funcional 123456, etc;

XVII - campo "SITUACAO\_IDENTIFICACAO":

a) tipo: numérico;

b) tamanho: 1 caractere;

c) descrição: informar o valor fixo "0" (zero);

XVIII - campo "OBSERVACAO":

a) tipo: texto;

b) tamanho: 250 caracteres;

c) descrição: outras informações importantes, como por exemplo, "saque em espécie", "saque na boca do caixa", "distribuição de depósito em contas distintas", entre outras.

8. Os arquivos devem ser preparados em formato texto (extensão ".txt"), padrão ASCII, para utilização em microcomputadores do tipo PC, observadas as seguintes instruções:

I - não deve ser gerado cabeçalho;

II - como separador de coluna, usar o caractere de tabulação , e como separador de linha, usar o caractere de "retorno de carro" ;

III - no caso de ausência de informação, os campos vazios devem ser deixados em branco, ou seja, não preencher com espaços ou zeros;

IV - os campos do tipo texto devem ser alinhados à esquerda. Caso o conteúdo do dado seja menor que o tamanho máximo da coluna, os caracteres restantes não devem ser preenchidos com espaços;

V - para os campos do tipo data, usar o formato ddmmaaaa, sem separadores. Exemplo: 05/02/2008 = 05022008; e

VI - os campos do tipo numérico devem conter apenas números, sem formatação (pontos, traços, barras, vírgula, entre outros). Quando o conteúdo desses campos for um valor monetário, deve sempre ser informado até a segunda casa decimal. Não é necessário informar zeros à esquerda. Exemplos: 100,00 informar 10000; 10.023,03 informar 1002303; 0,00 informar 000.

9. As instituições financeiras devem estar aptas para o fornecimento das informações nas condições ora divulgadas, no prazo de até 120 (cento e vinte) dias a partir da data de publicação desta carta-circular.

10. Devem ser observados os prazos e as formas de atendimento e de encaminhamento das informações estabelecidos pela autoridade requerente. Eventuais alterações serão tratadas diretamente entre a instituição financeira e a autoridade requerente.

11. As instituições financeiras poderão utilizar sistemas de informática integrados de validação, transmissão, recepção e controle de atendimento das informações previstas nesta carta-circular, observados os requisitos de segurança.

12. Esta carta-circular entra em vigor na data de sua publica- ção.

13. Fica revogada a Carta-Circular nº 3.254, de 8 de dezembro de 2006.

Brasília, 14 de junho de 2010.

Departamento de Prevenção a Ilícitos Financeiros e de Atendimento de Demandas de Informações do Sistema Financeiro

Ricardo Liáo Chefe

Anexo à Carta-Circular nº 3.454, de 14 de junho de 2010

Lista os códigos para preenchimento do campo "TIPO\_LANCAMENTO":

1. Para lançamentos a débito, informar:

- 101 para cheques;

- 102 para encargos;

- 103 para estornos;

- 104 para lançamento avisado;

- 105 para tarifas;

- 106 para aplicação;

- 107 para empréstimo/financiamento;

- 108 para câmbio;

- 109 para CPMF;

- 110 para IOF;

- 111 para imposto de renda;

- 112 para pagamento fornecedores;

- 113 para pagamento salário;

- 114 para saque eletrônico;

- 115 para ações;

- 117 para transferência entre contas;

- 118 para devolução da compensação;

- 119 para devolução de cheque depositado;

- 120 para transferência interbancária (DOC, TED);

- 121 para antecipação a fornecedores; e

- 122 para OC/AEROPS;

2. Para lançamentos a crédito, informar:

- 201 para depósitos;

- 202 para líquido de cobrança;

- 203 para devolução de cheques;

- 204 para estornos;

- 205 para lançamento avisado;

- 206 para resgate de aplicação;

- 207 para empréstimo/financiamento;

- 208 para câmbio;

- 209 para transferência interbancária (DOC, TED);

- 210 para ações;

- 211 para dividendos;

- 212 para seguro;

- 213 para transferência entre contas;

- 214 para depósitos especiais;

- 215 para devolução da compensação;

- 216 para OCT;

- 217 para pagamento de fornecedores;

- 218 para pagamentos diversos; e

- 219 para pagamentos salariais
