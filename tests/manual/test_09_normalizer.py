from core.mapping.normalizer import normalize_name


def main():
    assert normalize_name("Nome Cliente") == "nome_cliente"
    assert normalize_name(" Telefone Principal ") == "telefone_principal"
    assert normalize_name("CPF/CNPJ") == "cpf_cnpj"
    assert normalize_name("TEL_DEEP") == "tel_deep"
    assert normalize_name("Data de Vencimento") == "data_de_vencimento"
    assert normalize_name("João") == "joao"

    print("Normalizer OK")


if __name__ == "__main__":
    main()
