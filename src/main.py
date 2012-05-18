import sys


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
