#remover as linhas que nao contem target ou source do arquivo csv  que esta no seguinte modelo. o arquivo csv encontra-se na mesma pasta do programa atual:

import csv

csv_filename = ["tweets_rouanet_graph_reduzido"]
input_file = f"{csv_filename[0]}.csv"  # Substitua pelo nome do seu arquivo
output_file = f"{csv_filename[0]}_filtrado.csv"

# Nome do arquivo de entrada e saída
input_file = 'tweets_rouanet_graph_reduzido.csv'  # Substitua pelo nome do seu arquivo

# Abre o arquivo de entrada para leitura e o arquivo de saída para escrita
with open(input_file, mode='r', encoding='utf-8') as infile, \
     open(output_file, mode='w', newline='', encoding='utf-8') as outfile:
    
    reader = csv.DictReader(infile)
    writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
    
    # Escreve o cabeçalho no arquivo de saída
    writer.writeheader()
    
    # Processa cada linha do arquivo de entrada
    for row in reader:
        # Verifica se a coluna 'target' não está vazia
        if row['target'].strip():  # strip() remove espaços em branco
            writer.writerow(row)

print(f"Arquivo filtrado salvo como {output_file}")