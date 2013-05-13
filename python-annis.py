#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2, re, urllib, cgi, codecs
import cgitb

def getCorpora():
  """ get all corpora """
  xml = urllib2.urlopen('https://korpling.german.hu-berlin.de/annis3-service/"
                        + 'annis/query/corpora').read().decode("utf-8")
  regex = re.compile("<name>(.+?)</name>")
  return regex.findall(xml)

def getAnnotationLevelsAndValuesFromCorpus(corpus):
  """ from a corpus, get all annotation levels and values """
  annodict = {}
  url = str("https://korpling.german.hu-berlin.de/annis3-service/annis/query/" 
            + "corpora/" + corpus + "/annotations?fetchvalues=true")
  xml = urllib2.urlopen(url).read().decode("utf-8")
  regexAttr = re.compile("<annisAttribute>(.+?)</annisAttribute>", re.DOTALL)
  regexAttrName = re.compile("<name>(.+?)</name>")
  regexValues = re.compile("<value>(.+?)</value>")
  attributes = regexAttr.findall(xml)
  for attribute in attributes:
    name = regexAttrName.findall(attribute)[0]
    values = regexValues.findall(attribute)
    try:
      annodict[name].extend(values)
      annodict[name] = list(set(annodict[name]))
    except KeyError:
      annodict[name] = list(set(values))
  return annodict

def getAnnotationLevelsAndValuesFromCorpora(corpora):
  """ from a list of corpora, get all annotation levels and values """
  annodict = {}
  for corpus in corpora:
    url = str("https://korpling.german.hu-berlin.de/annis3-service/annis/query/"
              + "corpora/" + corpus + "/annotations?fetchvalues=true")
    xml = urllib2.urlopen(url).read().decode("utf-8")
    regexAttr = re.compile("<annisAttribute>(.+?)</annisAttribute>", re.DOTALL)
    regexAttrName = re.compile("<name>(.+?)</name>")
    regexValues = re.compile("<value>(.+?)</value>")
    attributes = regexAttr.findall(xml)
    for attribute in attributes:
      name = regexAttrName.findall(attribute)[0]
      values = regexValues.findall(attribute)
      try:
        annodict[name].extend(values)
        annodict[name] = list(set(annodict[name]))
      except KeyError:
        annodict[name] = list(set(values))
  return annodict

def getAnnotationLevelsFromCorpus(corpus):
  """ from a corpus, get all annotation levels """
  annolist = []
  url = str("https://korpling.german.hu-berlin.de/annis3-service/annis/query/"
            + "corpora/" + corpus + "/annotations?fetchvalues=false")
  xml = urllib2.urlopen(url).read().decode("utf-8")
  regexAttr = re.compile("<annisAttribute>(.+?)</annisAttribute>", re.DOTALL)
  regexAttrName = re.compile("<name>(.+?)</name>")
  attributes = regexAttr.findall(xml)
  for attribute in attributes:
    name = regexAttrName.findall(attribute)[0]
    if name not in annolist:
      annolist.append(name)
  return annolist

def getAnnotationLevelsFromCorpora(corpora):
  """ from a list of corpora, get all annotation levels  """
  annolist = []
  for corpus in corpora:
    url = str("https://korpling.german.hu-berlin.de/annis3-service/annis/query/"
              + "corpora/" + corpus + "/annotations?fetchvalues=false")
    xml = urllib2.urlopen(url).read().decode("utf-8")
    regexAttr = re.compile("<annisAttribute>(.+?)</annisAttribute>", re.DOTALL)
    regexAttrName = re.compile("<name>(.+?)</name>")
    attributes = regexAttr.findall(xml)
    for attribute in attributes:
      name = regexAttrName.findall(attribute)[0]
      if name not in annolist:
        annolist.append(name)
  return annodict

def aql(ps):
  numbers = u""
  statements = u""
  if len(ps) > 1:
    j = 1
    i = 1
    for p in ps:
      statements = statements + p + " &\n"
    while i <= len(ps) and j < ((len(ps) * 2) - 1):
      if j%2 == 1:
        numbers = numbers + "#" + str(i)
        i += 1
      if j%2 == 0:
        numbers = numbers + " .1,3 #" + str(i) + " &\n"
      j += 1
  if len(ps) == 1:
    statements = ps[0]
  return unicode(statements + numbers).strip("&\n").encode("utf-8")

def parseQueryTerm(d, dkey, a, akey):
  out = []
  try:
    checks = d[dkey]
    potentials = a[akey]
    for check in checkss:
      for potential in potentials:
        if potential.startswith(check):
          if potential not in out:
            out.append(posera)
    q = unicode(akey + "=/(" + "|".join(out) + ")/").encode("utf-8")
    return q
  except KeyError:
    return ""

def createAQL(query, zeit, raum, text):
  baseurl = "https://korpling.german.hu-berlin.de/annis3/instance-ddd#"
  aqlurl = ""
  if query:
    aqlurl = query.strip()
  if text:
    aqlurl = aqlurl + " & " + text.strip()
  if zeit:
    aqlurl = aqlurl + " & " + zeit.strip()
  if raum:
    aqlurl = aqlurl + " & " + raum.strip()
  aqlurl = "_q=" + aqlurl.encode("base64")
  aqlstr = query + text + zeit + raum
  corpora = getDDDCorpora()
  scope = unicode("&_c=" + unicode(",".join(corpora)).encode("base64") + 
          "&cl=7&cr=7&s=0&l=30&seg=txt")
  return aqlstr, unicode(baseurl.strip() + aqlurl + scope.strip())

def cgiFieldStorageToDict( fieldStorage ):
  params = {}
  for key in fieldStorage.keys():
    params[key] = fieldStorage.getlist(key)
#  params = params = {"query": ["lieber"], "text": ["alltag"]}
  return params

def form2aql(form, adict):
  d = cgiFieldStorageToDict(form)
  query = parseQueryTerm(d, dkey, adict, akey)
  return createAQL(query)


