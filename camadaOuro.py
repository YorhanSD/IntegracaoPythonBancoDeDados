
"""
DEPENDÊNCIAS
============

pip install pandas faker sqlalchemy pymysql
"""

# ============================================================
# 1. IMPORTAÇÕES
# ============================================================

# random controla as probabilidades das regras de negócio.
import random

# Datas das vendas e dos cadastros.
from datetime import date, timedelta

# Criação e manipulação dos caminhos das pastas.
from pathlib import Path

# quote_plus codifica usuário/senha para uso seguro na URL de conexão.
# Isso evita problemas caso a senha contenha caracteres especiais.
from urllib.parse import quote_plus

# Pandas: extração, tratamento, transformação e carga tabular.
import pandas as pd

# Faker: geração de dados cadastrais sintéticos brasileiros.
from faker import Faker

# SQLAlchemy: camada de conexão entre Python/Pandas e MySQL.
from sqlalchemy import create_engine, text

# URL permite montar a conexão MySQL sem concatenar manualmente a senha.
from sqlalchemy.engine import URL


# ============================================================
# 2. CONFIGURAÇÃO DO MYSQL
# ============================================================

MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_USUARIO = "root"
MYSQL_SENHA = "Sua Senha"

# Dois bancos no MESMO servidor MySQL.
BANCO_OLTP = "empresa_oltp"
BANCO_DW = "empresa_dw"

# Charset utf8mb4 preserva corretamente caracteres como:
# São Paulo, Áudio, João etc.
MYSQL_CHARSET = "utf8mb4"


# ============================================================
# 3. CONFIGURAÇÃO DAS PASTAS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

BRONZE_DIR = BASE_DIR / "data" / "bronze"
SILVER_DIR = BASE_DIR / "data" / "silver"


# ============================================================
# 4. VOLUME DOS DADOS
# ============================================================

QTD_CLIENTES = 500
QTD_VENDEDORES = 20
QTD_PEDIDOS = 4000

# Faker configurado para português do Brasil.
fake = Faker("pt_BR")

# Não usamos random.seed() nem Faker.seed() fixos.
# Cada execução produzirá dados diferentes.


# ============================================================
# 5. CATÁLOGO CONTROLADO DE PRODUTOS
# ============================================================

# O Faker NÃO gera produtos porque queremos categorias e preços
# estáveis para que existam análises comparáveis no projeto.
#
# Estrutura:
# SKU, nome, categoria, marca, preço.

PRODUTOS = [
    ("NTB-001", "Notebook Start 14", "Notebooks", "TechOne", 2899.90),
    ("NTB-002", "Notebook Pro 15", "Notebooks", "MaxByte", 4199.90),
    ("NTB-003", "Notebook Ultra 16", "Notebooks", "VisionTech", 5799.90),

    ("PER-001", "Mouse Óptico", "Periféricos", "TechOne", 79.90),
    ("PER-002", "Mouse Gamer", "Periféricos", "HyperCore", 189.90),
    ("PER-003", "Teclado Mecânico", "Periféricos", "HyperCore", 349.90),

    ("MON-001", "Monitor 22", "Monitores", "VisionTech", 799.90),
    ("MON-002", "Monitor 24", "Monitores", "VisionTech", 1099.90),
    ("MON-003", "Monitor 27", "Monitores", "MaxByte", 1599.90),

    ("ARM-001", "SSD 500GB", "Armazenamento", "FastDisk", 299.90),
    ("ARM-002", "SSD 1TB", "Armazenamento", "FastDisk", 499.90),
    ("ARM-003", "HD Externo 2TB", "Armazenamento", "DataSafe", 569.90),

    ("AUD-001", "Headset USB", "Áudio", "SoundPro", 199.90),
    ("AUD-002", "Headset Gamer", "Áudio", "HyperCore", 329.90),
    ("AUD-003", "Caixa de Som Bluetooth", "Áudio", "SoundPro", 249.90),

    ("ACE-001", "Mochila para Notebook", "Acessórios", "UrbanCase", 169.90),
    ("ACE-002", "Hub USB-C", "Acessórios", "ConnectX", 219.90),
    ("ACE-003", "Suporte para Notebook", "Acessórios", "UrbanCase", 139.90),
]

FORMAS_PAGAMENTO = [
    "Pix",
    "Cartão de crédito",
    "Cartão de débito",
    "Boleto"
]


# ============================================================
# 6. FUNÇÕES DE CONEXÃO
# ============================================================

def criar_url_mysql(database=None):
    """
    Monta a URL de conexão do SQLAlchemy.

    Quando database=None, conectamos somente ao servidor MySQL.
    Isso é necessário antes de empresa_oltp e empresa_dw existirem.

    Quando database recebe um nome, conectamos diretamente ao banco.
    """

    return URL.create(
        drivername="mysql+pymysql",
        username=MYSQL_USUARIO,
        password=MYSQL_SENHA,
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        database=database,
        query={"charset": MYSQL_CHARSET}
    )


def criar_engine_mysql(database=None):
    """
    Cria um Engine do SQLAlchemy.

    Engine é o objeto responsável por administrar conexões
    entre Python e o banco de dados.

    pool_pre_ping=True verifica a conexão antes de reutilizá-la.
    """

    return create_engine(
        criar_url_mysql(database),
        pool_pre_ping=True
    )


def testar_conexao_mysql():
    """
    Testa se o MySQL está acessível com as credenciais informadas.

    Se o serviço estiver parado, usuário/senha estiverem incorretos
    ou PyMySQL não estiver instalado, o programa apresentará erro aqui.
    """

    engine_servidor = criar_engine_mysql()

    with engine_servidor.connect() as conn:
        versao = conn.execute(
            text("SELECT VERSION();")
        ).scalar()

    engine_servidor.dispose()

    print(
        f"MySQL conectado em {MYSQL_HOST}:{MYSQL_PORT} "
        f"| versão: {versao}"
    )


# ============================================================
# 7. FUNÇÕES AUXILIARES
# ============================================================

def preparar_pastas():
    """Cria as pastas Bronze e Silver."""

    BRONZE_DIR.mkdir(parents=True, exist_ok=True)
    SILVER_DIR.mkdir(parents=True, exist_ok=True)


def limpar_csvs(pasta):
    """Remove CSVs antigos para evitar mistura entre execuções."""

    for arquivo in pasta.glob("*.csv"):
        arquivo.unlink()


def data_aleatoria(inicio, fim):
    """Gera uma data aleatória entre inicio e fim."""

    dias = (fim - inicio).days

    return inicio + timedelta(
        days=random.randint(0, dias)
    )


def regiao_por_estado(estado):
    """
    Enriquece o estado com sua região brasileira.
    Esta coluna nasce na Silver, não no OLTP.
    """

    mapa = {
        "AC": "Norte", "AP": "Norte", "AM": "Norte",
        "PA": "Norte", "RO": "Norte", "RR": "Norte", "TO": "Norte",

        "AL": "Nordeste", "BA": "Nordeste", "CE": "Nordeste",
        "MA": "Nordeste", "PB": "Nordeste", "PE": "Nordeste",
        "PI": "Nordeste", "RN": "Nordeste", "SE": "Nordeste",

        "DF": "Centro-Oeste", "GO": "Centro-Oeste",
        "MT": "Centro-Oeste", "MS": "Centro-Oeste",

        "ES": "Sudeste", "MG": "Sudeste",
        "RJ": "Sudeste", "SP": "Sudeste",

        "PR": "Sul", "SC": "Sul", "RS": "Sul"
    }

    return mapa.get(estado, "Não informado")


# ============================================================
# 8. ETAPA 1 — CRIAÇÃO DOS DOIS DATABASES MYSQL
# ============================================================

def criar_bancos_mysql():
    """
    Conecta ao servidor MySQL sem selecionar database.

    Depois recria:
        empresa_oltp
        empresa_dw

    DROP DATABASE é usado para tornar a execução didática repetível:
    toda execução começa com uma base nova.

    ATENÇÃO:
    em ambiente real/produção não se faria DROP do banco dessa forma.
    """

    engine_servidor = criar_engine_mysql()

    # AUTOCOMMIT é apropriado para comandos administrativos
    # CREATE DATABASE e DROP DATABASE.
    with engine_servidor.connect().execution_options(
        isolation_level="AUTOCOMMIT"
    ) as conn:

        conn.execute(
            text(
                f"DROP DATABASE IF EXISTS `{BANCO_OLTP}`;"
            )
        )

        conn.execute(
            text(
                f"DROP DATABASE IF EXISTS `{BANCO_DW}`;"
            )
        )

        conn.execute(
            text(
                f"""
                CREATE DATABASE `{BANCO_OLTP}`
                CHARACTER SET utf8mb4
                COLLATE utf8mb4_unicode_ci;
                """
            )
        )

        conn.execute(
            text(
                f"""
                CREATE DATABASE `{BANCO_DW}`
                CHARACTER SET utf8mb4
                COLLATE utf8mb4_unicode_ci;
                """
            )
        )

    engine_servidor.dispose()

    print(
        "[1/8] Databases empresa_oltp e empresa_dw criados no MySQL."
    )


# ============================================================
# 9. ETAPA 2 — CRIAÇÃO DAS TABELAS DO OLTP
# ============================================================

def criar_oltp():
    """
    Cria o modelo transacional dentro de empresa_oltp.

    Relacionamentos:

    CLIENTE  1:N PEDIDO
    VENDEDOR 1:N PEDIDO
    PEDIDO   1:N ITEM_PEDIDO
    PRODUTO  1:N ITEM_PEDIDO
    """

    engine = criar_engine_mysql(BANCO_OLTP)

    comandos = [
        """
        CREATE TABLE cliente (
            id_cliente INT PRIMARY KEY,
            cpf VARCHAR(14) NOT NULL UNIQUE,
            email VARCHAR(120) NOT NULL UNIQUE,
            nome VARCHAR(100) NOT NULL,
            telefone VARCHAR(30),
            cidade VARCHAR(80) NOT NULL,
            estado CHAR(2) NOT NULL,
            data_cadastro DATE NOT NULL
        ) ENGINE=InnoDB;
        """,

        """
        CREATE TABLE vendedor (
            id_vendedor INT PRIMARY KEY,
            matricula VARCHAR(20) NOT NULL UNIQUE,
            email VARCHAR(120) NOT NULL UNIQUE,
            nome VARCHAR(100) NOT NULL,
            equipe VARCHAR(50) NOT NULL,
            estado CHAR(2) NOT NULL
        ) ENGINE=InnoDB;
        """,

        """
        CREATE TABLE produto (
            id_produto INT PRIMARY KEY,
            sku VARCHAR(30) NOT NULL UNIQUE,
            nome_produto VARCHAR(120) NOT NULL,
            categoria VARCHAR(60) NOT NULL,
            marca VARCHAR(60) NOT NULL,
            preco_lista DECIMAL(10,2) NOT NULL,
            ativo BOOLEAN NOT NULL,

            CONSTRAINT chk_produto_preco
                CHECK (preco_lista >= 0)
        ) ENGINE=InnoDB;
        """,

        """
        CREATE TABLE pedido (
            id_pedido INT PRIMARY KEY,
            numero_pedido VARCHAR(30) NOT NULL UNIQUE,
            id_cliente INT NOT NULL,
            id_vendedor INT NOT NULL,
            data_pedido DATETIME NOT NULL,
            status VARCHAR(20) NOT NULL,
            valor_frete DECIMAL(10,2) NOT NULL,
            forma_pagamento VARCHAR(30) NOT NULL,

            CONSTRAINT fk_pedido_cliente
                FOREIGN KEY (id_cliente)
                REFERENCES cliente(id_cliente),

            CONSTRAINT fk_pedido_vendedor
                FOREIGN KEY (id_vendedor)
                REFERENCES vendedor(id_vendedor),

            CONSTRAINT chk_pedido_frete
                CHECK (valor_frete >= 0)
        ) ENGINE=InnoDB;
        """,

        """
        CREATE TABLE item_pedido (
            id_item INT PRIMARY KEY,
            id_pedido INT NOT NULL,
            id_produto INT NOT NULL,
            quantidade INT NOT NULL,
            valor_unitario DECIMAL(10,2) NOT NULL,
            percentual_desconto DECIMAL(5,4) NOT NULL,
            valor_total DECIMAL(12,2) NOT NULL,

            CONSTRAINT fk_item_pedido
                FOREIGN KEY (id_pedido)
                REFERENCES pedido(id_pedido),

            CONSTRAINT fk_item_produto
                FOREIGN KEY (id_produto)
                REFERENCES produto(id_produto),

            CONSTRAINT chk_item_quantidade
                CHECK (quantidade > 0),

            CONSTRAINT chk_item_desconto
                CHECK (
                    percentual_desconto
                    BETWEEN 0 AND 0.20
                )
        ) ENGINE=InnoDB;
        """
    ]

    # engine.begin() inicia uma transação e executa COMMIT
    # automaticamente ao final, caso não ocorra erro.
    with engine.begin() as conn:

        for comando in comandos:
            conn.execute(text(comando))

    engine.dispose()

    print("[2/8] Estrutura OLTP criada no MySQL.")


# ============================================================
# 10. ETAPA 3 — POPULAÇÃO COM FAKER + REGRAS DE NEGÓCIO
# ============================================================

def popular_oltp():
    """
    Faker:
        dados cadastrais sintéticos.

    random:
        comportamento probabilístico do negócio.

    Assim, os registros mudam em cada execução, mas padrões
    pedagógicos continuam presentes.
    """

    inicio_cadastro = date(2024, 1, 1)
    fim_cadastro = date(2024, 12, 31)

    inicio_vendas = date(2025, 1, 1)
    fim_vendas = date(2026, 12, 31)

    total_dias = (
        fim_vendas - inicio_vendas
    ).days

    # --------------------------------------------------------
    # 10.1 CLIENTES
    # --------------------------------------------------------

    fake.unique.clear()

    clientes = []

    for id_cliente in range(1, QTD_CLIENTES + 1):

        clientes.append(
            {
                "id_cliente": id_cliente,

                # CPF sintético gerado pelo Faker.
                "cpf": fake.unique.cpf(),

                # safe_email usa domínios reservados para exemplos.
                "email": fake.unique.safe_email(),

                "nome": fake.name(),
                "telefone": fake.phone_number(),
                "cidade": fake.city(),
                "estado": fake.state_abbr(),

                "data_cadastro": data_aleatoria(
                    inicio_cadastro,
                    fim_cadastro
                )
            }
        )

    # --------------------------------------------------------
    # 10.2 VENDEDORES
    # --------------------------------------------------------

    vendedores = []

    for id_vendedor in range(1, QTD_VENDEDORES + 1):

        vendedores.append(
            {
                "id_vendedor": id_vendedor,

                # Matrícula é uma regra da empresa,
                # portanto não é gerada pelo Faker.
                "matricula": f"VEND{id_vendedor:03d}",

                "email": fake.unique.safe_email(),
                "nome": fake.name(),

                # 5 vendedores por equipe.
                "equipe": (
                    f"Equipe {(id_vendedor - 1) // 5 + 1}"
                ),

                "estado": fake.state_abbr()
            }
        )

    # --------------------------------------------------------
    # 10.3 PRODUTOS
    # --------------------------------------------------------

    produtos = []

    for id_produto, produto in enumerate(PRODUTOS, start=1):

        sku, nome, categoria, marca, preco = produto

        produtos.append(
            {
                "id_produto": id_produto,
                "sku": sku,
                "nome_produto": nome,
                "categoria": categoria,
                "marca": marca,
                "preco_lista": preco,
                "ativo": True
            }
        )

    # Catálogo auxiliar para geração dos itens.
    catalogo = [
        {
            "id_produto": i,
            "categoria": produto[2],
            "preco": produto[4]
        }
        for i, produto in enumerate(PRODUTOS, start=1)
    ]

    # --------------------------------------------------------
    # 10.4 PEDIDOS E ITENS
    # --------------------------------------------------------

    pedidos = []
    itens = []

    id_item = 1

    for id_pedido in range(1, QTD_PEDIDOS + 1):

        data_pedido = data_aleatoria(
            inicio_vendas,
            fim_vendas
        )

        # Varia aproximadamente de 0 a 1.
        progresso = (
            (data_pedido - inicio_vendas).days
            / total_dias
        )

        id_cliente = random.randint(
            1,
            QTD_CLIENTES
        )

        id_vendedor = random.randint(
            1,
            QTD_VENDEDORES
        )

        # Regra:
        # 92% concluído
        # 3% cancelado
        # 5% em processamento
        status = random.choices(
            [
                "Concluído",
                "Cancelado",
                "Em processamento"
            ],
            weights=[92, 3, 5],
            k=1
        )[0]

        pedidos.append(
            {
                "id_pedido": id_pedido,
                "numero_pedido": f"PED{id_pedido:06d}",
                "id_cliente": id_cliente,
                "id_vendedor": id_vendedor,
                "data_pedido": data_pedido,
                "status": status,
                "valor_frete": round(
                    random.uniform(15, 120),
                    2
                ),
                "forma_pagamento": random.choice(
                    FORMAS_PAGAMENTO
                )
            }
        )

        # Cada pedido terá entre 1 e 4 itens.
        quantidade_itens = random.randint(1, 4)

        for _ in range(quantidade_itens):

            pesos = []

            for produto in catalogo:

                categoria = produto["categoria"]
                peso = 1.0

                # REGRA 1:
                # notebooks ganham força ao longo do tempo.
                if categoria == "Notebooks":
                    peso *= 1 + 2.0 * progresso

                # REGRA 2:
                # monitores caem no último quarto do período.
                elif categoria == "Monitores":
                    if progresso >= 0.75:
                        peso *= 0.35

                # REGRA 3:
                # armazenamento cresce moderadamente.
                elif categoria == "Armazenamento":
                    peso *= 1 + 0.8 * progresso

                # REGRA 4:
                # sazonalidade.
                if data_pedido.month in (11, 12):
                    peso *= 1.5

                elif data_pedido.month in (2, 3):
                    peso *= 0.85

                pesos.append(peso)

            produto_escolhido = random.choices(
                catalogo,
                weights=pesos,
                k=1
            )[0]

            quantidade = random.randint(1, 3)

            # REGRA 5:
            # vendedor 7 tende a conceder descontos maiores.
            if id_vendedor == 7:

                desconto = random.choices(
                    [0.05, 0.10, 0.15, 0.20],
                    weights=[10, 25, 35, 30],
                    k=1
                )[0]

            else:

                desconto = random.choices(
                    [0.00, 0.05, 0.10, 0.15],
                    weights=[45, 35, 15, 5],
                    k=1
                )[0]

            valor_unitario = produto_escolhido["preco"]

            valor_total = round(
                quantidade
                * valor_unitario
                * (1 - desconto),
                2
            )

            itens.append(
                {
                    "id_item": id_item,
                    "id_pedido": id_pedido,
                    "id_produto": produto_escolhido[
                        "id_produto"
                    ],
                    "quantidade": quantidade,
                    "valor_unitario": valor_unitario,
                    "percentual_desconto": desconto,
                    "valor_total": valor_total
                }
            )

            id_item += 1

    # --------------------------------------------------------
    # 10.5 CARGA DOS DATAFRAMES NO MYSQL
    # --------------------------------------------------------

    # Converter listas de dicionários em DataFrames.
    df_clientes = pd.DataFrame(clientes)
    df_vendedores = pd.DataFrame(vendedores)
    df_produtos = pd.DataFrame(produtos)
    df_pedidos = pd.DataFrame(pedidos)
    df_itens = pd.DataFrame(itens)

    engine = criar_engine_mysql(BANCO_OLTP)

    # to_sql envia o conteúdo do DataFrame para uma tabela MySQL.
    #
    # if_exists="append":
    # mantém a tabela criada manualmente e apenas insere os registros.
    #
    # chunksize:
    # envia os dados em blocos, evitando um INSERT gigantesco.
    #
    # method="multi":
    # agrupa várias linhas em uma operação de inserção.
    df_clientes.to_sql(
        "cliente",
        engine,
        if_exists="append",
        index=False,
        chunksize=500,
        method="multi"
    )

    df_vendedores.to_sql(
        "vendedor",
        engine,
        if_exists="append",
        index=False,
        method="multi"
    )

    df_produtos.to_sql(
        "produto",
        engine,
        if_exists="append",
        index=False,
        method="multi"
    )

    df_pedidos.to_sql(
        "pedido",
        engine,
        if_exists="append",
        index=False,
        chunksize=500,
        method="multi"
    )

    df_itens.to_sql(
        "item_pedido",
        engine,
        if_exists="append",
        index=False,
        chunksize=500,
        method="multi"
    )

    engine.dispose()

    print(
        "[3/8] OLTP populado com Faker + regras controladas."
    )


# ============================================================
# 11. VALIDAÇÃO DO OLTP
# ============================================================

def validar_oltp():
    """Valida contagens e duplicidade de CPF."""

    engine = criar_engine_mysql(BANCO_OLTP)

    print("\nVALIDAÇÃO DO OLTP")

    for tabela in [
        "cliente",
        "vendedor",
        "produto",
        "pedido",
        "item_pedido"
    ]:

        consulta = text(
            f"SELECT COUNT(*) FROM `{tabela}`;"
        )

        with engine.connect() as conn:
            quantidade = conn.execute(
                consulta
            ).scalar()

        print(
            f"{tabela:<15}: {quantidade} registros"
        )

    consulta_cpf = text(
        """
        SELECT COUNT(*)
        FROM (
            SELECT cpf
            FROM cliente
            GROUP BY cpf
            HAVING COUNT(*) > 1
        ) AS duplicados;
        """
    )

    with engine.connect() as conn:
        duplicados = conn.execute(
            consulta_cpf
        ).scalar()

    print(
        f"CPFs duplicados : {duplicados}"
    )

    engine.dispose()


# ============================================================
# 12. ETAPA 4 — BRONZE
# ============================================================

def criar_bronze():
    """
    Extrai o OLTP para CSV com Pandas.

    A Bronze é uma cópia praticamente bruta da origem.
    """

    limpar_csvs(BRONZE_DIR)

    engine = criar_engine_mysql(BANCO_OLTP)

    tabelas = [
        "cliente",
        "vendedor",
        "produto",
        "pedido",
        "item_pedido"
    ]

    for tabela in tabelas:

        # read_sql lê diretamente do MySQL.
        df = pd.read_sql(
            f"SELECT * FROM `{tabela}`;",
            engine
        )

        df.to_csv(
            BRONZE_DIR / f"{tabela}.csv",
            index=False,
            encoding="utf-8-sig"
        )

    engine.dispose()

    print("[4/8] Bronze extraída do MySQL para CSV.")


# ============================================================
# 13. ETAPA 5 — SILVER COM PANDAS
# ============================================================

def criar_silver():
    """
    Trata os arquivos Bronze com Pandas.

    Aqui acontecem:
    - remoção de duplicidades;
    - tratamento de nulos;
    - padronização;
    - conversão de tipos;
    - enriquecimento;
    - merges;
    - cálculos.
    """

    limpar_csvs(SILVER_DIR)

    clientes = pd.read_csv(
        BRONZE_DIR / "cliente.csv"
    )

    vendedores = pd.read_csv(
        BRONZE_DIR / "vendedor.csv"
    )

    produtos = pd.read_csv(
        BRONZE_DIR / "produto.csv"
    )

    pedidos = pd.read_csv(
        BRONZE_DIR / "pedido.csv"
    )

    itens = pd.read_csv(
        BRONZE_DIR / "item_pedido.csv"
    )

    # --------------------------------------------------------
    # CLIENTES
    # --------------------------------------------------------

    clientes = clientes.drop_duplicates(
        subset=["id_cliente"]
    ).copy()

    clientes["telefone"] = (
        clientes["telefone"]
        .fillna("Não informado")
    )

    clientes["nome"] = (
        clientes["nome"]
        .astype(str)
        .str.strip()
    )

    clientes["cidade"] = (
        clientes["cidade"]
        .astype(str)
        .str.strip()
    )

    clientes["estado"] = (
        clientes["estado"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    clientes["data_cadastro"] = pd.to_datetime(
        clientes["data_cadastro"],
        errors="coerce"
    )

    clientes["regiao"] = (
        clientes["estado"]
        .map(regiao_por_estado)
    )

    clientes_silver = clientes[
        [
            "id_cliente",
            "nome",
            "cidade",
            "estado",
            "regiao",
            "data_cadastro"
        ]
    ].copy()

    clientes_silver.rename(
        columns={"nome": "nome_cliente"},
        inplace=True
    )

    # --------------------------------------------------------
    # VENDEDORES
    # --------------------------------------------------------

    vendedores = vendedores.drop_duplicates(
        subset=["id_vendedor"]
    ).copy()

    vendedores["nome"] = (
        vendedores["nome"]
        .astype(str)
        .str.strip()
    )

    vendedores["equipe"] = (
        vendedores["equipe"]
        .astype(str)
        .str.strip()
    )

    vendedores["estado"] = (
        vendedores["estado"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    vendedores["regiao"] = (
        vendedores["estado"]
        .map(regiao_por_estado)
    )

    vendedores_silver = vendedores[
        [
            "id_vendedor",
            "nome",
            "equipe",
            "estado",
            "regiao"
        ]
    ].copy()

    vendedores_silver.rename(
        columns={"nome": "nome_vendedor"},
        inplace=True
    )

    # --------------------------------------------------------
    # PRODUTOS
    # --------------------------------------------------------

    produtos = produtos.drop_duplicates(
        subset=["id_produto"]
    ).copy()

    produtos["sku"] = (
        produtos["sku"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    produtos["nome_produto"] = (
        produtos["nome_produto"]
        .astype(str)
        .str.strip()
    )

    produtos["categoria"] = (
        produtos["categoria"]
        .astype(str)
        .str.strip()
    )

    produtos["marca"] = (
        produtos["marca"]
        .astype(str)
        .str.strip()
    )

    produtos["preco_lista"] = pd.to_numeric(
        produtos["preco_lista"],
        errors="coerce"
    )

    produtos_silver = produtos[
        [
            "id_produto",
            "sku",
            "nome_produto",
            "categoria",
            "marca",
            "preco_lista",
            "ativo"
        ]
    ].copy()

    # --------------------------------------------------------
    # PEDIDOS
    # --------------------------------------------------------

    pedidos = pedidos.drop_duplicates(
        subset=["id_pedido"]
    ).copy()

    pedidos["data_pedido"] = pd.to_datetime(
        pedidos["data_pedido"],
        errors="coerce"
    )

    pedidos["status"] = (
        pedidos["status"]
        .astype(str)
        .str.strip()
    )

    pedidos["forma_pagamento"] = (
        pedidos["forma_pagamento"]
        .astype(str)
        .str.strip()
    )

    pedidos["valor_frete"] = pd.to_numeric(
        pedidos["valor_frete"],
        errors="coerce"
    )

    pedidos["ano"] = pedidos["data_pedido"].dt.year
    pedidos["mes"] = pedidos["data_pedido"].dt.month
    pedidos["trimestre"] = pedidos["data_pedido"].dt.quarter

    mapa_meses = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março",
        4: "Abril", 5: "Maio", 6: "Junho",
        7: "Julho", 8: "Agosto", 9: "Setembro",
        10: "Outubro", 11: "Novembro", 12: "Dezembro"
    }

    pedidos["nome_mes"] = (
        pedidos["mes"]
        .map(mapa_meses)
    )

    pedidos_silver = pedidos[
        [
            "id_pedido",
            "numero_pedido",
            "id_cliente",
            "id_vendedor",
            "data_pedido",
            "ano",
            "mes",
            "nome_mes",
            "trimestre",
            "status",
            "valor_frete",
            "forma_pagamento"
        ]
    ].copy()

    # --------------------------------------------------------
    # ITENS
    # --------------------------------------------------------

    itens = itens.drop_duplicates(
        subset=["id_item"]
    ).copy()

    for coluna in [
        "quantidade",
        "valor_unitario",
        "percentual_desconto"
    ]:

        itens[coluna] = pd.to_numeric(
            itens[coluna],
            errors="coerce"
        )

    # --------------------------------------------------------
    # MERGES
    # --------------------------------------------------------

    # merge() é conceitualmente equivalente a JOIN.
    vendas = itens.merge(
        pedidos_silver,
        on="id_pedido",
        how="inner"
    )

    vendas = vendas.merge(
        produtos_silver,
        on="id_produto",
        how="inner"
    )

    clientes_merge = (
        clientes_silver[
            ["id_cliente", "estado", "regiao"]
        ]
        .rename(
            columns={
                "estado": "estado_cliente",
                "regiao": "regiao_cliente"
            }
        )
    )

    vendas = vendas.merge(
        clientes_merge,
        on="id_cliente",
        how="inner"
    )

    vendedores_merge = (
        vendedores_silver[
            ["id_vendedor", "estado", "regiao"]
        ]
        .rename(
            columns={
                "estado": "estado_vendedor",
                "regiao": "regiao_vendedor"
            }
        )
    )

    vendas = vendas.merge(
        vendedores_merge,
        on="id_vendedor",
        how="inner"
    )

    # --------------------------------------------------------
    # MEDIDAS
    # --------------------------------------------------------

    vendas["valor_bruto"] = (
        vendas["quantidade"]
        * vendas["valor_unitario"]
    ).round(2)

    vendas["valor_desconto"] = (
        vendas["valor_bruto"]
        * vendas["percentual_desconto"]
    ).round(2)

    vendas["valor_liquido"] = (
        vendas["valor_bruto"]
        - vendas["valor_desconto"]
    ).round(2)

    vendas_silver = vendas[
        [
            "id_item",
            "id_pedido",
            "numero_pedido",
            "data_pedido",
            "ano",
            "mes",
            "nome_mes",
            "trimestre",
            "status",

            "id_cliente",
            "estado_cliente",
            "regiao_cliente",

            "id_vendedor",
            "estado_vendedor",
            "regiao_vendedor",

            "id_produto",
            "sku",
            "categoria",
            "marca",

            "quantidade",
            "valor_unitario",
            "percentual_desconto",
            "valor_bruto",
            "valor_desconto",
            "valor_liquido"
        ]
    ].copy()

    # --------------------------------------------------------
    # GRAVAÇÃO SILVER
    # --------------------------------------------------------

    arquivos = {
        "clientes_tratados.csv": clientes_silver,
        "vendedores_tratados.csv": vendedores_silver,
        "produtos_tratados.csv": produtos_silver,
        "pedidos_tratados.csv": pedidos_silver,
        "vendas_tratadas.csv": vendas_silver
    }

    for nome, dataframe in arquivos.items():

        dataframe.to_csv(
            SILVER_DIR / nome,
            index=False,
            encoding="utf-8-sig"
        )

    print("[5/8] Silver tratada com Pandas.")


# ============================================================
# 14. ETAPA 6 — CRIAÇÃO DO DATA WAREHOUSE NO MYSQL
# ============================================================

def criar_dw():
    """
    Cria o modelo estrela dentro de empresa_dw.

                      DIM_TEMPO
                          |
                          |
         DIM_CLIENTE -- FATO_VENDAS -- DIM_PRODUTO
                          |
                          |
                     DIM_VENDEDOR

    GRÃO:
    uma linha da fato representa um item vendido
    pertencente a um pedido concluído.
    """

    engine = criar_engine_mysql(BANCO_DW)

    comandos = [
        """
        CREATE TABLE dim_cliente (
            sk_cliente INT AUTO_INCREMENT PRIMARY KEY,
            id_cliente_origem INT NOT NULL UNIQUE,
            nome_cliente VARCHAR(100) NOT NULL,
            cidade VARCHAR(80) NOT NULL,
            estado CHAR(2) NOT NULL,
            regiao VARCHAR(20) NOT NULL,
            data_cadastro DATE NOT NULL
        ) ENGINE=InnoDB;
        """,

        """
        CREATE TABLE dim_vendedor (
            sk_vendedor INT AUTO_INCREMENT PRIMARY KEY,
            id_vendedor_origem INT NOT NULL UNIQUE,
            nome_vendedor VARCHAR(100) NOT NULL,
            equipe VARCHAR(50) NOT NULL,
            estado CHAR(2) NOT NULL,
            regiao VARCHAR(20) NOT NULL
        ) ENGINE=InnoDB;
        """,

        """
        CREATE TABLE dim_produto (
            sk_produto INT AUTO_INCREMENT PRIMARY KEY,
            id_produto_origem INT NOT NULL UNIQUE,
            sku VARCHAR(30) NOT NULL UNIQUE,
            nome_produto VARCHAR(120) NOT NULL,
            categoria VARCHAR(60) NOT NULL,
            marca VARCHAR(60) NOT NULL,
            preco_lista DECIMAL(10,2) NOT NULL
        ) ENGINE=InnoDB;
        """,

        """
        CREATE TABLE dim_tempo (
            sk_tempo INT AUTO_INCREMENT PRIMARY KEY,
            data DATE NOT NULL UNIQUE,
            dia INT NOT NULL,
            mes INT NOT NULL,
            nome_mes VARCHAR(20) NOT NULL,
            trimestre INT NOT NULL,
            ano INT NOT NULL
        ) ENGINE=InnoDB;
        """,

        """
        CREATE TABLE fato_vendas (
            sk_venda BIGINT AUTO_INCREMENT PRIMARY KEY,

            sk_tempo INT NOT NULL,
            sk_cliente INT NOT NULL,
            sk_produto INT NOT NULL,
            sk_vendedor INT NOT NULL,

            -- Dimensão degenerada.
            numero_pedido VARCHAR(30) NOT NULL,

            quantidade INT NOT NULL,
            valor_bruto DECIMAL(12,2) NOT NULL,
            valor_desconto DECIMAL(12,2) NOT NULL,
            valor_liquido DECIMAL(12,2) NOT NULL,

            CONSTRAINT fk_fato_tempo
                FOREIGN KEY (sk_tempo)
                REFERENCES dim_tempo(sk_tempo),

            CONSTRAINT fk_fato_cliente
                FOREIGN KEY (sk_cliente)
                REFERENCES dim_cliente(sk_cliente),

            CONSTRAINT fk_fato_produto
                FOREIGN KEY (sk_produto)
                REFERENCES dim_produto(sk_produto),

            CONSTRAINT fk_fato_vendedor
                FOREIGN KEY (sk_vendedor)
                REFERENCES dim_vendedor(sk_vendedor)
        ) ENGINE=InnoDB;
        """
    ]

    with engine.begin() as conn:

        for comando in comandos:
            conn.execute(text(comando))

    engine.dispose()

    print("[6/8] Modelo estrela criado em empresa_dw.")


# ============================================================
# 15. ETAPA 7 — CARGA SILVER → GOLD
# ============================================================

def carregar_gold():
    """
    A Gold é carregada SOMENTE a partir da Silver.

    Não pulamos diretamente do OLTP para o DW.
    """

    clientes = pd.read_csv(
        SILVER_DIR / "clientes_tratados.csv"
    )

    vendedores = pd.read_csv(
        SILVER_DIR / "vendedores_tratados.csv"
    )

    produtos = pd.read_csv(
        SILVER_DIR / "produtos_tratados.csv"
    )

    pedidos = pd.read_csv(
        SILVER_DIR / "pedidos_tratados.csv"
    )

    vendas = pd.read_csv(
        SILVER_DIR / "vendas_tratadas.csv"
    )

    engine = criar_engine_mysql(BANCO_DW)

    # --------------------------------------------------------
    # DIM_CLIENTE
    # --------------------------------------------------------

    dim_cliente = (
        clientes.rename(
            columns={
                "id_cliente": "id_cliente_origem"
            }
        )[
            [
                "id_cliente_origem",
                "nome_cliente",
                "cidade",
                "estado",
                "regiao",
                "data_cadastro"
            ]
        ]
    )

    dim_cliente.to_sql(
        "dim_cliente",
        engine,
        if_exists="append",
        index=False,
        chunksize=500,
        method="multi"
    )

    # --------------------------------------------------------
    # DIM_VENDEDOR
    # --------------------------------------------------------

    dim_vendedor = (
        vendedores.rename(
            columns={
                "id_vendedor": "id_vendedor_origem"
            }
        )[
            [
                "id_vendedor_origem",
                "nome_vendedor",
                "equipe",
                "estado",
                "regiao"
            ]
        ]
    )

    dim_vendedor.to_sql(
        "dim_vendedor",
        engine,
        if_exists="append",
        index=False,
        method="multi"
    )

    # --------------------------------------------------------
    # DIM_PRODUTO
    # --------------------------------------------------------

    produtos_ativos = produtos[
        produtos["ativo"] == 1
    ].copy()

    dim_produto = (
        produtos_ativos.rename(
            columns={
                "id_produto": "id_produto_origem"
            }
        )[
            [
                "id_produto_origem",
                "sku",
                "nome_produto",
                "categoria",
                "marca",
                "preco_lista"
            ]
        ]
    )

    dim_produto.to_sql(
        "dim_produto",
        engine,
        if_exists="append",
        index=False,
        method="multi"
    )

    # --------------------------------------------------------
    # DIM_TEMPO
    # --------------------------------------------------------

    pedidos["data_pedido"] = pd.to_datetime(
        pedidos["data_pedido"]
    )

    dim_tempo = (
        pedidos[["data_pedido"]]
        .drop_duplicates()
        .sort_values("data_pedido")
        .copy()
    )

    dim_tempo["data"] = (
        dim_tempo["data_pedido"]
        .dt.date
    )

    dim_tempo["dia"] = (
        dim_tempo["data_pedido"].dt.day
    )

    dim_tempo["mes"] = (
        dim_tempo["data_pedido"].dt.month
    )

    mapa_meses = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março",
        4: "Abril", 5: "Maio", 6: "Junho",
        7: "Julho", 8: "Agosto", 9: "Setembro",
        10: "Outubro", 11: "Novembro", 12: "Dezembro"
    }

    dim_tempo["nome_mes"] = (
        dim_tempo["mes"].map(mapa_meses)
    )

    dim_tempo["trimestre"] = (
        dim_tempo["data_pedido"].dt.quarter
    )

    dim_tempo["ano"] = (
        dim_tempo["data_pedido"].dt.year
    )

    dim_tempo = dim_tempo[
        [
            "data",
            "dia",
            "mes",
            "nome_mes",
            "trimestre",
            "ano"
        ]
    ]

    dim_tempo.to_sql(
        "dim_tempo",
        engine,
        if_exists="append",
        index=False,
        chunksize=500,
        method="multi"
    )

    # --------------------------------------------------------
    # RECUPERAÇÃO DAS SURROGATE KEYS
    # --------------------------------------------------------

    mapa_cliente = pd.read_sql(
        """
        SELECT
            sk_cliente,
            id_cliente_origem
        FROM dim_cliente;
        """,
        engine
    )

    mapa_vendedor = pd.read_sql(
        """
        SELECT
            sk_vendedor,
            id_vendedor_origem
        FROM dim_vendedor;
        """,
        engine
    )

    mapa_produto = pd.read_sql(
        """
        SELECT
            sk_produto,
            id_produto_origem
        FROM dim_produto;
        """,
        engine
    )

    mapa_tempo = pd.read_sql(
        """
        SELECT
            sk_tempo,
            data
        FROM dim_tempo;
        """,
        engine
    )

    # Normalizamos data dos dois lados para datetime64[ns].
    mapa_tempo["data"] = pd.to_datetime(
        mapa_tempo["data"]
    )

    # --------------------------------------------------------
    # FATO_VENDAS
    # --------------------------------------------------------

    # Regra:
    # somente pedidos concluídos representam venda realizada.
    fato = vendas[
        vendas["status"] == "Concluído"
    ].copy()

    fato["data"] = pd.to_datetime(
        fato["data_pedido"]
    ).dt.normalize()

    # Troca dos IDs de origem pelas surrogate keys.
    fato = fato.merge(
        mapa_cliente,
        left_on="id_cliente",
        right_on="id_cliente_origem",
        how="inner"
    )

    fato = fato.merge(
        mapa_vendedor,
        left_on="id_vendedor",
        right_on="id_vendedor_origem",
        how="inner"
    )

    fato = fato.merge(
        mapa_produto,
        left_on="id_produto",
        right_on="id_produto_origem",
        how="inner"
    )

    fato = fato.merge(
        mapa_tempo,
        on="data",
        how="inner"
    )

    fato_vendas = fato[
        [
            "sk_tempo",
            "sk_cliente",
            "sk_produto",
            "sk_vendedor",
            "numero_pedido",
            "quantidade",
            "valor_bruto",
            "valor_desconto",
            "valor_liquido"
        ]
    ].copy()

    fato_vendas.to_sql(
        "fato_vendas",
        engine,
        if_exists="append",
        index=False,
        chunksize=500,
        method="multi"
    )

    engine.dispose()

    print("[7/8] Gold carregada a partir da Silver.")


# ============================================================
# 16. ETAPA 8 — VALIDAÇÃO FINAL
# ============================================================

def validar_dw():
    """Valida as tabelas e executa uma consulta analítica."""

    engine = criar_engine_mysql(BANCO_DW)

    print("\nVALIDAÇÃO DO DATA WAREHOUSE")

    for tabela in [
        "dim_cliente",
        "dim_vendedor",
        "dim_produto",
        "dim_tempo",
        "fato_vendas"
    ]:

        with engine.connect() as conn:

            quantidade = conn.execute(
                text(
                    f"SELECT COUNT(*) FROM `{tabela}`;"
                )
            ).scalar()

        print(
            f"{tabela:<15}: {quantidade} registros"
        )

    print("\nFATURAMENTO LÍQUIDO POR CATEGORIA")

    resultado = pd.read_sql(
        """
        SELECT
            p.categoria,
            ROUND(
                SUM(f.valor_liquido),
                2
            ) AS faturamento_liquido

        FROM fato_vendas AS f

        INNER JOIN dim_produto AS p
            ON f.sk_produto = p.sk_produto

        GROUP BY p.categoria

        ORDER BY faturamento_liquido DESC;
        """,
        engine
    )

    print(
        resultado.to_string(index=False)
    )

    engine.dispose()

    print("[8/8] Data Warehouse validado.")


# ============================================================
# 17. FUNÇÃO PRINCIPAL
# ============================================================

def main():
    """
    Executa o projeto inteiro na ordem correta.

    1. conecta ao MySQL;
    2. cria empresa_oltp e empresa_dw;
    3. cria tabelas OLTP;
    4. gera dados com Faker + regras;
    5. extrai Bronze;
    6. trata Silver com Pandas;
    7. cria e carrega Gold;
    8. valida o resultado.
    """

    print("=" * 65)
    print("PROJETO — PIPELINE MYSQL + FAKER + PANDAS")
    print("=" * 65)

    preparar_pastas()

    # Primeiro verificamos se o servidor realmente está disponível.
    testar_conexao_mysql()

    # Recria os dois databases.
    criar_bancos_mysql()

    # OLTP.
    criar_oltp()
    popular_oltp()
    validar_oltp()

    # Medallion.
    criar_bronze()
    criar_silver()

    # Data Warehouse / Gold.
    criar_dw()
    carregar_gold()
    validar_dw()

    print("\n" + "=" * 65)
    print("PIPELINE CONCLUÍDO")
    print("=" * 65)

    print(
        f"""
Servidor MySQL:
    {MYSQL_HOST}:{MYSQL_PORT}

OLTP:
    {BANCO_OLTP}

Bronze:
    data/bronze/*.csv

Silver:
    data/silver/*.csv

Gold / Data Warehouse:
    {BANCO_DW}

Tecnologias:
    Faker      -> geração cadastral sintética
    MySQL      -> OLTP e Data Warehouse
    Pandas     -> extração e tratamento
    SQLAlchemy -> conexão Python ↔ MySQL
    PyMySQL    -> driver MySQL utilizado pelo SQLAlchemy
"""
    )

# ============================================================
# 18. PONTO DE ENTRADA
# ============================================================

# Quando este arquivo é executado diretamente:
#
#     python projeto_mysql_faker_pandas_comentado.py
#
# __name__ recebe "__main__" e a função main() é executada.

if __name__ == "__main__":
    main()