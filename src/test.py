import unittest
import model


def runTests():
    mySuite = unittest.TestSuite([module.getSuite() for module in [model]])
    unittest.TextTestRunner(verbosity=2).run(mySuite)
#    unittest.main()

if __name__ == "__main__":
    runTests()