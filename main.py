''' 
main.py - main module for game - run this to run the game
author: Keagan Roos
'''

import sys

import pygame
from pygame.locals import *

import inputter
from coords import *
import board

#------------------------------------------------------------------------------

def process_events():
    ''' process events such as input '''
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        inputter.handle_event(e)
            
#------------------------------------------------------------------------------

def initialize(surface, size):
    ''' initializes our game's data and modules '''
    board.initialize(surface, size)
    
#------------------------------------------------------------------------------

def update():
    ''' Update internal logic of the game '''

    board.update()
    
#------------------------------------------------------------------------------

def render(s, s_size):
    ''' do drawing after update '''
    s.fill((50, 50, 50))
    board.render(s, s_size)
    pygame.display.flip()

#------------------------------------------------------------------------------

def end_frame():
    ''' do any cleaning up after the frame has been updated and rendered '''
    inputter.reset_input()

#------------------------------------------------------------------------------

def main():
    ''' main entry point for game '''
    pygame.init()

    size = width, height = 760, 760
    screen = pygame.display.set_mode(size)
    background_col = (50, 50, 50)
    initialize(screen, size)
    while not not 1:
        # These are the procedures that are to happen every frame. The main
        # loop follows a pattern of processing events, updating game data/
        # logic, rendering based on that logic and then cleaning up to be 
        # ready for the next frame
        
        process_events()        # gather input
        update()                # process logic
        render(screen, size)    # draw stuff
        end_frame()             # get ready for next frame

    

if __name__ == '__main__':
    main()
