#!/usr/bin/python
# Check supernova data
#

import urllib.request
import urllib.parse
import urllib.error
from bs4 import BeautifulSoup
from astropy.coordinates import AltAz, EarthLocation, SkyCoord
from astropy.time import Time
import ssl
from datetime import datetime, timedelta
import sys
import astropy.units as u


old=[
    "2023ixf",
    "2023wcr",
    "2023wrk",
    "2024akh",
    "2024ana",
    "2024axg",
    "2024bhp",
    "2024byg",
    "2024cld",
    "2024dlk",
    "2024dru",
    "2024drv",
    "2024ehs",
    "2024eys",
    "2024fjp",
    "2024gqf",
    "2024gwq",
    "2024gyr",
    "2024hcj",
    "2024iey",
    "AT2024ajf",
    "AT2024ccb",
    "AT2024cva",
    "AT2024dgr",
    "AT2024ego",
    "AT2024eqz",
    "AT2024evp",
    "AT2024fpe",
    "AT2024gfh",
    "AT2024iwq",
    "Nova M31 2024-03b?"
    ]

class Supernova:
    def __init__(self, date, mag, host, name, ra, decl, link, constellation, coordinates, firstObserved, maxMagnitude, maxMagnitudeDate, type, visibility):
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
        self.maxMagnitudeDate = maxMagnitudeDate
        self.visibility = visibility

class AxCordInTime:
    def __init__(self, time, coord):        
        self.time=time
        self.coord=coord
class Visibility:
    def __init__(self, visible,  azCords):
        self.visible=visible
        self.azCords=azCords


def printSupernova(data):
    print('-------------------------------------------------')
    print('Date:', data.date, ', Mag:',  data.mag, ', T: ', data.type, ', Name:', data.name)
    print('  Const:', data.constellation, ', Host:', data.host)
    print('  RA:', data.ra, ', DECL.', data.decl)
    print('')    
    print('  Visible from :', data.visibility.azCords[0].time.strftime('%y-%m-%d %H:%M'),
            'to:', data.visibility.azCords[-1].time.strftime('%y-%m-%d %H:%M'))
    print('  AzCoords az:', data.visibility.azCords[0].coord.az.to_string(sep=' ',precision=2) ,
          ', lat:', data.visibility.azCords[0].coord.alt.to_string(sep=' ',precision=2))
    print('  Last azCoords az:', data.visibility.azCords[-1].coord.az.to_string(sep=' ',precision=2) ,
          ', lat:', data.visibility.azCords[-1].coord.alt.to_string(sep=' ',precision=2))
    print('')
    print('  Discovered:', data.firstObserved, ', MAX Mag:', data.maxMagnitude, 'on: ', data.maxMagnitudeDate)   
    print(' ', data.link)    
    print('')


def printSupernovaShort(data):
    print('-------------------------------------------------')
    print('Const:', data.constellation, '-', data.host , ' S: ', data.name, ', M:', data.mag, ', T: ', data.type)    
    print('D: ', data.date, ' RA:', data.ra, ', DEC:', data.decl)
    print('Visible from :', data.visibility.azCords[0].time.strftime('%y-%m-%d %H:%M'),
            'to:',  data.visibility.azCords[-1].time.strftime('%y-%m-%d %H:%M'),
             'az:', data.visibility.azCords[0].coord.az.to_string(sep=' ',precision=2) , ', LAT:', data.visibility.azCords[0].coord.alt.to_string(sep=' ',precision=2))
    print('')



def selectSupernovas(maxMag, observationDay, deltaDays, site, minAlt=0, maxAlt=90, minAz=0,maxAz=360):

    dataRows = getRochesterHtmlDataRows()
    
    fromDateTime = observationDay + timedelta(days=deltaDays)
    fromDate = fromDateTime.strftime('%Y-%m-%d')

    observationStart = observationDay.strftime('%Y-%m-%d') + "T22:00Z"
    
    time1 = Time(observationStart)
    time2 = time1 + timedelta(hours=8)

    print('Supernovae from: ', fromDate, ' to now. Magnitud <=', maxMag) #, 'for location ', location)    
    print("Site: lon: {lon:.2f} lat: {lat:.2f} height: {height:.2f}m . Min alt {minAlt}º".format(lon=site.lon.value, lat=site.lat.value, height=site.height.value , minAlt=minAlt))
    print('')

    supernovas = []
    for dataRow in dataRows:
        if dataRow.contents[0].name == 'td':
            mag = dataRow.contents[5].contents[0]
            date = dataRow.contents[6].contents[0]

            if (mag < maxMag and date > fromDate):
                ra = dataRow.contents[2].contents[0]
                decl = dataRow.contents[3].contents[0]
                name = dataRow.contents[0].contents[0].contents[0]
                host = dataRow.contents[1].contents[0]
                coord = SkyCoord(ra, decl, frame='icrs',
                                 unit=(u.hourangle, u.deg))
                
                
                visibility = getVisibility(site, coord, time1, time2, minAlt, maxAlt, minAz, maxAz)

                if (visibility.visible and name not in old):

                    constellation = coord.get_constellation()
                    firstObserved = dataRow.contents[11].contents[0]
                    maxMagnitudeDate = dataRow.contents[10].contents[0]
                    maxMagnitude = dataRow.contents[9].contents[0]
                    type = dataRow.contents[7].contents[0]

                    link = 'https://www.rochesterastronomy.org/' + \
                        dataRow.contents[0].contents[0].get('href')[3:]
                    data = Supernova(date, mag, host, name, ra, decl, link,
                                     constellation, coord, firstObserved, maxMagnitude, maxMagnitudeDate, type, visibility)

                    supernovas.append(data)

    return supernovas

def getRochesterHtmlDataRows():
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

    return trs;


def getVisibility(site, coord, time1, time2, minAlt = 0, maxAlt=90, minAz =0, maxAz=360):
    
    visible = False
    loopTime = time1
    azVisibles = []
    while loopTime < time2:        
        altaz = coord.transform_to(AltAz(obstime=loopTime,location=site))
        loopTime = loopTime + timedelta(hours=0.5)        
        if (altaz.alt.dms.d >= minAlt and altaz.alt.dms.d <= maxAlt and altaz.az.dms.d >=minAz and altaz.az.dms.d<= maxAz ):            
            visible= True
            azVisibles.append(AxCordInTime(loopTime,altaz))

    azVisibles.sort(key=lambda x: x.time)    
       
    return Visibility(visible, azVisibles)


if len(sys.argv) > 3:
    raise ValueError('Usage: getsupernovae.py maxMag lastDays')

def main():

 
    mag = '18'
    deltaDays = -15

    if (len(sys.argv) == 3):
        deltaDays = (-1 * int(sys.argv[2]))
        mag = sys.argv[1]
    elif (len(sys.argv) == 2):
        mag = sys.argv[1]

    site = EarthLocation(lat=41.55*u.deg, lon=2.09*u.deg, height=224*u.m)

    supernovas = selectSupernovas(mag, datetime.now(), deltaDays, site, 25)
    #supernovas = selectSupernovas(mag, datetime.now(), deltaDays, site, 25, 55, 180, 340)

    
    
    supernovas.sort(key=lambda x: x.visibility.azCords[-1].time)
    supernovas.sort(key=lambda x: x.visibility.azCords[0].time)
    
    for data in supernovas:
        printSupernova(data)
        print ('')

    
    #for data in supernovas:
    #    printSupernovaShort(data)

if __name__ == "__main__":
    main()
