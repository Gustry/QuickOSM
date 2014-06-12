'''
Created on 4 juin 2014

@author: etienne
'''

import urllib2
import urllib
import re
import tempfile

class ConnexionOAPI:

    def __init__(self,url="http://overpass-api.de/api/interpreter", output = None):
        self.__url = url

        if output not in (None, "json","xml"):
            raise Exception, "Output not available"
        self.__output = output
        
    def query(self,req):
        urlQuery = self.__url
        
        if self.__output:
            req = re.sub(r'output="[a-z]*','output="'+self.__output+'"', req)
            req = re.sub(r'out:[a-z]*','out:'+self.__output, req)

        req = req.encode("utf-8")
        queryString = urllib.urlencode({'data':req})
        print queryString
        print  urlQuery

        try:
            return urllib2.urlopen(url=urlQuery, data=queryString).read()
        except urllib2.HTTPError as e:
            if e.code == 400:
                raise Exception, "Bad request OverpassAPI"
            
    def getFileFromQuery(self,req):
        req = self.query(req)
        '''Creation d'un fichier OSM temporaire'''
        tf = tempfile.NamedTemporaryFile(delete=False,suffix=".osm")
        tf.write(req)
        namefile = tf.name
        tf.flush()
        tf.close()
        return namefile