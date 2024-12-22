"""
grading.py
"""
from html import escape
import time
from collections import defaultdict
import util
import traceback

class Counter(dict): # child class of dict
  """
  Dict with default 0
  """
  def __getitem__(self, idx):
    try:
      return dict.__getitem__(self, idx)
    except KeyError:
      return 0

  def totalCount(self):
    """
    Returns the sum of counts for all keys.
    """
    return sum(self.values())


class Grades:
    " "
    def __init__(self, projectName, questions, muteOutput=False):


        self.questions = [el[0] for el in questions]
        self.maxes = dict(questions)
        self.points = Counter()
        self.messages = dict([(q, []) for q in self.questions])
        self.project = projectName
        self.start = time.localtime()[1:6]
        self.sane = True # Sanity checks
        self.currentQuestion = None # Which question we're grading
        self.mute = muteOutput
        self.prereqs = defaultdict(set)

        print('Starting on %d-%d at %d:%02d:%02d' % self.start)

    def addPrereq(self, question, prereq):
        self.prereqs[question].add(prereq)

    def grade(self, gradingModule, exceptionMap = {}):
        """
        To grade each question
        """
        # print("hey we are here")
        doneQuestions = set([])
        for ques in self.questions:
            print('\nQuestion %s' % ques)
            print('=' * (9+len(ques)))

            self.currentQuestion = ques

            remaining = self.prereqs[ques].difference(doneQuestions)

            if len(remaining) > 0:
                prereq = remaining.pop()
                print(
"""*** NOTE: Make sure to complete Question %s before working on Question %s,
*** because Question %s builds upon your answer for Question %s.
""" % (prereq, ques, ques, prereq))
                continue


            if self.mute: util.mutePrint()
            try:
                util.TimeoutFunction(getattr(gradingModule, ques),1800)(self) # Call the question's function
            except Exception as inst:
                self.addExceptionMessage(ques, inst, traceback)
                self.addErrorHints(exceptionMap, inst, ques[1])
            except:
                self.fail('FAIL: Terminated with a string exception.')
            finally:
                if self.mute: util.unmutePrint()

            if self.points[ques] >= self.maxes[ques]:
                doneQuestions.add(ques)

            print('\n### Question %s: %d/%d ###\n' % (ques, self.points[ques], self.maxes[ques]))


        print('\nFinished at %d:%02d:%02d' % time.localtime()[3:6])
        print("\nProvisional grades\n==================")

        for ques in self.questions:
            print('Question %s: %d/%d' % (ques, self.points[ques], self.maxes[ques]))
        print('------------------')
        print('Total: %d/%d' % (self.points.totalCount(), sum(self.maxes.values())))

    def addMessage(self, message, raw=False):
        if not raw:
            # We assume raw messages, formatted for HTML, are printed separately
            if self.mute: util.unmutePrint()
            print('*** ' + message)
            if self.mute: util.mutePrint()
            message = escape(message)
        self.messages[self.currentQuestion].append(message)

    def addErrorHints(self, exceptionMap, errorInstance, questionNum):
        typeOf = str(type(errorInstance))
        questionName = 'q' + questionNum
        errorHint = ''

        # question specific error hints
        if exceptionMap.get(questionName):
            questionMap = exceptionMap.get(questionName)
            if (questionMap.get(typeOf)):
                errorHint = questionMap.get(typeOf)
            # fall back to general error messages if a question specific
            # one does not exist
        if (exceptionMap.get(typeOf)):
            errorHint = exceptionMap.get(typeOf)

        # dont include the HTML if we have no error hint
        if not errorHint:
            return ''

        for line in errorHint.split('\n'):
            self.addMessage(line)

    def addExceptionMessage(self, ques, inst, traceback):
        """
        Method to format the exception message, this is more complicated because
        we need to escape the traceback but wrap the exception in a <pre> tag
        """
        self.fail('FAIL: Exception raised: %s' % inst)
        self.addMessage('')
        for line in traceback.format_exc().split('\n'):
            self.addMessage(line)

    def fail(self, message, raw=False):
        "Sets sanity check bit to false and outputs a message"
        self.sane = False
        self.assignZeroCredit()
        self.addMessage(message, raw)

    def assignZeroCredit(self):
        self.points[self.currentQuestion] = 0

    def assignFullCredit(self, message="", raw=False):
        self.points[self.currentQuestion] = self.maxes[self.currentQuestion]
        if message != "":
            self.addMessage(message, raw)

    def addPoints(self, amt):
        self.points[self.currentQuestion] += amt