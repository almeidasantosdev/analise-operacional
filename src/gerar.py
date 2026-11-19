"""Gera uma base fictícia de itens de pedido, com sujeira proposital."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

SEMENTE = 42
RAIZ = Path(__file__).resolve().parents[1]

PRODUTOS = [
    ("COP-01", "Copo vidro 300 ml", "Copa", 18.0, 7.2),
    ("COP-02", "Taca vinho", "Copa", 32.0, 14.0),
    ("COP-03", "Jarra 1 litro", "Copa", 28.0, 11.0),
    ("MES-01", "Prato raso", "Mesa", 22.0, 9.0),
    ("MES-02", "Prato fundo", "Mesa", 24.0, 9.5),
    ("MES-03", "Talher avulso", "Mesa", 8.0, 2.4),
    ("MES-04", "Travessa oval", "Mesa", 46.0, 19.0),
    ("COZ-01", "Panela 2 litros", "Cozinha", 89.0, 41.0),
    ("COZ-02", "Frigideira 24 cm", "Cozinha", 72.0, 33.0),
    ("COZ-03", "Tigela inox", "Cozinha", 26.0, 10.0),
    ("COZ-04", "Peneira", "Cozinha", 19.0, 6.5),
    ("BAN-01", "Toalha banho", "Banho", 42.0, 18.0),
    ("BAN-02", "Toalha rosto", "Banho", 18.0, 7.0),
    ("BAN-03", "Tapete box", "Banho", 35.0, 14.5),
    ("ESC-01", "Caderno A5", "Escritorio", 16.0, 6.0),
    ("ESC-02", "Caneta esferografica", "Escritorio", 4.5, 1.2),
    ("ESC-03", "Organizador mesa", "Escritorio", 38.0, 15.0),
    ("ESC-04", "Luminaria mesa", "Escritorio", 95.0, 44.0),
]

CENTROS = ["Leme", "Vela", "Mastro", "Quilha", "Popa"]
CANAIS = ["balcao", "site", "televendas"]
ATRASO_MEDIO = {"Leme": 0, "Vela": 1, "Mastro": 0, "Quilha": 2, "Popa": 1}


def catalogo() -> pd.DataFrame:
    return pd.DataFrame(
        PRODUTOS,
        columns=["sku", "produto", "linha", "preco_tabela", "custo_unitario"],
    )


def construir(semente: int = SEMENTE, linhas: int = 6000) -> pd.DataFrame:
    rng = np.random.default_rng(semente)
    produtos = catalogo()
    escolhido = rng.integers(0, len(produtos), size=linhas)
    base = produtos.iloc[escolhido].reset_index(drop=True)
    dias = pd.bdate_range("2025-01-01", "2025-12-31").to_numpy()
    data_pedido = pd.Series(pd.to_datetime(rng.choice(dias, size=linhas)))
    quebra = rng.random(linhas) < 0.42
    quebra[0] = True
    pedido = [f"PED-{numero:05d}" for numero in np.cumsum(quebra)]
    centro = rng.choice(CENTROS, size=linhas, p=[0.22, 0.20, 0.20, 0.18, 0.20])
    canal = rng.choice(CANAIS, size=linhas, p=[0.35, 0.40, 0.25])
    quantidade = rng.integers(1, 9, size=linhas)
    desconto = np.where(
        canal == "site",
        rng.uniform(0.05, 0.28, size=linhas),
        np.where(
            canal == "televendas",
            rng.uniform(0.0, 0.12, size=linhas),
            rng.uniform(0.0, 0.08, size=linhas),
        ),
    )
    prazo = np.where(centro == "Quilha", 5, 3)
    atraso = np.array([int(rng.normal(ATRASO_MEDIO[item], 1.4)) for item in centro])
    data_prometida = data_pedido + pd.to_timedelta(prazo, unit="D")
    data_entrega = data_pedido + pd.to_timedelta(np.maximum(prazo + atraso, 0), unit="D")
    cancelado = rng.random(linhas) < 0.09
    data_entrega = data_entrega.mask(cancelado)

    return pd.DataFrame(
        {
            "id_linha": [f"LIN-{indice:05d}" for indice in range(1, linhas + 1)],
            "pedido": pedido,
            "data_pedido": data_pedido.dt.strftime("%Y-%m-%d"),
            "centro": centro,
            "canal": canal,
            "sku": base["sku"].to_numpy(),
            "quantidade": quantidade,
            "preco_tabela": base["preco_tabela"].to_numpy(),
            "desconto": np.round(desconto, 4),
            "custo_unitario": base["custo_unitario"].to_numpy(),
            "data_prometida": data_prometida.dt.strftime("%Y-%m-%d"),
            "data_entrega": data_entrega.dt.strftime("%Y-%m-%d").fillna(""),
            "situacao": np.where(cancelado, "cancelado", "entregue"),
        }
    )


def sujar(limpo: pd.DataFrame, semente: int = SEMENTE) -> pd.DataFrame:
    rng = np.random.default_rng(semente + 7)
    sujo = limpo.copy()
    copias = sujo.iloc[rng.choice(len(sujo), size=25, replace=False)].copy()
    sujo = pd.concat([sujo, copias], ignore_index=True)

    def posicoes(quantidade: int) -> np.ndarray:
        return rng.choice(len(sujo), size=quantidade, replace=False)

    quantidade_ruim = posicoes(30)
    sujo.loc[sujo.index[quantidade_ruim], "quantidade"] = -1

    sem_desconto = posicoes(40)
    sujo.loc[sujo.index[sem_desconto], "desconto"] = np.nan

    em_pontos = posicoes(35)
    sujo.loc[sujo.index[em_pontos], "desconto"] = (
        pd.to_numeric(sujo.loc[sujo.index[em_pontos], "desconto"], errors="coerce").fillna(0.1) * 100
    )

    invertidas = posicoes(12)
    pedido = pd.to_datetime(sujo.loc[sujo.index[invertidas], "data_pedido"])
    sujo.loc[sujo.index[invertidas], "data_entrega"] = (pedido - pd.Timedelta(days=2)).dt.strftime("%Y-%m-%d")
    sujo.loc[sujo.index[invertidas], "situacao"] = "entregue"

    desconhecidas = posicoes(8)
    sujo.loc[sujo.index[desconhecidas], "sku"] = "SKU-404"

    caixa_alta = posicoes(20)
    sujo.loc[sujo.index[caixa_alta], "situacao"] = " Entregue "
    return sujo


def gravar(destino: Path | None = None, semente: int = SEMENTE) -> Path:
    pasta = destino or RAIZ / "data" / "bruto"
    pasta.mkdir(parents=True, exist_ok=True)
    sujar(construir(semente)).to_csv(pasta / "itens.csv", index=False)
    catalogo().to_csv(pasta / "produtos.csv", index=False)
    return pasta


if __name__ == "__main__":
    print(gravar())
