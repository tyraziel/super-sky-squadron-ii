import pygame
import argparse

#Import of Key Constants to make evaluation a bit easier
from pygame.locals import (
    K_ESCAPE, K_F1, K_F2, K_F3, K_F4, K_F5, K_F6, K_F7, K_F8, K_F9, K_F10, K_F11, K_F12,
    K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_9, K_0, K_MINUS, K_PLUS,
    K_w, K_a, K_s, K_d,
    K_UP, K_DOWN, K_LEFT, K_RIGHT,
    KEYDOWN, KEYUP, QUIT
)

#Argument parsing to make running the game in different modes slightly easier
argument_parser = argparse.ArgumentParser(description="CodeMash 2025 Divez - So you want to be a video game developer?")

argument_parser.add_argument("--debug", help="Enter Debug Mode", action="store_true", dest="debug")
argument_parser.add_argument("--debug-to-console", help="Debug to Console only (does not need to be used in conjunction with --debug, does not debug events)", action="store_true", dest="debug_to_console")
argument_parser.add_argument("--debug-events", help="Debug Events to Console (does not need --debug or --debug-to-console)", action="store_true", dest="debug_events")
argument_parser.add_argument("--mute-audio", help="Mute all Sounds", action="store_true", dest="mute_audio")
argument_parser.add_argument("--no-frame", help="Remove any windowing system framing", action="store_true", dest="no_frame")
argument_parser.add_argument("--full-screen", help="Go Full Screen Mode", action="store_true", dest="full_screen")
argument_parser.add_argument("--double-buffer", help="Enable Double Buffering", action="store_true", dest="double_buffer")

######################################################################
# PARSE GAME CLI ARGUMENTS
######################################################################
GAME_CLI_ARGUMENTS = argument_parser.parse_args()

######################################################################
# SET GAME DEFAULTS
######################################################################

#Game State is generally held within this dictionary
#These are 'indexed' by GAME_STATE['KEY']
GAME_STATE = {'DEBUG': False, 'DEBUG_TO_CONSOLE': False, 'DEBUG_EVENTS': False, 'DEV_MODE': False,
              'RUNNING': True, 'GAME_OVER': False,
              } 
            #   'main_game': False, 'title_screen': False, 'mission_screen': False, 'high_score_screen': False,
            #   'transition_to_game_from_mission': False, 'transition_to_game_from_mission_ttl': TRANSITION_TO_GAME_TTL,
            #   'transition_to_mission_from_title': False, 'transition_to_mission_from_title_ttl': TRANSITION_TO_MISSION_TTL,
            #   'transition_to_high_score_from_game': False, 'transition_to_high_score_from_game_ttl': TRANSITION_TO_HIGH_SCORE_TTL,
            #   'transition_to_title_from_high_score': False, 'transition_to_title_from_high_score_ttl': TRANSITION_TO_TITLE_TTL,

#Game Constants are generally held within this dictionary
#These are 'indexed' by GAME_CONSTANTS['KEY']
GAME_CONSTANTS = {'SCREEN_WIDTH': 1280, 'SCREEN_HEIGHT': 720, 'SCREEN_FLAGS': 0}

#Time to live defaults are within this dictionary
TTL_DEFAULTS = {}

#We create a separate dictionary for the game keys so we can do stuff according to the state of the keys
#'indexed' by game_keys['key']
GAME_KEYS = {'up': False, 'down' : False, 'left': False, 'right': False, 'space': False, 'advance': False, 'backspace': False}

######################################################################
# SETUP THE DISPLAY
######################################################################
GAME_CONSTANTS['PYGAME_SCREEN_FLAGS'] = 0 #|pygame.NOFRAME|pygame.RESIZABLE

if(GAME_CLI_ARGUMENTS.full_screen):
  GAME_CONSTANTS['PYGAME_SCREEN_FLAGS'] = GAME_CONSTANTS['PYGAME_SCREEN_FLAGS'] | pygame.FULLSCREEN
  print(f"Full Screen Mode")

if(GAME_CLI_ARGUMENTS.no_frame):
  GAME_CONSTANTS['PYGAME_SCREEN_FLAGS'] = GAME_CONSTANTS['PYGAME_SCREEN_FLAGS'] | pygame.NOFRAME
  print(f"Removing Window Frames")

if(GAME_CLI_ARGUMENTS.double_buffer):
  GAME_CONSTANTS['PYGAME_SCREEN_FLAGS'] = GAME_CONSTANTS['PYGAME_SCREEN_FLAGS'] | pygame.DOUBLEBUF
  print(f"Setting Double Buffering")

pygame.display.set_caption("CodeMash 2025 Divez - So you want to be a video game developer?")
THE_SCREEN = pygame.display.set_mode((GAME_CONSTANTS['SCREEN_WIDTH'], GAME_CONSTANTS['SCREEN_HEIGHT']), GAME_CONSTANTS['PYGAME_SCREEN_FLAGS'])
print(f"{pygame.display.get_driver()}")
print(f"{pygame.display.Info()}")


#screen.fill((r,g,b))

######################################################################
# ESTABLISH THE GAME CLOCK
#
# The game clock and ELAPSED_MS will be used for most, if not all
# our calculations for how all elements are to progress in the game.
# At the end of our game loop, we have the game clock tick near 60fps
# as best as the hardware we're running off of can go.
######################################################################
GAME_CLOCK = pygame.time.Clock()
ELAPSED_MS = GAME_CLOCK.tick()
ELAPSED_S = ELAPSED_MS / 1000.0

######################################################################
# MAIN GAME LOOP
######################################################################
while GAME_STATE['RUNNING']:

  ####################################################################
  # HANDLE EVENTS
  ####################################################################
  for the_event in pygame.event.get():
    if GAME_STATE['DEBUG_EVENTS']:
      print(the_event)
    if the_event.type == QUIT:  #If we have evaluated that QUIT has happened as an event, then we need to state that the GAME_STATE of running is now False
      GAME_STATE['RUNNING'] = False

    ##################################################################
    # HANDLE USER I/O
    ##################################################################



  ####################################################################
  # FINAL UPDATES FOR OUR GAME LOOP
  ####################################################################
  if(GAME_CLI_ARGUMENTS.double_buffer):
    pygame.display.flip() #Updates the whole screen, with double buffering, we want to use flip
  else:
    pygame.display.update() #show the updates
  
  ELAPSED_MS = GAME_CLOCK.tick(60)
  ELAPSED_S = ELAPSED_MS / 1000.0

pygame.quit()