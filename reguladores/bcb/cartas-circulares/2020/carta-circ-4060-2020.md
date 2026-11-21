---
titulo: "Carta Circular nº 4.060, de 23 de junho de 2020"
orgao: "Banco Central do Brasil"
tipo: "Carta Circular"
tipo_na_fonte: "Carta Circular"
numero: "4060"
data: 2020-06-23
ementa: "Divulga procedimentos a respeito da prestação de informações de que trata a Circular nº 3.975, de 8 de janeiro de 2020."
situacao: "revogado"
revogada: true
versao_texto: "texto mantido pelo Banco Central do Brasil no portal de normativos, com as alterações incorporadas e a redação revogada tachada quando houve alteração; não substitui a publicação no Diário Oficial da União"
publicacao: "Publicada no DOU de 26/6/2020, Seção 1, p. 27/28."
data_publicacao: "2020-06-26"
fonte: "https://www.bcb.gov.br/estabilidadefinanceira/exibenormativo?tipo=Carta%20Circular&numero=4060"
fonte_texto: "https://www.bcb.gov.br/api/conteudo/app/normativos/exibenormativo?p1=Carta%20Circular&p2=4060"
sha256_fonte: "31935d0f4983eea4eaff5675bba4ddb86ef125afbffea76b8d57efd0e7ea73f9"
baixado_em: 2026-11-20
---
# Carta Circular nº 4.060, de 23 de junho de 2020

O Chefe do Departamento de Operações Bancárias e de Sistema de Pagamentos (Deban), no uso da atribuição que lhe confere o art. 23, inciso I, alínea “a”, do Regimento Interno do Banco Central, anexo à Portaria nº 84.287, de 27 de fevereiro de 2015, e tendo em vista o disposto na Circular nº 3.975, de 8 de janeiro de 2020,

R E S O L V E :

**Art. 1º** Para a prestação de informações relativas ao recolhimento compulsório sobre depósitos de poupança de que trata a Circular nº 3.975, de 2020, as instituições devem observar os seguintes procedimentos:

I - Instituições participantes do Sistema de Transferência de Reservas (STR) com acesso principal pela Rede do Sistema Financeiro Nacional (RSFN): utilizar a RSFN; e

II - Demais instituições: utilizar o aplicativo STR-Web.

**Art. 2º** Para a prestação das informações, devem ser utilizados os seguintes códigos do Dicionário de Domínios associado ao Catálogo de Serviços do Sistema Financeiro Nacional:

I - Instituições participantes do STR com acesso principal pela RSFN: utilizar a mensagem "RCO0002 - IF informa Demonstrativo", do Grupo de Serviços RCO, constante do Catálogo de Serviços do Sistema Financeiro Nacional, preenchendo o campo "CodRCO" com o código "7- Depósitos de Poupança", observando os seguintes códigos do Dicionário de Domínios:

a) CodItem “7001 – Depósitos de Poupança Livre”;

b) CodItem “7002 – APE - Recursos de Associados Poupadores”;

c) CodItem “7005 – Depósitos de Poupança Livre a partir de 4 de maio de 2012”;

d) CodItem “7006 – APE – Recursos de Associados Poupadores a partir de 4 de maio de 2012”;

e) CodItem “7011 – Depósitos de Poupança Rural”;

f) CodItem “7015 – Depósitos de Poupança Rural a partir de 4 de maio de 2012”;

g) CodItem “7021 – Depósitos de Poupança Pecúlio”;

h) CodItem “7024 – Depósitos de Poupança Pecúlio a partir de 4 de maio de 2012”;

i) CodItem “7031 – Depósitos de Poupança Vinculada”;

j) CodItem “7032 – Depósitos Poup. Vinculada-Vinc Carta Crédito”;

k) CodItem “7016 - Saldo de operações de crédito para financiamento de capital de giro para empresas (inciso I, art. 5º-A, da Circular nº 3.975)”, contratadas a partir de 22 de junho de 2020;

l) CodItem “7017 - Saldo de aplicações em Depósitos a Prazo com Garantia Especial (DPGE) (inciso II, art. 5º-A, da Circular nº 3.975), tendo como depositária instituição que pertença ao segmento de regulação prudencial S3”, realizadas a partir de 22 de junho de 2020;

m) CodItem “7018 - Saldo de aplicações em Depósitos a Prazo com Garantia Especial (DPGE) (inciso II, art. 5º-A, da Circular nº 3.975), tendo como depositária instituição que pertença ao segmento de regulação prudencial S4”, realizadas a partir de 22 de junho de 2020;

n) CodItem “7019 - Saldo de aplicações em Depósitos a Prazo com Garantia Especial (DPGE) (inciso II, art. 5º-A, da Circular nº 3.975), tendo como depositária instituição que pertença ao segmento de regulação prudencial S5”, realizadas a partir de 22 de junho de 2020;

II - demais instituições: utilizar aplicativo STR-Web, para informar os dados previstos no inciso I.

**Parágrafo único.** Os CodItens 7016, 7017, 7018 e 7019 não devem ser informados por Associações de Poupança e Empréstimo, Sociedades de Crédito Imobiliário e/ou Cooperativas de Crédito.

**Art. 3º** Os cálculos das deduções de exigibilidade estabelecidas no art. 5º-A da Circular nº 3.975, de 2020, e, consequentemente, da exigibilidade a recolher, serão realizados conforme segue:

OpCapGiro = CodItem 7016

SomaDPGE = CodItem 7017 + CodItem 7018 + CodItem 7019

OpDPGE = Menor entre (SomaDPGE; (CodItem 7018 + CodItem 7019) / 30%)

SomaOp = OpCapGiro + OpDPGE

PLivre (proporção VSR em poupança livre) = VSRlivre/(VSRlivre+VSRRural)

PRural (proporção VSR em Poupança Rural) = VSRrural/(VSRlivre+VSRRural)

Pre\_Exigível\_L = exigibilidade poupança livre sem deduções

Pre\_Exigível\_R = exigibilidade poupança rural sem deduções

DeducLivre = Menor entre (PLivre x SomaOp; 30% Pré\_Exigível\_L)

DeducRural = Menor entre (PRural x SomaOp; 30% Pré\_Exigível\_R)

**Art. 4º** Em caso de descumprimento dos montantes mínimos, a que se refere o art. 7º, § 3º, da Circular nº 3.975, de 2020, a remuneração paga à instituição financeira será calculada segundo o disposto na fórmula constante no caput do referido artigo, sendo que, do valor da variável S, será deduzido 30% (trinta por cento) do valor da exigibilidade calculada, respectivamente, para as modalidades livre e rural.

**Art. 5º** Para cada um dos CodItens ativos em ambiente de produção desde junho de 2002, “7001 – Depósitos de Poupança Livre”, “7002 - APE – Recursos de Associados Poupadores”, “7011 - Depósitos de Poupança Rural”, “7021 - Depósitos de Poupança Pecúlio”, “7031 - Depósitos de Poupança Vinculada” e “7032 - Depósitos Poup. Vinculada-Vinc Carta”, o valor informado continua a ser o saldo, na data de referência, de todos os depósitos de poupança da respectiva modalidade, independentemente se realizados antes ou a partir de 4 de maio de 2012.

**Art. 6º** No caso de sistema cooperativo organizado em três níveis no qual a confederação não seja de crédito, o banco cooperativo responsável pela comprovação do cumprimento da exigibilidade, bem como o recolhimento e o pagamento de custos financeiros, deve contatar o Deban (Suban/SP - (11) 3491-6758) para receber as orientações quanto aos procedimentos operacionais, durante o processo de autorização para captação de que tratam as Resoluções ns. 4.716, de 25 de abril de 2019 e 4.763, de 27 de novembro de 2019.

**Art. 7º** Ficam revogadas as Cartas Circulares ns. 3.555, de 21 de maio de 2012, e 3.824, de 13 de junho de 2017.

**Art. 8º** A documentação comprobatória das informações objeto desta Carta Circular deverá ser mantida à disposição do Banco Central do Brasil pelo prazo de cinco anos, contados a partir da data a que se refere cada informação, nos termos do disposto no art. 1º da Lei nº 9.873, de 23 de novembro de 1999.

**Art. 9º** Esta Carta Circular entra em vigor na data de sua publicação, produzindo efeitos a partir do período de cálculo com início em 22 de junho de 2020 e término em 26 de junho de 2020, cujo ajuste ocorrerá em 6 de julho de 2020.

Flávio Túlio Vilela
