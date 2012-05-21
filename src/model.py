import json
import unittest


class Tree(object):
    
    def __init__(self, value, children = {}):
        self.setValue(value)
        self.children = {}
        for (key, c) in children.iteritems():
            self.addChild(key, c)

    def addChild(self, key, child):
        '''Tree a -> String -> a -> Tree a'''
        if self.children.has_key(key):
            raise ValueError("already have key <%s>" % key)
        if type(child) != type(self):
            raise ValueError("bad type for Tree child: <%s>" % str(type(child)))
        self.children[key] = child

    def getChild(self, key):
        '''Tree a -> String -> Tree a'''
        if self.children.has_key(key):
            return self.children[key]
        raise ValueError("Tree does not have key <%s>" % key)

    def fmap(self, f):
        '''Tree a -> (a -> b) -> Tree b'''
        newTree = Tree(f(self.getValue()))
        for (key, treeNode) in self.children.iteritems():
            newTree.addChild(key, treeNode.fmap(f))
        return newTree

    def toJSON(self):
        '''Tree a -> JSONObject'''
        cs = {}
        for (k, v) in self.children.iteritems():
            cs[k] = v.toJSON()
        return {
            'value': self.getValue(), 
            'children': cs
        }
 
    @classmethod
    def fromJSON(cls, js):
        '''JSONObject -> Tree a'''
        t = Tree(js['value'])
        for key in js['children'].keys():
            t.addChild(key, Tree.fromJSON(js['children'][key]))
        return t

    def __repr__(self):
        return json.dumps(self.toJSON())

    def foldl(self, f, b):
        '''Tree a -> (a -> b -> b) -> b -> b
           I believe this is a left-fold based on the Haskell docs'''
        result = b
        for key in sorted(self.children.keys()):
            child = self.children[key]
            result = child.foldl(f, result)
        val = f(self.getValue(), result)
        return val

    def applySubTree(self, f):
        '''Tree a -> ([a] -> a) -> Tree a'''
        newTree = Tree(None)
        vals = [self.getValue()]
        for (k, v) in self.children.iteritems():
            child = v.applySubTree(f)
            vals.append(child.getValue())
            newTree.addChild(k, child)
        newTree.setValue(f(vals))
        return newTree
  
    def getValue(self):
        return self._value

    def setValue(self, newValue):
        self._value = newValue



class TreeTest(unittest.TestCase):

    def setUp(self):
        self.tree = Tree(14, {
            'sub1': Tree(101), 
            'sub2': Tree(0), 
            'sub3': Tree(-27)
        })

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

    def testFoldlSmall(self):
        def f(x, base):
            return base + [x]
        fs = Tree('me').foldl(f, [])
        self.assertEqual(fs, ['me'])

    def testFoldlBig(self):
        def f(x, base):
#            print '\nargs:', x, base
            return base + [x]
        fs = self.tree.foldl(f, [])
        self.assertEqual(fs, [101, 0, -27, 14])

    def testApplySubTree(self):
        calced = self.tree.applySubTree(sum)
        self.assertEqual(88, calced.getValue())
        self.assertEqual(101, calced.getChild('sub1').getValue())
        self.assertEqual(-27, calced.getChild('sub3').getValue())

    def testToJSON(self):
        t = Tree(13, {'me': Tree(14)})
        j = {
         'value': 13, 
         'children': {
           'me': {
             'value': 14, 
             'children': {}
           }
         }
        }
        self.assertEqual(t.toJSON(), j)
        self.assertEqual(j, t.toJSON())

    def testFromJSON(self):
        t = Tree(13, {'me': Tree(14)})
        j = {'value': 13, 'children': {'me': {'value': 14, 'children': {}}}}
        self.assertEqual(Tree.fromJSON(j).toJSON(), t.toJSON())
        self.assertEqual(t.toJSON(), Tree.fromJSON(j).toJSON())

    def testFmap(self):
        t = Tree('val string!', {'me': Tree('another value')})
        newTree = t.fmap(len)
        self.assertEqual(newTree.getValue(), 11)
        self.assertEqual(newTree.getChild('me').getValue(), 13)


def getSuite():
    suite1 = unittest.TestLoader().loadTestsFromTestCase(TreeTest)
    return unittest.TestSuite([suite1])



