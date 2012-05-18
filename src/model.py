import json
import unittest


class Tree(object):
    
    def __init__(self, value, children = []):
        self.value = value
        self.children = {}
        for (key, c) in children:
            self.addChild(key, c)

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



class TreeTest(unittest.TestCase):

    def setUp(self):
        pass

    @unittest.expectedFailure
    def testAddChildDupeKey(self):
        t = Tree(13)
        t.addChild('hi', Tree(4))
        t.addChild('hi', Tree(45))

    @unittest.expectedFailure
    def testAddChildBadType(self):
        t = Tree(13)
        t.addChild('hi', [])

    def testAddChild(self):
        t = Tree(13)
        for x in range(20):
            t.addChild(str(x), Tree(x))
        self.assertTrue(True)

    def testFoldl(self):
        pass

    def testApplySubTree(self):
        pass

    def testToJSON(self):
        t = Tree(13, [('me', Tree(14))])
        j = {'value': 13, 'children': {'me': {'value': 14, 'children': {}}}}
        print '\n',t,'\n',j
        self.assertTrue(t == j)

    def testFromJSON(self):
        pass

    def testFmap(self):
        pass


def getSuite():
    suite1 = unittest.TestLoader().loadTestsFromTestCase(TreeTest)
    return unittest.TestSuite([suite1])



