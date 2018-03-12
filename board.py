''' 
board.py - the game board: logic and rending
author: Keagan Roos
'''

import enum
import math
from pygame import Rect, Surface, draw
import main
import inputter
from coords import *


# to indicate that the index of the board we are trying to access it out of 
# the range of the tiles array
class InvalidBoardIndex(): pass
INVALID_BOARD_INDEX = InvalidBoardIndex()   # was that an awkward thing to do?

#-----------------------------------------------------------------------------
# Board's data classes
#-----------------------------------------------------------------------------

# tester 

def all_tile_as_move_options(piece):
    return _brd.tiles

# helper functions that'll probably be useful in most of the *_move_opts functions

def board_index(rank, row):
    if not (0 <= row < _brd.NUM_TILES and 0 <= rank < _brd.NUM_TILES):
        return INVALID_BOARD_INDEX
    return row * _brd.NUM_TILES + rank


# add the tile with rank=rank and row=row if it is a valid board index i.e: it's actually in the board
# and the requirements of the state of that tiles piece are fufilled, i.e: the tile should be empty and 
# it is empty then we add otherwise we don't
# return the tile if we added one or none if we didn't, so that the caller can asses it i.e: the caller

# might want to access if the tile contained a piece in case that means we should stop looking for pieces
# in the case of pieces which cannot jump over other pieces, i.e: any piece except a Knight

class TilePieceReq(enum.Enum):
    MUST_BE_FILLED = 0
    MUST_BE_EMPTY  = 1
    CAN_BE_EITHER  = 2

    @classmethod
    def met(cls, req, state_filled):
        return req is cls.CAN_BE_EITHER or (req is cls.MUST_BE_FILLED and state_filled) or\
            (req is cls.MUST_BE_EMPTY and not state_filled)


def add_if_valid(tiles_ref, rank, row, must_have_piece=TilePieceReq.CAN_BE_EITHER):
    brd_index = board_index(rank, row)
    # assert brd_index == INVALID_BOARD_INDEX
    if brd_index != INVALID_BOARD_INDEX:
        tile = _brd.tiles[brd_index]
        if TilePieceReq.met(must_have_piece, bool(tile.piece)):
            if tile.piece and tile.piece.side == _brd.selected_tile.piece.side:
                return None
            tiles_ref.append(tile)
            return tile
    return None


# pawns are the only chess pieces that rely on a direction to
# to figure out their move options, the dir_ is where we look
# for a move option relative to the pieces position

def pawn_move_opts(piece):
    """ pawns move options (a pawn can move two a spaces forward on first turn, on every 
    turn: one space forward and diagonally right and left if there is an enemy there """
    dir_ = 1 if piece.side is 1 else -1
    tiles = []
    row  = piece.tile.row
    rank = piece.tile.rank
    add_if_valid(tiles, row,     rank + dir_, TilePieceReq.MUST_BE_EMPTY)
    if not piece.moved:
        add_if_valid(tiles, row,     rank + dir_ + dir_, TilePieceReq.MUST_BE_EMPTY)
    add_if_valid(tiles, row - 1, rank + dir_, TilePieceReq.MUST_BE_FILLED)
    add_if_valid(tiles, row + 1, rank + dir_, TilePieceReq.MUST_BE_FILLED)
    return tiles


def rook_move_opts(piece):
    """ rooks can move as far as they can in their row to the left of right or
    in their cols up or down """
    row = piece.tile.row
    rank = piece.tile.rank
    tiles = [] 
    
    # register "up"
    offset = 1
    while 1: 
        tile = add_if_valid(tiles, row, rank + offset)
        offset += 1
        if not tile or tile.piece: break

    # register "down"
    offset = 1
    while 1: 
        tile = add_if_valid(tiles, row, rank - offset)
        offset += 1
        if not tile or tile.piece: break

    # register "left"
    offset = 1
    while 1: 
        tile = add_if_valid(tiles, row - offset, rank)
        offset += 1
        if not tile or tile.piece: break

    # register "right"
    offset = 1
    while 1: 
        tile = add_if_valid(tiles, row + offset, rank)
        offset += 1
        if not tile or tile.piece: break

    return tiles


def knight_move_opts(piece):
    tiles = []
    row = piece.tile.row
    rank = piece.tile.rank
    add_if_valid(tiles, row + 2, rank + 1)
    add_if_valid(tiles, row + 2, rank - 1)
    add_if_valid(tiles, row - 2, rank + 1)
    add_if_valid(tiles, row - 2, rank - 1)
    add_if_valid(tiles, row + 1, rank + 2)
    add_if_valid(tiles, row - 1, rank + 2)
    add_if_valid(tiles, row + 1, rank - 2)
    add_if_valid(tiles, row - 1, rank - 2)
    return tiles


def bishop_move_opts(piece):
    tiles = []
    row = piece.tile.row
    rank = piece.tile.rank

    # register "down-right"
    offset = 1
    while 1: 
        tile = add_if_valid(tiles, row + offset, rank + offset)
        offset += 1
        if not tile or tile.piece: break

    # register "down-left"
    offset = 1
    while 1: 
        tile = add_if_valid(tiles, row - offset, rank + offset)
        offset += 1
        if not tile or tile.piece: break

    # register "up-right"
    offset = 1
    while 1: 
        tile = add_if_valid(tiles, row + offset, rank - offset)
        offset += 1
        if not tile or tile.piece: break

    # register "up-left"
    offset = 1
    while 1: 
        tile = add_if_valid(tiles, row - offset, rank - offset)
        offset += 1
        if not tile or tile.piece: break

    return tiles


def queen_move_opts(piece):
    """ I have decided to view the queen as a combination of a rook and 
    bishop instead of being related to the king. Queens can move in union of
    a Rook and Bishop"""
    row = piece.tile.row
    rank = piece.tile.rank
    tiles = bishop_move_opts(piece)
    tiles.extend(rook_move_opts(piece))
    return tiles

def king_move_opts(piece):
    row = piece.tile.row
    rank =  piece.tile.rank
    tiles = []
    add_if_valid(tiles, row - 1, rank - 1)
    add_if_valid(tiles, row, rank - 1)
    add_if_valid(tiles, row + 1, rank - 1)
    add_if_valid(tiles, row - 1, rank)
    add_if_valid(tiles, row + 1, rank)
    add_if_valid(tiles, row - 1, rank + 1)
    add_if_valid(tiles, row, rank + 1)
    add_if_valid(tiles, row + 1, rank + 1)
    return tiles

piece_type_switch = [
    ('Pawn' ,  pawn_move_opts),
    ('Rook',   rook_move_opts),
    ('Knight', knight_move_opts),
    ('Bishop', bishop_move_opts),
    ('Queen',  queen_move_opts),
    ('King',   king_move_opts),
]


class PieceData:

    SIDE_1_COLOR = (200, 200, 200)
    SIDE_2_COLOR = (50,   50,  50)

    def __init__(self, tile):
        self.rect = None
        self.side = 0        # the team of side of the piece
        self.tile = tile

        # used for moving pieces (visually indicating a move)
        #
        # - if a pieces offset is (0, 0) it's probably not moving if it's anything
        #   else: we draw it at it's tile offset in position by self.offset.
        #
        # - Only ever, as it stands, modify a pieces offset in the move_piece 
        #   generator routine

        self.offset = (0, 0) 

        # The only major difference between one piece type and another is where it 
        # is allowed to move to, so we only need to store that information, there
        # is no need for enums just names and move options

        self.move_opts_func = None
        self.name = ''

        # This is used for pawns and for some special moves
        self.moved = False


class TileData:
    def __init__(self, row: int, rank: int, color: (int, int, int), \
                 piece: PieceData = None):
        self.rect = None
        self.color = color
        self.row = row
        self.rank = rank
        self.piece = piece


class BoardInfo:
    ''' 
    all data relating to the board
    '''
    # in screen coords
    BOARD_SIZE = 0.75  

    # TODO(Keagan): Remember to remove this
    NUM_TILES = 8

    COLOR_TILE_DARK  = (175, 173, 169)
    COLOR_TILE_LIGHT = (250, 250, 242)
    BACKGROUND_COLOR = (212, 161, 156)
    
    def __init__(self):
        self.initialized = False

        self.move_in_progess     = False

        # pieces are moved by a generator function, when we want to start a 
        # move, we call _enact_move_piece which assigns the iterator of that
        # generator to self.cur_piece_move_iter and while 
        # self.move_in_progress we call next(self.cur_piece_move_iter) in 
        # update to further the move each frame

        self.cur_piece_move_iter = None  # the iterator object for when a piece is moving
                                         # for now only one thing will be moving at a time
        
        self.cur_piece_move_opts = None  # a set of opts to move to for the current piece
                                         # (current piece is self.selected_tile.piece)

        self.rect = None

        self.tile_size  = 0
        self.piece_size = 0
        # screen coords
        self.piece_margin = 15

        self.tiles  = []
        self.pieces = []

        self.hovered_tile  = None
        self.selected_tile = None

# board view info 
_brd = BoardInfo()

#-----------------------------------------------------------------------------
# Initialization Functions
#-----------------------------------------------------------------------------

def initialize(s: Surface, s_size: (int, int)):
    ''' initialize the board data '''
    _brd.rect = _calculate_board_rect(s, s_size)
    
    # piece values work as follows:
    # 0 -> Not a piece
    # 1 -> Pawn
    # 2 -> Rook
    # 3 -> Knight
    # 4 -> Bishop
    # 5 -> Queen
    # 6 -> King

    board_values  = ['2:1','3:1','4:1','6:1','5:1','4:1','3:1','2:1',
                     '1:1','1:1','1:1','1:1','1:1','1:1','1:1','1:1',
                     '0:0','0:0','0:0','0:0','0:0','0:0','0:0','0:0',
                     '0:0','0:0','0:0','0:0','0:0','0:0','0:0','0:0',
                     '0:0','0:0','0:0','0:0','0:0','0:0','0:0','0:0',
                     '0:0','0:0','0:0','0:0','0:0','0:0','0:0','0:0',
                     '1:2','1:2','1:2','1:2','1:2','1:2','1:2','1:2',
                     '2:2','3:2','4:2','6:2','5:2','4:2','3:2','2:2',]

    # NOTE: When piece_values is not correct in size, the no. of tiles created
    # gets affected since we enumerate over piece_values, this would be a
    # strange bug to have in my opinion and another implementation might be
    # considered more clear, but for now there's just an assert which does
    # the job in catching that wierdo bug

    assert len(board_values) == 64

    _brd.tile_size  = _brd.rect.width // _brd.NUM_TILES
    _brd.piece_size = _brd.tile_size - _brd.piece_margin 
    
    for i, board_val in enumerate(board_values):

        piece_value = int(board_val[0])
        # skip the board_val[1] which is always ':'
        piece_side  = int(board_val[2])

        row  = i % _brd.NUM_TILES
        rank = i // _brd.NUM_TILES

        def even_tile(row, rank) -> bool:
            ''' return true if the tiles linear index would be even '''
            return (row % 2 is 0 and rank % 2 is 0) or \
                (row % 2 is 1 and rank % 2 is 1)

        tile_color = _brd.COLOR_TILE_LIGHT if even_tile(row, rank)\
            else _brd.COLOR_TILE_DARK
        
        tile = TileData(row, rank, tile_color)

        tile.rect = _calculate_tile_rect(tile)
        
        if piece_value: # if the piece code is not zero create a new piece
            piece = PieceData(tile)
            tile.piece = piece
            piece.rect = _calculate_piece_rect(piece)

            # index into piece_type_switch, using the piece value, it acts like a switch
            # returning the corresponding piece name and move_opts_func
            # 
            # each piece_type is a 2-tuple (name, piece_opts_func)

            piece.name           = piece_type_switch[piece_value - 1][0]
            piece.move_opts_func = piece_type_switch[piece_value - 1][1]
            piece.side = piece_side

            _brd.pieces.append(piece)
    
        _brd.tiles.append(tile)

#-----------------------------------------------------------------------------

def _calculate_board_rect(s: Surface, s_size: (int, int)) -> Rect:   
    ''' calculate the values of the _board_rect '''
    # calculate the size of the board relative to the size of the screen
    # instead of a fixed number of pixels
    rect_left = 0.5 - _brd.BOARD_SIZE / 2
    rect_top  = 0.5 - _brd.BOARD_SIZE  / 2
    top, left = screen_coord_to_pixel(s_size, (rect_left, rect_top))
    width, height \
        = screen_coord_to_pixel(s_size, (_brd.BOARD_SIZE, _brd.BOARD_SIZE))
    # this final Rect is the board rect
    return Rect(top, left, width, height)

#-----------------------------------------------------------------------------

def _calculate_piece_rect(piece: PieceData) -> Rect:
    ''' given a piece calculate its rect '''
    return Rect(
        (piece.tile.row + piece.offset[0])  *_brd.tile_size + \
        _brd.piece_margin // 2 + _brd.rect.left,
        (piece.tile.rank + piece.offset[1]) * _brd.tile_size + \
        _brd.piece_margin // 2+ _brd.rect.top,
        _brd.piece_size,
        _brd.piece_size,
    )

#-----------------------------------------------------------------------------

def _calculate_tile_rect(tile: TileData) -> Rect:
    return Rect(
        tile.row * _brd.tile_size + _brd.rect.left,
        tile.rank * _brd.tile_size + _brd.rect.top,
        _brd.tile_size, _brd.tile_size
    )

#-----------------------------------------------------------------------------
# Update functions
#-----------------------------------------------------------------------------

def _move_piece(piece: PieceData, new_tile: TileData):
    """ A generator function to manipulate a piece's offset value to give the
    illusion of movement; update the data to show that the piece has actually 
    been moved """

    # TODO(Keagan): Look up some smoothing equations to make moves look more
    # interesting
    
    _brd.move_in_progess = True
    
    # TODO(Keagan): Lerne about pygame's time, I'm not sure how accurate
    # time.time would be
    STEPS = 30

    # TODO(Keagan): Create a Vec2 class lol
    diff = (new_tile.row - piece.tile.row, new_tile.rank - piece.tile.rank)
    total_dist = math.sqrt(diff[0] ** 2 + diff[1] ** 2)
    dir_ = (diff[0] / total_dist, diff[1] / total_dist) # normalize

    dist_travelled = 0.0
    dist_per_frame = total_dist / (STEPS * total_dist)
    move = (dir_[0] * dist_per_frame, dir_[1] * dist_per_frame)

    while dist_travelled < total_dist:
        piece.rect = _calculate_piece_rect(piece)
        piece.offset   = (piece.offset[0] + move[0], 
            piece.offset[1] + move[1])
        dist_travelled += dist_per_frame
        yield

    piece.offset = (0, 0)

    # do the move on the data side once the visual movement is done

    piece.tile.piece = None
    piece.tile = new_tile
    piece.moved = True

    # if we move into a tile that already has a piece then gobble it up 
    # FUCKING YUM

    # TODO(Keagan): This is just the naive impl, more work doth need'th to'th
    # be'th done'th
    
    if new_tile.piece:
        _brd.pieces.remove(new_tile.piece)
        new_tile.piece = None 

    new_tile.piece = piece
    _brd.selected_tile = None
    _brd.cur_piece_move_opts = None
    piece.rect = _calculate_piece_rect(piece)   
    
    return

#-----------------------------------------------------------------------------

def _enact_move_piece(piece: PieceData, new_tile: TileData):
    """  A wrapper function to get an iterator, and assign it to the 
    _brd.cur_piece_move_iter """
    
    _brd.move_in_progess = True
    _brd.selected_tile = None
    _brd.hovered_tile  = None
    _brd.cur_piece_move_iter = iter(_move_piece(piece, new_tile))

#-----------------------------------------------------------------------------

def update():
    """ update board based on any player input or game logic """

    # Begin Update Mouse Hover Code
    if not _brd.move_in_progess:
        mouse_index_in_board = INVALID_BOARD_INDEX
        mouse_pos = inputter.mouse_pos()
        rank = (mouse_pos[0] - _brd.rect.left) // _brd.tile_size
        row  = (mouse_pos[1] - _brd.rect.top)  // _brd.tile_size
    
        if 0 <= row < _brd.NUM_TILES and 0 <= rank < _brd.NUM_TILES:
            mouse_index_in_board = row * _brd.NUM_TILES + rank
            _brd.hovered_tile = _brd.tiles[mouse_index_in_board]
        else:
            _brd.hovered_tile = None
   
    # End Update Mouse Hover Code

    # NOTE(Keagan): This logic is going to get more complex when we introduce
    # the notion of teams and making moves and whatnot

    if _brd.move_in_progess:
        try:
            next(_brd.cur_piece_move_iter)
        except StopIteration:
            _brd.move_in_progess = False
    else:
        if mouse_index_in_board != INVALID_BOARD_INDEX and inputter.mouse_up(1):
            the_tile = _brd.tiles[mouse_index_in_board]
            
            # NOTE(Keagan): This is the simplified logic, what we might want 
            # to actually be doing in the future is asking if we clicked a 
            # tile with piece who's "team" matches the current turn's team 
            # and moving if we have

            if _brd.selected_tile and the_tile and the_tile is _brd.selected_tile:
                _brd.cur_piece_move_opts = None
                _brd.selected_tile = None

            elif the_tile.piece:
                if _brd.selected_tile and \
                    the_tile.piece.side != _brd.selected_tile.piece.side and\
                        the_tile in _brd.cur_piece_move_opts:
                            _enact_move_piece(_brd.selected_tile.piece, the_tile)
                else:
                    _brd.selected_tile = the_tile
                    _brd.cur_piece_move_opts \
                        = _brd.selected_tile.piece.move_opts_func(_brd.selected_tile.piece)

            elif _brd.selected_tile:
                if the_tile in _brd.cur_piece_move_opts: 
                        _enact_move_piece(_brd.selected_tile.piece, the_tile)

#-----------------------------------------------------------------------------
# Drawing functions
#-----------------------------------------------------------------------------

def _render_tiles(s: Surface) -> None:
    s.fill(_brd.BACKGROUND_COLOR)
    for t in _brd.tiles:
        draw.rect(s, t.color, t.rect)
        
#-----------------------------------------------------------------------------

def _render_selections(s: Surface):
    ''' render selection related items such as hovered tile or selected 
    piece '''

    if _brd.hovered_tile:
        draw.rect(s, (208, 240, 192), _brd.hovered_tile.rect, 3)

    if _brd.selected_tile:
        draw.rect(s, (250, 218, 94), _brd.selected_tile.rect, 5)

    PADDING = 10
    
    if _brd.cur_piece_move_opts:
        for opt in _brd.cur_piece_move_opts:
            r = Rect(
                opt.rect.left + PADDING / 2, 
                opt.rect.top + PADDING / 2,
                opt.rect.width - PADDING,
                opt.rect.height - PADDING,
            )
            draw.rect(s, (176, 224, 230), r)

#-----------------------------------------------------------------------------

def _render_pieces(s: Surface):
    for p in _brd.pieces:
        color = None
        if p.side is 1:   color = PieceData.SIDE_1_COLOR
        elif p.side is 2: color = PieceData.SIDE_2_COLOR 
        draw.rect(s, color, p.rect)

#-----------------------------------------------------------------------------

def render(s: Surface, s_size: (int, int)):
    _render_tiles(s)
    _render_selections(s)
    _render_pieces(s)

#-----------------------------------------------------------------------------