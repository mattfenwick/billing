import sys
import analyze
import yaml
import model



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


def run():
    try:
        # parse the cl args
        l = sys.argv
        _, outpath, inpaths = l[:2] + [l[2:]]

        # read the files and build the tree
        cs = {}
        for f in inpaths:
            cs[f] = readFile(f)

        tree = analyze.makeModel(cs)
        analedTree = analyze.analyzeTree(tree)

        # dump the tree ... somewhere
#        output(yaml.dump(analedTree.toJSON()))

        con = model.addContext(analedTree.fmap(lambda x: x.total_seconds()))

#        print yaml.dump(con.toJSON())

        abc = sorted(con.foldl(lambda x,y: [x] + y, []), key = lambda x: x[1])

        abcd = filter(lambda x: x[0] > 0, abc)

        for x in abcd:
            print x

#        output()

    except ValueError, e:
        print 'usage: program outfile infile [infiles]'
        raise


if __name__ == "__main__":
    run()