---
titulo: "Carta Circular nº 3.012, de 19 de abril de 2002"
orgao: "Banco Central do Brasil"
tipo: "Carta Circular"
tipo_na_fonte: "Carta Circular"
numero: "3012"
data: 2002-04-19
ementa: "Estabelece os requisitos para prestação de serviços de tecnologia no âmbito do Sistema de Pagamentos Brasileiro."
situacao: "revogado"
revogada: true
versao_texto: "texto mantido pelo Banco Central do Brasil no portal de normativos, com as alterações incorporadas e a redação revogada tachada quando houve alteração; não substitui a publicação no Diário Oficial da União"
fonte: "https://www.bcb.gov.br/estabilidadefinanceira/exibenormativo?tipo=Carta%20Circular&numero=3012"
fonte_texto: "https://www.bcb.gov.br/api/conteudo/app/normativos/exibenormativo?p1=Carta%20Circular&p2=3012"
sha256_fonte: "5cc8778819c87109f98a1ebf2d1cf6529ccb28188cca269cf5f471bdca1a940b"
baixado_em: 2026-11-20
---
# Carta Circular nº 3.012, de 19 de abril de 2002

CARTA-CIRCULAR N. 003012

Estabelece os requisitos para prestação de serviços de tecnologia no âmbito do Sistema de Pagamentos Brasileiro.

Esclarecemos que os Provedores de Serviços de Tecnologia da informação - PSTI podem prestar serviços para uma ou mais instituições financeiras detentoras de conta Reservas Bancárias, desde que observados os requisitos e as definições referentes à topologia "n x 2", estabelecidos nesta carta-circular, bem como o disposto nos documentos Catálogo de Mensagens do Sistema de Pagamentos Brasileiro, Manual Técnico da Rede do Sistema Financeiro Nacional e Manual de Segurança de mensagens do Sistema de Pagamentos Brasileiro, instituídos pela Circular 3.104, de 28 de março de 2002 e disponíveis na página do Banco Central do Brasil na internet (www.bcb.gov.br) e na página da Rede do Sistema Financeiro Nacional - RSFN (www.bcb.rsfn.net.br);

2. Considera-se PSTI a entidade que proporciona o encaminhamento das mensagens originadas das instituições financeiras por ela servidas ou a elas destinadas, observado que:

I) uma instituição financeira somente pode ser PSTI para instituições do conglomerado a que pertencer; e

II) os provedores da RSFN não podem ser PSTI.

3. Define-se "n x 2" (n variando de 1 a 8) a topologia em que "n" significa o número máximo de instituições que podem compartilhar, de forma independente de outros grupos de até oito instituições, os serviços do PSTI e "2" o número mínimo de Centros de Serviços de Informática - CSI possuídos pelo PSTI e utilizados na prestação desses serviços;

4. A topologia "n x 2" pode ter as seguintes formas de aglutinação:

I) AGLOMERADO BANCÁRIO: conjunto de, no máximo, oito instituições financeiras detentoras de conta Reservas Bancárias não participantes de um mesmo conglomerado financeiro, compartilhando os serviços de um PSTI de forma independente de outros aglomerados bancários;

II) CONGLOMERADO: conjunto de até oito instituições financeiras detentoras de conta Reservas Bancarias com controlador comum, direto ou indireto, das quais uma presta os serviços típicos de PSTI, mesmo que qualquer das demais seja participante do Sistema de Transferência de Reservas - STR; ou

III) CONTINGÊNCIA: conjunto de, no máximo, oito institui- ções financeiras detentoras de conta Reservas Bancárias não partici - pantes de um mesmo conglomerado financeiro, compartilhando os servi- ços de um PSTI, apenas em situação de contingência, de forma indepen- dente de outros aglomerados bancários.

5. Na prestação dos serviços para AGLOMERADOS e CONGLOMERA- DOS, o PSTI deve:

I) manter inalterado o conteúdo das mensagens por ele cursadas;

II) assegurar e preservar o sigilo das informações processadas por seu intermédio;

III) oferecer nível de serviços indiferenciado às instituições financeiras participantes de um aglomerado ou conglomerado;

IV) possuir, no mínimo:

a) dois CSI independentes e interligados, de modo a oferecer funcionamento ininterrupto, observado o índice de 99,8% de operacionalidade; e

b) uma ligação a cada um dos provedores de comunicações da RSFN, em cada um de seus CSI;

V) possuir, para cada aglomerado ou conglomerado, elementos computacionais independentes, definindo-se como elementos computacionais todas as máquinas, programas e aplicações necessários para cursar as mensagens das instituições financeiras participantes do aglomerado ou conglomerado;

VI) ter disponível, para supervisão pelo Banco Central do Brasil, os programas-fonte de seus programas de acesso ao STR, os diagramas de conexão ao STR e os diagramas de programas, máquinas e de telecomunicações, envolvendo a instituição e o PSTI, caso os aplicativos sejam providos aos aglomerados.

6. Na prestação dos serviços de CONTINGÊNCIA, o PSTI deve:

I) manter inalterado o conteúdo das mensagens por ele cursadas;

II) assegurar e preservar o sigilo das informações processadas por seu intermédio;

III) oferecer nível de serviços indiferenciado às instituições financeiras que utilizem seus serviços;

IV) possuir, no mínimo, uma ligação a cada um dos provedores de comunicações da RSFN;

V) caso os aplicativos sejam por ele providos:

a) permitir que as instituições possam compartilhar servidores de aplicação e infra-estrutura necessários, desde que garantido o sigilo das informações processadas;

b) ter disponível, para supervisão pelo Banco Central do Brasil, os programas-fonte de seus programas de acesso ao STR, os diagramas de conexão ao STR e os diagramas de programas, máquinas e de telecomunicações, envolvendo a instituição e o PSTI;

VI) prover elementos computacionais independentes para cada instituição, caso os aplicativos sejam providos pelas instituições, definindo-se como elementos computacionais todas as máquinas e infra- estrutura necessárias à aplicação.

7. A instituição financeira participante de AGLOMERADO ban- cário, conforme definido no inciso I do item 4, deve:

I) zelar pela guarda e integridade de sua chave criptográfica secreta para assinatura digital, que não pode, em nenhuma hipótese, estar localizado nas máquinas servidoras do PSTI;

II) possuir máquinas e programas apropriados para preparar, assinar digitalmente, cifrar e encaminhar suas mensagens;

III) possuir máquinas e programas apropriados para receber, conferir a assinatura digital, decifrar e processar as mensagens que lhe forem encaminhadas;

IV) possuir duas ligações à RSFN, para comunicação com o PSTI a que esteja ligada;

V) ter disponível, para supervisão pelo Banco Central do Brasil, os programas-fonte de seus programas de acesso ao STR, os diagramas de conexão ao STR e os diagramas de programas, máquinas e de telecomunicações, envolvendo a própria instituição e o PSTI.

8. No caso de CONGLOMERADO, conforme definido no inciso II do item 4:

I) os serviços de processamento de dados das instituições financeiras participantes devem ser executados em um único CSI;

II) o PSTI do conglomerado não pode ter seu centro de informática terceirizado, caso contrário, o conglomerado passa à condição de aglomerado bancário, sujeitando-se às condições pertinentes;

III) cada instituição financeira participante deve possuir seu próprio certificado digital, devendo suas mensagens serem assinadas com as chaves privadas relativas ao seu certificado;

IV) a instituição financeira que operar como PSTI deve possuir dois CSI independentes e interligados e, no mínimo, duas ligações à RSFN, de modo a oferecer funcionamento ininterrupto, observado o índice de 99,8% de operacionalidade; e

V) ter disponível, para supervisão pelo Banco Central, os programas-fonte de seus programas de acesso ao STR, os diagramas de conexão ao STR e os diagramas de programas, máquinas e de telecomunicações.

9. A instituição, independentemente da topologia adotada, que não puder encaminhar as mensagens relativas à movimentação de sua conta Reservas Bancárias, deverá adotar os procedimentos da contingência oferecida pelo Banco Central do Brasil.

10. Os PSTI, ao aderirem à RSFN, deverão submeter ao Banco Central do Brasil a topologia que pretendem utilizar e manter atualizadas as informações pertinentes, as quais estarão sujeitas à supervisão desta Autarquia, a exemplo dos programas-fonte e dos diagramas já mencionados, bem como à fiscalização das suas dependências.

11. É admitida a hospedagem de máquinas e de aplicativos e a utilização de centros de processamento comerciais especializados, desde que observados todos os critérios definidos nesta carta- circular para as instituições financeiras participantes e para os PSTI.

12. É vedado o trânsito, entre as partes, das chaves criptográficas privadas utilizadas ou de mensagens "em claro".

13. Só é permitido o trânsito de mensagens entre o PSTI e as instituições que dele se utilizam e entre o PSTI e os demais participantes através da RSFN.

14. Esta carta-circular entra em vigor na data de sua publicação.

Brasília, 19 de abril de 2002.

Departamento de Informática Departamento de Operações Bancárias e de Sistema de Pagamentos

José Antônio Eirado Neto Luis Gustavo da Matta Machado Chefe Chefe
