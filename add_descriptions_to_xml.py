import xml.etree.ElementTree as ET
from ai_content_generator import AIContentGenerator
import pandas as pd
import os
import re
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

def is_technical_product(name: str, category: str) -> bool:
    """Определяет, является ли товар техническим (нуждается в tech поле)"""
    technical_keywords = [
        'станок', 'двигатель', 'мотор', 'привод', 'шпиндель', 'патрон',
        'фреза', 'сверло', 'резец', 'диск', 'круг', 'полотно',
        'насос', 'компрессор', 'генератор', 'трансформатор',
        'редуктор', 'коробка', 'механизм', 'устройство',
        'прибор', 'инструмент', 'оборудование', 'машина'
    ]
    
    name_lower = name.lower()
    category_lower = category.lower()
    
    # Проверяем ключевые слова в названии
    for keyword in technical_keywords:
        if keyword in name_lower:
            return True
    
    # Проверяем категории
    technical_categories = ['станки', 'оборудование', 'инструмент', 'механизм']
    for cat_keyword in technical_categories:
        if cat_keyword in category_lower:
            return True
    
    return False

def generate_tech_specs(ai_generator: AIContentGenerator, name: str, category: str) -> str:
    """Генерирует технические характеристики для товара"""
    prompt = f"""
    Создай технические характеристики для товара в виде HTML таблицы:
    Название: {name}
    Категория: {category}
    
    Требования:
    - Создай реалистичные технические характеристики
    - Используй HTML таблицу с тегами <table>, <tbody>, <tr>, <td>
    - Включи 8-15 основных параметров
    - Параметры должны соответствовать типу оборудования
    - Используй стандартные единицы измерения (мм, кВт, об/мин, В, кг и т.д.)
    - На русском языке
    
    Пример формата:
    <table>
    <tbody>
    <tr>
    <td>Напряжение, В</td>
    <td>380</td>
    </tr>
    <tr>
    <td>Мощность, кВт</td>
    <td>1,5</td>
    </tr>
    </tbody>
    </table>
    
    Верни только HTML таблицу без дополнительного текста.
    """
    
    return ai_generator._make_request(prompt, max_tokens=500)

def main():
    """Добавляет description и tech в XML файл там, где их нет"""
    
    # Получаем API ключ
    env_api_key = os.getenv('API_KEY')
    
    if env_api_key:
        print(f"Найден API ключ в .env: {env_api_key[:20]}...")
        use_env = input("Использовать ключ из .env? (y/n): ").lower().strip()
        
        if use_env == 'y':
            api_key = env_api_key
            print("Используется API ключ из .env")
        else:
            api_key = input("Введите ваш API ключ: ").strip()
    else:
        print("Файл .env не найден или API_KEY не указан")
        api_key = input("Введите ваш API ключ: ").strip()
    
    if not api_key:
        print("API ключ не указан. Завершение работы.")
        return
    
    # Создаем генератор ИИ
    ai_generator = AIContentGenerator(api_key)
    
    # Загружаем каталог для получения названий и категорий
    try:
        catalog_df = pd.read_csv('catalog6_new.csv', sep=';', encoding='utf-8-sig')
        print(f"Загружен каталог с {len(catalog_df)} товарами")
    except FileNotFoundError:
        print("Файл catalog6_new.csv не найден. Сначала запустите update_catalog.py")
        return
    
    # Создаем словарь артикул -> данные товара
    product_data = {}
    for _, row in catalog_df.iterrows():
        artikul = str(row['Артикул']).strip()
        product_data[artikul] = {
            'name': str(row['Наименование']),
            'category': str(row['Категория: 1']),
            'price': str(row['Цена'])
        }
    
    # Загружаем XML
    try:
        tree = ET.parse('feed-yml-0.xml')
        root = tree.getroot()
        print("XML файл загружен")
    except FileNotFoundError:
        print("Файл feed-yml-0.xml не найден")
        return
    
    # Ищем товары без description и/или tech
    offers_to_process = []
    offers_with_desc = 0
    offers_with_tech = 0
    debug_count = 0
    
    for offer in root.findall('.//offer'):
        vendor_code_elem = offer.find('vendorCode')
        if vendor_code_elem is not None:
            vendor_code = vendor_code_elem.text.strip()
            description_elem = offer.find('description')
            tech_elem = offer.find('tech')
            
            # Отладочная информация для первых 5 товаров
            if debug_count < 5:
                name_elem = offer.find('name')
                name = name_elem.text if name_elem is not None else 'Нет названия'
                desc_status = 'Нет элемента' if description_elem is None else ('Пустой' if not description_elem.text or description_elem.text.strip() == '' else f'Есть ({len(description_elem.text)} симв.)')
                tech_status = 'Нет элемента' if tech_elem is None else ('Пустой' if not tech_elem.text or tech_elem.text.strip() == '' else f'Есть ({len(tech_elem.text)} симв.)')
                print(f"Отладка {debug_count + 1}: {vendor_code} - {name[:30]}... - Description: {desc_status}, Tech: {tech_status}")
                debug_count += 1
            
            # Проверяем отсутствие description
            has_description = False
            if description_elem is not None and description_elem.text:
                desc_text = description_elem.text.strip()
                if desc_text and desc_text != '' and not desc_text.isspace():
                    has_description = True
                    offers_with_desc += 1
            
            # Проверяем отсутствие tech
            has_tech = False
            if tech_elem is not None and tech_elem.text:
                tech_text = tech_elem.text.strip()
                if tech_text and tech_text != '' and not tech_text.isspace():
                    has_tech = True
                    offers_with_tech += 1
            
            # Добавляем в список для обработки если нужно
            if vendor_code in product_data:
                product = product_data[vendor_code]
                needs_description = not has_description
                needs_tech = not has_tech and is_technical_product(product['name'], product['category'])
                
                if needs_description or needs_tech:
                    offers_to_process.append((offer, vendor_code, needs_description, needs_tech))
    
    total_offers = len(root.findall('.//offer'))
    print(f"Всего товаров в XML: {total_offers}")
    print(f"Товаров с описанием: {offers_with_desc}")
    print(f"Товаров с tech: {offers_with_tech}")
    print(f"Товаров для обработки: {len(offers_to_process)}")
    
    if len(offers_to_process) == 0:
        print("Все товары уже имеют необходимые поля!")
        return
    
    # Показываем примеры товаров для обработки
    print(f"\nПримеры товаров для обработки:")
    for i, (offer, vendor_code, needs_desc, needs_tech) in enumerate(offers_to_process[:3]):
        name_elem = offer.find('name')
        name = name_elem.text if name_elem is not None else 'Нет названия'
        actions = []
        if needs_desc:
            actions.append("description")
        if needs_tech:
            actions.append("tech")
        print(f"  {i+1}. {vendor_code} - {name[:40]}... - Нужно: {', '.join(actions)}")
    
    # Подтверждение
    proceed = input(f"\nОбработать {len(offers_to_process)} товаров? (y/n): ").lower().strip()
    if proceed != 'y':
        print("Отменено.")
        return
    
    # Обрабатываем товары
    print("\nНачинаю обработку товаров...")
    processed_desc = 0
    processed_tech = 0
    
    for i, (offer, vendor_code, needs_desc, needs_tech) in enumerate(offers_to_process):
        product = product_data[vendor_code]
        print(f"Товар {i + 1}/{len(offers_to_process)}: {product['name'][:40]}...")
        
        try:
            # Генерируем описание если нужно
            if needs_desc:
                temp_row = pd.Series({
                    'Наименование': product['name'],
                    'Категория: 1': product['category'],
                    'Цена': product['price']
                })
                
                description = ai_generator.generate_description_from_tech(temp_row, {})
                
                if description:
                    description_elem = offer.find('description')
                    if description_elem is None:
                        description_elem = ET.SubElement(offer, 'description')
                    
                    description_elem.text = description
                    processed_desc += 1
                    print(f"  ✓ Добавлено описание ({len(description)} символов)")
            
            # Генерируем tech если нужно
            if needs_tech:
                tech_specs = generate_tech_specs(ai_generator, product['name'], product['category'])
                
                if tech_specs and '<table>' in tech_specs:
                    tech_elem = offer.find('tech')
                    if tech_elem is None:
                        tech_elem = ET.SubElement(offer, 'tech')
                    
                    tech_elem.text = tech_specs
                    processed_tech += 1
                    print(f"  ✓ Добавлены технические характеристики ({len(tech_specs)} символов)")
                else:
                    print(f"  ✗ Не удалось сгенерировать tech")
                    
        except Exception as e:
            print(f"  ✗ Ошибка обработки {vendor_code}: {e}")
        
        # Промежуточное сохранение каждые 10 товаров
        if (i + 1) % 10 == 0:
            try:
                tree.write('feed-yml-0.xml', encoding='utf-8', xml_declaration=True)
                print(f"  Промежуточное сохранение ({i + 1} товаров)")
            except Exception as e:
                print(f"  Ошибка сохранения: {e}")
    
    # Финальное сохранение
    try:
        tree.write('feed-yml-0.xml', encoding='utf-8', xml_declaration=True)
        print(f"\nГотово! Добавлено {processed_desc} описаний и {processed_tech} tech полей. XML файл обновлен.")
    except Exception as e:
        print(f"\nОшибка финального сохранения: {e}")
        # Сохраняем резервную копию
        try:
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f'feed-yml-0_backup_{timestamp}.xml'
            tree.write(backup_name, encoding='utf-8', xml_declaration=True)
            print(f"Резервная копия сохранена как {backup_name}")
        except Exception as e2:
            print(f"Не удалось сохранить резервную копию: {e2}")

if __name__ == "__main__":
    main()