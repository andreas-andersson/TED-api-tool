import requests
from bs4 import BeautifulSoup
import base64
import urllib.parse
import json
import argparse
from datetime import date
import os

parser = argparse.ArgumentParser()

parser.add_argument('--country', '-c', help = 'Set country code, two letters in caps, default is SE', type = str, default = "SE")
parser.add_argument('--limit', '-l', help = 'Limit results to, default is 50', type = int, default = 20)
parser.add_argument('--page', '-p', help = 'Limit results to, default is 50', type = int, default = 1)
parser.add_argument('--search', '-t', help = 'Search string', type = str )
parser.add_argument('--date', '-d', help = 'Date to search (YYYYMMDD)', type = str )
parser.add_argument('--savexml', '-s', help = 'Save results as XML-files', type = str )
parser.add_argument('--json', '-j', help = 'Return as json', type = str )

# Save all arguements here
args = parser.parse_args()

# print(args)



def fetchFromApi():
    qs = []
    if args.country:
        qs.append("CY=[" + str(args.country) +"]")

    if args.date:
        qs.append("PD=[" + str(args.country) +"]")
    
    if args.search:
        searchList = []
        for w in args.search.split(","):
            searchList.append('FT=[' + w + ']')
        search = " AND ".join(searchList)
        qs.append('(' + search + ')' )

    apiQuery = urllib.parse.quote( " AND ".join(qs) )
    apiUrl = 'https://ted.europa.eu/api/v2.0/notices/search?fields=CONTENT&pageNum=' + str(args.page) + '&pageSize=' + str(args.limit) + '&q=' + apiQuery + '&reverseOrder=false&scope=2&sortField=ND'
    req = requests.get(apiUrl);
    req_json = req.json()

    print('__________________________________________')
    print('    Showing '+ str(len(req_json['results'])) + ' of ' + str(req_json['total']) + ' found notices.')
    print('__________________________________________')
    print('')
    print('')
    for c in req_json['results']:
        doc = readContent( c['content'] )
        #  print(json.dumps(doc))
        print(doc['name'] + ' / ' + doc['city'] )
        print(doc['title'])
        print(doc['desc'])
        print(doc['applyurl'])
        print('')
        print('__________________________________________')
        print('')



def readContent(content):
    # Base64 decode to xml string
    xml = base64.b64decode(content)

    # Parse with BeautifulSoup
    doc = BeautifulSoup(xml, "xml")

    # Extract the data we want here
    ted = extractJSON(doc)


    if args.savexml:
        # Get current dir, create output dir and save file
        path = os.path.dirname(os.path.abspath(__file__)) + '/' + str(args.savexml)
        os.makedirs(path, exist_ok=True)
        filename = path + '/' + ted['docId'] + '.xml';
        f = open(filename,"w+")
        f.write(doc.prettify())
        f.close()

    return ted;


def extractJSON(doc):
    ted = {}
    
    # ted['org_details'] = {}
    # ted['org_details']['name']
    # ted['org_details']['street']
    # ted['org_details']['zip']
    # ted['org_details']['city']
    # ted['org_details']['contact_name']
    # ted['org_details']['contact_email']
    # ted['org_details']['url']
    
    # ted['primary_cpv'] = ''
    # ted['cpv'] = []

    ted['name'] =     doc.OFFICIALNAME.get_text()
    ted['city'] =     doc.TOWN.get_text()
    ted['title'] =    doc.TITLE.get_text()
    ted['desc'] =     doc.SHORT_DESCR.get_text()
    ted['docId'] =    doc.TED_EXPORT['DOC_ID']
    ted['applyurl'] = doc.CONTRACTING_BODY.URL_DOCUMENT.get_text()
    return ted;

fetchFromApi()