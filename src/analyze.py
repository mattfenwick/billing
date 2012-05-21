import unittest
import model as m


def prune(tree, f):
    '''Tree a -> Maybe Tree a
       remove nodes with f(value) == True and no children 
         (or all children with f(childvalue) == False)'''
    children = tree.getChildren()
    newTree = m.Tree(tree.getValue())
    for key in children:
        child = children[key]
        pruned = prune(child, f)
        if pruned is not None:
            newTree.addChild(key, child)
    if not f(newTree.getValue()) and len(newTree.getChildren()) == 0:
        return None
    return newTree


####################################################################################


class AnalyzeTest(unittest.TestCase):

    def setUp(self):
        self.tree = m.Tree(14, {
            'sub1': m.Tree(101, {
               'a': m.Tree(104),
               'b': m.Tree(210),
               'c': m.Tree(333),
               'd': m.Tree(3523),
            }), 
            'sub2': m.Tree(0), 
            'sub3': m.Tree(-27)
        })

    def testTestPruneSubTree(self):
        pruned = prune(self.tree, lambda x: x < 100)
        self.assertTrue(pruned)
        self.assertEqual(len(pruned.getChildren()), 2)
        self.assertFalse(pruned.hasChild('sub1'))
        print pruned

    def testPruneSingleNode(self):
        pruned = prune(self.tree, lambda x: x != 0)
        self.assertTrue(pruned)
        self.assertEqual(len(pruned.getChildren()), 2)

def getSuite():
    suite1 = unittest.TestLoader().loadTestsFromTestCase(AnalyzeTest)
    return unittest.TestSuite([suite1])
