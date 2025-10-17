import pandas as pd
import io
import re

# Definição do layout do arquivo TXT (Layout PS.txt)
# Campo: (Tamanho, Posição Inicial, Tipo de Dado, Coluna Excel Correspondente, Preenchimento)
# Posições são 1-based.
LAYOUT_PS = [
    # Campo 001: TIPO_REGISTRO (Fixo 3) - Posição 1, Tamanho 1
    {"campo": "TIPO_REGISTRO", "tamanho": 1, "pos_inicial": 1, "tipo": "Fixo", "valor": "3"},
    
    # Campo 002: CPF_AUTONOMO (CPF do Titular) - Posição 2, Tamanho 11
    {"campo": "CPF_AUTONOMO", "tamanho": 11, "pos_inicial": 2, "tipo": "Num", "coluna_excel": "CPF DO AUTÔNOMO"},
    
    # Campo 003: CODIGO_PLANO_AUTONOMO (Plano do Titular) - Posição 13, Tamanho 4
    {"campo": "CODIGO_PLANO_AUTONOMO", "tamanho": 4, "pos_inicial": 13, "tipo": "AlfaNum", "coluna_excel": "CÓDIGO PLANO"},
    
    # Campo 004: VALOR_DESCONTO_AUTONOMO (Mensalidade Titular) - Posição 17, Tamanho 8
    {"campo": "VALOR_DESCONTO_AUTONOMO", "tamanho": 8, "pos_inicial": 17, "tipo": "Valor", "coluna_excel": "MENSALIDADE TITULAR"},
    
    # Campo 005: CPF_AUTONOMO_DEPENDENTE (CPF do Dependente) - Posição 25, Tamanho 11
    {"campo": "CPF_AUTONOMO_DEPENDENTE", "tamanho": 11, "pos_inicial": 25, "tipo": "Num", "coluna_excel": "CPF DO DEPENDENTE"},
    
    # Campo 006: CODIGO_PLANO_AUTONOMO_DEPENDENTE (Plano do Dependente) - Posição 36, Tamanho 4
    {"campo": "CODIGO_PLANO_AUTONOMO_DEPENDENTE", "tamanho": 4, "pos_inicial": 36, "tipo": "AlfaNum", "coluna_excel": "CÓDIGO PLANO DEPENDENTE"},
    
    # Campo 007: VALOR_DESCONTO_AUTONOMO_DEPENDENTE (Mensalidade Dependente) - Posição 40, Tamanho 8
    {"campo": "VALOR_DESCONTO_AUTONOMO_DEPENDENTE", "tamanho": 8, "pos_inicial": 40, "tipo": "Valor", "coluna_excel": "MENSALIDADE DEPENDENTE"},
]
TOTAL_LINE_SIZE = 200

def format_field(value, field_info):
    """Formata o valor de um campo de acordo com suas especificações."""
    tamanho = field_info["tamanho"]
    tipo = field_info["tipo"]
    valor_padrao = field_info.get("valor")
    
    if tipo == "Fixo":
        return valor_padrao.ljust(tamanho, ' ')[:tamanho]
    
    if pd.isna(value) or value is None:
        value = ""
    
    if tipo == "Num":
        # Remove caracteres não numéricos e preenche com zeros à esquerda
        clean_value = re.sub(r'\D', '', str(value)) if str(value).strip() else ''
        if not clean_value:
            return ''.zfill(tamanho)[:tamanho] # Retorna zeros se estiver vazio
        return clean_value.zfill(tamanho)[:tamanho]
    
    if tipo == "Valor":
        # Formato 9(tamanho-2)V99 (implícito), 8 posições = 6 inteiros + 2 decimais
        try:
            # Tenta converter para float, tratando vírgula como separador decimal se necessário
            if isinstance(value, str):
                value = value.replace('.', '').replace(',', '.')
            
            vlr_float = float(value)
        except:
            vlr_float = 0.0
            
        # Converte para centavos e formata com zeros à esquerda
        cents = int(round(vlr_float * 100))
        return f"{cents:0{tamanho}d}"[:tamanho]
    
    if tipo == "AlfaNum":
        # Preenche com espaços à direita
        str_value = str(value).strip() if str(value).strip() else ''
        if not str_value:
            return ''.ljust(tamanho, ' ')[:tamanho]
        return str_value.ljust(tamanho, ' ')[:tamanho]
    
    # Padrão: Alfanumérico com preenchimento à direita
    str_value = str(value).strip()
    return str_value.ljust(tamanho, ' ')[:tamanho]

def convert_excel_to_ps_txt(excel_file):
    """
    Converte um arquivo Excel de Planos de Saúde para o formato TXT (Layout PS.txt).
    """
    try:
        # Lê a planilha, assumindo que os cabeçalhos estão na segunda linha (índice 1)
        df = pd.read_excel(excel_file, header=1, dtype=str)
    except Exception as e:
        raise ValueError(f"Erro ao ler o Excel: {e}")

    # Renomeia colunas para remover espaços extras no final, se houver
    df.columns = [col.strip() for col in df.columns]
    
    # Trata colunas duplicadas para garantir o mapeamento correto
    # A coluna 'CÓDIGO PLANO' para o dependente é a segunda com o mesmo nome.
    # O pandas renomeia a segunda coluna para 'CÓDIGO PLANO.1' (ou similar)
    
    # Verifica se a coluna duplicada existe e renomeia para o nome esperado no LAYOUT_PS
    if 'CÓDIGO PLANO.1' in df.columns:
        df.rename(columns={'CÓDIGO PLANO.1': 'CÓDIGO PLANO DEPENDENTE'}, inplace=True)
    elif 'CÓDIGO PLANO 1' in df.columns:
        df.rename(columns={'CÓDIGO PLANO 1': 'CÓDIGO PLANO DEPENDENTE'}, inplace=True)
            
    # Limpeza de dados (removendo linhas totalmente vazias)
    df.dropna(how='all', inplace=True)
    
    if df.empty:
        raise ValueError("A planilha não contém dados válidos.")

    lines = []
    
    # Itera sobre as linhas do DataFrame
    for _, row in df.iterrows():
        line = ""
        current_pos = 1 # Posição inicial 1-based
        
        # Constrói a linha com base no LAYOUT_PS
        for field_info in LAYOUT_PS:
            # Verifica se a posição inicial no layout corresponde à posição atual
            if field_info["pos_inicial"] != current_pos:
                # Se houver um gap, preenche com espaços
                gap_size = field_info["pos_inicial"] - current_pos
                line += " " * gap_size
                current_pos += gap_size

            # Obtém o valor da coluna Excel, se aplicável
            excel_col = field_info.get("coluna_excel")
            value = row.get(excel_col) if excel_col else None
            
            # Formata o campo
            formatted_value = format_field(value, field_info)
            
            # Adiciona à linha
            line += formatted_value
            current_pos += len(formatted_value)

        # Preenche o restante da linha até o tamanho total com espaços
        if len(line) < TOTAL_LINE_SIZE:
            line += " " * (TOTAL_LINE_SIZE - len(line))
        
        # Garante que a linha tenha exatamente o tamanho total
        line = line[:TOTAL_LINE_SIZE]
        
        lines.append(line)

    txt_content = "\n".join(lines)
    
    # Retorna o conteúdo TXT em um objeto BytesIO
    return io.BytesIO(txt_content.encode('utf-8'))
