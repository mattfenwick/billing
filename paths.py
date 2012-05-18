import sys


def getDirs(l):
  i = 0
  dirs = []
  while i < len(l):
    if l[i] == '/':
      dirs.append(l[:i])
    i += 1
  print dirs
  return dirs[1:] # ditch first (just spectrometer number)


def munge(lines):
  dirs = set([])
  for l in lines:
    these = getDirs(l)
    for d in these:
      dirs.add(d)
  return '\n'.join(sorted(dirs))


def parse(mystring):
    mylines = mystring.split("\n") # or whatever newline is
    return mylines[1:-1] # ditch first (heading) and last (empty) lines


def run():
    try:
        _, inpath, outpath = sys.argv
        inf = open(inpath, 'r')
        instring = inf.read()
        inf.close()
        lines = parse(instring)
        outstring = munge(lines)
        outf = open(outpath, 'w')
        outf.write(outstring)
        outf.close()
    except ValueError, e:
        print 'usage: program infile outfile\n\n\nexception:\n'
        raise


if __name__ == "__main__":
    run()
