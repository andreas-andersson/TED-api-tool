#!/usr/bin/env python

import requests
from bs4 import BeautifulSoup
import base64
import urllib.parse
import json
import argparse
from datetime import date
import os


#
#   CLI arguements Setup
#
parser = argparse.ArgumentParser()

parser.add_argument('--country', '-c', help = 'Set country code, two letters in caps, default is SE', type = str, default = "SE")
parser.add_argument('--limit', '-l', help = 'Limit results to, default is 50', type = int, default = 20)
parser.add_argument('--page', '-p', help = 'Limit results to, default is 50', type = int, default = 1)
parser.add_argument('--search', '-t', help = 'Search string', type = str )
parser.add_argument('--date', '-d', help = 'Date to search (YYYYMMDD)', type = str )
parser.add_argument('--savexml', help = 'Save results as XML-files', type = str )
parser.add_argument('--json', help = 'Return as json', action='store_true' )
parser.add_argument('--debug', help = 'Prints out debug information', action='store_true' )

# Save all arguements here
args = parser.parse_args()


def fetchFromApi():

    # Start building a query
    qs = []
    if args.country:
        qs.append("CY=[" + str(args.country) +"]")

    if args.date:
        qs.append("PD=[" + str(args.date) +"]")
    
    if args.search:
        searchList = []
        for w in args.search.split(","):
            searchList.append('FT=[' + w + ']')
        search = " AND ".join(searchList)
        qs.append('(' + search + ')' )

    # Parse query string
    apiQuery = urllib.parse.quote( " AND ".join(qs) )
    debug(" AND ".join(qs), 'query')

    # Generate request URI
    apiUrl = 'https://ted.europa.eu/api/v2.0/notices/search?fields=CONTENT&pageNum=%d&pageSize=%d&q=%s&reverseOrder=false&scope=2&sortField=ND' % (args.page, args.limit, apiQuery)
    debug(apiUrl, 'request url')

    # Get the response
    req = requests.get(apiUrl)
    req_json = req.json()
    debug(req_json, 'json response')

    print('-------------------------------------------------------------------')
    print('')
    print('    Showing '+ str(len(req_json['results'])) + ' of ' + str(req_json['total']) + ' found notices.')
    print('')
    print('-------------------------------------------------------------------')
    print('')
    print('')

    for c in req_json['results']:
        doc = readContent( c['content'] )
        #  print(json.dumps(doc))
        if args.json == False:
            print(doc['name'] + ' / ' + doc['city'] )
            print(doc['title'])
            print(doc['desc'])
            print(doc['applyurl'])
            print('')
            print('-------------------------------------------------------------------')
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
        filename = path + '/' + ted['docId'] + '.xml'
        f = open(filename,"w+")
        f.write(doc.prettify())
        f.close()

    return ted


def extractJSON(doc):
    ted = {}
    
    # Find ORG information
    org_details = doc.find('CONTRACTING_BODY')
    if org_details:
        ted['org_details'] = {
            "name":          findOrFalse( org_details.find('OFFICIALNAME') ),
            "city":          findOrFalse( org_details.find('TOWN') ),
            "street":        findOrFalse( org_details.find('ADDRESS') ),
            "contact_name":  findOrFalse( org_details.find('CONTACT_POINT') ),
            "contact_email": findOrFalse( org_details.find('E_MAIL') ),
            "url":           findOrFalse( org_details.find('E_MAIL') )
        }
    
    # ted['primary_cpv'] = ''
    ted['cpv'] = {}
    for cpv in doc.find_all('ORIGINAL_CPV'):
        ted['cpv'][cpv['CODE']] = cpv.get_text()

    ted['nuts'] =          findOrFalse( doc.find('NUTS'), 'CODE' ) or ""
    ted['name'] =          findOrFalse( doc.find('CONTRACTING_BODY').find('OFFICIALNAME') ) or ""
    ted['city'] =          findOrFalse( doc.find('TOWN') ) or ""
    ted['title'] =         findOrFalse( doc.find('TITLE') ) or ""
    ted['desc'] =          findOrFalse( doc.find('SHORT_DESCR') ) or ""
    ted['docId'] =         findOrFalse( doc.find('TED_EXPORT'), 'DOC_ID' )  or "" 
    ted['date_added'] =    findOrFalse( doc.find('CODED_DATA_SECTION').find('DATE_PUB') )  or "" 
    ted['date_expires'] =  findOrFalse( doc.find('DELETION_DATE') )  or "" 
    ted['date_submitby'] = findOrFalse( doc.find('DATE_RECEIPT_TENDERS') )  or "" 
    ted['applyurl'] =      findOrFalse( doc.find('URL_DOCUMENT') ) or ""
    return ted

def findOrFalse(el, attr = False):
    if el and attr == False:
        return el.get_text().strip()
    elif el and attr:
        return el[attr]
    else:
        return False

def debug(data, flag = ""):
    if args.debug:
        print( '[' + flag + ']' )
        print( repr(data) )
        print( '[/' + flag + ']' )

fetchFromApi()