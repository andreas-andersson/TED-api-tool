# Python TED API Tool

## Get started

Install Python dependencies.

`pip install -r requirements.txt`

Make the file executable with:

`chmod +x ted.py`

## Usage

Search for notices directly in the terminal.

`python ted.py --country=SE --limit=20 --date=20191110 --search='search string'`

### Arguements

 `--limit` 
 
 Limit number of returned documents, default is 10
 
 `--page` 
 
 To paginate results use page arguement to set page number

`--date` 

Limit search to notices published on a specific day. (YYYYMMDD)

`--country` 

Set a two letter countrycode for the notice origin

`--search` 

A search string

## Documentation of TED API

[TED API Explorer (Swagger)](https://ted.europa.eu/api/swagger-ui.html#/search-controller-v-2)