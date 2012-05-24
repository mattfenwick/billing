import unittest
import model as m
import re
import logging
import datetime
# just for ???
import yaml
import parse


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
    t.setValue(t.getValue() + [event])
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
    tree = m.Tree([]) # ?? args?
    okay = filterPaths(pLines)
    for p in okay:
        dirs = splitPath(p.path)
        event = m.Event(p.time, p.isStart) # arg order?
        addEvent(tree, dirs, event)
    return tree


def makeModel(files):
    '''Map String String -> Tree [Event]'''
    tree = m.Tree([])
    for spec in files:
        parsedLines = parse.parseFile(files[spec])
        specTree = makeTree(parsedLines)
        tree.addChild(spec, specTree)
    return tree


####################################################################################

class Experiment(object):

    def __init__(self, start, stop):
        self.start = start
        self.stop = stop


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


def orderEvents(events):
    '''Maybe (Event, Event) -> Maybe Experiment'''
    assert len(events) in [0, 2], "need exactly 2 events"
    if len(events) == 0:
        return None
    e1, e2 = events
    assert e1.isStart != e2.isStart, "start AND stop required"
    if e1.isStart:
        return Experiment(e1, e2)
    else:
        return None


def filterByDate(exp, startDate, stopDate):
    '''Maybe Experiment -> Maybe Experiment'''
    if exp is None:
        return None
    stop = exp.stop
    if stop.time >= startDate and stop.time < stopDate:
        return exp
    else:
        return None


def calculateInterval(exp):
    '''Maybe Experiment -> Interval'''
    if exp is None:
        return datetime.timedelta()
    start, stop = exp.start, exp.stop
    assert stop.isStart != start.isStart, "must have exactly one start and one stop"
    return stop.time - start.time


def sumIntervals(intervals):
    '''[datetime.timedelta] -> datetime.timedelta'''
    total = datetime.timedelta()
    for i in intervals:
        total = total + i
    return total


def analyzeTree(tree, startDate, stopDate):
    '''Tree [Event] -> Tree timedelta'''

    # remove junk -- wrong number of events, and 2 starts/stops
    #   :: Tree [Event]
    t1 = m.fmap(tree, removeJunk)

    # put events in order
    #   :: Tree (Maybe Experiment)
    t2 = m.fmap(t1, orderEvents)

    # remove event pairs outside the date range
    #   :: Tree (Maybe Experiment)
    t3 = m.fmap(t2, lambda events: filterByDate(events, startDate, stopDate)) 

    # Tree (Maybe Experiment) -> Tree timedelta
    #   :: Tree timedelta
    t4 = m.fmap(t3, calculateInterval) 

    # sum subtrees: Tree timedelta -> Tree timedelta
    t5 = m.applySubTree(t4, sumIntervals)

    return t5


####################################################################################


class AnalyzeTest(unittest.TestCase):

    def setUp(self):
        self.numtree = m.Tree(14, {
            'sub1': m.Tree(101, {
               'a': m.Tree(104),
               'b': m.Tree(210),
               'c': m.Tree(333),
               'd': m.Tree(3523),
            }), 
            'sub2': m.Tree(0), 
            'sub3': m.Tree(-27)
        })
        self.d = d = datetime.datetime
        self.timetree = m.Tree([m.Event(d(2012,3,11), True), m.Event(d(2012,3,11,1,0,0), False)], {  # 1 hour
            'sub1': m.Tree([m.Event(d(2012,3,12,8), True), m.Event(d(2012,3,12,8,4), False)], {      # 4 minutes
               'a': m.Tree([m.Event(d(2012,3,11), True)]),                               # should be filtered
               'b': m.Tree([]),                                                          # should be filtered
               'c': m.Tree([m.Event(d(2012,3,11), True), m.Event(d(2012,4,4), True)]),   # should be filtered
               'd': m.Tree([m.Event(d(2012,3,11), True), m.Event(d(2012,3,11,0,0,27), False)]),      # 27 seconds
            }), 
            'sub2': m.Tree([m.Event(d(2012,4,2), True), m.Event(d(2012,4,4), False)]),               # 2 days
            'sub3': m.Tree([m.Event(d(2012,3,11), False), m.Event(d(2012,3,11), True)])              # 0
        })
        self.subtimetree = self.timetree.getChild('sub2')

    def testRemoveJunk(self):
        my = m.Event(None, None)
        d = self.d
        e1, e2, e3, e4 = (
            [m.Event(None, None)], 
            [my, my, my, my],
            [m.Event(d(2012,3,11), True), m.Event(d(2012,4,4), True)], 
            [m.Event(d(2012,8,7), True), m.Event(d(2012,9,1), False)]
        )
        # case 1:  not 2 events
        self.assertEqual([], removeJunk(e1))
        # case 2:  two stops or two starts
        self.assertEqual([], removeJunk(e2))
        self.assertEqual([], removeJunk(e3))
        # case 3:  acceptable
        self.assertEqual(e4, removeJunk(e4))

    def testOrderEvents(self):
        d = self.d
        e1, e2 = m.Event(d(2012, 3, 11), True), m.Event(d(2012, 4, 1), False)
        exp1, exp2 = orderEvents([e1, e2]), orderEvents([e2, e1])
        self.assertEqual([e1, e2], [exp1.start, exp1.stop])
        self.assertEqual([e1, e2], [exp1.start, exp1.stop])

    def testFilterByDate(self):
        d = self.d
        r1, r2 = d(2012, 1, 1), d(2012, 5, 1, 0, 0, 0)
        e1, e2 = m.Event(d(2011, 2, 18), True), m.Event(d(2011, 12, 31), False)

        # ends right before range
        exp1 = Experiment(e1, e2)
        self.assertEqual(filterByDate(exp1, r1, r2), None)

        # ends right as range starts
        e2.time = d(2012, 1, 1)
        self.assertEqual(filterByDate(exp1, r1, r2), exp1)

        # ends right as range ends
        e2.time = d(2012, 4, 30)
        self.assertEqual(filterByDate(exp1, r1, r2), exp1)

        # ends right after range ends
        e2.time = d(2012, 5, 1)
        self.assertEqual(filterByDate(exp1, r1, r2), None)

    def testCalculateInterval(self):
        stop = m.Event(self.d(2012, 4, 1, 10, 0, 0), False)
        start = m.Event(self.d(2012, 4, 1, 8, 0, 0), True)
        i = calculateInterval(Experiment(start, stop))
        self.assertEqual(i.total_seconds(), 7200)

    def testSumIntervals(self):
        t = datetime.timedelta
        ints = [t(4, 78), t(5, -12), t(0, 22334)]
        total = sumIntervals(ints)
        self.assertEqual(total.total_seconds(), 800000)

    def testAnalyzeTree(self):
        subtree = analyzeTree(self.subtimetree, self.d(2009, 8, 11), self.d(2013, 12, 2))
        self.assertEqual(subtree.getValue(), datetime.timedelta(2))

        tree = analyzeTree(self.timetree, self.d(2009, 8, 11), self.d(2013, 12, 2))
        i = tree.getValue()
        self.assertEqual(i.days, 2)
        self.assertEqual(i.total_seconds(), 3600 + 240 + 27 + 3600 * 48)


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
        ps = [
            'not/me/0003.fid/log:Thu Aug 20 18:55:12 2009: Experiment started',
            'not/me/0003.fid/log:Thu Aug 20 19:04:08 2009: Acquisition complete',
            'ab/0002.fid/log:Thu Aug 20 18:16:47 2009: Experiment started',
            'not/me/0002.fid/log:Thu Aug 20 18:55:12 2009: Acquisition complete',
            'not/me/0008.fid/log:Thu Aug 20 19:52:59 2009: Experiment started',
            'second/vnmrsys/dba/0008.fid/log:Thu Aug 20 20:25:56 2009: Acquisition complete',
            'myname/vnmrsys/abc/def/01.fid/log:Thu Aug 20 18:16:12 2009: Experiment started',
        ]
        self.pathdict = {
            '800.txt': '\n'.join(ps[0:3]) + '\n',
            'hmm???':  '\n'.join(ps[2:5]) + '\n',
            'third':   '\n'.join(ps[-4:]) + '\n'
        }

    def testAddEventEmptyPath(self):
        tree = m.Tree([13])
        addEvent(tree, [], 14)
        self.assertEqual([13, 14], tree.getValue())

    def testAddEventNonEmptyPath(self):
        tree = m.Tree(13)
        addEvent(tree, ["abc", "haha", "path"], m.Tree(14))
        addEvent(tree, ["abc", "haha", "what?"], 37)
        self.assertEqual([37], tree.getChild("abc").getChild("haha").getChild("what?").getValue())
        self.assertEqual([], tree.getChild("abc").getChild("haha").getValue())
        self.assertEqual(2, len(tree.getChild("abc").getChild("haha").getChildren()))

    def testPathIsOkay(self):
        rs = map(pathIsOkay, self.paths)
        self.assertEqual(rs, [False, False, False, False, True, False, True])

    def testSplitPath(self):
        sp = splitPath(self.paths[0])
        self.assertEqual(sp[:4], [".", "what", "vnmrsys", "exp27"])
        sp2 = splitPath(self.paths[4])
        self.assertEqual(sp2[-4:], ["hithere", "ADA", "dunno.fid", "log"])

    def testMakeTree(self):
        p = parse.ParsedLine
        plines = [p("abcd/def", None, True), p("ab/cd", 37, False)]
        tree = makeTree(plines)
        self.assertEqual(tree.getChild("ab").getChild("cd").getValue()[0].time, 37) 
        self.assertTrue(tree.getChild("abcd").hasChild("def"))

    def testBuildModel(self):
        tree = makeModel(self.pathdict)
#        print yaml.dump(tree.toJSON())
        self.assertTrue(tree.getChild('third').getChild('myname').getChild('vnmrsys').hasChild('abc'))
        self.assertEqual(tree.getChild('hmm???').getChild('ab').getChild('0002.fid').getValue()[0].time.year, 2009)


def getSuite():
    suite1 = unittest.TestLoader().loadTestsFromTestCase(AnalyzeTest)
    suite2 = unittest.TestLoader().loadTestsFromTestCase(BuildTest)
    return unittest.TestSuite([suite1, suite2])
