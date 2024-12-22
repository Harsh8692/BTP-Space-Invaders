"""
multiagentTestClasses.py
"""
import time
import testClasses
import spaceship
import layout
import random
from enemyAgents import RandomAgent, DirectionalAgent
from collections import defaultdict
import json
from game import Agent
from spaceship import GameState

class EvalAgentTest(testClasses.TestCase):

    def __init__(self, question, testDict):
        super(EvalAgentTest, self).__init__(question, testDict)
        self.layoutName = testDict['layoutName']
        self.agentName = testDict['agentName']
        self.enemies = eval(testDict['enemies'])
        self.maxTime = int(testDict['maxTime'])
        self.seed = int(testDict['randomSeed'])
        self.numGames = int(testDict['numGames'])

        self.scoreMinimum = int(
            testDict['scoreMinimum']) if 'scoreMinimum' in testDict else None
        self.nonTimeoutMinimum = int(
            testDict['nonTimeoutMinimum']) if 'nonTimeoutMinimum' in testDict else None
        self.winsMinimum = int(
            testDict['winsMinimum']) if 'winsMinimum' in testDict else None

        self.scoreThresholds = [int(s) for s in testDict.get(
            'scoreThresholds', '').split()]
        self.nonTimeoutThresholds = [int(s) for s in testDict.get(
            'nonTimeoutThresholds', '').split()]
        self.winsThresholds = [int(s) for s in testDict.get(
            'winsThresholds', '').split()]

        self.maxPoints = sum([len(t) for t in [
                             self.scoreThresholds, self.nonTimeoutThresholds, self.winsThresholds]])
        self.agentArgs = testDict.get('agentArgs', '')

    def execute(self, grades, moduleDict, solutionDict):
        startTime = time.time()

        agentType = getattr(moduleDict['multiAgents'], self.agentName)
        agentOpts = spaceship.parseAgentArgs(self.agentArgs) if self.agentArgs != '' else {}
        agent = agentType(**agentOpts)

        lay = layout.getLayout(self.layoutName)

        disp = self.question.getDisplay()

        random.seed(self.seed)
        games = spaceship.run_games(agent, self.numGames, self.enemies, lay, disp)
        
        totalTime = time.time() - startTime

        stats = {'time': totalTime, 'wins': [g.state.isWin() for g in games].count(True),
                 'games': games, 'scores': [g.state.getScore() for g in games],
                }

        averageScore = sum(stats['scores']) / float(len(stats['scores']))
        wins = stats['wins']

        def gradeThreshold(value, minimum, thresholds, name):
            points = 0
            passed = (minimum == None) or (value >= minimum)
            if passed:
                for t in thresholds:
                    if value >= t:
                        points += 1
            return (passed, points, value, minimum, thresholds, name)

        results = [gradeThreshold(averageScore, self.scoreMinimum, self.scoreThresholds, "average score"),
                   gradeThreshold(wins, self.winsMinimum, self.winsThresholds, "wins")]

        totalPoints = 0
        for passed, points, value, minimum, thresholds, name in results:
            if minimum == None and len(thresholds) == 0:
                continue

            # print passed, points, value, minimum, thresholds, name
            totalPoints += points
            if not passed:
                assert points == 0
                self.addMessage(
                    "%s %s (fail: below minimum value %s)" % (value, name, minimum))
            else:
                self.addMessage("%s %s (%s of %s points)" %
                                (value, name, points, len(thresholds)))

            if minimum != None:
                self.addMessage("    Grading scheme:")
                self.addMessage("     < %s:  fail" % (minimum,))
                if len(thresholds) == 0 or minimum != thresholds[0]:
                    self.addMessage("    >= %s:  0 points" % (minimum,))
                for idx, threshold in enumerate(thresholds):
                    self.addMessage("    >= %s:  %s points" %
                                    (threshold, idx+1))
            elif len(thresholds) > 0:
                self.addMessage("    Grading scheme:")
                self.addMessage("     < %s:  0 points" % (thresholds[0],))
                for idx, threshold in enumerate(thresholds):
                    self.addMessage("    >= %s:  %s points" %
                                    (threshold, idx+1))

        if any([not passed for passed, _, _, _, _, _ in results]):
            totalPoints = 0

        return self.testPartial(grades, totalPoints, self.maxPoints)

    def writeSolution(self, moduleDict, filePath):
        handle = open(filePath, 'w')
        handle.write('# This is the solution file for %s.\n' % self.path)
        handle.write('# File intentionally blank.\n')
        handle.close()
        return True

VERBOSE = False


class MultiagentTreeState(object):
    def __init__(self, problem, state):
        self.problem = problem
        self.state = state

    def generateSuccessor(self, agentIndex, action):
        if VERBOSE:
            print("generateSuccessor(%s, %s, %s) -> %s" % (self.state, agentIndex,
                                                           action, self.problem.stateToSuccessorMap[self.state][action]))
        successor = self.problem.stateToSuccessorMap[self.state][action]
        self.problem.generatedStates.add(successor)
        return MultiagentTreeState(self.problem, successor)
    
    def getNumMinMaxAgents(self):
        return self.problem.numAgents
    
    def getBulletAgents(self):
        return []

    def getMinMaxAgents(self):
        return [i for i in range(self.problem.numAgents)]

    def getScore(self):
        if VERBOSE:
            print("getScore(%s) -> %s" %
                  (self.state, self.problem.evaluation[self.state]))
        if self.state not in self.problem.evaluation:
            raise Exception(
                'getScore() called on non-terminal state or before maximum depth achieved.')
        return float(self.problem.evaluation[self.state])

    def getLegalActions(self, agentIndex=0):
        if VERBOSE:
            print("getLegalActions(%s) -> %s" %
                  (self.state, self.problem.stateToActions[self.state]))
        return list(self.problem.stateToActions[self.state])

    def isWin(self):
        if VERBOSE:
            print("isWin(%s) -> %s" %
                  (self.state, self.state in self.problem.winStates))
        return self.state in self.problem.winStates

    def isLose(self):
        if VERBOSE:
            print("isLose(%s) -> %s" %
                  (self.state, self.state in self.problem.loseStates))
        return self.state in self.problem.loseStates

    def getNumAgents(self):
        if VERBOSE:
            print("getNumAgents(%s) -> %s" %
                  (self.state, self.problem.numAgents))
        return self.problem.numAgents

    
class MultiagentTreeProblem(object):
    def __init__(self, numAgents, startState, winStates, loseStates, successors, evaluation):
        self.startState = MultiagentTreeState(self, startState)

        self.numAgents = numAgents
        self.winStates = winStates
        self.loseStates = loseStates
        self.evaluation = evaluation
        self.successors = successors

        self.reset()

        self.stateToSuccessorMap = defaultdict(dict)
        self.stateToActions = defaultdict(list)
        for state, action, nextState in successors:
            self.stateToActions[state].append(action)
            self.stateToSuccessorMap[state][action] = nextState

    def reset(self):
        self.generatedStates = set([self.startState.state])


def parseTreeProblem(testDict):
    numAgents = int(testDict["num_agents"])
    startState = testDict["start_state"]
    winStates = set(testDict["win_states"].split(" "))
    loseStates = set(testDict["lose_states"].split(" "))
    successors = []

    evaluation = {}
    for line in testDict["evaluation"].split('\n'):
        tokens = line.split()
        if len(tokens) == 2:
            state, value = tokens
            evaluation[state] = float(value)
        else:
            raise Exception("[parseTree] Bad evaluation line: |%s|" % (line,))

    for line in testDict["successors"].split('\n'):
        tokens = line.split()
        if len(tokens) == 3:
            state, action, nextState = tokens
            successors.append((state, action, nextState))
        else:
            raise Exception("[parseTree] Bad successor line: |%s|" % (line,))

    return MultiagentTreeProblem(numAgents, startState, winStates, loseStates, successors, evaluation)


class GraphGameTreeTest(testClasses.TestCase):

    def __init__(self, question, testDict):
        super(GraphGameTreeTest, self).__init__(question, testDict)
        self.problem = parseTreeProblem(testDict)
        self.alg = self.testDict['alg']
        self.diagram = self.testDict['diagram'].split('\n')
        self.depth = int(self.testDict['depth'])

    def solveProblem(self, multiAgents):
        self.problem.reset()
        studentAgent = getattr(multiAgents, self.alg)(depth=self.depth)
        action = studentAgent.getAction(self.problem.startState)
        generated = self.problem.generatedStates
        return action, " ".join([str(s) for s in sorted(generated)])

    def addDiagram(self):
        self.addMessage('Tree:')
        for line in self.diagram:
            self.addMessage(line)

    def execute(self, grades, moduleDict, solutionDict):
        multiAgents = moduleDict['multiAgents']
        goldAction = solutionDict['action']
        goldGenerated = solutionDict['generated']
        action, generated = self.solveProblem(multiAgents)

        fail = False
        if action != goldAction:
            self.addMessage('Incorrect move for depth=%s' % (self.depth,))
            self.addMessage(
                '    Student move: %s\n    Optimal move: %s' % (action, goldAction))
            fail = True

        if generated != goldGenerated:
            self.addMessage(
                'Incorrect generated nodes for depth=%s' % (self.depth,))
            self.addMessage('    Student generated nodes: %s\n    Correct generated nodes: %s' % (
                generated, goldGenerated))
            fail = True

        if fail:
            self.addDiagram()
            return self.testFail(grades)
        else:
            return self.testPass(grades)

    def writeSolution(self, moduleDict, filePath):
        multiAgents = moduleDict['multiAgents']
        action, generated = self.solveProblem(multiAgents)
        with open(filePath, 'w') as handle:
            handle.write('# This is the solution file for %s.\n' % self.path)
            handle.write('action: "%s"\n' % (action,))
            handle.write('generated: "%s"\n' % (generated,))
        return True
    
class GradingAgent(Agent):
    def __init__(self, seed, studentAgent, optimalActions, altDepthActions, partialPlyBugActions):
        # save student agent and actions of refernce agents
        self.studentAgent = studentAgent
        self.optimalActions = optimalActions
        self.altDepthActions = altDepthActions
        self.partialPlyBugActions = partialPlyBugActions
        # create fields for storing specific wrong actions
        self.suboptimalMoves = []
        self.wrongStatesExplored = -1
        # boolean vectors represent types of implementation the student could have
        self.actionsConsistentWithOptimal = [
            True for i in range(len(optimalActions[0]))]
        self.actionsConsistentWithAlternativeDepth = [
            True for i in range(len(altDepthActions[0]))]
        self.actionsConsistentWithPartialPlyBug = [
            True for i in range(len(partialPlyBugActions[0]))]
        # keep track of elapsed moves
        self.stepCount = 0
        self.seed = seed

    def registerInitialState(self, state):
        if 'registerInitialState' in dir(self.studentAgent):
            self.studentAgent.registerInitialState(state)
        random.seed(self.seed)

    def getAction(self, state, agentIndex=0):
        GameState.getAndResetExplored()
        studentAction = (self.studentAgent.getAction(state),
                         len(GameState.getAndResetExplored()))
        optimalActions = self.optimalActions[self.stepCount]
        altDepthActions = self.altDepthActions[self.stepCount]
        partialPlyBugActions = self.partialPlyBugActions[self.stepCount]
        studentOptimalAction = False
        curRightStatesExplored = False
        for i in range(len(optimalActions)):
            if studentAction[0] in optimalActions[i][0]:
                studentOptimalAction = True
            else:
                self.actionsConsistentWithOptimal[i] = False
            if studentAction[1] == int(optimalActions[i][1]):
                curRightStatesExplored = True
        if not curRightStatesExplored and self.wrongStatesExplored < 0:
            self.wrongStatesExplored = 1
        for i in range(len(altDepthActions)):
            if studentAction[0] not in altDepthActions[i]:
                self.actionsConsistentWithAlternativeDepth[i] = False
        for i in range(len(partialPlyBugActions)):
            if studentAction[0] not in partialPlyBugActions[i]:
                self.actionsConsistentWithPartialPlyBug[i] = False
        if not studentOptimalAction:
            self.suboptimalMoves.append(
                (state, studentAction[0], optimalActions[0][0][0]))
        self.stepCount += 1
        random.seed(self.seed + self.stepCount)
        return optimalActions[0][0][0]

    def getSuboptimalMoves(self):
        return self.suboptimalMoves

    def getWrongStatesExplored(self):
        return self.wrongStatesExplored

    def checkFailure(self):
        """
        Return +n if have n suboptimal moves.
        Return -1 if have only off by one depth moves.
        Return 0 otherwise.
        """
        if self.wrongStatesExplored > 0:
            return -3
        if self.actionsConsistentWithOptimal.count(True) > 0:
            return 0
        elif self.actionsConsistentWithPartialPlyBug.count(True) > 0:
            return -2
        elif self.actionsConsistentWithAlternativeDepth.count(True) > 0:
            return -1
        else:
            return len(self.suboptimalMoves)
        
