import unittest
import model as m
import re
import logging


myLogger = logging.getLogger('analyze')



def addEvent(tree, dirs, event):
    '''Tree [Event] -> [String] -> Event -> Tree [Event]'''
    t = tree

    # traverse the tree, moving deeper and deeper
    for x in dirs:
        if not t.hasChild(x):
            # we just need an empty child -- empty of events & of children
            t.addChild(x, m.Tree([]))
        t = t.getChild(x)

    # append the event to the event list
    t.setValue(t.getValue().append(event))
    return tree


def splitPath(path):
    '''String -> [String]'''
    return path.split("/")


pathMatcher = re.compile('(?:vnmrsys/exp|vnmrsys/gshimlib/|vnmrj_2\.3_A|vnmrj_3\.2_A|BioPack\.dir)')
def pathIsOkay(path):
    '''String -> Bool'''
    isOkay = not bool(pathMatcher.search(path))
    if not isOkay:
        myLogger.info("discarding path: <%s>" % path)
    return isOkay


def filterPaths(pLines):
    '''[ParsedLine] -> [ParsedLine]'''
    return [p for p in pLines if pathIsOkay(p.path)]


def makeTree(pLines):
    '''[ParsedLine] -> Tree [Event]'''
    tree = m.Tree() # ?? args?
    okay = filterPaths(pLines)
    for p in okay:
        dirs = splitPath(p.path)
        event = m.Event(p.time, p.isStart) # arg order?
        addEvent(tree, dirs, event)
    return tree


def makeModel(files):
    '''Map String String -> Tree Event'''
    tree = m.Tree("root") # value ??
    for spec in files:
        parsedLines = parse.parseFile(files[spec])
        specTree = bm.makeTree(parsedLines)
        tree.addChild(spec, specTree)
    return tree


####################################################################################



def removeJunk(events):
    '''[Event] -> [Event]'''
    if len(events) != 2:
        myLogger.info('removing events: <%s>' % str(events))
        return []
    elif events[0].isStart == events[1].isStart:
        myLogger.info('removing events: <%s>' % str(events))
        return []
    else:
        myLogger.info('keeping events: <%s>' % str(events))
        return events


def calculateInterval(events):
    if events[0].isStart:
        start, stop = events
    else:
        stop, start = events
    assert stop.isStart != start.isStart, "must have exactly one start and one stop"
    return stop.time - start.time


def sumIntervals(intervals):
    '''[datetime.timedelta] -> datetime.timedelta'''
    total = timedelta()
    for i in intervals:
        total = total + i
    return total


def analyzeTree(tree):
    '''Tree Event -> Tree Interval'''

    # remove junk
    t1 = tree.fmap(removeJunk)

    # Tree Event -> Tree timedelta
    t2 = t1.fmap(calculateInterval)

    # sum subtrees: Tree timedelta -> Tree timedelta
    t3 = t2.applySubTree(sumIntervals)

    return t2


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
        self.assertFalse(True)

    def testPruneSingleNode(self):
        self.assertFalse(True)


class BuildTest(unittest.TestCase):

    def setUp(self):
        self.paths = [
            './what/vnmrsys/exp27/whatisthis/log',
            './dunno/vnmrsys/BioPack.dir/backups/Something_2009-09-09_09:09/something_fine.fid/log',
            './vnmrj_2.3_A/fidlib/auto_2007.05.23/something_001/Proton_01.fid/log',
            './vnmrj_3.2_A/biopack/fidlib/AutoTripRes2D/meh.fid/log',
            './hi/vnmrsys/data/hithere/ADA/dunno.fid/log',
            './hello/vnmrsys/gshimlib/shimmaps/wowthisislong.fid/log',
            './myname/vnmrsys/data/isme/ADA/andhtistoo.fid/log'
        ]

    @unittest.expectedFailure
    def testAddEvent(self):
        self.assertTrue(False) # oddly, this passes ???

    def testPathIsOkay(self):
        rs = map(pathIsOkay, self.paths)
        self.assertEqual(rs, [False, False, False, False, True, False, True])

    def testSplitPath(self):
        self.assertTrue(False)

    def testMakeTree(self):
        self.assertTrue(False)


def getSuite():
    suite1 = unittest.TestLoader().loadTestsFromTestCase(AnalyzeTest)
    suite2 = unittest.TestLoader().loadTestsFromTestCase(BuildTest)
    return unittest.TestSuite([suite1, suite2])
