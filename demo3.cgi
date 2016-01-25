#!/usr/bin/python

import  cgi, smtplib, string, sys, time, re, string
from rdflib import *
from webobjects4 import *

def notfound():
  print "Content-type: text/html\n\n"
  print '<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">'
  print '<html><head>'
  print '<title>404 Not Found</title>'
  print '</head><body>'
  print '<h1>Not Found</h1>'
  print '<p>The requested URL was not found on this server.</p>'
  print '<hr>'
  print '</body></html>'


def simplePage():
  mypage = WebPage()
  myhead = Head()
  mybody = Body()
  mypage += myhead
  mypage += mybody
  tnode1 = TextNode()
  tnode1.setContent("Hello World")
  para1 = Paragraph()
  para1 += tnode1
  mybody += para1
  return(mypage)

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

def graph2html1(mygraph):
  mypage = WebPage()
  myhead = Head()
  mybody = Body()
  mytitle = Title()
  mypage += myhead
  mypage += mybody
  myhead += mytitle
  mypage.setTitle("SKOS Concept Description")
  for concept in mygraph.subjects(RDF.type, skos.Concept):
    mybody += Header1(TextNode(mygraph.value(concept, skos.prefLabel)))
    mybody += Header2(TextNode(concept))
    defptr = mygraph.value(concept, skos.definition)
    mydef = Ddescription(TextNode(stripnl(mygraph.value(defptr,RDF.value))))
    for source in mygraph.objects(defptr,dcterms.references):
       myanchor = Anchor(sourceURI(source))
       myanchor += TextNode(source)
       mydef += TextNode(" ")
       mydef += myanchor
    mylist = DescriptionList()
    mylist += DescriptionTerm(TextNode("In Scheme"))
    mylist += Ddescription(webLink(mygraph.value(concept,skos.inScheme)))

    mylist += DescriptionTerm(TextNode("Definition"))
    mylist += Ddescription(mydef)

    for (label,prop) in [("Broader",skos.broader), ("Narrower",skos.narrower), ("Related", skos.related), ("Editorial page",skos.editorialNote)]:
       if (concept, prop, None) in mygraph:
           mylist += DescriptionTerm(TextNode(label))
           ulist = UnorderedList()
           mydd = Ddescription(ulist) 
           for buri in mygraph.objects(concept,prop):
               ulist += ListItem(webLink(buri))
           mylist += mydd

    mybody += mylist
    
  return(mypage)

def graph2html0(mygraph):
  if (None, RDF.type, skos.ConceptScheme) in mygraph:
    return(graph2html2(mygraph))
  else:
    return(graph2html1(mygraph))

def graph2html2(mygraph):
  mypage = WebPage()
  myhead = Head()
  mybody = Body()
  mytitle = Title()
  mypage += myhead
  mypage += mybody
  myhead += mytitle
  mypage.setTitle("SKOS Concept Scheme")
  for scheme in mygraph.subjects(RDF.type, skos.ConceptScheme):
    mybody += Header1(TextNode(mygraph.value(scheme, dc['title'])))
    mybody += Header2(TextNode(scheme))
    mylist = DescriptionList()
    for (label,prop) in [("Date",dc.date)]:
       if (scheme, prop, None) in mygraph:
           dstring = mygraph.value(scheme,prop)
           mylist += DescriptionTerm(TextNode(label))
           mylist += Ddescription(TextNode(dstring))
    mybody += mylist
    newlist = UnorderedList()
    for concept in sorted(mygraph.subjects(skos.inScheme, scheme)):
       newlist += ListItem(webLink(concept))
    mybody += newlist
  return(mypage)



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

inputform = cgi.FieldStorage()

if ('resource' in inputform.keys()) and ('format' in inputform.keys()):
 r = inputform['resource'].value
 s = provig[r] 
 f = inputform['format'].value
 outputgraph = getgraph(mygraph,s)
 outputpage = graph2html0(outputgraph)
 if f == 'html':
   outputpage.publish()
 elif f == 'rdf':
   print "Content-type: application/rdf+xml\n"
   print outputgraph.serialize(format="pretty-xml")   
 else: notfound()
else: notfound()





#r = 'eScienceProvenance'





# webpage1 = simplePage()

# print outputgraph.serialize(format="pretty-xml")

#  webpage1.publish()

# if ('resource' in inputform.keys()):
# print("Content-Type: text/plain\n\n")
# print("Resource: " + inputform['resource'].value)
 
# else: notfound()
  

# http://cirssweb.lis.illinois.edu/DataCon/test2.cgi?resource=foo

