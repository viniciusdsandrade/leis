---
titulo: "Carta Circular nº 3.010, de 19 de abril de 2002"
orgao: "Banco Central do Brasil"
tipo: "Carta Circular"
tipo_na_fonte: "Carta Circular"
numero: "3010"
data: 2002-04-19
ementa: "Esclarece procedimentos para operação de participante em regime de contingência no âmbito do novo Sistema de Pagamentos Brasileiro."
situacao: "revogado"
revogada: true
versao_texto: "texto mantido pelo Banco Central do Brasil no portal de normativos, com as alterações incorporadas e a redação revogada tachada quando houve alteração; não substitui a publicação no Diário Oficial da União"
fonte: "https://www.bcb.gov.br/estabilidadefinanceira/exibenormativo?tipo=Carta%20Circular&numero=3010"
fonte_texto: "https://www.bcb.gov.br/api/conteudo/app/normativos/exibenormativo?p1=Carta%20Circular&p2=3010"
sha256_fonte: "b8cb335d7264843015d95a0abafa2145b673f6917a477dd2cc39c52f25c2403a"
baixado_em: 2026-11-21
---
# Carta Circular nº 3.010, de 19 de abril de 2002

CARTA-CIRCULAR N. 003010

Esclarece procedimentos para operação de participante em regime de contingência no âmbito do novo Sistema de Pagamentos Brasileiro.

Com base no disposto no art. 4. da Circular 3.100, de 28 de março de 2002, informamos os procedimentos a serem adotados por instituição financeira titular de conta Reservas Bancárias e por câmara ou por prestador de serviço de compensação e de liquidação titular de Conta de Liquidação no Banco Central do Brasil, doravante denominada câmara, para operação no regime de contingência de que trata o art. 44 do regulamento anexo à mencionada circular.

2. No caso de falha ou de dificuldade técnica que impossibilite a instituição financeira ou a câmara entregar corretamente suas mensagens no Gerenciador de Filas (MQ Series) do Banco Central do Brasil por meio da Rede do Sistema Financeiro Nacional - RSFN, o Banco Central do Brasil disponibilizará serviço de inserção de mensagens em regime de contingência.

3. O regime de contingência poderá ser:

I- integral, hipótese em que toda e qualquer mensagem de transferência de fundos poderá ser enviada pelo participante; ou

II- parcial, hipótese em que poderá ser solicitada pelo participante a inserção, pelo Banco Central do Brasil, de ordem de transferência de fundos relativa às seguintes mensagens do Catálogo de Mensagens do Sistema de Pagamentos Brasileiro:

a) RCO0011 - IF requisita Transferência Recursos da conta Reservas Bancárias para compulsório, exclusivamente quando se tratar de transferência de fundos destinada à liquidação de obrigações interbancárias decorrentes das sessões diárias da Centralizadora da Compensação de Cheques e Outros Papéis - Compe;

b) LDL0004 - IF requisita Transferência do resultado líquido de negociação;

c) LDL0005 - Câmara requisita Transferência do resultado líquido de negociação LDL;

d) LDL0006 - Câmara requisita Transferência por devolução de créditos para IF;

e) LDL0011 - IF requisita Transferência da conta corrente câmara para conta liquidação; e

f) LDL0027 - IF requisita Cancelamento de lançamento LDL pendente no STR.

4. As instituições financeiras e as câmaras deverão manter atualizado junto ao Departamento de Operações Bancárias e de Sistema de Pagamentos - Deban, cadastro contendo os nomes, telefones (inclusive para contatos fora do horário de funcionamento normal da instituição), CPF e RG de, no mínimo, três responsáveis pelos procedimentos em regime de contingência. As informações deverão ser prestadas por meio de correio eletrônico, transação PMSG750 do Sistema de Informações Banco Central - Sisbacen, e deverão indicar a ordem de preferência entre os responsáveis.

5. Para as solicitações de entrada e de saída do regime de contingência, a instituição financeira ou câmara deverá utilizar-se da chave de segurança para verificação de autenticidade. O algoritmo para o cálculo da chave de segurança é informado por meio de correspondência encaminhada ao participante pelo Banco Central do Brasil.

6. Os componentes necessários para o cálculo da chave de segurança, tabela de números randômicos seqüenciais (RDLIST) e tabela de números randômicos por valor (VLOPER) são fornecidos pelo Banco Central do Brasil, preferencialmente por meio eletrônico, e devem ser objeto de tratamento sigiloso por parte do participante, que terá inteira responsabilidade pela sua correta utilização.

7. Para recuperar as tabelas citadas no item anterior, a instituição financeira ou a câmara deve seguir as orientações contidas na correspondência enviada a cada participante pelo Banco Central do Brasil. A recuperação das tabelas deverá ser feita por meio do acesso aos seguintes endereços na -Internet-, conforme o caso:

I- ftp-t.bcb.rsfn.net.br, caso a instituição esteja em ambiente de teste (homologação); e

II- ftp-p.bcb.rsfn.net.br, caso a instituição esteja em ambiente de produção.

8. As tabelas RDLIST e VLOPER poderão ser substituídas a qualquer momento, por iniciativa do Banco Central do Brasil ou a pedido da instituição ou da câmara.

9. Para solicitar a substituição das tabelas, a instituição financeira ou a câmara deverá enviar correio eletrônico ao Deban, por meio da transação PMSG750 do Sisbacen, com assinatura de dois dos responsáveis por operações em contingência, indicados conforme o item 4 desta carta-circular.

10. Sempre que houver geração de novas tabelas, as instituições financeiras e as câmaras serão informadas por meio da mensagem GEN0010 - GEN informa Tabelas de contingência disponíveis, do Catálogo de Mensagens do Sistema de Pagamentos Brasileiro, e deverão, obrigatoriamente após o recebimento dessa mensagem, recuperar as novas tabelas e validá-las por meio do envio da mensagem GEN0011 - IF requisita Validação das tabelas de contingência.

11. O participante, quando colocado em contingência integral, passará a utilizar diretamente o endereço na -Internet- http://www.bcb.gov.br/spb-contingencia para o registro de suas mensagens que, nessa situação, deverão conter obrigatoriamente a chave de segurança mencionada no item 5.

12. O endereço mencionado no item anterior provê comunicação criptografada por meio do protocolo SSL, com chave de sessão de 128 bits, que permite à instituição ou à câmara elaborar e enviar, de forma segura, por meio da -Internet-, as mensagens destinadas ao Banco Central do Brasil durante o regime de contingência.

13. Para o correto funcionamento do sistema de contingência, a instituição ou a câmara deverá ativar as opções -execução de script- e -gravação de cookies- na sua ferramenta de navegação na -Internet-.

14. Os procedimentos operacionais para entrada, permanência e saída da contingência integral são os descritos a seguir:

I - Entrada em contingência integral:

a) um dos responsáveis pela contingência na instituição financeira ou na câmara, indicado conforme item 4, efetua contato com o Deban, pelo telefone 0xx61-4143396, solicitando entrada em contingência integral; em seguida, envia fax contendo solicitação formal de entrada em contingência, descrição sucinta dos problemas e chave de segurança para confirmação da solicitação;

b) o Deban efetua contato telefônico com um outro responsável, indicado conforme o item 4, para confirmação da entrada em contingência;

c) o Deban insere os dados da solicitação no sistema, sendo efetuada a conferência da chave de segurança. A partir desse momento, e enquanto o participante estiver operando sob o regime de contingência, qualquer tentativa, por parte da instituição financeira ou da câmara, de envio de mensagem por meio da RSFN, obterá como retorno mensagem GEN0004 - GEN Informa erro de transmissão na mensagem, indicando erro EGEN0021 - ISPB emissora em contingência;

d) o acesso, via "browser", ao endereço na -Internet- http://www.bcb.gov.br/spb-contingencia é liberado para registro e envio de mensagens; e

e) o Deban envia fax ao solicitante, contendo data e hora da entrada em contingência, número de controle STR da última ordem de transferência de fundos debitada e saldo da sua conta Reservas Bancárias ou da sua Conta de Liquidação naquele momento.

II - Durante a contingência integral:

a) as mensagens geradas em regime de contingência são processadas normalmente;

b) os créditos a favor da instituição ou da câmara são efetivados normalmente;

c) as mensagens que possuam -Confirm on Arrival - COA- com data/hora anteriores à data/hora da efetiva entrada em contingência são processadas normalmente, ressalvadas as de participantes alcançados pela decretação dos regimes especiais mencionados no art. 16 do regulamento anexo à Circular 3.100, de 28 de março de 2002, quando será observado o disposto no inciso I do parágrafo único daquele artigo;

d) as mensagens recebidas anteriormente à entrada em contingência e que, no momento da entrada em contingência, estiverem eventualmente na fila de espera, são processadas normalmente de acordo com a regulamentação em vigor, aplicando-se, igualmente, a ressalva contida na alínea -e- deste inciso; e

e) a instituição contará com o suporte do Centro de Monitoramento do Deban durante sua operação em contingência, especialmente para acompanhamento de sua conta Reservas Bancárias;

III - Saída da contingência:

a) um dos responsáveis pela contingência na instituição financeira ou na câmara efetua contato com o Deban, pelo telefone 0xx61-4143396, comunicando solução dos problemas e solicitando saída da contingência; em seguida envia fax contendo a solicitação formal de saída da contingência e a chave de segurança para confirmação da solicitação;

b) o Deban efetua contato telefônico com um outro responsável na instituição financeira ou na câmara solicitante, para confirmação da saída da contingência;

c) o Deban insere os dados da solicitação no sistema, sendo efetuada a conferência da chave de segurança; nesse momento é bloqueado o acesso, da instituição financeira ou da câmara solicitante, ao endereço http://www.bcb.gov.br/spb-contingencia e é restabelecido o acesso regular ao Gerenciador de Filas do Banco Central do Brasil;

d) quando da saída da contingência, o Banco Central do Brasil enviará à instituição financeira ou à câmara as mensagens R1 referentes às solicitações processadas, eventuais R2 e mensagens de erro a ela destinadas durante a contingência;

e) o Banco Central do Brasil enviará, ainda, as requisições originais, identificadas pelo número da operação (NUOp) composto pelo ISPB do Banco Central do Brasil, encaminhadas pela instituição financeira ou pela câmara por meio do sistema de contingência, para possibilitar a conciliação com as mensagens R1 e eventuais mensagens de erro que serão recebidas pelo usuário quando da sua saída do regime de contingência;

f) o Deban envia fax ao solicitante, contendo data e hora da saída da contingência, saldo da conta Reservas Bancárias ou da Conta de Liquidação naquele momento; e

g) uma vez encerrada a contingência, a instituição deverá solicitar o extrato de sua conta via mensagem STR0014.

15. Os procedimentos operacionais para a utilização da contingência parcial são os descritos a seguir:

I- Para a entrada em regime de contingência parcial, um dos responsáveis pela contingência na instituição financeira ou na câmara, indicado conforme item 4, efetua contato com o Deban, pelo telefone 0xx61-4143396, solicitando entrada em contingência parcial e informando a chave de segurança para validação da solicitação;

II- o Deban insere os dados da solicitação no sistema, sendo efetuada a conferência da chave de segurança. A partir desse momento, e enquanto o participante estiver operando sob o regime de contingência parcial, qualquer tentativa, por parte da instituição financeira ou da câmara, de envio de mensagem por meio da RSFN, obterá como retorno mensagem GEN0004, indicando erro EGEN0021;

III- por telefone, um dos responsáveis pela contingência na instituição financeira ou na câmara, indicado conforme item 4, informa ao Centro de Monitoramento do Deban as mensagens a serem inseridas em regime de contingência parcial, dentre as estabelecidas no item 3 desta carta-circular, bem como os dados necessários ao seu preenchimento;

IV- o Deban insere as mensagens solicitadas e confirma por telefone sua efetivação;

V- durante a contingência parcial, aplicam-se os procedimentos para a contingência integral, descritos no inciso II do item 14;

VI- para a saída do regime de contingência parcial, um dos responsáveis pela contingência na instituição financeira ou na câmara, indicado conforme item 4, efetua contato com o Deban, pelo telefone 0xx61-4143396, solicitando saída da contingência parcial e informando chave de segurança para validação da solicitação;

VII- quando da saída da contingência, o Banco Central do Brasil enviará à instituição financeira ou à câmara as mensagens R1 referentes às solicitações processadas, eventuais R2 e mensagens de erro a ela destinadas durante a contingência;

VIII- o Banco Central do Brasil enviará, ainda, as requisições originais, identificadas pelo número da operação (NUOp) composto pelo ISPB do Banco Central do Brasil, encaminhadas pela instituição financeira ou pela câmara por meio do sistema de contingência, para possibilitar a conciliação com as mensagens R1 e eventuais mensagens de erro que serão recebidas pelo usuário quando da sua saída do regime de contingência;

16. As ordens e instruções emanadas do Centro de Monitoramento do Deban e por ele recebidas das instituições financeiras e das câmaras por meio de fax ou contato telefônico, são consideradas firmes e com validade para todos os fins.

17. Esta carta-circular entra em vigor na data de sua publicação.

Brasília, 19 de abril de 2002.

Departamento de Operações Bancárias e de Sistema de Pagamentos

Luis Gustavo da Matta Machado Chefe
