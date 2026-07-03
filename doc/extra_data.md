# Extra Data Schema Example

This template inherits the standard project fields and adds optional extra fields.

## Purpose

Use this when a campaign needs the standard project columns plus additional business data.

Inherited fields usually include:

- `nome`
- `telefone`

This example adds:

- `valor_parcela`
- `data_vencimento`
- `dias_atraso`

## Behavior

The extra fields are optional because `required: false`.

If the app finds any of these fields in the uploaded CSV, it will rename them according to `output_name`.

If they are not found, the app can still generate the output as long as all required fields are mapped.

## Example

If the input CSV has:

```txt
Nome Cliente;Celular;valor parcela;vencimento;CPF
```

The output may become:

```txt
nome;TEL_DEEP;valor_parcela;data_vencimento;CPF
```

The `CPF` column is kept unchanged because the Batch Splitter keeps all input columns.

## When to use

Use this for templates that need additional informational columns, but where those columns are not required to generate the batch.
