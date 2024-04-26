# Otomoto scrapper

This code scrapping otomoto website and send data to database


## Usage

To run the script, i suggest to have a virtual environment installed.

1. Install dependences:

```
pip install -r requirements.txt
```

2. Run script with your parametters

```
python scrapper.py --car_brands_path "otomoto_dictionary/car_brands.csv" 
                   --car_models_path "otomoto_dictionary/car_models" 
                   --db_port 5432 
                   --db_username "master" 
                   --db_password "IsthataSupra1234" 
                   --db_table_name "postgres" 
                   --db_hostname "130.162.226.117"
```
