''' 
inputter.py - input wrapper (called inputter because input is a builtin name)
author: Keagan Roos
'''

# This may be a little wierd considering that pygame has a similar interface
# already, but the docs reccommend processing the events using 
# pygame.event.get() so as to capture all input events - so this input wrapper
# is set and reset according the main loop of my game so I can be sure I am 
# gathering all the input I possibly can - again, according to the structure
# of my game's loop

import types
import copy 
import pygame

# used for type annotations
Event = type(pygame.event)

#-----------------------------------------------------------------------------

_MOUSE_FALSE  = [False, False, False] # convieniently reset click input

# namespace for storing global variables without using the global keyword and 
# semantics aswell as being able to treat them as one entity when it might be 
# useful

_globals = types.SimpleNamespace(
    mouse_position  = (0, 0)
)

def _set_the_defaults_for_resetables():
    _globals.mouse_up   = copy.copy(_MOUSE_FALSE)
    _globals.mouse_down = copy.copy(_MOUSE_FALSE)
    _globals.mouse      = copy.copy(_MOUSE_FALSE)

_set_the_defaults_for_resetables() # initialize them

#---------------------------------------------------------------------------

# interface funcs... I also feel queasy when I look at this, don't worry.
mouse_pos = lambda        : _globals.mouse_position
mouse_up  = lambda button : _globals.mouse_up[button]

#-----------------------------------------------------------------------------

def _handle_mouse_input(e: Event):
    ''' handle all mouse related events '''
    if e.type == pygame.MOUSEMOTION:
        _globals.mouse_position = e.pos

    elif e.type == pygame.MOUSEBUTTONUP: 
        _globals.mouse_up[e.button] = True

#-----------------------------------------------------------------------------

def _is_mouse_event(e: Event):
    ''' return true is e.type is one of the three mouse events '''
    return e.type == pygame.MOUSEMOTION or e.type == pygame.MOUSEBUTTONDOWN \
        or e.type == pygame.MOUSEBUTTONUP

#-----------------------------------------------------------------------------

def handle_event(e: Event):
    ''' handle the specified event '''
    # TODO(Keagan): Right now this solution is sub par, but at least for
    # now, we stop trying to handle events after an event has been handled
    if _is_mouse_event(e): 
        _handle_mouse_input(e)

#-----------------------------------------------------------------------------

# client code interface alias
def reset_input(): 
    _set_the_defaults_for_resetables()
