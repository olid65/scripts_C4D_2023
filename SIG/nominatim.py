from typing import Optional
import c4d
import os, ssl



import logging
log = logging.getLogger(__name__)

import json

from urllib.request import urlopen
from urllib.request import Request
from urllib.parse import quote_plus



doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

TIMEOUT = 2

# SOURCE code : BlenderGIS
def nominatimQuery(
    query,
    base_url = 'https://nominatim.openstreetmap.org/',
    referer = None,
    user_agent = None,
    format = 'json',
    limit = 10):

    url = base_url + 'search?'
    url += 'format=' + format
    url += '&q=' + quote_plus(query)
    url += '&limit=' + str(limit)

    log.debug('Nominatim search request : {}'.format(url))
    print(url)
    req = Request(url)
    if referer:
        req.add_header('Referer', referer)
    if user_agent:
        req.add_header('User-Agent', user_agent)

    response = urlopen(req, timeout=TIMEOUT)

    r = json.loads(response.read().decode('utf-8'))

    return r

def wgs84_to_lv95(lat,lon):
    """converti de wgs84 en chlv95 via une requete REST 
       sur l'outil en ligne de swisstopo"""
    url = f'http://geodesy.geo.admin.ch/reframe/wgs84tolv95?easting={lon}&northing={lat}&format=json'
    site = urlopen(url)
    data =  json.load(site)
    return data['easting'],data['northing']


def main() -> None:
    #par défaut la fonction renvoie 10 résultats
    for res in nominatimQuery('Trient,CH'):
        print(res['display_name'])
        lat = res['lat']
        lon = res['lon']
        print(wgs84_to_lv95(lat,lon))
        return
        print('-'*50)

"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()