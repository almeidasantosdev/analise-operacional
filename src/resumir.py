"""Resume a base tratada para o README e para a conferência do SQL."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]


def resumir(itens: pd.DataFrame, produtos: pd.DataFrame, descartes: pd.DataFrame) -> dict:
    entregue = itens[itens["situacao"].eq("entregue")].copy()
    receita = float(entregue["receita_liquida"].sum())
    margem = float(entregue["margem"].sum())
    por_sku = (
        entregue.groupby("sku", as_index=False)["receita_liquida"]
        .sum()
        .sort_values(["receita_liquida", "sku"], ascending=[False, True])
    )
    por_sku["acumulado"] = por_sku["receita_liquida"].cumsum() / receita
    nomes = produtos.set_index("sku")["produto"]
    centros = (
        entregue.groupby("centro")
        .agg(linhas=("id_linha", "size"), pct_no_prazo=("no_prazo", "mean"), atraso_medio=("atraso_dias", "mean"))
        .reset_index()
        .sort_values(["pct_no_prazo", "centro"])
    )
    canais = (
        entregue.groupby("canal")
        .apply(
            lambda grupo: pd.Series(
                {
                    "receita": grupo["receita_liquida"].sum(),
                    "margem_pct": grupo["margem"].sum() / grupo["receita_liquida"].sum(),
                    "desconto_medio": grupo["desconto"].mean(),
                }
            ),
            include_groups=False,
        )
        .reset_index()
        .sort_values("margem_pct")
    )
    mensal = (
        entregue.assign(mes=entregue["data_pedido"].str.slice(0, 7))
        .groupby("mes")["receita_liquida"]
        .sum()
        .round(2)
    )
    centro = centros.iloc[0]
    canal = canais.iloc[0]
    return {
        "linhas_brutas": int(len(itens) + descartes["linhas"].sum()),
        "linhas_tratadas": int(len(itens)),
        "linhas_entregues": int(len(entregue)),
        "descartes": {linha.motivo: int(linha.linhas) for linha in descartes.itertuples(index=False)},
        "receita_entregue": round(receita, 2),
        "margem_entregue": round(margem, 2),
        "margem_pct": round(margem / receita, 4),
        "pct_no_prazo": round(float(entregue["no_prazo"].mean()), 4),
        "taxa_cancelamento": round(float(itens["situacao"].eq("cancelado").mean()), 4),
        "skus_para_80_pct": int((por_sku["acumulado"] < 0.80).sum() + 1),
        "centro_menor_prazo": {
            "centro": centro.centro,
            "pct_no_prazo": round(float(centro.pct_no_prazo), 4),
            "atraso_medio": round(float(centro.atraso_medio), 2),
        },
        "canal_menor_margem": {
            "canal": canal.canal,
            "margem_pct": round(float(canal.margem_pct), 4),
            "desconto_medio": round(float(canal.desconto_medio), 4),
        },
        "top_skus": [
            {
                "sku": linha.sku,
                "produto": nomes.loc[linha.sku],
                "receita": round(float(linha.receita_liquida), 2),
            }
            for linha in por_sku.head(3).itertuples(index=False)
        ],
        "receita_mensal": {mes: float(valor) for mes, valor in mensal.items()},
    }


def gravar() -> Path:
    pasta = RAIZ / "data" / "tratado"
    itens = pd.read_csv(pasta / "itens.csv")
    produtos = pd.read_csv(pasta / "produtos.csv")
    descartes = pd.read_csv(pasta / "descartes.csv")
    resumo = resumir(itens, produtos, descartes)
    destino = pasta / "resumo.json"
    destino.write_text(json.dumps(resumo, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(resumo, ensure_ascii=False, indent=2))
    return destino


if __name__ == "__main__":
    gravar()
