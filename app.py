from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import streamlit as st

from core.engine import (
    apply_mapping_and_build_output,
    generate_zip,
    prepare_batches,
    prepare_template,
    prepare_uploaded_file,
)
from core.export.zip_exporter import render_filename
from core.schemas.discovery import list_projects, list_templates

APP_TIMEZONE = "America/Sao_Paulo"
SCHEMA_ROOT = "schemas"


def check_password() -> bool:
    expected_password = st.secrets.get("APP_PASSWORD")

    if not expected_password:
        st.error("Senha do app não configurada.")
        st.caption("Configure APP_PASSWORD nos secrets do Streamlit.")
        st.stop()

    if st.session_state.get("authenticated") is True:
        return True

    col1, col2, col3 = st.columns([1, 1.2, 1])

    with col2:
        st.title("🔒 Acesso Restrito")
        st.caption("Digite a senha para acessar o Batch Splitter.")

        with st.form("login_form"):
            password = st.text_input(
                "Senha",
                type="password",
                placeholder="Digite a senha de acesso",
            )

            submitted = st.form_submit_button(
                "Entrar",
                type="primary",
                use_container_width=True,
            )

        if submitted:
            if password == expected_password:
                st.session_state["authenticated"] = True
                st.rerun()

            st.error("Senha incorreta.")

    st.stop()


def render_logout_button() -> None:
    st.sidebar.divider()

    if st.sidebar.button("Sair"):
        for key in list(st.session_state.keys()):
            st.session_state.pop(key, None)

        st.rerun()


def default_tomorrow_date():
    now = datetime.now(ZoneInfo(APP_TIMEZONE))
    return (now + timedelta(days=1)).date()


def format_date_ddmm(value) -> str:
    return value.strftime("%d%m")


def validate_runtime_config(runtime_config: dict) -> list[str]:
    errors = []

    if runtime_config["batch_size"] <= 0:
        errors.append("Clientes por lote deve ser maior que zero.")

    if runtime_config["batch_num"] <= 0:
        errors.append("Número do lote deve ser maior que zero.")

    if not 0 <= runtime_config["remainder_threshold_percent"] <= 100:
        errors.append("Limite de remanescente deve estar entre 0 e 100.")

    return errors


def build_project_options(projects: list[dict]) -> dict[str, dict]:
    return {f"{project['project_name']}": project for project in projects}


def build_template_options(templates: list[dict]) -> dict[str, dict]:
    return {f"{template['template_name']}": template for template in templates}


def render_schema_preview(schema_preview: dict) -> None:
    with st.expander("Visualização do Template Escolhido", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            st.metric("Projeto", schema_preview.get("project_name", "-"))

        with col2:
            st.metric("Template", schema_preview.get("template_name", "-"))

        st.subheader("Campos do Template")

        fields_preview = [
            {
                "Coluna de Entrada": field["field"],
                "Coluna de Saída": field["output_name"],
                "Obrigatório": field["required"],
                "Sinônimos": ", ".join(field.get("aliases", [])),
            }
            for field in schema_preview.get("fields", [])
        ]

        st.dataframe(fields_preview, use_container_width=True)


def render_mapping_preview(mapping: dict, schema: dict) -> None:
    mapped_rows = []

    for field, csv_column in mapping.get("mapped", {}).items():
        field_config = schema.get("fields", {}).get(field, {})

        mapped_rows.append(
            {
                "Campo": field,
                "Coluna no CSV": csv_column,
                "Coluna de Saída": field_config.get("output_name"),
                "Obrigatório": field_config.get("required", False),
            }
        )

    if mapped_rows:
        st.dataframe(mapped_rows, use_container_width=True)
    else:
        st.warning("Nenhum campo foi mapeado automaticamente.")

    unmapped = mapping.get("unmapped_columns", [])

    if unmapped:
        with st.expander("Colunas mantidas sem alteração", expanded=False):
            st.write(unmapped)


def render_validation(validation: dict, label: str = "Mapeamento") -> None:
    if validation.get("valid"):
        st.success(f"{label} válido.")
        return

    st.error(f"{label} possui erros.")

    with st.expander("Erros de validação", expanded=True):
        st.json(validation.get("errors", []))


def build_manual_mapping_ui(
    mapping: dict,
    validation: dict,
    schema: dict,
    csv_columns: list[str],
) -> dict[str, str]:
    manual_mapping = {}

    if validation.get("valid"):
        return manual_mapping

    fields = {
        field_key: field_config
        for field_key, field_config in schema.get("fields", {}).items()
        if field_config.get("enabled", True) is not False
    }

    if not fields:
        return manual_mapping

    st.subheader("Mapeamento Manual")

    options = [""] + csv_columns

    for field_key, field_config in fields.items():
        current_column = mapping.get("mapped", {}).get(field_key, "")
        output_name = field_config.get("output_name", field_key)
        required = field_config.get("required", False)
        aliases = field_config.get("aliases", [])

        label = f"{field_key} → {output_name}"

        if required:
            label += " *"

        if current_column in options:
            default_index = options.index(current_column)
        else:
            default_index = 0

        selected_column = st.selectbox(
            label=label,
            options=options,
            index=default_index,
            key=f"manual_mapping_{field_key}",
            help=f"Sinônimos esperados: {', '.join(aliases)}",
        )

        if selected_column:
            manual_mapping[field_key] = selected_column

    if not manual_mapping:
        st.warning(
            "O mapeamento automático possui erros. "
            "Revise os campos acima e selecione a coluna correta do CSV."
        )

    return manual_mapping


def render_filename_preview(
    schema: dict,
    batch_plan: list[dict],
    runtime_config: dict,
) -> None:
    if not batch_plan:
        st.warning("Nenhum arquivo previsto.")
        return

    preview_files = [
        {
            "Arquivo": render_filename(schema, batch, runtime_config),
            "Qtd. Clientes": batch["rows"],
        }
        for batch in batch_plan
    ]

    st.dataframe(preview_files, use_container_width=True)


def clear_zip_if_generation_changed(generation_key: dict) -> None:
    if st.session_state.get("generation_key") != generation_key:
        st.session_state.pop("zip_result", None)
        st.session_state["generation_key"] = generation_key


def main() -> None:
    st.set_page_config(
        page_title="Batch Splitter",
        page_icon="📦",
        layout="wide",
    )

    check_password()

    st.title("📦 Batch Splitter")
    st.caption("Separador de bases de acionamento - 1Digital")

    # -----------------------------
    # Sidebar: project/template
    # -----------------------------

    st.sidebar.header("1. Seleção do Template")

    projects = list_projects(SCHEMA_ROOT)

    if not projects:
        st.error("Nenhum projeto ativo encontrado em schemas/.")
        st.stop()

    project_options = build_project_options(projects)

    selected_project_label = st.sidebar.selectbox(
        "Projeto",
        options=list(project_options.keys()),
    )

    selected_project = project_options[selected_project_label]

    templates = list_templates(
        project_id=selected_project["project_id"],
        schema_root=SCHEMA_ROOT,
    )

    if not templates:
        st.error(
            f"Nenhum template ativo encontrado para o projeto: "
            f"{selected_project['project_name']}"
        )
        st.stop()

    template_options = build_template_options(templates)

    selected_template_label = st.sidebar.selectbox(
        "Template",
        options=list(template_options.keys()),
    )

    selected_template = template_options[selected_template_label]

    template_result = prepare_template(
        project_schema_path=selected_project["project_path"],
        template_schema_path=selected_template["template_path"],
    )

    schema = template_result["schema"]
    schema_preview = template_result["schema_preview"]

    render_schema_preview(schema_preview)

    # -----------------------------
    # Sidebar: runtime config
    # -----------------------------

    st.sidebar.header("2. Configurações do Lote")

    default_batch_size = int(schema.get("batch", {}).get("default_size", 2000))
    default_threshold = int(
        schema.get("batch", {}).get("remainder_threshold_percent", 50)
    )
    default_batch_num = int(schema.get("batch", {}).get("default_batch_num", 1))

    batch_size = st.sidebar.number_input(
        "Clientes por Lote",
        min_value=1,
        value=default_batch_size,
        step=100,
    )

    remainder_threshold_percent = st.sidebar.number_input(
        "Limite de Remanescente (%)",
        min_value=0,
        max_value=100,
        value=default_threshold,
        step=5,
    )

    batch_num = st.sidebar.number_input(
        "Número do Lote",
        min_value=1,
        value=default_batch_num,
        step=1,
    )

    selected_date = st.sidebar.date_input(
        "Data do Lote",
        value=default_tomorrow_date(),
        format="DD/MM/YYYY",
    )

    date = format_date_ddmm(selected_date)

    runtime_config = {
        "batch_size": int(batch_size),
        "remainder_threshold_percent": float(remainder_threshold_percent),
        "batch_num": int(batch_num),
        "date": date,
    }

    runtime_errors = validate_runtime_config(runtime_config)

    if runtime_errors:
        for error in runtime_errors:
            st.sidebar.error(error)

    render_logout_button()

    # -----------------------------
    # Upload
    # -----------------------------

    st.header("1. Upload da Base")

    uploaded_file = st.file_uploader(
        "Upload da Base de Acionamento CSV",
        type=["csv"],
    )

    if uploaded_file is None:
        st.info("Upload um arquivo CSV para continuar.")
        st.stop()

    try:
        upload_result = prepare_uploaded_file(
            uploaded_file=uploaded_file,
            schema=schema,
            preview_rows=10,
        )
    except Exception as error:
        st.error("Não foi possível processar o arquivo enviado.")
        st.caption(str(error))
        st.stop()

    df_clean = upload_result["df_clean"]
    mapping = upload_result["mapping"]
    validation = upload_result["validation"]

    # -----------------------------
    # Input preview
    # -----------------------------

    st.divider()
    st.header("2. Visualização de Input")

    read_info = upload_result["read_info"]
    cleaning_report = upload_result["cleaning_report"]
    input_preview = upload_result["input_preview"]

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Linhas", input_preview["rows"])

    with col2:
        st.metric("Colunas", input_preview["total_columns"])

    with col3:
        st.metric("Separador", read_info["delimiter"])

    with st.expander("Relatório de Limpeza da Base", expanded=False):
        st.json(cleaning_report)

    st.dataframe(input_preview["sample"], use_container_width=True)

    # -----------------------------
    # Mapping
    # -----------------------------

    st.divider()
    st.header("3. Mapeamento de Colunas")

    render_mapping_preview(mapping, schema)

    csv_columns = list(df_clean.columns)

    manual_mapping = build_manual_mapping_ui(
        mapping=mapping,
        validation=validation,
        schema=schema,
        csv_columns=csv_columns,
    )

    if validation.get("valid"):
        render_validation(validation, label="Mapeamento automático")

    # -----------------------------
    # Output build
    # -----------------------------

    output_result = apply_mapping_and_build_output(
        df_clean=df_clean,
        schema=schema,
        mapping=mapping,
        manual_mapping=manual_mapping,
        preview_rows=10,
    )

    if not output_result["success"]:
        st.error("O mapeamento final ainda possui erros.")

        with st.expander("Erros do mapeamento final", expanded=True):
            st.json(output_result["validation"].get("errors", []))

        st.stop()

    if not validation.get("valid") and manual_mapping:
        st.success("Mapeamento manual aplicado com sucesso.")

    df_output = output_result["df_output"]
    output_preview = output_result["output_preview"]
    output_report = output_result["output_result"]["report"]

    st.divider()
    st.header("4. Visualização do Arquivo de Saída")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Linhas de Saída", output_preview["rows"])

    with col2:
        st.metric("Colunas de Saída", output_preview["total_columns"])

    with st.expander("Relatório de Saída", expanded=False):
        st.json(output_report)

    st.dataframe(output_preview["sample"], use_container_width=True)

    # -----------------------------
    # Batch preview
    # -----------------------------

    st.divider()
    st.header("5. Relatório de Lotes")

    batch_result = prepare_batches(
        df_output=df_output,
        schema=schema,
        runtime_config=runtime_config,
    )

    batch_plan = batch_result["batch_plan"]
    batch_summary = batch_result["batch_summary"]

    st.success(batch_summary["summary"])

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Arquivos Totais", batch_summary["total_batches"])

    with col2:
        st.metric("Linhas Totais", batch_summary["total_rows"])

    render_filename_preview(schema, batch_plan, runtime_config)

    # -----------------------------
    # ZIP state safety
    # -----------------------------

    generation_key = {
        "project_id": selected_project["project_id"],
        "template_id": selected_template["template_id"],
        "uploaded_file_name": uploaded_file.name,
        "uploaded_file_size": uploaded_file.size,
        "batch_size": runtime_config["batch_size"],
        "remainder_threshold_percent": runtime_config["remainder_threshold_percent"],
        "batch_num": runtime_config["batch_num"],
        "date": runtime_config["date"],
        "manual_mapping": tuple(sorted(manual_mapping.items())),
        "output_columns": tuple(df_output.columns),
        "output_rows": len(df_output),
    }

    clear_zip_if_generation_changed(generation_key)

    # -----------------------------
    # ZIP generation
    # -----------------------------

    st.divider()
    st.header("6. Gerar Lotes de Acionamento")

    can_generate = not runtime_errors

    if runtime_errors:
        st.warning("Corrija as configurações do lote antes de gerar os arquivos.")

    if st.button("Gerar Lotes", type="primary", disabled=not can_generate):
        try:
            zip_result = generate_zip(
                df_output=df_output,
                batch_plan=batch_plan,
                schema=schema,
                runtime_config=runtime_config,
            )

            st.session_state["zip_result"] = zip_result

        except Exception as error:
            st.error("Não foi possível gerar os lotes.")
            st.caption(str(error))

    zip_result = st.session_state.get("zip_result")

    if zip_result:
        st.success("Lotes gerados com sucesso.")

        project_name = schema.get("_meta", {}).get("project_name", "project")
        file_prefix = schema.get("output", {}).get("file_prefix", "template")

        zip_filename = f"{project_name}_{file_prefix}_{runtime_config['date']}.zip"

        st.download_button(
            label="Download Lotes",
            data=zip_result["zip_bytes"],
            file_name=zip_filename,
            mime="application/zip",
        )


if __name__ == "__main__":
    main()
