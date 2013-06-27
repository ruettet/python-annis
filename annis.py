#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2, re, urllib, cgi, codecs, cgitb
from bs4 import BeautifulSoup

def getCorpora():
  """ get all corpora """
  xml = urllib2.urlopen('https://korpling.german.hu-berlin.de/annis3-service/'
                        + 'annis/query/corpora').read().decode("utf-8")
  soup = BeautifulSoup(xml)
  names = soup.find_all("name")
  out = []
  for name in names:
    out.append(name.string)
  return out

def getAnnotations(*args):
  if len(args) == 0:
    return getAnnotationsImpl(getCorpora(), [], "true")

  # underspecify corpora and levels || only specify values
  if len(args) == 1 and isinstance(args[0], bool):
    return getAnnotationsImpl(getCorpora(), [], str(args[0]).lower() )

  # underspecify levels and values || only specify corpora
  if len(args) == 1 and isinstance(args[0], str):
    return getAnnotationsImpl([args[0]], [], "true")
  if len(args) == 1 and isinstance(args[0], list):
    return getAnnotationsImpl(args[0], [], "true")

  # underspecify values || only specify corpora and levels
  if len(args) == 2 and isinstance(args[0], str) and isinstance(args[1], str):
    return getAnnotationsImpl([args[0]], [args[1]], "true")
  if len(args) == 2 and isinstance(args[0], list) and isinstance(args[1], str):
    return getAnnotationsImpl(args[0], [args[1]], "true")
  if len(args) == 2 and isinstance(args[0], str) and isinstance(args[1], list):
    return getAnnotationsImpl([args[0]], args[1], "true")
  if len(args) == 2 and isinstance(args[0], list) and isinstance(args[1], list):
    return getAnnotationsImpl(args[0], args[1], "true")

  # underspecify levels || only specify corpora and values
  if len(args) == 2 and isinstance(args[0], str) and isinstance(args[1], bool):
    return getAnnotationsImpl([args[0]], [], str(args[2]).lower() )
  if len(args) == 2 and isinstance(args[0], list) and isinstance(args[1], bool):
    return getAnnotationsImpl(args[0], [], str(args[2]).lower() )

  # underspecify anything || specify corpora, levels and values
  if len(args) == 3 and isinstance(args[0], str) and isinstance(args[1], str) and isinstance(args[2], bool):
    return getAnnotationsImpl([args[0]], [args[1]], str(args[2]).lower() )
  if len(args) == 3 and isinstance(args[0], list) and isinstance(args[1], str) and isinstance(args[2], bool):
    return getAnnotationsImpl(args[0], [args[1]], str(args[2]).lower() )
  if len(args) == 3 and isinstance(args[0], str) and isinstance(args[1], list) and isinstance(args[2], bool):
    return getAnnotationsImpl([args[0]], args[1], str(args[2]).lower() )
  if len(args) == 3 and isinstance(args[0], list) and isinstance(args[1], list) and isinstance(args[2], bool):
    return getAnnotationsImpl(args[0], args[1], str(args[2]).lower() )

  else:
    raise TypeError('I do not know how to deal with these parameter settings.')

def getAnnotationsImpl(corpora, levels, boolvalues):
  out = {}
  for corpus in corpora:
    if corpus in getCorpora():
      out[corpus] = {}
      url = str("https://korpling.german.hu-berlin.de/annis3-service/annis/query/" 
                + "corpora/" + corpus + "/annotations?fetchvalues=" + boolvalues)
      print "checking url", url
      xml = urllib2.urlopen(url).read().decode("utf-8")
      soup = BeautifulSoup(xml)
      attributes = soup.find_all("annisattribute")
      for attribute in attributes:
        name = attribute.find("name")
        if name != None:
          name = name.string
          if len(levels) == 0 or (name in levels or ":".join(name.split(":")[1:]) in levels):
            typ = attribute.find("type").string
            values_raw = attribute.find_all("value")
            values = []
            for value_raw in values_raw:
              values.append(value_raw.string)
            out[corpus][name] = {"type": typ, "values": values}
    else:
      raise TypeError('This is not a corpus.')
  return out

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
        numbers = numbers + " . #" + str(i) + " &\n"
      j += 1
  if len(ps) == 1:
    statements = ps[0]
  return unicode(statements + numbers).strip("&\n").encode("utf-8")

def parseQueryTerm(d, dkey, a, akey):
  out = []
  try:
    checks = d[dkey]
    potentials = a[akey]
    for check in checks:
      for potential in potentials:
        if potential.startswith(check):
          if potential not in out:
            out.append(posera)
    q = unicode(akey + "=/(" + "|".join(out) + ")/").encode("utf-8")
    return q
  except KeyError:
    return ""

def createURL(query, corpora, contextleft, contextright, hitsperpage, seg):
  """
    create aql url in base 64
    query: pure aql
    corpora: list of corpora names
    contextleft: integer with amount of tokens left
    contextright: integer with amount of tokens right
    hitsperpage: integer with amount of hits per annis page
    seg: default segmentation in kwic
  """

  baseurl = "https://korpling.german.hu-berlin.de/annis3/#"
  aqlurl = ""
  aqlurl = query.strip()
  aqlurl = "_q=" + aqlurl.encode("base64")
  scope = unicode("&_c=" + unicode(",".join(corpora)).encode("base64") + 
          "&cl=" + str(contextleft) + "&cr=" + str(contextright) + 
          "&s=0&l=" + str(hitsperpage) + "&seg=" + seg)
  return unicode(baseurl.strip() + aqlurl + scope.strip())

def cgiFieldStorageToDict( fieldStorage ):
  params = {}
  for key in fieldStorage.keys():
    params[key] = fieldStorage.getlist(key)
  return params

def form2aql(form, adict):
  d = cgiFieldStorageToDict(form)
  query = parseQueryTerm(d, dkey, adict, akey)
  return createURL(query, corpora)


