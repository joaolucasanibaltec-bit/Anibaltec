import csv

f = open(r'C:\Users\joaol\OneDrive\Desktop\Conversão de dados\ibge_municipios.csv', 'r', encoding='utf-8')
reader = csv.DictReader(f)

for row in reader:
    if row['uf'] == 'RN' and 'MOSSORO' in row['name'].upper():
        print(row['name'] + ': ' + row['municipio'])

f.close()