# Conversor de Planos de Saúde (Layout PS.txt) - Web App Flask

Este projeto é uma aplicação web autônoma e minimalista, desenvolvida em Flask, Python, para automatizar a conversão de planilhas Excel de Planos de Saúde para o formato TXT com posições fixas (`Layout PS.txt`). Este formato é exigido por sistemas contábeis para a importação de dados.

## Funcionalidade Principal

A aplicação foca em uma única tarefa: converter uma planilha Excel no modelo padrão para um arquivo TXT de 200 posições por linha, conforme a especificação do `Layout PS.txt`.

## Estrutura da Planilha de Entrada

A planilha deve seguir o modelo fornecido, contendo as seguintes colunas na **segunda linha** (a primeira linha é ignorada):

| Coluna | Descrição | Exemplo |
| :--- | :--- | :--- |
| `CÓDIGO PLANO ` | Código do plano de saúde (para titular e dependente) | `1234` |
| `CPF DO AUTÔNOMO` | CPF do titular do plano (somente números) | `12345678901` |
| `MENSALIDADE TITULAR` | Valor da mensalidade do titular (Ex: `150.50`) | `150.50` |
| `CPF DO DEPENDENTE ` | CPF do dependente (somente números). Deixar vazio se não houver. | `11122233344` |
| `MENSALIDADE DEPENDENTE` | Valor da mensalidade do dependente (Ex: `120.00`) | `120.00` |

**Nota:** As colunas `COPARTICIPAÇÃO TITULAR` e `COPARTICIPAÇÃO DEPENDENTE` podem existir na planilha, mas são ignoradas no processo de conversão para o TXT, pois o layout fornecido não as inclui.

## Estrutura do Arquivo de Saída (`Layout PS.txt`)

O arquivo de saída é um TXT com **200 posições fixas** por linha. A conversão utiliza os 47 primeiros caracteres para os dados essenciais, preenchendo o restante com espaços.

| Campo | Posição Inicial | Tamanho | Conteúdo | Tipo | Preenchimento |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1. Tipo Registro | 1 | 1 | Valor Fixo `3` | Fixo | Espaços à direita |
| 2. CPF Autônomo | 2 | 11 | CPF do titular (somente números) | Numérico | Zeros à esquerda |
| 3. Cód. Plano Autônomo | 13 | 4 | Código do plano do titular | Alfanumérico | Espaços à direita |
| 4. Valor Autônomo | 17 | 8 | Mensalidade do titular (centavos, sem vírgula/ponto) | Valor (9(6)V99) | Zeros à esquerda |
| 5. CPF Dependente | 25 | 11 | CPF do dependente (somente números) | Numérico | Zeros à esquerda |
| 6. Cód. Plano Dependente | 36 | 4 | Código do plano do dependente | Alfanumérico | Espaços à direita |
| 7. Valor Dependente | 40 | 8 | Mensalidade do dependente (centavos, sem vírgula/ponto) | Valor (9(6)V99) | Zeros à esquerda |
| **Restante** | 48 | 153 | Espaços em branco | Alfanumérico | Espaços à direita |

## Instalação e Uso (Local)

### Pré-requisitos

*   Python 3.8+
*   `pip` (gerenciador de pacotes do Python)

### Passos

1.  **Clone o repositório** (após o upload para o GitHub):
    ```bash
    git clone [SEU_REPOSITORIO_GITHUB]
    cd [SEU_REPOSITORIO_GITHUB]
    ```

2.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Execute a aplicação:**
    ```bash
    python app.py
    ```

4.  **Acesse a aplicação:**
    Abra seu navegador e acesse `http://127.0.0.1:5000`.

## Deploy no Railway

O projeto utiliza Flask e `gunicorn`, o que o torna ideal para o *deploy* em plataformas como o Railway.

1.  Crie um novo projeto no Railway.
2.  Conecte-o ao seu repositório GitHub.
3.  O Railway detectará o `requirements.txt` e instalará as dependências.
4.  O comando de inicialização (Start Command) deve ser configurado como:
    ```bash
    gunicorn -w 4 app:app
    ```
    (Onde `-w 4` define 4 *workers* para melhor desempenho).

## Estrutura do Projeto

```
.
├── app.py                  # Aplicação principal Flask com a lógica de conversão embutida
├── MODELODEPLANILHA-PLANODESAUDEAUTONOMOS.XLSX # Modelo de planilha para download
├── requirements.txt        # Dependências do projeto
├── README.md               # Este arquivo
├── templates/
│   ├── base.html           # Template base para a estrutura da página
│   └── ps_txt.html         # Interface principal para a conversão
└── static/
    ├── css/
    │   └── style.css       # Estilos CSS modernos
    └── js/
        └── main.js         # Arquivo JavaScript (mínimo, com a lógica principal no template)
```
