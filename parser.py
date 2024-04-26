class ParserOTOMOTO:

    @staticmethod
    def get_max_page(soup):
        element = soup.find(class_ = 'ooa-1vdlgt7')

        if not element:
            return 0

        ul = element
        pagination_numbers = ul.find_all(class_='ooa-g4wbjr')
        max_page_numer = pagination_numbers[len(pagination_numbers)-1].find('span').text
        return int(max_page_numer)
    
    @staticmethod
    def get_num_records(soup):
        element = soup.find(class_ = 'e17gkxda2')

        if element is None:
            return 0

        return int(element.find('b').text.replace(" ", ""))

    
    @staticmethod
    def get_generations(soup):

        """
        Returns:
            List: Each element contain name of generation and link. [(name, link), ...]
        """

        generation = soup.find(class_='ooa-231jno') if soup else None
        
        if generation is not None:

            if generation.find(class_='eiujiyl3').text.split(" ")[0] == "Generacje":
                generation_links = generation.find_all('a')
                generations_mapping = [(link.find('em').text.strip(), link.get('href')) for link in generation_links]

                return generations_mapping
        
        return None
    
    @staticmethod
    def get_post_data(soup):
        records = []

        div = soup.find('div', {'data-testid': 'search-results'})
        offers = div.find_all('article', class_='ooa-yca59n') if div else []

        for offer in offers:
            mileage, fuel_type, gearbox, year_production = ParserOTOMOTO.get_post_body_details(offer)

            if fuel_type == "Elektryczny":
                _, horse_power = ParserOTOMOTO.get_post_header_details(offer, skip_capacity=True)
                capacity = None

            else:
                capacity, horse_power = ParserOTOMOTO.get_post_header_details(offer)

            price = ParserOTOMOTO.get_post_price(offer)

            records.append({'capacity': capacity, 
                            'horse_power': horse_power, 
                            'mileage': mileage, 
                            'fuel_type': fuel_type, 
                            'gearbox': gearbox, 
                            'year_production': year_production, 
                            'price': price})

        return records

    @staticmethod
    def get_model_is_selected(soup):

        try:
            element = soup.find(class_ = 'ezh3mkl8') if soup else None
            li_elements = element.find_all('li')

            if len(li_elements) == 4:
                return True
            
            return False
        
        except Exception:
            return None

            
    @staticmethod
    def get_post_header_details(soup, skip_capacity=False):
            header_details = soup.find(class_='e1i3khom9') if soup else None
            header_details_text = header_details.text

            try:
                if skip_capacity:
                    horse_power = header_details_text.split("•")[0]
                    capacity_cleaned = None

                else:
                    capacity, horse_power = header_details_text.split("•")[:2]
                    capacity_cleaned = int(capacity.strip()[:-3].replace(" ", ""))

            except ValueError:
                return None, None

            try:
                horse_power_cleaned = int(horse_power.strip()[:-2].replace(" ", ""))
            except ValueError:
                horse_power_cleaned = None

            return capacity_cleaned, horse_power_cleaned
    
    @staticmethod
    def get_post_body_details(soup):
        body_details = soup.find(class_='ooa-1uwk9ii') if soup else None

        # mileage
        try:
            mileage = body_details.find('dd', {'data-parameter': 'mileage'})
            if mileage is not None:
                mileage = int(mileage.text.strip()[:-2].replace(" ", ""))
            else:
                mileage = 0
        except Exception:
            fuel_type = None        

        # fuel_type
        try:
            fuel_type = body_details.find('dd', {'data-parameter': 'fuel_type'}).text
            fuel_type = fuel_type.strip()
        except Exception:
            fuel_type = None

        # gearbox
        try:
            gearbox = body_details.find('dd', {'data-parameter': 'gearbox'}).text
            gearbox = gearbox.strip()
        except Exception:
            gearbox = None

        # year_production
        try:
            year_production = body_details.find('dd', {'data-parameter': 'year'}).text
            year_production = year_production.strip()
        except Exception:
            year_production = None

        return mileage, fuel_type, gearbox, year_production
    
    def get_post_price(soup):
        try:
            price_body = soup.find(class_='emjt7sh16').text if soup else None
            price = price_body.replace(" ", "")

            return price
        
        except Exception:
            return None
