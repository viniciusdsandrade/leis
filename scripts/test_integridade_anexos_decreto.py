from pathlib import Path
import sys, unittest
from types import SimpleNamespace
sys.path.insert(0,str(Path(__file__).resolve().parent))
from integridade_anexos_decreto import anexo_proprio_ausente as gate, _ponteiro_bibliografico_para_revisao, _limpar

P=SimpleNamespace(visual=[],structure=[])
MAIN='DECRETO Nº 52.677\n\nArtigo único. Fica aprovado o Regimento que com êste baixa.\n\nBrasília, 14 de outubro de 1963; 142º da Independência.\n\nJOÃO GOULART\n\nPaulo de Tarso'
class Anexos(unittest.TestCase):
 def test_somente_assinaturas_ou_nota_retem(self):
  self.assertIsNotNone(gate(MAIN,P))
  self.assertIsNotNone(gate(MAIN+'\n\nO Regimento foi publicado no Diário Oficial de 17 de outubro.',P))
 def test_regimento_presente_nao_retem(self):
  self.assertIsNone(gate(MAIN+'\n\nREGIMENTO DA FACULDADE\n\nArt. 1º A Faculdade...',P))
 def test_citacao_de_outro_decreto_nao_retem(self):
  self.assertIsNone(gate(MAIN.replace('que com êste baixa','anexo ao Decreto nº 1.234 de 1960'),P))
 def test_link_tabela_ou_visual_exige_outra_analise(self):
  self.assertIsNotNone(gate(MAIN+'\n\n[Regimento](https://official/anexo)',P))
  self.assertIsNotNone(gate(MAIN+'\n\n<a href="anexo.pdf">ANEXO</a>',P))
  self.assertIsNotNone(gate(MAIN+'\n\nANEXO',P))
  self.assertIsNone(gate(MAIN+'\n\n[ANEXO](#anexo)\n\nANEXO\n\nArt. 1º Ficam fixados os valores.',P))
  self.assertIsNone(gate(MAIN,SimpleNamespace(visual=[],structure=[('table',())])))
  self.assertIsNone(gate(MAIN,SimpleNamespace(visual=['img'],structure=[])))
 def test_placeholder_escapado_nao_e_conteudo(self):
  for label in ['&lt;&lt;ANEXO&gt;&gt;', '&amp;lt;&amp;lt;ANEXO&amp;gt;&amp;gt;', '«ANEXO»', 'TABELAS.', 'ANEXO I', r'\\\Final do documento.']:
   self.assertIsNotNone(gate(MAIN+'\n\n'+label,P),label)
 def test_aprovacao_na_forma_dos_anexos_retem(self):
  self.assertIsNotNone(gate(MAIN.replace('o Regimento que com êste baixa','o Quadro de Pessoal, na forma dos anexos'),P))
 def test_documento_aprovado_sem_palavra_anexo_exige_revisao(self):
  text=MAIN.replace('o Regimento que com êste baixa','o Manual de Procedimentos do Órgão')
  self.assertEqual(gate(text,P)['estado'],'revisao_documental_necessaria')
 def test_objeto_inline_sem_suplemento_nao_retem(self):
  text=MAIN.replace('o Regimento que com êste baixa','a lotação numérica na forma seguinte:\n\n1 - Oficial de Administração\n\n2 - Escriturários')
  self.assertIsNone(gate(text,P))
 def test_alteracao_atomizada_nao_exige_estatuto_inteiro(self):
  text=MAIN.replace('o Regimento que com êste baixa','a alteração do art. 8º do Estatuto, que passa a ter a seguinte redação:\n\nArt. 8º O capital social é de cem unidades')
  self.assertIsNone(gate(text,P))
 def test_regulamento_antes_do_ultimo_fecho_nao_e_rotulo(self):
  text=MAIN.replace('Brasília, 14','Brasília (DF), 14')+'\n\nREGIMENTO\n\nArt. 1º A Faculdade terá cursos.\n\nArt. 2º Os cursos são gratuitos.\n\nBrasília, 14 de outubro de 1963.\n\nMinistro da Educação'
  self.assertIsNone(gate(text,P))
 def test_aprovacao_futura_nao_e_documento_aprovado_agora(self):
  text=MAIN.replace('Fica aprovado o Regimento que com êste baixa','O Diretor exercerá a competência até que seja instalado o Conselho e aprovado o respectivo Regimento')
  self.assertIsNone(gate(text,P))
 def test_relacao_prometida_substituida_por_pontilhado(self):
  text=MAIN.replace('o Regimento que com êste baixa','o enquadramento dos professores, abrangendo os ocupantes a seguir mencionados, a saber:\n\n..........................................\n\nParágrafo único. Permanecem nas cadeiras')
  self.assertIn('pontilhado',gate(text,P)['motivo'])
 def test_relacao_nominal_reproduzida_nao_retem(self):
  text=MAIN.replace('o Regimento que com êste baixa','o enquadramento dos professores, abrangendo os ocupantes a seguir mencionados, a saber:\n\n1. José da Silva - Química\n\n2. Maria dos Santos - Física')
  self.assertIsNone(gate(text,P))
 def test_tabela_depois_da_aprovacao_pode_ser_objeto(self):
  text=MAIN.replace('o Regimento que com êste baixa','a tabela na forma do anexo\n\n<table><tr><td>Valor</td><td>10</td></tr></table>')
  self.assertIsNone(gate(text,SimpleNamespace(visual=[],structure=[('table',())])))
 def test_tabela_anterior_nao_prova_suplemento_posterior(self):
  text='<table><tr><td>Dado anterior</td></tr></table>\n\n'+MAIN
  self.assertIsNotNone(gate(text,SimpleNamespace(visual=[],structure=[('table',())])))
 def test_rotulos_sem_dados_e_nota_de_publicacao_nao_sao_objeto(self):
  text=MAIN+'\n\nQUADRO DE PESSOAL - PARTE PERMANENTE\n\nCONSELHO NACIONAL DE SERVIÇO SOCIAL\n\nSECRETARIA EXECUTIVA\n\n&lt;&lt;TABELA&gt;&gt;\n\nO anexo foi publicado no D.O. de 4-8-72.'
  self.assertIsNotNone(gate(text,P))
 def test_aprovacao_posterior_e_formas_de_anexo(self):
  for obj in ['o anexo Estatuto da Companhia', 'a tabela em anexo', 'as relações nominais anexas', 'o Regimento, de acordo com o texto anexo']:
   text=MAIN.replace('Artigo único. Fica aprovado o Regimento que com êste baixa','Art. 1º Fica aprovado o valor de dez unidades.\n\nArt. 2º Fica aprovado '+obj)
   self.assertIsNotNone(gate(text,P),obj)
 def test_corpo_curto_de_regimento_sem_artigos_e_conteudo(self):
  self.assertIsNone(gate(MAIN+'\n\nREGIMENTO\n\nA Faculdade terá cursos gratuitos.',P))
 def test_inicial_de_assinatura_nao_e_artigo_gramatical(self):
  self.assertIsNotNone(gate(MAIN.replace('JOÃO GOULART','A. COSTA E SILVA'),P))
 def test_eleicao_depois_de_aprovacao_futura_nao_retem(self):
  text=MAIN.replace('Artigo único. Fica aprovado o Regimento que com êste baixa','Art. 2º A eleição se realizará quinze dias depois e aprovado o novo Regimento do HSE')
  self.assertIsNone(gate(text,P))
 def test_modelo_substituido_com_placeholder_nao_e_integral(self):
  text=MAIN.replace('Fica aprovado o Regimento que com êste baixa',
                    'Fica substituída pelo modêlo anexo denominado Guia de Embarque a atual Guia de Exportação')
  for label in ['<<Anexo>>', '&lt;&lt;Anexo&gt;&gt;', '&lt;&lt;Anexo>>']:
   result=gate(text+'\n\n'+label,P)
   self.assertIsNotNone(result,label)
   self.assertEqual(result['estado'],'ausencia_na_transcricao')
 def test_modelo_de_outra_norma_nao_e_objeto_proprio(self):
  text=MAIN.replace('Fica aprovado o Regimento que com êste baixa',
                    'A repartição utilizará o modelo anexo ao Decreto nº 1.234 de 1960')
  self.assertIsNone(gate(text+'\n\n<<Anexo>>',P))
 def test_modelo_substituido_efetivamente_reproduzido(self):
  text=MAIN.replace('Fica aprovado o Regimento que com êste baixa',
                    'Fica substituída pelo modelo anexo denominado Guia de Embarque a atual Guia')
  self.assertIsNone(gate(text+'\n\nANEXO\n\nGUIA DE EMBARQUE\n\nNome do exportador: ______ Endereço: ______ Quantidade: ______',P))
 def test_anexo_bibliografico_sem_fecho_nao_e_conteudo(self):
  text='DECRETO Nº 34.126\n\nArt. 1º Fica aprovada, na forma da relação anexa, a Tabela Numérica Especial.\n\nArt. 2º Este Decreto entra em vigor na data de sua publicação.'
  for label in ['<<ANEXO>> CLBR Vol. 08 Ano 1953 Pág. 250 Tabela.', '&lt;&lt;ANEXO>>CLBR Vol. 08 Ano 1953 Pág. 250 Tabela.', '&amp;lt;&amp;lt;ANEXO&amp;gt;&amp;gt;']:
   self.assertEqual(gate(text+'\n\n'+label,P)['estado'],'ausencia_na_transcricao')
 def test_anexo_externo_sem_fecho_nao_retem(self):
  text='Art. 1º Fica aprovada a utilização da relação anexa ao Decreto nº 10, de 1950.\n\n<<ANEXO>> CLBR Vol. 08 Ano 1953 Pág. 250 Tabela.'
  self.assertIsNone(gate(text,P))
 def test_tabela_reproduzida_sem_fecho_nao_retem(self):
  text='Art. 1º Fica aprovada a tabela anexa.\n\n<table><tr><td>Cargo</td><td>10</td></tr></table>\n\n<<ANEXO>>'
  self.assertIsNone(gate(text,SimpleNamespace(visual=[],structure=[('table',())])))
 def test_relacao_nominal_alterada_sem_formula_de_aprovacao(self):
  article='Art. 1º Fica alterada, na forma da relação anexa, a Tabela Única de Extranumerários-Mensalistas do Ministério da Aeronáutica.\n\nArt. 2º Este Decreto entra em vigor na data de sua publicação.'
  for fecho in ['', '\n\nRio de Janeiro. em 19 de dezembro de 1950; 129º da Independência.\n\nEurico G. Dutra']:
   text=article+fecho+'\n\n&lt;&lt;ANEXO>>CLBR Vol. 08 Ano 1950 Págs. 389 a 392 Tabelas.'
   self.assertEqual(gate(text,P)['estado'],'ausencia_na_transcricao')
 def test_relacao_nominal_de_outra_norma_nao_e_objeto_proprio(self):
  text='Art. 1º Fica alterada, na forma da relação anexa ao Decreto nº 10, de 1950, a tabela de cargos.\n\n<<ANEXO>>'
  self.assertIsNone(gate(text,P))
 def test_relacao_nominal_efetivamente_representada(self):
  text='Art. 1º Fica alterada, na forma da relação anexa, a Tabela Única de Extranumerários-Mensalistas do Ministério da Aeronáutica.\n\n<table><tr><td>Nome</td><td>Cargo</td></tr><tr><td>João</td><td>Professor</td></tr></table>\n\n<<ANEXO>>'
  self.assertIsNone(gate(text,SimpleNamespace(visual=[],structure=[('table',())])))
  self.assertIsNone(gate(text.split('<table>')[0]+'<<ANEXO>>\n\nNome: João. Cargo: Professor.',P))
 def test_modelos_graficos_apos_regulamento_e_tabelas_exigem_revisao(self):
  text=MAIN.replace('o Regimento que com êste baixa','o novo Regulamento que com êste baixa')+'\n\nREGULAMENTO\n\nArt. 1º Os estabelecimentos são regulados.\n\n<table><tr><td>Outro dado</td></tr></table>\n\nArt. 832. Os carimbos devem obedecer à descrição e aos modelos anexos.\n\n<<ANEXO>>CLBR Vol. 06 Ano 1952 Págs. 486 a 492 Carimbos.'
  self.assertEqual(gate(text,SimpleNamespace(visual=[],structure=[('table',())]))['estado'],'revisao_documental_necessaria')
 def test_figuras_do_proprio_regulamento_exigem_revisao(self):
  text=MAIN+'\n\nREGIMENTO\n\nArt. 1º Os uniformes obedecem às figuras anexas.\n\n&lt;&lt;ANEXO>>CLBR Vol. 08 Ano 1951 Págs. 117 a 140 Figuras.'
  self.assertIsNotNone(gate(text,P))
 def test_figuras_com_representacao_ou_regulamento_externo(self):
  text=MAIN+'\n\n<<ANEXO>>CLBR Vol. 08 Ano 1951 Págs. 117 a 140 Figuras.'
  self.assertIsNone(gate(text,SimpleNamespace(visual=['img'],structure=[])))
  external=text.replace('que com êste baixa','anexo ao Decreto nº 1.234 de 1960')
  self.assertIsNone(gate(external,P))
 def test_anexo_numerado_deste_decreto_sem_representacao(self):
  text=MAIN.replace('Fica aprovado o Regimento que com êste baixa','Ficam extintas as funções constantes do Anexo I dêste decreto')
  self.assertEqual(gate(text,P)['estado'],'ausencia_na_transcricao')
 def test_anexos_numerados_reproduzidos_nao_retem(self):
  text=MAIN.replace('Fica aprovado o Regimento que com êste baixa','Ficam extintas as funções constantes dos Anexos I e II dêste decreto')+'\n\nANEXO I\n\n<table><tr><td>Função</td><td>Professor</td></tr></table>\n\nANEXO II\n\n<table><tr><td>Função</td><td>Secretário</td></tr></table>'
  self.assertIsNone(gate(text,SimpleNamespace(visual=[],structure=[('table',())])))
 def test_anexo_numerado_do_decreto_externo_nao_retem(self):
  text=MAIN.replace('Fica aprovado o Regimento que com êste baixa','Ficam extintas as funções constantes do Anexo I do Decreto nº 1.234 de 1960')
  self.assertIsNone(gate(text,P))
class LacunasGraficasEEditoriais(unittest.TestCase):
 def test_parte_rasgada_no_dispositivo_retem(self):
  self.assertEqual(gate('Art. 2º As subcomissões prestarão seu concurso (**Ilegível** parte rasgada no livro.).',P)['estado'],'revisao_documental_necessaria')
 def test_lacunas_nomes_objeto_e_alinea_retem(self):
  for text in ['Art. 1º Vagos em virtude da aposentadoria de Francisco, (ilegível) Marcos Pinheiro.', 'Art. 3º XVI – Recuperação e consertos de peças e móveis (ilegivel).', 'Art. 4º Candidatos sem observância do nº(ilegível).', 'Art. 6º Diploma a que se refere a alínea (ilegivel) do art. 23.']:
   self.assertIsNotNone(gate(text,P),text)
 def test_ilegivel_legitimo_no_servico_postal_nao_retem(self):
  self.assertIsNone(gate('Art. 1º Não será aceita remessa que traga ilegível o nome do destinatário.',P))
 def test_ilegivel_legitimo_no_cancelamento_nao_retem(self):
  self.assertIsNone(gate('Art. 1º A nota é riscada em cruz sem a tornar ilegível; quando a praça fôr desligada, a nota será tornada ilegível.',P))
 def test_definicao_explicita_de_rotulo_nao_retem(self):
  self.assertIsNone(gate('Art. 1º Usar a expressão (ilegível) para classificar documentos sem leitura possível.',P))
 def test_desenhos_medalha_propria_com_placeholder_retem(self):
  text='Art. 1º A Medalha tem as seguintes características, elucidadas nos desenhos anexos.\n\nRio de Janeiro, 22 de outubro de 1947.\n\nAssinatura\n\n&lt;&lt;ANEXO>> CLBR Vol. 08 Ano 1947 Pág. 91 Desenhos.'
  self.assertIn('desenhos anexos',gate(text,P)['remissao'])
 def test_formulario_de_proposta_nao_prova_desenhos_insignias(self):
  text=MAIN+'\n\nREGULAMENTO\n\nArt. 1º A Ordem possui cinco graus.\n\nArt. 3º As insígnias terão as dimensões e características consignadas nas explicações e desenhos anexos.\n\nArt. 29. As propostas seguirão o anexo.\n\nANEXO\n\nNome do candidato ....\n\nGrau ....'
  self.assertIn('art. 3',gate(text,P)['remissao'])
 def test_descricao_uniforme_sem_desenhos_retem(self):
  self.assertIsNotNone(gate('Art. 13. Para a distinção de categorias, serão colocados na gola do uniforme bordados dourados de acordo com os desenhos anexos.',P))
 def test_desenhos_de_norma_externa_nao_retem(self):
  self.assertIsNone(gate('Art. 1º A medalha obedecerá às características dos desenhos anexos ao Decreto nº 123 de 1930.',P))
 def test_alteracao_citada_sem_novo_desenho_nao_retem(self):
  self.assertIsNone(gate('Art. 1º O art. 3º do Decreto nº 123 passa a vigorar com a seguinte redação: As insígnias obedecem às características dos desenhos anexos.',P))
 def test_visual_presente_nao_e_declarado_ausente(self):
  self.assertIsNone(gate('Art. 3º As insígnias terão as dimensões consignadas nos desenhos anexos.',SimpleNamespace(visual=['svg'],structure=[])))

class RegulamentosFuturos(unittest.TestCase):
 def test_desenhos_da_regulamentacao_a_ser_baixada_nao_retem(self):
  for text in ['Art. 2º A Ordem constará de quatro graus, cujas insígnias obedecerão a desenhos anexos à regulamentação a ser baixada pelo Ministro.', 'Art. 2º As insígnias da Ordem obedecerão a desenhos anexos ao regulamento a ser baixado.']:
   self.assertIsNone(gate(text,P))
 def test_futuro_expresso_em_outro_artigo_da_mesma_ordem_nao_retem(self):
  text='Art. 2º As insígnias obedecerão aos desenhos anexos ao regulamento da ordem.\n\nArt. 7º O Regulamento da Ordem Nacional será aprovado pelo Presidente, mediante proposta do Conselho.'
  self.assertIsNone(gate(text,P))
 def test_regulamento_futuro_de_outro_objeto_nao_apaga_desenho_proprio(self):
  text='Art. 1º A Medalha terá as características indicadas nos desenhos anexos.\n\nArt. 3º O regulamento das cerimônias será aprovado posteriormente.'
  self.assertIsNotNone(gate(text,P))


class PrecisaoDeReferentes(unittest.TestCase):
 def test_termo_com_lacuna_nao_e_definicao(self):
  self.assertIsNotNone(gate('Art. 1º O termo de (ilegível) será lavrado.',P))
 def test_rubrica_com_lacuna_nao_e_definicao(self):
  self.assertIsNotNone(gate('Art. 2º A rubrica do (ilegível) figurará no certificado.',P))
 def test_definicao_com_significado_explicito_nao_retem(self):
  self.assertIsNone(gate('Art. 1º A expressão (ilegível) significa documento sem leitura possível.',P))
 def test_rotulo_legitimo_nao_oculta_segunda_lacuna(self):
  self.assertIsNotNone(gate('Art. 1º Usar a expressão (ilegível) para classificação.\n\nArt. 2º O termo de (ilegível) será lavrado.',P))
 def test_aprovacao_propria_nao_e_dispensada_por_cerimonias_futuras(self):
  text='Art. 2º As insígnias obedecerão às características dos desenhos anexos ao regulamento aprovado por este decreto.\n\nArt. 7º O regulamento das cerimônias será aprovado posteriormente.'
  self.assertIsNotNone(gate(text,P))
 def test_regulamento_nomeado_atual_nao_e_dispensado_por_outro_futuro(self):
  text='Art. 1º Fica aprovado o Regulamento da Ordem.\n\nArt. 2º As insígnias obedecerão às características dos desenhos anexos ao regulamento da ordem.\n\nArt. 7º O regulamento das cerimônias será aprovado posteriormente.'
  self.assertIsNotNone(gate(text,P))
 def test_regulamento_futuro_no_mesmo_artigo_de_outro_objeto_nao_dispensa(self):
  text='Art. 2º As insígnias obedecerão às características dos desenhos anexos ao regulamento aprovado por este decreto; o regulamento das cerimônias será aprovado posteriormente.'
  self.assertIsNotNone(gate(text,P))

class Bibliografia(unittest.TestCase):
 def test_quadro_substituido_real24799(self):
  r=gate('Art. 1º Os quadros ficam substituídos pelos quadros que acompanham o presente decreto.\n\n<<ANEXO>>CLBR Vol. 04 Ano 1948 Pág. 54 Tabela.',P)
  self.assertEqual(r['classe'],'ponteiro_bibliografico_nao_certifica_integralidade')
  self.assertFalse(r['ausencia_propria_demonstrada'])
 def test_placeholder_intermediario_real24140(self):
  t='Art. 2º Fica aprovada a lotação com a seguinte distribuição:\n\n<<ANEXO>>CLBR Vol. 08 Ano 1947 Págs. 386 e 387 Tabelas.\n\nArt. 3º Fica aprovada a distribuição na forma da relação anexa.'
  self.assertIsNotNone(gate(t,P))
 def test_substituicao_anexo_alheio_cria_relacao_propria_real24142(self):
  t='Art. 1º As tabelas que acompanharam o Decreto nº 23.405 passam a vigorar com as alterações constantes da relação anexa.\n\n<<ANEXO>>CLBR Vol. 08 Ano 1947 Págs. 397 a 400 Tabelas.'
  self.assertIsNotNone(gate(t,P))
 def test_lista_inline_real18735_exige_revisao_sem_declarar_ausencia(self):
  t='Art. 1º A relação nominal fica alterada de acordo com a relação anexa.\n\nRELAÇÃO NOMINAL\n\n1. Antônio de Oliveira Paiva.\n\n19. Vago.\n\n<<ANEXO>>CLBR Vol. 04 Ano 1945 Págs. 585 a 587 Tabelas.'
  self.assertFalse(gate(t,P)['ausencia_propria_demonstrada'])
 def test_regulamento_art1_nao_oculta_ponteiro_real11451(self):
  t='Art. 1º Fica aprovado o Regulamento.\n\nREGULAMENTO\n\nArt. 1º Organização.\n\nArt. 54 Organiza um mapa dos efetivos (Anexo n. 2).\n\n<<ANEXO>>CLBR Vol. 02 Ano 1943 Pág. 241 Tabela.'
  self.assertIsNotNone(gate(t,P))
 def test_outra_tabela_nao_resolve_ponteiro(self):
  t='Art. 1º Ficam aprovadas as tabelas anexas.\n\n<table><tr><td>Escala salarial</td><td>100</td></tr></table>\n\n<<ANEXO>>CLBR Vol. 04 Ano 1944 Pág. 252 Tabelas.'
  self.assertIsNotNone(gate(t,SimpleNamespace(visual=[],structure=[('table',())])))
 def test_html_nativo_e_duplo_escape(self):
  for marker in ['&lt;&lt;ANEXO&gt;&gt;','&amp;lt;&amp;lt;ANEXO&amp;gt;&amp;gt;','<<ANEXO>>']:
   self.assertIsNotNone(gate('<p><span>'+marker+'CLBR Vol. 08 Ano 1942 Pág. 488. Mapa 1.</span></p>',P))
 def test_remissao_simples_a_outra_norma_nao_retem(self):
  self.assertIsNone(gate('Art. 1º Aplicam-se os valores do anexo ao Decreto nº 2 de 1940.',P))
 def test_placeholder_citado_dentro_de_artigo_nao_prova_omissao(self):
  self.assertIsNone(gate('Art. 1º No catálogo, a expressão <<ANEXO>>CLBR Vol. 08 Ano 1942 Pág. 488 significa remissão bibliográfica.',P))
 def test_modelo_efetivamente_presente_sem_ponteiro(self):
  self.assertIsNone(gate('Art. 1º Fica aprovada a relação seguinte:\n\n1. José da Silva\n\n2. Maria dos Santos',P))
 def test_rotulo_anexo_em_frase_nao_e_endereco_isolado(self):
  self.assertIsNone(gate('Art. 1º Empregar a expressão <<ANEXO>> nos formulários.',P))
 def test_endereco_bibliografico_sem_placeholder_nao_retem(self):
  self.assertIsNone(gate('Art. 1º Consultar a CLBR Vol. 04 Ano 1945 Págs. 585 a 587 para estudo histórico.',P))

class VinculoBibliografico(unittest.TestCase):
 def test_substituta_propria_antes_de_tabela_antiga_real23913(self):
  text='Art. 1º Fica substituída, pela que acompanha o presente Decreto, a tabela anexa ao Decreto nº 22.499, de 1947.\n\n<<ANEXO>>CLBR Vol. 08 Ano 1947 Pág. 99 Tabela.'
  r=_ponteiro_bibliografico_para_revisao(_limpar(text))
  self.assertIsNotNone(r)
  self.assertEqual([v['vinculo_externo_explicito'] for v in r['vinculos_das_remissoes']],[True,False])
 def test_alteracoes_constantes_da_relacao_nova_nao_sao_anexo_antigo(self):
  text='Art. 1º Aplicam-se os critérios da relação anexa ao Decreto nº 10, de 1950.\n\nArt. 2º Ficam estabelecidas as alterações constantes da relação anexa.\n\n<<ANEXO>>CLBR Vol. 08 Ano 1953 Pág. 250 Tabela.'
  r=_ponteiro_bibliografico_para_revisao(_limpar(text))
  self.assertIsNotNone(r)
  self.assertEqual([v['vinculo_externo_explicito'] for v in r['vinculos_das_remissoes']],[True,False])
  self.assertIsNotNone(gate(text,P))
 def test_funcoes_indicadas_em_relacao_nova_nao_sao_anexo_antigo(self):
  text='Art. 1º Mantém-se a tabela anexa ao Decreto nº 10, de 1950.\n\nArt. 2º Ficam criadas as funções indicadas na relação anexa.\n\n<<ANEXO>>CLBR Vol. 08 Ano 1953 Pág. 250 Tabela.'
  r=_ponteiro_bibliografico_para_revisao(_limpar(text))
  self.assertIsNotNone(r)
  self.assertEqual([v['vinculo_externo_explicito'] for v in r['vinculos_das_remissoes']],[True,False])
  self.assertIsNotNone(gate(text,P))

class ObjetoAtualBibliografico(unittest.TestCase):
 def check_current(self,own):
  text='Art. 1º Mantém-se a relação anexa ao Decreto nº 10, de 1950.\n\nArt. 2º '+own+'\n\n<<ANEXO>>CLBR Vol. 04 Ano 1948 Pág. 54 Tabela.'
  r=_ponteiro_bibliografico_para_revisao(_limpar(text))
  self.assertIsNotNone(r)
  self.assertTrue(any(v.get('vinculo_atual_explicito') for v in r['vinculos_das_remissoes']))
  self.assertFalse(r['ausencia_propria_demonstrada'])
  self.assertIsNotNone(gate(text,P))
 def test_quadros_atuais_real24799_apos_anexo_antigo(self):
  for expr in ['Os quadros ficam substituídos pelos quadros que acompanham o presente decreto.', 'Os quadros ficam substituídos pelos quadros que acompanham este decreto.']:
   self.check_current(expr)
 def test_regulamento_que_com_este_baixa_apos_anexo_antigo(self):
  for expr in ['Fica aprovado o regulamento que com este baixa.', 'Ficam aprovados os quadros que com êste baixam.']:
   self.check_current(expr)
 def test_relacao_que_a_este_acompanha_apos_anexo_antigo(self):
  for expr in ['Fica aprovada a relação que a este acompanha.', 'Ficam aprovadas as tabelas que a êste acompanham.']:
   self.check_current(expr)

# Decretos do Império e da Primeira República (normas.leg.br, 20/11/2026), recortados.
IMPERIO=('**DECRETO N. 10.199 - DE 9 DE MARÇO DE 1889**\n\n***Manda executar a Tarifa especial, integral, das Alfandegas da Provincia de S. Pedro do Rio Grande do Sul.***\n\n'
 'Usando da autorisação, concedida no art. 2º, n. 12, da Lei n. 3396 de 24 de Novembro de 1888, Hei por bem Decretar:\n\n'
 '**Art. 1º** As mercadorias mencionadas na Tarifa que acompanha este Decreto, e que forem despachadas, para consumo, nas Alfandegas do Rio Grande, Porto Alegre e Uruguayana, pagarão os direitos estabelecidos na mesma Tarifa.\n\n'
 '**Art. 2º** Continuam em vigor nas referidas Alfandegas as demais disposições dos Regulamentos Fiscaes.\n\n'
 'João Alfredo Corrêa de Oliveira, Conselheiro de Estado, Presidente do Conselho de Ministros, assim o tenha entendido e faça executar. Palacio do Rio de Janeiro aos 9 de Março de 1889, 68º da Independencia e do Imperio.\n\n'
 'Com a rubrica de Sua Magestade o Imperador.\n\nJoão Alfredo Corrêa de Oliveira.')
class FechoHistorico(unittest.TestCase):
 def test_fecho_imperial_no_bloco_do_ministro_retem_tarifa_ausente(self):
  r=gate(IMPERIO,P)
  self.assertIsNotNone(r)
  self.assertEqual(r['estado'],'ausencia_na_transcricao')
 def test_fecho_imperial_com_a_tarifa_reproduzida_nao_retem(self):
  self.assertIsNone(gate(IMPERIO+'\n\nTarifa especial das Alfandegas da Provincia de S. Pedro do Rio Grande do Sul\n\nAlgodão em rama, kilogramma, 0$080',P))
 def test_data_sem_marca_da_era_nao_e_fecho(self):
  self.assertIsNone(gate(IMPERIO.replace(', 68º da Independencia e do Imperio',''),P))
 def test_clausulas_que_a_este_acompanham_reproduzidas_nao_retem(self):
  text=('DECRETO N. 12.155 – DE 2 DE AGOSTO DE 1916\n\nConcede autorização a The Oversea Company of Brazil, Limited, para funccionar na Republica\n\n'
   'O Presidente da Republica dos Estados Unidos do Brazil, attendendo ao que requereu a sociedade anonyma,\n\ndecreta:\n\n'
   '**Artigo unico.** E’ concedida autorização a The Oversea Company of Brazil Limited, para funccionar na Republica mediante as clausulas que a este acompanham.\n\n'
   'Rio de Janeiro 2 de agosto de 1916, 95º da Independencia a 28º da Republica.\n\nWenceslau Braz P. Gomes.\n\nJosé Rufino Beserra Cavalcanti.\n\n'
   'Clausulas que acompanham o decreto n. 12.155, desta data\n\nI\n\nThe Oversea Company of Brazil, Limited, é obrigada a ter um representante geral no Brazil com plenos e illimitados poderes.')
  self.assertIsNone(gate(text,P))
 def test_annexo_de_outro_ato_nao_retem(self):
  text=('DECRETO N. 2303 – DE 2 DE JULHO DE 1896\n\nAbre ao Ministerio da Fazenda o credito supplementar de 600:000$.\n\n'
   'O Presidente da Republica, de accordo com o art. 35 do regulamento annexo ao decreto n. 1166 de 17 de dezembro de 1892,\n\ndecreta:\n\n'
   '**Art. 1º** Fica aberto o credito supplementar de seiscentos contos de réis, de accordo com a tabella annexa ao referido orçamento.\n\n'
   '**Art. 2º** Ficam revogadas as disposições em contrario.\n\nCapital Federal, 2 de julho de 1896, 8º da Republica.\n\nPrudente J. DE Moraes Barros.\n\nFrancisco de Paula Rodrigues Alves.')
  self.assertIsNone(gate(text,P))
 def test_grafia_antiga_approvado_regulamento_que_acompanha_retem(self):
  text=('DECRETO N. 1.363 – DE 13 DE JANEIRO DE 1937\n\nExtende á Caixa de Pensões dos Empregados da Casa da Moeda o regimen do decreto n. 20.465 e approva o respectivo regulamento\n\n'
   'O Presidente da Republica resolve:\n\n**Art. 1º** E’ extensivo á Caixa de Pensões o regimen do decreto n. 20.465, de 1 de outubro de 1931, e approvado o regulamento que ao presente decreto acompanha.\n\n'
   '**Art. 2º** Ficam revogadas as disposições em contrario.\n\nRio de Janeiro, 13 de janeiro de 1937, 116º da Independencia e 49º da Republica.\n\nGetulio Vargas.\n\nAgamemnon Magalhães.')
  self.assertIsNotNone(gate(text,P))
 def test_grafia_antiga_quadro_annexo_ao_presente_decreto_retem(self):
  text=('DECRETO N. 18.093 – DE 9 DE FEVEREIRO DE 1928\n\nO Presidente da Republica decreta:\n\n'
   '**Art. 1º** Os serviços serão distribuidos conforme o quadro annexo ao presente decreto.\n\n**Art. 2º** Revogam-se as disposições em contrario.\n\n'
   'Rio de Janeiro, 9 de fevereiro de 1928, 107º da Independencia e 40º da Republica.\n\nWASHINGTON LUIS P. DE SOUSA.\n\nArnaldo Siqueira Pinto da Luz.')
  self.assertIsNotNone(gate(text,P))

if __name__=='__main__':unittest.main()
