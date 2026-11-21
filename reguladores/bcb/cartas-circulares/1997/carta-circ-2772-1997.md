---
titulo: "Carta Circular nº 2.772, de 1º de dezembro de 1997"
orgao: "Banco Central do Brasil"
tipo: "Carta Circular"
tipo_na_fonte: "Carta Circular"
numero: "2772"
data: 1997-12-01
ementa: "Estabelece procedimentos para a remessa de informacoes e recolhimento tratados na Circular 2.789, de 28.11.97."
situacao: "revogado"
revogada: true
versao_texto: "texto mantido pelo Banco Central do Brasil no portal de normativos, com as alterações incorporadas e a redação revogada tachada quando houve alteração; não substitui a publicação no Diário Oficial da União"
fonte: "https://www.bcb.gov.br/estabilidadefinanceira/exibenormativo?tipo=Carta%20Circular&numero=2772"
fonte_texto: "https://www.bcb.gov.br/api/conteudo/app/normativos/exibenormativo?p1=Carta%20Circular&p2=2772"
sha256_fonte: "d12dec674254dafb2dada98849a5d4f462c92d299ec82ed5b6e170419e2b01b3"
baixado_em: 2026-11-20
---
# Carta Circular nº 2.772, de 1º de dezembro de 1997

CARTA-CIRCULAR N. 002772

Estabelece procedimentos para a remessa de informacoes e recolhimento tratados na Circular 2.789, de 28.11.97.

Comunicamos que as instituicoes detentoras de contas de depositos, sob qualquer titulo, nao recadastradas, objeto do arti- go 1o da Circular 2.789/97, deverao fornecer o valor consolidado des- sas contas ao Banco Central do Brasil/Departamento de Cadastro e In- formacoes (DECAD/DICON), ate as 17:00h, horario de Brasilia, do dia 02.12.97, via transacao PMSG750 do Sistema de Informacoes Banco Cen- tral (SISBACEN), sob o assunto "Circ.2789-Contas nao recad.", devendo o prestador da informacao estar identificado com o cargo e numero de telefone.

2. O referido debito na conta Reservas Bancarias do titu- lar ou da instituicao convenente sera efetuado, sempre, com data-va- lor de 02.12.97.

3. A inexistencia de recursos nas contas de depositos deve ser comunicada na mesma forma descrita no item 1, sob o assunto "Circ.2789-Inexist.saldos".

4. As informacoes citadas no artigo 2. daquela Circular devem ser entregues ate 05.12.97, de acordo com as instrucoes cons- tantes do documento anexo.

5. As instituicoes que nao cumprirem o disposto nesta Carta-Circular estarao sujeitas a multa tratada na Resolucao 2.194, de 31.08.95.

6. Eventuais duvidas serao dirimidas nos telefones (061) 414.1494, 414.2229, 414.1885 e 414.1684.

Brasilia, 1. de dezembro de 1997.

DEPARTAMENTO DE CADASTRO E INFORMACOES DEPARTAMENTO DE INFORMATICA

Sergio Almeida de Souza Lima Roberto Ozu Chefe Chefe

## ANEXO I

1. Meios Magneticos aceitos pelo Banco Central

1.1 - Cartucho modelo 3480/Fita magnetica: - Densidade de gravacao: 1600 ou 6250 bpi - Label omitido - Codificacao: EBCDIC - Tamanho do bloco: 3850 bytes (Fator de Bloco: 70) - Cada arquivo informado deve estar delimitado por um "tape mark" inicial e um "tape mark" final.

1.2 - Disquete: - Tamanho: 3 1/2" - Padrao de gravacao IBM/PC - Face dupla - Codificacao: ASCII

2. Identificacao Externa:

Os volumes magneticos devem ser entregues, contendo o arquivo gerado, nas Delegacias Regionais, com etiqueta externa contendo as seguintes informacoes:

- CGC da entidade remetente - Nome da entidade remetente - Nome do arquivo: 'AESP200' - Data da remessa - Densidade de gravacao (no caso de cartucho ou fita)

3. Leiautes de registros em meio magnetico

Os leiautes descritos a seguir sao utilizaveis na geracao de ar- quivos contendo as informacoes de que trata o paragrafo 3. do art. 1. da Medida Provisoria 1.597, de 10 de novembro de 1.997.

Nao serao admitidos arquivos com continuacao em outros volumes (multi-volume).

Cada arquivo e composto por um primeiro registro de identifica- cao, um ou mais registros de dados e um ultimo registro de controle, cujos leiautes sao descritos a seguir: 3.1. Registro de Identificacao: Campo de ate Picture Conteudo Identificacao 01 01 X(01) 'Ý' (valor hexadecimal '23' do registro em ASCII, e '7B' em EBCDIC) 02 02 X(01) 'A' (letra A) 03 03 9(01) '1' (algarismo 1) Nome do Arquivo 04 10 X(07) 'AESP200' CGC da Insti- 11 24 9(14) CGC da instituicao deposita- tuicao ria com 14 posicoes Data do Movi- 25 32 9(08) Dia, mes e ano - formato: mento DDMMAAAA Filler 33 48 X(16) Sequencial 49 55 9(07) Numero sequencial do registro Contera 0000001 no registro de identificacao.

3.2. Registros de dados: Campo de ate Picture Conteudo Agencia 01 05 X(05) Codigo da agencia deposita- ria Conta 06 20 X(15) Numero da conta de deposito Natureza da 21 21 9(01) Natureza da conta, onde: conta 1 - Deposito a Vista 3 - Deposito a Prazo 5 - Deposito de Poupanca 7 - Outros Valor recolhido 22 38 9(17) Informar o valor com ponto decimal implicito, ficando estabelecido duas casas deci- mais nas duas ultimas posi- coes Filler 39 48 X(10) Sequencial 49 55 9(07) Numero sequencial do regis- tro.

3.3. Registro de Controle Final: Campo de ate Picture Conteudo Identificacao 01 01 X(01) 'Ð' (valor hexadecimal '40' do registro em ASCII, e '7C' em EBCDIC). 02 03 9(02) '10' (algarismo 10) Nome do Arquivo 04 10 X(07) 'AESP200' CGC da Insti- 11 24 9(14) CGC da instituicao informan- tuicao te com 14 posicoes Registros gra- 25 31 9(07) Total de registros gravados vados no no arquivo, inclusive os de arquivo controle. Filler 32 48 X(17) Sequencial 49 55 9(07) Numero sequencial do regis- tro.

3.4. Preenchimento dos campos:

3.4.1. Campos numericos: - Devem ser informados no formato decimal externo ('DISPLAY'); - Devem se alinhados a direita e completados com zeros a esqueda; - No caso de valores que compreendem uma parte fracionaria, o ponto decimal e implicito, ficando estabelecido duas casas deci mais nas duas ultimas posicoes; - No caso de ausencia da informacao, preencher com zeros.

3.4.2. Campos alfanumericos: - Devem ser alinhados a esquerda e completados com brancos a direita; - No caso de ausencia da informacao, preencher com brancos.

4. Observacoes:

4.1. A entidade remetente deve manter, pelo prazo minimo de trinta dias, copia do meio magnetico remetido ao Banco Central, de forma a ser possivel pronta reposicao do conteudo primitivo, caso necessario.

4.2. Eventuais duvidas poderao ser esclarecidas pelos Centros de Ser- vicos de Informatica Regionais e, na Sede, pela Divisao de Operacao do Departamento de Informatica (DEINF/DIVOP), Telefone (061) 414-2157.
