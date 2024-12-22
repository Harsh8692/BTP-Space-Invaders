# **Space Invaders - Multiagent**

Welcome to the Space Invaders Multiagent Project!

## **Installation Guide**

To run the project, ensure you have the following prerequisites and dependencies installed on your system.

### **Prerequisites**

1. **Python**:  
   - Required version: Python 3.7 or higher.  
   - Download and install from the [official Python website](https://www.python.org/downloads/).

2. **Pygame**:  
   - Required to render the game’s graphical interface.
   - `pip install pygame`

## **Introduction**

In this project, you will design agents for the classic version of Space Invaders, including enemies. Along the way, you will implement both minimax and expectimax search and try your hand at evaluation function design.

The code base has not changed much from the previous project, but please start with a fresh installation, rather than intermingling files from Search Project.

The project includes an autograder to test and evaluate your implementations based on different game scenarios. You can run the autograder using the command:

```bash
python autograder.py
```
The code for this project consists of several Python files, some of which you will need to read and understand in order to complete the assignment, and some of which you can ignore.

<!-- | **File**                    | **Description**                                                                                                                                                          |-->
| **Files to Edit**            |                                                    |
|-----------------------------|-----------------------------------------------------|
| `multiAgents.py`            | Where all of your multi-agent search agents will reside. |
| **Files You Might Want to Look At** |                                                                                                                                                                          |
| `spaceship.py`               | The main file that runs Space Invaders games. This file describes a Space Invaders GameState type, which you will use in this project. |
| `game.py`                    | The logic behind how the Space Invaders world works. This file describes several supporting types like `AgentState`, `Agent`, `Direction`, and `Grid`. |
| `util.py`                    | Includes useful data structures for implementing search algorithms. You don't need to use these for this project, but may find other functions defined here to be useful. |
| **Supporting Files You Can Ignore** |                                                                                                                                                                          |
| `graphicsDisplay.py`         | Graphics for Space Invaders|
| `textDisplay.py`             | ASCII graphics for Space Invaders |
| `enemyAgents.py`             | Agents to control enemies |
| `bulletAgents.py`            | Agents to control bullets |
| `keyboardAgents.py`          | Keyboard interfaces to control Space Invaders |
| `layout.py`                  | Code for reading layout files and storing their contents |
| `autograder.py`              | Project autograder |
| `testParser.py`              | Parses autograder test and solution files |
| `testClasses.py`             | General autograding test classes |
| `test_cases/`                | Directory containing the test cases for each question |
| `multiagentTestClasses.py`   | Multiagent Project specific autograding test classes |

## **Welcome to Multi-Agent Space Invaders**

First, play a game of classic Space Invaders by running the following command:
```bash
python spaceship.py
```
and using the arrow keys to move and spacebar to fire. Now, run the provided `ReflexAgent` in `multiAgents.py`
```bash
python spaceship.py -s ReflexAgent
```
Note that it plays quite poorly even on simple layouts:
```bash
python spaceship.py -s ReflexAgent -l testClassic
```
Inspect its code (in `multiAgents.py`) and make sure you understand what it’s doing.

## **Q1 (4 pts): Reflex Agent**
In this task, you'll enhance the `ReflexAgent` in `multiAgents.py` to perform significantly better in navigating the Space Invaders world. The provided starter code includes examples of querying the `GameState` for information, which you can use to design an effective agent. A good `ReflexAgent` should evaluate asteroid locations, enemy positions and enemy bullets positions to make intelligent decisions.


#### *Task Instructions:*
1. **Objective:**
   - Implement an improved `ReflexAgent` capable of clearing layouts like `testClassic`.

2. **Testing Your ReflexAgent:**
   - Run the agent on the `testClassic` layout:
     ```bash
     python spaceship.py -s ReflexAgent -l testClassic
     ```

3. **Evaluation Function:**
   - Your `ReflexAgent` will evaluate state-action pairs using an evaluation function. Incorporate features like:
     - **Asteroid Distance:** Prefer moves that reduce the distance to asteroids (using the reciprocal of the distance may improve results).
     - **Enemy Distance:** Avoid moves that lead to enemies, especially when they are close.
     - **Enemies Bullets Distance:** Avoid moves that lead to enemies bullets, especially when they are close.
     - **Asteroid Locations:** Use `newAsteroid.asList()` to access asteroids positions effectively.
   - Debugging Tip: Print object representations for insights, e.g., `print(newEnemyStates)`.


#### *Grading:*
1. Your agent will be evaluated on the `openClassic` layout over 10 games.
   - **Conditions for Scoring:**
     - **0 Points:** The agent times out or never wins.
     - **1 Point:** Wins at least 5 games.
     - **2 Points:** Wins all 10 games.
   - **Bonus Points:**
     - **+1 Point:** Average score > 1000.
     - **+2 Points:** Average score > 1400.

2. Use the autograder to check your implementation:
   - With graphics:
     ```bash
     python autograder.py -q q1
     ```
   - Without graphics:
     ```bash
     python autograder.py -q q1 --no-graphics
     ```

#### *Notes and Tips:*
- The default enemies move randomly, but you can test against smarter enemies using the `DirectionalAgent` option.
- Consider features like enemy proximity and asteroid distribution to improve the reflex agent's evaluation.
- Experiment with reciprocal values (e.g., `1/distance`) to emphasize closeness to asteroid or threats.

## **Q2 (5 pts): Minimax**
In this task, you will implement the `MinimaxAgent` class in `multiAgents.py` to handle adversarial search in the game environment. The agent should expand the game tree to an arbitrary depth and evaluate the leaves using the provided `self.evaluationFunction`. By default, the evaluation function uses `scoreEvaluationFunction`.


#### *Key Details:*
1. **Agent Behavior:**
   - **Spaceship (Max Agent):** Acts to maximize its score.
   - **Enemies (Min Agents):** Respond to minimize the spaceship's score.
   - **Bullets:** Move deterministically (upward or downward) and are considered after spaceship and enemy moves at each depth.

2. **Depth:**
   - A single ply includes:
     - One move from the **Spaceship** (Max Agent).
     - Responses from all **enemies** (Min Agents).
     - Movements from all **bullets**.
   - For example, a depth of 2 includes two full cycles of spaceship moves, enemy responses, and bullet movements.

3. **Implementation Notes:**
   - Use `self.depth` and `self.evaluationFunction` to guide your implementation.
   - The `self.evaluationFunction` evaluates states rather than actions, as opposed to reflex agents.

4. **Hints for Implementation:**
   - Use a recursive helper function to construct the minimax tree.
   - Your implementation must adhere strictly to the expected number of calls to `GameState.generateSuccessor`. Deviations may cause the autograder to fail.
   - It is normal for the spaceship to lose in some scenarios; this reflects correct behavior. To visualize it you can try running
     ```bash
     python spaceship.py -s MinimaxAgent -a depth=2 -l layout9
     ```


#### *Testing and Debugging:*
1. Run the following command to test your implementation:
   ```bash
   python autograder.py -q q2
   ```

## **Q3 (5 pts): Alpha-Beta Pruning**
In this task, you will implement the `AlphaBetaAgent` class in `multiAgents.py` to efficiently perform minimax search using alpha-beta pruning. The goal is to optimize the exploration of the game tree while maintaining the same minimax values as the `MinimaxAgent`. Note that the specific actions chosen may differ due to varying tie-breaking behavior.


#### *Key Details:*
1. **Alpha-Beta Pruning:**
   - The algorithm uses **alpha** (the best score the maximizer can guarantee) and **beta** (the best score the minimizer can guarantee) to prune branches that will not affect the final decision.
   - Successor states are processed in the order returned by `GameState.getLegalActions`.

2. **Behavior Consistency:**
   - The agent must **not prune on equality** to ensure compatibility with the autograder's grading logic.

3. **Implementation Notes:**
   - Avoid unnecessary calls to `GameState.generateSuccessor`.
   - Do not reorder successor states; process them as returned by `GameState.getLegalActions`.

4. **Expected Outcome:**
   - Some tests will result in the spaceship losing; this reflects correct behavior and will still pass the tests. To visualize it you can try running
   ```bash
   python spaceship.py -s AlphaBetaAgent -a depth=2 -l layout9
   ```


#### *Testing and Debugging:*
1. Run the following command to test your implementation:
   ```bash
   python autograder.py -q q3
   ```

## **Q4 (5 pts): Expectimax**
In this task, you will implement the `ExpectimaxAgent` class in `multiAgents.py`. Unlike `MinimaxAgent` or `AlphaBetaAgent`, the `ExpectimaxAgent` models adversaries as probabilistic agents who choose actions uniformly at random instead of always playing optimally. This makes the algorithm more suited for situations with non-deterministic or suboptimal opponents.

#### *Key Details:*
1. **Expectimax Algorithm:**
   - Replaces the minimization step for adversaries with an **expectation** step based on the average of possible outcomes.
   - The agent assumes that adversaries choose actions uniformly at random from their `getLegalActions`.

2. **Correct Behavior:**
   - The correct implementation may result in Spaceship losing some tests, as it is designed to handle probabilistic scenarios, not guarantee a win. To visualize it you can try running
   ```bash
   python spaceship.py -s ExpectimaxAgent -a depth=2 -l layout9
   ```

3. **Implementation Tips:**
   - Expectimax follows a similar structure to minimax but replaces the `min` calculation with an **average** of values weighted by probability.
   - Use helper functions for recursion to manage the tree depth and switch between maximizing (Spaceship) and expectation (adversaries) layers.


#### *Testing and Debugging:*
1. Use the following command to run the autograder with small, manageable test cases:
   ```bash
   python autograder.py -q q4
   ```

## **Q5 (5 pts): Evaluation Function**
In this task, you will develop a better evaluation function in `betterEvaluationFunction` within `multiAgents.py`. This function will evaluate **states** rather than **actions** (as done by the reflex agent). A well-designed evaluation function is crucial for effective gameplay in Space Invaders, particularly when using depth-2 search.

#### *Requirements for the Evaluation Function:*
1. **State Evaluation:**
   - The evaluation function should balance different aspects of the game, such as:
     - Proximity to enemies.
     - Avoidance of enemy fire.
     - Maximizing score by targeting valuable enemies or bonuses.

2. **Performance Criteria:**
   - With depth-2 search, the agent must clear the `smallClassic` layout with one random enemy:
     - Win **at least 50% of games**.
     - Maintain **reasonable computation speed**.
     - Achieve an **average score of around 1300 points** during wins.


#### *Grading Criteria:*
The autograder evaluates the agent over **10 games** on the `smallClassic` layout with one random enemy:
1. **Basic Success:**
   - Win at least **1 game** without timing out to earn **1 point**.
   - Agents failing this will receive **0 points**.
2. **Win Consistency:**
   - **+1 point** for winning **at least 5 games**.
   - **+2 points** for winning **all 10 games**.
3. **Score Performance:**
   - **+1 point** for an **average score of at least 1000**.
   - **+2 points** for an **average score of at least 1300** (including scores from losses).


#### *Running the Autograder:*
To test your evaluation function under these conditions, use the following command:
```bash
python autograder.py -q q5
```
