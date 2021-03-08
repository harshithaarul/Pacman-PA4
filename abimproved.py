from pacai.util import reflection
import random
from pacai.agents.capture.capture import CaptureAgent
from pacai.core import distance
from pacai.core.directions import Directions

class AlphaBetaAgent(CaptureAgent):
    """
    A Dummy agent to serve as an example of the necessary agent structure.
    You should look at `pacai.core.baselineTeam` for more details about how to create an agent.
    """

    def __init__(self, index, **kwargs):
        super().__init__(index)

    def registerInitialState(self, gameState):
        super().registerInitialState(gameState)
        self.isRed = gameState.isOnRedTeam(self.index)
        self.startingPosition = self.getPosition(gameState)

    def chooseAction(self, state):
        """
        alpha-beta pruning algorithm
        (esentially minimax with additional alpha, beta conditions)
        """
        ghostDists = [distance.manhattan(self.getPosition(state), ghost)
             for ghost in self.getOppGhost(state)]

        if len(ghostDists) > 0 and min(ghostDists) > 5:
            legalMoves = state.getLegalActions(self.index)
            if Directions.STOP in legalMoves:
                legalMoves.remove(Directions.STOP)

            # Choose one of the best actions.
            scores = [self.offenseEvaluationFunction(state, action) for action in legalMoves]
            bestScore = max(scores)
            bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
            chosenIndex = random.choice(bestIndices)  # Pick randomly among the best.

            return legalMoves[chosenIndex]

        # print("alpha beta")

        # maxDepth = 2
        # numAgents = 4
        # evalFunc = self.ABEvaluationFunction
        #
        # def alphabeta(state, depth, agentIndex, alpha, beta):
        #     legalMoves = state.getLegalActions(agentIndex)
        #     if Directions.STOP in legalMoves:
        #         legalMoves.remove(Directions.STOP)
        #     if depth == maxDepth or len(legalMoves) == 0:
        #         return evalFunc(state), Directions.STOP
        #     print(legalMoves)
        #     v2, move = (None, None)
        #     nextStates = [state.generateSuccessor(agentIndex, move) for move in legalMoves]
        #     if agentIndex == 0:
        #         v = -99999
        #         for nextState, nextAction in zip(nextStates, legalMoves):
        #             v2, _ = alphabeta(nextState, depth, 1, alpha, beta)
        #             if v2 > v:
        #                 v, move = v2, nextAction
        #                 alpha = max(alpha, v)
        #             if v >= beta:
        #                 return v, move
        #         return v, move
        #     elif agentIndex == numAgents - 1:
        #         v = 99999
        #         for nextState in nextStates:
        #             v2, action = alphabeta(nextState, depth + 1, 0, alpha, beta)
        #             if v2 < v:
        #                 v, move = v2, action
        #                 beta = min(beta, v)
        #             if v <= alpha:
        #                 return v, move
        #         return v, move
        #     else:
        #         v = 99999
        #         for nextState in nextStates:
        #             v2, action = alphabeta(nextState, depth, agentIndex + 1, alpha, beta)
        #             if v2 < v:
        #                 v, move = v2, action
        #                 beta = min(beta, v)
        #             if v <= alpha:
        #                 return v, move
        #         return v, move
        #
        # alphabetaVal = alphabeta(state, 0, 0, -99999, 99999)
        # # print(alphabetaVal)
        # print(alphabetaVal)
        # return alphabetaVal[1]
        # passing in alpha = -inf and beta = inf
        value, move = self.maxValue(state, 2, float('-inf'), float('inf'))
        # print("move: ", move + " value: ", value)
        return move

    def maxValue(self, state, depth, alpha, beta):
        """
        Pacman's value and move calculator
        this time with alpha and beta values
        """
        # if state.isOver():  # return terminal value
        #    return self.betterEvaluationFunction(state), Directions.STOP
        value = float('-inf')  # variable for utility value
        move = None
        for action in state.getLegalActions(self.index):
            if action == Directions.STOP:  # don't consider STOP
                continue
            if depth == 1:
                return self.ABEvaluationFunction(state), action
            v2 = self.minValue(state.generateSuccessor(self.index, action), depth, self.getOpponents(state)[0], alpha,
                               beta)
            if v2 > value:  # choose max value
                value = v2
                move = action
                alpha = max(alpha, value)  # track alpha value
            if value >= beta:  # skip remaining (prune) if value > beta
                return value, move
        return value, move

    def minValue(self, state, depth, index, alpha, beta):
        """
        Ghosts' value and move calculator
        index keeps track of which ghost agent is deciding
        """
        # if state.isOver():  # return terminal value
        #    return self.betterEvaluationFunction(state), Directions.STOP
        value = float('inf')
        move = None

        if self.getPosition(state) == self.startingPosition:
            return float('inf')

        for action in state.getLegalActions(index):
            if action == Directions.STOP:  # don't consider STOP
                continue
            if index == self.getOpponents(state)[1]:  # on last ghost, go back to pacman
                v2, a2 = self.maxValue(state.generateSuccessor(index, action), depth - 1, alpha,
                                       beta)
            else:  # multiple min layers for ghosts
                v2 = self.minValue(state.generateSuccessor(index, action), depth,
                                   self.getOpponents(state)[1],
                                   alpha, beta)
            if v2 < value:  # choose min value
                value = v2
                # move = action
                beta = min(beta, value)  # track beta value
            if value <= alpha:  # skip remaining (prune) if value < alpha
                return value
        return value

    def getPosition(self, gameState):
        return gameState.getAgentPosition(self.index)

    def getNumWalls(self,position, gameState):
        walls = gameState.getWalls()
        xmax = walls.getWidth()
        ymax = walls.getHeight()
        pos1 = (position[0] + 1, position[1])
        pos2 = (position[0], position[1] + 1)
        pos3 = (position[0] - 1, position[1])
        pos4 = (position[0], position[1] - 1)
        posList = [pos1, pos2, pos3, pos4]
        wallCount = 0
        for pos in posList:
            x,y = pos
            try:
                if walls[x][y]:
                    wallCount += 1
            except:
                continue
        return wallCount

    def oppIsScared(self, gameState):
        oppGhostStates = self.getOppGhostState(gameState)
        oppIsScared = False
        for oppGhost in oppGhostStates:
            oppIsScared = oppIsScared or (oppGhost.getScaredTimer() > 0)
        return oppIsScared

    def ABEvaluationFunction(self, currentGameState):

        food = self.getOppFood(currentGameState).asList()

        minManhattanFood = None
        minFoodDist = 999999

        for f in food:
            curDist = distance.manhattan(f, self.getPosition(currentGameState))
            if curDist < minFoodDist:
                minFoodDist = curDist
                minManhattanFood = f

        currentPos = self.getPosition(currentGameState)
        numWalls = self.getNumWalls(currentPos, currentGameState)
        # print("Num Walls =", numWalls)
        ateCapsule = self.oppIsScared(currentGameState)
        ghostDistMultiplier = 1
        if ateCapsule:
            # print ("ate capsule")
            ghostDistMultiplier = -2

        closestDistToGhost = 0

        try:
            closestDistToGhost = min([distance.manhattan(self.getPosition(currentGameState), ghost)
                 for ghost in self.getOppGhost(currentGameState)])
        except:
            pass

        if closestDistToGhost > 10:
            return -10000

        features = {
            "closestDistToFood": distance.maze(minManhattanFood, self.getPosition(currentGameState), currentGameState),
            "closestDistToGhost": min([distance.manhattan(self.getPosition(currentGameState), ghost)
                                      for ghost in self.getOppGhost(currentGameState)]),
            # "closestDistToGhost": closestDistToGhost,
            "surroundingWalls": numWalls

        }

        weights = {
            "closestDistToFood": -50,
            "closestDistToGhost": 100 * ghostDistMultiplier,
            "surroundingWalls": -100
        }

        return sum([features[feat] * weights[feat] for feat in features.keys()])

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
        # self.getNumWalls(newPosition, currentGameState)
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
        return score

    def OppEvaluationFunction(self, currentGameState, action):

        successorGameState = currentGameState.generateSuccessor(self.index, action)

        # Useful information you can extract.
        newPosition = successorGameState.getAgentPosition(self.index)
        oldFood = self.getMyFood(currentGameState)
        oldMyPacmanPositions = self.getMyPacman(currentGameState)
        # newScaredTimes = [ghostState.getScaredTimer() for ghostState in newGhostStates]

        if not self.onOppositeSide(newPosition, successorGameState):
            return -1000

        if len(oldOppPacmanPositions) == 0:
            return -1 * distance.maze(self.midpoint, newPosition, successorGameState)

        return -1 * distance.maze(oldMyPacmanPositions[0], newPosition, successorGameState)

    def getMyFood(self, gameState):
        if self.isRed:
            return gameState.getRedFood()
        else:
            return gameState.getBlueFood()

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

    def getMyPacman(self, gameState):
        if self.isRed:
            redIndices = gameState.getRedTeamIndices()
            oppPos = [gameState.getAgentPosition(idx) for idx in redIndices]
            redGhostPos = [pos for pos in oppPos if gameState.isOnBlueSide(pos)]
            return redGhostPos
        else:
            blueIndices = gameState.getBlueTeamIndices()
            oppPos = [gameState.getAgentPosition(idx) for idx in blueIndices]
            blueGhostPos = [pos for pos in oppPos if gameState.isOnRedSide(pos)]
            return blueGhostPos

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



# class OffenseAgent(CaptureAgent):
#
#     def __init__(self, index, **kwargs):
#         super().__init__(index)
#
#     def registerInitialState(self, gameState):
#         super().registerInitialState(gameState)
#         self.isRed = gameState.isOnRedTeam(self.index)
#         # Your initialization code goes here, if you need any.
#
#     def chooseAction(self, gameState):
#         # Collect legal moves.
#         legalMoves = gameState.getLegalActions(self.index)
#         if Directions.STOP in legalMoves:
#             legalMoves.remove(Directions.STOP)
#
#         # Choose one of the best actions.
#         scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
#         bestScore = max(scores)
#         bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
#         chosenIndex = random.choice(bestIndices)  # Pick randomly among the best.
#         return legalMoves[chosenIndex]
#
#     def getOppFood(self, gameState):
#         if self.isRed:
#             return gameState.getBlueFood()
#         else:
#             return gameState.getRedFood()
#
#     def getOppGhost(self, gameState):
#         """
#         Returns list of opponent ghost POSITIONS
#         """
#         if self.isRed:
#             blueIndices = gameState.getBlueTeamIndices()
#             oppPos = [gameState.getAgentPosition(idx) for idx in blueIndices]
#             blueGhostPos = [pos for pos in oppPos if gameState.isOnBlueSide(pos)]
#             return blueGhostPos
#         else:
#             redIndices = gameState.getRedTeamIndices()
#             oppPos = [gameState.getAgentPosition(idx) for idx in redIndices]
#             redGhostPos = [pos for pos in oppPos if gameState.isOnRedSide(pos)]
#             return redGhostPos
#
#     def getOppGhostState(self, gameState):
#         """
#         Returns list of opponent ghost states
#         """
#         if self.isRed:
#             blueGhostState = []
#             blueIndices = gameState.getBlueTeamIndices()
#             for idx in blueIndices:
#                 if gameState.isOnBlueSide(gameState.getAgentPosition(idx)):
#                     blueGhostState.append(gameState.getAgentState(idx))
#             return blueGhostState
#         else:
#             redGhostState = []
#             redIndices = gameState.getRedTeamIndices()
#             for idx in redIndices:
#                 if gameState.isOnRedSide(gameState.getAgentPosition(idx)):
#                     redGhostState.append(gameState.getAgentState(idx))
#             return redGhostState
#
#     def onOppositeSide(self, position, gameState):
#         if self.isRed:
#             return gameState.isOnBlueSide(position)
#         else:
#             return gameState.isOnRedSide(position)
#
#     def evaluationFunction(self, currentGameState, action):
#         """
#         Design a better evaluation function here.
#         The evaluation function takes in the current `pacai.bin.pacman.PacmanGameState`
#         and an action, and returns a number, where higher numbers are better.
#         Make sure to understand the range of different values before you combine them
#         in your evaluation function.
#         """
#
#         successorGameState = currentGameState.generateSuccessor(self.index, action)
#
#         # Useful information you can extract.
#         newPosition = successorGameState.getAgentPosition(self.index)
#         oldFood = self.getOppFood(currentGameState)
#         newGhostStates = self.getOppGhostState(successorGameState)
#         newGhostPositions = self.getOppGhost(successorGameState)
#
#         score = currentGameState.getScore() * 100  # weighted current score
#         closestDistToFood = float('-inf')
#         if self.onOppositeSide(newPosition, successorGameState):
#             score += 100
#         for food in oldFood.asList():
#             dist = distance.maze(newPosition, food, currentGameState)
#             if dist == 0:  # check if the new position is food
#                 score += 1000
#             else:  # add reciprocol manhattan dist to food (b/c close food = more points) * weight
#                 score += (1 / dist) * 100
#         # calculate ghost score
#         eat_ghost = 1  # coefficient to switch values if ghost are edible
#         for i in range(len(newGhostPositions)):
#             dist = distance.manhattan(newGhostPositions[i], newPosition)
#             if newGhostStates[i].getScaredTimer() > 0:  # if ghosts edible, weight=inverse reciprocol
#                 eat_ghost = -0.1
#             if dist <= 1:  # if near ghost run away
#                 score -= 50 * eat_ghost
#             else:  # subtract reciprocol ghost distance (b/c closer ghost = less points) * weight
#                 score -= (1 / dist) * 50 * eat_ghost
#         return score
#
#
# class DefenseAgent(CaptureAgent):
#
#     def __init__(self, index, **kwargs):
#         super().__init__(index)
#
#     def registerInitialState(self, gameState):
#
#         super().registerInitialState(gameState)
#         self.isRed = gameState.isOnRedTeam(self.index)
#         # Your initialization code goes here, if you need any.
#         midpoint_list = []
#         layout = gameState.getInitialLayout()
#         layout_height = layout.getHeight()
#         layout_width = layout.getWidth()
#         walls = gameState.getWalls()
#
#         mid_x_coord = layout_width // 2
#         if self.red:
#             mid_x_coord -= 1
#
#         for i in range(1, layout_height):
#             if not walls[mid_x_coord][i]:
#                 midpoint_list.append((mid_x_coord, i))
#
#         self.midpoint = midpoint_list[len(midpoint_list) // 2]
#
#     def chooseAction(self, gameState):
#         # Collect legal moves.
#         legalMoves = gameState.getLegalActions(self.index)
#         if Directions.STOP in legalMoves:
#             legalMoves.remove(Directions.STOP)
#
#         # Choose one of the best actions.
#         scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
#         bestScore = max(scores)
#         bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
#         chosenIndex = random.choice(bestIndices)  # Pick randomly among the best.
#
#         return legalMoves[chosenIndex]
#
#     def getOppFood(self, gameState):
#         if self.isRed:
#             return gameState.getBlueFood()
#         else:
#             return gameState.getRedFood()
#
#     def getOppGhost(self, gameState):
#         if self.isRed:
#             blueIndices = gameState.getBlueTeamIndices()
#             oppPos = [gameState.getAgentPosition(idx) for idx in blueIndices]
#             blueGhostPos = [pos for pos in oppPos if gameState.isOnBlueSide(pos)]
#             return blueGhostPos
#         else:
#             redIndices = gameState.getRedTeamIndices()
#             oppPos = [gameState.getAgentPosition(idx) for idx in redIndices]
#             redGhostPos = [pos for pos in oppPos if gameState.isOnRedSide(pos)]
#             return redGhostPos
#
#     def getOppPacman(self, gameState):
#         if self.isRed:
#             blueIndices = gameState.getBlueTeamIndices()
#             oppPos = [gameState.getAgentPosition(idx) for idx in blueIndices]
#             blueGhostPos = [pos for pos in oppPos if gameState.isOnRedSide(pos)]
#             return blueGhostPos
#         else:
#             redIndices = gameState.getRedTeamIndices()
#             oppPos = [gameState.getAgentPosition(idx) for idx in redIndices]
#             redGhostPos = [pos for pos in oppPos if gameState.isOnBlueSide(pos)]
#             return redGhostPos
#
#     def onOppositeSide(self, position, gameState):
#         if self.isRed:
#             return gameState.isOnBlueSide(position)
#         else:
#             return gameState.isOnRedSide(position)
#
#     def evaluationFunction(self, currentGameState, action):
#
#         successorGameState = currentGameState.generateSuccessor(self.index, action)
#
#         # Useful information you can extract.
#         newPosition = successorGameState.getAgentPosition(self.index)
#         oldFood = self.getOppFood(currentGameState)
#         oldOppPacmanPositions = self.getOppPacman(currentGameState)
#         # newScaredTimes = [ghostState.getScaredTimer() for ghostState in newGhostStates]
#
#         if self.onOppositeSide(newPosition, successorGameState):
#             return -1000
#
#         if len(oldOppPacmanPositions) == 0:
#             return -1 * distance.maze(self.midpoint, newPosition, successorGameState)
#
#         return -1 * distance.maze(oldOppPacmanPositions[0], newPosition, successorGameState)


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
        isScared = currentGameState.getAgentState(self.index).getScaredTimer() > 0
        # if len(oldOppPacmanPositions) < 2:f
        if isScared:
            evalFunc = self.offenseEvaluationFunction
        return evalFunc(currentGameState, action)

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
        return score


def createTeam(firstIndex, secondIndex, isRed,
               first=HybridAgent,
               second=AlphaBetaAgent):
    firstAgent = first
    secondAgent = second

    return [
        firstAgent(firstIndex),
        secondAgent(secondIndex),
    ]
