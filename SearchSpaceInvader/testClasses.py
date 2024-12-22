"""
testClasses.py
"""

import inspect
import sys


# For making question in the project. 
# A Question consists of its maximum score and 
# a bunch of test cases.
class Question(object):

    def __init__(self, quesDict, display): #
        self.maxScore = int(quesDict['maxScore'])
        self.testCases = []
        self.display = display

    def raiseNotDefined(self):
        print('Method not implemented: %s' % inspect.stack()[1][3])
        sys.exit(1)

    def getMaxScore(self):
        return self.maxScore
    
    def getDisplay(self):
        return self.display
    
    def addTestCase(self, testCase, lambdaFn):
        self.testCases.append((testCase, lambdaFn))

    def execute(self, grades):
        self.raiseNotDefined()


# Question in which all test cases has to be passed in order to get credits.
class PassAllTestsQuestion(Question):

    def execute(self, grades):
        testsFailed = False
        grades.assignZeroCredit()
        for _, f in self.testCases:
            if not f(grades):
                testsFailed = True
        if testsFailed:
            grades.fail("Tests failed.")
        else:
            grades.assignFullCredit()



# making a testcase
class TestCase(object):

    def __init__(self, question, testDict):
        self.question = question
        self.testDict = testDict
        self.path = testDict['path']
        self.messages = []

    def getPath(self):
        return self.path

    def raiseNotDefined(self):
        print('Method not implemented: %s' % inspect.stack()[1][3])
        sys.exit(1)

    def __str__(self):
        self.raiseNotDefined()

    def execute(self, grades, moduleDict, solutionDict):
        self.raiseNotDefined()

    def writeSolution(self, moduleDict, filePath):
        self.raiseNotDefined()
        return True

    def testPass(self, grades):
        grades.addMessage('PASS: %s' % (self.path,))
        for line in self.messages:
            grades.addMessage('    %s' % (line,))
        return True

    def testFail(self, grades):
        grades.addMessage('FAIL: %s' % (self.path,))
        for line in self.messages:
            grades.addMessage('    %s' % (line,))
        return False

    def testPartial(self, grades, points, maxPoints):
        grades.addPoints(points)
        extraCredit = max(0, points - maxPoints)
        regularCredit = points - extraCredit

        grades.addMessage('%s: %s (%s of %s points)' % ("PASS" if points >= maxPoints else "FAIL", self.path, regularCredit, maxPoints))
        if extraCredit > 0:
            grades.addMessage('EXTRA CREDIT: %s points' % (extraCredit,))

        for line in self.messages:
            grades.addMessage('    %s' % (line,))

        return True

    def addMessage(self, message):
        self.messages.extend(message.split('\n'))


class Q6PartialCreditQuestion(Question):
    """Fails any test which returns False, otherwise doesn't effect the grades object.
    Partial credit tests will add the required points."""

    def execute(self, grades):
        grades.assignZeroCredit()

        results = []
        for _, f in self.testCases:
            results.append(f(grades))
        if False in results:
            # print("we get some incorrect thing?")
            grades.assignZeroCredit()

class PartialCreditQuestion(Question):
    """Fails any test which returns False, otherwise doesn't effect the grades object.
    Partial credit tests will add the required points."""

    def execute(self, grades):
        grades.assignZeroCredit()

        for _, f in self.testCases:
            if not f(grades):
                grades.assignZeroCredit()
                grades.fail("Tests failed.")
                return False