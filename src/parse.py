import model as m
import sys
import re
import unittest


class ParsedLine(object):
    def __init__(self, path, time, isStart):
        self.path = path
        self.time = time
        self.isStart = isStart


# capture groups:
# 0: filepath
# 1: month (three letter abbr.)
# 2: day of month
# 3: hours
# 4: minutes
# 5: seconds
# 6: year
# 7: start/stop
lineregex = re.compile("^(.+log):[a-zA-Z]{3} ([a-zA-Z]{3}) +(\d+) (\d{2}):(\d{2}):(\d{2}) (\d{4}): (Experiment started|Acquisition complete)$")


month2num = {
  'Jan': 1,
  'Feb': 2,
  'Mar': 3,
  'Apr': 4,
  'May': 5,
  'Jun': 6,
  'Jul': 7,
  'Aug': 8,
  'Sep': 9,
  'Oct': 10,
  'Nov': 11,
  'Dec': 12
}


def convertMonth(name):
    if month2num.has_key(name):
        return month2num[name]
    raise ValueError('invalid 3-letter month name <%s>' % name)


def parseLine(inline):
    '''String -> ParsedLine'''
    m = lineregex.match(inline)
    if m is None or len(m.groups()) != 8:
        raise ValueError("bad line: " + inline)
    grps = m.groups()
    mytime = d.datetime(grps[6], month2num[grps[1]], grps[2], grps[3], grps[4], grps[5])
    myIsStart = False
    if grps[7] == 'Experiment started':
       myIsStart = True
    pline = ParsedLine(path = grps[0], time = mytime, isStart = myIsStart)
    return pline


def parseFile(contents):
    '''String -> [ParsedLine]'''
    assert contents[-1] == '\n', 'file must end with a newline'
    mylines = mystring.split("\n") # or whatever newline is
    return [parseLine(line) for line in mylines[:-1]] # skip the last one because it's empty


####################################################################################


class ParseTest(unittest.TestCase):

    def setUp(self):
        pass

    @unittest.expectedFailure
    def testConvertMonth(self):
        self.assertTrue(False) # oddly, this passes ???

    def testParseLine(self):
        self.assertTrue(False)

    def testParseFile(self):
        self.assertTrue(False)

def getSuite():
    suite1 = unittest.TestLoader().loadTestsFromTestCase(ParseTest)
    return unittest.TestSuite([suite1])

