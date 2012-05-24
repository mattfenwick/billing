import sys
import analyze
import yaml
import model
import datetime



def readFile(path):
    f = open(path, 'r')
    c = f.read()
    f.close()
    return c


def output(st):
#    outf = open(outpath, 'w')
#    outf.write(outstring)
#    outf.close()
    print st


def parseDate(d):
    try:
        fs = d.split('-')
        return datetime.datetime(*map(int, fs))
    except:
        print "improperly formatted date: require 'yyyy-mm-dd'"
        raise


def run():
    try:
        # parse the cl args
        l = sys.argv
        _, start, stop, outpath, inpaths = l[:4] + [l[4:]]

        # read the files and build the tree
        cs = {}
        for f in inpaths:
            cs[f] = readFile(f)

        tree = analyze.makeModel(cs)
        analedTree = analyze.analyzeTree(tree, parseDate(start), parseDate(stop))

        # extract just the seconds
        secs = model.fmap(analedTree, lambda x: x.total_seconds())

        con = model.addContext(secs)

        # sort by path
        abc = sorted(model.foldl(con, lambda x,y: [x] + y, []), key = lambda x: x[1])

        # remove those with a total of 0
        abcd = filter(lambda x: x[0] > 0, abc)

        for x in abcd:
            print x

    except ValueError, e:
        print 'usage: program outfile infile [infiles]'
        raise


if __name__ == "__main__":
    run()