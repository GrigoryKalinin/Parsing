import xml.etree.ElementTree as ET
from ai_content_generator import AIContentGenerator
import pandas as pd
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

def main():
    """Добавляет description в XML файл там, где его нет"""
    
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
    
    # Ищем товары без description
    offers_without_desc = []
    offers_with_desc = 0
    debug_count = 0
    
    for offer in root.findall('.//offer'):
        vendor_code_elem = offer.find('vendorCode')
        if vendor_code_elem is not None:
            vendor_code = vendor_code_elem.text.strip()
            description_elem = offer.find('description')
            
            # Отладочная информация для первых 5 товаров
            if debug_count < 5:
                name_elem = offer.find('name')
                name = name_elem.text if name_elem is not None else 'Нет названия'
                desc_status = 'Нет элемента' if description_elem is None else ('Пустой' if not description_elem.text or description_elem.text.strip() == '' else f'Есть ({len(description_elem.text)} симв.)')
                print(f"Отладка {debug_count + 1}: {vendor_code} - {name[:30]}... - Description: {desc_status}")
                debug_count += 1
            
            # Проверяем отсутствие description или пустое содержимое
            has_description = False
            if description_elem is not None and description_elem.text:
                desc_text = description_elem.text.strip()
                if desc_text and desc_text != '' and not desc_text.isspace():
                    has_description = True
            
            if not has_description:
                if vendor_code in product_data:
                    offers_without_desc.append((offer, vendor_code))
            else:
                offers_with_desc += 1
    
    total_offers = len(root.findall('.//offer'))
    print(f"Всего товаров в XML: {total_offers}")
    print(f"Товаров с описанием: {offers_with_desc}")
    print(f"Товаров без описания: {len(offers_without_desc)}")
    print(f"Товаров не найдено в каталоге: {total_offers - offers_with_desc - len(offers_without_desc)}")
    
    if len(offers_without_desc) == 0:
        print("Все товары уже имеют описания!")
        return
    
    # Показываем примеры товаров без описания
    print(f"\nПримеры товаров без описания:")
    for i, (offer, vendor_code) in enumerate(offers_without_desc[:3]):
        name_elem = offer.find('name')
        name = name_elem.text if name_elem is not None else 'Нет названия'
        print(f"  {i+1}. {vendor_code} - {name}")
    
    # Подтверждение
    proceed = input(f"\nДобавить описания для {len(offers_without_desc)} товаров? (y/n): ").lower().strip()
    if proceed != 'y':
        print("Отменено.")
        return
    
    # Генерируем описания
    print("\nНачинаю генерацию описаний...")
    processed = 0
    
    for i, (offer, vendor_code) in enumerate(offers_without_desc):
        product = product_data[vendor_code]
        print(f"Товар {i + 1}/{len(offers_without_desc)}: {product['name'][:40]}...")
        
        # Генерируем описание
        try:
            # Создаем временный row для совместимости с методом
            temp_row = pd.Series({
                'Наименование': product['name'],
                'Категория: 1': product['category'],
                'Цена': product['price']
            })
            
            description = ai_generator.generate_description_from_tech(temp_row, {})
            
            if description:
                # Добавляем или обновляем description элемент
                description_elem = offer.find('description')
                if description_elem is None:
                    description_elem = ET.SubElement(offer, 'description')
                
                description_elem.text = description
                processed += 1
                print(f"  ✓ Добавлено описание ({len(description)} символов): {description[:50]}...")
            else:
                print(f"  ✗ Не удалось сгенерировать описание")
                
        except Exception as e:
            print(f"  ✗ Ошибка генерации для {vendor_code}: {e}")
        
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
        print(f"\nГотово! Добавлено {processed} описаний. XML файл обновлен.")
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