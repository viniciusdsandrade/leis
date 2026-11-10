Ferramentas da coleta de Campinas/SP (SAPL)
===========================================

Apoio à coleta de municipais/SP/campinas a partir de sapl.campinas.sp.leg.br, feita com
scripts/baixar_organicas_sapl.py. Os caminhos são relativos à raiz do repositório. Os scripts
leem o cache em municipais/_indice/organicas-sapl/sapl.campinas.sp.leg.br e as fontes em
municipais/_fonte/organicas-sapl/sapl.campinas.sp.leg.br, pastas que ficam fora do Git.
Rodar com `python3 -I scripts/municipios/campinas/<script>.py`.

Script                 Função                                                                     Rede
---------------------  -------------------------------------------------------------------------  ----
campinas.py            verificar (identidade dos .md contra o índice da API), carimbos            não
                       (carimbos residuais) e regenerar (refaz o corpo a partir do PDF em
                       cache e compara com o gravado)
campinas_regenerar.py  Refaz o corpo dos .md com o código atual e compara com o gravado           não
cobertura.py           Mede, por ano, quantas normas de um tipo têm texto integral no SAPL        sim
prefetch.py            Pré-baixa índice e PDFs de um tipo por ano nos caminhos de cache           sim
simular_ano.py         Simula a conversão de um ano a partir do cache, sem gravar                 não
retidas.py             Lista as normas sem .md nos índices parciais e classifica o motivo         não
trocados.py            Acha PDFs anexados à norma errada no SAPL                                  não
sem_epigrafe.py        Lista .md cujo corpo não traz a epígrafe da própria norma                  não
antiga.py              Testa a epígrafe antiga dos livros de leis contra o acervo                 não
conversor_novo.py      Rascunho do conversor PDF para MD com cabeçalho e rodapé só nas bordas     não
medir_conversor.py     Regenera os .md de Campinas com o conversor novo e classifica o que muda   não
medir_outros.py        Compara o conversor atual e o novo nos PDFs em cache fora de Campinas      não

`regenerar` refaz o corpo na mesma ordem do pipeline (carimbos e, quando versao_texto anota o recorte, o ato
próprio da página de livro de leis) e também confere os .md do bibjuri a partir do HTML em cache.
Testes destas ferramentas: test_campinas.py nesta pasta, rodado localmente (o CI não faz checkout de scripts/municipios/).

Em `verificar`, um .md cuja ficha do SAPL não tem anexo passa quando `fonte_texto` aponta uma página de norma
do bibjuri (lotes de baixar_bibjuri_campinas.py); anos sem índice parcial são lidos das páginas da API em cache.
O mesmo vale para a edição do Diário Oficial do Município no portal da Prefeitura (lotes de
scripts/baixar_dom_campinas.py, que recorta o decreto do PDF da edição lido coluna a coluna); `regenerar` refaz esses
.md a partir do PDF em municipais/_fonte/dom-campinas.

Tipos do SAPL de Campinas usados em --tipo e em cobertura.py/prefetch.py: 1 Lei, 2 Lei
Complementar, 4 Decreto, 7 Decreto Legislativo, 8 Resolução, 9 Emenda à Lei Orgânica, 17
Decreto-lei, 18 Leis até 1948, 19 Decretos até 1948, 20 Resoluções até 1948, 21 Lei Orgânica.

Snapshot do cache (31/10/2026)
------------------------------

Cópias em scripts/dados/ do que o pipeline guarda fora do Git e que custaria horas de rede refazer:

- campinas-sapl-retidos-integralidade-20261031.json: 292 normas retidas, com o motivo de cada uma.
- campinas-sapl-falhas-20261031.jsonl: última falha registrada por id do SAPL (3.114 ids).
- campinas-sapl-equivalencias-20261031.json: ids do SAPL equivalentes a .md já publicados.
- campinas-sapl-cobertura-decretos-20261031.json: por ano, total de decretos (tipo 4) e ids com
  texto integral, de 1934 a 2026.
- campinas-sapl-retencao-decretos-lote1-20261031.json: motivos de retenção do primeiro lote de decretos.

Para restaurar o cache, copiar os três primeiros para
municipais/_indice/organicas-sapl/sapl.campinas.sp.leg.br/ com os nomes originais
(retidos-integralidade.json, falhas.jsonl, equivalencias.json). Os índices parciais por ano e os
PDFs das fontes (4 GB) não têm cópia no Git: prefetch.py refaz os dois a partir do SAPL.
