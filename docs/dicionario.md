# Dicionário

A base não tem cliente, documento, endereço nem nome de pessoa. Centros e produtos são rótulos fictícios.

## produtos.csv

| Coluna | Significado |
| --- | --- |
| `sku` | Código do produto |
| `produto` | Nome fictício |
| `linha` | Copa, Mesa, Cozinha, Banho ou Escritorio |
| `preco_tabela` | Preço de tabela, em reais |
| `custo_unitario` | Custo unitário, em reais |

## itens.csv tratado

| Coluna | Significado |
| --- | --- |
| `id_linha` | Identificador da linha. Único depois do tratamento |
| `pedido` | Pedido ao qual a linha pertence |
| `data_pedido` | Data do pedido, `AAAA-MM-DD` |
| `centro` | Leme, Vela, Mastro, Quilha ou Popa |
| `canal` | `balcao`, `site` ou `televendas` |
| `sku` | Chave para `produtos.csv` |
| `quantidade` | Unidades, sempre maior que zero |
| `preco_tabela` | Preço unitário de tabela |
| `desconto` | Fração de 0 a 1. Valor acima de 1 na origem foi lido como ponto percentual |
| `custo_unitario` | Custo unitário |
| `data_prometida` | Data prometida de entrega |
| `data_entrega` | Data em que a linha foi entregue. Vazio quando cancelada |
| `situacao` | `entregue` ou `cancelado` |
| `receita_liquida` | `quantidade * preco_tabela * (1 - desconto)`, com duas casas |
| `custo_total` | `quantidade * custo_unitario`, com duas casas |
| `margem` | `receita_liquida - custo_total` |
| `no_prazo` | `1` se a entrega ocorreu até a data prometida. Vazio no cancelamento |
| `atraso_dias` | Entrega menos data prometida, em dias. Negativo significa adiantado. Vazio no cancelamento |

## Métricas

| Métrica | Fórmula |
| --- | --- |
| Receita | Soma de `receita_liquida` das linhas entregues |
| Margem % | Soma da margem dividida pela receita, só no entregue |
| No prazo % | Linhas entregues com `no_prazo = 1` divididas pelas linhas entregues |
| Cancelamento | Linhas canceladas divididas por todas as linhas tratadas |
| Participação do produto | Receita do SKU dividida pela receita entregue |

Cancelamento e prazo usam a linha, não o pedido. Um pedido pode misturar as duas situações.
