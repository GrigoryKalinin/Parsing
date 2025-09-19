import pandas as pd

# Читаем лист "Деревообработка"
df = pd.read_excel('PROMA_VISPROM_Прайс_лист_с_15_09_2025_курс_86.xlsx', sheet_name='Деревообработка')

# Сохраняем в CSV с правильной кодировкой
df.to_csv('price_new.csv', encoding='utf-8-sig', index=False)

print("Excel файл конвертирован в price_new.csv")