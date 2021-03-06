#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
#
# Quick script for updating the geoJson file used by the main map
#
import codecs
import json
import datetime
import odok as odokConnect
import common
config = common.loadJsonConfig()


def allGeoJson(filename="../site/AllFeatures.geo.json", source=None, full=True, debug=False):
    '''
    repetedly queries api for geojson of all features and
    outputs a file with the data
    '''
    out = codecs.open(filename, 'w', 'utf8')
    dbApi = odokConnect.OdokApi.setUpApi(user=config['odok_user'],
                                         site=config['odok_site'])

    features = dbApi.getGeoJson(full=full, source=source, debug=debug)

    print u'processing %d features' % len(features)

    outJson = {
        "type": "FeatureCollection",
        "features": features,
        "head": {
            "status": "1",
            "hits": len(features),
            "timestamp": datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
            }
        }
    out.write(json.dumps(outJson))  # , ensure_ascii=False))
    out.close()
    print '%s was created with %d features' % (filename, len(features))


if __name__ == "__main__":
    allGeoJson()
