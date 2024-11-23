from django.test import TestCase

import openpyxl

# Caminho do arquivo Excel
arquivo_excel = 'C:/Users/junio/Downloads/Pasta1.xlsx'  # Substitua pelo caminho do seu arquivo

# Carregar o arquivo Excel
wb = openpyxl.load_workbook(arquivo_excel)

# Selecionar a primeira planilha (active é a planilha atual, geralmente a primeira)
sheet = wb.active

# Iterar sobre as linhas e colunas da planilha
for row in sheet.iter_rows(values_only=True):  # values_only=True retorna apenas os valores das células
    print(row)  # Imprime a linha no terminal
