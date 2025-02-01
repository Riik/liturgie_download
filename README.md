Code to download data from immanualkerkdelft.nl about the services and songs. 

### Setup 
Create virtual environment:
`python -m venv .venv` 
Activate it:
`source .venv/bin/activate`

Visit the website -> inspect element -> network tab, extract the header with cookie that looks like this: 
```
kerkspot=<some characters>; ident=<some characters>; s=1
```
and place this in a file `auth_cookie.txt` in the root folder.

## Usage
Download data:
`python liturgy/scraper.py`
Preprocessing: 
`python liturgy/preprocessor.py`
Extracting info:
`python liturgy/regex_parser.py`

Outputs will be written to `data/output`