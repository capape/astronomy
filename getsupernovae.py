#
# Check supernova data
#

import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
from astropy.coordinates import SkyCoord, Distance
import ssl

class Supernova:
    def __init__(self, date, mag, host, name, ra, decl, link, constellation, coordinates):
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


   

def printSupernova(data):    
        print('Date:', data.date, ',    Magnitude:', data.mag)
        print('     Const:', data.constellation,', Host:', data.host, ', Name:', data.name)
        print('     RA:', data.ra, ', DECL.', data.decl)
        print('     Goto: ', data.link)


def selectSupernovas(trs, maxMag, fromDate):
    supernovas = []
    for tr in trs:
        if tr.contents[0].name == 'td':
            mag = tr.contents[8].contents[0]
            date = tr.contents[2].contents[0]

            if (mag < maxMag and date > fromDate): 
                ra = tr.contents[0].contents[0]
                decl = tr.contents[1].contents[0]            
                name = tr.contents[10].contents[0].contents[0]
                host = tr.contents[6].contents[0]
                coord=SkyCoord(ra, decl, frame='icrs', unit='deg')            
                constellation = coord.get_constellation()

                link = 'https://www.physics.purdue.edu/brightsupernovae/' + tr.contents[10].contents[0].get('href')[3:]
                data = Supernova(date, mag, host, name, ra, decl, link, constellation, coord)
            
                supernovas.append(data)
    return supernovas
    



# Ignore ssl cert errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
url = 'https://www.physics.purdue.edu/brightsupernovae/snimages/sndate.html'
html = urllib.request.urlopen(url, context=ctx).read()
soup = BeautifulSoup(html, 'html.parser')

# Find all supernovae rows
trs = soup('tr')

supernovas = selectSupernovas(trs, '18', '2022/09/15')

supernovas.sort(key = lambda x : x.date, reverse=True)

for data in supernovas:
    printSupernova(data)

    