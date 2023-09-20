# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import copy
import string
import multiprocessing

class Box:


    def __init__(self,num,type):
        self.number=num
        self.edges={}
        self.wonByMe = 0
        self.type=type


class Board:


    #this will only be done once to create the inital board
    #all other board configuations will be made by copying the last board then making the change
    def __init__(self,size):


        self.maxBoxes=0
        self.minBoxes=0
        self.possableBoxesToTake = 0
        self.size=size
        self.reverseMoves=[]

        self.dummyBoxesTop={}
        self.dummyBoxesRight={}
        self.dummyBoxesLeft={}
        self.dummyBoxesBot={}
        self.boxes={}

        for i in range(size):
            self.dummyBoxesTop[i] = Box(i,"Top")
            self.dummyBoxesRight[i] = Box(i,"Right")
            self.dummyBoxesLeft[i] = Box(i,"Left")
            self.dummyBoxesBot[i] = Box(i,"Bot")
        for i in range(size*size):
            self.boxes[i] = Box(i,"Normal")
        # connect all the boxes
        for i in range(size*size):

            # connection numbering for a box
            #       1
            #    0  b  2
            #       3
            #connect left
            #if on left edge connect to dummy left
            if i % size == 0:

                self.dummyBoxesLeft[i/size].edges[2] = self.boxes[i]
                self.boxes[i].edges[0] = self.dummyBoxesLeft[i/size]
            else:
                self.boxes[i].edges[0] = self.boxes[i-1]

            #connect Right
            # if on Right edge connect to dummy Right
            if (i+1) % size == 0:

                self.dummyBoxesRight[((i+1) / size) - 1].edges[0] = self.boxes[i]
                self.boxes[i].edges[2] = self.dummyBoxesRight[((i+1) / size) - 1]
            else:
                self.boxes[i].edges[2] = self.boxes[i + 1]

            # connect Top
            # if on Top edge connect to dummy Top
            if i < size:
                self.dummyBoxesTop[i].edges[3] = self.boxes[i]
                self.boxes[i].edges[1] = self.dummyBoxesTop[i]
            else:
                self.boxes[i].edges[1] = self.boxes[i-size]
            # connect Bot
            # if on bot edge connect to dummy bot
            if i >= size*size-size:
                self.dummyBoxesTop[i-size*(size-1)].edges[1] = self.boxes[i]
                self.boxes[i].edges[3] = self.dummyBoxesTop[i-size*(size-1)]
            else:
                self.boxes[i].edges[3] = self.boxes[i+size]



    def multipleMoves(self,listOfMoves):
        for move in listOfMoves:
            self.changeEdge(self.boxes[move[0]],move[1],move[2])
            self.reverseMoves.append(move)


    def reset(self):
        for x in range(len(self.reverseMoves)):
            move=self.reverseMoves.pop()
            self.addEdge(self.boxes[move[0]],move[1],move[2])

    #does the change specified
    # nodeToChange stores the node whose edge will be changed
    # edge stores the edge to cut
    # 0 for left
    # 1 for top
    # 2 for right
    # 3 for bottom

    # returns 1 if box was taken 0 if it was not
    def changeEdge(self,nodeToChange,edge,minOrMax):

        node2 = nodeToChange.edges[edge]

        #delting left edge
        if edge == 0:
            del nodeToChange.edges[edge]
            del node2.edges[2]
        #Top
        elif edge == 1:
            del nodeToChange.edges[edge]
            del node2.edges[3]
        #Right
        elif edge == 2:
            del nodeToChange.edges[edge]
            del node2.edges[0]
        #Bot
        elif edge == 3:
            del nodeToChange.edges[edge]
            del node2.edges[1]

        boxTaken=self.updateBoxes(nodeToChange,minOrMax)
        boxTaken2=self.updateBoxes(node2,minOrMax)

       # print("doing move")
        #print((nodeToChange.number,edge,minOrMax))
        #self.printBoard()
        #print(str(self.uValue))

        if boxTaken == 1 or boxTaken2 ==1:
            return 1
        return 0

    def addEdge(self,nodeToChange,edge,minOrMax):

        #if move would re-connect a box
        if len(nodeToChange.edges)==0 :
            #box is takeable again
            self.possableBoxesToTake+=1
            if minOrMax=="max":
                self.maxBoxes-=1
            else:
                self.minBoxes-=1
        #if box would become untakeable in one move
        if len(nodeToChange.edges) == 1:
            self.possableBoxesToTake -= 1

        # adding left edge
        if edge == 0:
            #add edge to dummy node left
            if nodeToChange.number % self.size ==0:
                nodeToChange.edges[0]=self.dummyBoxesLeft[nodeToChange.number/self.size]
                self.dummyBoxesLeft[nodeToChange.number / self.size].edges[2]=nodeToChange
            else:
                #if other box would also be re-connected update uvalue
                self.reverseUvalue(self.boxes[nodeToChange.number-1],minOrMax)

                nodeToChange.edges[0] = self.boxes[nodeToChange.number-1]
                self.boxes[nodeToChange.number - 1].edges[2] = nodeToChange

        # Top
        elif edge == 1:
            # add edge to dummy node top
            if nodeToChange.number < self.size :
                nodeToChange.edges[1] = self.dummyBoxesTop[nodeToChange.number]
                self.dummyBoxesTop[nodeToChange.number].edges[3] = nodeToChange
            else:
                self.reverseUvalue(self.boxes[nodeToChange.number - self.size], minOrMax)
                nodeToChange.edges[1] = self.boxes[nodeToChange.number - self.size]
                self.boxes[nodeToChange.number - self.size].edges[3] = nodeToChange

        # Right
        elif edge == 2:
            # add edge to dummy node Right
            if (nodeToChange.number+1) % self.size == 0:
                nodeToChange.edges[2] = self.dummyBoxesRight[(nodeToChange.number-(self.size-1)) / self.size]
                self.dummyBoxesRight[(nodeToChange.number-(self.size-1)) / self.size].edges[0] = nodeToChange
            else:
                self.reverseUvalue(self.boxes[nodeToChange.number + 1], minOrMax)
                nodeToChange.edges[2] = self.boxes[nodeToChange.number + 1]
                self.boxes[nodeToChange.number + 1].edges[0] = nodeToChange

        # Bot
        elif edge == 3:
            # add edge to dummy node bot
            if nodeToChange.number >=(self.size-1)*self.size:
                nodeToChange.edges[3] = self.dummyBoxesBot[nodeToChange.number-(self.size-1)*self.size]
                self.dummyBoxesBot[nodeToChange.number-(self.size-1)*self.size].edges[1] = nodeToChange
            else:
                self.reverseUvalue(self.boxes[nodeToChange.number +self.size], minOrMax)
                nodeToChange.edges[3] = self.boxes[nodeToChange.number +self.size]
                self.boxes[nodeToChange.number +self.size].edges[1] = nodeToChange

        #print("undoing move")
        #print((nodeToChange.number, edge, minOrMax))
        #self.printBoard()
        #print(str(self.uValue))


    def changeEdgeDontUpdate(self, nodeToChange, edge):

        node2 = nodeToChange.edges[edge]

        # delting left edge
        if edge == 0:
            del nodeToChange.edges[edge]
            del node2.edges[2]
        # Top
        elif edge == 1:
            del nodeToChange.edges[edge]
            del node2.edges[3]
        # Right
        elif edge == 2:
            del nodeToChange.edges[edge]
            del node2.edges[0]
        # Bot
        elif edge == 3:
            del nodeToChange.edges[edge]
            del node2.edges[1]


    #returns 1 if box was taken 0 if it was not
    def updateBoxes(self,boxChanged,minOrMax):
        if len(boxChanged.edges) == 1 and boxChanged.type=="Normal":
            self.possableBoxesToTake+=1
        if len(boxChanged.edges) == 0 and boxChanged.type=="Normal":
            if minOrMax == "max":
                self.possableBoxesToTake -= 1
                self.maxBoxes+=1

            else:
                self.possableBoxesToTake -= 1
                self.minBoxes += 1

            return 1

        return 0
    def reverseUvalue(self,boxChanged,minOrMax):
        if len(boxChanged.edges) == 1 :
            self.possableBoxesToTake-=1
        if len(boxChanged.edges) == 0:
            if minOrMax == "max":
                self.possableBoxesToTake += 1
                self.maxBoxes -= 1
            else:
                self.possableBoxesToTake += 1
                self.minBoxes -= 1



        #self.Board = copy.deepcopy(boardToCopy)

    #DOES NOT DO a rigrous check of connections
    def printBoard(self):
        print("----------------------------------------------------")
        print("!    0    1    2    3    4    5    6    7    8     !")

        row = 0

        while row < self.size:
            # top
            print("!    ", end="")
            for i in range(self.size):
                try:
                    if self.boxes[i+row*self.size].edges.get(1) != None:
                        print("|", end="    ")
                    else:
                        print(" ", end="    ")
                except:
                    print(" ", end="    ")
            print(" !")

            # horzontal
            print("! ", end="")
            try:
                if self.dummyBoxesLeft[row].edges.get(2) != None:
                    print(row, end="--")
                else:
                    print(row, end="  ")
            except:
                print(row, end="  ")

            for i in range(self.size-1):
                try:
                    if self.boxes[i+row*self.size].edges.get(2) != None:
                        #formating
                        if row==0:
                            print(str(i + row * self.size), end="----")
                        elif row==1:
                            if i + row * self.size == self.size:
                                print(str(i + row * self.size), end="----")
                            else:
                                print(str(i+row*self.size), end="---")

                        else:
                            print(str(i+row*self.size), end="---")

                    else:
                        print(str(i+row*self.size), end="   ")
                except:
                    print(str(i + row * self.size), end="   ")

            try:
                if self.boxes[self.size-1+row*self.size].edges.get(2)!= None:
                    print(str(self.size-1+row*self.size), end="--")
                else:
                    print(str(self.size-1+row*self.size), end="  ")
            except:
                print(str(self.size-1 + row * self.size), end="  ")
            print(row,end="")

            if row == 0:
                print("  !")
            else:
                print(" !")


            row += 1

        #Bot
        print("!    ", end="")
        for i in range(self.size*(self.size-1),self.size*self.size):
            try:
                if self.boxes[i].edges.get(3) != None:
                    print("|", end="    ")
                else:
                    print(" ", end="    ")
            except:
                print(" ", end="    ")
        print(" !")
        print("!    0    1    2    3    4    5    6    7    8     !")


        print("----------------------------------------------------")

    def printBox(self):
        for box in self.boxes:
            try:
                print("   "+str(self.boxes[box].edges[1].number))
                print("   |")
            except:
                print()
                print("    ")
            # horzontal
            try:
                print(str(self.boxes[box].edges[0].number)+"--",end="")
            except:
                print("   ",end="")


            print(str(self.boxes[box].number),end="")

            try:
                print("--"+str(self.boxes[box].edges[2].number) , end="")
            except:
                print("   ", end="")
            print()

            try:
                num = str(self.boxes[box].edges[3].number)
                print("   |")
                print("   " + num)

            except:
                print()
            print("------------------------------")





class Node:
    childrenGenerated=0

    #def __init__(self,move,type):

    #    self.minOrMax=type
    #    self.children = {}
    #    self.moves=move
    #    self.uValue=0

    def __init__(self,move,type,uVal,hVal):

        self.minOrMax=type
        self.children = {}
        self.moves=move
        self.uValue=uVal
        self.hValue=hVal





    def generateChildren(self):
        #make sure children have not been generated already
        if len(self.children)==0:
            # to number children
            i = 0
            # use a copy of the board to stop dupicate moves
            rootBoardCopy = copy.deepcopy(self.board)

            for box in rootBoardCopy.boxes:
                # for each edge generate a new board with that edge removed
                # and create a new node to add too roots children
                while len(rootBoardCopy.boxes[box].edges) != 0:
                    # remove the edge from the copy board to stop dupicate edges
                    edge = list(rootBoardCopy.boxes[box].edges.keys())[0]
                    newBoard = copy.deepcopy(self.board)
                    #debug
                    self.childrenGenerated+=1
                    if self.childrenGenerated%100==0:
                        print("childrenGenerated:"+str(self.childrenGenerated))
                    if self.minOrMax == "min":
                        boxTaken = newBoard.changeEdge(newBoard.boxes[box], edge, "min") # mins move
                        if boxTaken == 1:
                            self.children[i] = Node(newBoard, "min")#min gets to go again
                        else:
                            self.children[i] = Node(newBoard, "max")  # max turn now
                        # do move to create new permentation

                    else:
                        boxTaken = newBoard.changeEdge(newBoard.boxes[box], edge, "max")  # maxs move
                        if boxTaken == 1:
                            self.children[i] = Node(newBoard, "max")#max gets to go again
                        else:
                            self.children[i] = Node(newBoard, "min")  # min turn now

                        # do move to create new permentation






                    # remove the edge from the copy board to stop dupicate edges
                    rootBoardCopy.changeEdgeDontUpdate(rootBoardCopy.boxes[box], edge)



                    i += 1

    def generateChildren2(self,board,minionBoard,size):

        #if a terminal node dont generate children
        if self.uValue!=0:
            return
        # make sure children have not been generated already
        if len(self.children) == 0:
            # create this nodes board
            board.multipleMoves(self.moves)
            #use copy of board to stop duipicate edges
            #print("SHOULD BE FULL")
            #minionBoard.printBoard()
            #print(minionBoard.reverseMoves)
            minionBoard.multipleMoves(self.moves)

            # to number children
            i = 0

            stop=0

            for box in minionBoard.boxes:
                # for each edge generate a new board with that edge removed
                # and create a new node to add too roots children
                if stop ==1:
                    break
                while len(minionBoard.boxes[box].edges) != 0:
                    edge =list(minionBoard.boxes[box].edges.keys())[0]
                    # make new move list incling new move

                    newMoveList = self.moves.copy()
                    newMoveList.append((box,edge,self.minOrMax))

                    # debug
                    self.childrenGenerated += 1
                    if self.childrenGenerated % 100 == 0:
                        print("childrenGenerated:" + str(self.childrenGenerated))

                    #create new node  and update U based on new move
                    boxTaken = board.changeEdge(board.boxes[box],edge,self.minOrMax)

                    #call multiple move to make sure it goes on the redo list
                    minionBoard.multipleMoves([(box,edge,self.minOrMax)])




                    if boxTaken == 1:
                        #if terminal board
                        if board.maxBoxes == int((size * size) / 2 + 1) and self.minOrMax == "max":
                            # this is a terminal node and one what will win the game for us so keep it as the only child
                            self.children = {}
                            self.children[0] = self.children[i] = Node(newMoveList, self.minOrMax,
                                                                       int((size * size) / 2 + 1),int((size * size) / 2 + 1))  # max turn again
                            stop=1
                            break #have a winning board so dont need more children
                        elif board.minBoxes == int((size * size) / 2 + 1) and self.minOrMax == "min":
                            self.children = {}
                            self.children[0] = self.children[i] = Node(newMoveList, self.minOrMax,
                                                                    -int((size * size) / 2 + 1),-int((size * size) / 2 + 1))  # min turn again
                            stop=1
                            break #have a winning board so dont need more children
                        #not terminal board
                        else:
                            if self.minOrMax=="max":
                                self.children[i] = Node(newMoveList, "max ",0,board.maxBoxes+board.possableBoxesToTake) # get to go again
                            else:
                                self.children[i] = Node(newMoveList, "min", 0,
                                                        -(board.minBoxes + board.possableBoxesToTake))  # get to go again

                    else:
                        if self.minOrMax == "max":
                            self.children[i] = Node(newMoveList, "min",0,-(board.minBoxes + board.possableBoxesToTake)) # min turn\


                        else:
                            self.children[i] = Node(newMoveList, "max",0,board.maxBoxes+board.possableBoxesToTake) # max turn



                    #undo new move for new claulation on next child
                    board.addEdge(board.boxes[box],edge,self.minOrMax)

                    i += 1

            #reset the board for later use
            board.reset()# may not need this
            minionBoard.reset()


class Solver:
    def __init__(self, move,size):
        self.root = Node(move,"max",0,0)
        self.size=size
        self.masterBoard = Board(size)
        self.minionBoard = Board(size)

        #if going 2nd just put the move in the constructer


    def initlise(self):
        #generate boards to pass to threads
        #IDEA: each thread gets a copy of main and the frist possable moves
        #it then gets a range of first moves to check with A B pruning

        #generate all first moves possable
        self.root.generateChildren()

        #number of cores
        numOfCores = multiprocessing.cpu_count()
        #calulate ranges
        rangeEachThreadFloat = (len(self.root.children)-1)/numOfCores
        #truncate to int
        rangeEachThread = int(rangeEachThreadFloat)



        # if less moves than threads
        if rangeEachThread ==0 :
            rangeEachThread=1

        startingNode =0
        needLastThread = True

        while (startingNode + rangeEachThread < len(self.root.children)):
            #TODO create threads with range startingNode : startingNode+rangeEachThread

            startingNode+=rangeEachThread
            # if no more moves break early


        #make last thread range correct
        if needLastThread:
            lastRange =  (len(self.root.children)-1)-startingNode
            print(lastRange)
            #TODO  make last thread


        #Wait for caluations


        #find best move based on return


        #return best move




    def threadWorker(self,start,end):
        #delete children outside of range
        children = {}
        for x in range(start,end+1):
            children[x]=self.root.children[x]
        self.root.children = children

        # start iterative deepening search






        print()

    def singleThreaded(self):
        self.root.generateChildren2(self.masterBoard,self.minionBoard)
        #print("SHOULD Both BE FULL")
        #self.minionBoard.printBoard()
       #print(self.minionBoard.reverseMoves)
        #self.masterBoard.printBoard()
        #print(self.masterBoard.reverseMoves)
        #print(len(self.root.children))
        move = self.iterativeDeepening()



    def iterativeDeepening(self):
        depth=0
        while True:
            print("depth:"+str(depth))
            result = self.alphaBeta(self.root, depth, -float('inf'), float('inf'))
            #TODO time limit
            if result[1] == False:
                break
            depth+=1
        return result

    #returns 3 things uValue(of child),moreToGet(bool)
    def alphaBeta(self,root,depth, alpha, beta):
        # create roots children

        if len(root.children)==0:
            root.generateChildren2(self.masterBoard,self.minionBoard)
        #print("childLen: " + str(len(root.children)))
        # if no children
        if len(root.children)==0:
            return root.uValue, False
        if depth ==0:
            return root.uValue,True

        if root.minOrMax == "max":
            uValue = -float('inf')
            # only calulate on nodes between start,end (incluesive)
            for x in root.children:
                result = self.alphaBeta(root.children[x],depth-1,alpha,beta)
                uValue = max(uValue, result[0])
                if uValue > beta:
                    break
                alpha=max(alpha,uValue)
            return uValue,result[1]
        else:
            uValue = float('inf')
            for x in root.children:
                result = self.alphaBeta(root.children[x], depth - 1, alpha, beta)
                uValue = min(uValue, result[0])
                if uValue < alpha:
                    break
                beta = min(beta, uValue)
            return uValue, result[1]

    # when only root node exists
    def aStarInital(self):

        #generate possable next moves while analyzing

        #go though the board and generate a new node for each possable move
        # for each box in the root board
        i=0
        #use a copy of the board to top dupicate moves
        rootBoardCopy = copy.deepcopy(self.root.board)

        for box in rootBoardCopy.boxes:
            # for each edge generate a new board with that edge removed
            # and create a new node to add too roots children
            while len(rootBoardCopy.boxes[box].edges) != 0:
                # remove the edge from the copy board to stop dupicate edges
                edge = list(rootBoardCopy.boxes[box].edges.keys())[0]
                newBoard = copy.deepcopy(self.root.board)
                newBoard.changeEdge(newBoard.boxes[box],edge)
                # remove the edge from the copy board to stop dupicate edges
                rootBoardCopy.changeEdge(rootBoardCopy.boxes[box], edge)
                self.root.children[i]=Node(newBoard,"min")
                i+=1



    def iterativeDeepeningTest(self):
        depth = 0
        while True:
            print("depth:" + str(depth))
            result = self.alphaBetaTest(self.root, depth, -float('inf'), float('inf'))
            # TODO time limit
            if result[1] == False:
                break
            depth += 1
        return result

        # returns 3 things uValue(of child),moreToGet(bool)

    def alphaBetaTest(self, root, depth, alpha, beta):
        # create roots children

        # print("childLen: " + str(len(root.children)))
        # if no children
        if len(root.children) == 0:
            return root.uValue, False
        if depth == 0:
            return root.uValue, True

        if root.minOrMax == "max":
            uValue = -float('inf')
            # only calulate on nodes between start,end (incluesive)
            for x in root.children:
                result = self.alphaBetaTest(root.children[x], depth - 1, alpha, beta)
                uValue = max(uValue, result[0])
                if uValue > beta:
                    break
                alpha = max(alpha, uValue)
            return uValue, result[1]
        else:
            uValue = float('inf')
            for x in root.children:
                result = self.alphaBetaTest(root.children[x], depth - 1, alpha, beta)
                uValue = min(uValue, result[0])
                if uValue < alpha:
                    break
                beta = min(beta, uValue)
            return uValue, result[1]




    def printRoot(self):
        print("ROOT"+"   util:"+str(self.root.uValue))
        print(self.root.moves)
        i=0
        for child in self.root.children:
            print("####### "+str(i)+"   util:"+str(self.root.children[child].uValue))
            print(self.root.children[child].moves)
            i+=1

    def printNodeComplex(self,root):
        print("ROOT "+root.minOrMax+"   util:"+str(root.uValue) + "  hval: "+str(root.hValue))
        print(root.moves)
        board2 = Board(self.size)
        board2.multipleMoves(root.moves)
        board2.printBoard()
        i=0
        for child in root.children:
            board = Board(self.size)
            board.multipleMoves(root.children[child].moves)
            print("####### "+str(i)+" "+root.children[child].minOrMax+"  uval:"+str(root.children[child].uValue) + "  hval: "+str(root.children[child].hValue))
            board.printBoard()
            i+=1

#max gets two boxes
def testBoard1():
    test = Board()
    for x in range(2,81):
        test.boxes[x].edges={}
    for x in test.dummyBoxesLeft:
        test.dummyBoxesLeft[x].edges={}
        test.dummyBoxesRight[x].edges = {}
        test.dummyBoxesTop[x].edges = {}
        test.dummyBoxesBot[x].edges = {}
    del test.boxes[1].edges[1]
    del test.boxes[1].edges[3]
    del test.boxes[1].edges[2]
    del test.boxes[0].edges[0]
    del test.boxes[0].edges[1]
    del test.boxes[0].edges[3]
    test.printBoard()

    test.changeEdge(test.boxes[0],2,"max")

    testNode = Node(test,"min")
    testSolver = Solver(-1,-1)
    testSolver.root=testNode
    testSolver.printRoot()

#min gets one box
def testBoard2():
    test = Board()
    for x in range(3,81):
        test.boxes[x].edges={}
    for x in test.dummyBoxesLeft:
        test.dummyBoxesLeft[x].edges={}
        test.dummyBoxesRight[x].edges = {}
        test.dummyBoxesTop[x].edges = {}
        test.dummyBoxesBot[x].edges = {}
    del test.boxes[1].edges[1]
    del test.boxes[1].edges[3]

    del test.boxes[0].edges[0]
    del test.boxes[0].edges[1]
    del test.boxes[0].edges[3]
    del test.boxes[2].edges[1]
    del test.boxes[2].edges[2]
    del test.boxes[2].edges[3]
    test.printBoard()
    test.changeEdge(test.boxes[0],2,"min")

    testNode = Node(test,"max")
    testSolver = Solver(-1,-1)
    testSolver.root=testNode
    testSolver.printRoot()

#test for alpha beta pruning
def testBoard3():
    test = Board()


    for i in range(0,3):
        for x in range(3,9):
                del test.boxes[x+i*9]

    for x in range(27,81):
        del test.boxes[x]

    for x in test.dummyBoxesLeft:
        test.dummyBoxesRight[x].edges = {}
        test.dummyBoxesBot[x].edges = {}
    for x in range(3, 9):
        test.dummyBoxesTop[x].edges = {}
        test.dummyBoxesLeft[x].edges = {}

    #box 0
    del test.boxes[0].edges[0]
    del test.boxes[0].edges[1]
    del test.dummyBoxesLeft[0].edges[2]
    #box1
    del test.boxes[1].edges[1]
    del test.boxes[1].edges[3]

    #box2
    del test.boxes[2].edges[3]
    test.boxes[2].edges[2]=test.dummyBoxesRight[0]
    test.dummyBoxesRight[0].edges[0]=test.boxes[2]
    # box9
    del test.boxes[9].edges[0]
    del test.boxes[9].edges[2]
    del test.dummyBoxesLeft[1].edges[2]
    # box10
    del test.boxes[10].edges[0]
    del test.boxes[10].edges[1]
    # box11
    del test.boxes[11].edges[1]
    test.boxes[11].edges[2] = test.dummyBoxesRight[1]
    test.dummyBoxesRight[1].edges[0]= test.boxes[11]

    # box18
    del test.boxes[18].edges[2]
    test.boxes[18].edges[3] = test.dummyBoxesBot[0]
    test.dummyBoxesBot[0].edges[1] = test.boxes[18]
    # box19
    del test.boxes[19].edges[0]
    del test.boxes[19].edges[3]
    # box20
    del test.boxes[20].edges[2]
    test.boxes[20].edges[3] = test.dummyBoxesBot[2]
    test.dummyBoxesBot[2].edges[1] = test.boxes[20]

    test.printBoard()
    test.printBox()


    #test.changeEdge(test.boxes[0],2,"min")

    testNode = Node(test,"max")
    testSolver = Solver(-1,-1)
    testSolver.root=testNode
    testSolver.printRoot()
    testSolver.singleThreaded()
    print("hihihi")
    testSolver.printRoot()


# max gets two boxes
def testBoard4():
    test = Board(9)

    #moves=[(0,1,"max"),(0,0,"min"),(0,2,"max"),(0,3,"min")]
    moves=[(8,1,"max"),(7,1,"min"),(7,0,"max"),(7,3,"min"),(8,2,"max"),(8,3,"min"),(7,2,"max")]

    test.multipleMoves(moves)
    print("val:"+str(test.uValue))
    test.reset()
    print("val:" + str(test.uValue))

# max gets two boxes
def testBoard5():
    testSolver = Solver([],9)
    testSolver.root.generateChildren2(testSolver.masterBoard,testSolver.minionBoard)
    print(len(testSolver.root.children))
    testSolver.printRootComplex()

def testBoard6():

    moveList=[]

    test = Board(3)
    test.printBoard()

    # box 0
    moveListFinal =[(0,0,"max"),(0,1,"max"),(1,1,"max"),(1,3,"max"),(2,3,"max"),(2,2,"max"),
                     (3,0,"max"),(3,2,"max"),
                     (6,2,"max"),(7,3,"max"),(8,2,"max")]


    testSolver = Solver(moveListFinal,3)
    testSolver.printNodeComplex(testSolver.root)
    testSolver.root.generateChildren2(testSolver.masterBoard,testSolver.minionBoard,testSolver.size)
    testSolver.printNodeComplex(testSolver.root)
    testSolver.root.children[0].generateChildren2(testSolver.masterBoard,testSolver.minionBoard,testSolver.size)
    print("child 0")
    testSolver.printNodeComplex(testSolver.root.children[0])
    print("child 1")
    testSolver.root.children[0].children[0].generateChildren2(testSolver.masterBoard,testSolver.minionBoard,testSolver.size)
    testSolver.printNodeComplex(testSolver.root.children[0].children[0])
    #testSolver.singleThreaded()

def testMinMax():

    # node a
    node9p = Node([(0,0,"9p")],"max",9)
    node5p = Node([(0,0,"5p")],"max",5)
    node7p = Node([(0,0,"7p")],"max",7)
    nodep = Node([(0,0,"p")],"min", 0)
    nodep.children[0]=node9p
    nodep.children[1] = node5p
    nodep.children[2] = node7p

    node6q = Node([(0,0,"6q")],"max", 6)
    node3q = Node([(0,0,"3q")],"max", 3)
    nodeq = Node([(0,0,"q")],"min", 0)
    nodeq.children[0] = node6q
    nodeq.children[1] = node3q


    nodek = Node([[(0,0,"k")]],"max", 0)
    nodek.children[0] = nodep
    nodek.children[1] = nodeq

    node4r = Node([[(0,0,"4r")]],"max", 4)
    node5r = Node([[(0,0,"5r")]],"max", 5)
    node6r = Node([[(0,0,"6r")]],"max", 6)
    noder = Node([[(0,0,"r")]],"min", 0)
    noder.children[0]=node4r
    noder.children[1] = node5r
    noder.children[2] = node6r

    node14s = Node([[(0,0,"14s")]],"max", 14)
    nodes = Node([[(0,0,"s")]],"min", 0)
    nodes.children[0] = node14s

    node8t = Node([[(0,0,"8t")]],"max", 8)
    node2t= Node([[(0,0,"2t")]],"max", 2)
    nodet = Node([[(0,0,"t")]],"min", 0)
    nodet.children[0] = node8t
    nodet.children[1] = node2t

    nodel = Node([[(0,0,"l")]],"max", 0)
    nodel.children[0] = noder
    nodel.children[1] = nodes
    nodel.children[2] = nodet

    nodea = Node([[(0,0,"a")]], "min", 0)
    nodea.children[0] = nodek
    nodea.children[1] = nodel

    #node b

    node8u = Node([[(0,0,"8u")]], "max", 8)
    node3u = Node([[(0,0,"3u")]], "max", 3)
    node12u = Node([[(0,0,"12u")]], "max", 12)
    nodeu = Node([[(0,0,"u")]], "min", 0)
    nodeu.children[0] = node8u
    nodeu.children[1] = node3u
    nodeu.children[2] = node12u

    node14v = Node([[(0,0,"14v")]], "max", 14)
    node4v = Node([[(0,0,"4v")]], "max", 4)
    nodev = Node([[(0,0,"v")]], "min", 0)
    nodev.children[0] = node14v
    nodev.children[1] = node4v

    nodem = Node([[(0,0,"m")]], "max", 0)
    nodem.children[0] = nodeu
    nodem.children[1] = nodev

    node7w = Node([[(0,0,"7w")]], "max", 7)
    node3w = Node([[(0,0,"3w")]], "max", 3)
    nodew = Node([[(0,0,"w")]], "min", 0)
    nodew.children[0] = node7w
    nodew.children[1] = node3w

    node9x = Node([[(0,0,"9x")]], "max", 9)
    node15x = Node([[(0,0,"15x")]], "max", 15)
    node20x = Node([[(0,0,"20x")]], "max", 20)
    nodex = Node([[(0,0,"x")]], "min", 0)
    nodex.children[0] = node9x
    nodex.children[1] = node15x
    nodex.children[2] = node20x

    noden = Node([[(0,0,"n")]], "max", 0)
    noden.children[0] = nodew
    noden.children[1] = nodex

    nodeb = Node([[(0,0,"b")]], "min", 0)
    nodeb.children[0] = nodem
    nodeb.children[1] = noden

    # c

    node8y = Node([[(0,0,"8y")]], "max", 8)
    nodey = Node([[(0,0,"y")]], "min", 0)
    nodey.children[0] = node8y

    node7z = Node([[(0,0,"7z")]], "max", 7)
    node2z = Node([[(0,0,"2z")]], "max", 2)
    nodez = Node([[(0,0,"z")]], "min", 0)
    nodez.children[0] = node7z
    nodez.children[1] = node2z

    nodeo = Node([[(0,0,"o")]], "max", 0)
    nodeo.children[0] = nodey
    nodeo.children[1] = nodez

    nodec = Node([[(0,0,"c")]], "min", 0)
    nodec.children[0] = nodeo

    nodef = Node([[(0,0,"f")]], "max", 0)
    nodef.children[0]=nodea
    nodef.children[1] = nodeb
    nodef.children[2] = nodec

    testSol=Solver([],9)
    testSol.root=nodef
    testSol.iterativeDeepeningTest()
    print()



# Press the green button in the gutter to run the script.
if __name__ == '__main__':




    """
    test = Board()
    test.printBoard()
    test.changeEdgeDontUpdate(test.boxes[0],0)
    test.printBoard()
    test.changeEdgeDontUpdate(test.boxes[11], 2)
    test.printBoard()
    test.changeEdgeDontUpdate(test.boxes[61], 1)
    test.printBoard()
    test.changeEdgeDontUpdate(test.boxes[53], 2)
    test.printBoard()
    test.changeEdgeDontUpdate(test.boxes[4], 1)
    test.changeEdgeDontUpdate(test.boxes[80], 3)
    test.printBoard()

    sol =Solver(-1,-1)
    sol.initlise()
    sol.printRoot()
"""




    #testBoard1()
    #testBoard2()
    #testBoard3()
    #testBoard4()
    #testBoard5()
    testBoard6()
    #testMinMax()


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
