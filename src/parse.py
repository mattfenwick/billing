import model as m
import sys
import re

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
    '''in: string
       out:  list of fields, based on regex extraction'''
    m = lineregex.match(inline)
    if m is None or len(m.groups()) != 8:
        raise ValueError("bad line: " + inline)
    grps = m.groups()
    fields = {
      'path':     grps[0],
      'time':     d.datetime(grps[6], month2num[grps[1]], grps[2], grps[3], grps[4], grps[5]),
      'isStart':  False
    }
    if grps[7] == 'Experiment started':
        fields['isStart'] = True
    return fields


def parse(mystring):
    mylines = mystring.split("\n") # or whatever newline is
    return [parseLine(line) for line in mylines[:-1]] # skip the last one (presumably because it's empty??  test)


def parseAll(filecontents):
    '''in: [(string, spectrometer name)]
       out: NmrUsage'''
    usage = m.NmrUsage()
    for (fc, spec) in filecontents:
        parsedLines = parse(fc)
        for pl in parsedLines:
            event = m.Event(pl['time'], pl['isStart'])
            usage.addEvent(spec, pl['path'], event)
    return usage

