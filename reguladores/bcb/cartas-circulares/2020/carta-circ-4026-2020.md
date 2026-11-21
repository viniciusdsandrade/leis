---
titulo: "Carta Circular nº 4.026, de 14 de abril de 2020"
orgao: "Banco Central do Brasil"
tipo: "Carta Circular"
tipo_na_fonte: "Carta Circular"
numero: "4026"
data: 2020-04-14
ementa: "Divulga procedimentos a respeito de informações relativas ao recolhimento compulsório sobre recursos a prazo de que trata a Circular nº 3.916, de 22 de novembro de 2018."
situacao: "revogado"
revogada: true
versao_texto: "texto mantido pelo Banco Central do Brasil no portal de normativos, com as alterações incorporadas e a redação revogada tachada quando houve alteração; não substitui a publicação no Diário Oficial da União"
publicacao: "Publicada no DOU de 15/4/2020, Seção 1, p. 41."
data_publicacao: "2020-04-15"
fonte: "https://www.bcb.gov.br/estabilidadefinanceira/exibenormativo?tipo=Carta%20Circular&numero=4026"
fonte_texto: "https://www.bcb.gov.br/api/conteudo/app/normativos/exibenormativo?p1=Carta%20Circular&p2=4026"
sha256_fonte: "3bdcb76b15fc45891ec7a93c5c656e04686b8c0b351778d19f9874054d0351ea"
baixado_em: 2026-11-20
---
# Carta Circular nº 4.026, de 14 de abril de 2020

O Chefe do Departamento de Operações Bancárias e de Sistema de Pagamentos (Deban), no uso da atribuição que lhe confere o art. 23, inciso I, alínea “a”, do Regimento Interno do Banco Central do Brasil, anexo à Portaria nº 84.287, de 27 de fevereiro de 2015, e tendo em vista o disposto nos arts. 5º-B, 5º-C e 5º-D da Circular nº 3.916, de 22 de novembro de 2018,

R E S O L V E :

**Art. 1º** Para a prestação de informações relativas ao recolhimento compulsório sobre recursos a prazo, de que trata a Circular nº 3.916, de 2018, as instituições devem observar os seguintes procedimentos:

I – Instituições participantes do Sistema de Transferência de Reservas (STR) com acesso principal pela Rede do Sistema Financeiro Nacional (RSFN): utilizar a RSFN; e

II – Demais instituições: utilizar o aplicativo STR-Web.

**Art. 2º** Para a prestação das informações, devem ser utilizados os seguintes códigos do Dicionário de Domínios associado ao Catálogo de Serviços do Sistema Financeiro Nacional:

I- Instituições participantes do STR com acesso principal pela RSFN: utilizar a mensagem "RCO0002 - IF informa Demonstrativo", do Grupo de Serviços RCO, constante do Catálogo de Serviços do Sistema Financeiro Nacional, preenchendo o campo "CodRCO" com o código "9- Recursos a Prazo", observando os seguintes códigos do Dicionário de Domínios:

a) CodItem 9001 - saldo total da rubrica "4.1.5.10.00-9 Depósitos a Prazo", do Cosif (inciso V, art. 2º, da Circular nº 3.916);

b) CodItem 9002- saldo total da rubrica "4.3.1.00.00-8 Recursos de Aceites Cambiais", do Cosif (inciso VI, art. 2º, da Circular nº 3.916);

c) CodItem 9003 - saldo total da rubrica "4.3.4.50.00-2 Cédulas Pignoratícias de Debêntures", do Cosif (inciso VII, art. 2º, da Circular nº 3.916);

d) CodItem 9004 - saldo total da rubrica "4.2.1.10.80-0 Títulos de Emissão Própria", do Cosif (inciso VIII, art. 2º, da Circular nº 3.916);

e) CodItem 9005 - saldo total da rubrica "4.9.9.12.20-7 Contratos de Assunção de Obrigações - Vinculados a Operações Realizadas no Exterior", do Cosif (inciso IX, art.2º, da Circular nº 3.916);

f) CodItem 9024 – saldo total de depósitos a prazo resultantes de operações de assistência ou de suporte financeiro contratadas com fundos ou outros mecanismos constituídos pelas instituições do Sistema Financeiro Nacional na forma do § 1º do art. 28 da Lei Complementar nº 101, de 4 de maio de 2000, inclusive com aqueles de que trata o art. 12, inciso IV, da Lei Complementar nº 130, de 17 de abril de 2009;

g) CodItem 9025 - Saldo devedor atualizado dos financiamentos concedidos no âmbito do Programa Emergencial de Suporte a Empregos, de que trata o artigo 5-A da Circular 3.916, de 22 de novembro de 2018;

h) CodItem 9026 - Saldo de Letras Financeiras de emissão própria recompradas pela instituição financeira emissora, de que trata o caput do artigo 5-B da Circular 3.916, de 2018, e que atendam ao disposto no §7º do mesmo artigo; e

i) CodItem 9027 – valor total das debêntures adquiridas pela instituição financeira de que trata o § 4º do artigo 5-B da Circular 3.916, de 2018;

II - demais instituições: utilizar aplicativo STR-Web, para informar os dados previstos no inciso I.

**§ 1º** Para os CodItens 9025, 9026 e 9027 somente o valor informado referente ao último dia útil do período de cálculo será considerado no cálculo da dedução no período de movimentação correspondente.

**§ 2º** Os valores informados nos Coditens 9026 e 9027 devem corresponder ao efetivamente pago na aquisição ou recompra dos ativos, enquanto de posse dos mesmos.

**Art. 3º** O saldo bloqueado do recolhimento compulsório sobre recursos a prazo a que se referem os arts. 5º-A e 5º-B da Circular nº 3.916, de 2018, utilizado para a aplicação dos limites de dedução, corresponde ao do final do último dia útil do período de cálculo.

**Art. 4º** Os cálculos das deduções de exigibilidade estabelecidas nos arts. 5º-A e 5º-B da Circular nº 3.916, de 2018, e consequente da exigibilidade a recolher, serão realizados conforme segue:

DeducFopa = Menor valor entre (Pre\_Exigível – DeducPR1 – SBLTEL; 15% x CodItem 9025)

DeducLF = Menor valor entre (CodItem 9026; CodItem 9027; Pre\_Exigível – DeducPR1 – DeducFopa – SBLTEL; 15% x (Pre\_Exigível – DeducPR1 – DeducFopa); Maior entre (0; 30% x (Pre\_Exigível – DeducPR1 – DeducFopa) – SBLTEL))

Exigibilidade a Recolher= Pre-Exigível – DeducPR1 – DeducFopa – DeducLF

Em que:

Pre\_Exigível = exigibilidade sem deduções, conforme artº 4º da Circular 3.916, de 2018;

SBLTEL = saldo bloqueado em garantia de operações da Linha Temporária Especial de Liquidez (LTEL-Debêntures) em recolhimento compulsório sobre recursos a prazo no último dia do período de cálculo;

DeducPR1 = dedução estabelecida no art. 5º da Circular 3.916, de 2018;

DeducFopa = dedução utilizada do Programa Emergencial de Suporte a Emprego, estabelecida no art. 5º A da Circular 3.916, de 2018;

DeducLF = dedução utilizada de Letras Financeiras de emissão própria recompradas, estabelecida no art. 5ºB da Circular 3.916, de 2018.

**Art. 5º** A partir do período de cálculo com início em 4 de maio de 2020, a dedução de Letras Financeiras de emissão própria recompradas deve observar o que está estabelecido nos arts. 5º-C e 5º-D da Circular nº 3.916, de 2018, sem mais necessidade da prestação das informações relativas aos CodItens 9026 e 9027.

**Art. 6º** A documentação comprobatória das informações objeto desta Carta Circular, salvo disposição em contrário, deverá ser mantida à disposição do Banco Central do Brasil pelo prazo de cinco anos, contados a partir da data a que se refere cada informação, nos termos do disposto no art. 1º da Lei nº 9.873, de 23 de novembro de 1999.

**Art. 7º** Fica revogada a Carta Circular 4.021, de 7 de abril de 2020.

**Art. 8º** Esta Carta Circular entra em vigor na data de sua publicação, produzindo efeitos a partir do período de cálculo de 13 a 17 de abril de 2020, cujo ajuste ocorrerá em 27 de abril de 2020.

Flávio Túlio Vilela
