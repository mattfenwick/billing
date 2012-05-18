
import json


class Event(object):

    def __init__(self, time, isStart):
        self.time = time
        self.isStart = isStart



class Experiment(object):

    def __init__(self, spectrometer, path): # do I need spectrometer and path?
        self.spectrometer = spectrometer
        self.path = path
        self.events = []

    def addEvent(self, event):
        assert type(event) == 'Event' # probably doesn't run/compile
        self.events.append(event)



class NmrUsage(object):

    def __init__(self, description):
        self.experiments = {}
        self.description = description

#    def addExperiment(self, spectrometer, path):
#        pass

    def addEvent(self, spectrometer, path, event):
        key = (spectrometer, path)
        if not self.experiments.has_key(key):
            self.experiments[key] = Experiment(spectrometer, path)
        exp = self.experiments[key]
        exp.addEvent(event)


####################################


class Tree(object):
    
    def __init__(self, value):
        self.value = value
        self.children = {}

    def addChild(self, key, child):
        if self.children.has_key(key):
            raise ValueError("already have key <%s>" % key)
        if type(child) != type(self):
            raise ValueError("bad type for Tree child: <%s>" % str(type(child)))
        self.children[key] = child

    def fmap(self, f):
        newTree = Tree(f(self.value))
        for (key, treeNode) in self.children.iteritems():
            newTree.addChild(key, treeNode.fmap(f))
        return newTree

    def toJSON(self):
        cs = {}
        for (k, v) in self.children.iteritems():
            cs[k] = v.toJSON()
        return {'value': self.value, 'children': cs}
 
    @classmethod
    def fromJSON(cls, js):
        t = Tree(js['value'])
        for key in js['children'].keys():
            t.addChild(key, Tree.fromJSON(js['children'][key]))
        return t

    def __repr__(self):
        return json.dumps(self.toJSON())

    def foldl(self, f, b):
        '''in: (a -> b -> b), b
           out: b
           I believe this is a left-fold based on the Haskell docs'''
        result = b
        for key in sorted(self.children.keys()):
            child = self.children[key]
            result = child.fold(f, result)
        return f(self.value, result)

    def applySubTree(self, f):
        '''Tree a -> ([a] -> a) -> Tree a'''
        newTree = Tree(None)
        vals = [self.value]
        for (k, v) in self.children.iteritems():
            child = v.applySubTree(f)
            vals.append(child.value)
            newTree.addChild(k, child)
        newTree.value = f(vals)
        return newTree



