# Batch Splitter System

O Batch Splitter é um sistema semi-automatizado para processamento e
segmentação de bases CSV em lotes menores, projetado para operações
escaláveis de acionamento e distribuição de dados.

O objetivo principal da ferramenta é padronizar, automatizar e
flexibilizar o tratamento de bases recebidas de diferentes clientes,
independentemente de estrutura, nomenclatura de colunas ou delimitadores
utilizados.

O sistema opera através de um modelo orientado por schemas
configuráveis, onde cada projeto ou cliente possui um template próprio
contendo regras de validação, aliases de colunas, padrões de saída e
configurações específicas de lote.

Com isso, a adição de novos projetos não exige alteração no código
principal, apenas a criação de um novo schema.

## Principais funcionalidades

-   Detecção automática de delimitadores de arquivos CSV.
-   Mapeamento inteligente de colunas através de aliases configuráveis.
-   Validação de campos obrigatórios.
-   Renomeação padronizada de colunas para compatibilidade com sistemas
    externos.
-   Segmentação dinâmica em lotes configuráveis.
-   Tratamento inteligente de sobras de registros.
-   Exportação estruturada dos lotes gerados.

A ferramenta utiliza uma interface gráfica baseada em Streamlit para
permitir que o processo seja executado de forma simples e controlada,
mantendo a flexibilidade necessária para ajustes manuais quando
necessário.

Sua arquitetura modular garante escalabilidade, reutilização de código e
rápida adaptação para novos fluxos operacionais.
