---
titulo: "Carta Circular nº 3.339, de 11 de setembro de 2008"
orgao: "Banco Central do Brasil"
tipo: "Carta Circular"
tipo_na_fonte: "Carta Circular"
numero: "3339"
data: 2008-09-11
ementa: "Divulga procedimentos a serem observados para a operação de participante em regime de contingência no Sistema de Transferência de Reservas - STR."
situacao: "revogado"
revogada: true
versao_texto: "texto mantido pelo Banco Central do Brasil no portal de normativos, com as alterações incorporadas e a redação revogada tachada quando houve alteração; não substitui a publicação no Diário Oficial da União"
fonte: "https://www.bcb.gov.br/estabilidadefinanceira/exibenormativo?tipo=Carta%20Circular&numero=3339"
fonte_texto: "https://www.bcb.gov.br/api/conteudo/app/normativos/exibenormativo?p1=Carta%20Circular&p2=3339"
sha256_fonte: "402dc9cc4901aadbc56fc7a357964b1795827e8584bdfc63fc2bc6e1cc13949e"
baixado_em: 2026-11-21
---
# Carta Circular nº 3.339, de 11 de setembro de 2008

CARTA-CIRCULAR N. 003339

Divulga procedimentos a serem observados para a operação de participante em regime de con- tingência no Sistema de Trans- ferência de Reservas - STR.

Com base no disposto no art. 4º da Circular 3.100, de 28 de março de 2002, indicamos os procedimentos a serem adotados por parti- cipante do Sistema de Transferência de Reservas - STR para operação em regime de contingência de que trata o art. 44 do regulamento anexo à mencionada circular.

Do serviço de contingência

2. O participante que, por falha ou dificuldade técnica, esti- ver impossibilitado de entregar corretamente suas mensagens, constan- tes do Catálogo de Mensagens do Sistema de Pagamentos Brasileiro, no Gerenciador de Filas - MQ Series do Banco Central do Brasil por in- termédio da Rede do Sistema Financeiro Nacional - RSFN, poderá utili- zar o serviço de inserção de mensagens em regime de contingência.

Do regime de contingência

3. O regime de contingência poderá ser:

I - integral, modalidade em que o participante poderá:

a) enviar direta e simultaneamente mensagens informativas ou de transferência de fundos, por ele digitadas, por intermédio de aplicativo disponível em sítio específico na Internet; e

b) enviar arquivos, por intermédio do Serviço de Transfe- rência de Arquivos do Banco Central - PSTA, que contenham exclusiva- mente mensagens de transferências de fundos do grupo de serviços STR.

II - parcial, modalidade em que o participante poderá soli- citar a inserção, pelo Banco Central do Brasil, das seguintes mensa- gens relativas a ordens de transferência de fundos:

a) LDL0004 - IF requisita Transferência do resultado líqui- do de negociações;

b) LDL0005 - Câmara requisita Transferência do resultado liquido de negociações LDL;

c) LDL0006 - Câmara requisita Transferência por devolução de créditos para IF;

d) LDL0011 - IF requisita Transferência da conta corrente câmara para conta liquidação;

e) LDL0020 - Câmara requisita Transferência do resultado líquido;

f) LDL0022 - IF requisita Transferência para depósito ope- racional;

g) LDL0025 - IF requisita Transferência por devolução de créditos;

h) RCO0010 - IF requisita Transferência recursos de compul- sórios para conta Reservas Bancárias;

i) RCO0011 - IF requisita Transferência de Reservas Bancá- rias para compulsórios, exclusivamente quando se tratar de transfe- rência de fundos destinada à liquidação de obrigações interbancárias decorrentes das sessões diárias da Centralizadora da Compensação de Cheques e Outros Papéis - Compe;

j) RDC0002 - IF requisita Redesconto intradia;

l) RDC0003 - IF requisita Redesconto com prazo de um dia útil;

m) RDC0005 - IF requisita Conversão redesconto intradia em redesconto com prazo de um dia útil ou recontratação de redesconto com prazo de um dia útil;

n) RDC0007 - IF requisita Pagamento de redesconto; e

o) STR0011 - IF requisita Cancelamento de lançamento STR pendente.

Dos procedimentos necessários para utilização do serviço

4. Os participantes deverão manter atualizado, junto ao Depar- tamento de Operações Bancárias e de Sistema de Pagamentos - Deban, cadastro contendo o nome, telefones (inclusive para contatos fora do horário de funcionamento normal do STR), CPF e RG de, no mínimo, três responsáveis pelos procedimentos do regime de contingência. As infor- mações cadastrais deverão ser prestadas por intermédio de correio e- letrônico, transação PMSG750 do Sistema de Informações Banco Central - Sisbacen.

5. As solicitações de entrada e de saída do regime de contin- gência deverão ser feitas por intermédio de contato telefônico origi- nado de responsável autorizado, na forma do item precedente, com o componente da Gerência de Monitoramento do Deban ao qual o solicitan- te estiver vinculado, quando necessitar utilizar o serviço, seguindo os procedimentos descritos no "Manual da Contingência", disponível no sítio da RSFN (www.rsfn.net.br), ocasião em que o participante deverá fornecer chave de segurança para a verificação de autenticidade da solicitação.

6. A solicitação de encerramento da operação em regime de com- tingência observará os procedimentos divulgados no "Manual da Contin- gência", ressalvado que no fechamento diário do STR, caso não tenha havido a solicitação mencionada, o participante retornará à condição de operação normal. Encerrada a utilização do serviço de contingên- cia, o participante deverá solicitar o extrato de sua conta, utili- zando mensagem específica para esse fim, constante do Catálogo de Mensagens.

7. O algoritmo para cálculo da chave de segurança será infor- mado por correspondência encaminhada pelo Deban e os componentes ne- cessários para o cálculo da chave de segurança, quais sejam, a tabela de números randômicos seqüenciais (RDLIST) e a tabela de números ran- dômicos por valor (VLOPER), serão fornecidos preferencialmente por meio eletrônico e devem, juntamente com o algoritmo para o cálculo da chave de segurança, ser objeto de tratamento sigiloso pelo partici- pante, que terá inteira responsabilidade pela sua correta utilização.

8. Para obter as tabelas RDLIST e VLOPER, o participante deve- rá seguir as orientações contidas na correspondência citada no item precedente, bem como as instruções constantes no "Manual da Contin- gência".

9. As tabelas RDLIST e VLOPER poderão ser substituídas, a qualquer momento, por iniciativa do Deban ou por solicitação do par- ticipante, esta mediante envio da mensagem "GEN0014 - Participante requisita Arquivo", observadas as orientações contidas no "Manual da Contingência".

10. Sempre que houver geração de novas tabelas será enviada a mensagem "GEN0015 - GEN avisa Arquivo disponível" e o arquivo será encaminhado conforme o tipo de transmissão solicitado, ocasião em que as tabelas antigas perdem a validade para todos os fins. Os partici- pantes deverão, obrigatoriamente, após o recebimento dessa mensagem, extrair as novas tabelas e validá-las mediante o envio da mensagem "STR0036 - IF requisita Validação das tabelas de contingência".

Do encaminhamento e processamento das mensagens

Contingência Parcial

11. Para a operação no regime de contingência parcial, caberá ao participante fornecer, por telefone, todos os dados necessários para o preenchimento da mensagem a ser enviada.

12. A exatidão dos dados fornecidos durante a utilização do serviço de contingência será de inteira responsabilidade do partici- pante.

Contingência Integral

13. Os procedimentos operacionais para a utilização dos servi- ços de inserção de mensagem e de transmissão de arquivos em regime de contingência estão estabelecidos no "Manual da Contingência".

14. O envio de arquivos, disponível somente aos participantes considerados aptos em testes homologatórios específicos definidos pe- lo Deban, deve obrigatoriamente ocorrer enquanto o participante esti- ver em regime de contingência integral e dentro do horário de funcio- namento do STR para registro de ordens de transferência de fundos previsto no "caput" do art. 9º do regulamento anexo à Circular 3.100, sendo rejeitados os arquivos que não atenderem a essas premissas.

15. O arquivo será submetido à validação, conforme definido no "Manual da Contingência", e o resultado da validação será enviado, pela mesma via, ao participante remetente. Se integralmente válido, será disponibilizado, no sítio da contingência na Internet, o resumo das informações constantes do arquivo para que o participante confir- me ou cancele o seu envio para processamento.

16. O processamento das ordens de transferência de fundos transmitidas por intermédio de arquivo obedecerá, no momento do iní- cio do processamento de cada mensagem, independentemente do horário de transmissão, de validação e de confirmação do arquivo, o horário de funcionamento do STR para registro de ordens de transferência de fundos, conforme disposto no "caput" e no § 1º do art. 9º do regula- mento anexo à Circular 3.100.

17. Arquivos pendentes de confirmação serão cancelados por oca- sião da saída do participante da contingência ou quando do fechamento do STR, o que ocorrer primeiro.

Das disposições finais

18. Durante o período de operação em regime de contingência:

I - os créditos a favor do participante serão efetivados normalmente;

II - as mensagens geradas no sítio da Internet e as mensa- gens recebidas anteriormente à entrada em contingência que, naquele momento, estiverem na fila de espera, serão processadas normalmente, de acordo com a regulamentação em vigor;

III - qualquer tentativa de envio de mensagem pelo partici- pante, por meio da RSFN, resultará em mensagem "GEN0004 - GEN informa Erro de transmissão na mensagem", indicando o código de erro EGEN0021 (ISPB emissora em contingência); e

IV - o participante contará com o suporte do componente da Gerência de Monitoramento do Deban ao qual estiver vinculado.

19. As comunicações telefônicas com os componentes da Gerência de Monitoramento do Deban são gravadas e consideradas firmes e com validade para todos os fins.

20. Esta Carta-Circular entra em vigor na data da sua publica- ção.

21. Fica revogada a Carta-Circular 3.262, de 10 de janeiro de 2007.

Brasília, 11 de setembro de 2008.

Departamento de Operações Bancárias e de Sistema de Pagamentos

Adriana Soares Sales Chefe de Unidade, Substituta
