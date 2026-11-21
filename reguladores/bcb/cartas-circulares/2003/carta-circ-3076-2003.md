---
titulo: "Carta Circular nº 3.076, de 3 de janeiro de 2003"
orgao: "Banco Central do Brasil"
tipo: "Carta Circular"
tipo_na_fonte: "Carta Circular"
numero: "3076"
data: 2003-01-03
ementa: "Esclarece procedimentos para operação de participante em regime de contingência no âmbito do Sistema de Pagamentos Brasileiro."
situacao: "revogado"
revogada: true
versao_texto: "texto mantido pelo Banco Central do Brasil no portal de normativos, com as alterações incorporadas e a redação revogada tachada quando houve alteração; não substitui a publicação no Diário Oficial da União"
fonte: "https://www.bcb.gov.br/estabilidadefinanceira/exibenormativo?tipo=Carta%20Circular&numero=3076"
fonte_texto: "https://www.bcb.gov.br/api/conteudo/app/normativos/exibenormativo?p1=Carta%20Circular&p2=3076"
sha256_fonte: "ad75e8d60f2f91b5ab38b48e22eac3d1906d958593f8ccdaf2667b09e2506564"
baixado_em: 2026-11-21
---
# Carta Circular nº 3.076, de 3 de janeiro de 2003

CARTA-CIRCULAR N. 003076

Esclarece procedimentos para operação de participante em regime de contingência no âmbito do Sistema de Pagamentos Bra- sileiro.

Com base no disposto no art. 4. da Circular 3.100, de 28 de março de 2002, informamos os procedimentos a serem adotados por instituição financeira titular de conta Reservas Bancárias e por câmara ou por prestador de serviço de compensação e de liquidação titular de Conta de Liquidação no Banco Central do Brasil, doravante denominada câmara, para operação no regime de contingência de que trata o art. 44 do regulamento anexo à mencionada circular.

2. No caso de falha ou de dificuldade técnica que impossibilite a instituição financeira ou a câmara entregar corretamente suas mensagens no Gerenciador de Filas (MQ Series) do Banco Central do Brasil por meio da Rede do Sistema Financeiro Nacional - RSFN, o Banco Central do Brasil disponibilizará serviço de inserção de mensagens em regime de contingência.

3. As instituições financeiras e as câmaras deverão man- ter atualizado, junto ao Departamento de Operações Bancárias e de Sistema de Pagamentos - Deban, cadastro contendo os nomes, telefones (inclusive para contatos fora do horário de funcionamento normal da instituição), CPF e RG de, no mínimo, três responsáveis pelos procedimentos em regime de contingência. As informações deverão ser prestadas por meio de correio eletrônico, transação PMSG750 do Sistema de Informações Banco Central - Sisbacen.

4. O regime de contingência poderá ser:

I - integral, hipótese em que toda e qualquer mensagem de transferência de fundos poderá ser enviada pelo participante, por meio da Internet, com possibilidade de envio de mensagens por mais de um usuário ao mesmo tempo; ou

II - parcial, hipótese em que o participante poderá solicitar a inserção, pelo Banco Central do Brasil, de ordem de transferência de fundos relativa às seguintes mensagens do Catálogo de Mensagens do Sistema de Pagamentos Brasileiro:

a) LDL0004 - IF requisita Transferência do resultado líquido de negociação;

b) LDL0005 - Câmara requisita Transferência do resul- tado líquido de negociação LDL;

c) LDL0006 - Câmara requisita Transferência por devo- lução de créditos para IF;

d) LDL0011 - IF requisita Transferência da conta cor- rente câmara para conta liquidação;

e) LDL0020 - Câmara requisita Transferência do resul- tado líquido;

f) LDL0022 - IF requisita Transferência para depósito operacional;

g) LDL0025 - IF requisita Transferência por devolução de crédito;

h) LDL0027 - IF requisita Cancelamento de lançamento LDL pendente no STR;

i) RCO0011 - IF requisita Transferência Recursos da conta Reservas Bancárias para compulsório, exclusivamente quando se tratar de transferência de fundos destinada à liquidação de obriga- ções interbancárias decorrentes das sessões diárias da Centralizadora da Compensação de Cheques e Outros Papéis - Compe;

j) RCO0018 - IF requisita Cancelamento de lançamento RCO pendente no STR, exclusivamente quando se tratar de transferência de fundos destinada à liquidação de obrigações interbancárias decor- rentes das sessões diárias da Centralizadora da Compensação de Che- ques e Outros Papéis - Compe;

l) RDC0002 - IF requisita Redesconto intradia;

m) RDC0003 - IF requisita Redesconto com prazo de um dia;

n) RDC0005 - IF requisita Conversão redesconto intra- dia em redesconto com prazo de um dia ou recontratação de redesconto com prazo de um dia;

o) RDC0007 - IF requisita Pagamento de redesconto.

5. Os procedimentos operacionais para a utilização dos serviços de inserção de mensagem em regime de contingência estão es- tabelecidos no "Manual de Contingência" disponível na página da RSFN na Internet (www.rsfn.net.br).

6. As solicitações de entrada e de saída do regime de contingência devem ser feitas por meio de contato telefônico com o Deban, seguindo os procedimentos descritos no "Manual de Contingên- cia". A instituição financeira ou câmara utilizará, para as solicita- ções de que se trata, chave de segurança para verificação de autenti- cidade. O algoritmo para o cálculo da chave de segurança é informado por meio de correspondência encaminhada ao participante pelo Banco Central do Brasil.

7. Os componentes necessários para o cálculo da chave de segurança, tabela de números randômicos seqüenciais (RDLIST) e tabela de números randômicos por valor (VLOPER) são fornecidos pelo Banco Central do Brasil, preferencialmente por meio eletrônico, e devem, juntamente com o algoritmo para o cálculo da chave de segurança, ser objeto de tratamento sigiloso por parte do participante, que terá in- teira responsabilidade pela sua correta utilização.

8. Para obter as tabelas citadas no item anterior, a ins- tituição financeira ou a câmara deve seguir as orientações contidas na correspondência enviada a cada participante pelo Banco Central do Brasil, bem como as instruções constantes no "Manual de Contingên- cia".

9. As tabelas RDLIST e VLOPER poderão ser substituídas, a qualquer momento, por iniciativa do Banco Central do Brasil ou a pe- dido da instituição ou da câmara. Para solicitar a substituição das tabelas, o participante deverá enviar correio eletrônico ao Deban, por meio da transação PMSG750 do Sisbacen, com assinatura de dois dos responsáveis por operações em contingência, indicados conforme o item 3 desta carta-circular.

10. Sempre que houver geração de novas tabelas, o Banco Central enviará a mensagem "GEN0010 - GEN informa Tabelas de contin- gência disponíveis", do Catálogo de Mensagens, e, a partir desse mo- mento, perdem validade as tabelas antigas para efeito de cálculo da chave de segurança. As instituições financeiras e as câmaras deverão, obrigatoriamente, após o recebimento dessa mensagem, obter as novas tabelas e validá-las por meio do envio da mensagem "GEN0011 - IF re- quisita Validação das tabelas de contingência".

11. Durante o período de operação em regime de contingên- cia:

a) as mensagens geradas são processadas normalmente;

b) os créditos a favor da instituição ou da câmara são efetivados normalmente;

c) as mensagens que possuam "Confirm on Arrival - COA" com data/hora anterior à data/hora da efetiva entrada em contingência são processadas normalmente, ressalvadas as de participantes alcança- dos pela decretação dos regimes especiais mencionados no art. 16 do regulamento anexo à Circular 3.100, de 28 de março de 2002, quando será observado o disposto no inciso I do parágrafo único daquele ar- tigo;

d) as mensagens recebidas anteriormente à entrada em contingência e que, no momento da entrada em contingência, estiverem eventualmente na fila de espera, são processadas normalmente de acor- do com a regulamentação em vigor, aplicando-se, igualmente, a ressal- va contida na alínea "c" deste inciso; e

e) a instituição contará com o suporte do Centro de Monitoramento do Deban durante sua operação em contingência, especi- almente para acompanhamento de sua conta Reservas Bancárias.

12. O encerramento da operação em regime de contingência observa os procedimentos divulgados no "Manual de Contingência".

13. Uma vez encerrada a utilização do serviço de contin- gência, a instituição deverá solicitar o extrato de sua conta, utili- zando a mensagem "STR0014 (IF consulta Extrato)".

14. As ordens e instruções emanadas do Centro de Monitora- mento do Deban e por ele recebidas das instituições financeiras e das câmaras, por meio de fax ou contato telefônico, são consideradas fir- mes e com validade para todos os fins.

15. Esta carta-circular entra em vigor em 6 de janeiro de 2003, quando ficará revogada a Carta-Circular 3.040, de 30 de agosto de 2002.

Brasília, 03 de janeiro de 2003.

Departamento de Operações Bancárias e de Sistema de Pagamentos

José Antonio Marciano Chefe de Unidade
