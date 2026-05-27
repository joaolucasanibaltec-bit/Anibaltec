import csv
import os

arquivo_ibge = r'C:\Users\joaol\OneDrive\Desktop\Conversão de dados\ibge_municipios.csv'

with open(arquivo_ibge, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)
    
    for row in reader:
        if row[1] == '24' and 'Moss' in row[3]:
            print(f"Found: Name='{row[3]}', UF={row[1]}, Codigo={row[0]}")
            break
    else:
        print("Not found with row[1] == '24'")
        
        f.seek(0)
        reader = csv.reader(f)
        for row in reader:
            if 'Moss' in row[3]:
                print(f"Found anywhere: Name='{row[3]}', UF={row[1]}, Codigo={row[0]}")
                break