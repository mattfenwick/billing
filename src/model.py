import json
import unittest



class Event(object):

    def __init__(self, time, isStart):
        self.time = time
        self.isStart = isStart
        
    def toJSON(self):
        '''Event -> JSONObject'''
        return {
            'time': str(self.time),
            'isStart': self.isStart
        }


class Tree(object):
    
    def __init__(self, value, children = {}):
        self.setValue(value)
        self._children = {}
        for (key, c) in children.iteritems():
            self.addChild(key, c)

    #### getters and setters

    def hasChild(self, key):
        '''Tree a -> String -> Bool'''
        return self._children.has_key(key)

    def addChild(self, key, child):
        '''Tree a -> String -> Tree a -> Tree a'''
        if self.hasChild(key):
            raise ValueError("already have key <%s>" % key)
        if type(child) != type(self):
            raise ValueError("bad type for Tree child: <%s>" % str(type(child)))
        self._children[key] = child

    def getChild(self, key):
        '''Tree a -> String -> Tree a'''
        if self.hasChild(key):
            return self._children[key]
        raise ValueError("Tree does not have key <%s>" % key)
  
    def getValue(self):
        return self._value

    def setValue(self, newValue):
        self._value = newValue

    def getChildren(self):
        return self._children

    #### serialization/loading methods

    def toJSON(self):
        '''Tree a -> JSONObject'''
        cs = {}
        for (k, v) in self.getChildren().iteritems():
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


#### traversal algorithms

def fmap(tree, f):
    '''Tree a -> (a -> b) -> Tree b'''
    newTree = Tree(f(tree.getValue()))
    for key in tree.getChildren():
        child = tree.getChild(key)
        newTree.addChild(key, fmap(child, f))
    return newTree


def foldl(tree, f, b):
    '''Tree a -> (a -> b -> b) -> b -> b
       I believe this is a left-fold based on the Haskell docs'''
    result = b
    for key in sorted(tree.getChildren()):
        child = tree.getChild(key)
        result = foldl(child, f, result)
    val = f(tree.getValue(), result)
    return val


def applySubTree(tree, f):
    '''Tree a -> ([a] -> a) -> Tree a'''
    newTree = Tree(None)
    vals = [tree.getValue()]

    for key in tree.getChildren():
        child = applySubTree(tree.getChild(key), f)
        vals.append(child.getValue())
        newTree.addChild(key, child)

    newTree.setValue(f(vals))
    return newTree


def addContext(tree, context = []):
    '''Tree a -> [String] -> Tree (a, [String])'''
    newTree = Tree(None)
    for key in tree.getChildren():
        newContext = context + [key]
        child = addContext(tree.getChild(key), newContext)
        newTree.addChild(key, child)
    newTree.setValue((tree.getValue(), context))
    return newTree


##################################################################


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
        fs = foldl(Tree('me'), f, [])
        self.assertEqual(fs, ['me'])

    def testFoldlBig(self):
        def f(x, base):
#            print '\nargs:', x, base
            return base + [x]
        fs = foldl(self.tree, f, [])
        self.assertEqual(fs, [101, 0, -27, 14])

    def testApplySubTree(self):
        calced = applySubTree(self.tree, sum)
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
        newTree = fmap(t, len)
        self.assertEqual(newTree.getValue(), 11)
        self.assertEqual(newTree.getChild('me').getValue(), 13)

    def testAddContext(self):
        myTree = addContext(self.tree)
        self.assertEqual((14, []), myTree.getValue())
        self.assertEqual((-27, ['sub3']), myTree.getChild('sub3').getValue())


def getSuite():
    suite1 = unittest.TestLoader().loadTestsFromTestCase(TreeTest)
    return unittest.TestSuite([suite1])



