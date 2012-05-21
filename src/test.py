import unittest
import model
import parse
import analyze as am


def runTests():
    testModules = [parse, model, am]
    mySuite = unittest.TestSuite([module.getSuite() for module in testModules])
    unittest.TextTestRunner(verbosity=2).run(mySuite)
#    unittest.main()

if __name__ == "__main__":
    runTests()
