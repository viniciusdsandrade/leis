---
titulo: "Carta Circular nº 3.653, de 25 de abril de 2014"
orgao: "Banco Central do Brasil"
tipo: "Carta Circular"
tipo_na_fonte: "Carta Circular"
numero: "3653"
data: 2014-04-25
ementa: "Estabelece procedimentos operacionais relativos à manutenção no Banco Central do Brasil de recursos, em espécie, correspondentes ao valor de moedas eletrônicas mantidas em conta de pagamento."
situacao: "revogado"
revogada: true
versao_texto: "texto mantido pelo Banco Central do Brasil no portal de normativos, com as alterações incorporadas e a redação revogada tachada quando houve alteração; não substitui a publicação no Diário Oficial da União"
publicacao: "Publicada no DOU de 29/4/2014, Seção 1, p. 42."
data_publicacao: "2014-04-29"
fonte: "https://www.bcb.gov.br/estabilidadefinanceira/exibenormativo?tipo=Carta%20Circular&numero=3653"
fonte_texto: "https://www.bcb.gov.br/api/conteudo/app/normativos/exibenormativo?p1=Carta%20Circular&p2=3653"
sha256_fonte: "9069e8efb926f984604756bd23e69adf53e1faa75b7c069f7c7d0c4a2395c786"
baixado_em: 2026-11-20
---
# Carta Circular nº 3.653, de 25 de abril de 2014

O Chefe do Departamento de Operações Bancárias e de Sistema de Pagamentos (Deban), substituto, no uso da atribuição que confere o art. 22, inciso I alínea “a”, do Regimento Interno do Banco Central do Brasil, anexo à Portaria nº 29.971, de 4 de março de 2005, com base no art. 12, § 8º, da Circular nº 3.681, de 4 de novembro de 2013, e na Circular nº 3.704, de 24 de abril de 2014,

RESOLVE:

**Art. 1º** O disposto nesta Carta Circular se aplica às instituições emissoras de moeda eletrônica e aos titulares de conta Reservas Bancárias e de Conta de Liquidação, exceto câmaras e prestadores de serviços de compensação e de liquidação.

**Art. 2º** Para cumprimento da obrigatoriedade de manutenção, no Banco Central do Brasil, de recursos em espécie correspondentes ao valor de moedas eletrônicas mantidas em contas de pagamento e em trânsito entre contas de pagamento na mesma instituição de pagamento, de que trata o **caput** e o inciso I do §1º do art. 12 da Circular nº 3.681, de 4 de novembro de 2013, com as alterações introduzidas pela Circular nº 3.705, de 24 de abril de 2014, as instituições emissoras de moeda eletrônica devem observar os procedimentos operacionais estabelecidos nesta Carta Circular.

#### CAPÍTULO I — DAS DEFINIÇÕES

**Art. 3º** Para efeitos dessa Carta Circular, considera-se:

I- instituição emissora de moeda eletrônica (IEME): instituição que gerencia conta de pagamento de usuário final, do tipo pré-paga, e disponibiliza transação de pagamento com base em moeda eletrônica aportada nessa conta;

II- instituição de pagamento: pessoa jurídica integrante do Sistema de Pagamentos Brasileiro (SPB), definida no art.6º, inciso III, da Lei nº 12.865, de 9 de outubro de 2013;

III- Conta Correspondente a Moeda Eletrônica (CCME): conta específica mantida no Banco Central do Brasil, de titularidade das instituições de pagamento, das instituições financeiras e das demais instituições autorizadas a funcionar pelo Banco Central do Brasil, quando emissoras de moeda eletrônica, destinada exclusivamente à manutenção dos recursos em espécie correspondentes ao valor de moedas eletrônicas mantidas em conta de pagamento pré-paga por elas gerenciadas, acrescido dos saldos de moedas eletrônicas em trânsito entre contas de pagamento na mesma instituição de pagamento;

IV- recursos em espécie: saldo em reais mantido em conta no Banco Central do Brasil.

#### CAPÍTULO II — DAS MOVIMENTAÇÕES DE RECURSOS NA CONTA CORRESPONDENTE A MOEDA ELETRÔNICA

##### Seção I — Da utilização do Grupo de Serviços SME

**Art. 4º** As movimentações de recursos na CCME são realizadas por meio de mensagens do Grupo de Serviços SME, do Catálogo de Serviços do SFN, observado que:

I - o envio das mensagens do Grupo de Serviços SME pelas instituições participantes do STR é feito por meio da Rede do Sistema Financeiro Nacional (RSFN) ou pela internet, utilizando o aplicativo STR-Web, conforme o tipo de acesso principal ao STR utilizado pelo participante, durante operação em regime normal ou de contingência.

II - as IEME não participantes do STR utilizam o aplicativo STR-Web para comandar transferências a débito da CCME de sua titularidade.

##### Seção II — Da alocação dos recursos

**Art. 5º** A transferência a crédito da CCME é realizada por meio da mensagem “SME0001- IF requisita transferência para depósito em conta específica”, constante do Catálogo de Serviços do SFN, observado que:

I - as instituições financeiras titulares de conta Reservas Bancárias podem comandar transferências para a conta:

a) de sua titularidade; ou

b) de titularidade de IEME não participante do STR conforme acordo específico firmado entre as partes.

II – as instituições titulares de Conta de Liquidação de que trata o art. 1º podem comandar transferências exclusivamente para a CCME de sua titularidade.

##### Seção III — Do saque dos recursos

**Art. 6º** A transferência a débito da CCME deve ser comandada exclusivamente pelo titular da referida conta por meio da mensagem “SME0002- IEME requisita transferência para saque em conta específica”, observado que:

I – caso o titular seja participante do STR os recursos são creditados na conta Reservas Bancárias ou Conta de Liquidação de sua titularidade;

II- caso o titular não seja participante do STR, a solicitação deve ser efetuada via internet, utilizando o aplicativo STR-Web, e os recursos creditados exclusivamente na conta-corrente de sua titularidade em instituição detentora de conta Reservas Bancárias indicada na mensagem.

**Parágrafo único.** O sistema verificará, a cada requisição de débito na CCME, o saldo disponível na referida conta do solicitante e rejeitará as requisições no caso de insuficiência de saldo.

##### Seção IV — Das Devoluções de recursos recebidos indevidamente

**Art. 7º** A devolução de transferência envolvendo a CCME deve ser realizada por meio da mensagem “SME0004 – IF ou IEME requisita transferência para devolução de lançamento indevido no SME”

**§1º** A devolução deve ocorrer em comando único e corresponder ao valor total do originalmente recebido.

**§2º** Todas as instituições detentoras de conta Reservas Bancárias devem estar aptas ao envio da mensagem SME0004 – IF ou IEME requisita transferência para devolução de lançamento indevido no SME – para eventual necessidade de devolução de recursos indevidamente creditados em sua conta.

##### Seção V — Da autorização para movimentação financeira na CCME

**Art. 8º** As IEME devem solicitar, por intermédio de expediente encaminhado ao Deban, autorização para uso das mensagens do Grupo de Serviços SME, do Catálogo de Serviços do SFN, e a ativação da CCME de sua titularidade, esclarecido que a solicitação deve ser encaminhada:

I- instituição de pagamento em processo de constituição: durante o processo de implementação da estrutura organizacional, após o cumprimento das condições previstas no art. 9º, inciso I, da Circular nº 3.683, de 4 de novembro de 2013;

II – instituição de pagamento em atividade em processo de autorização no Banco Central do Brasil para funcionamento: após a manifestação favorável à proposta de empreendimento de que trata o art. 7º, inciso I, da Circular nº 3.683, de 2013, durante a execução dos procedimentos previstos no art. 16 da mencionada Circular;

III- instituições de pagamento em funcionamento, em processo de autorização para atuar na modalidade de emissor de moeda eletrônica: após a entrega no Banco Central do Brasil da documentação prevista no art. 19, da Circular nº 3.683, de 2013;

IV – instituições financeiras e demais instituições autorizadas a funcionar pelo Banco Central do Brasil em processo de autorização para prestação de serviços de pagamento na modalidade de emissor de moeda eletrônica: após a manifestação favorável à proposta de empreendimento de que trata o art. 7º, inciso I, da Circular nº 3.683, de 2013, durante a execução dos procedimentos previstos no art. 46 da mencionada Circular; e

V- bancos comerciais, bancos múltiplos com carteira comercial, caixas econômicas e cooperativas singulares de crédito: a qualquer momento.

**Parágrafo único.** A liberação para uso das mensagens do Grupo de Serviços SME pela instituição e a ativação da CCME, em ambiente de produção, estão condicionadas à realização de testes estabelecidos pelo Deban e à expedição, pelo Banco Central do Brasil, das autorizações previstas nos arts. 12, 17, 18, 47 e 49, §3º, da Circular nº 3.683, de 2013, conforme o caso.

**Art. 9º** As instituições financeiras titulares de conta Reservas Bancárias não emissoras de moeda eletrônica podem solicitar, a qualquer momento, autorização para utilização da mensagem “SME0001- IF requisita transferência para depósito em conta específica” para comandar transferências em nome de IEME não participante do STR, nos termos do art. 5º, inciso I, alínea “b”, desta Carta Circular.

**Parágrafo único.** A liberação de uso da mensagem, na situação mencionada no **caput**, deve ser objeto de solicitação específica ao Deban, que indicará o teste necessário para o cadastramento.

#### CAPÍTULO III — DA UTILIZAÇÃO DO APLICATIVO STR-WEB PELAS IEME NÃO PARTICIPANTES DO STR

**Art.10.** A utilização do aplicativo STR-Web pelas IEME não participantes do STR segue os requisitos técnicos e de segurança para acesso ao STR-Web descritos no Manual de Acesso ao STR via Internet, disponível no sítio do Banco Central do Brasil (www.bcb.gov.br).

**Art.11.** A solicitação de acesso ao STR-Web e de movimentação da CCME deve ser feita por intermédio de expediente encaminhado ao Deban, firmado pelo diretor responsável pelo cumprimento das normas relativas à conta de pagamento, observado que:

**§1º** A solicitação de que trata o **caput** deve ser encaminhada, conforme o caso, nos momentos descritos no art. 8º, incisos I a IV, desta Carta Circular.

**§2º** A liberação para uso do STR-Web pela instituição em ambiente de produção está condicionada à realização de testes estabelecidos pelo Deban e à expedição, pelo Banco Central do Brasil, das autorizações previstas nos arts. 12, 17, 18, 47 e 49, §3º, da Circular nº 3.683, de 2013, conforme o caso.

**Art. 12.** As IEME não participantes do STR devem informar e manter atualizado, por meio de registro no **portlet** “Responsáveis” do STR-Web, o nome, o número de CPF, o número do documento oficial de identificação, o endereço de e-mail e, no mínimo, dois números de telefone em ordem de prioridade para contato:

I- do diretor responsável pelo cumprimento das normas relativas à conta de pagamento, de que trata o art. 5º da Circ. 3.680, de 4 de novembro de 2013;

II- de, no mínimo, dois responsáveis pelo gerenciamento da Conta Correspondente a Moeda Eletrônica;

III- de, no mínimo, três representantes para as solicitações referentes ao regime de operação em Contingência Telefônica.

**Parágrafo único.** As responsabilidades descritas nos incisos I, II e III podem ser atribuídas de forma acumulada.

**Art.13.** A instituição emissora de moeda eletrônica não participante do STR deve informar ao Deban, por meio de expediente firmado pelo diretor responsável pelo cumprimento das normas relativas à conta de pagamento, os dados bancários para envio da cobrança da tarifa pela utilização do serviço de contingência de que trata o art. 10 da Circular nº 3.704, de 24 de abril de 2014.

**Art.14.** As solicitações de ativação e de encerramento da operação em regime de Contingência Telefônica de que trata o art. 9º da Circular nº 3.704, de 2014, são feitas por intermédio de contato telefônico originado de um dos representantes citados no art.12, inciso III, desta Carta Circular, com o componente da Divisão de Gestão e Monitoramento do STR (Gemon) ao qual o solicitante estiver vinculado.

**Art. 15.** Esta Carta Circular entra em vigor em 5 de maio de 2014.

Carlos Eduardo de Andrade Brandt Silva
