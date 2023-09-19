# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import copy
import string
import multiprocessing

class Box:


    def __init__(self,num):
        self.number=num
        self.edges={}
        self.wonByMe = 0


class Board:


    #this will only be done once to create the inital board
    #all other board configuations will be made by copying the last board then making the change
    def __init__(self):
        self.dummyBoxesTop={}
        self.dummyBoxesRight={}
        self.dummyBoxesLeft={}
        self.dummyBoxesBot={}
        self.boxes={}
        for i in range(9):
            self.dummyBoxesTop[i] = Box(i)
            self.dummyBoxesRight[i] = Box(i)
            self.dummyBoxesLeft[i] = Box(i)
            self.dummyBoxesBot[i] = Box(i)
        for i in range(81):
            self.boxes[i] = Box(i)
        # connect all the boxes
        for i in range(81):

            # connection numbering for a box
            #       1
            #    0  b  2
            #       3
            #connect left
            #if on left edge connect to dummy left
            if i % 9 == 0:

                self.dummyBoxesLeft[i/9].edges[2] = self.boxes[i]
                self.boxes[i].edges[0] = self.dummyBoxesLeft[i/9]
            else:
                self.boxes[i].edges[0] = self.boxes[i-1]

            #connect Right
            # if on Right edge connect to dummy Right
            if (i+1) % 9 == 0:

                self.dummyBoxesRight[((i+1) / 9) - 1].edges[0] = self.boxes[i]
                self.boxes[i].edges[2] = self.dummyBoxesRight[((i+1) / 9) - 1]
            else:
                self.boxes[i].edges[2] = self.boxes[i + 1]

            # connect Top
            # if on Top edge connect to dummy Top
            if i < 9:
                self.dummyBoxesTop[i].edges[3] = self.boxes[i]
                self.boxes[i].edges[1] = self.dummyBoxesTop[i]
            else:
                self.boxes[i].edges[1] = self.boxes[i-9]
            # connect Bot
            # if on bot edge connect to dummy bot
            if i >= 72:
                self.dummyBoxesTop[i-72].edges[1] = self.boxes[i]
                self.boxes[i].edges[3] = self.dummyBoxesTop[i-72]
            else:
                self.boxes[i].edges[3] = self.boxes[i+9]

    #does the change specified
    # nodeToChange stores the node whose edge will be changed
    # edge stores the edge to cut
    # 0 for left
    # 1 for top
    # 2 for right
    # 3 for bottom

    def changeEdge(self,nodeToChange,edge):

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

        #TODO add check for when box is taken



        #self.Board = copy.deepcopy(boardToCopy)

    #DOES NOT DO a rigrous check of connections
    def printBoard(self):
        print("----------------------------------------------------")
        print("!    0    1    2    3    4    5    6    7    8     !")

        row = 0;

        while row < 9:
            # top
            print("!    ", end="")
            for i in range(9):
                if self.boxes[i+row*9].edges.get(1) != None:
                    print("|", end="    ")
                else:
                    print(" ", end="    ")
            print(" !")

            # horzontal
            print("! ", end="")
            if self.dummyBoxesLeft[row].edges.get(2) != None:
                print(row, end="--")
            else:
                print(row, end="  ")
            for i in range(8):
                if self.boxes[i+row*9].edges.get(2) != None:
                    #formating
                    if row==0:
                        print(str(i + row * 9), end="----")
                    elif row==1:
                        if i + row * 9 == 9:
                            print(str(i + row * 9), end="----")
                        else:
                            print(str(i+row*9), end="---")

                    else:
                        print(str(i+row*9), end="---")

                else:
                    print(str(i+row*9), end="   ")
            if self.boxes[8+row*9].edges.get(2)!= None:
                print(str(8+row*9), end="--")
            else:
                print(str(8+row*9), end="  ")
            print(row,end="")

            if row == 0:
                print("  !")
            else:
                print(" !")


            row += 1

        #Bot
        print("!    ", end="")
        for i in range(72,81):
            if self.boxes[i].edges.get(3) != None:
                print("|", end="    ")
            else:
                print(" ", end="    ")
        print(" !")
        print("!    0    1    2    3    4    5    6    7    8     !")


        print("----------------------------------------------------")

class Node:

    def __init__(self,board,type):
        self.board=board
        self.minOrMax=type
        self.children = {}

        #calulate util
        self.util = 0
        for box in board.boxes:
            self.util+= board.boxes[box].wonByMe

    def generateChildren(self):
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
                newBoard.changeEdge(newBoard.boxes[box], edge)
                # remove the edge from the copy board to stop dupicate edges
                rootBoardCopy.changeEdge(rootBoardCopy.boxes[box], edge)

                #TODO need to change later based on multiple moves
                if self.minOrMax =="min":
                    self.children[i] = Node(newBoard, "max")
                else:
                    self.children[i] = Node(newBoard, "min")
                #TODO also NEED TO ADD ultil calulation for boxes
                i += 1



class Solver:
    def __init__(self, moveNode, moveEdge):
        self.root = Node(Board(),"max")
        # if going 2nd
        if moveNode != -1:
            self.root.board.changeEdge(moveNode,moveEdge)

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
            #create threads with range startingNode : startingNode+rangeEachThread
            startingNode+=rangeEachThread
            # if no more moves break early


        #make last thread range correct
        if needLastThread:
            lastRange =  (len(self.root.children)-1)-startingNode
            print(lastRange)
            # make last thread


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

    def iterativeDeepening(self):
        depth=0
        while True:
            result = self.alphaBeta(self.root, depth, -int('inf'), int('inf'))
            #TODO time limit
            if result[1] == False:
                break
            depth+=1

    #returns 3 things uValue(of child),moreToGet(bool)
    def alphaBeta(self,root,depth, alpha, beta):

        # if no more children
        if len(root.children)==0:
            return root.util, False
        if depth ==0:
            return root.util,True

        if self.root.minOrMax == "max":
            uValue = -int('inf')
            # only calulate on nodes between start,end (incluesive)
            for x in root.children:
                result = self.alphaBeta(self.root.children[x],depth-1,alpha,beta)
                uValue = max(uValue, result[0])
                if uValue > beta:
                    break
                alpha=max(alpha,uValue)
            return uValue,result[1]
        else:
            uValue = int('inf')
            for x in root.children:
                result = self.alphaBeta(self.root.children[x], depth - 1, alpha, beta)
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






    def aStarThreaded(self,root):
        print()

    def printRoot(self):
        print("ROOT")
        self.root.board.printBoard()
        i=0
        for child in self.root.children:
            print("####### "+str(i))
            self.root.children[child].board.printBoard()
            i+=1






def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

    dict = {1:"hi",2:"g"}

    for st in dict:
        print(st)


    test = Board()
    test.printBoard()
    test.changeEdge(test.boxes[0],0)
    test.printBoard()
    test.changeEdge(test.boxes[11], 2)
    test.printBoard()
    test.changeEdge(test.boxes[61], 1)
    test.printBoard()
    test.changeEdge(test.boxes[53], 2)
    test.printBoard()
    test.changeEdge(test.boxes[4], 1)
    test.changeEdge(test.boxes[80], 3)
    test.printBoard()

    sol =Solver(-1,-1)
    sol.initlise()
    sol.printRoot()
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
