# Standard Schema Example

This template is the simplest schema example.

## Purpose

Use this when a campaign only needs the standard fields inherited from `project.yaml`.

Typical inherited fields:

- `nome`
- `telefone`

## Behavior

This file only defines the template identity and output prefix.

It does not add, remove, or override any fields.

## Example output

If the project has these standard fields:

```yaml
fields:
  nome:
    output_name: nome
  telefone:
    output_name: TEL_DEEP
```

Then this template will output at least:

```txt
nome
TEL_DEEP
```

Any extra input CSV columns are kept unchanged by the Batch Splitter.

## When to use

Use this for normal templates where the input base only needs the default project mapping.
