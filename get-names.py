#!/usr/bin/python
#

from astroquery.simbad import Simbad
from astroquery.vizier import Vizier

# result_table = Simbad.query_objectids("m31")
result_table = Vizier.query_object("m31")
# result_table = Simbad.query_object("m31")

print(result_table)
