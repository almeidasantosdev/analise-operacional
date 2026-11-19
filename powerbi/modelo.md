# Modelo para o Power BI

O arquivo `.pbix` não entra no Git. O modelo é pequeno e cabe em duas tabelas.

## Carga

1. Obter dados, texto/CSV, e apontar para `data/tratado/itens.csv` e `data/tratado/produtos.csv`.
2. Codificação UTF-8 e delimitador vírgula.
3. Em `itens`, marcar `data_pedido`, `data_prometida` e `data_entrega` como data. A entrega vazia fica nula.
4. Relação: `produtos[sku]` (1) para `itens[sku]` (*), filtro simples, da dimensão para a fato.

Centro e canal ficam na fato. Cada um tem poucos valores e nenhum atributo além do nome. Uma dimensão separada não muda o indicador.

## Medidas

Colar o conteúdo de `medidas.dax` na tabela `itens`. Receita, margem, prazo e desconto médio consideram só linha entregue. O cancelamento usa todas as linhas tratadas.

## Páginas

1. **Resultado.** Cartões de receita, margem %, no prazo % e cancelamento. Gráfico de colunas da receita por mês, usando `data_pedido`.
2. **Entrega.** Barras de `% no prazo` e atraso médio por `centro`. Quilha é o centro que o gerador atrasa de propósito.
3. **Margem.** Matriz de linha de produto por canal, com receita, margem % e desconto médio. O site é o canal com maior desconto.

O recorte de um cartão precisa usar a mesma fórmula do README. Receita do ano entregue: 779.779,75.
