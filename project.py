import os
import pandas as pd


class PriceListAnalyzer:
    def __init__(self):
        self.data = []

    def load_prices(self, directory='.'):
        product_columns = ['название', 'продукт', 'товар', 'наименование']
        price_columns = ['цена', 'розница']
        weight_columns = ['фасовка', 'масса', 'вес']

        for filename in os.listdir(directory):
            if 'price' in filename and filename.endswith('.csv'):
                file_path = os.path.join(directory, filename)
                try:
                    df = pd.read_csv(file_path)
                except Exception as e:
                    print(f"Ошибка чтения файла {file_path}: {e}")
                    continue

                product_col = self._search_product_price_weight(df.columns, product_columns)
                price_col = self._search_product_price_weight(df.columns, price_columns)
                weight_col = self._search_product_price_weight(df.columns, weight_columns)

                if product_col is not None and price_col is not None and weight_col is not None:
                    for index, row in df.iterrows():
                        name = row[product_col] if pd.notna(row[product_col]) else 'Неизвестно'
                        price = row[price_col] if pd.notna(row[price_col]) else 0
                        weight = row[weight_col] if pd.notna(row[weight_col]) else 0

                        self.data.append({
                            'name': name,
                            'price': price,
                            'weight': weight,
                            'file': filename
                        })

    def _search_product_price_weight(self, headers, columns):
        for col in columns:
            if col in headers:
                return col
        return None

    def export_to_html(self, fname='output.html'):
        with open(fname, 'w', encoding='utf-8') as file:
            file.write('''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Позиции продуктов</title>
            </head>
            <body>
                <table border="1">
                    <tr>
                        <th>Номер</th>
                        <th>Название</th>
                        <th>Цена</th>
                        <th>Фасовка</th>
                        <th>Файл</th>
                        <th>Цена за кг.</th>
                    </tr>
            ''')
            for count, item in enumerate(self.data, start=1):
                price_per_kg = item['price'] / item['weight'] if item['weight'] > 0 else 0
                file.write(f'''
                    <tr>
                        <td>{count}</td>
                        <td>{item['name']}</td>
                        <td>{item['price']}</td>
                        <td>{item['weight']}</td>
                        <td>{item['file']}</td>
                        <td>{price_per_kg:.2f}</td>
                    </tr>
                ''')
            file.write('''
                </table>
            </body>
            </html>
            ''')

    def find_text(self, text, fname=None):
        results = []
        for item in self.data:
            if text.lower() in item['name'].lower():
                results.append(item)

        for item in results:
            item['price_per_kg'] = item['price'] / item['weight'] if item['weight'] > 0 else float('inf')
        results.sort(key=lambda x: (x['name'], x['price_per_kg']))

        if fname:
            df = pd.DataFrame(results)
            df.to_html(fname, index=False, encoding='utf-8')
            print(f'Результаты поиска сохранены в {fname}.')
        return results


pm = PriceListAnalyzer()
pm.load_prices()

while True:
    search_text = input('Введите текст для поиска или "exit" для выхода: ')
    if search_text.lower() == 'exit':
        print('Работа завершена.')
        break
    if not search_text.strip():
        print("Ошибка: Ввод не может быть пустым. Пожалуйста, попробуйте снова.")
        continue
    results = pm.find_text(search_text)
    if not results:
        print("По вашему запросу ничего не найдено.")
        continue

    for count, item in enumerate(results, start=1):
        price_per_kg = item['price'] / item['weight'] if item['weight'] > 0 else float('inf')
        print(
            f'{count}  {item["name"]:50}  {item["price"]:>6}  {item["weight"]:>4}  {item["file"]}  {price_per_kg:.2f}')

    file_name = f'Поиск_{search_text}.html'
    pm.find_text(search_text, fname=file_name)

pm.export_to_html()
