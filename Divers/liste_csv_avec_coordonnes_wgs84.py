from typing import Optional
import c4d
import csv
import urllib,json


def wgs84_to_lv95(lat,lon):
    """converti de wgs84 en chlv95 via une requete REST
       sur l'outil en ligne de swisstopo"""
    url = 'http://geodesy.geo.admin.ch/reframe/wgs84tolv95?easting={0}&northing={1}&format=json'.format(lat,lon)
    site = urllib.request.urlopen(url)
    data =  json.load(site)
    return float(data['easting']),float(data['northing'])

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

def main() -> None:
    # Called when the plugin is selected by the user. Similar to CommandData.Execute.
    fn = '/Users/olivierdonze/switchdrive/Mandats/Parc_naturel_regional_vallee_Trient/docs/automnales-scenario_pour_python.csv'
    fn_dst = '/Users/olivierdonze/switchdrive/Mandats/Parc_naturel_regional_vallee_Trient/docs/automnales_scenario_lv95.json'
    lst = []
    with open(fn, newline='', encoding = 'utf-8') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=';', quotechar='|')
        for commune,libel,coord,theme in spamreader:
            lon,lat = [float(val) for val in coord.split(',')]
            print(commune,libel,coord,theme)
            x,y = wgs84_to_lv95(lat,lon)
            lst.append([commune,libel,x,y,theme])

    with open(fn_dst,'w',encoding = 'utf-8') as f:
        f.write(json.dumps(lst,indent = 4))



"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()