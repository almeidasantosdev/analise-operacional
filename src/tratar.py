"""Aplica as regras de limpeza e calcula as métricas da base fictícia."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
SITUACOES = {"entregue", "cancelado"}


def _marcar(motivos: pd.Series, mascara: pd.Series, codigo: str) -> pd.Series:
    return motivos.mask(motivos.eq("") & mascara.fillna(False), codigo)


def preparar(bruto: pd.DataFrame, produtos: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = bruto.copy()
    df["id_linha"] = df["id_linha"].astype(str).str.strip()
    df["pedido"] = df["pedido"].astype(str).str.strip()
    df["sku"] = df["sku"].astype(str).str.strip()
    df["centro"] = df["centro"].astype(str).str.strip()
    df["canal"] = df["canal"].astype(str).str.strip().str.lower()
    df["situacao"] = df["situacao"].astype(str).str.strip().str.lower()
    df["quantidade"] = pd.to_numeric(df["quantidade"], errors="coerce")
    df["preco_tabela"] = pd.to_numeric(df["preco_tabela"], errors="coerce")
    df["custo_unitario"] = pd.to_numeric(df["custo_unitario"], errors="coerce")
    df["desconto"] = pd.to_numeric(df["desconto"], errors="coerce").astype("float64")
    for coluna in ("data_pedido", "data_prometida", "data_entrega"):
        df[coluna] = pd.to_datetime(df[coluna], errors="coerce")

    df["desconto"] = df["desconto"].fillna(0)
    em_pontos = df["desconto"].gt(1) & df["desconto"].le(100)
    df.loc[em_pontos, "desconto"] = df.loc[em_pontos, "desconto"] / 100

    motivos = pd.Series("", index=df.index, dtype="object")
    motivos = _marcar(motivos, df["id_linha"].duplicated(keep="first"), "id_duplicado")
    motivos = _marcar(motivos, ~df["situacao"].isin(SITUACOES), "situacao_desconhecida")
    motivos = _marcar(motivos, ~df["sku"].isin(set(produtos["sku"])), "sku_sem_cadastro")
    motivos = _marcar(motivos, df["quantidade"].isna() | df["quantidade"].le(0), "quantidade_invalida")
    motivos = _marcar(motivos, df["desconto"].lt(0) | df["desconto"].gt(1), "desconto_invalido")
    motivos = _marcar(motivos, df["data_pedido"].isna() | df["data_prometida"].isna(), "data_ausente")
    entrega_invertida = df["data_entrega"].notna() & df["data_entrega"].lt(df["data_pedido"])
    motivos = _marcar(motivos, entrega_invertida, "entrega_antes_do_pedido")
    entrega_obrigatoria = df["situacao"].eq("entregue") & df["data_entrega"].isna()
    motivos = _marcar(motivos, entrega_obrigatoria, "entrega_ausente")

    descartes = (
        motivos[motivos.ne("")]
        .value_counts()
        .rename_axis("motivo")
        .reset_index(name="linhas")
        .sort_values("motivo")
    )
    limpo = df.loc[motivos.eq("")].copy()
    limpo["receita_liquida"] = (limpo["quantidade"] * limpo["preco_tabela"] * (1 - limpo["desconto"])).round(2)
    limpo["custo_total"] = (limpo["quantidade"] * limpo["custo_unitario"]).round(2)
    limpo["margem"] = (limpo["receita_liquida"] - limpo["custo_total"]).round(2)
    entregue = limpo["situacao"].eq("entregue")
    limpo["no_prazo"] = pd.Series(pd.NA, index=limpo.index, dtype="Int64")
    limpo.loc[entregue, "no_prazo"] = limpo.loc[entregue, "data_entrega"].le(limpo.loc[entregue, "data_prometida"]).astype(int)
    limpo["atraso_dias"] = pd.Series(pd.NA, index=limpo.index, dtype="Int64")
    limpo.loc[entregue, "atraso_dias"] = (
        limpo.loc[entregue, "data_entrega"] - limpo.loc[entregue, "data_prometida"]
    ).dt.days.astype(int)

    for coluna in ("data_pedido", "data_prometida", "data_entrega"):
        limpo[coluna] = limpo[coluna].dt.strftime("%Y-%m-%d")
    limpo.loc[~entregue, "data_entrega"] = ""
    limpo = limpo.sort_values(["data_pedido", "id_linha"]).reset_index(drop=True)
    return limpo, descartes.reset_index(drop=True)


def gravar(origem: Path | None = None, destino: Path | None = None) -> Path:
    bruto = origem or RAIZ / "data" / "bruto"
    pasta = destino or RAIZ / "data" / "tratado"
    pasta.mkdir(parents=True, exist_ok=True)
    itens = pd.read_csv(bruto / "itens.csv")
    produtos = pd.read_csv(bruto / "produtos.csv")
    limpo, descartes = preparar(itens, produtos)
    limpo.to_csv(pasta / "itens.csv", index=False)
    produtos.to_csv(pasta / "produtos.csv", index=False)
    descartes.to_csv(pasta / "descartes.csv", index=False)
    return pasta


if __name__ == "__main__":
    print(gravar())
