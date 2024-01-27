#!/usr/bin/python
# Check supernova data
#

import urllib.request
import urllib.parse
import urllib.error
from bs4 import BeautifulSoup
from astropy.coordinates import SkyCoord
import ssl
from datetime import datetime, timedelta
import sys
import astropy.units as u




def printInfo(ra, decl, data):
    print('-------------------------------------------------')
    print('  RA:', ra, ', DECL.', decl, ' is in constellation', data)
    print('-------------------------------------------------')


def getConstellation(ra, decl):

    
    coord = SkyCoord(ra, decl, frame='icrs', unit=(u.hourangle, u.deg))
    constellation = coord.get_constellation()
    return constellation


if len(sys.argv) != 3:
    raise ValueError('Usage: getconstellation.py ra dr')


ra= sys.argv[1]
decl = sys.argv[2]

printInfo(ra, decl, getConstellation(ra, decl))
