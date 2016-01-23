# This version is sketchy, but usable for a demo.

import cgi

class WebObject: # The most generic class
    def __init__(*argt):
        args = list(argt)
        args.reverse()
        self = args.pop()
        self.empty = False
        if len(args) == 0:
           self.childnodes = []
        else: self.childnodes = [args[0]]
        self.parent = False
        self.attributes = [] # Object attributes that match HTML attributes
        self.elementName = ''
        self.mimeType = ''
        self.htmlID = ''
        self.htmlStyleClass = ''
    def attributeString(self): # A/V pairs for the start tag
        attString = ''
        for attName in self.attributes:
            attString += ' ' + attName +  '="'
            attString += str(self.__dict__[attName])
            attString += '"'
        return(attString)
    def html(self): # All objects can express themselves in html
        if isinstance(self,Block):
            fstr = "\n"
        else: fstr = ""
        if self.empty:
            return( fstr + '<' + self.elementName + self.attributeString() + '/>' + fstr)
        else:
            htmlString = fstr + '<' + self.elementName + self.attributeString() + '>'
            for child in self.children():
                htmlString += child.html()
            htmlString +=  '</' + self.elementName + '>' + fstr
            return(htmlString)
    def children(self):
        return self.childnodes
    def setParent(self, parent):
        self.parent = parent
    def getParent(self):
        return self.parent
    def grandparent(self):
        return((self.getParent()).getParent())
    def addChild(self,newchild): # Append a child node
        if self.empty: return False
        elif not(isinstance(newchild,WebObject)): return False
        else:
            self.childnodes.append(newchild)
            newchild.setParent(self)
            return True
    def __iadd__(self,other):
        self.addChild(other)
        return(self)

        
class WebPage(WebObject):
    def __init__(*argt):
        WebObject.__init__(*argt)
        args = list(argt)
        args.reverse()
        self = args.pop()
        self.elementName = 'html'
        self.mimeType = 'text/html'
        self.title = 'Untitled'
    def mimeType(self):
        return self.mimeType
    def publish(self):
        httpstring = 'Content-type: ' + self.mimeType + '\n\n'
        print httpstring
        print self.html()
    def setTitle(self, theTitle):
        self.title = theTitle

class TextNode(WebObject):
    def __init__(*argt):
        args = list(argt)
        args.reverse()
        self = args.pop()
        WebObject.__init__(self)
        if len(args) == 0:
            self.content = ''
        else: self.content = str(args[0])
    def setContent(self, contentstring):
        self.content = contentstring
    def getContent(self):
        return self.content
    def addContent(self, contentstring):
        self.content += contentstring
    def html(self): # Override the default HTML expression
        return self.content


class Block(WebObject): # paragraphs, lists, divisions, etc.
      def __init__(*argt):
          WebObject.__init__(*argt)

class Head(Block):
    def __init__(*argt):
        Block.__init__(*argt)
        args = list(argt)
        args.reverse()
        self = args.pop()
        self.elementName = 'head'

class Title(Block):
    def __init__(*argt):
        Block.__init__(*argt)
        args = list(argt)
        args.reverse()
        self = args.pop()
        self.elementName = 'title'
    def children(self):
       if isinstance(self.grandparent(),WebPage):
           titlestring = (self.grandparent()).title
       else: titlestring = "Untitled"
       tn = TextNode(titlestring)
       return([tn])


class Body(Block):
    def __init__(*argt):
        Block.__init__(*argt)
        args = list(argt)
        args.reverse()
        self = args.pop()
        self.elementName = 'body'

class Header1(Block):
    def __init__(*argt):
        Block.__init__(*argt)
        args = list(argt)
        args.reverse()
        self = args.pop()
        self.elementName = 'h1'

class Header2(Block):
    def __init__(*argt):
        Block.__init__(*argt)
        args = list(argt)
        args.reverse()
        self = args.pop()
        self.elementName = 'h2'

class Header3(Block):
    def __init__(*argt):
        Block.__init__(*argt)
        args = list(argt)
        args.reverse()
        self = args.pop()
        self.elementName = 'h3'

class Paragraph(Block):
    def __init__(*argt):
        Block.__init__(*argt)
        args = list(argt)
        args.reverse()
        self = args.pop()
        self.elementName = 'p'

class Division(Block):
    def __init__(*argt):
        Block.__init__(*argt)
        args = list(argt)
        args.reverse()
        self = args.pop()
        self.elementName = 'div'

class UnorderedList(Block):
    def __init__(*argt):
        Block.__init__(*argt)
        args = list(argt)
        args.reverse()
        self = args.pop()
        self.elementName = 'ul'

class OrderedList(Block):
    def __init__(*argt):
        Block.__init__(*argt)
        args = list(argt)
        args.reverse()
        self = args.pop()
        self.elementName = 'ol'

class ListItem(Block):
    def __init__(*argt):
        Block.__init__(*argt)
        args = list(argt)
        args.reverse()
        self = args.pop()
        self.elementName = 'li'

class DescriptionList(Block):
    def __init__(*argt):
        Block.__init__(*argt)
        args = list(argt)
        args.reverse()
        self = args.pop()
        self.elementName = 'dl'


class DescriptionTerm(Block):
    def __init__(*argt):
        Block.__init__(*argt)
        args = list(argt)
        args.reverse()
        self = args.pop()
        self.elementName = 'dt'

class Ddescription(Block):
    def __init__(*argt):
        Block.__init__(*argt)
        args = list(argt)
        args.reverse()
        self = args.pop()
        self.elementName = 'dd'

class Inline(WebObject): # spanning elements like <em>
    def __init__(*argt):
        WebObject.__init__(*argt)

class Anchor(Inline):
    def __init__(*argt):
        args = list(argt)
        args.reverse()
        self = args.pop()
        Inline.__init__(self)
        if len(args) == 0:
           self.href = ''
        else: self.href = str(args[0])
        self.attributes.append('href')
        self.elementName = 'a'


class WebForm(WebObject):
    def __init__(self):
        WebObject.__init__(self)
        self.elementName = 'form'
        self.attributes.append('action')
        self.attributes.append('method')
        self.action = '' # post or get
        self.method = '' # uri for the program to process
        self.formdata = False
    def setAction(self,action):
        self.action = action
    def setMethod(self,method):
        self.method = method
    def collectData(self): # But what if there's more than one form?
        self.formdata = cgi.FieldStorage()
    def hasData(self): # Have I already been filled out?
        self.collectData()
        if (self.formdata.keys() != []): return True
        else: return False
    def hasKey(self,key):
        if self.formdata.has_key(key): return True
        else: return False
    def formValue(self, key):
        return str(self.formdata[key].value)

class FormObject(WebObject): # Things that live on web forms
    def __init__(self):
        WebObject.__init__(self)
    def myForm(self):
        foundmyform  = False
        lookingat = self
        while not(foundmyform):
            if isinstance(lookingat,WebForm): return lookingat
            else: lookingat = lookingat.getParent()
            if lookingat == False: return False
    def myValue(self):
        if self.myForm():
            if self.myForm().hasData():
                if self.myForm().hasKey(self.name):
                    return self.myForm().formValue(self.name)
                else: return ''
            else: return ''
        else: return ''

class Input(FormObject): # Generic form input
    def __init__(self):
        FormObject.__init__(self)
        self.type = ''
        self.attributes.append('type')
        self.name = ''
        self.attributes.append('name')
        self.value = ''
        self.checked = False
        self.empty = True
        self.elementName = 'input'
    def setName(self, nameString):
        self.name = nameString

class TextBox(Input):
    def __init__(self,name):
        Input.__init__(self)
        self.type = 'text'
        self.setName(name)
    def setSize(self,size):
        self.size = size
        self.attributes.append('size')
    def setMaxLength(self,maxlength):
        self.maxlength = maxlength
        self.attributes.append('maxlength')

class SubmitButton(Input):
    def __init__(self):
        Input.__init__(self)
        self.type = 'submit'
        self.name = 'submit'
        self.value = 'submit'
        self.attributes.append('value')
        
class Label(FormObject):
    def __init__(self):
        FormObject.__init__(self)
        self.elementName = 'label'

class Select(FormObject): # not ready yet
    def __init__(self):
        FormObject.__init__(self)

class TextArea(FormObject): # not ready yet
    def __init__(self):
        FormObject.__init__(self)

class FieldSet(FormObject): # not ready yet
    def __init__(self):
        FormObject.__init__(self)

class Button(FormObject): # not ready yet
    def __init__(self):
        FormObject.__init__(self)

