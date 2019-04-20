# Falabella-Utils

Falabella-utils are Python scripts for extracting the information of a SKU from [Saga Falabella](https://falabella.com.pe/falabella-pe/) peruvian website.

## Requirements

This scrpits are intended to be ran in a online enviroment like [Repl.it](https://repl.it/) but can be used locally with the following dependencies:

```bash
pandas
requests
xlsxwriter
bs4
scrapy
```

## Usage


First get the correct folder structure, a file named __Lista__ with all the SKUs to check, and the scripts you want to run:

```
Lista
get_report.py
scrapy_report.py
```

Then run the script and it will return __Resultado.xlsx__, a report with the data of each SKU __(published, image, prod and brand)__.

## Contributing
Pull requests and new features sugestions are welcome. For major changes, please open an issue first to discuss what you would like to change.

Or also you can contact me at (jpereira@pucp.edu.pe) 
