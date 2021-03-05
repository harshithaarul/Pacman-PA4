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

    def chooseAction(self, state):
        """
        alpha-beta pruning algorithm
        (esentially minimax with additional alpha, beta conditions)
        """
        # passing in alpha = -inf and beta = inf
        value, move = self.maxValue(state, 4, float('-inf'), float('inf'))
        # print("move: ", move + " value: ", value)
        return move

    def maxValue(self, state, depth, alpha, beta):
        """
        Pacman's value and move calculator
        this time with alpha and beta values
        """
        #if state.isOver():  # return terminal value
        #    return self.betterEvaluationFunction(state), Directions.STOP
        value = float('-inf')  # variable for utility value
        move = None
        for action in state.getLegalActions(self.index):
            if action == Directions.STOP:  # don't consider STOP
                continue
            if depth == 1:
                return self.offenseEvaluationFunction(state, action), action
            v2 = self.minValue(state.generateSuccessor(self.index, action), depth, self.getOpponents(state)[0] , alpha,
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
        #if state.isOver():  # return terminal value
        #    return self.betterEvaluationFunction(state), Directions.STOP
        value = float('inf')
        move = None
        for action in state.getLegalActions(index):
            if action == Directions.STOP:  # don't consider STOP
                continue
            if index == self.getOpponents(state)[1]:  # on last ghost, go back to pacman
                v2, a2 = self.maxValue(self.getCurrentObservation().generateSuccessor(index, action), depth - 1, alpha,
                    beta)
            else:  # multiple min layers for ghosts
                v2 = self.minValue(self.getCurrentObservation().generateSuccessor(index, action), depth, self.getOpponents(state)[1],
                    alpha, beta)
            if v2 < value:  # choose min value
                value = v2
                # move = action
                beta = min(beta, value)  # track beta value
            if value <= alpha:  # skip remaining (prune) if value < alpha
                return value
        return value

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
            dist = distance.manhattan(newPosition, food)
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
