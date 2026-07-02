from __future__ import annotations

from datetime import datetime, timedelta

import streamlit as st

from core.engine import (
    apply_mapping_and_build_output,
    generate_zip,
    prepare_batches,
    prepare_template,
    prepare_uploaded_file,
)
from core.schemas.discovery import list_projects, list_templates

SCHEMA_ROOT = "schemas"


def default_tomorrow_ddmm() -> str:
    return (datetime.now() + timedelta(days=1)).strftime("%d%m")


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

        # with col3:
        #     st.metric(
        #         "Prefixo do Lote",
        #         schema_preview.get("output", {}).get("file_prefix", "-"),
        #     )

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

        # st.subheader("Batch config")
        # st.json(schema_preview.get("batch", {}))

        # st.subheader("Output config")
        # st.json(schema_preview.get("output", {}))


def render_mapping_preview(mapping: dict, schema: dict) -> None:
    mapped_rows = []

    for field, csv_column in mapping.get("mapped", {}).items():
        field_config = schema.get("fields", {}).get(field, {})

        mapped_rows.append(
            {
                "field": field,
                "csv_column": csv_column,
                "output_name": field_config.get("output_name"),
                "required": field_config.get("required", False),
            }
        )

    if mapped_rows:
        st.dataframe(mapped_rows, use_container_width=True)
    else:
        st.warning("No fields were mapped automatically.")

    unmapped = mapping.get("unmapped_columns", [])

    if unmapped:
        with st.expander("Unmapped CSV columns", expanded=False):
            st.write(unmapped)


def render_validation(validation: dict) -> None:
    if validation.get("valid"):
        st.success("Mapping is valid.")
        return

    st.error("Mapping has errors.")

    with st.expander("Validation errors", expanded=True):
        st.json(validation.get("errors", []))


def build_manual_mapping_ui(
    missing_required: list[str],
    schema: dict,
    csv_columns: list[str],
) -> dict[str, str]:
    manual_mapping = {}

    if not missing_required:
        return manual_mapping

    st.subheader("Mapeamento Manual")

    st.warning(
        "Alguns campos obrigatórios não foram reconhecidos automaticamente. "
        "Selecione a coluna correta do CSV para cada campo faltante."
    )

    options = [""] + csv_columns

    for field in missing_required:
        aliases = schema.get("fields", {}).get(field, {}).get("aliases", [])

        st.caption(f"Expected aliases for `{field}`: {', '.join(aliases)}")

        selected_column = st.selectbox(
            label=f"Map field `{field}` to CSV column",
            options=options,
            key=f"manual_mapping_{field}",
        )

        if selected_column:
            manual_mapping[field] = selected_column

    return manual_mapping


def render_batch_plan(batch_plan: list[dict]) -> None:
    if not batch_plan:
        st.warning("Nenhum lote gerado.")
        return

    display_rows = []

    for batch in batch_plan:
        display_rows.append(
            {
                "Lote": f"{batch['batch_num']:02d}",
                "Arquivo": f"{batch['file_num']:02d}",
                "Qtd. Clientes": batch["rows"],
                "Linha Inicial": batch["start"] + 1,
                "Linha Final": batch["end"],
            }
        )

    st.dataframe(display_rows, use_container_width=True)


def main() -> None:
    st.set_page_config(
        page_title="Batch Splitter",
        page_icon="📦",
        layout="wide",
    )

    st.title("📦 Batch Splitter")
    st.caption("Separador de bases de acionamento - 1Digital")

    # -----------------------------
    # Sidebar: project/template
    # -----------------------------

    st.sidebar.header("1. Seleção do Template")

    projects = list_projects(SCHEMA_ROOT)

    if not projects:
        st.error("No active projects found in schemas/.")
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
            f"No active templates found for project: {selected_project['project_name']}"
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

    date = st.sidebar.text_input(
        "Date (DDMM)",
        value=default_tomorrow_ddmm(),
        max_chars=4,
    )

    runtime_config = {
        "batch_size": int(batch_size),
        "remainder_threshold_percent": float(remainder_threshold_percent),
        "batch_num": int(batch_num),
        "date": date,
    }

    # -----------------------------
    # Upload
    # -----------------------------

    st.header("1. Upload CSV")

    uploaded_file = st.file_uploader(
        "Upload da Base de Acionamento CSV",
        type=["csv"],
    )

    if uploaded_file is None:
        st.info("Upload um arquivo CSV para continuar.")
        st.stop()

    upload_result = prepare_uploaded_file(
        uploaded_file=uploaded_file,
        schema=schema,
        preview_rows=10,
    )

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
    # with st.expander("Visualização do input", expanded=True):

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Linhas", input_preview["rows"])

    with col2:
        st.metric("Colunas", input_preview["total_columns"])

    with col3:
        st.metric("Separador", read_info["delimiter"])

    with st.expander("Relatório de Limpeza", expanded=False):
        st.json(cleaning_report)

    st.dataframe(input_preview["sample"], use_container_width=True)

    # -----------------------------
    # Mapping
    # -----------------------------

    st.divider()
    st.header("3. Mapeamento de Colunas")

    render_mapping_preview(mapping, schema)
    render_validation(validation)

    csv_columns = list(df_clean.columns)

    manual_mapping = build_manual_mapping_ui(
        missing_required=mapping.get("missing_required", []),
        schema=schema,
        csv_columns=csv_columns,
    )

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
        st.stop()

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

    with st.expander("Output report", expanded=False):
        st.json(output_report)

    st.dataframe(output_preview["sample"], use_container_width=True)

    # -----------------------------
    # Batch preview
    # -----------------------------

    st.divider()
    st.header("5. Batch preview")

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
        st.metric("Total batches", batch_summary["total_batches"])

    with col2:
        st.metric("Total rows", batch_summary["total_rows"])

    render_batch_plan(batch_plan)

    # -----------------------------
    # ZIP generation
    # -----------------------------

    st.divider()
    st.header("6. Gerar Lotes de Acionamento")

    if st.button("Gerar Lotes", type="primary"):
        zip_result = generate_zip(
            df_output=df_output,
            batch_plan=batch_plan,
            schema=schema,
            runtime_config=runtime_config,
        )

        st.session_state["zip_result"] = zip_result

    zip_result = st.session_state.get("zip_result")

    if zip_result:
        st.success("Lotes gerados com sucesso.")

        st.subheader("Arquivos gerados")
        st.dataframe(zip_result["files"], use_container_width=True)

        project_name = schema.get("_meta", {}).get("project_name", "project")
        template_id = schema.get("_meta", {}).get("template_id", "template")

        zip_filename = f"{project_name}_{template_id}_{date}.zip"

        st.download_button(
            label="Download Lotes",
            data=zip_result["zip_bytes"],
            file_name=zip_filename,
            mime="application/zip",
        )


if __name__ == "__main__":
    main()
