import xml.etree.ElementTree as ET
import pandas as pd
import re
from bs4 import BeautifulSoup

def parse_table_to_list(table_html):
    """Парсит HTML таблицу и возвращает список характеристик"""
    soup = BeautifulSoup(table_html, 'html.parser')
    table = soup.find('table')
    if not table:
        return []
    
    rows = table.find_all('tr')
    characteristics = []
    
    for row in rows:
        cells = row.find_all(['td', 'th'])
        if len(cells) >= 2:
            name = cells[0].get_text(strip=True)
            value = cells[1].get_text(strip=True)
            if name and value and name != 'Характеристика' and value != 'Значение':
                characteristics.append(f"{name}: {value}")
    
    return characteristics

def format_description(description_text, tech_text, equipment_text):
    """Форматирует описание в нужном HTML формате"""
    result = ""
    char_count = 0
    
    # Добавляем основное описание
    if description_text:
        clean_desc = description_text.replace('<![CDATA[', '').replace(']]>', '')
        # Разбиваем на абзацы
        paragraphs = clean_desc.split('</p>')
        for i, p in enumerate(paragraphs):
            if p.strip():
                p_clean = p.replace('<p>', '').replace('<br />', '<br />').strip()
                if p_clean:
                    start_pos = char_count
                    char_count += len(p_clean) + 20
                    result += f'<p data-end="{char_count}" data-start="{start_pos}">{p_clean}</p>\n\n'
    
    # Добавляем технические характеристики
    if tech_text:
        # Заголовок характеристик
        start_pos = char_count
        char_count += 29
        result += f'<p data-end="{char_count}" data-start="{start_pos}" style="font-weight: bold; font-size: 18px;">Технические характеристики:</p>\n\n'
        
        # Парсим характеристики
        tech_clean = tech_text.replace('<![CDATA[', '').replace(']]>', '')
        characteristics = parse_table_to_list(tech_clean)
        
        if characteristics:
            ul_start = char_count
            result += f'<ul data-end="PLACEHOLDER_UL_END" data-start="{ul_start}">\n'
            
            for char in characteristics:
                li_start = char_count
                char_count += len(char) + 5
                li_end = char_count
                
                p_start = char_count - len(char) - 2
                p_end = char_count - 2
                
                result += f'<li data-end="{li_end}" data-start="{li_start}">\n'
                result += f'<div data-end="{p_end}" data-start="{p_start}" style="line-height:2;">{char}</div>\n'
                result += '</li>\n'
            
            char_count += 10
            result = result.replace('PLACEHOLDER_UL_END', str(char_count))
            result += '</ul>\n\n'
    
    # Добавляем комплектацию
    if equipment_text:
        start_pos = char_count
        char_count += 15
        result += f'<p data-end="{char_count}" data-start="{start_pos}" style="font-weight: bold; font-size: 18px;">Комплектация:</p>\n\n'
        
        # Парсим комплектацию из таблицы
        equip_clean = equipment_text.replace('<![CDATA[', '').replace(']]>', '')
        equipment_items = parse_table_to_list(equip_clean)
        
        if equipment_items:
            ul_start = char_count
            result += f'<ul data-end="PLACEHOLDER_UL_END2" data-start="{ul_start}">\n'
            
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
            result = result.replace('PLACEHOLDER_UL_END2', str(char_count))
            result += '</ul>\n'
    
    return result

# Основной код
tree = ET.parse('feed-yml-0.xml')
root = tree.getroot()
catalog_df = pd.read_csv('catalog6_new.csv', sep=';')

xml_data = {}
offers = root.findall('.//offer')

for offer in offers:
    vendor_code = offer.find('vendorCode')
    if vendor_code is not None:
        description = offer.find('description')
        tech = offer.find('tech')
        equipment = offer.find('equipment')
        pictures = offer.findall('picture')
        
        # Собираем все фото
        all_photos = [pic.text for pic in pictures if pic.text]
        photos_string = ";".join(all_photos)
        
        # Форматируем описание
        desc_text = description.text if description is not None and description.text else ""
        tech_text = tech.text if tech is not None and tech.text else ""
        equip_text = equipment.text if equipment is not None and equipment.text else ""
        
        formatted_description = format_description(desc_text, tech_text, equip_text)
        
        xml_data[vendor_code.text] = {
            'photos': photos_string,
            'description': formatted_description
        }

# Обновляем каталог
for index, row in catalog_df.iterrows():
    artikul = str(row['Артикул'])
    if artikul in xml_data:
        if pd.isna(row['Фото товара']) or row['Фото товара'] == '':
            catalog_df.at[index, 'Фото товара'] = xml_data[artikul]['photos']
        
        if pd.isna(row['Описание']) or row['Описание'] == '':
            catalog_df.at[index, 'Описание'] = xml_data[artikul]['description']

catalog_df.to_csv('catalog6_formatted.csv', sep=';', index=False, encoding='utf-8-sig')
print("Каталог с форматированными описаниями сохранен как catalog6_formatted.csv")