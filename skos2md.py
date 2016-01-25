#!/usr/bin/python

import string, sys, time, re, string
from rdflib import *


def sourceURI(uristring):
  httprx = re.compile(r"http:")
  isbnrx = re.compile(r"urn:isbn:([0-9X]+)")
  imatch = re.search(isbnrx,uristring)
  hmatch = re.search(httprx,uristring)
  if hmatch: return(uristring)
  elif imatch:
     isbn = imatch.group(1)
     return("http://books.google.com/books?isbn=" + isbn)
  else: return("")

def webLink(uristring):
   mylink = Anchor(uristring)
   mylink += TextNode(uristring)
   return(mylink)

def stripnl(instring):
   return(string.replace(instring, r"\n", " "))


def md(etype):
  mdhash = {'Header1': '# ', 'Header2': '## ', 'Header3': '### ', 'Ddescription': ':    ', 'uitem': '- '}
  return(mdhash[etype])

def mlink(id,anchor):
  return("[" + anchor + "](" + id + ")")
 
def graph2md(mygraph):
  docstring = ""
  for concept in mygraph.subjects(RDF.type, skos.Concept):
    docstring += md('Header1') + mygraph.value(concept, skos.prefLabel) + '\n\n'
    docstring += md('Header2') + mlink(concept,concept) + '\n\n'
    defptr = mygraph.value(concept, skos.definition)
    mydef = stripnl(mygraph.value(defptr,RDF.value))
    for source in mygraph.objects(defptr,dcterms.references):
       myanchor = mlink(sourceURI(source),source)
       myanchor += " "
       mydef += myanchor
    docstring += md('Header3') + "In Scheme" + '\n\n'
    schemeURI = mygraph.value(concept,skos.inScheme)
    docstring += mlink(schemeURI,schemeURI) + '\n\n'
    docstring += md('Header3') + "Definition" + '\n\n'
    docstring += mydef + '\n\n'

    for (label,prop) in [("Broader",skos.broader), ("Narrower",skos.narrower), ("Related", skos.related)]:
       if (concept, prop, None) in mygraph:
           mylist = md('Header3') + label + '\n'
           for buri in mygraph.objects(concept,prop):
               mylist += md('uitem') + mlink(buri,buri) + '\n'
           docstring += mylist + '\n'
    
  return(docstring)



def is_uri(thing):                    # Boolean test if rdf term is a URI ref
  return(type(thing) == URIRef)

def is_literal(thing):                # Boolean test if rdf term is an rdf literal
  return(type(thing) == Literal)

def is_bnode(thing):
  return(type(thing) == BNode)

def setupgraph(mygraph):
  mygraph.bind("skos","http://www.w3.org/2004/02/skos/core#")
  mygraph.bind("foaf","http://xmlns.com/foaf/0.1/")
  mygraph.bind("dc","http://purl.org/dc/elements/1.1/")
  mygraph.bind("dcterms","http://purl.org/dc/terms/")
  mygraph.bind("xsd","http://www.w3.org/2001/XMLSchema#")
  mygraph.bind("sam","http://cirssweb.lis.illinois.edu/DataCon/SAM/")
  mygraph.bind("org","http://www.w3.org/ns/org#")


def getgraph(thegraph,resource):
  newgraph = ConjunctiveGraph()
  setupgraph(newgraph)
  for (p,o) in thegraph.predicate_objects(resource):
    newgraph.add((resource,p,o))
    if (is_bnode(o)):
       for (x,y) in thegraph.predicate_objects(o):
         newgraph.add((o,x,y))
         if (is_bnode(y)):
           for (t,u) in thegraph.predicate_objects(y):
             newgraph.add((y,t,u))
       for (s,p) in thegraph.subject_predicates(o):
         newgraph.add((s,p,o))
  for (s,p) in thegraph.subject_predicates(resource):
    newgraph.add((s,p,resource))
  return(newgraph)




provig = Namespace("http://purl.org/RDA-Provenance/Concepts/")
skos = Namespace("http://www.w3.org/2004/02/skos/core#")
foaf = Namespace("http://xmlns.com/foaf/0.1/")
dc = Namespace("http://purl.org/dc/elements/1.1/")
dcterms = Namespace("http://purl.org/dc/terms/")
xsd = Namespace("http://www.w3.org/2001/XMLSchema#")
org = Namespace("http://www.w3.org/ns/org#")
sam = Namespace("http://cirssweb.lis.illinois.edu/DataCon/SAM/")

mygraph = ConjunctiveGraph()
mygraph.parse("glos4.ttl",format="n3")



l1 = ['dbDataProvenance','eScienceProvenance','experimentalProvenance','identity']
l2 = ['provenance','provenancePrinciple','scientificWorkflow','workflow','workflowManagementSystem']

for r in (l1 + l2):
  s = provig[r] 
  outputgraph = getgraph(mygraph,s)
  outputpage = graph2md(outputgraph)
  filename = r + ".md"
  myfile = open(filename, "wb")
  myfile.write(outputpage)
  myfile.close



