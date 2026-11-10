
import pandas as pd
import mysql.connector
from sqlalchemy import create_engine

#=============================================
# CONFIGURAÇÃO DO BANCO
#=============================================

DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "Sua Senha"

DB_SILVER = "retropixel_silver"
DB_GOLD = "retropixel_gold"

DB_PORT = 3306


#=============================================
# CRIAÇÃO DAS CONEXÕES
#=============================================

def criar_engine(database):

    conexao = (
        f"mysql+mysqlconnector://"
        f"{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{database}"
    )

    return create_engine(conexao)


#=============================================
# CRIANDO BANCO GOLD
#=============================================

def criar_banco_gold():

    conexao = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )

    cursor = conexao.cursor()

    cursor.execute(
        f"CREATE DATABASE IF NOT EXISTS {DB_GOLD};"
    )

    conexao.commit()

    cursor.close()
    conexao.close()

    print("Banco Gold criado e verificado com sucesso!")


#=============================================
# CONSULTA: FATURAMENTO MENSAL
#=============================================

def gerar_faturamento_mensal(engine):

    print("\nGerando faturamento mensal...")

    query = """
        SELECT
            YEAR(data_pedido) AS ano,
            MONTH(data_pedido) AS mes,

            COUNT(DISTINCT id_pedido)
                AS quantidade_pedidos,

            ROUND(SUM(valor_total), 2)
                AS faturamento_total

        FROM pedidos

        GROUP BY
            YEAR(data_pedido),
            MONTH(data_pedido)

        ORDER BY ano, mes;
    """

    return pd.read_sql(query, engine)


#=============================================
# CONSULTA: PRODUTOS MAIS VENDIDOS
#=============================================

def gerar_produtos_mais_vendidos(engine):

    print("\nGerando produtos mais vendidos...")

    query = """
        SELECT
            pr.id_produto,
            pr.nome_produto,

            SUM(i.quantidade)
                AS unidades_vendidas,

            ROUND(
                SUM(i.quantidade * i.preco_unitario),
                2
            ) AS faturamento_produto

        FROM itens_pedido i

        INNER JOIN produtos pr
            ON i.id_produto = pr.id_produto

        GROUP BY
            pr.id_produto,
            pr.nome_produto

        ORDER BY unidades_vendidas DESC;
    """

    return pd.read_sql(query, engine)


#=============================================
# CONSULTA: CLIENTES MAIS ATIVOS
#=============================================

def gerar_clientes_mais_ativos(engine):

    print("\nGerando clientes mais ativos...")

    query = """
        SELECT
            c.id_cliente,
            c.nome,

            COUNT(p.id_pedido)
                AS quantidade_pedidos,

            ROUND(SUM(p.valor_total), 2)
                AS total_gasto

        FROM clientes c

        INNER JOIN pedidos p
            ON c.id_cliente = p.id_cliente

        GROUP BY
            c.id_cliente,
            c.nome

        ORDER BY total_gasto DESC;
    """

    return pd.read_sql(query, engine)


#=============================================
# CARREGAMENTO NA GOLD
#=============================================

def carregar_gold(engine, dados, tabela):

    dados.to_sql(
        name=tabela,
        con=engine,
        if_exists="replace",
        index=False
    )

    print(
        f"Tabela {tabela} carregada: "
        f"{len(dados)} registros."
    )


#=============================================
# PIPELINE PRINCIPAL
#=============================================

def pipeline_silver_para_gold():

    print("=" * 60)
    print("PIPELINE SILVER => GOLD")
    print("=" * 60)

    # 1. Criar banco Gold

    criar_banco_gold()

    # 2. Criar conexões

    engine_silver = criar_engine(DB_SILVER)
    engine_gold = criar_engine(DB_GOLD)

    # 3. Gerar indicadores

    faturamento = gerar_faturamento_mensal(
        engine_silver
    )

    produtos = gerar_produtos_mais_vendidos(
        engine_silver
    )

    clientes = gerar_clientes_mais_ativos(
        engine_silver
    )

    # 4. Carregar resultados na Gold

    carregar_gold(
        engine_gold,
        faturamento,
        "faturamento_mensal"
    )

    carregar_gold(
        engine_gold,
        produtos,
        "produtos_mais_vendidos"
    )

    carregar_gold(
        engine_gold,
        clientes,
        "clientes_mais_ativos"
    )

    print("\n")
    print("=" * 60)
    print("PIPELINE SILVER => GOLD FINALIZADO!")
    print("=" * 60)


if __name__ == "__main__":
    pipeline_silver_para_gold()
