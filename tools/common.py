# -*- coding: UTF-8  -*-
#
# Methods comonly shared by the tool scripts
#
import codecs
import os
import operator
import urllib, urllib2
from json import loads

def openFile(filename):
    '''opens a given file (utf-8) and returns the lines'''
    fin = codecs.open(filename, 'r', 'utf-8')
    txt = fin.read()
    fin.close()
    lines = txt.split('\n')
    lines.pop()
    return lines

def sortedDict(ddict):
    '''turns a dict into a sorted list'''
    sorted_ddict = sorted(ddict.iteritems(), key=operator.itemgetter(1), reverse=True)
    return sorted_ddict

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
    
def extractName(entry):
    '''If field includes square brackets then this ignores any part of name field which lies outside
       If field contains semicolons then treats thes as separate objects'''
    if u'[' in entry:
        pos1 = entry.find(u'[')
        pos2 = entry.find(u']')
        entry = entry[pos1+1:pos2]
    return entry.split(u';')

def extractNameParts(name):
    '''Tries to separate a name into first and second name.'''
    #Algorithm. If one "," in names then asume lName, fName.
    #Else asume last name is the last word of the name.
    #Plain name returned if all else fails
    if u',' in name:
        parts = name.split(u',')
        if len(parts)==2:
            return u'%s;%s' %(parts[1].strip(),parts[0].strip())
    if u' ' in name:
        parts = name.split(u' ')
        lName = parts[-1].strip()
        fName = name[:-len(lName)].strip()
        return u'%s;%s' %(fName,lName)
    return name

def getWikidata(article, verbose=False):
    '''returns the wikidata enitity id of an article'''
    wikiurl = u'https://www.wikidata.org'
    apiurl = '%s/w/api.php' %wikiurl
    urlbase = '%s?action=wbgetentities&format=json&sites=svwiki&props=info&titles=' %apiurl
    url = urlbase+urllib.quote(article.encode('utf-8'))
    req = urllib2.urlopen(url)
    j = loads(req.read())
    req.close()
    if (j['success'] == 1) or (not 'warnings' in j.keys()) or (not len(j['entities'])==1):
        if j['entities'].keys()[0] == u'-1':
            if verbose: print 'no entry'
            return (None, 'no entry')
        else:
            if verbose: print u'Found the wikidata entry at %s' %j['entities'].keys()[0]
            return (j['entities'].keys()[0],'')
    else:
        error = 'success: %s, warnings: %s, entries: %d' %(j['success'], 'warnings' in j.keys(), len(j['entities']))
        if verbose: print error
        return (None, error)

def getManyWikidata(articles, dDict, verbose=False):
    '''returns the wikidata enitity ids of a list of articles'''
    if not isinstance(articles,list):
        print '"getManyWikidata" requiresa list of articles. for individual articles use "getWikidata" instead'
        return None
    #do an upper limit check (max 50 titles per request allowed)
    if len(articles) > 50:
        i=0
        while True:
            getManyWikidata(articles[i:i+50], dDict, verbose=verbose)
            i=i+50
            if i+50 > len(articles):
                getManyWikidata(articles[i:], dDict, verbose=verbose)
                break
    elif len(articles) > 0:
        wikiurl = u'https://www.wikidata.org'
        apiurl = '%s/w/api.php' %wikiurl
        urlbase = '%s?action=wbgetentities&format=json&sites=svwiki&props=info|sitelinks&titles=' %apiurl
        url = urlbase+urllib.quote('|'.join(articles).encode('utf-8'))
        if verbose: print url
        req = urllib2.urlopen(url)
        j = loads(req.read())
        req.close()
        if (j['success'] == 1) or (not 'warnings' in j.keys()) or (not len(j['entities'])==1):
            for k, v in j['entities'].iteritems():
                if k.startswith(u'q'):
                    title = v['sitelinks']['svwiki']['title']
                    dDict[title] = k
                    if verbose: print u'%s: Found the wikidata entry at %s' %(title,k)
                else:
                    title = v['title']
                    dDict[title] = None
                    if verbose: print '%s: no entry' %title
        else:
            error = 'success: %s, warnings: %s, entries: %d' %(j['success'], 'warnings' in j.keys(), len(j['entities']))
            if verbose: print error
            return (None, error)

def getManyArticles(wikidata, dDict, verbose=False):
    '''returns the articles of a list of wikidata enitity ids'''
    if not isinstance(wikidata,list):
        print '"getManyArticles" requiresa list of articles. for individual wikidata entities use "getArticles" instead'
        return None
    #do an upper limit check (max 50 titles per request allowed)
    if len(wikidata) > 50:
        i=0
        while True:
            getManyArticles(wikidata[i:i+50], dDict, verbose=verbose)
            i=i+50
            if i+50 > len(wikidata):
                getManyArticles(wikidata[i:], dDict, verbose=verbose)
                break
    elif len(wikidata) > 0:
        wikiurl = u'https://www.wikidata.org'
        apiurl = '%s/w/api.php' %wikiurl
        urlbase = '%s?action=wbgetentities&format=json&props=sitelinks&ids=' %apiurl
        url = urlbase+urllib.quote('|'.join(wikidata).encode('utf-8'))
        if verbose: print url
        req = urllib2.urlopen(url)
        j = loads(req.read())
        req.close()
        if (j['success'] == 1) or (not 'warnings' in j.keys()) or (not len(j['entities'])==1):
            for k, v in j['entities'].iteritems():
                if 'svwiki' in v['sitelinks'].keys():
                    title = v['sitelinks']['svwiki']['title']
                    dDict[k] = title
                    if verbose: print u'%s: Found the title at %s' %(k,title)
                else:
                    dDict[k] = None
                    if verbose: print '%s: no entry' %k
        else:
            error = 'success: %s, warnings: %s, entries: %d' %(j['success'], 'warnings' in j.keys(), len(j['entities']))
            if verbose: print error
            return (None, error)

def findUnit(contents, start, end, brackets=None):
    '''
    Method for isolating an object in a string. Will not work with either start or end using the ¤ symbol
    @input: 
        * content: the string to look at
        * start: the substring indicateing the start of the object
        * end: the substring indicating the end of the object
        * brackets: a dict of brackets used which must match within the object
    @output:
        the-object, lead-in-to-object, the-remainder-of-the-string
        OR None,None if an error
        OR '','' if no object is found
    '''
    if start in contents:
        uStart = contents.find(start) + len(start)
        uEnd = contents.find(end,uStart)
        if brackets:
            for bStart,bEnd in brackets.iteritems():
                dummy=u'¤'*len(bEnd)
                diff = contents[uStart:uEnd].count(bStart) - contents[uStart:uEnd].count(bEnd)
                if diff<0:
                    print 'Negative bracket missmatch for: %s <--> %s' %(bStart,bEnd)
                    return None, None, None
                i=0
                while(diff >0):
                    i=i+1
                    uEnd = contents.replace(bEnd,dummy,i).find(end,uStart)
                    if uEnd < 0:
                        print 'Positive (final) bracket missmatch for: %s <--> %s' %(bStart,bEnd)
                        return None, None, None
                    diff = contents[uStart:uEnd].count(bStart) - contents[uStart:uEnd].count(bEnd)
        unit = contents[uStart:uEnd]
        lead_in = contents[:uStart-len(start)]
        remainder = contents[uEnd+len(end):]
        return (unit, remainder, lead_in)
    else:
        return '','',''

def extractLink(text):
    '''
    Given wikitiext this checks for the first wikilink
    Limitations: Only identifies the first wikilink
    @output: (plain_text, link)
    '''
    if not u'[[' in text: return (text, '')
    interior, dummy, dummy = findUnit(text, u'[[', u']]')
    wikilink = u'[['+interior+u']]'
    pos = text.find(wikilink)
    pre = text[:pos]
    post = text[pos+len(wikilink):]
    center=''
    link=''
    
    #determine which type of link we are dealing with see meta:Help:Links#Wikilinks for details
    if not u'|' in interior: #[[ab]] -> ('ab', 'ab')
        center = interior
        link = interior.strip()
    else:
        pos = interior.find(u'|')
        link = interior[:pos]
        center = interior[pos+1:]
        if len(link) == 0: #[[|ab]] -> ('ab', 'ab')
            link = center
        elif len(center)>0:  #[[a|b]] -> ('b', 'a')
            pass
        else:
            center=link
            if u':' in center:  # [[a:b|]] -> ('b', 'a:b')
                center = center[center.find(u':')+1:]
            if u', ' in center: # [[a, b|]] -> ('a', 'a, b')
                center = center.split(u', ')[0]
            if u'(' in center: #[[a (b)|]] -> ('a', 'a (b)')
                pos = center.find(u'(')
                if u')' in center[pos:]:
                    center=center[:pos]
                    if center.endswith(' '): # the first space separating text and bracket is ignored
                        center = center[:-1]
    return ((pre+center+post).strip(), link.strip())

def extractAllLinks(text):
    '''
    Given wikitiext this checks for any wikilinks
    @output: (plain_text, list of link)
    '''
    wikilinks=[]
    while '[[' in text:
        text, link = extractLink(text)
        wikilinks.append(link)
    return text, wikilinks

def latLonFromCoord(coord):
    '''
    returns lat, lon as decimals based on string using the Coord-template
    @output (lat,lon) as float
    '''
    if not (coord.startswith(u'{{Coord|') or coord.startswith(u'{{coord|')): print 'incorrectly formated coordinate: %s' %coord; return None
    p = coord.split('|')
    if len(p) >= 9:
        lat_d, lat_m, lat_s, lat_sign = float(p[1].strip()), float(p[2].strip()), float(p[3].strip()), p[4]
        lon_d, lon_m, lon_s, lon_sign = float(p[5].strip()), float(p[6].strip()), float(p[7].strip()), p[8]
        lat = lat_d + lat_m/60 + lat_s/3600
        lon = lon_d + lon_m/60 + lon_s/3600
    elif len(p) >= 5:
        lat, lat_sign = float(p[1].strip()), p[2]
        lon, lon_sign = float(p[3].strip()), p[4]
    if lat_sign == u'N': lat_sign=1
    elif lat_sign == u'S': lat_sign=-1
    else: print 'incorrectly formated coordinate: %s' %coord; return None
    if lon_sign == u'E': lon_sign=1
    elif lon_sign == u'W': lon_sign=-1
    else: print 'incorrectly formated coordinate: %s' %coord; return None
    lat = lat_sign*lat
    lon = lon_sign*lon
    return (lat,lon)
#done
