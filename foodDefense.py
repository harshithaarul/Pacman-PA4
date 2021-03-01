# class DefenseAgent(CaptureAgent): has food logic
#     """
#     A Dummy agent to serve as an example of the necessary agent structure.
#     You should look at `pacai.core.baselineTeam` for more details about how to create an agent.
#     """
#
#     def __init__(self, index, **kwargs):
#         super().__init__(index)
#
#     def registerInitialState(self, gameState):
#         """
#         This method handles the initial setup of the agent and populates useful fields,
#         such as the team the agent is on and the `pacai.core.distanceCalculator.Distancer`.
#
#         IMPORTANT: If this method runs for more than 15 seconds, your agent will time out.
#         """
#
#         super().registerInitialState(gameState)
#         self.isRed = gameState.isOnRedTeam(self.index)
#         self.goingForFood = False
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
#             return gameState.getBlueFood().asList()
#         else:
#             return gameState.getRedFood().asList()
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
#
#         dist2mid = distance.maze(currentGameState.getAgentPosition(self.index), self.midpoint, currentGameState)
#
#         if len(oldOppPacmanPositions) == 0:
#             foodList = self.getOppFood(currentGameState)
#             minDist = 10000
#             currPos = currentGameState.getAgentPosition(self.index)
#             if dist2mid <= 1 or self.goingForFood:
#                 self.goingForFood = True
#                 for food in foodList:
#                     dist2food = distance.maze(currPos, food, currentGameState)
#                     if dist2food < minDist:
#                         minDist = dist2food
#                 if minDist == 0:
#                     self.goingForFood = False
#                 return 1 / (minDist + 1)
#             if self.onOppositeSide(newPosition, successorGameState):
#                 return -1000
#             return -1 * distance.maze(self.midpoint, newPosition, successorGameState)
#         self.goingForFood = False
#         return -1 * distance.maze(oldOppPacmanPositions[0], newPosition, successorGameState)