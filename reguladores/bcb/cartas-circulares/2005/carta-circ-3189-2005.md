---
titulo: "Carta Circular nº 3.189, de 10 de maio de 2005"
orgao: "Banco Central do Brasil"
tipo: "Carta Circular"
tipo_na_fonte: "Carta Circular"
numero: "3189"
data: 2005-05-10
ementa: "Estabelece os requisitos para prestação de serviços de tecnologia no âmbito do Sistema de Pagamentos Brasileiro."
situacao: "revogado"
revogada: true
versao_texto: "texto mantido pelo Banco Central do Brasil no portal de normativos, com as alterações incorporadas e a redação revogada tachada quando houve alteração; não substitui a publicação no Diário Oficial da União"
fonte: "https://www.bcb.gov.br/estabilidadefinanceira/exibenormativo?tipo=Carta%20Circular&numero=3189"
fonte_texto: "https://www.bcb.gov.br/api/conteudo/app/normativos/exibenormativo?p1=Carta%20Circular&p2=3189"
sha256_fonte: "9865d1f10d6f7809e85789a5b54a1d1506040baec039d05ea2e3f536ed56c1fa"
baixado_em: 2026-11-20
---
# Carta Circular nº 3.189, de 10 de maio de 2005

CARTA-CIRCULAR N. 003189

Estabelece os requisitos para prestação de serviços de tecno- logia no âmbito do Sistema de Pagamentos Brasileiro.

Esclarecemos que os Provedores de Serviços de Tecnologia da Informação - PSTI podem prestar serviços para uma ou mais instituições financeiras detentoras de conta Reservas Bancárias, desde que observados os requisitos e as definições referentes à topologia "n x 2", estabelecidos nesta carta-circular, bem como o disposto nos documentos Catálogo de Mensagens do Sistema de Pagamentos Brasileiro, Manual Técnico da Rede do Sistema Financeiro Nacional e Manual de Segurança de Mensagens do Sistema de Pagamentos Brasileiro, instituídos pela Circular 3.104, de 28 de março de 2002, e disponíveis na página do Banco Central do Brasil na internet (www.bcb.gov.br) e na página da Rede do Sistema Financeiro Nacional - RSFN (www.bcb.rsfn.net.br).

2. Considera-se PSTI a entidade que proporciona o encaminha- mento das mensagens originadas das instituições financeiras por ela servidas ou a elas destinadas, observado que:

I - uma instituição financeira somente pode ser PSTI para instituições do conglomerado a que pertencer; e

II - os provedores da RSFN não podem ser PSTI.

3. Define-se "n x 2" a topologia em que "n" significa o número de instituições usuárias de cada serviço compartilhado, e "2" o número mínimo de Centros de Serviços de Informática - CSI que o PSTI deve possuir para a prestação desses serviços.

4. A quantidade máxima de instituições que poderão utilizar os serviços de um PSTI será definida pelo Banco Central do Brasil, em cada caso, observadas a concentração de risco operacional no PSTI e a possibilidade de propagação desse risco, no âmbito do Sistema de Pagamentos Brasileiro - SPB, esclarecido que uma instituição somente pode compartilhar os serviços de um PSTI.

5. A topologia "n x 2" pode ter as seguintes formas de aglutinação de instituições financeiras para efeito de compartilhamento de serviços prestados por um PSTI:

I - Aglomerado: conjunto de instituições financeiras detentoras de conta Reservas Bancárias e não participantes de um mesmo conglomerado financeiro;

II - Conglomerado: conjunto de instituições financeiras detentoras de conta Reservas Bancárias com controlador comum, direto ou indireto, das quais uma presta os serviços típicos de PSTI às demais, mesmo que qualquer das demais seja participante do Sistema de Transferência de Reservas - STR; ou

III - Contingência: conjunto de instituições financeiras detentoras de conta Reservas Bancárias e não integrantes de um mesmo conglomerado financeiro, que utiliza os serviços de um PSTI, exclusivamente em situação de contingência.

6. Na prestação dos serviços, o PSTI deve:

I - manter inalterado o conteúdo das mensagens por ele cursadas;

II - assegurar e preservar o sigilo das informações processadas por seu intermédio;

III- oferecer nível de serviços indiferenciado às insti- tuições financeiras que utilizem seus serviços;

IV - ter disponível, para supervisão pelo Banco Central do Brasil, os programas-fonte de seus programas de acesso ao STR, os diagramas de conexão ao STR e os diagramas de programas, de máquinas e de telecomunicações, envolvendo a instituição e o PSTI, caso os aplicativos sejam providos aos aglomerados;

V - possuir, no mínimo, uma ligação a cada um dos provedores de comunicações da RSFN, em cada um de seus CSI;

VI - possuir, para cada Aglomerado ou Conglomerado, elementos computacionais independentes, assim definidos todas as máquinas, os programas e as aplicações necessários para cursar as mensagens das instituições financeiras;

VII - possuir, no mínimo, dois CSI independentes e interligados, de modo a oferecer funcionamento ininterrupto, observado o índice de 99,8% de operacionalidade.

7. Na prestação dos serviços de Contingência, o PSTI deve, adicionalmente ao previsto nos incisos de I a VI do item 6;

I - garantir, caso os aplicativos sejam por ele providos, o sigilo das informações processadas, quando as instituições compartilharem os servidores de aplicação e infra-estrutura;

II - prover elementos computacionais independentes para cada instituição, assim definidos todas as máquinas e a infra- estrutura necessárias à aplicação, caso os aplicativos sejam providos pelas instituições.

8. A instituição financeira participante de Aglomerado, con- forme definido no inciso I do item 5, deve:

I - zelar pela guarda e integridade de sua chave cripto- gráfica secreta para assinatura digital, que não pode, em nenhuma hipótese, estar localizada nas máquinas servidoras do PSTI;

II - possuir máquinas e programas apropriados para prepa- rar, assinar digitalmente, cifrar e encaminhar suas mensagens;

III - possuir máquinas e programas apropriados para receber, conferir a assinatura digital, decifrar e processar as mensagens que lhe forem encaminhadas;

IV - possuir, no mínimo, uma ligação a cada um dos provedores de comunicações da RSFN, para comunicação com o PSTI a que esteja ligada;

V - ter disponível, para supervisão pelo Banco Central do Brasil, os programas-fonte de seus programas de acesso ao STR, os diagramas de conexão ao STR e os diagramas de programas, de máquinas e de telecomunicações, envolvendo a própria instituição e o PSTI.

9. No caso de Conglomerado, conforme definido no inciso II do item 5:

I - os serviços de processamento de dados das institui- ções financeiras participantes devem ser executados em um único CSI;

II - o PSTI do Conglomerado não pode utilizar CSI de terceiros, hipótese em que passa a atuar sujeito às condições previstas para Aglomerado;

III - cada instituição financeira participante deve possuir seu próprio certificado digital e suas mensagens devem ser assinadas com as chaves privadas relativas ao seu certificado;

10. A instituição financeira que, independentemente da topolo- gia adotada, não puder encaminhar as mensagens relativas à movimenta- ção de sua conta Reservas Bancárias, deve utilizar o serviço de inserção de mensagens em contingência disponibilizado pelo Banco Central do Brasil.

11. O PSTI, ao aderir à RSFN, deve submeter ao Banco Central do Brasil a topologia que pretende utilizar e manter atualizadas as informações pertinentes, as quais estarão sujeitas, assim como os programas-fonte e os diagramas já mencionados e as suas dependências, à fiscalização do Banco Central do Brasil.

12. São admitidas a hospedagem de máquinas e de aplicativos e a utilização de centros de processamento comerciais especializados, desde que observados todos os critérios definidos nesta carta- circular, para as instituições financeiras participantes e para os PSTI.

13. É vedado o trânsito, entre as partes, das chaves criptográ- ficas privadas utilizadas ou de mensagens "em claro".

14. Só é permitido o trânsito de mensagens entre o PSTI e as instituições que dele se utilizam e entre o PSTI e os demais participantes por meio da RSFN.

15. Esta carta-circular entra em vigor na data de sua publica- ção.

16. Fica revogada a Carta-Circular 3.012, de 19 de abril de 2002.

Brasília, 10 de maio de 2005.

Departamento de Operações Bancárias Departamento de Tecnologia da e de Sistema de Pagamentos Informação

José Antonio Marciano Fernando de Abreu Faria Chefe Chefe
