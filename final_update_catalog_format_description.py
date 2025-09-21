import xml.etree.ElementTree as ET
import pandas as pd
from bs4 import BeautifulSoup

def parse_tech_properties(tech_text):
    """Парсит технические характеристики из HTML таблицы"""
    if not tech_text:
        return {}
    
    soup = BeautifulSoup(tech_text, 'html.parser')
    table = soup.find('table')
    if not table:
        return {}
    
    properties = {}
    rows = table.find_all('tr')
    
    for row in rows:
        cells = row.find_all(['td', 'th'])
        if len(cells) >= 2:
            name = cells[0].get_text(strip=True)
            value = cells[1].get_text(strip=True)
            if name and value:
                properties[name] = value
    
    return properties

def parse_equipment_to_list(equipment_text):
    """Парсит комплектацию из таблицы"""
    if not equipment_text:
        return []
    
    soup = BeautifulSoup(equipment_text, 'html.parser')
    table = soup.find('table')
    if not table:
        return []
    
    equipment_items = []
    rows = table.find_all('tr')
    
    for row in rows:
        cells = row.find_all(['td', 'th'])
        if len(cells) >= 2:
            name = cells[0].get_text(strip=True)
            value = cells[1].get_text(strip=True)
            if name and value and name != 'Наименование':
                equipment_items.append(f"{name}: {value}")
    
    return equipment_items

def format_description(description_text, equipment_text):
    """Форматирует описание без tech"""
    result = ""
    char_count = 0
    
    # Добавляем основное описание
    if description_text:
        clean_desc = description_text.replace('<![CDATA[', '').replace(']]>', '')
        paragraphs = clean_desc.split('</p>')
        for p in paragraphs:
            if p.strip():
                p_clean = p.replace('<p>', '').replace('<br />', '<br />').strip()
                if p_clean:
                    start_pos = char_count
                    char_count += len(p_clean) + 20
                    result += f'<p data-end="{char_count}" data-start="{start_pos}">{p_clean}</p>\n\n'
    
    # Добавляем комплектацию
    if equipment_text:
        equipment_items = parse_equipment_to_list(equipment_text)
        if equipment_items:
            start_pos = char_count
            char_count += 15
            result += f'<p data-end="{char_count}" data-start="{start_pos}" style="font-weight: bold; font-size: 18px;">Комплектация:</p>\n\n'
            
            ul_start = char_count
            result += f'<ul data-end="PLACEHOLDER_UL_END" data-start="{ul_start}">\n'
            
            for item in equipment_items:
                li_start = char_count
                char_count += len(item) + 5
                li_end = char_count
                
                p_start = char_count - len(item) - 2
                p_end = char_count - 2
                
                result += f'<li data-end="{li_end}" data-start="{li_start}">\n'
                result += f'<div data-end="{p_end}" data-start="{p_start}" style="line-height:2;">{item}</div>\n'
                result += '</li>\n'
            
            char_count += 10
            result = result.replace('PLACEHOLDER_UL_END', str(char_count))
            result += '</ul>\n'
    
    return result

# Основной код
tree = ET.parse('feed-yml-0.xml')
root = tree.getroot()
catalog_df = pd.read_csv('catalog6_new.csv', sep=';')

# Собираем все возможные свойства из XML
all_properties = set()
offers = root.findall('.//offer')

for offer in offers:
    tech = offer.find('tech')
    if tech is not None and tech.text:
        tech_clean = tech.text.replace('<![CDATA[', '').replace(']]>', '')
        properties = parse_tech_properties(tech_clean)
        all_properties.update(properties.keys())

# Добавляем недостающие столбцы свойств
existing_columns = list(catalog_df.columns)
for prop in all_properties:
    column_name = f"Свойство: {prop}:"
    if column_name not in existing_columns:
        catalog_df[column_name] = ""

# Обрабатываем XML данные
xml_data = {}
for offer in offers:
    vendor_code = offer.find('vendorCode')
    if vendor_code is not None:
        description = offer.find('description')
        tech = offer.find('tech')
        equipment = offer.find('equipment')
        pictures = offer.findall('picture')
        
        # Собираем фото
        all_photos = [pic.text for pic in pictures if pic.text]
        photos_string = ";".join(all_photos)
        
        # Парсим технические характеристики
        tech_properties = {}
        if tech is not None and tech.text:
            tech_clean = tech.text.replace('<![CDATA[', '').replace(']]>', '')
            tech_properties = parse_tech_properties(tech_clean)
        
        # Форматируем описание
        desc_text = description.text if description is not None and description.text else ""
        equip_text = equipment.text if equipment is not None and equipment.text else ""
        formatted_description = format_description(desc_text, equip_text)
        
        xml_data[vendor_code.text] = {
            'photos': photos_string,
            'description': formatted_description,
            'properties': tech_properties
        }

# Обновляем каталог
for index, row in catalog_df.iterrows():
    artikul = str(row['Артикул'])
    if artikul in xml_data:
        # Обновляем фото
        if pd.isna(row['Фото товара']) or row['Фото товара'] == '':
            catalog_df.at[index, 'Фото товара'] = xml_data[artikul]['photos']
        
        # Обновляем описание
        if pd.isna(row['Описание']) or row['Описание'] == '':
            catalog_df.at[index, 'Описание'] = xml_data[artikul]['description']
        
        # Обновляем свойства
        for prop_name, prop_value in xml_data[artikul]['properties'].items():
            column_name = f"Свойство: {prop_name}:"
            if column_name in catalog_df.columns:
                catalog_df.at[index, column_name] = prop_value

catalog_df.to_csv('catalog6_formatted.csv', sep=';', index=False, encoding='utf-8-sig')
print("Каталог с форматированными описаниями и свойствами сохранен как catalog6_formatted.csv")