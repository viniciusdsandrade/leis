---
titulo: "Carta Circular nº 3.520, de 29 de agosto de 2011"
orgao: "Banco Central do Brasil"
tipo: "Carta Circular"
tipo_na_fonte: "Carta Circular"
numero: "3520"
data: 2011-08-29
ementa: "Altera os procedimentos e padrões técnicos para uso de assinatura digital em contratos de câmbio."
situacao: "revogado"
revogada: true
versao_texto: "texto mantido pelo Banco Central do Brasil no portal de normativos, com as alterações incorporadas e a redação revogada tachada quando houve alteração; não substitui a publicação no Diário Oficial da União"
fonte: "https://www.bcb.gov.br/estabilidadefinanceira/exibenormativo?tipo=Carta%20Circular&numero=3520"
fonte_texto: "https://www.bcb.gov.br/api/conteudo/app/normativos/exibenormativo?p1=Carta%20Circular&p2=3520"
sha256_fonte: "cef4c54d2f4d02b870e901d383b05fb406b43601ab7b55f7648739c687d87222"
baixado_em: 2026-11-20
---
# Carta Circular nº 3.520, de 29 de agosto de 2011

CARTA-CIRCULAR N. 003520

Altera os procedimentos e padrões técnicos para uso de assinatura digital em contratos de câmbio.

O Chefe do Departamento de Tecnologia da Informação (DEINF), no uso da atribuição que confere o art. 22, inciso I, alínea "a", do Regimento Interno do Banco Central do Brasil, anexo à Portaria nº 29.971, de 4 de março de 2005, em decorrência do disposto no Título 1 - Capítulo 3 - Seção 1 do Regulamento do Mercado de Câmbio e Capitais Internacionais - RMCCI,

R E S O L V E:

**Art. 1º** Os agentes autorizados a operar no mercado de câmbio que façam uso de assinatura digital em contratos de câmbio devem adotar os seguintes procedimentos:

I - os certificados digitais utilizados na assinatura de contratos de câmbio devem ser emitidos por Autoridades Certificadoras no âmbito da Infraestrutura de Chaves Públicas Bra- sileira- ICP - Brasil, instituída pela Medida Provisória MP 2.200-2, de 24 de agosto de 2001, e podem ser do tipo A1, A2, A3 ou A4, a critério da parte contratante autorizada a operar no mercado de câmbio;

II - o arquivo base oferecido para assinatura digital deve ser produzido exclusivamente nos formatos texto (código ASCII) ou PDF (Portable Document Format), contendo as condições estipuladas entre as partes;

III - as assinaturas digitais dos contratos de câmbio devem adotar exclusivamente um dos padrões técnicos aqui descritos, mesmo no caso de arquivos PDF, para os quais possam existir protocolos proprietários de assinatura.

**Art. 2º** Devem ser observados pela parte contratante autorizada a operar no mercado de câmbio, os seguintes padrões técnicos:

I - o formato do arquivo contendo o contrato de câmbio assinado digitalmente deve adotar o padrão de assinatura digital com Referência Básica (AD-RB) ou com Referência de Tempo (AD-RT), conforme definido nos documentos DOC-ICP-15 e detalhamentos, regulamentados pela Resolução nº 76, de 31/3/2010, do Comitê Gestor da ICP-Brasil;

II - para geração do "digest" (resumo do documento) devem ser utilizados os algoritmos de "hashing" SHA-1 (RFC 3174) ou SHA- 256 (RFC 4634);

III - na assinatura digital deve ser utilizado o algoritmo assimétrico RSA, com uso das respectivas chaves privadas das partes para cifragem do "digest" do documento, no padrão PKCS#1 (RFC 2313);

IV - cada assinatura deve ser executada considerando o atributo "signingTime" no campo "signedAttributes" da estrutura "SignerInfos", refletindo a data-hora de sua efetivação, sendo que todas as assinaturas assim obtidas devem estar dispostas como coassinaturas. A data e hora de efetivação devem ser controladas pela contratante.

**Art. 3º** Excepcionalmente para os contratos produzidos até 31/12/2012, para efeito de compatibilidade e transição com a sistemática vigente, a parte contratante autorizada a operar no mercado de câmbio poderá adotar os seguintes padrões técnicos:

I - o formato do arquivo contendo o contrato de câmbio assinado digitalmente deve adotar o padrão Public-Key Cryptography Standard nº 7 (PKCS#7), versão 1.5, conforme detalhado no "Request for Comments" (RFC) 2315, do Internet Engineering Task Force - IETF, com a estrutura "ContentType" igual a "SignedData" e com o conteúdo do contrato de câmbio presente no campo "content" da estrutura "contentInfo";

II - para geração do "digest" (resumo do documento) deve ser utilizado o algoritmo de "hashing" SHA-1 (RFC 3174);

III - na assinatura digital deve ser utilizado o algoritmo assimétrico RSA, com uso das respectivas chaves privadas das partes para cifragem do "digest" do documento, no padrão PKCS#1 (RFC 2313);

IV - cada assinatura deve ser executada considerando o atributo "signingTime" no campo "authenticatedAttributes" da estrutura "SignerInfo", refletindo a data-hora de sua efetivação, sendo que todas as assinaturas assim obtidas devem estar no mesmo nível na estrutura do PKCS#7, pela repetição do campo "SignerInfo" da estrutura "SignedData", tantas vezes quantas forem o número de assinaturas digitais apostas. A data e hora de efetivação devem ser controladas pela contratante.

**Art. 4º** O arquivo resultante, contendo o contrato de câmbio (representação attached), as assinaturas digitais geradas e os respectivos certificados digitais utilizados, deve ser armazenado pelo prazo que a regulamentação cambial determinar. É opcional o armazenamento dos certificados digitais das Autoridades Certificadoras participantes da cadeia de confiança, bem como das respectivas Listas de Certificados Revogados (LCRs).

**Art. 5º** Para efeito de apresentação ao Banco Central do Brasil, quando solicitado, a contratante deve manter ou extrair cópia em claro dos arquivos, sem envelopamento para cifragem. Caso exista a necessidade de cifrar os dados para segurança adicional na guarda ou transmissão pode, para tal, fazer uso de qualquer padrão.

**Art. 6º** Esta carta circular entra em vigor na data de sua publicação, produzindo seus efeitos a partir de 3 de outubro de 2011, quando fica revogada a Carta Circular nº 3.134, de 27 de abril de 2004.

Brasília-DF, 29 de agosto de 2011

Marcelo Jose Oliveira Yared
