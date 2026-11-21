---
titulo: "Carta Circular nº 3.829, de 30 de junho de 2017"
orgao: "Banco Central do Brasil"
tipo: "Carta Circular"
tipo_na_fonte: "Carta Circular"
numero: "3829"
data: 2017-06-30
ementa: "Altera o MCR - Documento 5-A, que trata do Sistema de Operações do Crédito Rural e do Proagro (Sicor)."
situacao: "revogado"
revogada: true
versao_texto: "texto mantido pelo Banco Central do Brasil no portal de normativos, com as alterações incorporadas e a redação revogada tachada quando houve alteração; não substitui a publicação no Diário Oficial da União"
publicacao: "Publicada no DOU de 3/7/2017, Seção 1, p. 13/14."
data_publicacao: "2017-07-03"
fonte: "https://www.bcb.gov.br/estabilidadefinanceira/exibenormativo?tipo=Carta%20Circular&numero=3829"
fonte_texto: "https://www.bcb.gov.br/api/conteudo/app/normativos/exibenormativo?p1=Carta%20Circular&p2=3829"
sha256_fonte: "a6c6fa28fe8c827b0c1426d9c4620a6891d39f293c37a7fc3d891fc0347fde37"
baixado_em: 2026-11-20
---
# Carta Circular nº 3.829, de 30 de junho de 2017

O Chefe do Departamento de Regulação, Supervisão e Controle das Operações do Crédito Rural e do Proagro (Derop), no uso das atribuições que lhe conferem o art. 23, inciso I, alínea “a”, do Regimento Interno do Banco Central do Brasil, anexo à Portaria nº 84.287, de 27 de fevereiro de 2015, e o art. 3º da Circular nº 3.620, de 21 de dezembro de 2012, e tendo em vista as disposições do Item 5 da Seção 5-A do Capítulo 3 do Manual de Crédito Rural (MCR),

R E S O L V E:

**Art. 1º** O item 14 da Seção Condições Gerais do MCR - Documento 5-A (Sistema de Operações do Crédito Rural e do Proagro - Sicor) passa a vigorar com a seguinte redação:

“14 - As mensagens do Sicor (grupo de serviços COR) estão assim divididas:

a) “COR0001 - instituição financeira requisita inclusão ou alteração de Instrumento de Crédito Rural” (operação) no Sicor;

b) “COR0002 - instituição financeira requisita exclusão de Instrumento de Crédito Rural” (operação) já cadastrado no Sicor;

c) “COR0003 - instituição financeira consulta Instrumento de Crédito Rural” (operação) no Sicor;

d) “COR0004” - IF requisita alteração na composição das destinações de financiamento de uma Cédula;

e) “COR0005”: instituição pode alterar/incluir informações em destinações de financiamento como complemento à COR0001;

f) “COR0001R1 - Sicor informa a inclusão ou a alteração do Instrumento de Crédito Rural” (operação) no Sicor;

g) “COR0002R1 - Sicor informa a exclusão do Instrumento de Crédito Rural” (operação) já cadastrado no Sicor;

h) “COR0003R1 - Sicor informa o resultado da consulta solicitada pela instituição financeira”, por CPF ou por CNJP;

i) “COR0004R1” - Sicor informa ao requisitante de alteração na composição das destinações de financiamento de uma Cédula de Crédito Rural;

j) “COR0005R1” - Sicor informa o resultado do envio da COR0005.”(NR)

**Art. 2º** A Seção Condições Gerais do MCR - Documento 5-A passa a vigorar acrescida do item 27 com a seguinte redação:

“**Envio de informações relativas aos cooperados e integrados**

27 - O envio das informações sobre cooperados atendidos pela cooperativa de produção agropecuária na modalidade de Atendimento a Cooperados, na forma do MCR 5-2-3, ou sobre integrados atendidos na modalidade Exploração sob Regime de Integração com Agroindústria, na forma do MCR 3-2-11, de que tratam os Campos 13-A, 14-A e 27-A deste documento, devem ocorrer via mensageria ou via STA, respeitadas as seguintes condições:

a) via Mensageria: conforme leiaute da mensagem COR0005, apresentado no volume III do Catálogo versão 4.09, divulgado no site do Banco Central;

b) via STA: por meio do arquivo ACRP600, considerando os seguintes itens:

I - o leiaute do arquivo enviado deve obedecer ao que foi divulgado na Página de Notícias do Sicor no dia 14/6/2017;

II - o arquivo poderá ser enviado das 0h até às 20h, sendo processado no mesmo dia do envio, após às 20h;

III - os códigos de erro disponíveis são "Cédula não encontrada" (Código 0), "Tipo de pessoa incompatível com o CPF/CNPJ informado" (Código 1) e "CPF/CNPJ inválido" (Código 2).

Notas:

a) para fins de apuração do limite do produtor de que trata o MCR 3-2-5, e inclusão ou rejeição da operação no Sicor, terá prioridade a operação da instituição financeira que primeiro enviar as informações conforme instruções deste item;

b) as informações das operações realizadas entre 1º/7/2017 a 31/12/2017 podem ser enviadas até o dia 3/1/2018;

c) a partir de 1º/1/2018 será excluída da base de dados do Sicor a operação cujas informações sobre cooperados/integrados, de que trata o **caput,** não tenham sido recebidas via Mensageria ou via STA em até dois úteis após a data de contratação.”(NR)

**Art. 3º** A Seção Condições Específicas do MCR - Documento 5-A passa a vigorar acrescida dos Campos 1-A, 13-A, 14-A e 27-A com a seguinte redação:

“Campo 1-A - Base Normativa da Renegociação: informar o código do normativo que dá amparo à renegociação da operação de crédito rural (Lei, Medida Provisória, Decreto, Resolução do CMN, MCR, etc.), conforme tabela disponibilizada no site do Banco Central, quando houver prorrogação (SOR03) ou renegociação (SOR04, SOR05 e SOR06).

Notas:

Para o cadastramento no Sicor de operações renegociadas parcialmente com nova operação (SOR05) ou totalmente com nova operação (SOR06), o Campo 24 (Código do Empreendimento) deverá ser preenchido com o código “00000000000000”.”(NR)

“Campo 13-A - CNPJ/CPF Beneficiário Cooperado/Integrado: informar o número de inscrição no Cadastro Nacional de Pessoas Jurídicas (CNPJ) ou no Cadastro de Pessoas Físicas (CPF) do beneficiário cooperado/integrado observada a formatação admitida para envio de mensagem conforme item 27.

Notas:

a) este campo é preenchido somente quando o beneficiário do crédito rural informado no Campo 13 for cooperativa de produção agropecuária ou agroindústria na condição de integradora;

b) os empreendimentos admitidos são “Adiantamentos a cooperados por conta de produtos entregues para a venda”, “Aquisição de insumos para fornecimento a cooperados”, “Aquisição de bens para fornecimento aos cooperados” e “Exploração sob regime de integração”.”(NR)

“Campo 14-A - Tipo Pessoa Beneficiária Cooperado/Integrado: informar o código que identifica se o cooperado/integrado é pessoa física ou pessoa jurídica, conforme Dicionário de Domínios do SPB disponível na área “Crédito Rural” no site do site do Banco Central.

Notas:

a) este campo é preenchido somente quando o beneficiário do crédito rural informado no Campo 13 for cooperativa de produção agropecuária ou agroindústria na condição de integradora;

b) os empreendimentos admitidos são “Adiantamentos a cooperados por conta de produtos entregues para a venda”, “Aquisição de insumos para fornecimento a cooperados”, “Aquisição de bens para fornecimento aos cooperados” e “Exploração sob regime de integração”(NR)

“Campo 27-A - Valor da Parcela do Cooperado/Integrado: informar o valor da parcela de cada cooperado/integrado, cujo CPF e/ou CNPJ esteja listado no campo 13-A, observada a formatação admitida para envio de mensagem conforme item 27.

Notas:

a) este campo é preenchido somente quando o beneficiário do crédito rural informado no Campo 13 for cooperativa de produção agropecuária ou agroindústria na condição de integradora;

b) os empreendimentos admitidos são “Adiantamentos a cooperados por conta de produtos entregues para a venda”, “Aquisição de insumos para fornecimento a cooperados”, “Aquisição de bens para fornecimento aos cooperados” e “Exploração sob regime de integração”;

c) o somatório dos valores das parcelas de cada cooperados/integrados deve ser idêntico ao valor informado no Campo 27.”(NR)

**Art. 4º** Esta Carta Circular entra em vigor em 1º de julho de 2017.

José Angelo Mazzillo Júnior

Chefe do Derop
