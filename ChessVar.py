# Author: Josh Flenniken
# GitHub username: JoshFlenniken
# Date: 3/17/2024
# Description: Program for playing a special variant of chess with hunter and falcon fairy pieces. Includes classes
# all pieces, a board object, and various functions and methods to keep track of players, turns, game state, etc.

uni_icons = {
    'black_square': u'\u25FB',
    'black_pawn': u'\u265F',
    'black_rook': u'\u265C',
    'black_knight': u'\u265E',
    'black_bishop': u'\u265D',
    'black_king': u'\u265A',
    'black_queen': u'\u265B',
    'white_checker': u'\u25FC',
    'white_pawn': u'\u2659',
    'white_rook': u'\u2656',
    'white_knight': u'\u2658',
    'white_bishop': u'\u2657',
    'white_king': u'\u2654',
    'white_queen': u'\u2655'
}

class ChessVar:
    """
    Represents a variant of chess. Methods for incrementing/tracking turns, moving pieces, tracking gamestate, and
    various other functions to abstract a game of chess.
    """
    def __init__(self):
        """
        Creates a new game of chess, initializes turn count to 1 (white going first), initializes game state to
        UNFINISHED, creates Player 1 and Player 2 objects, creates a new Board object (which sets up pieces).
        Has methods for making moves to advance the game state and returning the game state.
        """
        self._turn = 1
        self._game_state = 'UNFINISHED'
        self._player_1 = Player('player_1', 'white')
        self._player_2 = Player('player_2', 'black')
        self._piece_generation_counter = 32
        self._new_board = Board()
        self._player_1.new_piece_set()
        self._player_2.new_piece_set()
        self._new_board.populate_board('black', 7, 8)
        self._new_board.populate_board('white', 2, 1)

    def get_new_board(self):
        """Returns the Board object for this ChessVar object"""
        return self._new_board

    def get_turn(self):
        """Returns the current turn count."""
        return self._turn

    def set_turn(self, turn):
        """Sets the current turn. Only necessary for debugging."""
        self._turn = turn

    def increment_turn(self):
        """
        Checks if a player has won the game and increments the turn counter. Called at the end of each
        valid make_move call.
        """
        if 'king' in self._player_1.get_captured_pieces_list():
            self._game_state = 'BLACK_WON'
        if 'king' in self._player_2.get_captured_pieces_list():
            self._game_state = 'WHITE_WON'
        self._turn += 1


    def get_piece_counter(self):
        """
        Returns a piece counter for use when populating a new board with pieces. Each number corresponds to
        a piece's starting space from left to right in order from a8—h1 (a8=32, b7=31, etc.). Decrements the counter
        by 1 when called.
        """
        piece_counter = self._piece_generation_counter
        self._piece_generation_counter -= 1
        return piece_counter

    def get_game_state(self):
        """Returns the game state."""
        return self._game_state

    def make_move(self, current_square, new_square):
        """
        Takes as arguments a space containing a player-controlled piece and a destination space (i.e. g5, f5).
         Validates that the 'from' space contains a piece controlled by the turn player and calls to the piece type's
         relevant valid_move method for a list of potentially valid moves, then checks for obstacles that would make the
          move illegal. Also checks if an opponent's piece was captured (and updates that piece's status in the
           player's active_pieces and captured_pieces data members if it was).

          Also checks if the opponent's king was just captured and increments the turn counter with a call to
           increment_turn. Returns a boolean True for a valid move, and False for an invalid one.
          """
        player_turn = ''
        if self._game_state != 'UNFINISHED':
            return False
        if self._turn % 2 == 1:  # 1 for white player, 0 for black player
            player_turn = 'white'
        else:
            player_turn = 'black'

        # checks that a player controlled piece is being selected, and that the source and destination squares are valid
        moving_piece = self._new_board.get_board_dict()[current_square]
        if moving_piece is None:
            return False
        if moving_piece.get_color() != player_turn:
            return False
        if current_square not in self._new_board.get_board_dict():
            return False
        if new_square not in self._new_board.get_board_dict():
            return False

        # converts algebraic coordinates to an integer-based data table number to send to the piece's valid_move
        # method for mathematical calculations.
        new_square_location = self._new_board.get_space_name_as_location(new_square)
        moving_piece_location = self._new_board.get_space_name_as_location(current_square)
        opponent_in_new_square = self._new_board.get_board_dict()[new_square]
        valid_move_list = moving_piece.valid_move(moving_piece_location, new_square_location, opponent_in_new_square)
        if valid_move_list is None:  # if None is returned from the piece's method, no valid move was calculated
            return False

        for move in valid_move_list:  # detects if another piece is blocking desired move
            if move != new_square_location and move != moving_piece_location:
                if self._new_board.get_board_dict()[self._new_board.get_location_as_space_name(move)] is not None:
                    return False

        # detects if a valid capture is being performed
        if opponent_in_new_square is not None:
            if player_turn == 'white':
                if opponent_in_new_square.get_color() == 'white':
                    return False
                else:
                    self._player_2.add_captured_piece(opponent_in_new_square.get_name())
                    self._player_2.remove_active_piece(opponent_in_new_square.get_name())
            if player_turn == 'black':
                if opponent_in_new_square.get_color() == 'black':
                    return False
                else:
                    self._player_1.add_captured_piece(opponent_in_new_square.get_name())
                    self._player_1.remove_active_piece(opponent_in_new_square.get_name())

        # move has been validated at this point, relevant updates performed here
        self._new_board.set_space_occupant(moving_piece, new_square)
        self._new_board.set_space_occupant(None, current_square)
        self.increment_turn()
        return True

    def entry_fairy_piece(self, piece_type, entry_square):
        """
        Method for entering a fairy piece. Checks that the turn Player has valid piece in their captured pieces
         list data member before allowing fairy piece entry, checks that the requested entry piece is in the player's
          fairy_piece_stable data member, then checks that the square they're entering on is both on their
         own backline by location number and unoccupied by any other piece (by calling the Board class's
        get_square_occupant method). If valid entry is performed, increment_turn is called (just as if make_move had
        been called).
        """
        player_turn = ''
        if self._turn % 2 == 1:
            player_turn = 'white'
        else:
            player_turn = 'black'

        # validates request from white player
        if player_turn == 'white' and self._new_board.get_space_name_as_location(entry_square) > 47:
            if self._new_board.get_board_dict()[entry_square] is None:
                if piece_type == 'F':
                    if 'falcon' in self._player_1.get_fairy_pieces_stable():
                        if 'rook' or 'knight' or 'bishop' or 'queen' in self._player_1.get_captured_pieces_list():
                            self._new_board.get_board_dict()[entry_square] = self._new_board.get_board_dict()['F']
                            self._player_1.remove_fairy_piece('falcon')
                            self.increment_turn()
                            return True
                if piece_type == 'H':
                    if 'hunter' in self._player_1.get_fairy_pieces_stable():
                        if 'rook' or 'knight' or 'bishop' or 'queen' in self._player_1.get_captured_pieces_list():
                            self._new_board.get_board_dict()[entry_square] = self._new_board.get_board_dict()['H']
                            self._player_1.remove_fairy_piece('hunter')
                            self.increment_turn()
                            return True

        # validates request from black player
        elif player_turn == 'black' and self._new_board.get_space_name_as_location(entry_square) < 16:
            if self._new_board.get_board_dict()[entry_square] is None:
                if piece_type == 'f':
                    if 'falcon' in self._player_1.get_fairy_pieces_stable():
                        if 'rook' or 'knight' or 'bishop' or 'queen' in self._player_1.get_captured_pieces_list():
                            self._new_board.get_board_dict()[entry_square] = self._new_board.get_board_dict()['f']
                            self._player_1.remove_fairy_piece('falcon')
                            self.increment_turn()
                            return True
                if piece_type == 'h':
                    if 'hunter' in self._player_1.get_fairy_pieces_stable():
                        if 'rook' or 'knight' or 'bishop' or 'queen' in self._player_1.get_captured_pieces_list():
                            self._new_board.get_board_dict()[entry_square] = self._new_board.get_board_dict()['h']
                            self._player_1.remove_fairy_piece('hunter')
                            self.increment_turn()
                            return True
        return False  # returns false if any necessary conditions aren't met


class Player:
    """
    Player object represents one of the two players. Has methods and variables for player's color (black or white),
    whether it's the player's turn, which pieces are active/inactive.
    """
    def __init__(self, name, color):
        """
        Creates new player, with data members for player name, assigned piece colors, and lists for the three states
        a player's pieces can be in.
        """
        self._name = name
        self._color = color
        self._active_pieces = []
        self._captured_pieces = []
        self._fairy_pieces_stable = []  # fairy pieces that haven't been entered yet

    def new_piece_set(self):
        """
        Will add a full set of pieces to a Player's self._active_pieces list for tracking king capture, falcon/hunter
        valid placement, etc.
        """
        for piece in range(1, 8):
            self._active_pieces.append('pawn')
        self._active_pieces.append('rook')
        self._active_pieces.append('rook')
        self._active_pieces.append('knight')
        self._active_pieces.append('knight')
        self._active_pieces.append('bishop')
        self._active_pieces.append('bishop')
        self._active_pieces.append('king')
        self._active_pieces.append('queen')
        self._fairy_pieces_stable.append('hunter')
        self._fairy_pieces_stable.append('falcon')

    def get_active_pieces_list(self):
        """Returns list of the player's active pieces."""
        return self._active_pieces

    def remove_active_piece(self, piece_name):
        """Removes a piece from the active_pieces list with piece name (lower case) as argument."""
        for piece in self._active_pieces:
            if piece == piece_name:
                self._active_pieces.remove(piece_name)
                return

    def add_captured_piece(self, piece_name):
        """Adds piece with parameter name (lower case) to captured_pieces list."""
        self._captured_pieces.append(piece_name)

    def get_captured_pieces_list(self):
        """Returns captured_pieces list."""
        return self._captured_pieces

    def get_fairy_pieces_stable(self):
        """Returns fairy_pieces_stable list."""
        return self._fairy_pieces_stable

    def remove_fairy_piece(self, piece_name):
        """Removes parameter-named piece from fairy_pieces_stable"""
        self._fairy_pieces_stable.remove(piece_name)


class Board:
    """Board object for holding the current positions of all active pieces. """
    def __init__(self):
        """
        Creates a new chess board object as a dictionary. Keys represent alphanumeric spaces cells, with Piece objects
        as values. Will have integration with ChessVar class to create and instantiate correct pieces on each player's
         side of the board at the beginning of a new game.

         Also contains a data table for converting those keys to integer location for move-validating calculations.
        """
        self._board_dict = dict(
            f = None, h = None,
            a8 = None, b8 = None, c8 = None, d8 = None, e8 = None, f8 = None, g8 = None, h8 = None,
            a7 = None, b7 = None, c7 = None, d7 = None, e7 = None, f7 = None, g7 = None, h7 = None,
            a6 = None, b6 = None, c6 = None, d6 = None, e6 = None, f6 = None, g6 = None, h6 = None,
            a5 = None, b5 = None, c5 = None, d5 = None, e5 = None, f5 = None, g5 = None, h5 = None,
            a4 = None, b4 = None, c4 = None, d4 = None, e4 = None, f4 = None, g4 = None, h4 = None,
            a3 = None, b3 = None, c3 = None, d3 = None, e3 = None, f3 = None, g3 = None, h3 = None,
            a2 = None, b2 = None, c2 = None, d2 = None, e2 = None, f2 = None, g2 = None, h2 = None,
            a1 = None, b1 = None, c1 = None, d1 = None, e1 = None, f1 = None, g1 = None, h1 = None,
            F = None, H = None
        )

        self._name_to_location_dict = dict(
            a8=0, b8=1, c8=2, d8=3, e8=4, f8=5, g8=6, h8=7,
            a7=8, b7=9, c7=10, d7=11, e7=12, f7=13, g7=14, h7=15,
            a6=16, b6=17, c6=18, d6=19, e6=20, f6=21, g6=22, h6=23,
            a5=24, b5=25, c5=26, d5=27, e5=28, f5=29, g5=30, h5=31,
            a4=32, b4=33, c4=34, d4=35, e4=36, f4=37, g4=38, h4=39,
            a3=40, b3=41, c3=42, d3=43, e3=44, f3=45, g3=46, h3=47,
            a2=48, b2=49, c2=50, d2=51, e2=52, f2=53, g2=54, h2=55,
            a1=56, b1=57, c1=58, d1=59, e1=60, f1=61, g1=62, h1=63
        )

    def populate_board(self, color, row_front, row_back):
        """
        Method to populate a new game board with pieces in their proper positions, as well as fairy pieces
         in reserve (not on board).
         """
        p1 = Pawn(color)
        self._board_dict['a' + str(row_front)] = p1
        p2 = Pawn(color)
        self._board_dict['b' + str(row_front)] = p2
        p3 = Pawn(color)
        self._board_dict['c' + str(row_front)] = p3
        p4 = Pawn(color)
        self._board_dict['d' + str(row_front)] = p4
        p5 = Pawn(color)
        self._board_dict['e' + str(row_front)] = p5
        p6 = Pawn(color)
        self._board_dict['f' + str(row_front)] = p6
        p7 = Pawn(color)
        self._board_dict['g' + str(row_front)] = p7
        p8 = Pawn(color)
        self._board_dict['h' + str(row_front)] = p8
        r1 = Rook(color)
        self._board_dict['a' + str(row_back)] = r1
        r2 = Rook(color)
        self._board_dict['h' + str(row_back)] = r2
        k1 = Knight(color)
        self._board_dict['b' + str(row_back)] = k1
        k2 = Knight(color)
        self._board_dict['g' + str(row_back)] = k2
        b1 = Bishop(color)
        self._board_dict['c' + str(row_back)] = b1
        b2 = Bishop(color)
        self._board_dict['f' + str(row_back)] = b2
        q1 = Queen(color)
        self._board_dict['d' + str(row_back)] = q1
        king = King(color)
        self._board_dict['e' + str(row_back)] = king
        if color == 'black':
            falcon = Falcon(color)
            self._board_dict['f'] = falcon
            hunter = Hunter(color)
            self._board_dict['h'] = hunter
        elif color == 'white':
            falcon = Falcon(color)
            self._board_dict['F'] = falcon
            hunter = Hunter(color)
            self._board_dict['H'] = hunter


    def get_board_dict(self):
        """Returns board dictionary."""
        return self._board_dict

    def get_space_occupant(self, space_name):
        """
        Returns the color and piece type name of the piece occupying a parameter space as a string,
        i.e. 'black pawn'. Returns None if the space is empty.
        """
        if self._board_dict[str(space_name)] is not None:
            return str(self._board_dict[space_name].get_color()) + str(self._board_dict[space_name].get_name())
        return None

    def set_space_occupant(self, piece_object, space_name):
        """Takes a Piece object and space name as parameters and sets the piece as occupying that space."""
        self._board_dict[space_name] = piece_object

    def get_name_to_location_dict(self):
        """Returns name_to_location_dictionary for positional calculations."""
        return self._name_to_location_dict

    def get_space_name_as_location(self, space_name=None):
        """
        Takes a space parameter and returns the equivalent location number, 0-63. For use in determining legal
        moves.
        """
        if space_name in self._board_dict:
            return self._name_to_location_dict[space_name]
        return None

    def get_location_as_space_name(self, location):
        """Takes a location integer and returns the equivalent alphanumeric cell name."""
        for key, value in self._name_to_location_dict.items():
            if location == value:
                return key

    def display_board_white(self):
        """Prints a visual representation of the current board from the perspective of the white player."""
        alpha_range = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        white_space = True
        row_count = 0
        for num in reversed(range(1, 9)):
            print_list = []
            for alpha in alpha_range:
                print_list.append(str(alpha) + str(num))
            print_row = ''
            for key in print_list:
                if key != 'F' or 'H' or "f" or 'h':
                    if self._board_dict[key] is None and white_space is True:
                        print_row += u'\u25FB' + '  '
                    else:
                        print_row += self._board_dict[key].get_icon() + '  '
            print(print_row)


class Pawn:
    """Pawn-type subclass that inherits from the main Piece class."""

    def __init__(self, color):
        """
        Creates a new Pawn object of the parameter color. Has a first_move data member for
        determining move legality.
        """
        self._piece_name = 'pawn'
        self._color = color
        self._first_move = True
        self._move = None
        self._location = None
        self._edge_one = [0, 8, 16, 24, 32, 40, 48, 56]
        self._edge_eight = [7, 15, 23, 31, 39, 47, 55, 63]
        if color == 'white':
            self._icon = u'\u2659'
        elif color == 'black':
            self._icon = u'\u265F'

    def get_icon(self):
        """Returns the unicode for the piece's icon."""
        return self._icon

    def get_color(self):
        """Returns the piece's color as a string."""
        return self._color

    def get_name(self):
        """Returns piece's name as a string."""
        return self._piece_name

    def valid_move(self, current_location, new_location, new_location_occupant):
        """
        Called by make_move method in ChessVar. Returns a list of all valid locations a called pawn could
         legally move.
         """
        # valid moves if piece is not on the edge of the board
        if current_location not in self._edge_one and current_location not in self._edge_eight:
            if self._color == 'black':  # valid moves for black piece, not on either edge
                if current_location + 8 == new_location and new_location_occupant is None:
                    self._first_move = False
                    return [new_location]
                if current_location + 16 == new_location and self._first_move is True and new_location_occupant is None:
                    self._first_move = False
                    return [current_location + 8, new_location]
                if new_location_occupant is not None:
                    if new_location_occupant.get_color() == 'black':
                        return None
                    if current_location + 7 == new_location or current_location + 9 == new_location:
                        if new_location_occupant.get_color() == 'white':
                            self._first_move = False
                            return [new_location]
                return None

            if self._color == 'white':  # Valid moves if piece is white, not on either edge of board
                if current_location - 8 == new_location and new_location_occupant is None:
                    self._first_move = False
                    return [new_location]
                if current_location - 16 == new_location and self._first_move is True and new_location_occupant is None:
                    self._first_move = False
                    return [current_location - 8, new_location]
                if new_location_occupant is not None:
                    if current_location - 7 == new_location or current_location - 9 == new_location:
                        if new_location_occupant.get_color() == 'black':
                            self._first_move = False
                            return [new_location]
                return None

        if current_location in self._edge_one:
            if self._color == 'black':  # valid moves for black piece on edge one (left)
                if current_location + 8 == new_location and new_location_occupant is None:
                    self._first_move = False
                    return [new_location]
                if current_location + 16 == new_location and self._first_move is True and new_location_occupant is None:
                    self._first_move = False
                    return [current_location + 8, new_location]
                if new_location_occupant is not None:
                    if current_location + 9 == new_location:
                        if new_location_occupant.get_color() == 'white':
                            self._first_move = False
                            return [new_location]
                return None

        if current_location in self._edge_eight:
            if self._color == 'black':  # valid moves for black piece on edge eight (right)
                if current_location + 8 == new_location and new_location_occupant is None:
                    self._first_move = False
                    return [new_location]
                if current_location + 16 == new_location and self._first_move is True and new_location_occupant is None:
                    self._first_move = False
                    return [current_location + 8, new_location]
                if new_location_occupant is not None:
                    if current_location + 7 == new_location:
                        if new_location_occupant.get_color() == 'white':
                            self._first_move = False
                            return [new_location]
                return None

        if current_location in self._edge_one:
            if self._color == 'white':  # valid moves for white piece on edge one (left)
                if current_location - 8 == new_location and new_location_occupant is None:
                    self._first_move = False
                    return [new_location]
                if current_location - 16 == new_location and self._first_move is True and new_location_occupant is None:
                    self._first_move = False
                    return [current_location - 8, new_location]
                if new_location_occupant is not None:
                    if current_location - 7 == new_location:
                        if new_location_occupant.get_color() == 'black':
                            self._first_move = False
                            return [new_location]
                return None

        if current_location in self._edge_eight:
            if self._color == 'white':  # valid moves for white piece on edge eight (right)
                if current_location - 8 == new_location and new_location_occupant is None:
                    self._first_move = False
                    return [new_location]
                if current_location - 16 == new_location and self._first_move is True and new_location_occupant is None:
                    self._first_move = False
                    return [current_location - 8, new_location]
                if new_location_occupant is not None:
                    if current_location - 9 == new_location:
                        if new_location_occupant.get_color() == 'black':
                            self._first_move = False
                            return [new_location]
                return None

class Rook:
    """Rook-type subclass that inherits from the main Piece class."""

    def __init__(self, color):
        """Creates a new Rook object of the parameter color."""
        self._piece_name = 'rook'
        self._color = color
        self._edge_one = [0, 8, 16, 24, 32, 40, 48, 56]
        self._edge_eight = [7, 15, 23, 31, 39, 47, 55, 63]
        self._move = None
        self._location = None
        if color == 'white':
            self._icon = u'\u2656'
        elif color == 'black':
            self._icon = u'\u265C'

    def valid_move(self, current_location, new_location, new_location_occupant=None):
        """
        Move validator that calculates whether a requested move (from make_move method in ChessVar) is legal
        using the location number (based on spaces entered), turn counter (for player control) and piece color, and
        the piece's unique move set.
        """
        valid_move_list = []
        if (current_location - new_location) % 8 == 0:
            if current_location < new_location:
                for location in range(current_location, new_location+1):
                    if (current_location - location) % 8 == 0:
                        valid_move_list.append(location)
                return valid_move_list
            if current_location > new_location:
                for location in range(new_location, current_location+1):
                    if (current_location - location) % 8 == 0:
                        valid_move_list.append(location)
            return valid_move_list
        elif 0 <= current_location <= 7 and 0 <= new_location <= 7:
            if current_location > new_location:
                for location in range(new_location, current_location+1):
                    valid_move_list.append(location)
            if new_location < current_location:
                for location in range(current_location, new_location+1):
                    valid_move_list.append(location)
            return valid_move_list
        elif 8 <= current_location <= 15 and 8 <= new_location <= 15:
            if current_location > new_location:
                for location in range(new_location, current_location+1):
                    valid_move_list.append(location)
            if new_location < current_location:
                for location in range(current_location, new_location+1):
                    valid_move_list.append(location)
            return valid_move_list
        elif 16 <= current_location <= 23 and 16 <= new_location <= 23:
            if current_location > new_location:
                for location in range(new_location, current_location+1):
                    valid_move_list.append(location)
            if new_location < current_location:
                for location in range(current_location, new_location+1):
                    valid_move_list.append(location)
            return valid_move_list
        elif 24 <= current_location <= 31 and 24 <= new_location <= 31:
            if current_location > new_location:
                for location in range(new_location, current_location+1):
                    valid_move_list.append(location)
            if new_location < current_location:
                for location in range(current_location, new_location+1):
                    valid_move_list.append(location)
            return valid_move_list
        elif 32 <= current_location <= 39 and 32 <= new_location <= 39:
            if current_location > new_location:
                for location in range(new_location, current_location+1):
                    valid_move_list.append(location)
            if new_location < current_location:
                for location in range(current_location, new_location+1):
                    valid_move_list.append(location)
            return valid_move_list
        elif 40 <= current_location <= 47 and 40 <= new_location <= 47:
            if current_location > new_location:
                for location in range(new_location, current_location+1):
                    valid_move_list.append(location)
            if new_location < current_location:
                for location in range(current_location, new_location+1):
                    valid_move_list.append(location)
            return valid_move_list
        elif 48 <= current_location <= 55 and 48 <= new_location <= 55:
            if current_location > new_location:
                for location in range(new_location, current_location+1):
                    valid_move_list.append(location)
            if new_location < current_location:
                for location in range(current_location, new_location+1):
                    valid_move_list.append(location)
            return valid_move_list
        elif 56 <= current_location <= 63 and 56 <= new_location <= 63:
            if current_location > new_location:
                for location in range(new_location, current_location+1):
                    valid_move_list.append(location)
            if new_location < current_location:
                for location in range(current_location, new_location+1):
                    valid_move_list.append(location)
            return valid_move_list
        return None



    def get_icon(self):
        """Returns the unicode for the piece's icon."""
        return self._icon

    def get_color(self):
        """Returns piece's color as string."""
        return self._color

    def get_name(self):
        """Returns piece's name as string."""
        return self._piece_name


class Bishop:
    """Bishop-type subclass that inherits from the main Piece class."""

    def __init__(self, color):
        """Creates a new Bishop object of the parameter color."""
        self._piece_name = 'bishop'
        self._color = color
        self._edge_one = [0, 8, 16, 24, 32, 40, 48, 56]
        self._edge_eight = [7, 15, 23, 31, 39, 47, 55, 63]
        self._move = None
        self._location = None
        if color == 'white':
            self._icon = u'\u2657'
        elif color == 'black':
            self._icon = u'\u265D'

    def valid_move(self, current_location, new_location, new_location_occupant=None):
        """
        Move validator that calculates whether a requested move (from make_move method in ChessVar) is legal
        using the location number (based on spaces entered), turn counter (for player control) and piece color, and
        the piece's unique move set.
        """
        if (current_location - new_location) % 7 == 0:
            if current_location > new_location:
                valid_move_list = []
                for location in range(new_location, current_location+1):
                    if abs(location - current_location) % 7 == 0:
                        valid_move_list += [location]
                    return valid_move_list
            elif new_location > current_location:
                valid_move_list = []
                for location in range(current_location, new_location+1):
                    if abs(location - current_location) % 7 == 0:
                        valid_move_list += [location]
                    return valid_move_list
        elif (current_location - new_location) % 9 == 0:
            if current_location > new_location:
                valid_move_list = []
                for location in range(new_location, current_location+1):
                    if abs(location - current_location) % 9 == 0:
                        valid_move_list += [location]
                return valid_move_list
            elif new_location > current_location:
                valid_move_list = []
                for location in range(current_location, new_location+1):
                    if abs(location - current_location) % 9 == 0:
                        valid_move_list += [location]
                return valid_move_list
        return None


    def get_icon(self):
        """Returns the unicode for the piece's icon."""
        return self._icon

    def get_color(self):
        """Returns piece's color as string."""
        return self._color

    def get_name(self):
        """Returns piece's name as string."""
        return self._piece_name


class Knight:
    """Knight-type subclass that inherits from the main Piece class."""

    def __init__(self, color):
        """Creates a new Knight object of the parameter color."""
        self._piece_name = 'knight'
        self._color = color
        self._first_move = True
        self._move = None
        self._location = None
        if color == 'white':
            self._icon = u'\u2658'
        elif color == 'black':
            self._icon = u'\u265E'

    def valid_move(self, current_location, new_location, new_location_occupant=None):
        """
        Move validator that calculates whether a requested move (from make_move method in ChessVar) is legal
        using the location number (based on spaces entered), turn counter (for player control) and piece color, and
        the piece's unique move set.
        """
        if abs((current_location - new_location)) / 6 == 1 or abs((current_location - new_location)) / 10 == 1\
            or abs((current_location - new_location)) / 14 == 1 or abs((current_location - new_location)) / 15 == 1\
            or abs((current_location - new_location)) / 17 == 1:
              return [new_location]
        return None

    def get_icon(self):
        """Returns the unicode for the piece's icon."""
        return self._icon

    def get_color(self):
        """Returns piece's color as string."""
        return self._color

    def get_name(self):
        """Returns piece's name as string."""
        return self._piece_name


class Queen:
    """Queen-type subclass that inherits from the main Piece class."""

    def __init__(self, color):
        """Creates a new Queen object of the parameter color."""
        self._piece_name = 'queen'
        self._color = color
        self._first_move = True
        self._move = None
        self._location = None
        if color == 'white':
            self._icon = u'\u2655'
        elif color == 'black':
            self._icon = u'\u265B'

    def valid_move(self, current_location, new_location, new_location_occupant=None):
        """
        Move validator that calculates whether a requested move (from make_move method in ChessVar) is legal
        using the location number (based on spaces entered), turn counter (for player control) and piece color, and
        the piece's unique move set.
        """
        valid_move_list = []
        if (current_location - new_location) % 8 == 0:
            if current_location < new_location:
                for location in range(current_location, new_location + 1):
                    if abs((current_location - location)) % 8 == 0:
                        valid_move_list.append(location)
                return valid_move_list
            if current_location > new_location:
                for location in range(new_location, current_location + 1):
                    if abs((current_location - location)) % 8 == 0:
                        valid_move_list.append(location)
            return valid_move_list
        elif 0 <= current_location <= 7 and 0 <= new_location <= 7:
            if current_location > new_location:
                for location in range(new_location, current_location + 1):
                    valid_move_list.append(location)
            if new_location < current_location:
                for location in range(current_location, new_location + 1):
                    valid_move_list.append(location)
            return valid_move_list
        elif 8 <= current_location <= 15 and 8 <= new_location <= 15:
            if current_location > new_location:
                for location in range(new_location, current_location + 1):
                    valid_move_list.append(location)
            if new_location < current_location:
                for location in range(current_location, new_location + 1):
                    valid_move_list.append(location)
            return valid_move_list
        elif 16 <= current_location <= 23 and 16 <= new_location <= 23:
            if current_location > new_location:
                for location in range(new_location, current_location + 1):
                    valid_move_list.append(location)
            if new_location < current_location:
                for location in range(current_location, new_location + 1):
                    valid_move_list.append(location)
            return valid_move_list
        elif 24 <= current_location <= 31 and 24 <= new_location <= 31:
            if current_location > new_location:
                for location in range(new_location, current_location + 1):
                    valid_move_list.append(location)
            if new_location < current_location:
                for location in range(current_location, new_location + 1):
                    valid_move_list.append(location)
            return valid_move_list
        elif 32 <= current_location <= 39 and 32 <= new_location <= 39:
            if current_location > new_location:
                for location in range(new_location, current_location + 1):
                    valid_move_list.append(location)
            if new_location < current_location:
                for location in range(current_location, new_location + 1):
                    valid_move_list.append(location)
            return valid_move_list
        elif 40 <= current_location <= 47 and 40 <= new_location <= 47:
            if current_location > new_location:
                for location in range(new_location, current_location + 1):
                    valid_move_list.append(location)
            if new_location < current_location:
                for location in range(current_location, new_location + 1):
                    valid_move_list.append(location)
            return valid_move_list
        elif 48 <= current_location <= 55 and 48 <= new_location <= 55:
            if current_location > new_location:
                for location in range(new_location, current_location + 1):
                    valid_move_list.append(location)
            if new_location < current_location:
                for location in range(current_location, new_location + 1):
                    valid_move_list.append(location)
            return valid_move_list
        elif 56 <= current_location <= 63 and 56 <= new_location <= 63:
            if current_location > new_location:
                for location in range(new_location, current_location + 1):
                    valid_move_list.append(location)
            if new_location < current_location:
                for location in range(current_location, new_location + 1):
                    valid_move_list.append(location)
            return valid_move_list

        if abs((current_location - new_location)) % 7 == 0:
            if current_location > new_location:
                for location in range(new_location, current_location+1):
                    if abs(location - current_location) % 7 == 0:
                        valid_move_list.append(location)
                return valid_move_list
            elif new_location > current_location:
                for location in range(current_location, new_location+1):
                    if abs(location - current_location) % 7 == 0:
                        valid_move_list.append(location)
                return valid_move_list
        elif abs(current_location - new_location) % 9 == 0:
            if current_location > new_location:
                for location in range(new_location, current_location+1):
                    if abs(location - current_location) % 9 == 0:
                        valid_move_list.append(location)
                return valid_move_list
            elif new_location > current_location:
                for location in range(current_location, new_location+1):
                    if abs(location - current_location) % 9 == 0:
                        valid_move_list.append(location)
                return valid_move_list
        return None

    def get_icon(self):
        """Returns the unicode for the piece's icon."""
        return self._icon

    def get_color(self):
        """Returns piece's color as string."""
        return self._color

    def get_name(self):
        """Returns piece's name as string."""
        return self._piece_name


class King:
    """King-type subclass that inherits from the main Piece class."""

    def __init__(self, color):
        """Creates a new King object of the parameter color."""
        self._piece_name = 'king'
        self._color = color
        self._first_move = True
        self._move = None
        self._location = None
        if color == 'white':
            self._icon = u'\u2654'
        elif color == 'black':
            self._icon = u'\u265A'

    def valid_move(self, current_location, new_location, new_location_occupant=None):
        """
        Move validator that calculates whether a requested move (from make_move method in ChessVar) is legal
        using the location number (based on spaces entered), turn counter (for player control) and piece color, and
        the piece's unique move set.
        """
        if abs(current_location - new_location) / 9 == 1 or abs(current_location - new_location) / 8 == 1\
            or abs(current_location - new_location) / 7 == 1:
            return [new_location]
        elif current_location + 1 == new_location or current_location - 1 == new_location:
            return [new_location]
        return None

    def get_icon(self):
        """Returns the unicode for the piece's icon."""
        return self._icon

    def get_color(self):
        """Returns piece's color as string."""
        return self._color

    def get_name(self):
        """Returns piece's name as string."""
        return self._piece_name

class Hunter:
    """Hunter-type subclass that inherits from the main Piece class."""
    def __init__(self, color):
        """Creates a new Hunter object of the parameter color."""
        self._piece_name = 'hunter'
        self._color = color
        self._first_move = True
        self._move = None
        self._location = None
        if color == 'white':
            self._icon = u'\u21E7'
        elif color == 'black':
            self._icon = u'\u21C8'

    def valid_move(self, current_location, new_location, new_location_occupant=None):
        """
        Move validator that calculates whether a requested move (from make_move method in ChessVar) is legal
        using the location number (based on spaces entered), turn counter (for player control) and piece color, and
        the piece's unique move set.
        """
        valid_move_list = []
        if self._color == 'black':
            # rook-forward move set for black piece
            if new_location > current_location:
                if (current_location - new_location) % 8 == 0:
                    for location in range(current_location, new_location + 1):
                        if (current_location - location) % 8 == 0:
                            valid_move_list.append(location)
                    return valid_move_list
            # bishop-backward move set for black piece
            elif new_location < current_location:
                if (current_location - new_location) % 7 == 0:
                    for location in range(new_location, current_location + 1):
                        if location - current_location % 7 == 0:
                            valid_move_list.append(location)
                    return valid_move_list
                elif (current_location - new_location) % 9 == 0:
                    for location in range(new_location, current_location + 1):
                        if location - current_location % 9 == 0:
                            valid_move_list.append(location)
                    return valid_move_list
            return None

        if self._color == 'white':
            # rook-forward move set for white piece
            if new_location < current_location:
                if (current_location - new_location) % 8 == 0:
                    for location in range(new_location, current_location + 1):
                        if (current_location - location) % 8 == 0:
                            valid_move_list.append(location)
                    return valid_move_list
            # bishop-backward move set for white piece
            elif new_location > current_location:
                if (current_location - new_location) % 7 == 0:
                    for location in range(current_location, new_location + 1):
                        if location - current_location % 7 == 0:
                            valid_move_list.append(location)
                    return valid_move_list
                elif (current_location - new_location) % 9 == 0:
                    for location in range(current_location, new_location + 1):
                        if location - current_location % 9 == 0:
                            valid_move_list.append(location)
                    return valid_move_list
            return None

    def get_color(self):
        """Returns piece's color as string."""
        return self._color

    def get_icon(self):
        """Returns the unicode for the piece's icon."""
        return self._icon

    def get_name(self):
        """Returns piece's name as string."""
        return self._piece_name

class Falcon:
    """Falcon-type subclass that inherits from the main Piece class."""
    def __init__(self, color):
        """Creates a new Falcon object of the parameter color."""
        self._piece_name = 'falcon'
        self._color = color
        self._first_move = True
        self._move = None
        self._location = None
        if color == 'white':
            self._icon = u'\u2660'
        elif color == 'black':
            self._icon = u'\u2664'

    def valid_move(self, current_location, new_location, new_location_occupant=None):
        """
        Move validator that calculates whether a requested move (from make_move method in ChessVar) is legal
        using the location number (based on spaces entered), turn counter (for player control) and piece color, and
        the piece's unique move set.
        """
        valid_move_list = []
        if self._color == 'black':
            # rook-backward move set for black piece
            if new_location < current_location:
                if (current_location - new_location) % 8 == 0:
                    for location in range(current_location, new_location + 1):
                        if (current_location - location) % 8 == 0:
                            valid_move_list.append(location)
                    return valid_move_list
            # bishop-forward move set for black piece
            elif new_location > current_location:
                if (current_location - new_location) % 7 == 0:
                    for location in range(new_location, current_location + 1):
                        if location - current_location % 7 == 0:
                            valid_move_list.append(location)
                    return valid_move_list
                elif (current_location - new_location) % 9 == 0:
                    for location in range(new_location, current_location + 1):
                        if location - current_location % 9 == 0:
                            valid_move_list.append(location)
                    return valid_move_list
            return None


        elif self._color == 'white':
            # rook-backward move set for white piece
            if new_location > current_location:
                if (current_location - new_location) % 8 == 0:
                    for location in range(current_location, new_location + 1):
                        if (current_location - location) % 8 == 0:
                            valid_move_list.append(location)
                    return valid_move_list
            # bishop-forward move set for white piece
            elif new_location < current_location:
                if (current_location - new_location) % 7 == 0:
                    for location in range(new_location, current_location + 1):
                        if location - current_location % 7 == 0:
                            valid_move_list.append(location)
                    return valid_move_list
                elif (current_location - new_location) % 9 == 0:
                    for location in range(new_location, current_location + 1):
                        if location - current_location % 9 == 0:
                            valid_move_list.append(location)
                    return valid_move_list
            return None

        if self._color == 'white':
            # rook-forward move set for white piece
            if new_location < current_location:
                if (current_location - new_location) % 8 == 0:
                    for location in range(new_location, current_location + 1):
                        if (current_location - location) % 8 == 0:
                            valid_move_list.append(location)
                    return valid_move_list
            # bishop-backward move set for white piece
            elif new_location > current_location:
                if (current_location - new_location) % 7 == 0:
                    for location in range(current_location, new_location + 1):
                        if location - current_location % 7 == 0:
                            valid_move_list.append(location)
                elif (current_location - new_location) % 9 == 0:
                    for location in range(current_location, new_location + 1):
                        if location - current_location % 9 == 0:
                            valid_move_list.append(location)
            return False

    def get_color(self):
        """Returns piece's color as string."""
        return self._color

    def get_icon(self):
        """Returns the unicode for the piece's icon."""
        return self._icon

    def get_name(self):
        """Returns piece's name as string."""
        return self._piece_name
