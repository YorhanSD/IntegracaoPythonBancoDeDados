# ctrl + shift + p
# select interpreter
# .venv versão python 3.14.3
# .venv\Scripts\activate.bat
# pip install mysql-connector-python faker

import random
from datetime import datetime, timedelta

import mysql.connector
from faker import Faker

# ============================================================
# CONFIGURAÇÃO DO BANCO
# ============================================================

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Sua Senha",
    "database": "retropixel_bronze",
    "port": 3306,
}


# ============================================================
# FAKERS
# ============================================================

faker_br = Faker("pt_BR")

fakers_ext = [
    Faker("en_US"),
    Faker("es_ES"),
    Faker("de_DE"),
    Faker("ja_JP"),
]


# ============================================================
# FUNÇÃO PRINCIPAL
# ============================================================

def popular_camada_bronze():

    conn = None
    cursor = None

    try:

        # ========================================================
        # CONEXÃO
        # ========================================================

        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        print("=" * 60)
        print("INICIANDO CARGA DA CAMADA BRONZE")
        print("=" * 60)

        # ========================================================
        # PLATAFORMAS
        # ========================================================

        print("\nInserindo plataformas...")

        plataformas_base = [
            ("Playstation 5", "Sony"),
            ("Playstation 4", "Sony"),
            ("Playstation 3", "Sony"),
            ("Playstation 2", "Sony"),
            ("Playstation 1", "Sony"),
            ("Nintendo Switch", "Nintendo"),
            ("Super Nintendo (SNES)", "Nintendo"),
            ("Nintendo 64", "Nintendo"),
            ("Game Boy Color", "Nintendo"),
            ("Xbox Series X", "Microsoft"),
            ("Mega Drive", "Sega"),
            ("Sega Dreamcast", "Sega"),
            ("PC Gamer", None),
            ("Arcade Retro", None),
        ]

        plataformas_inserir = []

        for nome, fabricante in plataformas_base:

            # Mantém alguns dados inconsistentes
            # para simular a camada Bronze

            nome_mod = random.choice([
                nome.upper(),
                nome.lower(),
                nome,
                None,
            ])

            if fabricante:

                fabricante_mod = random.choice([
                    fabricante.upper(),
                    fabricante.lower(),
                    fabricante,
                    None,
                ])

            else:

                fabricante_mod = None

            plataformas_inserir.append(
                (
                    nome_mod,
                    fabricante_mod,
                )
            )

        cursor.executemany(
            """
            INSERT INTO plataformas
            (
                nome,
                fabricante
            )
            VALUES
            (%s, %s)
            """,
            plataformas_inserir,
        )

        conn.commit()

        print(
            f"{len(plataformas_inserir)} "
            f"plataformas carregadas."
        )

        # ========================================================
        # FRANQUIAS
        # ========================================================

        franquias = [
            "Mario",
            "Zelda",
            "Sonic",
            "Final Fantasy",
            "Resident Evil",
            "God of War",
            "Halo",
            "Pokemon",
            "Metroid",
            "Street Fighter",
            "Doom",
            "GTA",
            "Castlevania",
            "Mega Man",
            "Crash Bandicoot",
            "Silent Hill",
            "Tekken",
            "Mortal Kombat",
            "Chrono Trigger",
            "Dark Souls",
        ]

        sufixos = [
            "Remastered",
            "Deluxe Edition",
            "Classic",
            "Chronicles",
            "Trilogy",
            "2",
            "3",
            "4",
            "X",
            "Origins",
            "Adventures",
            "Kart",
            "Tactics",
            "Portable",
            "Collection",
        ]

        # ========================================================
        # BUSCAR IDS DAS PLATAFORMAS
        # ========================================================

        cursor.execute(
            """
            SELECT id_plataforma
            FROM plataformas
            WHERE id_plataforma IS NOT NULL
            """
        )

        ids_plataforma = [
            row[0]
            for row in cursor.fetchall()
        ]

        if not ids_plataforma:

            raise Exception(
                "Nenhuma plataforma encontrada."
            )

        # ========================================================
        # PRODUTOS
        # ========================================================

        print("\nInserindo produtos...")

        produtos_inserir = []

        for i in range(1, 401):

            # ----------------------------------------------------
            # CONSOLES
            # ----------------------------------------------------

            if i <= 20:

                nome_p = (
                    f"Console "
                    f"{random.choice([
                        "Slim",
                        "Pro",
                        "Collector Edition"
                    ])} "
                    f"Mod-{i}"
                )

                preco = round(
                    random.uniform(
                        1200.00,
                        4500.00
                    ),
                    2
                )

                estoque = random.randint(
                    5,
                    30
                )

            # ----------------------------------------------------
            # CONTROLES
            # ----------------------------------------------------

            elif i <= 60:

                nome_p = (
                    f"Controle "
                    f"{random.choice([
                        "Wireless",
                        "Arcade Stick",
                        "Pro Controller"
                    ])} "
                    f"V-{i}"
                )

                preco = round(
                    random.uniform(
                        150.00,
                        450.00
                    ),
                    2
                )

                estoque = random.randint(
                    15,
                    60
                )

            # ----------------------------------------------------
            # JOGOS
            # ----------------------------------------------------

            else:

                nome_p = (
                    f"{random.choice(franquias)} "
                    f"{random.choice(sufixos)} "
                    f"Vol. {i}"
                )

                preco = round(
                    random.uniform(
                        29.90,
                        349.90
                    ),
                    2
                )

                estoque = random.randint(
                    0,
                    120
                )

            plataforma_id = random.choice(
                ids_plataforma
            )

            produtos_inserir.append(
                (
                    nome_p,
                    preco,
                    estoque,
                    plataforma_id,
                )
            )

        cursor.executemany(
            """
            INSERT INTO produtos
            (
                nome_produto,
                preco,
                estoque,
                fkPlataforma
            )
            VALUES
            (%s, %s, %s, %s)
            """,
            produtos_inserir,
        )

        conn.commit()

        print(
            f"{len(produtos_inserir)} "
            f"produtos carregados."
        )

        # ========================================================
        # CLIENTES
        # ========================================================

        print("\nInserindo clientes...")

        clientes_inserir = []

        for _ in range(2000):

            # Aproximadamente 8% estrangeiros
            eh_estrangeiro = random.random() < 0.08

            if eh_estrangeiro:

                fkr = random.choice(
                    fakers_ext
                )

                nome_cli = fkr.name()

                cpf_cli = (
                    f"PASS-{fkr.country_code()}-"
                    f"{random.randint(100000, 999999)}"
                )

            else:

                nome_cli = faker_br.name()

                padrao_cpf = random.random()

                # CPF com pontuação
                if padrao_cpf < 0.45:

                    cpf_cli = faker_br.cpf()

                # CPF somente com números
                elif padrao_cpf < 0.93:

                    cpf_cli = (
                        faker_br.cpf()
                        .replace(".", "")
                        .replace("-", "")
                    )

                # CPF ausente
                else:

                    cpf_cli = None

            # ====================================================
            # E-MAIL
            # ====================================================

            if random.random() < 0.08:

                email_cli = None

            else:

                nome_email = (
                    nome_cli
                    .lower()
                    .replace(" ", ".")
                )

                email_base = (
                    f"{nome_email}"
                    f"{random.randint(1, 99)}"
                    "@email.com"
                )

                email_cli = random.choice([
                    email_base,
                    email_base.upper(),
                ])

            # ====================================================
            # DATA DE CADASTRO
            # ====================================================

            dt_cad = faker_br.date_time_between(
                start_date=datetime(
                    2024,
                    1,
                    1
                ),
                end_date=datetime(
                    2026,
                    6,
                    30
                ),
            )

            nome_final = random.choice([
                nome_cli.upper(),
                nome_cli.lower(),
                nome_cli,
            ])

            clientes_inserir.append(
                (
                    nome_final,
                    cpf_cli,
                    email_cli,
                    dt_cad,
                )
            )

        cursor.executemany(
            """
            INSERT INTO clientes
            (
                nome,
                cpf,
                email,
                data_cadastro
            )
            VALUES
            (%s, %s, %s, %s)
            """,
            clientes_inserir,
        )

        conn.commit()

        print(
            f"{len(clientes_inserir)} "
            f"clientes carregados."
        )

        # ========================================================
        # BUSCAR CLIENTES
        # ========================================================

        cursor.execute(
            """
            SELECT id_cliente
            FROM clientes
            """
        )

        ids_clientes = [
            row[0]
            for row in cursor.fetchall()
        ]

        if not ids_clientes:

            raise Exception(
                "Nenhum cliente encontrado."
            )

        # ========================================================
        # BUSCAR PRODUTOS
        # ========================================================

        cursor.execute(
            """
            SELECT
                id_produto,
                preco,
                fkPlataforma
            FROM produtos
            """
        )

        produtos_info = cursor.fetchall()

        if not produtos_info:

            raise Exception(
                "Nenhum produto encontrado."
            )

        # ========================================================
        # PERÍODO DAS VENDAS
        # ========================================================

        dt_inicio = datetime(
            2026,
            1,
            1
        )

        dt_fim = datetime(
            2026,
            6,
            30
        )

        total_dias = (
            dt_fim - dt_inicio
        ).days + 1

        # ========================================================
        # PEDIDOS
        # ========================================================

        print("\nGerando pedidos...")

        pedidos_inserir = []

        # Também vamos gerar os itens separadamente
        itens_inserir = []

        for dia_idx in range(total_dias):

            dt_atual = (
                dt_inicio
                + timedelta(
                    days=dia_idx
                )
            )

            # ----------------------------------------------------
            # QUANTIDADE DE VENDAS POR DIA
            # ----------------------------------------------------

            if dt_atual.weekday() >= 5:

                qtd_vendas_dia = random.randint(
                    100,
                    135
                )

            else:

                qtd_vendas_dia = random.randint(
                    65,
                    105
                )

            # ----------------------------------------------------
            # PEDIDOS DO DIA
            # ----------------------------------------------------

            for _ in range(qtd_vendas_dia):

                hora = random.randint(
                    9,
                    22
                )

                minuto = random.randint(
                    0,
                    59
                )

                segundo = random.randint(
                    0,
                    59
                )

                dt_pedido = dt_atual.replace(
                    hour=hora,
                    minute=minuto,
                    second=segundo,
                )

                cliente_id = random.choice(
                    ids_clientes
                )

                # Entre 1 e 4 produtos
                quantidade_produtos = random.randint(
                    1,
                    min(
                        4,
                        len(produtos_info)
                    )
                )

                produtos_pedido = random.sample(
                    produtos_info,
                    k=quantidade_produtos
                )

                total_pedido = 0.0

                itens_pedido_atual = []

                # =================================================
                # ITENS DO PEDIDO
                # =================================================

                for (
                    produto_id,
                    preco_catalogo,
                    plataforma_id
                ) in produtos_pedido:

                    quantidade = random.randint(
                        1,
                        3
                    )

                    desconto = random.choice([
                        0.0,
                        0.05,
                        0.10,
                    ])

                    preco_unitario = round(
                        float(preco_catalogo)
                        * (1.0 - desconto),
                        2
                    )

                    subtotal = round(
                        quantidade
                        * preco_unitario,
                        2
                    )

                    total_pedido += subtotal

                    itens_pedido_atual.append(
                        (
                            plataforma_id,
                            produto_id,
                            quantidade,
                            preco_unitario,
                        )
                    )

                total_pedido = round(
                    total_pedido,
                    2
                )

                # =================================================
                # ADICIONAR PEDIDO
                # =================================================

                pedidos_inserir.append(
                    (
                        cliente_id,
                        dt_pedido,
                        total_pedido,
                    )
                )

                # =================================================
                # ADICIONAR ITENS
                # =================================================

                itens_inserir.extend(
                    itens_pedido_atual
                )

        # ========================================================
        # INSERIR PEDIDOS
        # ========================================================

        print(
            f"\nInserindo "
            f"{len(pedidos_inserir)} pedidos..."
        )

        cursor.executemany(
            """
            INSERT INTO pedidos
            (
                fkCliente,
                data_pedido,
                valor_total
            )
            VALUES
            (%s, %s, %s)
            """,
            pedidos_inserir,
        )

        conn.commit()

        print(
            f"{len(pedidos_inserir)} "
            f"pedidos carregados."
        )

        # ========================================================
        # INSERIR ITENS DOS PEDIDOS
        # ========================================================

        print(
            f"\nInserindo "
            f"{len(itens_inserir)} itens..."
        )

        cursor.executemany(
            """
            INSERT INTO itens_pedido
            (
                fkPlataforma,
                fkProduto,
                quantidade,
                preco_unitario
            )
            VALUES
            (%s, %s, %s, %s)
            """,
            itens_inserir,
        )

        conn.commit()

        print(
            f"{len(itens_inserir)} "
            f"itens carregados."
        )

        # ========================================================
        # FINALIZAÇÃO
        # ========================================================

        print("\n" + "=" * 60)
        print("CARGA FINALIZADA COM SUCESSO!")
        print("=" * 60)

        print(
            f"Plataformas: "
            f"{len(plataformas_inserir)}"
        )

        print(
            f"Produtos: "
            f"{len(produtos_inserir)}"
        )

        print(
            f"Clientes: "
            f"{len(clientes_inserir)}"
        )

        print(
            f"Pedidos: "
            f"{len(pedidos_inserir)}"
        )

        print(
            f"Itens: "
            f"{len(itens_inserir)}"
        )

        print("=" * 60)

    except Exception as erro:

        if conn:
            conn.rollback()

        print(
            f"\nERRO durante a carga: {erro}"
        )

    finally:

        if cursor:

            try:
                cursor.execute(
                    "SET FOREIGN_KEY_CHECKS = 1"
                )
            except Exception:
                pass

            cursor.close()

        if conn:
            conn.close()

        print(
            "\nConexão com o MySQL encerrada!"
        )


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":
    popular_camada_bronze()

