# Override Schema Example

This template changes inherited project behavior.

## Purpose

Use this when a specific template needs to disable or change fields inherited from `project.yaml`.

## Behavior

This example does two things:

1. Disables the inherited `nome` field.
2. Overrides the inherited `telefone` field output name.

## Disabled field

```yaml
nome:
  enabled: false
```

This means `nome` is no longer treated as a schema-mapped field for this template.

Important: the Batch Splitter keeps all input columns. So if the input CSV has a raw `nome` column, it will still remain in the output unchanged. It just will not be renamed by the schema.

## Overridden field

```yaml
telefone:
  required: true
  output_name: WHATSAPP
```

This changes the final output column name for the phone field from the project default, for example `TEL_DEEP`, to `WHATSAPP`.

## Example

If the input CSV has:

```txt
nome;telefone;CPF
```

The output may become:

```txt
nome;WHATSAPP;CPF
```

The `nome` column remains unchanged because it was disabled as a mapped field, not deleted.

## When to use

Use this when a specific template needs to remove inherited mapping behavior or change an inherited output column name.
