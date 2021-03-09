from pacai.util import reflection
import random
from pacai.agents.capture.capture import CaptureAgent
from pacai.core import distance
from pacai.core.directions import Directions

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

        self.mid_x_coord = layout_width // 2
        if self.red:
            self.mid_x_coord -= 1

        for i in range(1, layout_height):
            if not walls[self.mid_x_coord][i]:
                midpoint_list.append((self.mid_x_coord, i))

        self.midpoint = midpoint_list[len(midpoint_list) // 2]
        self.teammatePos = 0
        self.teammateIdx = 0
        self.posHistory =[]

    def chooseAction(self, gameState):
        self.posHistory.append(gameState.getAgentPosition(self.index))
        if(len(self.posHistory) > 2):
            self.posHistory.pop(0)
        # Collect legal moves.
        legalMoves = gameState.getLegalActions(self.index)
        if Directions.STOP in legalMoves:
            legalMoves.remove(Directions.STOP)

        self.teammateIdx = 0
        if self.isRed:
            for i in gameState.getRedTeamIndices():
                if i != self.index:
                    self.teammateIdx = i
        else:
            for i in gameState.getBlueTeamIndices():
                if i != self.index:
                    self.teammateIdx = i
        self.teammatePos = gameState.getAgentPosition(self.teammateIdx)

        evaluationFunction = self.getEvaluationFunction(gameState)
        # Choose one of the best actions.
        scores = [evaluationFunction(gameState, action) for action in legalMoves]
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
    
    def onMySide(self, position, gameState):
        if self.isRed:
            return gameState.isOnRedSide(position)
        else:
            return gameState.isOnBlueSide(position)
        
    def isOppClose(self, currentGameState):
        myPos = currentGameState.getAgentPosition(self.index)
        OppPositions = self.getOppGhost(currentGameState)
        if(len(self.getOppPacman(currentGameState)) <= 1):
            return True
        for i in OppPositions:
            if self.isRed:
                if self.mid_x_coord <= (i[0] - 20):
                    return True
            else:
                if self.mid_x_coord >= (i[0] + 20):
                    return True
        return False

    def getEvaluationFunction(self, currentGameState):
        myPos = currentGameState.getAgentPosition(self.index)
        evalFunc = self.offenseEvaluationFunction
        isScared = currentGameState.getAgentState(self.index).getScaredTimer() > 0
        if not self.onMySide(self.teammatePos, currentGameState) and self.isOppClose(currentGameState):
            evalFunc = self.defenseEvaluationFunction
        return evalFunc

    def defenseEvaluationFunction(self, currentGameState, action):

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

        successorGameState = currentGameState.generateSuccessor(self.index, action)

        # Useful information you can extract.
        newPosition = successorGameState.getAgentPosition(self.index)
        oldFood = self.getOppFood(currentGameState)
        newGhostStates = self.getOppGhostState(successorGameState)
        newGhostPositions = self.getOppGhost(successorGameState)
        oldOppPacmanPositions = self.getOppPacman(currentGameState)
        score = currentGameState.getScore() * 100  # weighted current score
        closestDistToFood = float('-inf')
        if newPosition in oldOppPacmanPositions:
            return 10000
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
            dist = distance.manhattan(newGhostPositions[i], newPosition)
            if newGhostStates[i].getScaredTimer() > 0:  # if ghosts edible, weight=inverse reciprocol
                eat_ghost = -0.1
            if dist <= 1:  # if near ghost run away
                score -= 50 * eat_ghost
            else:  # subtract reciprocol ghost distance (b/c closer ghost = less points) * weight
                score -= (1 / dist) * 50 * eat_ghost
        if(len(self.posHistory) > 2 and newPosition == self.posHistory[len(self.posHistory) - 2]):
            score -= 10000
        return score


def createTeam(firstIndex, secondIndex, isRed,
               first=HybridAgent,
               second=HybridAgent):
    firstAgent = first
    secondAgent = second

    return [
        firstAgent(firstIndex),
        secondAgent(secondIndex),
    ]
