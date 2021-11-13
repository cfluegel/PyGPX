import xml
import xml.etree.ElementTree as ET 
import os.path
from pathlib import Path


class GeocachingLogEntry:
    _FoundDate = None
    _FoundBy = None
    _Comment = None 
    _Type = None 

    def __init__(self, xmltree = None):
        if not xmltree:
            raise Exception("No XML data given")
        
        if isinstance(xmltree, str):
            tree = ET.fromstring(xmltree)
            root = tree.getroot()
        elif isinstance(xmltree, xml.etree.ElementTree.Element):
            tree = xmltree 
            root = xmltree

        self._FoundDate = root.find("{http://www.groundspeak.com/cache/1/0}date").text
        self._FoundBy = root.find("{http://www.groundspeak.com/cache/1/0}finder").text
        self._Comment = root.find('{http://www.groundspeak.com/cache/1/0}text').text
        self._Type = root.find('{http://www.groundspeak.com/cache/1/0}type').text

    @property 
    def Comment(self):
        return self._Comment

    @property
    def FoundBy(self):
        return self._FoundBy
    
    @property
    def FoundOn(self):
        return self._FoundDate
    
    @property 
    def CommentType(self):
        return self._Type

    def __str__(self):
        return f"{self._FoundBy} found the cache on {self._FoundDate}"

class GeocachingCache:
    _GCID = None
    _Name = None
    _Type = None
    _URL = None
    _Difficulty = 0 
    _Terrain = 0
    _Location = {
        "Country": None,
        "Coordinates": {
            "lat" :0.00, 
            "long":0.00
        }
    }
    _Owner = None
    _ContainerSize = None 
    _ShortDescription = None
    _LongDescription = None

    _Logs = []

    def __init__(self, xmltree = None):
        if not xmltree:
            raise Exception("No XML data given")
        
        if isinstance(xmltree, str):
            tree = ET.fromstring(xmltree)
            root = tree.getroot()
        elif isinstance(xmltree, xml.etree.ElementTree.Element):
            tree = xmltree 
            root = xmltree

        self._URL = root.find('{http://www.topografix.com/GPX/1/0}url').text
        self._GCID = root.find('{http://www.topografix.com/GPX/1/0}name').text
        
        groundspeak = root.find('{http://www.groundspeak.com/cache/1/0}cache')
        self._Type = groundspeak.find('{http://www.groundspeak.com/cache/1/0}type').text
        self._Difficulty = groundspeak.find('{http://www.groundspeak.com/cache/1/0}difficulty').text
        self._Terrain = groundspeak.find('{http://www.groundspeak.com/cache/1/0}terrain').text
        self._Location["Country"] = groundspeak.find('{http://www.groundspeak.com/cache/1/0}country').text
        self._Location["Coordinates"]["lat"] = root.attrib['lat']
        self._Location["Coordinates"]["long"] = root.attrib['lon']
        self._Owner = groundspeak.find('{http://www.groundspeak.com/cache/1/0}owner').text
        self._Name =  groundspeak.find('{http://www.groundspeak.com/cache/1/0}name').text
        self._ShortDescription = groundspeak.find('{http://www.groundspeak.com/cache/1/0}short_description').text
        self._LongDescription = groundspeak.find('{http://www.groundspeak.com/cache/1/0}long_description').text
        self._ContainerSize = groundspeak.find('{http://www.groundspeak.com/cache/1/0}container').text

        for logentry in groundspeak.find('{http://www.groundspeak.com/cache/1/0}logs'):
            newlogentry = GeocachingLogEntry(logentry)
            self._Logs.append(newlogentry)

    def __str__(self):
        if self._Name: 
            return f"{self._Name}    by   {self._Owner} (T{self._Terrain}/D{self._Difficulty})"
        else:
            return f"{self._Owner} (T{self._Terrain}/D{self._Difficulty})"

    def GetLogs(self):
        return self._Logs

    @property
    def Found(self):
        return self._FoundIt
    @property
    def Country(self):
        return self._Location["Country"]
    @property
    def GPSCoordinates(self):
        return (self._Location["Coodinates"]["lat"],self._Location["Coodinates"]["long"])
    @property
    def ID(self):
        return self._GCID
    @property
    def name(self):
        return self._Name
    @property
    def Difficulty(self):
        return self._Difficulty
    @property
    def Terrain(self):
        return self._Terrain
    @property
    def ShortDescription(self):
        return self._ShortDescription
    @property
    def LongDescription(self):
        return self._LongDescription

class GeocachingPocketQuery:
    _tree = None
    _root = None

    _GPXExportedOn = None
    _GeocachingName = None

    _Caches = []

    def __init__(self, GeocachingName=None):
        if not GeocachingName:
            raise Exception("No GC Name provided!")
        
        self._GeocachingName = GeocachingName

    def ReadFile(self, FName=None):
        if not FName:
            raise Exception("No filename was given")
    
        if not Path(FName).is_file():
            raise Exception("Filename does not point to a file")

        self._tree = ET.parse(FName)

        self._parseData()

    def ReadStream(self, Data=None):
        if isinstance(Data, str):
            raise Exception("Type Error")
        
        self._tree = ET.fromstring(Data)

        self._parseData()

    def _parseData(self):
        self._root = self._tree.getroot()
        self._GPXExportedOn = self._root.find('{http://www.topografix.com/GPX/1/0}time').text

        for cache in self._root.findall('{http://www.topografix.com/GPX/1/0}wpt'):
            newcache = GeocachingCache(cache)
            self._Caches.append(newcache)

    def GetAllFindes(self):
        return self._Caches

    def GetMyFinds(self):
        MyFinds = []
        for Cache in self._Caches:
            if self._GeocachingName == Cache.GetLogs()[0].FoundBy:
                MyFinds.append(Cache)
        return MyFinds
        
    def __str__(self):
        return f"Exported on {self._GPXExportedOn}" 

if __name__ == "__main__":
    GPX = GeocachingPocketQuery("discordia23")
    GPX.ReadFile("1489306.gpx")
    # print(GPX)
    for c in GPX.GetMyFinds():
        print(c)

    import sys
    sys.exit(0)


    ## FRom here there is only maddness. 
    # Leftover "getting used to xml parsing" script fragments 
    testtree = ET.parse("1489306.gpx")
    root = testtree.getroot()

    for cache in root.findall('{http://www.topografix.com/GPX/1/0}wpt'):
        # print(cache.attrib["lat"], cache.attrib["lon"])
        gs_info = cache.find('{http://www.groundspeak.com/cache/1/0}cache')
        logs = gs_info.find('{http://www.groundspeak.com/cache/1/0}logs')
        for child in logs:
            for cchild in child:
                pass
                # print(cchild)



