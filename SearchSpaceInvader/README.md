# **Space Invaders - Search**

Welcome to the Space Invaders Search Project!

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

In this project, your spaceship agent will employ search algorithms to navigate through an asteroid field, with the goal of destroying all the asteroids in order to win the game. The challenge involves finding the most efficient paths and strategies to target and destroy asteroids. You will design and implement general search algorithms and apply them to the Space Invaders-like gameplay mechanics where your agent must systematically clear the field of asteroids.

The project includes an autograder to test and evaluate your implementations based on different game scenarios. You can run the autograder using the command:

```bash
python autograder.py
```
The code for this project consists of several Python files, some of which you will need to read and understand in order to complete the assignment, and some of which you can ignore.

<!-- | **File**                    | **Description**                                                                                                                                                          |-->
| **Files to Edit**            |                                                    |
|-----------------------------|-----------------------------------------------------|
| `search.py`                  | Where all of your search algorithms will reside.   |
| `searchAgents.py`            | Where all of your search-based agents will reside. |
| **Files You Might Want to Look At** |                                                                                                                                                                          |
| `spaceship.py`               | The main file that runs Space Invaders games. This file describes a Space Invaders GameState type, which you use in this project. |
| `game.py`                    | The logic behind how the Space Invaders world works. This file describes several supporting types like `AgentState`, `Agent`, `Direction`, and `Grid`. |
| `util.py`                    | Includes useful data structures for implementing search algorithms. |
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
| `searchTestClasses.py`       | Search Project specific autograding test classes |

## **Welcome to Space Invaders**

After downloading the code, and changing to the directory, you should be able to play a game of Space Invaders by typing the following at the command line:
```bash
python spaceship.py
```
Note that `spaceship.py` supports a number of options that can each be expressed in a long way (e.g., `--layout`) or a short way (e.g., `-l`). You can see the list of all options and their default values via:
```bash 
python spaceship.py -h
```

## **Q1 (3 pts):Finding a Fixed Asteroid Dot using Depth First Search**
In `searchAgents.py`, you’ll find a fully implemented `SearchAgent`, which plans out a path through Space Invaders' world and then executes that path step-by-step. The search algorithms for formulating a plan are not implemented – that’s your job.

First, test that the `SearchAgent` is working correctly by running:
```bash
python spaceship.py -l tinyMaze -s SearchAgent -a fn=tinyMazeSearch
```

You are required to implement the **Depth-First Search (DFS)** algorithm in the `depthFirstSearch` function located in the `search.py` file. To ensure your algorithm is complete, make sure to use the **graph search** version of DFS. This means your implementation should avoid expanding any previously visited states.

#### *Instructions:*
Your implementation should be able to find a solution efficiently for the following commands:

```bash
python spaceship.py -l layout1 -s SearchAgent
python spaceship.py -l layout2 -s SearchAgent
python spaceship.py -l layout3 -s SearchAgent
```

#### *Important Notes:*
- Use the **Stack**, **Queue**, and **PriorityQueue** data structures provided in the `util.py` file. These structures have specific properties that are important for compatibility with the autograder and ensure the correct functionality of the search algorithms.
  
#### *Grading:*
To check if your DFS implementation passes all the required test cases, run the following command:

```bash
python autograder.py -q q1
```


## **Q2 (3 pts): Breadth First Search**
Your task is to implement the **Breadth-First Search (BFS)** algorithm in the `breadthFirstSearch` function found in `search.py`. As with the DFS implementation, make sure to write a **graph search** version of BFS that avoids revisiting any previously expanded states.

#### *Instructions:*
You should test your BFS implementation with the following commands:
```bash
python spaceship.py -l layout1 -s SearchAgent -a fn=bfs
python spaceship.py -l layout2 -s SearchAgent -a fn=bfs
python spaceship.py -l layout3 -s SearchAgent -a fn=bfs
```

#### *Key Questions:*
- **Does BFS guarantee the least cost solution?** If not, recheck your implementation to ensure it adheres to BFS principles.

#### *Grading:*
To verify that your BFS implementation passes all the required autograder tests, execute the following command:

```bash
python autograder.py -q q2
```

## **Q3 (3 pts): Varying the Cost Function**
In this task, you are required to implement the **Uniform-Cost Search (UCS)** algorithm in the `uniformCostSearch` function located in `search.py`. UCS is a graph search algorithm that can be modified with different cost functions to help the agent find "optimal" paths in terms of the total cost, rather than just the fewest steps.

#### *Instructions:*
We encourage you to explore `util.py` for data structures that can assist you in implementing UCS.

You should test your UCS implementation with the following commands:

```bash
python spaceship.py -l layout1 -s SearchAgent -a fn=ucs
python spaceship.py -l layout3 -s StayRightSearchAgent
python spaceship.py -l layout4 -s StayLeftSearchAgent
```

#### *Key Observations:*
- **For the StayRightSearchAgent**, you should observe low path costs due to the cost function's exponential behavior in asteroid-rich areas.
- **For the StayLeftSearchAgent**, expect high path costs due to the exponential increase in cost in enemy-ridden areas (see `searchAgents.py` for details).

#### *Grading:*
Run the following command to verify that your UCS implementation passes all required autograder test cases:

```bash
python autograder.py -q q3
```
## **Q4 (3 pts): A\* search**
In this task, you are required to implement the **A\* Graph Search** algorithm in the `aStarSearch` function located in `search.py`. A* is an informed search algorithm that combines the strengths of both **uniform-cost search** and **greedy search** by using a heuristic to guide the search process.

#### *Instructions:*
A* takes a **heuristic function** as an argument. The heuristic function evaluates the cost of reaching the goal from a given state and should take two arguments: the state itself and the problem. A trivial example of a heuristic function, `nullHeuristic`, is already provided in `search.py`.

To test your A* implementation, use the following command:
```bash
python spaceship.py -l layout3 -s SearchAgent -a fn=astar,heuristic=semimanhattanHeuristic
```
This command should use the **Semi Manhattan distance heuristic** (implemented as `semimanhattanHeuristic` in `searchAgents.py`) and will help you observe the behavior of A* in comparison to other search algorithms.

#### *Key Observations:*
**A\*** should find the optimal solution slightly faster than **Uniform-Cost Search (UCS)**. In our implementation, A* expands around **45 search nodes**, whereas UCS expands **386 nodes**. However, the exact number of nodes expanded may vary slightly due to tie-breaking in priority queues.

#### *Grading:*
To verify that your A* implementation passes all autograder test cases, run the following command:

```bash
python autograder.py -q q4
```

## **Q5 (3 pts): Finding All the Corners**

In this task, you will implement the **CornersProblem** in `searchAgents.py`. The goal of this problem is to find the smallest cost actions through the layout that destroys the top left and top right corner asteroids.

*Note:* Make sure to complete Question 2 before working on Question 5, because Question 5 builds upon your answer for Question 2.

#### *Instructions:*

1. **State Representation:**
   - Design an abstract state representation that encodes only the necessary information: the current position of Spaceship and the corners destroyed so far.
   - Avoid including irrelevant details, such as the position of enemies. Using the `Spaceship GameState` as a search state will lead to incorrect and inefficient solutions.

2. **Implementation:**
   - Define the `CornersProblem` class to represent the search problem as a whole. 
   - Create a state representation (e.g., a tuple or set) that captures the information about Spaceship’s current position and the corners destroyed so far.
   - In the `getSuccessors` function, ensure that each successor state is added to the list with a cost of **1**.

3. **Testing:**
   - Test your implementation using the following commands:
     ```bash
     python spaceship.py -l layout5 -s SearchAgent -a fn=bfs,prob=CornersProblem
     ```

   - Observe how your search agent solves this problem efficiently by destroying the top left and top right asteroids of the layout.

#### *Hints:*
- **Hint 1:** The only relevant parts of the game state for this problem are the starting Spaceship position and the locations of the top left and top right corners.
- **Hint 2:** When implementing `getSuccessors`, make sure to include child nodes in the `successors` list with a **cost of 1**.

#### *Grading:*
To verify your implementation, run the following autograder command:

```bash
python autograder.py -q q5
```

## **Q6 (3 pts): Corners Problem: Heuristic**
Note: Make sure to complete Question 4 before working on Question 6, because Question 6 builds upon your answer for Question 4.

Your task is to implement a **non-trivial and consistent heuristic** for the `CornersProblem` in the function `cornersHeuristic`, located in `searchAgents.py`. This heuristic will guide the A* search algorithm in solving the CornersProblem efficiently.

#### *Instructions:*

1. **Designing the Heuristic:**
   - Create a heuristic function that estimates the cost to destroy the top left and top right corners from the current state.
   - Ensure that your heuristic is **consistent** to guarantee optimality when used with A* search.
   - Avoid trivial heuristics (like returning 0 for all states) to achieve better performance.

2. **Testing the Heuristic:**
   - Use the following command to test your heuristic with the A* search algorithm:
     ```bash
     python spaceship.py -l layout5 -s AStarCornersAgent
     ```

   - Here, `AStarCornersAgent` is equivalent to using:
     ```bash
     -s SearchAgent -a fn=aStarSearch,prob=CornersProblem,heuristic=cornersHeuristic
     ```
*Remember:* If your heuristic is inconsistent, you will receive no credit, so be careful!

#### *Grading:*
To verify your heuristic and its consistency, run the following autograder command:

```bash
python autograder.py -q q6
```

## **Q7 (4 pts): Eating All The Dots**
Note: Make sure to complete Question 4 before working on Question 7, because Question 7 builds upon your answer for Question 4.

In this task, you'll create a **consistent heuristic** for the `AsteroidSearchProblem` in the `asteroidHeuristic` function within `searchAgents.py`. This heuristic will help solve the asteroid-destroying problem, where Spaceship destroys all the asteroid in the layout efficiently.

#### *Problem Definition:*
- The `AsteroidSearchProblem` (already implemented in `searchAgents.py`) defines the objective of destroy all asteroids in the Space Invaders world.
- Your goal is to implement a **non-trivial, non-negative, and consistent heuristic** to guide the A* search algorithm in solving this problem.

#### *Implementation Instructions:*
1. **Define the Heuristic:**
   - Your heuristic should estimate the cost to destroy all remaining asteroids.
   - Ensure that:
     - The heuristic value at any goal state is `0`.
     - The heuristic never returns a negative value.
     - The heuristic is **consistent** to ensure optimality with A*.

2. **Testing Your Heuristic:**
   - Use the following command to test your heuristic with the A* search algorithm:
     ```bash
     python spaceship.py -l layout7 -s AStarAsteroidSearchAgent
     ```
   - Here, `AStarAsteroidSearchAgent` is equivalent to using:
     ```bash
     -s SearchAgent -a fn=astar,prob=AsteroidSearchProblem,heuristic=asteroidHeuristic
     ```

3. **Scoring Based on Nodes Expanded:**
   - Your heuristic will be graded based on the number of nodes expanded during the search:
     | **Number of Nodes Expanded** | **Grade**             |
     |-------------------------------|-----------------------|
     | More than 3,000              | 1/4 (basic)          |
     | At most 3,000                | 2/4                  |
     | At most 2,800                | 3/4                  |
     | At most 2,600                 | 4/4 (full credit)    |
     | At most 2,400                 | 5/4 (extra credit)   |

   - To achieve full credit or extra credit, focus on designing an efficient heuristic that minimizes node expansion.


#### *Grading:*
To ensure your heuristic is consistent and passes all test cases, run the autograder with the following command:

```bash
python autograder.py -q q7
```

## **Q8 (3 pts): Suboptimal Search**
In this task, you will implement a function that allows the Spaceship agent to **greedily destroys the closest dot**. While this approach may not always find the shortest path through all dots, it provides a reasonably good path in a shorter time.

#### *Task Details:*
1. **Function to Implement:**
   - Fill in the `findPathToClosestDot` function in `searchAgents.py`.
   - This function should return a path to the nearest dot (asteroid).

2. **Key Hint:**
   - The easiest way to implement `findPathToClosestDot` is by completing the `AnyFoodSearchProblem` class, which is missing its goal test.
   - Once the goal test is implemented, you can solve the problem using an appropriate search algorithm (like BFS or UCS).
   - The solution should be concise and efficient.

3. **Testing the ClosestDotSearchAgent:**
   - Use the following command to test your implementation:
     ```bash
     python spaceship.py -l layout8 -s ClosestDotSearchAgent
     ```
   - The agent will navigate through the layout, greedily destroying the closest dot at every step.

4. **Understanding Limitations:**
   - The `ClosestDotSearchAgent` does not always guarantee the shortest path through all dots because it makes local greedy decisions.

5. **Grading:**
   - Verify your implementation by running the autograder:
     ```bash
     python autograder.py -q q8
     ```
   - This will check if your implementation works correctly and passes all test cases.


