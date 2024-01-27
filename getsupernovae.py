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
    print('  First observation date:', data.firstObserved, ', MAX Magnitude:', data.maxMagnitude, 'on: ', data.maxMagnitudeDate)   
    print('  GOTO: ', data.link)    
    print('')


def printSupernovaShort(data):
    print('-------------------------------------------------')
    print('Const:', data.constellation, '-', data.host , ' S: ', data.name, ', M:', data.mag, ', T: ', data.type)    
    print('D: ', data.date, ' RA:', data.ra, ', DEC:', data.decl)
    print('Visible from :', data.visibility.azCords[0].time.strftime('%y-%m-%d %H:%M'),
            'to:',  data.visibility.azCords[-1].time.strftime('%y-%m-%d %H:%M'),
             'az:', data.visibility.azCords[0].coord.az.to_string(sep=' ',precision=2) , ', LAT:', data.visibility.azCords[0].coord.alt.to_string(sep=' ',precision=2))
    print('')



def selectSupernovas(trs, maxMag, observationDay, deltaDays, minAlt=25):

    location = EarthLocation(lat=41.55*u.deg, lon=2.09*u.deg, height=224*u.m)
    
    fromDateTime = observationDay + timedelta(days=deltaDays)
    fromDate = fromDateTime.strftime('%Y-%m-%d')

    observationStart = observationDay.strftime('%Y-%m-%d') + "T20:00Z"
    
    time1 = Time(observationStart)
    time2 = time1 + timedelta(hours=8)

   
    print('Supernovae from: ', fromDate, ' to now. Magnitud <=', maxMag) #, 'for location ', location)
    print('')

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
                coord = SkyCoord(ra, decl, frame='icrs',
                                 unit=(u.hourangle, u.deg))
                
                
                visibility = getVisibility(location, coord, time1, time2, minAlt = 25)

                if (visibility.visible):

                    constellation = coord.get_constellation()
                    firstObserved = tr.contents[11].contents[0]
                    maxMagnitudeDate = tr.contents[10].contents[0]
                    maxMagnitude = tr.contents[9].contents[0]
                    type = tr.contents[7].contents[0]

                    link = 'https://www.rochesterastronomy.org/' + \
                        tr.contents[0].contents[0].get('href')[3:]
                    data = Supernova(date, mag, host, name, ra, decl, link,
                                     constellation, coord, firstObserved, maxMagnitude, maxMagnitudeDate, type, visibility)

                    supernovas.append(data)

    return supernovas

def getVisibility(astrosabadell, coord, time1, time2, minAlt = 25):
    
    visible = False
    loopTime = time1
    azVisibles = []
    while loopTime < time2:        
        altaz = coord.transform_to(AltAz(obstime=loopTime,location=astrosabadell))
        loopTime = loopTime + timedelta(hours=0.5)        
        if (altaz.alt.dms.d >= minAlt):            
            visible= True
            azVisibles.append(AxCordInTime(loopTime,altaz))

    azVisibles.sort(key=lambda x: x.time)    
       
    return Visibility(visible, azVisibles)


if len(sys.argv) > 3:
    raise ValueError('Usage: getsupernovae.py maxMag lastDays')

def main():

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

    mag = '18'
    deltaDays = -15

    if (len(sys.argv) == 3):
        deltaDays = (-1 * int(sys.argv[2]))
        mag = sys.argv[1]
    elif (len(sys.argv) == 2):
        mag = sys.argv[1]


    supernovas = selectSupernovas(trs, mag, datetime.now(), deltaDays)

    
    
    supernovas.sort(key=lambda x: x.visibility.azCords[-1].time)
    supernovas.sort(key=lambda x: x.visibility.azCords[0].time)
    
    for data in supernovas:
        printSupernova(data)
        print ('')

    
    #for data in supernovas:
    #    printSupernovaShort(data)

if __name__ == "__main__":
    main()
