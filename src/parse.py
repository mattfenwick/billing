import model as m
import sys
import re
import unittest
import datetime as d


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
    mytime = d.datetime(int(grps[6]), month2num[grps[1]], int(grps[2]), 
                        int(grps[3]), int(grps[4]), int(grps[5]))
    myIsStart = False
    if grps[7] == 'Experiment started':
       myIsStart = True
    pline = ParsedLine(path = grps[0], time = mytime, isStart = myIsStart)
    return pline


def parseFile(contents):
    '''String -> [ParsedLine]'''
    assert contents[-1] == '\n', 'file must end with a newline'
    mylines = contents.split("\n") # or whatever newline is
    return [parseLine(line) for line in mylines[:-1]] # skip the last one because it's empty


####################################################################################


class ParseTest(unittest.TestCase):

    def setUp(self):
        self.text = '''./vnmrj_2.3_A/fidlib/auto_2007.05.23/heavensabove_004/Roesy1d_01.fid/log:Thu May 24 10:20:01 2007: Acquisition complete
./vnmrj_2.3_A/fidlib/auto_2007.05.23/tempC.fid/log:Wed May 23 16:07:48 2007: Experiment started
./vnmrj_2.3_A/fidlib/auto_2007.05.23/tempC.fid/log:Wed May 23 16:16:44 2007: Acquisition complete
./vnmrj_2.3_A/fidlib/auto_2007.05.23/whateverd_001/Cosy_01.fid/log:Wed May 23 16:25:40 2007: Experiment started
./vnmrj_2.3_A/fidlib/auto_2007.05.23/notimpor_001/Cosy_01.fid/log:Wed May 23 16:36:32 2007: Acquisition complete
'''
        self.line1 = '''./vnmrj_2.3_A/fidlib/auto_2007.05.23/blahblah_001/Hsqcad_01.fid/log:Thu May 24 02:23:57 2007: Acquisition complete'''
        self.line2 = '''./vnmrj_2.3_A/fidlib/auto_2007.05.23/abcdefg_001/Hmqctoxy_01.fid/log:Wed May 23 23:13:35 2007: Experiment started'''

    def testConvertMonth(self):
        ms = [convertMonth(q) for q in ['Apr', 'Feb', 'Dec']]
        self.assertEqual(ms, [4, 2, 12])
        with self.assertRaises(ValueError) as cm:
            convertMonth('Juh')

    def testParseLine(self):
        l1 = parseLine(self.line1)
        l2 = parseLine(self.line2)
        self.assertEqual(l1.path[-5:], "d/log")
        self.assertFalse(l1.isStart)
        self.assertEqual(l2.time.month, 5)
        self.assertTrue(l2.isStart)

    def testParseFile(self):
        ped = parseFile(self.text)
        self.assertEqual(len(ped), 5)
        self.assertEqual(ped[2].time, d.datetime(2007, 5, 23, 16, 16, 44))


def getSuite():
    suite1 = unittest.TestLoader().loadTestsFromTestCase(ParseTest)
    return unittest.TestSuite([suite1])

