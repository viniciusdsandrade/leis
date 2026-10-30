# Contribuindo

Este repositório (fork de [ctresb/leis](https://github.com/ctresb/leis)) consolida o ordenamento jurídico brasileiro em Markdown estruturado. Para manter a integridade de um acervo com centenas de milhares de normas e garantir que os scripts de auditoria passem sem erros, siga as diretrizes abaixo.

---

## 1. Clonando o repositório sem sobrecarregar a máquina

O repositório possui centenas de milhares de commits e múltiplos gigabytes de histórico. **Evite fazer um `git clone` comum**.

### Clone raso (Shallow Clone)
Para contribuir pontualmente com uma norma ou script:
```bash
git clone --depth 1 https://github.com/viniciusdsandrade/leis.git
```

O clone raso não traz a linha do tempo por norma: as normas da base inicial entraram uma por commit, datadas do dia da aprovação, e esse histórico só aparece com o clone completo (ou com `git fetch --unshallow`).

### Sparse Checkout (Recomendado para normas municipais)
Se for trabalhar apenas com uma região (por exemplo, normas municipais de SC), baixe somente o que precisa:
```bash
git clone --depth 1 --filter=blob:none --no-checkout https://github.com/viniciusdsandrade/leis.git
cd leis
git sparse-checkout init --cone
git sparse-checkout set scripts municipais/SC
git checkout main
```

---

## 2. Padrão de Arquivos e Metadados (YAML Frontmatter)

Todo arquivo `.md` tem um cabeçalho YAML, o título principal (`#`) e o texto da norma (veja "Formato dos arquivos" no [README](README.md)).

Campos obrigatórios em **todos** os arquivos: `titulo`, `tipo`, `numero`, `data`, `versao_texto`, `fonte` e `baixado_em`. Os demais entram quando a fonte os fornece (`ementa`, `situacao`, `revogada`, `publicacao`, `data_publicacao`…). Nas normas municipais, `municipio`, `uf` e `codigo_ibge` identificam o município pelo cadastro do IBGE, e os coletores registram também a proveniência do texto: `tipo_na_fonte`, `fonte_texto`, `sha256_fonte` e `sha256_texto`.

Exemplo real, gravado pelo coletor SAPL (`scripts/baixar_organicas_sapl.py`):

```markdown
---
titulo: "Emenda à Lei Orgânica Municipal nº 5, de 18 de abril de 2024"
tipo: "Emenda à Lei Orgânica"
tipo_na_fonte: "Emenda à Lei Orgânica Municipal"
numero: "5"
data: "2024-04-18"
municipio: "Nova Friburgo"
uf: "RJ"
codigo_ibge: "3303401"
versao_texto: "texto integral anexado no SAPL municipal; "
fonte: "https://sapl.novafriburgo.rj.leg.br/norma/2158"
fonte_texto: "https://sapl.novafriburgo.rj.leg.br/media/sapl/public/normajuridica/2024/2158/emenda_5_lo.2018.doc"
sha256_fonte: "f7bfe548ea8eeac3986abb6e055b51850de5895eb9a7702f7b25185fde49cdb5"
sha256_texto: "8b3af4a92fa5c852ccf25c70f959f531ea431c83bfdc7743c956f238a870510e"
baixado_em: "2026-10-30"
---

# Emenda à Lei Orgânica Municipal nº 5, de 18 de abril de 2024

**EMENDA À LEI ORGÂNICA Nº 5**
...
```

Prefira gerar os arquivos pelo coletor existente (ou por um novo coletor) em vez de escrever o cabeçalho à mão: os campos saem na ordem que cada coletor grava, e `sha256_texto` precisa bater com o corpo.

### Regras do vocabulário canônico:
* O `tipo` e a pasta saem do mapa do coletor: `CANONICO` em `scripts/comum.py` (federal e estadual) e `categoria_norma` em `scripts/baixar_organicas_sapl.py` (SAPL municipais). A pasta precisa ser uma das que `scripts/plano.py` mede.
* Apenas o título da norma recebe `#`. A estrutura interna (Título, Capítulo, Seção) pode vir em `###` a `######`, como fazem os conversores; artigos, parágrafos e incisos ficam em texto corrido.

---

## 3. Diretrizes para Scripts de Raspagem (Scrapers)

Ao propor novos baixadores (especialmente para a Fase 3 - Legislação Municipal):
1. **Taxa de requisição:** comece com 1 requisição por segundo por servidor e só suba se o portal aguentar. Os coletores municipais usam de 1 a 3 (`--rps`, via `Rede` de `scripts/comum.py`), e o coletor SAPL recusa mais de 4.
2. **Idempotência:** O script deve verificar se o arquivo `.md` já existe no destino antes de fazer a requisição de download.
3. **Cache de brutos:** Mantenha os arquivos brutos (HTML ou PDFs baixados) em `_fonte/` e os índices em `_indice/`, que o `.gitignore` deixa fora do versionamento, para reprodução futura. Só os documentos de origem de catálogos explícitos (ex.: `municipais/_fonte/capitais/`) entram, com `git add -f`.

---

## 4. Validação Pré-Commit (Obrigatório)

Nenhum Pull Request deve ser submetido sem antes rodar a ferramenta interna de validação. O script valida a sintaxe YAML, existência no calendário e integridade estrutural:

```bash
git add municipais/
python3 -I scripts/auditar.py --staged
```

Em lotes municipais, rode também a auditoria de identidade IBGE, rotas e duplicatas entre lotes:

```bash
python3 scripts/auditar_municipal.py --staged --saida /tmp/auditoria-municipal.json
```

O commit só deve ser criado se os scripts reportarem zero erros e zero problemas.

`PROGRESSO.md` e `progresso.svg` são regenerados pelo hook `.githooks/pre-commit` (ative com `git config core.hooksPath .githooks`) ou à mão com `python3 -I scripts/progresso.py --git-index`.
