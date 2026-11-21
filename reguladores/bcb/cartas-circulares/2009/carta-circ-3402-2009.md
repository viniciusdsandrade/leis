---
titulo: "Carta Circular nº 3.402, de 23 de junho de 2009"
orgao: "Banco Central do Brasil"
tipo: "Carta Circular"
tipo_na_fonte: "Carta Circular"
numero: "3402"
data: 2009-06-23
ementa: "Divulga procedimentos a serem observados para a operação de participante no serviço de inserção de mensagens em regime de contingência do Sistema de Transferência de Reservas - STR."
situacao: "revogado"
revogada: true
versao_texto: "texto mantido pelo Banco Central do Brasil no portal de normativos, com as alterações incorporadas e a redação revogada tachada quando houve alteração; não substitui a publicação no Diário Oficial da União"
fonte: "https://www.bcb.gov.br/estabilidadefinanceira/exibenormativo?tipo=Carta%20Circular&numero=3402"
fonte_texto: "https://www.bcb.gov.br/api/conteudo/app/normativos/exibenormativo?p1=Carta%20Circular&p2=3402"
sha256_fonte: "75874a31cae16413246d20811f55dc4818adb79f165ea3b7883fa776fa4b1d07"
baixado_em: 2026-11-21
---
# Carta Circular nº 3.402, de 23 de junho de 2009

CARTA-CIRCULAR N. 003402

Divulga procedimentos a serem observados para a operação de participante no serviço de inserção de mensagens em regime de contingência do Sistema de Transferência de Reservas - STR.

Tendo em vista o disposto no art. 4º da Circular nº 3.100, de 28 de março de 2002, e no respectivo regulamento anexo, com as alterações introduzidas pela Circular nº 3.439, de 2 de março de 2009, esclarecemos os procedimentos a serem adotados por participante do Sistema de Transferência de Reservas - STR para utilização do serviço de inserção de mensagens em regime de contingência.

2. O participante que, por falha ou dificuldade técnica, estiver impossibilitado de entregar corretamente suas mensagens, constantes do Catálogo de Mensagens e de Arquivos da RSFN, no Gerenciador de Filas - MQ Series do Banco Central do Brasil por intermédio da RSFN, poderá utilizar o serviço de inserção de mensagens em regime de contingência.

3. A utilização do serviço poderá ser:

I - integral - modalidade em que o participante poderá:

a) enviar direta e simultaneamente mensagens informativas ou de transferência de fundos, por ele digitadas, por intermédio de aplicativo disponível em sítio específico na Internet; e

b) enviar arquivos, por intermédio do Serviço de Transferên- cia de Arquivos do Banco Central - PSTA, que contenham exclusivamente mensagens de transferências de fundos do grupo de serviços STR.

II - parcial - modalidade em que o participante poderá soli- citar a inserção, pelo Banco Central do Brasil, das seguintes mensa- gens relativas a ordens de transferência de fundos:

a) LDL0004 - IF requisita Transferência do resultado líquido de negociações;

b) LDL0005 - Câmara requisita Transferência do resultado lí- quido de negociações LDL;

c) LDL0006 - IF ou Câmara requisita transferência por devo- lução de créditos;

d) LDL0011 - IF requisita Transferência da conta corrente câmara para conta liquidação;

e) LDL0020 - Câmara requisita Transferência do resultado lí- quido;

f) LDL0022 - IF requisita Transferência para depósito opera- cional;

g) RCO0010 - IF requisita Transferência recursos de compul- sórios para conta Reservas Bancárias;

h) RCO0011 - IF requisita Transferênci a de Reservas Bancá- rias para compulsórios, exclusivamente quando se tratar de transfe- rência de fundos destinada à liquidação de obrigações interbancárias decorrentes das sessões diárias da Centralizadora da Compensação de Cheques - Compe;

i) RDC0002 - IF requisita Redesconto intradia;

j) RDC0003 - IF requisita Redesconto com prazo de um dia útil;

k) RDC0005 - IF requisita Conversão redesconto intradia em redesconto com prazo de um dia útil ou recontratação de redesconto com prazo de um dia útil;

l) RDC0007 - IF requisita Pagamento de redesconto; e

m) STR0011 - IF requisita Cancelamento de lançamento STR pendente.

4. A operação do participante no serviço de inserção de mensagens em regime de contingência deverá seguir os procedimentos descritos no Manual da Contingência, disponível no sítio da RSFN (www.rsfn.net.br).

5. Os participantes deverão manter cadastro atualizado de seus responsáveis pelos procedimentos de contingência, na forma definida pelo Departamento de Operações Bancárias e de Sistema de Pagamentos - Deban.

6. As solicitações de entrada e de saída do serviço de contingência deverão ser feitas por intermédio de contato telefônico originado de responsável, previamente cadastrado, com o componente da Gerência de Monitoramento do Deban ao qual o solicitante estiver vinculado, ocasião em que o participante deverá fornecer chave de segurança para a verificação de autenticidade da solicitação.

7. No fechamento diário do STR, o participante retornará à condição de operação normal, ainda que não tenha solicitado a saída do serviço de contingência.

8. Encerrada a utilização do serviço de contingência, o par- ticipante deverá solicitar o extrato de sua conta, utilizando men- sagem específica para esse fim, constante do Catálogo de Mensagens e de Arquivos da RSFN, e receberá o aviso de cobrança da tarifa pela u- tilização do serviço.

9. O algoritmo para cálculo da chave de segurança será infor- mado por correspondência encaminhada pelo Deban e os componentes ne- cessários para o cálculo da chave de segurança, quais sejam, a tabela de números randômicos sequenciais (RDLIST) e a tabela de números ran- dômicos por valor (VLOPER), serão fornecidos preferencialmente por meio eletrônico e devem, juntamente com o algoritmo para o cálculo da chave de segurança, ser objeto de tratamento sigiloso pelo partici- pante, que terá inteira responsabilidade pela sua correta utilização.

10. Para obter as tabelas RDLIST e VLOPER, o participante deverá seguir as orientações contidas na correspondência citada no item 9, bem como as instruções constantes no Manual da Contingência.

11. As tabelas RDLIST e VLOPER poderão ser substituídas, a qualquer momento, por iniciativa do Deban ou por solicitação do participante, esta mediante envio da mensagem "GEN0014 - Participante requisita Arquivo", observadas as orientações contidas no Manual da Contingência.

12. Sempre que houver geração de novas tabelas, será enviada a mensagem "GEN0015 - GEN avisa Arquivo disponível" e o arquivo será encaminhado conforme o tipo de transmissão solicitado, ocasião em que as tabelas antigas perdem a validade para todos os fins. Os participantes deverão, obrigatoriamente, após o recebimento dessa mensagem, extrair as novas tabelas e validá-las mediante o envio da mensagem "STR0036 - Participante requisita Validação das tabelas de contingência".

13. Para a operação no serviço de contingência parcial, caberá ao participante fornecer, por telefone, todos os dados necessários para o preenchimento da mensagem a ser enviada.

14. A exatidão dos dados fornecidos durante a utilização do serviço de contingência será de inteira responsabilidade do participante.

15. Os procedimentos operacionais para a utilização dos serviços de inserção de mensagem e de transmissão de arquivos em regime de contingência estão estabelecidos no Manual da Contingência.

16. O envio de arquivos, disponível somente para os participan- tes considerados aptos em testes homologatórios específicos definidos pelo Deban, deve, obrigatoriamente, ocorrer enquanto o participante estiver utilizando o serviço de contingência integral e dentro do ho- rário de funcionamento do STR para registro de ordens de transferên- cia de fundos previsto no caput do art. 9º do regulamento anexo à Circular nº 3.100, sendo rejeitados os arquivos que não atenderem a essas premissas.

17. O arquivo será submetido à validação, conforme definido no Manual da Contingência, e o resultado da validação será enviado, pela mesma via, ao participante remetente. Se integralmente válido, será disponibilizado, no sítio da contingência na Internet, o resumo das informações constantes do arquivo para que o participante confirme ou cancele o seu envio para processamento.

18. O processamento das ordens de transferência de fundos transmitidas por intermédio de arquivo obedecerá, no momento do início do processamento de cada mensagem, independentemente do horário de transmissão, de validação e de confirmação do arquivo, ao horário de funcionamento do STR para registro de ordens de transferência de fundos, conforme disposto no caput e no § 1º do art. 9º do regulamento anexo à Circular nº 3.100.

19. Arquivos pendentes de confirmação serão cancelados por ocasião da saída do participante da contingência ou quando do fechamento do STR, o que ocorrer primeiro.

20. Durante o período de utilização do serviço de contingência:

I - os créditos a favor do participante serão efetivados normalmente;

II - as mensagens geradas no sítio da Internet e as mensagens recebidas anteriormente à entrada em contingência que, naquele momento, estiverem na fila de espera, serão processadas normalmente, de acordo com a regulamentação em vigor;

III - qualquer tentativa de envio de mensagem pelo par- ticipante, por meio da RSFN, resultará em mensagem "GEN0004 - GEN informa Erro de transmissão na mensagem", indicando o código de erro EGEN0021 (ISPB Emissora em Contingência); e

IV - o participante contar á com o suporte da Gerência de Monitoramento do Deban a qual estiver vinculado.

21. As comunicações telefônicas com a Gerências de Monitora- mento do Deban são gravadas e consideradas firmes e com validade para todos os fins.

22. Esta Carta-Circular entra em vigor em 31 de agosto de 2009, quando fica revogada a Carta-Circular nº 3.339, de 11 de setembro de 2008.

Brasília, 23 de junho de 2009.

Departamento de Operações Bancárias e de Sistema de Pagamentos

José Antonio Marciano Chefe de Unidade
