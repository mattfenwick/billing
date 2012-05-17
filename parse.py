import sys
import re

# capture groups:
# 1: filepath
# 2: month (three letter abbr.)
# 3: day of month
# 4: hours
# 5: minutes
# 6: seconds
# 7: year
# 8: start/stop
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


def mungeLine(spectrometer, inline):
    m = lineregex.match(inline)
    if m is None or len(m.groups()) != 8:
        raise ValueError("bad line: " + inline)
    fields = list(m.groups())
    fields[0] = spectrometer + "/" + fields[0]  # add the spectrometer name to the path
    fields[1] = str(month2num[fields[1]]) # convert the 3-letter abbreviation to its numerical equivalent
    outline = '\t'.join(fields)
    return outline


def parse(spectrometer, mystring):
    mylines = mystring.split("\n") # or whatever newline is
    outlines = []
    for line in mylines[:-1]: # skip the last one
        outlines.append(mungeLine(spectrometer, line))
    return '\n'.join(outlines)


def run():
    try:
        _, spectrometer, inpath, outpath = sys.argv
        inf = open(inpath, 'r')
        instring = inf.read()
        inf.close()
        outstring = parse(spectrometer, instring)
        outf = open(outpath, 'w')
        outf.write(outstring)
        outf.close()
    except ValueError, e:
        print 'usage: program spectrometer infile outfile'
        raise


if __name__ == "__main__":
    run()
