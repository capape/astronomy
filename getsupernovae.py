#!/usr/bin/python
# Check supernova data
#

import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
from astropy.coordinates import SkyCoord
import ssl
from datetime import datetime, timedelta
import sys
import astropy.units as u
class Supernova:          
    def __init__(self, date, mag, host, name, ra, decl, link, constellation, coordinates, firstObserved, maxMagnitude, type):
        self.name = name
        self.date = date
        self.mag = mag
        self.host = host
        self.name = name
        self.ra = ra
        self.decl = decl
        self.link = link
        self.constellation = constellation
        self.coordinates = coordinates
        self.type = type
        self.firstObserved = firstObserved
        self.maxMagnitude = maxMagnitude


   

def printSupernova(data):    
        print('Date:', data.date, ',    Magnitude:', data.mag, ', Type: ', data.type)
        print('     FIRST Date:', data.firstObserved, ',  MAX:  Magnitude:', data.maxMagnitude)
        print('     Const:', data.constellation,', Host:', data.host, ', Name:', data.name)
        print('     RA:', data.ra, ', DECL.', data.decl)
        print('     Goto: ', data.link)
        print('')


def selectSupernovas(trs, maxMag, fromDate):

    print ('Selecting supernovae from: ', fromDate, ' to now and magnitud less than', maxMag)
    print
    supernovas = []
    for tr in trs:
        if tr.contents[0].name == 'td':
            mag = tr.contents[5].contents[0]
            date = tr.contents[6].contents[0]

            if (mag < maxMag and date > fromDate): 
                ra = tr.contents[2].contents[0]
                decl = tr.contents[3].contents[0]            
                name = tr.contents[0].contents[0].contents[0]
                host = tr.contents[1].contents[0]                
                coord=SkyCoord(ra, decl , frame='icrs', unit=(u.hourangle, u.deg))            
                constellation = coord.get_constellation()
                firstObserved = tr.contents[10].contents[0]
                maxMagnitude = tr.contents[9].contents[0]
                type =  tr.contents[8].contents[0]
                              

                link = 'https://www.rochesterastronomy.org/' + tr.contents[0].contents[0].get('href')[3:]
                data = Supernova(date, mag, host, name, ra, decl, link, constellation, coord, firstObserved, maxMagnitude, type)
            
                supernovas.append(data)
    return supernovas
    


 
if len(sys.argv) > 3:
    raise ValueError('Usage: getsupernovae.py maxMag lastDays')
 


# Ignore ssl cert errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
# url = 'https://www.physics.purdue.edu/brightsupernovae/snimages/sndate.html'
url = 'https://www.rochesterastronomy.org/snimages/snactive.html'
html = urllib.request.urlopen(url, context=ctx).read()
soup = BeautifulSoup(html, 'html.parser')

# Find all supernovae rows
trs = soup('tr')

mag='18'
deltaDays=-15
if (len(sys.argv)==3):
    deltaDays= (-1 * int(sys.argv[2]))
    mag=sys.argv[1]
elif (len(sys.argv)==2):
    mag=sys.argv[1]


fromDate = datetime.now() + timedelta(days = deltaDays);



supernovas = selectSupernovas(trs, mag, fromDate.strftime('%Y/%m/%d'))

supernovas.sort(key = lambda x : x.date, reverse=True)

for data in supernovas:
    printSupernova(data)

    