
from pacai.util import reflection
import random
from pacai.agents.capture.capture import CaptureAgent
from pacai.core import distance
from pacai.core.directions import Directions


class DefenseAgent(CaptureAgent):
    """
    A Dummy agent to serve as an example of the necessary agent structure.
    You should look at `pacai.core.baselineTeam` for more details about how to create an agent.
    """

    def __init__(self, index, **kwargs):
        super().__init__(index)

    def registerInitialState(self, gameState):
        """
        This method handles the initial setup of the agent and populates useful fields,
        such as the team the agent is on and the `pacai.core.distanceCalculator.Distancer`.

        IMPORTANT: If this method runs for more than 15 seconds, your agent will time out.
        """

        super().registerInitialState(gameState)
        self.isRed = gameState.isOnRedTeam(self.index)
        # Your initialization code goes here, if you need any.
        midpoint_list = []
        layout = gameState.getInitialLayout()
        layout_height = layout.getHeight()
        layout_width = layout.getWidth()
        walls = gameState.getWalls()

        mid_x_coord = layout_width // 2
        if self.red:
            mid_x_coord -= 1

        for i in range(1, layout_height):
            if not walls[mid_x_coord][i]:
                midpoint_list.append((mid_x_coord, i))

        self.midpoint = midpoint_list[len(midpoint_list) // 2]

    def chooseAction(self, gameState):
        # Collect legal moves.
        legalMoves = gameState.getLegalActions(self.index)
        if Directions.STOP in legalMoves:
            legalMoves.remove(Directions.STOP)

        # Choose one of the best actions.
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices)  # Pick randomly among the best.

        return legalMoves[chosenIndex]

    def getOppFood(self, gameState):
        if self.isRed:
            return gameState.getBlueFood()
        else:
            return gameState.getRedFood()

    def getOppGhost(self, gameState):
        if self.isRed:
            blueIndices = gameState.getBlueTeamIndices()
            oppPos = [gameState.getAgentPosition(idx) for idx in blueIndices]
            blueGhostPos = [pos for pos in oppPos if gameState.isOnBlueSide(pos)]
            return blueGhostPos
        else:
            redIndices = gameState.getRedTeamIndices()
            oppPos = [gameState.getAgentPosition(idx) for idx in redIndices]
            redGhostPos = [pos for pos in oppPos if gameState.isOnRedSide(pos)]
            return redGhostPos

    def getOppPacman(self, gameState):
        if self.isRed:
            blueIndices = gameState.getBlueTeamIndices()
            oppPos = [gameState.getAgentPosition(idx) for idx in blueIndices]
            blueGhostPos = [pos for pos in oppPos if gameState.isOnRedSide(pos)]
            return blueGhostPos
        else:
            redIndices = gameState.getRedTeamIndices()
            oppPos = [gameState.getAgentPosition(idx) for idx in redIndices]
            redGhostPos = [pos for pos in oppPos if gameState.isOnBlueSide(pos)]
            return redGhostPos

    def onOppositeSide(self, position, gameState):
        if self.isRed:
            return gameState.isOnBlueSide(position)
        else:
            return gameState.isOnRedSide(position)


    def evaluationFunction(self, currentGameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current `pacai.bin.pacman.PacmanGameState`
        and an action, and returns a number, where higher numbers are better.
        Make sure to understand the range of different values before you combine them
        in your evaluation function.
        """

        successorGameState = currentGameState.generateSuccessor(self.index, action)

        # Useful information you can extract.
        newPosition = successorGameState.getAgentPosition(self.index)
        oldFood = self.getOppFood(currentGameState)
        oldOppPacmanPositions = self.getOppPacman(currentGameState)
        # newScaredTimes = [ghostState.getScaredTimer() for ghostState in newGhostStates]

        if self.onOppositeSide(newPosition, successorGameState):
            return -1000

        if len(oldOppPacmanPositions) == 0:
            return -1 * distance.maze(self.midpoint, newPosition, successorGameState)

        return -1 * distance.maze(oldOppPacmanPositions[0], newPosition, successorGameState)


class HybridAgent(CaptureAgent):

    def __init__(self, index, **kwargs):
        super().__init__(index)

    def registerInitialState(self, gameState):
        super().registerInitialState(gameState)
        self.isRed = gameState.isOnRedTeam(self.index)
        # Your initialization code goes here, if you need any.
        midpoint_list = []
        layout = gameState.getInitialLayout()
        layout_height = layout.getHeight()
        layout_width = layout.getWidth()
        walls = gameState.getWalls()

        mid_x_coord = layout_width // 2
        if self.red:
            mid_x_coord -= 1

        for i in range(1, layout_height):
            if not walls[mid_x_coord][i]:
                midpoint_list.append((mid_x_coord, i))

        self.midpoint = midpoint_list[len(midpoint_list) // 2]

    def chooseAction(self, gameState):
        # Collect legal moves.
        legalMoves = gameState.getLegalActions(self.index)
        if Directions.STOP in legalMoves:
            legalMoves.remove(Directions.STOP)

        # Choose one of the best actions.
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices)  # Pick randomly among the best.

        return legalMoves[chosenIndex]

    def getOppFood(self, gameState):
        if self.isRed:
            return gameState.getBlueFood()
        else:
            return gameState.getRedFood()

    def getOppGhost(self, gameState):
        if self.isRed:
            blueIndices = gameState.getBlueTeamIndices()
            oppPos = [gameState.getAgentPosition(idx) for idx in blueIndices]
            blueGhostPos = [pos for pos in oppPos if gameState.isOnBlueSide(pos)]
            return blueGhostPos
        else:
            redIndices = gameState.getRedTeamIndices()
            oppPos = [gameState.getAgentPosition(idx) for idx in redIndices]
            redGhostPos = [pos for pos in oppPos if gameState.isOnRedSide(pos)]
            return redGhostPos

    def getOppPacman(self, gameState):
        if self.isRed:
            blueIndices = gameState.getBlueTeamIndices()
            oppPos = [gameState.getAgentPosition(idx) for idx in blueIndices]
            blueGhostPos = [pos for pos in oppPos if gameState.isOnRedSide(pos)]
            return blueGhostPos
        else:
            redIndices = gameState.getRedTeamIndices()
            oppPos = [gameState.getAgentPosition(idx) for idx in redIndices]
            redGhostPos = [pos for pos in oppPos if gameState.isOnBlueSide(pos)]
            return redGhostPos

    def getOppGhostState(self, gameState):
        """
        Returns list of opponent ghost states
        """
        if self.isRed:
            blueGhostState = []
            blueIndices = gameState.getBlueTeamIndices()
            for idx in blueIndices:
                if gameState.isOnBlueSide(gameState.getAgentPosition(idx)):
                    blueGhostState.append(gameState.getAgentState(idx))
            return blueGhostState
        else:
            redGhostState = []
            redIndices = gameState.getRedTeamIndices()
            for idx in redIndices:
                if gameState.isOnRedSide(gameState.getAgentPosition(idx)):
                    redGhostState.append(gameState.getAgentState(idx))
            return redGhostState

    def onOppositeSide(self, position, gameState):
        if self.isRed:
            return gameState.isOnBlueSide(position)
        else:
            return gameState.isOnRedSide(position)

    def evaluationFunction(self, currentGameState, action):

        successorGameState = currentGameState.generateSuccessor(self.index, action)
        newPosition = successorGameState.getAgentPosition(self.index)
        oldOppPacmanPositions = self.getOppPacman(currentGameState)
        evalFunc = self.defenseEvaluationFunction
        if len(oldOppPacmanPositions) < 2:
            evalFunc = self.offenseEvaluationFunction
        return evalFunc(currentGameState, action)

    def defenseEvaluationFunction(self, currentGameState, action):
        """
        Design a better evaluation function here.
        The evaluation function takes in the current `pacai.bin.pacman.PacmanGameState`
        and an action, and returns a number, where higher numbers are better.
        Make sure to understand the range of different values before you combine them
        in your evaluation function.
        """

        successorGameState = currentGameState.generateSuccessor(self.index, action)

        # Useful information you can extract.
        newPosition = successorGameState.getAgentPosition(self.index)
        oldFood = self.getOppFood(currentGameState)
        oldOppPacmanPositions = self.getOppPacman(currentGameState)
        # newScaredTimes = [ghostState.getScaredTimer() for ghostState in newGhostStates]

        if self.onOppositeSide(newPosition, successorGameState):
            return -1000

        if len(oldOppPacmanPositions) == 0:
            return -1 * distance.maze(self.midpoint, newPosition, successorGameState)

        return -1 * distance.maze(oldOppPacmanPositions[0], newPosition, successorGameState)

    def offenseEvaluationFunction(self, currentGameState, action):
        """
        Design a better evaluation function here.
        The evaluation function takes in the current `pacai.bin.pacman.PacmanGameState`
        and an action, and returns a number, where higher numbers are better.
        Make sure to understand the range of different values before you combine them
        in your evaluation function.
        """

        successorGameState = currentGameState.generateSuccessor(self.index, action)

        # Useful information you can extract.
        newPosition = successorGameState.getAgentPosition(self.index)
        oldFood = self.getOppFood(currentGameState)
        newGhostStates = self.getOppGhostState(successorGameState)
        newGhostPositions = self.getOppGhost(successorGameState)

        score = currentGameState.getScore() * 100  # weighted current score
        closestDistToFood = float('-inf')
        if self.onOppositeSide(newPosition, successorGameState):
            score += 100
        for food in oldFood.asList():
            dist = distance.maze(newPosition, food, currentGameState)
            if dist == 0:  # check if the new position is food
                score += 1000
            else:  # add reciprocol manhattan dist to food (b/c close food = more points) * weight
                score += (1 / dist) * 100
        # calculate ghost score
        eat_ghost = 1  # coefficient to switch values if ghost are edible
        for i in range(len(newGhostPositions)):
            if newGhostStates[i].getScaredTimer() > 0:  # if ghosts edible, change weight to inverse reciprocol
                eat_ghost = -0.1
            if distance.manhattan(newGhostPositions[i], newPosition) <= 1:  # if near ghost run away
                score -= 50 * eat_ghost
            else:  # subtract reciprocol ghost distance (b/c closer ghost = less points) * weight
                score -= (1 / distance.manhattan(newGhostPositions[i], newPosition)) * 50 * eat_ghost
        return score


def createTeam(firstIndex, secondIndex, isRed,
               first='pacai.student.myTeam.HybridAgent',
               second='pacai.student.defenseAgent.DefenseAgent'):
    """
    This function should return a list of two agents that will form the capture team,
    initialized using firstIndex and secondIndex as their agent indexed.
    isRed is True if the red team is being created,
    and will be False if the blue team is being created.
    """

    firstAgent = reflection.qualifiedImport(first)
    secondAgent = reflection.qualifiedImport(second)

    return [
        firstAgent(firstIndex),
        secondAgent(secondIndex),
    ]
