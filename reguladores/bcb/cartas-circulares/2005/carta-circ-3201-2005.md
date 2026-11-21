---
titulo: "Carta Circular nº 3.201, de 5 de agosto de 2005"
orgao: "Banco Central do Brasil"
tipo: "Carta Circular"
tipo_na_fonte: "Carta Circular"
numero: "3201"
data: 2005-08-05
ementa: "Esclarece procedimentos para operação de participante em regime de contingência no Sistema de Transferência de Reservas."
situacao: "revogado"
revogada: true
versao_texto: "texto mantido pelo Banco Central do Brasil no portal de normativos, com as alterações incorporadas e a redação revogada tachada quando houve alteração; não substitui a publicação no Diário Oficial da União"
fonte: "https://www.bcb.gov.br/estabilidadefinanceira/exibenormativo?tipo=Carta%20Circular&numero=3201"
fonte_texto: "https://www.bcb.gov.br/api/conteudo/app/normativos/exibenormativo?p1=Carta%20Circular&p2=3201"
sha256_fonte: "f9593705046264d7266e1fdc710ed46fdd9a6ed3f6de20f4b928d7e208e11721"
baixado_em: 2026-11-21
---
# Carta Circular nº 3.201, de 5 de agosto de 2005

CARTA-CIRCULAR N. 003201

Esclarece procedimentos para operação de participante em regime de contin- gência no Sistema de Transferência de Reservas.

Com base no disposto no art. 4º da Circular 3.100, de 28 de março de 2002, informamos os procedimentos a serem adotados por instituição financeira titular de conta Reservas Bancárias e por câmara ou por prestador de serviço de compensação e de liquidação titular de Conta de Liquidação no Banco Central do Brasil, doravante denominada câmara, para operação no regime de contingência de que trata o art. 44 do regulamento anexo à mencionada circular.

2. No caso de falha ou de dificuldade técnica que impossibilite a instituição financeira ou a câmara entregar corretamente suas mensagens no Gerenciador de Filas (MQ Series) do Banco Central do Brasil por meio da Rede do Sistema Financeiro Nacional - RSFN, o Banco Central do Brasil disponibilizará serviço de inserção de mensagens em regime de contingência.

3. As instituições financeiras e as câmaras deverão manter atualizado, junto ao Departamento de Operações Bancárias e de Sistema de Pagamentos - Deban, cadastro contendo os nomes, telefones (inclusive para contatos fora do horário de funcionamento normal da instituição), CPF e RG de, no mínimo, três responsáveis pelos procedimentos em regime de contingência. As informações deverão ser prestadas por meio de correio eletrônico, transação PMSG750 do Sistema de Informações Banco Central - Sisbacen.

4. O regime de contingência poderá ser:

I - integral, hipótese em que toda e qualquer mensagem de transferência de fundos poderá ser enviada pelo participante, por meio da Internet, com possibilidade de envio de mensagens por mais de um operador ao mesmo tempo; ou

II - parcial, hipótese em que o participante poderá solicitar a inserção, pelo Banco Central do Brasil, de ordem de transferência de fundos relativa às seguintes mensagens do Catálogo de Mensagens do Sistema de Pagamentos Brasileiro:

a) LDL0004 - IF requisita Transferência do resultado líqui- do de negociação;

b) LDL0005 - Câmara requisita Transferência do resultado líquido de negociação LDL;

c) LDL0006 - Câmara requisita Transferência por devolução de créditos para IF;

d) LDL0011 - IF requisita Transferência da conta corrente câmara para conta liquidação;

e) LDL0020 - Câmara requisita Transferência do resultado líquido;

f) LDL0022 - IF requisita Transferência para depósito ope- racional;

g) LDL0025 - IF requisita Transferência por devolução de crédito;

h) LDL0027 - IF requisita Cancelamento de lançamento LDL pendente no STR;

i) RCO0011 - IF requisita Transferência Recursos da conta Reservas Bancárias para compulsório, exclusivamente quando se tratar de transferência de fundos destinada à liquidação de obrigações interbancárias decorrentes das sessões diárias da Centralizadora da Compensação de Cheques e Outros Papéis - Compe;

j) RCO0018 - IF requisita Cancelamento de lançamento RCO pendente no STR, exclusivamente quando se tratar de transferência de fundos destinada à liquidação de obrigações interbancárias decorrentes das sessões diárias da Centralizadora da Compensação de Cheques e Outros Papéis - Compe;

l) RDC0002 - IF requisita Redesconto intradia;

m) RDC0003 - IF requisita Redesconto com prazo de um dia útil;

n) RDC0005 - IF requisita Conversão redesconto intradia em redesconto com prazo de um dia útil ou recontratação de redesconto com prazo de um dia útil;

o) RDC0007 - IF requisita Pagamento de redesconto.

5. Para a operação no regime de contingência parcial, caberá ao participante fornecer, por meio telefônico, todos os dados necessários para o preenchimento da mensagem a ser enviada. A exatidão dos dados fornecidos é de inteira responsabilidade do participante.

6. Os procedimentos operacionais para a utilização dos serviços de inserção de mensagem em regime de contingência estão estabelecidos no "Manual de Contingência" disponível na página da RSFN na Internet (www.rsfn.net.br).

7. As solicitações de entrada e de saída do regime de contingência devem ser feitas por meio de contato telefônico com os Centros de Monitoramento do Deban, seguindo os procedimentos descritos no "Manual de Contingência". A instituição financeira ou câmara utilizará, para as solicitações de que se trata, chave de segurança para verificação de autenticidade. O algoritmo para o cálculo da chave de segurança é informado por meio de correspondência encaminhada ao participante pelo Banco Central do Brasil.

8. Os componentes necessários para o cálculo da chave de segurança, tabela de números randômicos seqüenciais (RDLIST) e tabela de números randômicos por valor (VLOPER) são fornecidos pelo Banco Central do Brasil, preferencialmente por meio eletrônico, e devem, juntamente com o algoritmo para o cálculo da chave de segurança, ser objeto de tratamento sigiloso por parte do participante, que terá inteira responsabilidade pela sua correta utilização.

9. Para obter as tabelas citadas no item anterior, a instituição financeira ou a câmara deve seguir as orientações contidas na correspondência enviada a cada participante pelo Banco Central do Brasil, bem como as instruções constantes no "Manual de Contingência".

10. As tabelas RDLIST e VLOPER poderão ser substituídas, a qualquer momento, por iniciativa do Banco Central do Brasil ou a pedido da instituição ou da câmara. O participante deverá solicitar a substituição das tabelas por meio da mensagem "GEN0014 - Participante requisita Arquivo", especificando o tipo de transmissão do arquivo.

11. Sempre que houver geração de novas tabelas, o Banco Central enviará a mensagem "GEN0015 - GEN avisa Arquivo disponível" e o ar- quivo será encaminhado conforme o tipo de transmissão solicitado. A partir desse momento, perdem a validade as tabelas antigas para efei- to de cálculo da chave de segurança. As instituições financeiras e as câmaras deverão, obrigatoriamente, após o recebimento dessa mensagem, obter as novas tabelas e validá-las por meio do envio da mensagem "STR0036 - IF requisita Validação das tabelas de contingência".

12. Durante o período de operação em regime de contingência:

a) as mensagens geradas são processadas normalmente;

b) os créditos a favor da instituição ou da câmara são efetivados normalmente;

c) as mensagens que possuam "Confirm on Arrival - COA" com data/hora anterior à data/hora da efetiva entrada em contingência são processadas normalmente, ressalvadas as de participantes alcançados pela decretação dos regimes especiais mencionados no art. 16 do regulamento anexo à Circular 3.100, de 28 de março de 2002, quando será observado o disposto no inciso I do parágrafo único daquele artigo;

d) as mensagens recebidas anteriormente à entrada em contingência e que, no momento da entrada em contingência, estiverem eventualmente na fila de espera, são processadas normalmente de acordo com a regulamentação em vigor, aplicando-se, igualmente, a ressalva contida na alínea "c" deste inciso; e

e) o participante contará com o suporte do Centro de Monitoramento do Deban ao qual esteja vinculado durante sua operação em contingência, especialmente para acompanhamento de sua conta Reservas Bancárias ou de sua Conta de Liquidação.

13. O encerramento da operação em regime de contingência, por solicitação do participante, observa os procedimentos divulgados no "Manual de Contingência".

14. No fechamento diário do STR o participante retornará automaticamente à condição de operação normal, devendo solicitar no dia útil seguinte a entrada no regime de contingência, caso necessário.

15. Uma vez encerrada a utilização do serviço de contingência, a instituição deverá solicitar o extrato de sua conta, utilizando a mensagem "STR0014 (IF consulta Extrato)".

16. As comunicações com os Centros de Monitoramento do Deban, bem como as ordens e instruções, todas registradas por sistemas de gravação, são consideradas firmes e com validade para todos os fins.

17. Esta carta-circular entra em vigor em 5 de setembro de 2005, quando ficará revogada a Carta-Circular 3.175, de 7 de março de 2005.

Brasília, 5 de agosto de 2005.

Departamento de Operações Bancárias e de Sistema de Pagamentos

Luiz Fernando Cardoso Maciel Chefe de Unidade, substituto
