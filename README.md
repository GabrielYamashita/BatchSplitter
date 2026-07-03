# Batch Splitter

Sistema Streamlit para separar bases CSV de acionamento em lotes menores, usando schemas configuráveis por projeto e template.

O objetivo é padronizar o processamento de bases recebidas de diferentes clientes, mesmo quando cada base possui nomes de colunas, delimitadores e estruturas diferentes.

## Funcionalidades

- Upload de bases CSV
- Detecção automática de delimitador
- Mapeamento automático de colunas por aliases
- Mapeamento manual quando necessário
- Validação de campos obrigatórios
- Renomeação padronizada de colunas
- Preservação das colunas originais não mapeadas
- Divisão da base em lotes configuráveis
- Tratamento de remanescente por percentual
- Exportação dos lotes em ZIP
- Proteção simples por senha

## Estrutura do projeto

```txt
app.py
core/
schemas/
tests/
doc/
```

### `core/`

Contém a lógica principal da aplicação:

- leitura de CSV
- limpeza/preparação da base
- mapeamento de colunas
- validação
- geração da base de saída
- divisão em lotes
- exportação ZIP

### `schemas/`

Contém os projetos e templates configuráveis.

Exemplo:

```txt
schemas/
└─ afinz/
   ├─ project.yaml
   └─ templates/
      └─ informar_pendencia_maior_60.yaml
```

### `doc/`

Contém documentação auxiliar sobre schemas e exemplos de configuração.

## Como rodar localmente

Crie o ambiente virtual:

```powershell
python -m venv .venv
```

Ative o ambiente:

```powershell
.\.venv\Scripts\Activate.ps1
```

Instale as dependências:

```powershell
pip install -r requirements.txt
```

Rode a aplicação:

```powershell
streamlit run app.py
```

## Secrets

A aplicação usa uma senha simples para restringir o acesso.

Crie o arquivo local:

```txt
.streamlit/secrets.toml
```

Com:

```toml
APP_PASSWORD = "sua_senha_aqui"
```

No Streamlit Cloud, configure o mesmo valor em:

```txt
App Settings → Secrets
```

## Criando novos schemas

Cada projeto deve ter um `project.yaml`.

Exemplo simplificado:

```yaml
id: afinz
name: Afinz
active: true

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

Templates ficam dentro da pasta `templates/` do projeto.

Exemplo:

```yaml
id: informar_pendencia_maior_60
name: Informar Pendência Maior 60
active: true

output:
  file_prefix: PENDENCIA_MAIOR_60
```

Documentação mais detalhada sobre schemas fica em `doc/`.

## Testes

Os testes manuais ficam em:

```txt
tests/manual/
```

Para rodar:

```powershell
python .\tests\manual\run_all.py
```

## Deploy

A aplicação pode ser publicada no Streamlit Cloud.

Configuração principal:

```txt
Main file: app.py
Dependencies: requirements.txt
Secrets: APP_PASSWORD
```

## Privacidade

A aplicação processa os arquivos em memória durante a sessão.

O projeto não deve:

- salvar bases reais em disco;
- salvar ZIPs gerados em disco;
- versionar bases reais no GitHub;
- usar cache para DataFrames com dados de clientes.

## Versão atual

`v1.0.0`

Inclui:

- interface Streamlit;
- tema dark;
- proteção por senha;
- schemas por projeto/template;
- upload e preview de CSV;
- mapeamento automático/manual;
- geração de lotes;
- exportação ZIP.
