# Análise operacional

Base fictícia de itens de pedido. O fluxo coleta o arquivo bruto, corrige o que dá para corrigir, descarta o que quebra a métrica e calcula receita, margem, prazo e cancelamento. Os mesmos arquivos tratados alimentam o repositório [sql-indicadores](https://github.com/almeidasantosdev/sql-indicadores).

Não há cliente, documento, endereço nem nome de pessoa. Centros e produtos são rótulos.

## Leitura desta semente

A semente é 42. O gerador atrasa o centro Quilha de propósito e dá desconto maior ao canal site. Os números abaixo são a medição desse desenho, não uma série real.

| Indicador | Valor | Recorte |
| --- | --- | --- |
| Receita líquida | 779.779,75 | linhas entregues |
| Margem | 53,01% | linhas entregues |
| No prazo | 57,46% | linhas entregues |
| Cancelamento | 9,03% | todas as linhas tratadas |

Quilha entrega no prazo em 24,10% das linhas e atrasa 1,56 dia em média. Leme fica em 78,39% e entrega um pouco antes do prometido. O site desconta 16,46% em média e fica com margem de 49,21%. Balcão desconta 4,12% e fica com 55,54%.

Dez produtos, de dezoito, formam 80% da receita. Luminária de mesa, panela de 2 litros e frigideira de 24 cm somam 41,72%. A receita mensal oscila entre 56.238,50 em novembro e 70.262,16 em abril, sem uma tendência para interpretar.

Duas linhas entregues ficam com margem negativa. O detalhe das colunas está em `docs/dicionario.md`.

## Tratamento

O bruto tem 6.025 linhas. Entram 5.949. Os descartes desta semente estão em `data/tratado/descartes.csv`:

| Motivo | Linhas |
| --- | --- |
| `id_duplicado` | 25 |
| `quantidade_invalida` | 29 |
| `entrega_antes_do_pedido` | 12 |
| `sku_sem_cadastro` | 7 |
| `entrega_ausente` | 3 |

Antes de descartar, a situação é normalizada e o desconto vazio vira zero. Desconto entre 1 e 100 é lido como ponto percentual e dividido por 100. Receita e margem usam duas casas e só entram no indicador quando a situação é `entregue`. Prazo e atraso ficam vazios no cancelamento.

## Power BI

O `.pbix` não vai para o Git. `powerbi/modelo.md` descreve a carga, a relação `produtos[sku]` para `itens[sku]` e as três páginas. As medidas estão em `powerbi/medidas.dax`. O cartão de receita do ano precisa fechar em 779.779,75.

## Como rodar

Python 3.12 ou superior.

```powershell
python -m pip install -r requirements.txt
python src/gerar.py
python src/tratar.py
python src/resumir.py
python -m unittest discover -s tests
```

`src/resumir.py` regrava `data/tratado/resumo.json`. Os CSV de `data/tratado/` são a fonte do SQL e do Power BI.

## Estrutura

```text
src/gerar.py             base bruta e sujeira proposital
src/tratar.py            regras e métricas
src/resumir.py           totais usados neste README
data/bruto/              CSV antes do tratamento
data/tratado/            CSV limpo, descartes e resumo
powerbi/                 medidas DAX e modelo
docs/dicionario.md       colunas e fórmulas
tests/test_tratar.py     desconto, duplicidade, quantidade, SKU e data
```
