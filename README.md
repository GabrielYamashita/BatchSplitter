# Batch Splitter

Sistema Streamlit para separar bases CSV de acionamento em lotes menores, usando schemas configuráveis por projeto e template.

O objetivo é padronizar o processamento de bases recebidas de diferentes clientes, mesmo quando cada base usa nomes de colunas, delimitadores e estruturas diferentes.

A aplicação permite:

- selecionar um projeto e um template;
- fazer upload de uma base CSV;
- detectar o separador do arquivo;
- mapear colunas automaticamente por aliases;
- corrigir o mapeamento manualmente quando necessário;
- visualizar a base de saída;
- dividir a base em lotes;
- gerar os arquivos finais em um ZIP.

---

## Visão geral

O Batch Splitter funciona com uma arquitetura baseada em schemas.

Cada projeto possui um `project.yaml` com configurações padrão. Cada template possui um YAML próprio com as regras específicas daquela campanha ou operação.

Com isso, novos projetos e templates podem ser adicionados sem alterar o código principal da aplicação.

Exemplo de estrutura:

```txt
schemas/
└─ afinz/
   ├─ project.yaml
   └─ templates/
      └─ informar_pendencia_maior_60.yaml
```

---

## Principais funcionalidades

### Upload e leitura de CSV

A aplicação lê bases CSV e tenta detectar automaticamente:

- delimitador;
- encoding;
- colunas disponíveis;
- quantidade de linhas;
- estrutura inicial da base.

### Mapeamento de colunas

O mapeamento é feito por aliases definidos nos schemas.

Exemplo:

```yaml
telefone:
  required: true
  output_name: TEL_DEEP
  aliases:
    - telefone
    - celular
    - phone
    - nrtelefonecompleto
```

Se a base enviada tiver uma coluna chamada `NrTelefoneCompleto`, ela pode ser mapeada automaticamente para `TEL_DEEP`.

### Mapeamento manual

Quando o mapeamento automático não consegue validar todos os campos obrigatórios, a interface exibe uma seção de mapeamento manual.

Nessa seção, o usuário pode selecionar qual coluna da base corresponde a cada campo esperado pelo template.

### Saída preservando colunas

A aplicação mantém todas as colunas da base de entrada.

As colunas mapeadas são renomeadas conforme o schema. As demais colunas permanecem sem alteração.

Exemplo:

```txt
Entrada:
NrCpfCnpj;FirstName;IdCaso;NrTelefoneCompleto

Saída:
CPF;nome;IdCaso;TEL_DEEP
```

Nesse caso:

- `NrCpfCnpj` foi renomeado para `CPF`;
- `FirstName` foi renomeado para `nome`;
- `NrTelefoneCompleto` foi renomeado para `TEL_DEEP`;
- `IdCaso` foi mantido sem alteração.

### Divisão em lotes

O usuário define:

- quantidade de clientes por arquivo;
- número do lote;
- data do lote;
- limite percentual de remanescente.

A regra de remanescente define quando a sobra vira um novo arquivo ou é juntada ao arquivo anterior.

Exemplo com 2.501 clientes:

```txt
Clientes por lote: 1000
Limite de remanescente: 50%

Resultado:
Arquivo 01: 1000 clientes
Arquivo 02: 1000 clientes
Arquivo 03: 501 clientes
```

### Exportação em ZIP

Os arquivos CSV finais são gerados em memória e disponibilizados em um ZIP para download.

Exemplo de nomes gerados:

```txt
Afinz_PENDENCIA_MAIOR_60_Lote05_01_0307.csv
Afinz_PENDENCIA_MAIOR_60_Lote05_02_0307.csv
Afinz_PENDENCIA_MAIOR_60_Lote05_03_0307.csv
```

---

## Estrutura do projeto

```txt
batch-splitter/
├─ app.py
├─ requirements.txt
├─ README.md
├─ .gitignore
├─ .streamlit/
│  └─ config.toml
├─ core/
│  ├─ engine.py
│  ├─ batching/
│  ├─ export/
│  ├─ io/
│  ├─ mapping/
│  ├─ output/
│  ├─ preprocessing/
│  ├─ preview/
│  ├─ schemas/
│  └─ validation/
├─ schemas/
│  └─ <project_id>/
│     ├─ project.yaml
│     └─ templates/
│        └─ <template_id>.yaml
└─ tests/
   └─ manual/
```

---

## Como rodar localmente

### 1. Criar ambiente virtual

```powershell
python -m venv .venv
```

### 2. Ativar ambiente virtual

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Instalar dependências

```powershell
pip install -r requirements.txt
```

### 4. Rodar aplicação

```powershell
streamlit run app.py
```

---

## Variáveis e secrets

A aplicação usa uma senha simples para proteger o acesso.

### Local

Crie o arquivo:

```txt
.streamlit/secrets.toml
```

Com:

```toml
APP_PASSWORD = "sua_senha_aqui"
```

Esse arquivo não deve ser commitado.

### Streamlit Cloud

Configure o secret no painel do app:

```toml
APP_PASSWORD = "sua_senha_aqui"
```

---

## Como criar um novo projeto

Crie uma nova pasta dentro de `schemas/`.

Exemplo:

```txt
schemas/recovery/
├─ project.yaml
└─ templates/
   └─ cobranca_varejo_11.yaml
```

### Exemplo de `project.yaml`

```yaml
id: recovery
name: Recovery
active: true

input:
  auto_detect_delimiter: true
  delimiter_candidates: [";", ",", "|", "\t"]
  encoding_fallbacks: ["utf-8", "utf-8-sig", "latin1"]

cleaning:
  drop_empty_rows: true
  drop_empty_columns: true
  drop_unnamed_columns: true
  normalize_column_names: true

batch:
  default_size: 1000
  remainder_threshold_percent: 50
  default_batch_num: 1

output:
  delimiter: ";"
  encoding: utf-8-sig
  extension: csv
  include_header: true
  filename_pattern: "{name}_{prefix}_Lote{batch_num}_{file_num}_{date}.csv"

fields:
  cpf:
    required: true
    output_name: CPF
    aliases:
      - cpf
      - documento
      - nrcpfcnpj

  nome:
    required: true
    output_name: nome
    aliases:
      - nome
      - nome cliente
      - firstname

  telefone:
    required: true
    output_name: TEL_DEEP
    aliases:
      - telefone
      - celular
      - nrtelefonecompleto
```

---

## Como criar um novo template

Dentro de `schemas/<project_id>/templates/`, crie um novo arquivo YAML.

Exemplo:

```yaml
id: informar_pendencia_maior_60
name: Informar Pendência Maior 60
active: true

output:
  file_prefix: PENDENCIA_MAIOR_60
```

Esse template herda os campos definidos em `project.yaml`.

---

## Tipos de template

### Template padrão

Usado quando a campanha utiliza apenas os campos padrão do projeto.

```yaml
id: standard
name: Standard
active: true

output:
  file_prefix: STANDARD
```

### Template com dados extras

Usado quando a campanha precisa adicionar campos além dos padrões do projeto.

```yaml
id: extra_data
name: Extra Data
active: true

output:
  file_prefix: EXTRA_DATA

fields:
  valor_parcela:
    required: false
    output_name: valor_parcela
    aliases:
      - valor parcela
      - valor_parcela
      - parcela
```

### Template com override

Usado quando a campanha precisa sobrescrever ou desativar campos herdados do projeto.

```yaml
id: override
name: Override
active: true

output:
  file_prefix: OVERRIDE

fields:
  nome:
    enabled: false

  telefone:
    required: true
    output_name: WHATSAPP
    aliases:
      - telefone
      - celular
      - whatsapp
```

---

## Regras importantes de schema

### `required`

Define se o campo precisa estar mapeado para gerar os lotes.

```yaml
required: true
```

Campos obrigatórios não mapeados bloqueiam a geração.

### `output_name`

Define o nome final da coluna no CSV de saída.

```yaml
output_name: TEL_DEEP
```

### `aliases`

Define possíveis nomes da coluna na base de entrada.

Aliases não precisam estar em lowercase. O sistema normaliza os nomes antes de comparar.

Exemplo:

```yaml
aliases:
  - Nome Cliente
  - nome_cliente
  - NOME CLIENTE
```

Todos podem mapear para o mesmo campo.

### `enabled: false`

Remove o campo do mapeamento daquele template.

Importante: isso não apaga a coluna original da base. Como a aplicação mantém todas as colunas de entrada, a coluna continuará no output se existir no CSV.

---

## Testes manuais

Os testes ficam em:

```txt
tests/manual/
```

Para rodar:

```powershell
python .\tests\manual\run_all.py
```

Os testes validam:

- carregamento de YAML;
- descoberta de projetos e templates;
- resolução de schemas;
- leitura de CSV;
- limpeza/preparação de base;
- mapeamento automático;
- mapeamento manual;
- validação;
- geração do output;
- planejamento de lotes;
- exportação ZIP;
- fluxo completo pelo engine.

---

## Deploy

A aplicação pode ser publicada no Streamlit Cloud.

### Arquivo principal

```txt
app.py
```

### Dependências

As dependências devem estar em:

```txt
requirements.txt
```

Exemplo:

```txt
streamlit
pandas
pyyaml
```

### Tema

A configuração visual fica em:

```txt
.streamlit/config.toml
```

Exemplo:

```toml
[theme]
base = "dark"
primaryColor = "#FF4B4B"

[server]
maxUploadSize = 200
```

---

## Privacidade e armazenamento

A aplicação processa os arquivos em memória durante a sessão de uso.

O app não deve:

- salvar bases enviadas em disco;
- salvar ZIPs gerados em disco;
- armazenar dados em banco;
- usar cache para DataFrames com dados de clientes;
- versionar bases reais no GitHub.

Arquivos reais de clientes não devem ser commitados no repositório.

---

## Git e versionamento

Sugestão para finalizar uma versão:

```powershell
git add .
git commit -m "Finalize Batch Splitter V1"
git push

git tag v1.0.0
git push origin v1.0.0
```

---

## Status da versão

Versão atual: `v1.0.0`

Funcionalidades incluídas:

- interface Streamlit;
- tema dark;
- proteção por senha;
- seleção de projeto/template;
- upload de CSV;
- mapeamento automático;
- mapeamento manual quando necessário;
- preview de entrada e saída;
- separação em lotes;
- geração de ZIP;
- schemas configuráveis.
