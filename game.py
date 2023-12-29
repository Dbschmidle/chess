import random
import sys
from constants import *
from move import *
from board import *
from util import *
from piece import *
from computer import *
from GUI import *

"""
Defines a game of chess. 
- A board with alternating colored squares. Squares sometimes containing pieces.
- A player and a computer, each defined by their own classes.
- A turn marker, marking the color of whose turn it is.

The game also determines:
- Where its pieces are
- If a move is valid or not 
- Whether the user has stopped playing
- Getting all the possible moves for black or white.
- Moving pieces from one square to another.
- etc.

"""
class Game:
    def __init__(self, player, computer, board=Board()):
        self.board = board
        self.player = player
        self.computer = computer
        self.turn = COLORS[0] # white has first move
        self.inCheck = False
            
    def startGame(self):
        gui = GUI()
        while(1):
            gui.displayMenu()
        
            while(1):
                self.turn = COLORS[0]
                gui.displayBoard(self.board.getBoard(), self.turn)
                
                user_input = input("Your move...\n>")
                # make sure user input is valid and convert to proper form if necessary
                # exit the program if the user entered ex. "quit"
                if(gui.checkExit(user_input)):
                    break # go back to display menu loop
                
                user_move = Move(user_input)
                
                if(user_move.move == None):
                    print("Invalid move...")
                    continue 
                
                # find the piece associated with the players move 
                square = self.findFromSquare(user_move)
                if(square == None):
                    print("Piece not found...")
                    continue
                print(f"Piece found at: {square.label}")
                print(square.piece)
                
                # check those potential moves as being blocked, puts the player in checkmate

                legal_moves = self.getLegalMoves(square.piece)
                print(legal_moves)
                
                # check that the players choice is in legal_moves
                valid = False
                for move in legal_moves:
                    if(move.move == user_move.move):
                        valid = True
                        break
                if(not valid):
                    print(f"{user_move} is an invalid move...")
                    continue
                
                
                # move the player's piece to the designated square
                self.movePiece(square.label, user_move.getLabel())
                
                # change the turn to black
                self.turn = COLORS[1]
                
                # determine the computers move
                computerMove = Computer.computerMove(self)
                print(f"Computer: {computerMove}")
                # find the square associated with that move 
                computer_input = self.findFromSquare(computerMove)
                
                self.movePiece(computer_input.label, computerMove.getLabel())
    
    """
    Gets all the legal moves in this game given a piece on the board.
    Returns a list of moves in the format: 'Qb4', 'Pxd5', etc.
    """    
    def getLegalMoves(self, piece):
        pieceType = type(piece)
        if pieceType == Pawn:
            return self.pawnLegalMoves(piece)
        elif pieceType == Knight:
            return self.knightLegalMoves(piece)
        elif pieceType == Bishop:
            return self.bishopLegalMoves(piece)  
        elif pieceType == Rook:
            return self.rookLegalMoves(piece)
        elif pieceType == Queen:
            return self.queenLegalMoves(piece)
        else:
            return self.kingLegalMoves(piece)      
        
    def pawnLegalMoves(self, piece):
        valid_moves = []
        currentPosition = toIndexes(piece.currentSquare) # returns tuple of indexes

        if(piece.hasMoved == False):
            if(piece.color == COLORS[1]):
                # different coordinates for different colors
                newLabel = Move.toLabels((currentPosition[0] + 2, currentPosition[1]))
                
                # only count if there is no piece blocking
                if(not self.hasPiece(newLabel)):
                    valid_moves.append( Move("P"+newLabel) )
                
            else:
                # pawns can move 2 squares on their first turn 
                newLabel = Move.toLabels((currentPosition[0] - 2, currentPosition[1]))
                
                if(not self.hasPiece(newLabel)):
                    valid_moves.append( Move("P"+newLabel) )

        
        rowChange = 1 if self.turn == COLORS[1] else -1
            
        newPosition = (currentPosition[0] + rowChange, currentPosition[1])
        
        # check immediately in front of the pawn black or white
        if withinBoard(newPosition[0], newPosition[1]):
            newLabel = Move.toLabels(newPosition)
            if not self.hasPiece(newLabel):
                valid_moves.append(Move("P"+newLabel))
        
        # check for diagonal opponent pieces on the left and right side
        for value in (-1, 1):
            newPosition = (currentPosition[0] + rowChange, currentPosition[1] + value)
            if withinBoard(newPosition[0], newPosition[1]):
                newLabel = Move.toLabels(newPosition)
                diagonal_piece_color = self.hasPiece(newLabel)
                if diagonal_piece_color != None:                    
                    if diagonal_piece_color != self.turn:
                        # there is an opponent piece at the left diagonal
                        valid_moves.append(Move("Px"+newLabel))
                        
                        
        return valid_moves            
            
    def knightLegalMoves(self, piece):
        # get the board indexes of the horse 
        currentPosition = toIndexes(piece.currentSquare)
        valid_moves = []
        
        # the horse has 8 possible moves, some of which can be outside the range of the board
        values = ((-2,1),(-1,2),(1,2),(2,1),(2,-1),(1,-2),(-1,-2),(-2,-1))
        for value in values:
            # get a tuple of the new potential position
            newPosition = (currentPosition[0]+value[0], currentPosition[1]+value[1])
            
            # only add this new position to the potential moves if it is within the board coordinate system
            if(withinBoard(newPosition[0], newPosition[1])):
                
                newLabel = Move.toLabels(newPosition)
                
                # check if square is occupied and by which color piece
                potential_position_piece_color = self.hasPiece(newLabel)
                if(potential_position_piece_color == None):
                    # Blank space, append to valid moves
                    valid_moves.append(Move("N"+newLabel))
                    continue
                    
                if(potential_position_piece_color == self.turn):
                    # do not add to the list of moves if there is a piece as the same color of the potential position
                    continue
                
                if(potential_position_piece_color != self.turn):
                    # square is occupied by an opponent piece 
                    valid_moves.append(Move("Nx"+newLabel))
                
                
        return valid_moves
        
    def bishopLegalMoves(self, piece):
        currentPosition = toIndexes(piece.currentSquare)
        valid_moves = []
        values = ((-1, 1), (1, 1), (1, -1), (-1, -1)) # multipliers for each direction
        for i in values:
            for j in range(1, 8):
                newPosition = (currentPosition[0]+(j*i[0]), currentPosition[1]+(j*i[1]))
                
                # break out of this loop if outside the board and go to next diagonal
                if (not withinBoard(newPosition[0], newPosition[1])):
                    break

                # if a piece blocks this diagonal, check if it belongs to white or black
                newLabel = Move.toLabels(newPosition)
                potential_position_piece_color = self.hasPiece(newLabel)
                if(potential_position_piece_color != None):
                    # a piece exists at this square
                    # if the piece is the same color as the player then the position, and all after it are blocked
                    # if the piece is the opponents color, then only that square can be legally moved it, and all after it 
                    # are blocked 
                    if(potential_position_piece_color == self.turn):
                        break
                    else:
                        # opponent color case
                        valid_moves.append(Move(str(piece)+"x"+newLabel))
                        break
                
                # there is nothing in the path of the bishop, append to the possible moves list 
                valid_moves.append(Move(str(piece)+newLabel))
                
        return valid_moves

    def rookLegalMoves(self, piece):
        currentPosition = toIndexes(piece.currentSquare)
        valid_moves = []
        
        # horizontal/vertical movement
        # horizontal movement
        for i in range(-1, 2, 2):
            for j in range(1, 8):
                newPosition = (currentPosition[0], currentPosition[1]+(i*j))
                
                # check if the new position is within the board
                if(not withinBoard(newPosition[0], newPosition[1])):
                    break
                
                newLabel = Move.toLabels(newPosition)
                # check for piece blocking a square 
                newPositionPieceColor = self.hasPiece(newLabel)
                if(newPositionPieceColor == None):
                    # nothing blocking piece
                    valid_moves.append(Move(str(piece)+newLabel))
                    continue
                
                if(newPositionPieceColor == self.turn):
                    # blocked by same color piece 
                    break
                
                if(newPositionPieceColor != self.turn):
                    # blocked by opponent color piece
                    valid_moves.append(Move(str(piece)+"x"+newLabel))
                    break
                
        # vertical movement 
        for i in range(-1, 2, 2):
            for j in range(1, 8):
               
                newPosition = (currentPosition[0]+(i*j), currentPosition[1])
                newLabel = Move.toLabels(newPosition)
                
                if(not withinBoard(newPosition[0], newPosition[1])):
                    break
                
                newPositionPieceColor = self.hasPiece(newLabel)
                if(newPositionPieceColor == None):
                    # nothing blocking piece
                    valid_moves.append(Move(str(piece)+newLabel))
                    continue
                
                if(newPositionPieceColor == self.turn):
                    # blocked by same color piece 
                    break
                
                if(newPositionPieceColor != self.turn):
                    # blocked by opponent color piece
                    valid_moves.append(Move(str(piece)+"x"+newLabel))
                    break
                
        return valid_moves       
        
    def queenLegalMoves(self, piece):
        valid_moves = self.bishopLegalMoves(piece)
        valid_moves.extend(self.rookLegalMoves(piece))
        return valid_moves

    def kingLegalMoves(self, piece):
        currentPosition = toIndexes(piece.currentSquare)
        valid_moves = []
        
        # define the directional movement, goes clockwise 
        directions = ((-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1))
        for direction in directions:
            # get the new direction
            newPosition = (currentPosition[0] + direction[0], currentPosition[1] + direction[1])
            
        
            # skip if not in bounds
            if(not withinBoard(newPosition[0], newPosition[1])):
                continue
            
            toLabel = Move.toLabels(newPosition)
            
            # check for blocking piece 
            newPositionPieceColor = self.hasPiece(toLabel)
            if(newPositionPieceColor == None):
                # No blocking piece
                valid_moves.append(Move("K"+toLabel))
                    
            
            elif(newPositionPieceColor != self.turn):
                # Blocked by opponent piece
                valid_moves.append(Move("Kx"+toLabel))
                

                    
        return valid_moves
                
    """
    Determines if a given square specified by "label" has a piece.
    If a piece exists, returns the color of the piece.
    """
    def hasPiece(self, label:str):
        if(self.board.getSquare(label).hasPiece()):
            return self.board.getSquare(label).piece.color
        return None
        
    """ 
    Gets all of the possible moves for Black or White.
    Returns a 1d array of all the possible moves in label format ex. 'Bd4', 'Pxe5', etc.
    """  
    def getAllMoves(self, color):
        board = self.board.getBoard()
        allMoves = []
        
        for row in board:
            for square in row:
                if(square.piece != None):
                    if(square.piece.color == color):
                        piece_legal_moves = self.getLegalMoves(square.piece)
                        if(len(piece_legal_moves) == 0):
                            continue
                        allMoves.extend(piece_legal_moves)
                        
        return allMoves
        
     
    """
    Given a move find the current piece on the board associated with that move.
    Returns the square that the piece is on.
    """ 
    def findFromSquare(self, move):        
        # find the square that the piece is on
        for row in self.board.board:
            for square in row:
                if(str(square.piece) == move.move[0]):
                    if(square.piece.color == self.turn):
                        # found a potential piece 
                        # check the possible moves 
                        potential_moves = self.getLegalMoves(square.piece)
                        print(f"Potential Moves for {square.piece}{square.label}: ", end='')
                        print(potential_moves)
                        if(move in potential_moves):
                            # found, check for duplicates
                            if move.hasAmbiguitySymbol():
                                if square.piece.currentSquare[0] == move.getAmbiguitySymbol():
                                    # correct column/file
                                    return square
                                else:
                                    continue
                            # no duplicates (hopefully)
                            return square       
 
        
    """
    Moves a piece from 'fromLabel' to the 'toLabel'.
    Assumes this move is completely valid.
    Returns 1 on success.
    """
    def movePiece(self, fromLabel, toLabel):
        pieceCopy = None
        # find the fromLabel square
        for row in self.board.getBoard():
            for square in row:
                if(square.label == fromLabel):
                    # remove the piece from the square
                    pieceCopy = square.piece
                    square.piece = None


        if(pieceCopy == None):
            print("DEBUG: piece was not found on the board...")
            return

        # find the toLabel square
        for row in self.board.getBoard():
            for square in row:
                if (square.label == toLabel):
                    # add the piece to the square at the toLabel
                    pieceCopy.setCurrentSquare(toLabel)
                    square.piece = pieceCopy
                    
                    if(type(pieceCopy) == Pawn):
                        pieceCopy.hasMoved = True
                        
                    break
                    
                    
        return 1
    
    
    
    def causesCheck(self):
        return
    
    """
    Determines if a piece can be captured by the opponent.
    Returns True if it can, False otherwise.
    Particularly useful for determining valid moves.
    """
    def kingCanBeCaptured(self) -> bool:
        # get all opponent moves
        opponentColor = getOpponentColor(self.turn)
        opponentMoves = self.getAllMoves(opponentColor)

        # get current king square
        king_square = self.board.findPiece("K", self.turn)
        
        # compare toSquare of all the moves to the square of the king
        
        for move in opponentMoves:
            if move.toSquare == king_square.label():
                return True
        
        return False        
        
        
        
    def copy(self):
        new_game = Game(self.player, self.computer, self.board.copy())
        return new_game



class MoveGenerator:
    
    """
    Generates pseudo moves for black or white. Pseudo moves do NOT check for:
        - Black/White being in Check
        - Move causing the king to be captured by the opponent
        - Pawn promotions
    """
    def generatePseudoMoves():
        return 
    


    def generateLegalMoves():
        return

                     
        
class Player:
    def __init__(self, name, color=COLORS[0]):
        self.name = name
        self.color = color
        self.pieces = None



