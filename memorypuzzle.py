# Memory Puzzle
# By Ladarius Greene

import random, pygame, sys
from pygame.locals import *

FPS = 30

window_width = 640
window_height = 480

reveal_speed = 8 # the speed in which boxes reveals and covers

box_size = 40 # size of box height and width in pixels
gap_size = 10 # size of gap between boxes in pixels

board_width = 10 # number of columns of icons
board_height = 7 # number of rows of icons

assert (board_width * board_height) % 2 == 0, "Board needs to have an even number of boxes for pairs of matches."

x_margin = int((window_width - (board_width * (box_size + gap_size))) /2)
y_margin = int((window_height - (board_height * (box_size + gap_size))) /2)

# Colors
Gray = (100, 100, 100)
NavyBlue = (60, 60, 100)
White = (255, 255, 255)
Red = (255, 0, 0)
Green = (0, 255, 0)
Blue = (0, 0, 255)
Yellow = (255, 255, 0)
Orange = (255, 128, 0)
Purple = (255, 0, 255)
Cyan = (0, 255, 255)

bg_color = NavyBlue
light_bg_color = Gray
box_color = White
highlight_color = Blue

Donut = "donut"
Square = "square"
Diamond = "diamond"
Lines = "lines"
Oval = "oval"

all_colors = (Red, Green, Blue, Yellow, Orange, Purple, Cyan)
all_shapes = (Donut, Square, Diamond, Lines, Oval)
assert len(all_colors) * len(all_shapes) * 2 >= board_width * board_height, "Board is too big for the number of shapes/colors defined."

def main():
    global FPSclock, window
    pygame.init()
    FPSclock = pygame.time.Clock()
    window = pygame.display.set_mode((window_width, window_height))

    mousex = 0 # used to store x coordinate of mouse event
    mousey = 0 # used to store y coordinate of mouse event
    pygame.display.set_caption("Memory Puzzle")

    mainBoard = getRandomizedBoard()
    revealedBoxes = generateRevealedBoxesData(False)

    firstSelection = None # stores the (x, y) of the first box clicked.

    window.fill(bg_color)
    startGameAnimation(mainBoard)

    while True: # main game loop
        mouseClicked = False

        window.fill(bg_color)
        drawBoard(mainBoard, revealedBoxes)

        # Applies mouse functionality.
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEMOTION:
                mousex, mousey = event.pos
            elif event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                mouseClicked = True

        # Applies box reveal, and unreveal rules.
        boxx, boxy = getBoxAtPixel(mousex, mousey)
        if boxx != None and boxy != None:
            #The mouse is currently over a box.
            if not revealedBoxes[boxx][boxy]:
                drawHighlightBox(boxx, boxy)
            if not revealedBoxes[boxx][boxy] and mouseClicked:
                revealBoxesAnimation(mainBoard, [(boxx, boxy)])
                revealedBoxes[boxx][boxy] = True # set the box as "revealed"
                if firstSelection == None: # the current box was the first box clicked.
                    firstSelection = (boxx, boxy)
                else: # the current box was the second box clicked.
                    # Check if there is a match between the two icons.
                    icon1shape, icon1color = getShapeAndColor(mainBoard, firstSelection[0], firstSelection[1])
                    icon2shape, icon2color = getShapeAndColor(mainBoard, boxx, boxy)
                    if icon1shape != icon2shape or icon1color != icon2color:
                        # Icons don't match. Re-cover up both selections.
                        pygame.time.wait(1000) # 1000 milliseconds = 1 sec
                        coverBoxesAnimation(mainBoard, [(firstSelection[0], firstSelection[1]), (boxx, boxy)])
                        revealedBoxes[firstSelection[0]][firstSelection[1]] = False
                        revealedBoxes[boxx][boxy] = False
                    elif hasWon(revealedBoxes): # check if all pairs found
                        gameWonAnimation(mainBoard)
                        pygame.time.wait(2000)

                        # Reset the board
                        mainBoard = getRandomizedBoard()
                        revealedBoxes = generateRevealedBoxesData(False)

                        # Show the fully unrevealed board for a second.
                        drawBoard(mainBoard, revealedBoxes)
                        pygame.display.update()
                        pygame.time.wait(1000)

                        # Replay the start game animation.
                        startGameAnimation(mainBoard)
                    firstSelection = None # reset firstSelection variable

            # Redraw the screen and wait a clock tick.
            pygame.display.update()
            FPSclock.tick(FPS)


def generateRevealedBoxesData(val):
    revealedBoxes = []
    for i in range(board_width):
        revealedBoxes.append([val] * board_height)
    return revealedBoxes

def getRandomizedBoard():
    # Get a list of every possible shape in every possible color.
    icons = []
    for color in all_colors:
        for shape in all_shapes:
            icons.append( (shape, color) )

    random.shuffle(icons) # randomize the order of the icons list
    numIconsUsed = int(board_width * board_height/2) # calculate how many icons are needed
    icons = icons[:numIconsUsed] * 2 # make two of each
    random.shuffle(icons)

    # Create the board data structure, with randomly placed icons.
    board = []
    for x in range(board_width):
        column = []
        for y in range(board_height):
            column.append(icons[0])
            del icons[0] # remove the icons as we assign them
        board.append(column)
    return board

def splitIntoGroupsOf(groupSize, theList):
    # splits a list into a list if lists, where the inner lists have a
    # most groupSize number of items.
    result = []
    for i in range(0, len(theList), groupSize):
        result.append(theList[i:i + groupSize])
    return result

def leftTopCoordsOfBox(boxx, boxy):
    # Convert board coordinates to pixel coordinates
    left = boxx * (box_size + gap_size) + x_margin
    top = boxy * (box_size + gap_size) + y_margin
    return (left, top)

def getBoxAtPixel(x, y):
    for boxx in range(board_width):
        for boxy in range(board_height):
            left, top = leftTopCoordsOfBox(boxx, boxy)
            boxRect = pygame.Rect(left, top, box_size, box_size)
            if boxRect.collidepoint(x, y):
                return (boxx, boxy)
    return (None, None)

def drawIcon(shape, color, boxx, boxy):
    quarter = int(box_size * 0.25) # syntactic sugar
    half = int(box_size * 0.5) # syntactic sugar

    left, top = leftTopCoordsOfBox(boxx, boxy) # get pixel coords from board coords
    # Draw the shapes
    if shape == Donut:
        pygame.draw.circle(window, color, (left + half, top + half), half - 5)
        pygame.draw.circle(window, bg_color, (left + half, top + half), quarter - 5)
    elif shape == Square:
        pygame.draw.rect(window, color, (left + quarter, top + quarter, box_size - half, box_size - half))
    elif shape == Diamond:
        pygame.draw.polygon(window, color, ((left + half, top), (left + box_size - 1, top + half), (left + half, top + box_size - 1), (left, top + half)))
    elif shape == Lines:
        for i in range(0, box_size, 4):
            pygame.draw.line(window, color, (left, top + i), (left + i, top))
            pygame.draw.line(window, color, (left + i, top + box_size - 1), (left + box_size - 1, top + i))
    elif shape == Oval:
        pygame.draw.ellipse(window, color, (left, top + quarter, box_size, half))

def getShapeAndColor(board, boxx, boxy):
    # shape value for x, y spot is stored in board [x] [y] [0]
    # color value for x, y spot is stored in board [x] [y] [1]
    return board[boxx][boxy][0], board[boxx][boxy][1]

def drawBoxCovers(board, boxes, coverage):
    # Draws boxes being covered/revealed. "boxes" is a list
    # of two-item lists, which have the x & y spot of the box.
    for box in boxes:
        left, top = leftTopCoordsOfBox(box[0], box[1])
        pygame.draw.rect(window, bg_color, (left, top, box_size, box_size))
        shape, color = getShapeAndColor(board, box[0], box[1])
        drawIcon(shape, color, box[0], box[1])
        if coverage > 0: #only draw the cover if there is a coverage
            pygame.draw.rect(window, box_color, (left, top, coverage, box_size))
    pygame.display.update()
    FPSclock.tick(FPS)

def revealBoxesAnimation(board, boxesToReveal):
    # Do the "box reveal" animation.
    for coverage in range(box_size, (-reveal_speed) -1, -reveal_speed):
        drawBoxCovers(board, boxesToReveal, coverage)

def coverBoxesAnimation(board, boxesToCover):
    # Do the "box cover" animation.
    for coverage in range(0, box_size + reveal_speed, reveal_speed):
        drawBoxCovers(board, boxesToCover, coverage)

def drawBoard(board, revealed):
    # Draw all of the boxes in their covered or revealed state.
    for boxx in range(board_width):
        for boxy in range(board_height):
            left, top = leftTopCoordsOfBox(boxx, boxy)
            if not revealed[boxx][boxy]:
                # Draw a covered box.
                pygame.draw.rect(window, box_color, (left, top, box_size, box_size))
            else:
                # Draw the (revealed) icon.
                shape, color = getShapeAndColor(board, boxx, boxy)
                drawIcon(shape, color, boxx, boxy)

def drawHighlightBox(boxx, boxy):
    left, top = leftTopCoordsOfBox(boxx, boxy)
    pygame.draw.rect(window, highlight_color, (left - 5, top - 5, box_size + 10, box_size + 10), 4)    

def startGameAnimation(board):
    # Randomly reveal the boxes 8 at a time.
    coveredBoxes = generateRevealedBoxesData(False)
    boxes = []
    for x in range(board_width):
        for y in range(board_height):
            boxes.append( (x, y) )
    random.shuffle(boxes)
    boxGroups = splitIntoGroupsOf(8, boxes)

    drawBoard(board, coveredBoxes)
    for boxGroup in boxGroups:
        revealBoxesAnimation(board, boxGroup)
        coverBoxesAnimation(board, boxGroup)

def gameWonAnimation(board):
    # flash the background color when the player has won.
    coveredBoxes = generateRevealedBoxesData(True)
    color1 = light_bg_color
    color2 = bg_color

    for i in range(13):
        color1, color2 = color2, color1 # swap colors
        window.fill(color1)
        drawBoard(board, coveredBoxes)
        pygame.display.update()
        pygame.time.wait(300)

def hasWon(revealedBoxes):
    # Return True if all the boxes have been revealed, otherwise False
    for i in revealedBoxes:
        if False in i:
            return False # return False if any boxes are covered.
    return True

if __name__ == '__main__':
    main()
