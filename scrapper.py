import argparse
from bs4 import BeautifulSoup
import requests
import pandas as pd
from otomoto_db import OtomotoDB
from tqdm import tqdm
from parser import ParserOTOMOTO

class OtomotoScrapper:
    def __init__(self, car_brands_path, car_models_path):
        self.car_brands_path = car_brands_path
        self.car_models_path = car_models_path
        self.urls = []

    def get_urls(self):
        with open(self.car_brands_path, 'r') as brands:
            for brand in tqdm(brands):
                brand = brand.strip()
                
                with open(f'{self.car_models_path}/{brand}_models.csv', 'r') as models:
                    for model in models:
                        model = model.strip()

                        if model:
                            self.urls.append(f"https://www.otomoto.pl/osobowe/{brand}/{model}")

    @staticmethod
    def scrapper_search(url, get_page_sign='?'):
        records = []
        # First page
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            num_pages = ParserOTOMOTO.get_max_page(soup)

            # Get data
            post_data = ParserOTOMOTO.get_post_data(soup)

            records += post_data

            # If are more than one page go iterate of them
            if num_pages > 1:
                for page in range(num_pages - 1):
                    url_page = url + f"{get_page_sign}page={page + 2}"
                    response = requests.get(url_page)

                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        post_data = ParserOTOMOTO.get_post_data(soup)
                        records += post_data

                    else:
                        print(f'Błąd podczas pobierania strony, status code: {response.status_code}')

        else:
            print(f'Błąd podczas pobierania strony, status code: {response.status_code}')

        return records
    
    def run(self):
        df = pd.DataFrame(columns=['brand', 'model', 'generation', 'capacity', 'horse_power', 'mileage', 'fuel_type', 'gearbox', 'year_production', 'price'])

        for url in tqdm(self.urls): # Use self.urls[5:] for test
            # First page
            response = requests.get(url)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                num_records = ParserOTOMOTO.get_num_records(soup)

                if not num_records:
                    continue

                generations = ParserOTOMOTO.get_generations(soup)
                brand, model = url.split("/")[-2:]

                if generations is not None:
                    for (generation, url_generation) in generations:
                        data_search = OtomotoScrapper.scrapper_search(url_generation, get_page_sign='&')
                        if data_search:
                            data_search_df = pd.DataFrame(data_search)
                            data_search_df['generation'] = generation
                            data_search_df['brand'] = brand
                            data_search_df['model'] = model
                            data_search_df['segment'] = None
                            data_search_df['drive_type'] = None
                            df = pd.concat([df, data_search_df], ignore_index=True)

                else:
                    data_search = OtomotoScrapper.scrapper_search(url)
                    if data_search:
                        data_search_df = pd.DataFrame(data_search)
                        data_search_df['generation'] = None
                        data_search_df['brand'] = brand
                        data_search_df['model'] = model
                        data_search_df['segment'] = None
                        data_search_df['drive_type'] = None
                        df = pd.concat([df, data_search_df], ignore_index=True)

            else:
                print(f'Błąd podczas pobierania strony, status code: {response.status_code}')

        df.to_csv('otomoto_database.csv', index=False)
        return df


parser = argparse.ArgumentParser(description='Otomotot scrapper',
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument('--car_brands_path', default=None, help='Path to file witch mapping car brand')
parser.add_argument('--car_models_path', default=None, help='Path to file witch mapping car models')
parser.add_argument('--db_port', default=None, type=int, help='Database port')
parser.add_argument('--db_username', default=None, help='Database username')
parser.add_argument('--db_password', default=None, help='Database password')
parser.add_argument('--db_table_name', default=None, help='Database table name')
parser.add_argument('--db_hostname', default=None, help='Database ip / hostname')

def main():
    args = parser.parse_args()

    otomoto_scrapper = OtomotoScrapper(car_brands_path = args.car_brands_path, 
                                       car_models_path = args.car_models_path)

    otomoto_scrapper.get_urls()
    otomoto_data = otomoto_scrapper.run()

    if args.db_hostname is not None and args.db_table_name is not None and args.db_username is not None and args.db_password is not None and args.db_port is not None:
        otomoto_db = OtomotoDB()
        otomoto_db.connect(args.db_hostname, args.db_table_name, args.db_username, args.db_password, args.db_port)
        otomoto_db.send_data(otomoto_data)


if __name__ == '__main__':
    main()