"""
Autograder
"""
import optparse
import projectParameters
import sys
import re
import os
import importlib.util
import grading

# checking if we really want to write solution files
def checkGenerate():
    print("Warning: This will overwrite any solution file/files.")
    print("Do you want to continue? (yes/no)")

    while 1:
        res = sys.stdin.readline().strip()

        if res == 'yes':
            break
        elif res == 'no':
            sys.exit(0)
        else:
            print('Please answer either "yes" or "no"!')


# https://docs.python.org/3/library/importlib.html#importing-a-source-file-directly
def importFromPath(moduleName, filePath):
    spec = importlib.util.spec_from_file_location(moduleName, filePath)
    module = importlib.util.module_from_spec(spec)
    sys.modules[moduleName] = module
    spec.loader.exec_module(module)
    return module

# returns all the tests you need to run in order to run question
def getDepends(testParser, testRoot, question):
    allDeps = [question]
    questionDict = testParser.TestParser(os.path.join(testRoot, question, 'CONFIG')).parse()
    if 'depends' in questionDict:
        depends = questionDict['depends'].split()
        for d in depends:
            # run dependencies first
            allDeps = getDepends(testParser, testRoot, d) + allDeps
    return allDeps

# get list of questions to grade
def getTestSubDirs(testParser, testRoot, questionToGrade):
    problemDict = testParser.TestParser(os.path.join(testRoot, 'CONFIG')).parse()
    if questionToGrade != None:
        questions = getDepends(testParser, testRoot, questionToGrade)
        if len(questions) > 1:
            print('Note: due to dependencies, the following tests will be run: %s' % ' '.join(questions))
        return questions
    if 'order' in problemDict:
        return problemDict['order'].split()
    return sorted(os.listdir(testRoot))


def evaluate(generateSolutions, testRoot, moduleDict, muteOutput=False, printTestCase=False, questionToGrade=None,
            display=None):
    
    import testParser
    import testClasses

    for module in moduleDict:
        setattr(sys.modules[__name__], module, moduleDict[module])
    
    questions = [] # the questions we want to evaluate 
    questionDicts = {}
    testSubDirs = getTestSubDirs(testParser, testRoot, questionToGrade)
    for ques in testSubDirs:
        subDirPath = os.path.join(testRoot, ques)
        if not os.path.isdir(subDirPath) or ques[0] == '.':
            continue
        
        # create a question object
        questionDict = testParser.TestParser(os.path.join(subDirPath, 'CONFIG')).parse()
        questionClass = getattr(testClasses, questionDict['class'])
        question = questionClass(questionDict, display)
        questionDicts[ques] = questionDict

        # load test cases in the question
        tests = filter(lambda t: re.match('[^#~.].*\.test\Z', t), os.listdir(subDirPath))
        tests = map(lambda t: re.match('(.*)\.test\Z', t).group(1), tests)

        # for t in sorted(tests):
        for t in tests:
            testFile = os.path.join(subDirPath, '%s.test' % t)
            solFile = os.path.join(subDirPath, '%s.solution' % t)
            testDict = testParser.TestParser(testFile).parse()
            testClass = getattr(projectTestClasses, testDict['class'])
            testCase = testClass(question, testDict)

            def gradeLambda(testCase, solFile):
                if generateSolutions:
                    # write solution file
                    return lambda grades: testCase.writeSolution(moduleDict, solFile)
                else:
                    # read in solution 
                    testDict = testParser.TestParser(testFile).parse()
                    solDict = testParser.TestParser(solFile).parse()
                    if printTestCase:
                        return lambda grades: printTest(testDict, solDict) or testCase.execute(grades, moduleDict, solDict)
                    else:
                        return lambda grades: testCase.execute(grades, moduleDict, solDict)

            question.addTestCase(testCase, gradeLambda(testCase, solFile))

        def executeGradeLambda(question):
            return lambda grades: question.execute(grades)
        
        # setting the question to its corresponding grade function
        setattr(sys.modules[__name__], ques, executeGradeLambda(question))
        questions.append((ques, question.getMaxScore()))
    
    grades = grading.Grades(projectParameters.PROJECT_NAME, questions, muteOutput=muteOutput)
    if questionToGrade == None:
        for q in questionDicts:
            for prereq in questionDicts[q].get('depends', '').split():
                grades.addPrereq(q, prereq)

    grades.grade(sys.modules[__name__])
    return grades.points


def getDisplay(graphicsByDefault, options=None):
    graphics = graphicsByDefault
    if options is not None and options.noGraphics:
        graphics = False
    if graphics:
        try:
            import graphicsDisplay
            return graphicsDisplay.SpaceShipGraphics(1)
        except ImportError:
            pass
    import textDisplay
    return textDisplay.NullGraphics()



def printTest(testDict, solutionDict):
    print("Test case:")
    for line in testDict["__rawText__"]:
        print("   |", line)
    print("Solution:")
    for line in solutionDict["__rawText__"]:
        print("   |", line)


def runTest(testName, moduleDict, printTestCase=False, display=None):
    import testParser
    import testClasses
    for module in moduleDict:
        setattr(sys.modules[__name__], module, moduleDict[module])

    testDict = testParser.TestParser(testName + ".test").parse()
    solutionDict = testParser.TestParser(testName + ".solution").parse()
    test_out_file = os.path.join('%s.test_output' % testName)
    testDict['test_out_file'] = test_out_file
    testClass = getattr(projectTestClasses, testDict['class'])

    questionClass = getattr(testClasses, 'Question')
    question = questionClass({'maxScore': 0}, display)
    testCase = testClass(question, testDict)

    if printTestCase:
        printTest(testDict, solutionDict)

    # This is a fragile hack to create a stub grades object
    grades = grading.Grades(projectParameters.PROJECT_NAME, [(None, 0)])
    testCase.execute(grades, moduleDict, solutionDict)


# reading command from the command line
def read_command(argv):
    parser = optparse.OptionParser(description= 'Running and grading tests on student code')
    parser.set_defaults(generateSolution=False, muteOutput=False, printTestCase=False, noGraphics=False)
    parser.add_option('--test-directory',
                      dest = 'testRoot',
                      default = 'test_cases',
                      help = 'Root test directory which contains subdirectories corresponding to each question')
    parser.add_option('--student-code',
                      dest = 'studentCode',
                      default = projectParameters.STUDENT_CODE_DEFAULT,
                      help = 'comma separated list of student code files')
    parser.add_option('--code-directory',
                    dest = 'codeRoot',
                    default = "",
                    help = 'Root directory containing the student and testClass code')
    parser.add_option('--test-case-code',
                      dest = 'testCaseCode',
                      default = projectParameters.PROJECT_TEST_CLASSES,
                      help = 'class containing testClass classes for this project')
    parser.add_option('--generate-solutions',
                      dest = 'generateSolutions',
                      action = 'store_true',
                      help = 'Write solutions generated to .solution file')
    parser.add_option('--mute',
                    dest = 'muteOutput',
                    action = 'store_true',
                    help = 'Mute output from executing tests')
    parser.add_option('--print-tests', '-p',
                    dest = 'printTestCase',
                    action = 'store_true',
                    help = 'Print each test case before running them.')
    parser.add_option('--test', '-t',
                      dest = 'runTest',
                      default = None,
                      help = 'Run one particular test.  Relative to test root.')
    parser.add_option('--question', '-q',
                    dest = 'gradeQuestion',
                    default = None,
                    help = 'Grade one particular question.')
    parser.add_option('--no-graphics',
                    dest = 'noGraphics',
                    action = 'store_true',
                    help = 'No graphics display for space invaders games.')
    (options, args) = parser.parse_args(argv)
    return options


if __name__ == '__main__':
    options = read_command(sys.argv)
    if options.generateSolutions:
        checkGenerate()
    codePaths = options.studentCode.split(',')

    moduleDict = {}
    for cp in codePaths:
        moduleName = re.match('.*?([^/]*)\.py', cp).group(1)
        moduleDict[moduleName] = importFromPath(moduleName, os.path.join(options.codeRoot, cp))
    moduleName = re.match('.*?([^/]*)\.py', options.testCaseCode).group(1)
    moduleDict['projectTestClasses'] = importFromPath(moduleName, os.path.join(options.codeRoot, options.testCaseCode)) 

    # evaluate(True, options.testRoot, moduleDict,
    #         muteOutput=options.muteOutput, printTestCase=options.printTestCase, questionToGrade=options.gradeQuestion,
    #         display = getDisplay(options.gradeQuestion!=None, options))

    if options.runTest != None:
        runTest(options.runTest, moduleDict, printTestCase=options.printTestCase,
                display=getDisplay(True, options))

    else:
        evaluate(options.generateSolutions, options.testRoot, moduleDict,
            muteOutput=options.muteOutput, printTestCase=options.printTestCase, questionToGrade=options.gradeQuestion,
            display = getDisplay(options.gradeQuestion!=None, options))