---
titulo: "Carta Circular nº 3.562, de 7 de agosto de 2012"
orgao: "Banco Central do Brasil"
tipo: "Carta Circular"
tipo_na_fonte: "Carta Circular"
numero: "3562"
data: 2012-08-07
ementa: "Divulga procedimentos a respeito da prestação de informações de que trata a Circular nº 3.569, de 22 de dezembro de 2011."
situacao: "revogado"
revogada: true
versao_texto: "texto mantido pelo Banco Central do Brasil no portal de normativos, com as alterações incorporadas e a redação revogada tachada quando houve alteração; não substitui a publicação no Diário Oficial da União"
publicacao: "Publicada no DOU de 8/8/2012, Seção 1, p. 66-68."
data_publicacao: "2012-08-08"
fonte: "https://www.bcb.gov.br/estabilidadefinanceira/exibenormativo?tipo=Carta%20Circular&numero=3562"
fonte_texto: "https://www.bcb.gov.br/api/conteudo/app/normativos/exibenormativo?p1=Carta%20Circular&p2=3562"
sha256_fonte: "5315851ab1e9e7021616ea8a1459a360cbb27a039991f227edd432fa5a870085"
baixado_em: 2026-11-20
---
# Carta Circular nº 3.562, de 7 de agosto de 2012

O Chefe do Departamento de Operações Bancárias e de Sistema de Pagamentos e o Chefe do Departamento de Monitoramento do Sistema Financeiro, no uso das atribuições que lhes conferem, respectivamente, o art. 22, inciso I, alínea “a”, e o art. 71, incisos II e III, do Regimento Interno do Banco Central do Brasil, anexo à Portaria nº 29.971, de 4 de março de 2005, e tendo em vista o disposto no art. 14 da Circular nº 3.569, de 22 de dezembro de 2011,

R E S O L V E M :

**Art. 1º** Para a prestação de informações relativas ao recolhimento compulsório sobre recursos a prazo de que trata a Circular nº 3.569, de 2011, as instituições devem observar os seguintes procedimentos:

I - Instituições participantes do Sistema de Transferência de Reservas (STR) com acesso principal pela Rede do Sistema Financeiro Nacional (RSFN): utilizar a RSFN; ou

II - Demais instituições: utilizar a transação PRCO500, do Sistema de Informações Banco Central - Sisbacen.

**Art. 2º** Para a prestação das informações devem ser utilizados os seguintes códigos do Dicionário de Domínios associado ao Catálogo de Mensagens e de Arquivos da RSFN:

I - Instituições participantes do STR com acesso principal pela RSFN: utilizar a mensagem "RCO0002 - IF informa Demonstrativo", do Grupo de Serviços RCO, constante do Catálogo de Mensagens e de Arquivos da RSFN, preenchendo o campo "CodRCO" com o código "9 - Recursos a Prazo", observando:

a) Valores Sujeitos a Recolhimento (VSR):

1\. CodItem 9001 - saldo total da rubrica "4.1.5.10.00-9 Depósitos a Prazo", do Cosif (art. 2º, inciso V, da Circular nº 3.569);

2\. CodItem 9002 - saldo total da rubrica "4.3.1.00.00-8 Recursos de Aceites Cambiais", do Cosif (art. 2º, inciso VI, da Circular nº 3.569);

3\. CodItem 9003 - saldo total da rubrica "4.3.4.50.00-2 Cédulas Pignoratícias de Debêntures", do Cosif (art. 2º, inciso VII, da Circular nº 3.569);

4\. CodItem 9004 - saldo total da rubrica "4.2.1.10.80-0 Títulos de Emissão Própria", do Cosif (art. 2º, inciso VIII, da Circular nº 3.569);

5\. CodItem 9005 - saldo total da rubrica "4.9.9.12.20-7 Contratos de Assunção de Obrigações - Vinculados a Operações Realizadas no Exterior", do Cosif (art. 2º, inciso IX, da Circular nº 3.569);

6\. CodItem 9008 - saldo total da rubrica "4.1.3.10.60-1 Ligadas - Sociedade de Arrendamento Mercantil", do Cosif (art. 2º, inciso I, da Circular nº 3.569);

7\. CodItem 9009 - saldo total da rubrica "4.1.3.10.65-6 Ligadas com Garantia - Sociedade de Arrendamento Mercantil", do Cosif (art. 2º, inciso II, da Circular nº 3.569);

8\. CodItem 9010 - saldo total da rubrica "4.1.3.10.70-4 Não Ligadas - Sociedade de Arrendamento Mercantil", do Cosif (art. 2º, inciso III, da Circular nº 3.569); e

9\. CodItem 9011 - saldo total da rubrica "4.1.3.10.75-9 Não Ligadas com Garantia - Sociedade de Arrendamento Mercantil", do Cosif (art. 2º, inciso IV, da Circular nº 3.569);

b) Valores correspondentes às operações passíveis de dedução do recolhimento compulsório, sem nenhuma atualização devida à remuneração, acumulados até a data sob referência:

1\. CodItem 9006 - somatório das operações de que tratam os incisos I a V, art. 11, da Circular nº 3.569, apuradas pelo valor financeiro de liquidação;

2\. CodItem 9013 - somatório dos depósitos interfinanceiros de que tratam os incisos VI e VII, art. 11, da Circular nº 3.569, apurados pelo valor nominal depositado;

3\. CodItem 9016 - somatório das aquisições de letras financeiras, de que trata o inciso VIII, art. 11, da Circular nº 3.569, apuradas pelo valor de emissão; e

4\. CodItem 9017 - saldo das operações de crédito para financiamento e arrendamento mercantil de automóveis e de veículos comerciais leves, contratadas a partir de 22 de maio de 2012, de que trata o art. 11-A da Circular nº 3.569.

II – demais instituições: utilizar a transação PRCO500, do Sisbacen, para informar os dados previstos nas alíneas "a" e "b" do inciso I.

**Art. 3º** As informações das operações de que trata o art. 11 da Circular nº 3.569 deverão ser enviadas ao Banco Central do Brasil pela instituição beneficiada pela dedução, bem como por sua contraparte, por meio da mensagem "RCO0022 - IF informa operação para dedução de recolhimento compulsório", do Grupo de Serviços RCO, constante do Catálogo de Mensagens e de Arquivos da RSFN, observando as seguintes informações obrigatórias:

I – o ISPB da instituição que envia a mensagem;

II – o ISPB da instituição beneficiada pela dedução, mesmo se igual ao ISPB informado no inciso I;

III – o ISPB da instituição contraparte da operação, mesmo se igual ao ISPB informado no inciso I, sendo que para o Fundo Garantidor de Créditos (FGC), deve-se informar seu CNPJ-Base;

IV – o tipo da operação, entre os estabelecidos nos incisos do artigo 11 da Circular nº 3.569;

V – a data limite de dedução;

VI – a data e o valor da liquidação financeira, de que trata o art. 13 da Circular nº 3.569; e

VII – o “número de controle STR” da mensagem STR0004 ou STR0007, quando houver liquidação financeira da operação por intermédio de Transferência Eletrônica Disponível no Sistema de Transferência de Reservas (STR).

**§1º** Além das informações de que trata o caput, deverão ser prestadas adicionalmente, na mensagem “RCO0022”, as seguintes informações, quando existentes e de acordo com o tipo de operação:

I – para as operações de cessão de créditos e de direitos creditórios:

a) o valor total das operações envolvidas na cessão;

b) a modalidade da operação, no que diz respeito à cláusula de coobrigação; e

c) o número único de reserva (NURES), para as operações que forem realizadas por intermédio de sistema de registro, compensação e liquidação financeira de ativos, autorizado pelo Banco Central do Brasil.

II – para a aquisição de cotas de fundos de investimento:

a) a inscrição no CNPJ do fundo de investimento;

b) o código identificador e a data de emissão do ativo, se registrado em sistema de registro, compensação e liquidação financeira de ativos devidamente autorizados pelo Banco Central do Brasil, e

c) a quantidade de cotas adquiridas.

III – para a aquisição de Letras Financeiras:

a) o código identificador e a data de emissão do ativo registrado em sistema de registro, compensação e liquidação financeira de ativos devidamente autorizados pelo Banco Central do Brasil; e

b) o ISPB da instituição emissora da Letra Financeira, inclusive no caso em que for também a instituição contraparte da operação.

IV – para a aquisição de depósitos bancários, Letras de Arrendamento Mercantil e Letras de Câmbio de propriedade do FGC, o código identificador e a data de emissão do ativo, se registrado em sistema de registro, compensação e liquidação financeira de ativos devidamente autorizados pelo Banco Central do Brasil.

**§2º** No tratamento da mensagem “RCO0022”, o sistema de registro RCO não verifica as condições de elegibilidade, para fins de dedução, da operação e da instituição financeira cedente, vendedora, depositária ou emissora, segundo os critérios estabelecidos no inciso II do §1º do art. 11 da Circular nº 3.569. A verificação da validade das condições de elegibilidade cabe à instituição financeira beneficiada pela dedução.

**§3º** As instituições financeiras contrapartes em operações válidas para dedução e que não tenham acesso à RSFN, devem utilizar a transação PRCO500, do Sisbacen, para confirmar as informações das operações em situação “pendente de confirmação de contraparte”.

**Art. 4º** Para que o registro da operação no sistema RCO seja válido para dedução do recolhimento compulsório sobre recursos a prazo, as informações de que trata o artigo anterior deverão ser prestadas estritamente na seguinte ordem:

I – a instituição financeira beneficiada pela dedução envia mensagem “RCO0022”;

II – o sistema RCO registra a operação em situação “pendente de confirmação de contraparte”, envia à instituição beneficiada pela dedução a mensagem “RCO0022R1”, com o identificador único (“Número Controle RCO”) do registro da operação e envia mensagem “RCO0022R2” notificando a contraparte sobre o registro da operação e as informações prestadas;

III - a instituição contraparte da operação envia mensagem “RCO0022”, dentro das condições estabelecidas no §1º; e

IV – o sistema RCO altera a situação do registro da operação para “ativa” e envia mensagem “RCO0022R1” para as duas instituições participantes da operação, em resposta às suas respectivas “RCO0022”, informando a mudança de situação.

**§1º** A instituição contraparte tem prazo de 30 dias corridos, contados a partir do recebimento da mensagem “RCO0022R2” de que trata o inciso II, para enviar a mensagem referida no inciso III, com as informações da operação idênticas às prestadas pela instituição financeira beneficiada pela dedução.

**§2º** Findo o prazo estabelecido no parágrafo anterior sem a manifestação da contraparte, o registro da operação passará automaticamente para a situação “cancelada”, não podendo mais ser confirmado pela contraparte conforme o inciso III. Caso necessário, a instituição beneficiada pode enviar novamente as informações de que trata o inciso I, iniciando a contagem de um novo prazo para o fluxo descrito neste artigo.

**§3º** As operações com registro em situação “pendente de confirmação de contraparte” não podem ser utilizadas para fins de dedução no recolhimento compulsório a prazo. Somente operações com registro em situação “ativa” no sistema RCO são válidas para o cálculo da referida dedução.

**§4º** Para o caso de operação em que a contraparte é o FGC, não se aplica o disposto nos incisos II, III e IV. Seu registro será efetuado de imediato em situação “ativa” na prestação das informações de que trata o inciso I.

**§5º** A instituição financeira beneficiada pela dedução será notificada pelo sistema RCO, por meio da mensagem “RCO0022R1” descrita no inciso II, sempre que houver mudança automática da situação de registro de operação para as situações “vencida” ou “cancelada”.

**§6º** O fluxo de mensagens descrito neste artigo não se aplica às operações válidas para dedução de recolhimento compulsório, informadas sob a égide da Carta Circular nº 3.541, de 2 de março de 2012, ou normativos anteriores. Os registros destas operações serão automaticamente gerados no sistema RCO, no momento de sua implantação em ambiente de produção. Cada um destes registros receberá um identificador único (“Número Controle RCO”), que deverá ser consultado e utilizado pela instituição beneficiada pela dedução, na forma estabelecida nos arts. 6º e 7º desta Carta Circular.

**Art. 5º** O prazo médio ponderado a decorrer das operações objeto da cessão referido no art. 12 da Circular nº 3.569 deve ser calculado da seguinte forma, considerando-se, individualmente, cada operação de compra e venda realizada:

n  
Z Sdi x Pri  
i=1  
Pm = -------------- , onde:  
n  
Z Sdi  
i=1

Pm = prazo médio da carteira em dias corridos;

Sdi = saldo devedor do i-ésimo contrato que compõe a carteira, atualizado até a véspera da liquidação financeira da aquisição dos créditos;

Pri = prazo remanescente de vencimento do i-ésimo contrato, em dias corridos, calculado a partir da data de liquidação financeira da aquisição dos créditos; e

n = quantidade de contratos da carteira.

obs.: na fórmula a letra "Z" corresponde a Somatório.

**§1º** A data limite para dedução das operações objeto da cessão deve corresponder à data de liquidação da operação, acrescida do prazo médio calculado de acordo com o caput deste artigo.

**§2º** Quando prevista a coobrigação, a devolução dos contratos inadimplentes não será considerada para os efeitos da vedação à recompra estabelecida no §1º do art. 11 da Circular nº 3.569. Nessa hipótese, o valor dos créditos devolvidos deve ser deduzido do valor informado no CodItem 9006 (Total Operações de Crédito Adquiridas), assim como o prazo médio e a data limite de dedução devem ser recalculados conforme a fórmula definida no caput.

**§3º** O pagamento antecipado de parcelas ou a liquidação antecipada de contrato implicará diminuição do valor de dedução e a necessidade de recálculo do prazo médio e da data limite de dedução, devendo-se, para tanto, observar a fórmula definida no caput.

**Art. 6º** A instituição financeira beneficiada pela dedução no recolhimento compulsório deve informar as alterações no valor ou na data limite de dedução das operações por meio de mensagem "RCO0023 - IF informa evento de alteração em operação para dedução de recolhimento compulsório”, do Grupo de Serviços RCO, constante do Catálogo de Mensagens e de Arquivos da RSFN, sempre que ocorrer ao menos um dos seguintes eventos:

I – operação em situação “pendente de confirmação de contraparte”, quando houver a necessidade de cancelamento de registro por incorreção da informação.

II - operação com registro em situação “ativa”, quando houver:

a) alienação ou transferência parcial ou total da posse do ativo;

b) resgate de cotas de fundo de investimento;

c) devolução por inadimplência, para as operações de cessão de créditos ou de direitos creditórios;

d) liquidação antecipada, para as operações de cessão de créditos ou de direitos creditórios;

e) recompra total ou parcial dos ativos de que tratam os incisos I a V do art. 11 da Circular nº 3.569;

f) resgate antecipado total ou parcial de depósitos interfinanceiros; e

g) exclusão de registro por prestação de informação indevida.

**§1º** Na mensagem de que trata o caput deve-se informar:

I – obrigatoriamente:

a) o “Número Controle RCO” da operação objeto da alteração;

b) o tipo do evento;

II – adicionalmente, para os eventos de que trata o inciso II deste artigo, quando existentes:

a) a data em que ocorreu o evento gerador da alteração;

b) o novo valor e a nova data limite de dedução;

c) os valores relativos à devolução por inadimplência e à liquidação antecipada;

d) a quantidade de cotas resgatadas; e

e) o “número de controle STR” da mensagem STR0004 ou STR0007 referente à liquidação financeira do ajuste informado.

**§2º** A mensagem de que trata o caput deste artigo deve ser enviada até o dia útil imediatamente anterior ao início do período de movimentação, quando se referir a alteração em operação cuja liquidação financeira tenha ocorrido até o fim do respectivo período de cálculo.

**§3º** O descumprimento do prazo disposto no parágrafo anterior sujeitará a instituição à interpelação pelo Departamento de Operações Bancárias e de Sistema de Pagamentos do Banco Central do Brasil, sem prejuízo de outras medidas administrativas e fiscalizatórias cabíveis.

**§4º** Para alteração de operações de cessão de crédito e direitos creditórios, o novo valor de dedução informado na mensagem “RCO0023” deve corresponder ao valor precedente de dedução subtraído dos valores informados para devoluções por inadimplência e liquidações antecipadas.

**§5º** As operações válidas para dedução com registro no sistema RCO em situação “vencida”, “excluída” ou “alienada” não podem ser objeto de alteração por meio de mensagem "RCO0023”.

**Art. 7º** Para consultar as informações das operações registradas junto ao Banco Central do Brasil de que trata o art. 3º, a instituição financeira, beneficiada pela dedução ou contraparte da operação, deve utilizar a mensagem "RCO0024 - IF consulta operações para dedução de recolhimento compulsório”, do Grupo de Serviços RCO, constante do Catálogo de Mensagens e de Arquivos da RSFN.

**§1º** Para receber informações referentes a um subconjunto de operações registradas no sistema RCO, a instituição financeira pode especificar um ou mais dos seguintes critérios de pesquisa na mensagem “RCO0024”:

I – o “Número Controle RCO”, para receber as informações relativas a uma única operação específica;

II – a situação do registro da operação no sistema RCO, para receber informações relativas a operações em uma situação específica dentre “pendente de confirmação de contraparte”, “cancelada”, “ativa”, “vencida”, “excluída” e “alienada”; e

III – a data de início e de fim do período para a liquidação financeira, para receber informações relativas a operações cuja liquidação financeira tenha ocorrido dentro do intervalo especificado.

**§2º** Caso nenhum dos campos opcionais de que trata o §1º seja especificado, a mensagem de resposta “RCO0024R1” conterá as informações de todas as operações registradas no sistema RCO.

**§3º** A mensagem de resposta “RCO0024R1” contém informações de no máximo duzentas operações por consulta. Para além desse limite, existe a opção por download de arquivo, identificada pelo campo “TpRet” da mensagem “RCO0024”.

**§4º** A mensagem de resposta “RCO0024R1” apresenta as informações referentes ao momento da consulta, conforme registradas no sistema RCO. Não é possível fazer consultas das situações pretéritas das operações e nem do histórico de suas alterações.

**§5º** Além das informações originalmente registradas por meio da “RCO0022”, a mensagem “RCO0024R1” retorna, para cada operação, as seguintes informações adicionais:

I - o “Número Controle RCO”, identificador único da operação no sistema RCO;

II – a situação atual da operação, como:

a) “pendente de confirmação de contraparte”, quando informada pela instituição beneficiada pela dedução, mas não pela contraparte;

b) “ativa”, quando informada sem divergências tanto pela instituição beneficiada pela dedução como pela contraparte, e com prazo limite de dedução ainda não expirado;

c) “cancelada”, aplicável apenas à operação anteriormente em situação “pendente de confirmação de contraparte” e que não passou à situação “ativa”, indicando que nunca foi considerada no cálculo da dedução;

d) “vencida”, situação alterada automaticamente pelo sistema RCO quando a operação antes “ativa” expira após sua data limite de dedução;

e) “alienada”, quando se perde, integralmente, a posse ou propriedade de um ativo objeto de operação anteriormente “ativa”, porém sem infringir nenhuma das vedações de que trata o §1º do art. 11 da Circular nº 3.569, impossibilitando a dedução do valor da operação, sem efeitos retroativos nas deduções realizadas em períodos de movimento pretéritos; ou

f) “excluída”, quando se tratar de operação com situação anteriormente “ativa” que se tornou inelegível para fins de dedução por inexistir, por conter informações incorretas ou por infringir alguma das vedações de que trata o §1º do art. 11 da Circular nº 3.569, impossibilitando a dedução do seu valor e produzindo efeitos retroativos sobre as deduções em períodos de movimentação pretéritos.

III – o valor atual e a data limite para dedução;

IV – as datas de envio das informações da operação por meio da mensagem “RCO0022”, tanto pela instituição financeira beneficiada pela dedução, como pela contraparte; e

V – a data da última alteração na situação da operação, no valor ou na data limite de dedução, a partir da qual as informações presentes se aplicam à referida operação.

**Art. 8º** Os ativos de que tratam os incisos VI a VIII do art.11 da Circular nº 3.569 somente serão admitidos para fins de dedução se mantidos na conta “Vinculada a Redução de Compulsório”, cuja movimentação é feita a partir da conta “Própria”, seguindo os regulamentos e procedimentos operacionais do sistema de registro, compensação e liquidação autorizado a funcionar pelo Banco Central do Brasil.

**Art. 9º** Somente os valores informados por meio dos CodItens 9006 (Total Operações de Crédito Adquiridas), 9013 (Total de Aplicação Primária em DI), 9016 (Letras Financeiras) e 9017 (operações de crédito para financiamento e arrendamento mercantil de automóveis e de veículos comerciais leves), referentes ao último dia do período de cálculo, serão considerados para fins da dedução no período de movimentação correspondente.

**§1º** Para o cômputo dos valores dos CodItens 9006, 9013 e 9016 só devem ser consideradas as operações cujas informações de que tratam os arts. 3º e 6º tenham sido prestadas até o dia útil imediatamente anterior ao início do período de movimentação e com situação “ativa” ao final do referido dia.

**§2º** Operações com registro em situação “pendente de confirmação de contraparte” não estão aptas para fins de dedução e não devem ser consideradas no cálculo dos valores dos CodItens 9006, 9013 e 9016.

**§3º** O valor de dedução informado na mensagem “RCO0024R1” não considera o limite percentual do total das deduções em relação ao valor da exigibilidade, nem o limite de dedução por contraparte ou conglomerado financeiro, conforme definidos, respectivamente, nos incisos III e IV do §1º do art. 11, da Circular nº 3.569. Cabe à instituição beneficiada a estrita observância do limite previsto no referido inciso IV para o cálculo correto dos CodItens 9006, 9013 e 9016.

**§4º** As mensagens descritas nos arts. 3º, 6º e 7º desta Carta Circular não se aplicam às operações de crédito para financiamento e arrendamento mercantil de automóveis e de veículos comerciais leves, de que trata o art. 11-A da Circular nº 3.569.

**Art. 10.** O resgate antecipado das operações de que tratam os incisos VI e VII e a recompra, nas aquisições de ativos de que tratam os incisos I a V, art. 11, da Circular nº 3.569, implicam a desconsideração dessas operações para fins de dedução do recolhimento compulsório, inclusive dos valores já deduzidos em função de tais operações, a teor do disposto no inciso I, §1º, art. 11, da referida Circular.

**Art. 11.** Em vista do disposto no caput do art. 13 da Circular nº 3.569, deverão ser utilizadas na liquidação financeira de tais operações:

I - se ambas as instituições forem detentoras de conta Reservas Bancárias ou Conta de Liquidação, mensagem STR0004, indicando a finalidade adequada constante no Dicionário de Domínios associado ao Catálogo de Mensagens e de Arquivos da RSFN;

II - se a instituição financeira contraparte não for detentora de conta Reservas Bancárias ou Conta de Liquidação, mensagem STR0007, indicando a finalidade adequada constante no Dicionário de Domínios associado ao Catálogo de Mensagens e de Arquivos da RSFN; e

III - se a instituição financeira contraparte for cliente da instituição financeira beneficiada pela dedução, a liquidação deve ser realizada exclusivamente por crédito em conta-corrente.

**Art. 12.** As instituições financeiras que optarem pela dedução do recolhimento compulsório sobre recursos a prazo, nos termos do inciso II, do §1º do art. 11 da Circular nº 3.569 podem consultar as informações relativas às instituições financeiras independentes e de conglomerados financeiros, referentes aos meses de junho e de dezembro de 2011, na página do Banco Central do Brasil, na internet, nos endereços eletrônicos “http://www.bcb.gov.br/?RELINST” e “http://www4.bcb.gov.br/top50/port/top50.asp”, para verificar a possibilidade de serem consideradas elegíveis, nos termos do inciso II, do §1º do art. 11 da Circular nº 3.569, com redação dada pelo art. 4º da Circular nº 3.576, de 2012.

**Art. 13.** Para efeito do disposto no art. 11, § 1º, inciso II, da Circular nº 3.569, com redação dada pelo art. 4º da Circular nº 3.576, de 2012:

I - permanecem elegíveis as instituições financeiras adquiridas por instituições financeiras também consideradas elegíveis:

a) independentes; ou

b) integrantes de conglomerado financeiro;

II - instituições financeiras que tenham iniciado o funcionamento a partir de 2 de janeiro de 2012 não são consideradas elegíveis.

**Art. 14.** Nos termos do art. 11, § 1º, inciso IV, alínea “c”, da Circular nº 3.569, com redação dada pelo art. 4º da Circular nº 3.576, de 2012, deve ser utilizado o Nível 1 do Patrimônio de Referência (PR), apurado na forma estabelecida pela Resolução nº 3.444, de 28 de fevereiro de 2007:

I - da instituição envolvida nos processos de incorporação ou aquisição referidos no art. 13, inciso I, alínea “a”, que apresentar o maior valor em 30 de junho de 2011, quando o conglomerado financeiro for formado a partir de 1º de julho de 2011;

II - do conglomerado financeiro do qual a instituição financeira adquirida passou a fazer parte, nos casos referidos no art. 13, inciso I, alínea “b”, em 30 de junho de 2011.

**Art. 15.** A documentação comprobatória das informações objeto da Circular nº 3.569, de suas alterações posteriores e desta Carta Circular deve ser mantida à disposição do Banco Central do Brasil pelo prazo de cinco anos, contados a partir da data a que se refere cada informação, nos termos do disposto no art. 1º da Lei nº 9.873, de 23 de novembro de 1999.

**Art. 16.** Esta Carta Circular entra em vigor na data de sua publicação, produzindo efeitos a partir de 28 de setembro de 2012.

**Parágrafo único.** A partir da data estabelecida no caput para início da utilização, em ambiente de produção, das mensagens “RCO0022”, “RCO0023” e “RCO0024”, de que tratam respectivamente os arts. 3º, 6º e 7º, o envio das informações por meio de expediente firmado, por mensagem eletrônica (BC Correio) ou por planilha eletrônica, conforme estabelecido nos arts. 3º, 6º e 7º da Carta Circular nº 3.541, de 2012, não será mais aceito pelo Departamento de Operações Bancárias e de Sistema de Pagamentos do Banco Central do Brasil.

**Art. 17.** A partir da data de produção de efeitos desta Carta Circular, ficam revogadas as Cartas Circulares ns. 3.541, de 2 de março de 2012, e 3.556, de 23 de maio de 2012.  
  
  
  
  
Rodrigo Collares Arantes Gilneu Francisco Astolfi Vivan  
Chefe do Departamento de Chefe do Departamento de Monitora-  
Operações Bancárias e de mento do Sistema Financeiro,  
Sistema de Pagamentos, substituto  
substituto
