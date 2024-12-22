"""
testParser.py
"""

import re
import sys

class TestParser(object):

    def __init__(self, path):
        self.path = path
    
    def parse(self):
        # read the test case and remove comments, if any.
        test = {}
        with open(self.path) as text:
            rawText = text.read().split('\n')

        testText = self.removeComments(rawText)
        test['__rawText__'] = rawText
        test['path'] = self.path
        test['__emit__'] = []
        lines = testText.split('\n')
        i = 0
        # read a property in each loop cycle
        while(i < len(lines)):
            # skip blank lines
            if re.match('\A\s*\Z', lines[i]):
                test['__emit__'].append(("raw", rawText[i]))
                i += 1
                continue
            m = re.match('\A([^"]*?):\s*"([^"]*)"\s*\Z', lines[i])
            if m:
                test[m.group(1)] = m.group(2)
                test['__emit__'].append(("oneline", m.group(1)))
                i += 1
                continue
            m = re.match('\A([^"]*?):\s*"""\s*\Z', lines[i])
            if m:
                msg = []
                i += 1
                while(not re.match('\A\s*"""\s*\Z', lines[i])):
                    msg.append(rawText[i])
                    i += 1
                test[m.group(1)] = '\n'.join(msg)
                test['__emit__'].append(("multiline", m.group(1)))
                i += 1
                continue
            print('error parsing test file: %s' % self.path)
            sys.exit(1)
        return test
    
    def removeComments(self, rawText):
        # remove any portion of a line following a '#' symbol
        fixed_lines = []
        for l in rawText:
            idx = l.find('#')
            if idx == -1:
                fixed_lines.append(l)
            else:
                fixed_lines.append(l[0:idx])
        return '\n'.join(fixed_lines)