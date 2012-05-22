import sys
import parse
import model
import analyze as an



def readFile(path):
    f = open(path, 'r')
    c = f.read()
    f.close()
    return c



def run():
    try:
        l = sys.argv
        _, outpath, inpaths = l[:2] + [l[2:]]
        for f in inpaths:
            c = readFile(f)
        outstring = parse(spectrometer, instring)
        outf = open(outpath, 'w')
        outf.write(outstring)
        outf.close()
    except ValueError, e:
        print 'usage: program spectrometer infile outfile'
        raise


if __name__ == "__main__":
    run()