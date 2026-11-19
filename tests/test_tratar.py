import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from tratar import preparar


def linha(**alteracoes) -> dict:
    base = {
        "id_linha": "LIN-00001",
        "pedido": "PED-00001",
        "data_pedido": "2025-03-01",
        "centro": "Leme",
        "canal": "site",
        "sku": "COP-01",
        "quantidade": 2,
        "preco_tabela": 18.0,
        "desconto": 0.1,
        "custo_unitario": 7.2,
        "data_prometida": "2025-03-04",
        "data_entrega": "2025-03-04",
        "situacao": "entregue",
    }
    base.update(alteracoes)
    return base


PRODUTOS = pd.DataFrame(
    [{"sku": "COP-01", "produto": "Copo vidro 300 ml", "linha": "Copa", "preco_tabela": 18.0, "custo_unitario": 7.2}]
)


class Tratamento(unittest.TestCase):
    def test_calcula_receita_e_prazo(self):
        limpo, descartes = preparar(pd.DataFrame([linha()]), PRODUTOS)
        self.assertTrue(descartes.empty)
        self.assertEqual(limpo.loc[0, "receita_liquida"], 32.4)
        self.assertEqual(limpo.loc[0, "margem"], 18.0)
        self.assertEqual(int(limpo.loc[0, "no_prazo"]), 1)

    def test_desconto_gravado_em_pontos_vira_fracao(self):
        limpo, _ = preparar(pd.DataFrame([linha(desconto=12)]), PRODUTOS)
        self.assertAlmostEqual(limpo.loc[0, "desconto"], 0.12)

    def test_desconto_vazio_vira_zero(self):
        limpo, _ = preparar(pd.DataFrame([linha(desconto=None)]), PRODUTOS)
        self.assertEqual(limpo.loc[0, "desconto"], 0)

    def test_descarta_duplicado_quantidade_sku_e_data(self):
        bruto = pd.DataFrame(
            [
                linha(),
                linha(),
                linha(id_linha="LIN-00002", quantidade=-1),
                linha(id_linha="LIN-00003", sku="SKU-404"),
                linha(id_linha="LIN-00004", data_entrega="2025-02-20"),
                linha(id_linha="LIN-00005", situacao=" Entregue "),
            ]
        )
        limpo, descartes = preparar(bruto, PRODUTOS)
        motivos = dict(zip(descartes["motivo"], descartes["linhas"]))
        self.assertEqual(motivos["id_duplicado"], 1)
        self.assertEqual(motivos["quantidade_invalida"], 1)
        self.assertEqual(motivos["sku_sem_cadastro"], 1)
        self.assertEqual(motivos["entrega_antes_do_pedido"], 1)
        self.assertEqual(len(limpo), 2)
        self.assertIn("LIN-00005", set(limpo["id_linha"]))


if __name__ == "__main__":
    unittest.main()
