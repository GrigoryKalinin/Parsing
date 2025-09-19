import pandas as pd

# Читаем price_new.csv
price_df = pd.read_csv('price_new.csv')

# Читаем catalog6.csv
catalog_df = pd.read_csv('catalog6.csv', sep=';')

# Создаем новые записи для catalog6
new_records = []
current_category = ''

for _, row in price_df.iterrows():
    artikul = str(row['Unnamed: 0']).strip()
    name = str(row['Unnamed: 1']).strip()
    price = str(row['Unnamed: 2']).strip()
    
    # Проверяем, является ли строка названием категории
    if pd.isna(row['Unnamed: 0']) or artikul == '' or artikul == 'nan':
        if name and name != 'nan' and 'станки' in name.lower() or 'пилы' in name.lower() or any(x in name for x in ['Фрезерные', 'Строгальные', 'Рейсмусовые', 'Комбинированные', 'Шлифовальные', 'Подложка', 'Пылесосы', 'Подставки']):
            current_category = name
        continue
    
    # Проверяем, что артикул не пустой и цена числовая
    if artikul and artikul != 'nan' and price and price != '0' and current_category:
        category_path = f'Каталог >> Деревообрабатывающее оборудование >> {current_category}'
        
        product_name = f'Proma {name}'
        
        new_record = {
            'Артикул': artikul,
            'Артикул модификации': artikul,
            'Наименование': product_name,
            'Цена': f'{price},00',
            'Категория: 1': category_path,
            'Валюта': 'RUB',
            'Производитель': 'PROMA',
            'SEO H1': product_name,
            'Количество': 10,
            'Количество на складе: Основной': 10,
            'Включен': '+'
        }
        new_records.append(new_record)

# Добавляем новые записи к существующему каталогу
if new_records:
    new_df = pd.DataFrame(new_records)
    updated_catalog = pd.concat([catalog_df, new_df], ignore_index=True)
    
    # Сохраняем обновленный каталог
    updated_catalog.to_csv('catalog6_new.csv', sep=';', index=False, encoding='utf-8-sig')
    print(f"Добавлено {len(new_records)} новых товаров в catalog6_new.csv")
else:
    print("Нет данных для добавления")