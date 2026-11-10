import pandas as pd
import mysql.connector 
from sqlalchemy import create_engine

#=============================================
# CONFIGURAÇAO DO BANCO
#=============================================

DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "Sua Senha"
DB_BRONZE = "retropixel_bronze"
DB_SILVER = "retropixel_silver"
DB_PORT = 3306

#============================================
# CRIAÇÃO DA CONEXÃO COM O MYSQL
#============================================

def criar_engine(database):

    conexao = (
        f"mysql+mysqlconnector://"
        f"{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{database}"
    )

    return create_engine(conexao)

#==============================================
# CRIANDO BANCO SILVER
#==============================================

def criar_banco_silver():

    conexao = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )

    cursor = conexao.cursor()

    cursor.execute(
        f"CREATE DATABASE IF NOT EXISTS {DB_SILVER};"
    )

    conexao.commit()

    cursor.close()
    conexao.close()

    print("Banco Silver Criado e Verificado com Sucesso !.")


#===============================================
# EXTRAÇÃO DOS DADOS DA BRONZE
#===============================================

def extrair_bronze():

    print("\nExtraindo Dados da Camada Bronze...")

    engine_bronze = criar_engine(DB_BRONZE)

    plataformas = pd.read_sql(
        "SELECT * FROM plataformas",
            engine_bronze
    )

    produtos = pd.read_sql(
            "SELECT * FROM produtos",
            engine_bronze
    )

    clientes = pd.read_sql(
            "SELECT * FROM clientes",
            engine_bronze
    )

    pedidos = pd.read_sql(
            "SELECT * FROM pedidos",
            engine_bronze
    )

    itens_pedido = pd.read_sql(
            "SELECT * FROM itens_pedido",
            engine_bronze
    )

    print("Dados Extraídos com Sucesso !.")

    return (
            plataformas,
            produtos,
            clientes,
            pedidos,
            itens_pedido
    )


#==============================================
# TRATAMENTO DAS PLATAFORMAS
#==============================================

def tratar_plataformas(df):

    print("\nTratando plataformas...")

    df = df.copy()

    # Remove espaços antes e depois do texto
    df["nome"] = (
        df["nome"]
        .str.strip()
    )

    # Padroniza um maiúsculas
    df["nome"] = (
        df["nome"]
        .str.upper()
    )

    # Remove espaços do fabricante
    df["fabricante"] = (
        df["fabricante"]
        .str.strip()
    )

    # Padroniza fabricante em maiúsculas
    df["fabricante"] = (
        df["fabricante"]
        .str.upper()
    )

    # Troca strings vazias por valores nulos
    df["fabricante"] = (
        df["fabricante"]
        .replace("", pd.NA)
    )

    return df


#=======================================
# TRATAMENTO DOS PRODUTOS
#=======================================

def tratar_produtos(df):

    print("Tratando produtos...")

    df = df.copy()

    # Remove espaços extras
    df["nome_produto"] = (
        df["nome_produto"]
        .str.strip()
    )

    # Padroniza em maiúsculas
    df["nome_produto"] = (
        df["nome_produto"]
        .str.upper()
    )

    # Converte preço para número
    df["preco"] = pd.to_numeric(
        df["preco"],
        errors="coerce"
    )

    # Arredonda o preço para duas casas
    df["preco"] = df["preco"].round(2)

    # Converte o estoque para número
    df["estoque"] = pd.to_numeric(
        df["estoque"],
        errors="coerce"
    )

    # Estoques negativos passam a ser zero
    df.loc[
        df["estoque"] < 0,
        "estoque"
    ] = 0

    # Remove produtos sem preço válido
    df = df[
        df["preco"].notna()
    ]

    # Remove preços negativos
    df = df[
        df["preco"] >= 0
    ]

    return df


#==================================================
# FUNÇÃO PARA TRATAR CPF E PASSAPORTE
#==================================================

def tratar_documento(documento):

    print("Tratando documentos...")

    if pd.isna(documento):
        return None

    # converte para string
    documento = str(documento).strip()

    if documento == "":
        return None

    # Cliente estrangeiro
    if documento.upper().startswith("PASS-"):
        return documento.upper()

    # Cliente brasileiro
    # Mantém apenas números
    documento = "".join(
        caractere
        for caractere in documento
        if caractere.isdigit()
    )

    if documento == "":
        return None

    return documento


#=================================================
# TRATAMENTO DOS CLIENTES
#=================================================

def tratar_clientes(df):

    print("Tratando clientes...")

    df = df.copy()

    #---------------------------------------------------------------
    # NOME
    #---------------------------------------------------------------

    df["nome"] = (
        df["nome"]
        .str.strip()
        .str.upper()
    )

    #------------------------------------------------------------
    # CPF / PASSAPORTE
    #------------------------------------------------------------

    df["cpf"] = (
        df["cpf"]
        .apply(tratar_documento)
    )

    #------------------------------------------------------------
    # E-MAIL
    #------------------------------------------------------------

    df["email"] = (
        df["email"]
        .str.strip() #tira os espaços 
        .str.lower() #minusculo
    )

    # Strings vazias passam a ser nulas
    df["email"] = (
        df["email"]
        .replace("", pd.NA)
    )


    #--------------------------------------------------------------
    # DATA DE CADASTRO
    #--------------------------------------------------------------

    df["data_cadastro"] = pd.to_datetime(
        df["data_cadastro"],
        errors="coerce" #deixará nulo as datas que o pandas não conseguir converter
    )

    return df

#====================================================================
# TRATAMENTO DOS PEDIDOS
#====================================================================

def tratar_pedidos(df):

    print("Tratamento pedidos...")

    df = df.copy()

    # Converte a data
    df["dat_pedido"] = pd.to_datetime(
        df["data_pedido"],
        errors="coerce"
    )

    # Converte valor total
    df["valor_total"] = pd.to_numeric(
        df["valor_total"],
        errors="coerce"
    )

    # Arredonda para duas casas
    df["valor_total"] = (
        df["valor_total"]
        .round(2)
    )

    # Remove pedidos sem data
    df = df[
        df["data_pedido"].notna()
    ]

    # Remove pedidos sem valor
    df = df[
        df["valor_total"].notna()
    ]

    # Remove valores negativos
    df = df[
        df["valor_total"] >= 0
    ]

    return df


#======================================================
# TRATAMENTO DOS ITENS PEDIDOS
#======================================================

def tratar_itens_pedidos(df):

    print("Tratando itens do pedido...")

    df = df.copy()

    # Quantidade para número
    df["quantidade"] = pd.to_numeric(
        df["quantidade"],
        errors="coerce"
    )

    # Preço unitário para número
    df["preco_unitario"] = pd.to_numeric(
        df["preco_unitario"],
        errors="coerce"
    )

    # Arredonda preço
    df["preco_unitario"] = (
        df["preco_unitario"]
        .round(2)
    )

    # Remove quantidades inválidas 
    df = df[
        df["quantidade"] > 0
    ]

    # Remove preços inválidos
    df = df[
        df["preco_unitario"] >= 0
    ]

    return df


#=======================================================================
# CARREGAMENTO NA CAMADA SILVER
#=======================================================================

def carregar_silver(
        plataformas,
        produtos,
        clientes,
        pedidos,
        itens_pedido
):

    print("\n Carregando dados na camada Silver...")

    engine_silver = criar_engine(DB_SILVER)

    #----------------------------------------------------------------------
    # PLATAFORMA
    #----------------------------------------------------------------------

    plataformas.to_sql(
        name="plataformas",
        con=engine_silver,
        if_exists="replace",
        index=False
    )

    print(
        f"Plataformas carregadas: "
        f"{len(plataformas)}"
    )

    #-----------------------------------------------------------------------
    # PRODUTOS
    #-----------------------------------------------------------------------

    produtos.to_sql(
        name="produtos",
        con=engine_silver,
        if_exists="replace",
        index=False
    )

    print(
        f"Produtos carregados: "
        f"{len(produtos)}"
    )

    #------------------------------------------------------------------------
    # Clientes
    #------------------------------------------------------------------------

    clientes.to_sql(
        name="clientes",
        con=engine_silver,
        if_exists="replace",
        index=False
    )

    print(
        f"Clientes carregados: "
        f"{len(clientes)}"
    )

    #-----------------------------------------------------------------------
    # PEDIDOS
    #-----------------------------------------------------------------------

    pedidos.to_sql(
        name="pedidos",
        con=engine_silver,
        if_exists="replace",
        index=False
    )
    
    print(
        f"pedidos carregados: "
        f"{len(pedidos)}"
    )
    
    #-----------------------------------------------------------------------
    # ITENS
    #-----------------------------------------------------------------------

    itens_pedido.to_sql(
        name="itens_pedido",
        con=engine_silver,
        if_exists="replace",
        index=False
    )
    
    print(
        f"itens carregados: "
        f"{len(itens_pedido)}"
    )

    print("\nCarga da camada Silver concluída.")


#=========================================================================
#  EXIBIR COMPARAÇÃO BRONZE X SILVER
# ========================================================================

def mostrar_comparacao(
        clientes_bronze,
        clientes_silver
):

    print("Comparando Camadas : Bronze e Silver\n")

    print("\n")
    print("=" * 60)
    print("EXEMPLO BRONZE")
    print("=" * 60)

    print(
        clientes_bronze[
            [
                "id_cliente",
                "nome",
                "cpf",
                "email"
            ]
        ].head(10)
    )

    print("\n")   
    print("=" * 60)
    print("EXEMPLO SILVER")
    print("=" * 60)

    print(
        clientes_silver[
            [
                "id_cliente",
                "nome",
                "cpf",
                "email"
            ]
        ].head(10)
    )


#=============================================================
# PIPELINE PRINCIPAL
#=============================================================

def pipeline_bronze_para_silver():

    print("=" * 60)
    print("PIPELINE BRONZE => SILVER")
    print("=" * 60)

    #----------------------------------------------------------
    # 1. CRIA SILVER
    #----------------------------------------------------------

    criar_banco_silver()

    #----------------------------------------------------------
    # 2. EXTRAIR
    #----------------------------------------------------------

    (
        plataformas_bronze,
        produtos_bronze,
        clientes_bronze,
        pedidos_bronze,
        itens_bronze
    ) = extrair_bronze()



    #--------------------------------------------------------------
    # 3. TRANSFORM
    #-------------------------------------------------------------

    plataformas_silver = tratar_plataformas(
        plataformas_bronze
    )
    
    produtos_silver =  tratar_produtos(
        produtos_bronze
    )
    
    clientes_silver = tratar_clientes(
        clientes_bronze
    )
    pedidos_silver = tratar_pedidos(
        pedidos_bronze
    )
    
    itens_silver = tratar_itens_pedidos(
        itens_bronze
    )

    #--------------------------------------------------------------
    # 4- MOSTRA EXEMPLO DO TRATAMENTO
    #-------------------------------------------------------------
    
    mostrar_comparacao(
        clientes_bronze,
        clientes_silver
    )
    
    carregar_silver(
        plataformas_silver,
        produtos_silver,
        clientes_silver,
        pedidos_silver,
        itens_silver
    )
    
    print("\n")
    print("=" * 60)
    print("PIPELINE FINALIZADO COM SUCESSO")
    print("=" * 60)
    
    
    #--------------------------------------------------------------
    # EXECUÇÃO
    #-------------------------------------------------------------
    
if __name__ == "__main__":
    pipeline_bronze_para_silver()


print("\nAplicação Encerrada Com Sucesso !")
