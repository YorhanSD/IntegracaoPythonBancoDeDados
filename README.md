<h1> Integração entre o BancoDeDados e o Python </h1>

<br>

<h2> CAMADA BRONZE </h2>
<h3> Bibliotecas utilizadas na camada bronze: Faker.</h3>

<br>

<div>
  <h3> Adiciona dados no Banco de Dados existente por meio de código. </h3>
  <h3> No meu caso, o banco utilizado se chama : retropixel_bronze. </h3>
  <h3> Cada tabela é preenchida com erros de digitação e espaços em branco propositalmente. </h3>
  <h3> As tabelas possuem um grande volume de dados, simulando assim uma situação comum em diversos tipos de bancos. </h3>
</div>

<br>

<div>
  <h3> Ao executar o programa no terminal do vscode temos : </h3>
</div>

<img width="556" height="672" alt="Banco Bronze Terminal Print" src="https://github.com/user-attachments/assets/0c0d31c8-5ea4-4e37-be79-fb9d51d2406e" />

<br>
<br>

<div>
  <h3> Com as tabelas preenchidas, podemos realizar consultas e checar o resultado. </h3>
  <h3> Após isso podemos fazer o tratamento desses dados. </h3>
  <h3> Com isso, teremos a próxima etapa que será a camada SILVER. </h3>
</div>

<br>

<div>
  <h3> No Banco de Dados, Ao executar o comando SELECT em Clientes temos : </h3>
</div>

<img width="820" height="882" alt="Banco de Dados MySQL Print Clientes" src="https://github.com/user-attachments/assets/f5ac2d54-4f1e-461f-8a39-fb46c42b8ea8" />

<br>

<h2> CAMADA SILVER </h2>

<br>

<h3> A camada Silver é responsável por extrair os dados armazenados no banco Bronze, aplicar regras de limpeza, padronização e validação, e disponibilizar os dados tratados em um banco MySQL independente.</h3>
<h3> Bibliotecas utilizadas na camada silver: Pandas, SQLAlchemy e MySQL Connector.</h3>

<br>

<h3> Etapas de Processamento </h3>

1. Criação e verificação do banco de dados `retropixel_silver`.
2. Extração das tabelas `plataformas`, `produtos`, `clientes`, `pedidos` e `itens_pedido` da camada Bronze.
3. Aplicação de regras específicas de tratamento para cada conjunto de dados.
4. Carregamento dos DataFrames tratados nas respectivas tabelas do banco Silver.
5. Exibição de uma comparação entre os registros de clientes das camadas Bronze e Silver.

<h3> Correções </h3>

- Padronização de textos e remoção de espaços excedentes.
- Conversão de valores numéricos e datas.
- Normalização de CPF, passaportes e endereços de e-mail.
- Tratamento de valores nulos e registros inválidos.
- Remoção de registros que não atendem a determinados critérios de validação.


