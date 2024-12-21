############################################################################################################################################
# https://kenney.itch.io/ship-mixer
#
# Transporter-5
# MDowOjAvMTA6MDowLzM6MDowLzk6MDowLzA6MDowL3wwOjEzLzE6MTMvMjoxMy8zOjAvNDo1LzU6LTEv
#############################################################################################################################################
import pygame
import argparse

import xml.etree.ElementTree as element_tree

#Import of Key Constants to make evaluation a bit easier
from pygame.locals import (
    K_ESCAPE, K_F1, K_F2, K_F3, K_F4, K_F5, K_F6, K_F7, K_F8, K_F9, K_F10, K_F11, K_F12,
    K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_9, K_0, K_MINUS, K_PLUS,
    K_w, K_a, K_s, K_d,
    K_UP, K_DOWN, K_LEFT, K_RIGHT,
    K_SPACE, K_LALT, K_RALT,
    KMOD_SHIFT, KMOD_CTRL, KMOD_ALT,
    KEYDOWN, KEYUP, QUIT
)

#Argument parsing to make running the game in different modes slightly easier
argument_parser = argparse.ArgumentParser(description="CodeMash 2025 Divez - So you want to be a video game developer?")

argument_parser.add_argument("--test", "--test-mode", help="Enter Test/Dev Mode (Also turned on with any debug flag)", action="store_true", dest="test_mode")
argument_parser.add_argument("--debug", help="Enter Debug Mode", action="store_true", dest="debug")
argument_parser.add_argument("--debug-grid", help="Show Debug Grid", action="store_true", dest="debug_grid")
argument_parser.add_argument("--debug-to-console", help="Debug to Console only (does not need to be used in conjunction with --debug, does not debug events)", action="store_true", dest="debug_to_console")
argument_parser.add_argument("--debug-events", help="Debug Events to Console (does not need --debug or --debug-to-console)", action="store_true", dest="debug_events")
argument_parser.add_argument("--debug-events-verbose", help="Debug All Events with its Data to Console (does not need --debug or --debug-to-console or --debug-events)", action="store_true", dest="debug_events_verbose")
argument_parser.add_argument("--mute-audio", help="Mute all Sounds", action="store_true", dest="mute_audio")
argument_parser.add_argument("--no-frame", help="Remove any windowing system framing", action="store_true", dest="no_frame")
argument_parser.add_argument("--full-screen", help="Go Full Screen Mode", action="store_true", dest="full_screen")
argument_parser.add_argument("--double-buffer", help="Enable Double Buffering", action="store_true", dest="double_buffer")
argument_parser.add_argument("--disable-joystick", help="Disable Joystick Activity", action="store_true", dest="disable_joystick")

######################################################################
# PARSE GAME CLI ARGUMENTS
######################################################################
GAME_CLI_ARGUMENTS = argument_parser.parse_args()

######################################################################
# SET GAME DEFAULTS
# ***LESSON*** - State Machine
######################################################################


#Game State is generally held within this dictionary
#These are 'indexed' by GAME_STATE['KEY']
GAME_STATE = {'DEBUG': GAME_CLI_ARGUMENTS.debug, 'DEBUG_GRID': GAME_CLI_ARGUMENTS.debug_grid, 'DEBUG_TO_CONSOLE': GAME_CLI_ARGUMENTS.debug_to_console, 'DEBUG_EVENTS': GAME_CLI_ARGUMENTS.debug_events, 'DEBUG_EVENTS_VERBOSE': GAME_CLI_ARGUMENTS.debug_events_verbose, 
              'TEST_MODE': GAME_CLI_ARGUMENTS.test_mode or GAME_CLI_ARGUMENTS.debug or GAME_CLI_ARGUMENTS.debug_grid or GAME_CLI_ARGUMENTS.debug_to_console or GAME_CLI_ARGUMENTS.debug_events or GAME_CLI_ARGUMENTS.debug_events_verbose,
              'LAYER_1': True, 'LAYER_2': True, 'LAYER_3': True, 'LAYER_4': True,
              'RUNNING': True, 'GAME_OVER': False, 'PAUSED': False, 
             } 

#Game Constants are generally held within this dictionary
#These are 'indexed' by GAME_CONSTANTS['KEY']
######################################################################
# ***LESSON*** - SCREEN COORDINATES
######################################################################
GAME_CONSTANTS = {'SCREEN_WIDTH': 1280, 'SCREEN_HEIGHT': 720, 'SCREEN_FLAGS': 0, 'SQUARE_SIZE': 32}

####### Generate the Debug Grid in a clever way
GAME_CONSTANTS['DEBUG_GRID'] = []
for width in range(0,int(GAME_CONSTANTS['SCREEN_WIDTH']/GAME_CONSTANTS['SQUARE_SIZE'])):
  GAME_CONSTANTS['DEBUG_GRID'].append([width * GAME_CONSTANTS['SQUARE_SIZE'], 0])
  GAME_CONSTANTS['DEBUG_GRID'].append([width * GAME_CONSTANTS['SQUARE_SIZE'], GAME_CONSTANTS['SCREEN_HEIGHT']])
  GAME_CONSTANTS['DEBUG_GRID'].append([(width+1) * GAME_CONSTANTS['SQUARE_SIZE'], GAME_CONSTANTS['SCREEN_HEIGHT']])
  GAME_CONSTANTS['DEBUG_GRID'].append([(width+1) * GAME_CONSTANTS['SQUARE_SIZE'], 0])
  GAME_CONSTANTS['DEBUG_GRID'].append([(width+2) * GAME_CONSTANTS['SQUARE_SIZE'], 0])
for height in range(0,int(GAME_CONSTANTS['SCREEN_HEIGHT']/GAME_CONSTANTS['SQUARE_SIZE'])):
  GAME_CONSTANTS['DEBUG_GRID'].append([0, height * GAME_CONSTANTS['SQUARE_SIZE']])
  GAME_CONSTANTS['DEBUG_GRID'].append([GAME_CONSTANTS['SCREEN_WIDTH'], height * GAME_CONSTANTS['SQUARE_SIZE']])
  GAME_CONSTANTS['DEBUG_GRID'].append([GAME_CONSTANTS['SCREEN_WIDTH'], (height+1) * GAME_CONSTANTS['SQUARE_SIZE']])
  GAME_CONSTANTS['DEBUG_GRID'].append([0, (height+1) * GAME_CONSTANTS['SQUARE_SIZE']])
  GAME_CONSTANTS['DEBUG_GRID'].append([0, (height+2) * GAME_CONSTANTS['SQUARE_SIZE']])

#Primiative Colors are held within this dictionary
#These are 'indexed' by GAME_COLORS['KEY']
GAME_COLORS = {'DEEP_PURPLE': (58, 46, 63),
               'BLACK': (0, 0, 0),
               'NOT_QUITE_BLACK': (31, 36, 38),
               'RED': (255, 0, 0),
               'GREEN': (0, 255, 0),
               'BLUE': (0, 0, 255),
               'ALMOST_BLACK': (29, 25, 35),
               'STEEL_BLUE': (94, 129, 161),
               'SHMUP_BLUE': (51, 153, 218)
               }

#Time to live defaults are within this dictionary
# ***LESSON***
TTL_DEFAULTS = {}

######################################################################
# INITIALIZE PYGAME AND OTHER ELEMENTS FOR THE GAME
######################################################################
if GAME_CLI_ARGUMENTS.debug_to_console:
  print(f"[INIT] Initializing Pygame")
pygame.init()
if GAME_CLI_ARGUMENTS.debug_to_console:
  print(f"[INIT] Complete!")

#We create a separate dictionary for the game controls so we can do stuff according to the state of the controls
#'indexed' by GAME_CONTROLS['key']
GAME_CONTROLS = {'UP': False, 'LEFT': False, 'DOWN' : False, 'RIGHT': False,
                 'GREEN': False, 'BLUE': False, 'RED': False, 'YELLOW': False,
                 'w': False, 'a': False, 's': False, 'd': False,
                 'up_arrow': False, 'left_arrow': False, 'down_arrow': False, 'right_arrow': False,
                 'hat_up': False, 'hat_left': False, 'hat_down': False, 'hat_right': False,
                 'dpad_up': False, 'dpad_left': False, 'dpad_down': False, 'dpad_right': False,
                 'axis_0': 0.0, 'axis_1': 0.0, 'axis_2': 0.0, 'axis_3': 0.0, 'axis_4': 0.0, 'axis_5': 0.0,
                 'space_bar': False, 'left_alt': False, 'right_alt': False,
                 'controller_a': False, 'controller_b': False, 'controller_x': False, 'controller_y': False,
                 'controller_lb': False, 'controller_rb': False, 'controller_back': False, 'controller_start': False,
                }

#For joystick controllers
JOYSTICKS = {}

#Load our Fonts
if GAME_CLI_ARGUMENTS.debug_to_console:
  print(f"[INIT] [FONTS] Loading")

######################################################################
# LOAD IMAGES AND IMAGE SHEETS
# Game fonts are held within this dictionary
# These are 'indexed' by GAME_FONTS['KEY']
######################################################################

GAME_FONTS = {'KENNEY_MINI_16': pygame.font.Font('./fonts/Kenney Mini.ttf', 16),
              'KENNEY_MINI_32': pygame.font.Font('./fonts/Kenney Mini.ttf', 32),
              'KENNEY_MINI_SQUARE_16': pygame.font.Font('./fonts/Kenney Mini Square.ttf', 16),
              'KENNEY_MINI_SQUARE_32': pygame.font.Font('./fonts/Kenney Mini Square.ttf', 32),
              'KENNEY_PIXEL_16': pygame.font.Font('./fonts/Kenney Pixel.ttf', 16),
              'KENNEY_PIXEL_SQUARE_16': pygame.font.Font('./fonts/Kenney Pixel Square.ttf', 16),
              'KENNEY_BLOCKS_16': pygame.font.Font('./fonts/Kenney Blocks.ttf', 16),
              'KENNEY_FUTURE_16': pygame.font.Font('./fonts/Kenney Future.ttf', 16),
              'KENNEY_FUTURE_NARROW_16': pygame.font.Font('./fonts/Kenney Future Narrow.ttf', 16)
             }

if GAME_CLI_ARGUMENTS.debug_to_console:
  print(f"[INIT] [FONTS] Completed")

######################################################################
# LOAD IMAGES AND IMAGE SHEETS AND CONVERT TO GAME SURFACES
#
# **** LESSON ****
#
# After the full sheet is loaded we are then going to pull out the parts of the spritesheet (subsurface) that we want and we're making them twice as large (scale)
# GAME_SURFACES['INPUT_PROMPTS']['W_WHITE'] = pygame.transform.scale(GAME_SURFACES['INPUT_PROMPTS']['FULL_SHEET'].subsurface(pygame.Rect(18*16, 2*16, 16, 16)), (32, 32)) #18,2
# GAME_SURFACES['INPUT_PROMPTS']['W_GRAY'] = pygame.transform.scale(GAME_SURFACES['INPUT_PROMPTS']['FULL_SHEET'].subsurface(pygame.Rect(18*16, 10*16, 16, 16)), (32, 32)) #18,10
# GAME_SURFACES['INPUT_PROMPTS']['A_WHITE'] = pygame.transform.scale(GAME_SURFACES['INPUT_PROMPTS']['FULL_SHEET'].subsurface(pygame.Rect(18*16, 3*16, 16, 16)), (32, 32)) #18,3
# GAME_SURFACES['INPUT_PROMPTS']['A_GRAY'] = pygame.transform.scale(GAME_SURFACES['INPUT_PROMPTS']['FULL_SHEET'].subsurface(pygame.Rect(18*16, 11*16, 16, 16)), (32, 32)) #18,11
# GAME_SURFACES['INPUT_PROMPTS']['S_WHITE'] = pygame.transform.scale(GAME_SURFACES['INPUT_PROMPTS']['FULL_SHEET'].subsurface(pygame.Rect(19*16, 3*16, 16, 16)), (32, 32)) #19,3
# GAME_SURFACES['INPUT_PROMPTS']['S_GRAY'] = pygame.transform.scale(GAME_SURFACES['INPUT_PROMPTS']['FULL_SHEET'].subsurface(pygame.Rect(19*16, 11*16, 16, 16)), (32, 32)) #19,11
# GAME_SURFACES['INPUT_PROMPTS']['D_WHITE'] = pygame.transform.scale(GAME_SURFACES['INPUT_PROMPTS']['FULL_SHEET'].subsurface(pygame.Rect(20*16, 3*16, 16, 16)), (32, 32)) #20,3
# GAME_SURFACES['INPUT_PROMPTS']['D_GRAY'] = pygame.transform.scale(GAME_SURFACES['INPUT_PROMPTS']['FULL_SHEET'].subsurface(pygame.Rect(20*16, 11*16, 16, 16)), (32, 32)) #20,11
# GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_A_GRAY'] = pygame.transform.scale(GAME_SURFACES['INPUT_PROMPTS']['FULL_SHEET'].subsurface(pygame.Rect(13*16, 1*16, 16, 16)), (32, 32)) #13, 1
# GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_B_GRAY'] = pygame.transform.scale(GAME_SURFACES['INPUT_PROMPTS']['FULL_SHEET'].subsurface(pygame.Rect(14*16, 1*16, 16, 16)), (32, 32)) #14, 1
# GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_X_GRAY'] = pygame.transform.scale(GAME_SURFACES['INPUT_PROMPTS']['FULL_SHEET'].subsurface(pygame.Rect(15*16, 1*16, 16, 16)), (32, 32)) #15, 1
# GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_Y_GRAY'] = pygame.transform.scale(GAME_SURFACES['INPUT_PROMPTS']['FULL_SHEET'].subsurface(pygame.Rect(16*16, 1*16, 16, 16)), (32, 32)) #16, 1
# GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_A_COLOR'] = pygame.transform.scale(GAME_SURFACES['INPUT_PROMPTS']['FULL_SHEET'].subsurface(pygame.Rect(4*16, 0*16, 16, 16)), (32, 32)) #4, 0
# GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_B_COLOR'] = pygame.transform.scale(GAME_SURFACES['INPUT_PROMPTS']['FULL_SHEET'].subsurface(pygame.Rect(5*16, 0*16, 16, 16)), (32, 32)) #5, 0
# GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_X_COLOR'] = pygame.transform.scale(GAME_SURFACES['INPUT_PROMPTS']['FULL_SHEET'].subsurface(pygame.Rect(6*16, 0*16, 16, 16)), (32, 32)) #6, 0
# GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_Y_COLOR'] = pygame.transform.scale(GAME_SURFACES['INPUT_PROMPTS']['FULL_SHEET'].subsurface(pygame.Rect(7*16, 0*16, 16, 16)), (32, 32)) #7, 0
# GAME_SURFACES['INPUT_PROMPTS']['JOY_AXIS_DIRECTIONAL'] = pygame.transform.scale(GAME_SURFACES['INPUT_PROMPTS']['FULL_SHEET'].subsurface(pygame.Rect(0*16, 20*16, 16, 16)), (32, 32)) #0, 20
# GAME_SURFACES['INPUT_PROMPTS']['JOY_AXIS_BASE'] = pygame.transform.scale(GAME_SURFACES['INPUT_PROMPTS']['FULL_SHEET'].subsurface(pygame.Rect(28*16, 20*16, 16, 16)), (32, 32)) #28, 20
# GAME_SURFACES['INPUT_PROMPTS']['JOY_DPAD_BASE'] = pygame.transform.scale(GAME_SURFACES['INPUT_PROMPTS']['FULL_SHEET'].subsurface(pygame.Rect(28*16, 21*16, 16, 16)), (32, 32)) #28, 21
######################################################################
GAME_SURFACES = {}

if GAME_CLI_ARGUMENTS.debug_to_console:
  print(f"[INIT] [TEXTURE] Loading")

if GAME_CLI_ARGUMENTS.debug_to_console:
  print(f"[INIT] [TEXTURE-LOAD] [FULL-SHEET]: input-prompts-pixel-16")
GAME_SURFACES['INPUT_PROMPTS'] = {}
GAME_SURFACES['INPUT_PROMPTS']['FULL_SHEET'] = pygame.image.load("./sprites/input-prompts/pixel-16/tilemap_packed.png")

input_prompts_pixel_16_xml_subtextures = element_tree.parse("./sprites/input-prompts/pixel-16/tilemap_sheet.xml").getroot().findall("SubTexture")
for subtexture in input_prompts_pixel_16_xml_subtextures:
  subsurface_name = subtexture.attrib['name'].upper().split(".")[0]
  if GAME_CLI_ARGUMENTS.debug_to_console:
    print(f"[INIT] [TEXTURE-LOAD] [SUBSURFACE]: {subsurface_name}")
  subsurface_x = int(subtexture.attrib['x'])
  subsurface_y = int(subtexture.attrib['y'])
  subsurface_width = int(subtexture.attrib['width'])
  subsurface_height = int(subtexture.attrib['height'])
  # Here we are pulling out the parts of the spritesheet that we want and we're making them twice as large
  GAME_SURFACES['INPUT_PROMPTS'][subsurface_name] = pygame.transform.scale(GAME_SURFACES['INPUT_PROMPTS']['FULL_SHEET'].subsurface(pygame.Rect(subsurface_x, subsurface_y, subsurface_width, subsurface_height)), (subsurface_width*2, subsurface_height*2))

if GAME_CLI_ARGUMENTS.debug_to_console:
  print(f"[INIT] [TEXTURE-LOAD] [FULL-SHEET]: space-shooter-redux")

GAME_SURFACES['SPACE_SHOOTER_REDUX'] = {}
GAME_SURFACES['SPACE_SHOOTER_REDUX']['FULL_SHEET'] = pygame.image.load("./sprites/space-shooter-redux/sheet.png")

space_shooter_redux_xml_subtextures = element_tree.parse("./sprites/space-shooter-redux/sheet.xml").getroot().findall("SubTexture")
for subtexture in space_shooter_redux_xml_subtextures:
  subsurface_name = subtexture.attrib['name'].upper().split(".")[0]
  if GAME_CLI_ARGUMENTS.debug_to_console:
    print(f"[INIT] [TEXTURE-LOAD] [SUBSURFACE]: {subsurface_name}")
  subsurface_x = int(subtexture.attrib['x'])
  subsurface_y = int(subtexture.attrib['y'])
  subsurface_width = int(subtexture.attrib['width'])
  subsurface_height = int(subtexture.attrib['height'])
  GAME_SURFACES['SPACE_SHOOTER_REDUX'][subsurface_name] = GAME_SURFACES['SPACE_SHOOTER_REDUX']['FULL_SHEET'].subsurface(pygame.Rect(subsurface_x, subsurface_y, subsurface_width, subsurface_height))
if GAME_CLI_ARGUMENTS.debug_to_console:
  print(f"[INIT] [TEXTURE-LOAD] [FULL-SHEET]: pixel-shmup-tiles")
GAME_SURFACES['PIXEL_SHMUP_TILES'] = {}
GAME_SURFACES['PIXEL_SHMUP_TILES']['FULL_SHEET'] = pygame.image.load("./sprites/pixel-shmup/tiles_packed.png") #192x160

##### CONSIDER REFACTORING THIS INTO A METHOD/FUNCTION IN A SEPARATE FILE
pixel_shmup_tiles_xml_subtextures = element_tree.parse("./sprites/pixel-shmup/tiles_sheet.xml").getroot().findall("SubTexture")
for subtexture in pixel_shmup_tiles_xml_subtextures:
  subsurface_name = subtexture.attrib['name'].upper().split(".")[0]
  if GAME_CLI_ARGUMENTS.debug_to_console:
    print(f"[INIT] [TEXTURE-LOAD] [SUBSURFACE]: {subsurface_name}")
  subsurface_x = int(subtexture.attrib['x'])
  subsurface_y = int(subtexture.attrib['y'])
  subsurface_width = int(subtexture.attrib['width'])
  subsurface_height = int(subtexture.attrib['height'])
  GAME_SURFACES['PIXEL_SHMUP_TILES'][subsurface_name] = GAME_SURFACES['PIXEL_SHMUP_TILES']['FULL_SHEET'].subsurface(pygame.Rect(subsurface_x, subsurface_y, subsurface_width, subsurface_height))

if GAME_CLI_ARGUMENTS.debug_to_console:
  print(f"[INIT] [TEXTURE-LOAD] [FULL-SHEET]: pixel-shmup-ships")
GAME_SURFACES['PIXEL_SHMUP_SHIPS'] = {}
GAME_SURFACES['PIXEL_SHMUP_SHIPS']['FULL_SHEET'] = pygame.image.load("./sprites/pixel-shmup/ships_packed.png") #128x192

pixel_shmup_ships_xml_subtextures = element_tree.parse("./sprites/pixel-shmup/ships_sheet.xml").getroot().findall("SubTexture")
for subtexture in pixel_shmup_ships_xml_subtextures:
  subsurface_name = subtexture.attrib['name'].upper().split(".")[0]
  if GAME_CLI_ARGUMENTS.debug_to_console:
    print(f"[INIT] [TEXTURE-LOAD] [SUBSURFACE]: {subsurface_name}")
  subsurface_x = int(subtexture.attrib['x'])
  subsurface_y = int(subtexture.attrib['y'])
  subsurface_width = int(subtexture.attrib['width'])
  subsurface_height = int(subtexture.attrib['height'])
  GAME_SURFACES['PIXEL_SHMUP_SHIPS'][subsurface_name] = GAME_SURFACES['PIXEL_SHMUP_SHIPS']['FULL_SHEET'].subsurface(pygame.Rect(subsurface_x, subsurface_y, subsurface_width, subsurface_height))

if GAME_CLI_ARGUMENTS.debug_to_console:
  print(f"[INIT] [TEXTURE] Completed")

######################################################################
# SETUP THE DISPLAY
######################################################################
GAME_CONSTANTS['PYGAME_SCREEN_FLAGS'] = 0 #|pygame.NOFRAME|pygame.RESIZABLE

if GAME_CLI_ARGUMENTS.full_screen:
  GAME_CONSTANTS['PYGAME_SCREEN_FLAGS'] = GAME_CONSTANTS['PYGAME_SCREEN_FLAGS'] | pygame.FULLSCREEN
  print(f"[CLI] Full Screen Mode")

if GAME_CLI_ARGUMENTS.no_frame:
  GAME_CONSTANTS['PYGAME_SCREEN_FLAGS'] = GAME_CONSTANTS['PYGAME_SCREEN_FLAGS'] | pygame.NOFRAME
  print(f"[CLI] Removing Window Frames")

if GAME_CLI_ARGUMENTS.double_buffer:
  GAME_CONSTANTS['PYGAME_SCREEN_FLAGS'] = GAME_CONSTANTS['PYGAME_SCREEN_FLAGS'] | pygame.DOUBLEBUF
  print(f"[CLI] Setting Double Buffering")

pygame.display.set_caption("CodeMash 2025 Divez - So you want to be a video game developer?")

# Create the main screen object
THE_SCREEN = pygame.display.set_mode((GAME_CONSTANTS['SCREEN_WIDTH'], GAME_CONSTANTS['SCREEN_HEIGHT']), GAME_CONSTANTS['PYGAME_SCREEN_FLAGS'])
THE_SCREEN.fill(GAME_COLORS['DEEP_PURPLE'])
pygame.display.update()

print(f"PyGame Driver:  {pygame.display.get_driver()}")
print(f"PyGame Display Info:\n{pygame.display.Info()}")

CAMERA = {'X': 0, 'Y': 0}

######################################################################
# ***LESSON*** ESTABLISH THE GAME CLOCK
#
# The game clock and ELAPSED_MS will be used for most, if not all
# our calculations for how all elements are to progress in the game,
# for each frame.
# At the end of our game loop, we have the game clock tick near 60fps
# as best as the hardware we're running off of can go.
######################################################################
GAME_CLOCK = pygame.time.Clock()
ELAPSED_MS = GAME_CLOCK.tick()
ELAPSED_S = ELAPSED_MS / 1000.0

######################################################################
# MAIN GAME LOOP
# ***LESSON*** ***GAME LOOP***
######################################################################
while GAME_STATE['RUNNING']:
  ####################################################################
  # RESET THE SCREEN COLOR
  #
  # ***LESSON***
  # For the screen to be "wiped clean" so we can start fresh.  This
  # fill operation needs to take place.
  ####################################################################
  THE_SCREEN.fill(GAME_COLORS['DEEP_PURPLE'])

  ####################################################################
  # HANDLE EVENTS
  #
  # ***LESSON***
  # We need to handle user I/O as that's the main way the player
  # interacts with the game.  Every button press, key press or 
  # direction movement that we care about needs to be evaluated for
  # the game engine to take the appropriate action that we define.
  ####################################################################
  for the_event in pygame.event.get():
    if GAME_STATE['DEBUG_EVENTS_VERBOSE']:
      print(f"[EVENT-VERBOSE] {the_event}")
    if the_event.type == QUIT:  #If we have evaluated that QUIT has happened as an event, then we need to state that the GAME_STATE of running is now False
      GAME_STATE['RUNNING'] = False
      if GAME_STATE['DEBUG_EVENTS']:
        print("[EVENT] [QUIT]")

    ##################################################################
    # HANDLE USER I/O (KEYBOARD)
    ##################################################################
    if the_event.type == KEYDOWN:
      if GAME_STATE['DEBUG_EVENTS']:
        print(f"[EVENT] [KEYBOARD] [KEYDOWN] {the_event.key}")
    
      # The game wil exit / quit if someone hits the SHFIT+ESCAPE key sequence
      if the_event.key == K_ESCAPE and (the_event.mod & KMOD_SHIFT):
        GAME_STATE['RUNNING'] = False

      if the_event.key == K_UP:
        GAME_CONTROLS['up_arrow'] = True
      if the_event.key == K_LEFT:
        GAME_CONTROLS['left_arrow'] = True
      if the_event.key == K_DOWN:
        GAME_CONTROLS['down_arrow'] = True
      if the_event.key == K_RIGHT:
        GAME_CONTROLS['right_arrow'] = True

      if the_event.key == K_w:
        GAME_CONTROLS['w'] = True
      if the_event.key == K_a:
        GAME_CONTROLS['a'] = True
      if the_event.key == K_s:
        GAME_CONTROLS['s'] = True
      if the_event.key == K_d:
        GAME_CONTROLS['d'] = True

      if the_event.key == K_SPACE:
        GAME_CONTROLS['space_bar'] = True
      if the_event.key == K_LALT:
        GAME_CONTROLS['left_alt'] = True
      if the_event.key == K_RALT:
        GAME_CONTROLS['right_alt'] = True

      #If we are in TEST_MODE a bunch of additional keys not generally available are now activated for us to manage the
      #game to test various things out.  Helpful if we need to test a level and we don't want to have to play through
      #the game to get there (or even test out powerups / score / other things / and final boss battles!)
      #
      #Enter test mode by hitting the SHIFT+F12 key sequence
      if GAME_STATE['TEST_MODE']:
        if the_event.key == K_1 and (the_event.mod & KMOD_SHIFT):
          GAME_STATE['LAYER_1'] = not GAME_STATE['LAYER_1']
        if the_event.key == K_2 and (the_event.mod & KMOD_SHIFT):
          GAME_STATE['LAYER_2'] = not GAME_STATE['LAYER_2']
        if the_event.key == K_3 and (the_event.mod & KMOD_SHIFT):
          GAME_STATE['LAYER_3'] = not GAME_STATE['LAYER_3']
        if the_event.key == K_4 and (the_event.mod & KMOD_SHIFT):
          GAME_STATE['LAYER_4'] = not GAME_STATE['LAYER_4']

        if the_event.key == K_F8:
          print(f"[TEST-MODE] [DEBUG-GRID] MODE TOGGLED TO {(str(not GAME_STATE['DEBUG_GRID'])).upper()}")
          GAME_STATE['DEBUG_GRID'] = not GAME_STATE['DEBUG_GRID']
        if the_event.key == K_F9:
          print(f"[TEST-MODE] [DEBUG-TO-CONSOLE] MODE TOGGLED TO {(str(not GAME_STATE['DEBUG_TO_CONSOLE'])).upper()}")
          GAME_STATE['DEBUG_TO_CONSOLE'] = not GAME_STATE['DEBUG_TO_CONSOLE']
        if the_event.key == K_F10:
          print(f"[TEST-MODE] [DEBUG-EVENTS] MODE TOGGLED TO {(str(not GAME_STATE['DEBUG_EVENTS'])).upper()}")
          GAME_STATE['DEBUG_EVENTS'] = not GAME_STATE['DEBUG_EVENTS']
        if the_event.key == K_F11:
          print(f"[TEST-MODE] [DEBUG-EVENTS-VERBOSE] MODE TOGGLED TO {(str(not GAME_STATE['DEBUG_EVENTS_VERBOSE'])).upper()}")
          GAME_STATE['DEBUG_EVENTS_VERBOSE'] = not GAME_STATE['DEBUG_EVENTS_VERBOSE']
        if the_event.key == K_F12 and not (the_event.mod & KMOD_SHIFT):
          print(f"[TEST-MODE] [DEBUG] MODE TOGGLED TO {(str(not GAME_STATE['DEBUG'])).upper()}")
          GAME_STATE['DEBUG'] = not GAME_STATE['DEBUG']
        if the_event.key == K_F12 and (the_event.mod & KMOD_SHIFT):
          print(f"[TEST-MODE] DEACTIVATED")
          print(f"[TEST-MODE] [DEBUG] DEACTIVATED")
          print(f"[TEST-MODE] [DEBUG-GRID] DEACTIVATED")
          print(f"[TEST-MODE] [DEBUG-TO-CONSOLE] DEACTIVATED")
          print(f"[TEST-MODE] [DEBUG-EVENTS] DEACTIVATED")
          print(f"[TEST-MODE] [DEBUG-EVENTS-VERBOSE] DEACTIVATED")
          GAME_STATE['TEST_MODE'] = False
          GAME_STATE['DEBUG'] = False
          #GAME_STATE['DEBUG_GRID'] = False
          GAME_STATE['DEBUG_TO_CONSOLE'] = False
          GAME_STATE['DEBUG_EVENTS'] = False
          GAME_STATE['DEBUG_EVENTS_VERBOSE'] = False

          #Turn back on all the layers
          GAME_STATE['LAYER_1'] = True
          GAME_STATE['LAYER_2'] = True
          GAME_STATE['LAYER_3'] = True
          GAME_STATE['LAYER_4'] = True
      else:
        if the_event.key == K_F12 and (the_event.mod & KMOD_SHIFT):
          print(f"[TEST-MODE] ACTIVATED")
          print(f"[TEST-MODE] [DEBUG] ACTIVATED")
          print(f"[TEST-MODE] [DEBUG-GRID] ACTIVATED")
          GAME_STATE['TEST_MODE'] = True
          GAME_STATE['DEBUG'] = True
          #GAME_STATE['DEBUG_GRID'] = True

    if the_event.type == KEYUP:
      if GAME_STATE['DEBUG_EVENTS']:
        print(f"[EVENT] [KEYBOARD] [KEYUP] {the_event.key}")

      if the_event.key == K_UP:
        GAME_CONTROLS['up_arrow'] = False
      if the_event.key == K_LEFT:
        GAME_CONTROLS['left_arrow'] = False
      if the_event.key == K_DOWN:
        GAME_CONTROLS['down_arrow'] = False
      if the_event.key == K_RIGHT:
        GAME_CONTROLS['right_arrow'] = False

      if the_event.key == K_w:
        GAME_CONTROLS['w'] = False
      if the_event.key == K_a:
        GAME_CONTROLS['a'] = False
      if the_event.key == K_s:
        GAME_CONTROLS['s'] = False
      if the_event.key == K_d:
        GAME_CONTROLS['d'] = False

      if the_event.key == K_SPACE:
        GAME_CONTROLS['space_bar'] = False
      if the_event.key == K_LALT:
        GAME_CONTROLS['left_alt'] = False
      if the_event.key == K_RALT:
        GAME_CONTROLS['right_alt'] = False

    ##################################################################
    # HANDLE USER I/O (JOYSTICK)
    # 
    # ***LESSON*** 
    #
    # https://www.pygame.org/docs/ref/joystick.html
    # Xbox 360 Controller - a =0, b=1, x=2, y=3, lb=4, rb=5, back=6, start=7, xbox=10, leftaxis=8, rightaxis=9
    #                axis - axis-4 is left trigger, axis-5 is right trigger (-1 -> 1 [fully pressed])
    #                       0 - is left/right on the left axis, 1 is up/down on the left axis (minus is up and left, positive is down and right from 1.0 <-> -1.0)
    #                       2 - is left/right on the right axis, 3 is up/down on the right axis
    #                hat  - (0,0) - center, (0,1) - up, (0,-1) - down, (1,0) - right, (-1,0) - left
    # PowerA NSW Wired Controller - a=0 , b=1 , x=2 , y=3 , dpad-up=11, dpad-down=12, dpad-left=13, dpad-right=14, 
    #                               square/circle=15, home=5, minus=4, plus=6, L=9, R=10, leftaxis=7, rightaxis=8 
    #                             - ZL=Axis-4, ZR=Axis-5, leftaxis-left/right=0, leftaxis-up/down=1, rightaxis-left/right=2, rightaxis-up/down=3
    #                             - up=negative1, down=positive1, left=negative1, right=positive1
    #                             - ZL=pressed=-1.0,released=0.9999969482421875
    ##################################################################
    
    # Handle hotplugging
    if not GAME_CLI_ARGUMENTS.disable_joystick and the_event.type == pygame.JOYDEVICEADDED:
      # This event will be generated when the program starts for every
      # joystick, filling up the list without needing to create them manually.
      joystick = pygame.joystick.Joystick(the_event.device_index)
      JOYSTICKS[joystick.get_instance_id()] = joystick
      if GAME_STATE['DEBUG_EVENTS']:
        print(f"[EVENT] [JOYSTICK] [CONNECT] ID:{joystick.get_instance_id()} - {joystick} - {joystick.get_name()}")

    if not GAME_CLI_ARGUMENTS.disable_joystick and the_event.type == pygame.JOYDEVICEREMOVED:
      del JOYSTICKS[the_event.instance_id]
      if GAME_STATE['DEBUG_EVENTS']:
        print(f"[EVENT] [JOYSTICK] [DISCONNECT] ID:{the_event.instance_id}")

    if the_event.type == pygame.JOYBUTTONDOWN:
      if GAME_STATE['DEBUG_EVENTS']:
        print(f"[EVENT] [JOYSTICK] [BUTTONDOWN] {the_event.button}")

      if JOYSTICKS[the_event.instance_id].get_name() == 'Xbox 360 Controller' or JOYSTICKS[the_event.instance_id].get_name() == 'PowerA NSW Wired controller':
        if the_event.button == 0:
          GAME_CONTROLS['controller_a'] = True
        if the_event.button == 1:
          GAME_CONTROLS['controller_b'] = True
        if the_event.button == 2:
          GAME_CONTROLS['controller_x'] = True
        if the_event.button == 3:
          GAME_CONTROLS['controller_y'] = True

      if JOYSTICKS[the_event.instance_id].get_name() == 'PowerA NSW Wired controller':
        if the_event.button == 11:
          GAME_CONTROLS['dpad_up'] = True
        if the_event.button == 12:
          GAME_CONTROLS['dpad_down'] = True
        if the_event.button == 13:
          GAME_CONTROLS['dpad_left'] = True
        if the_event.button == 14:
          GAME_CONTROLS['dpad_right'] = True

    if the_event.type == pygame.JOYBUTTONUP:
      if GAME_STATE['DEBUG_EVENTS']:
        print(f"[EVENT] [JOYSTICK] [BUTTONUP] {the_event.button}")

      if JOYSTICKS[the_event.instance_id].get_name() == 'Xbox 360 Controller' or JOYSTICKS[the_event.instance_id].get_name() == 'PowerA NSW Wired controller':
        if the_event.button == 0:
          GAME_CONTROLS['controller_a'] = False
        if the_event.button == 1:
          GAME_CONTROLS['controller_b'] = False
        if the_event.button == 2:
          GAME_CONTROLS['controller_x'] = False
        if the_event.button == 3:
          GAME_CONTROLS['controller_y'] = False

      if JOYSTICKS[the_event.instance_id].get_name() == 'PowerA NSW Wired controller':
        if the_event.button == 11:
          GAME_CONTROLS['dpad_up'] = False
        if the_event.button == 12:
          GAME_CONTROLS['dpad_down'] = False
        if the_event.button == 13:
          GAME_CONTROLS['dpad_left'] = False
        if the_event.button == 14:
          GAME_CONTROLS['dpad_right'] = False

    if the_event.type == pygame.JOYAXISMOTION:
      if GAME_STATE['DEBUG_EVENTS']:
        print(f"[EVENT] [JOYSTICK] [AXISMOTION] {the_event.axis} value {the_event.value}")
      GAME_CONTROLS[f'axis_{the_event.axis}'] = the_event.value

    if the_event.type == pygame.JOYHATMOTION:
      if GAME_STATE['DEBUG_EVENTS']:
        print(f"[EVENT] [JOYSTICK] [HATMOTION] ({the_event.value[0]}, {the_event.value[1]})")

      if the_event.value[0] == 0:
        GAME_CONTROLS['hat_left'] = False
        GAME_CONTROLS['hat_right'] = False
      elif the_event.value[0] == 1:
        GAME_CONTROLS['hat_left'] = False
        GAME_CONTROLS['hat_right'] = True
      elif the_event.value[0] == -1:
        GAME_CONTROLS['hat_left'] = True
        GAME_CONTROLS['hat_right'] = False
      if the_event.value[1] == 0:
        GAME_CONTROLS['hat_up'] = False
        GAME_CONTROLS['hat_down'] = False
      elif the_event.value[1] == 1:
        GAME_CONTROLS['hat_up'] = True
        GAME_CONTROLS['hat_down'] = False
      elif the_event.value[1] == -1:
        GAME_CONTROLS['hat_up'] = False
        GAME_CONTROLS['hat_down'] = True

    ###################################
    #
    # Apply I/O to actual Game Controls
    # Not sure why this won't work when it's pulled out of the i/o loop
    #
    ###################################
    directional_axis_tolleration = 0.50

    GAME_CONTROLS['UP'] = GAME_CONTROLS['w'] or GAME_CONTROLS['up_arrow'] or GAME_CONTROLS['hat_up'] or GAME_CONTROLS['dpad_up'] or GAME_CONTROLS['axis_1'] < -directional_axis_tolleration or GAME_CONTROLS['axis_3'] < -directional_axis_tolleration
    GAME_CONTROLS['LEFT'] = GAME_CONTROLS['a'] or GAME_CONTROLS['left_arrow'] or GAME_CONTROLS['hat_left'] or GAME_CONTROLS['dpad_left'] or GAME_CONTROLS['axis_0'] < -directional_axis_tolleration or GAME_CONTROLS['axis_2'] < -directional_axis_tolleration
    GAME_CONTROLS['DOWN'] = GAME_CONTROLS['s'] or GAME_CONTROLS['down_arrow'] or GAME_CONTROLS['hat_down'] or GAME_CONTROLS['dpad_down'] or GAME_CONTROLS['axis_1'] > directional_axis_tolleration or GAME_CONTROLS['axis_3'] > directional_axis_tolleration
    GAME_CONTROLS['RIGHT'] = GAME_CONTROLS['d'] or GAME_CONTROLS['right_arrow'] or GAME_CONTROLS['hat_right'] or GAME_CONTROLS['dpad_right'] or GAME_CONTROLS['axis_0'] > directional_axis_tolleration or GAME_CONTROLS['axis_2'] > directional_axis_tolleration

    GAME_CONTROLS['GREEN'] = GAME_CONTROLS['space_bar'] or GAME_CONTROLS['controller_a']
    GAME_CONTROLS['RED'] = GAME_CONTROLS['left_alt'] or GAME_CONTROLS['right_alt'] or GAME_CONTROLS['controller_b']
    GAME_CONTROLS['BLUE'] = GAME_CONTROLS['controller_x']
    GAME_CONTROLS['YELLOW'] = GAME_CONTROLS['controller_y']

    ##################################################################
    # WINDOW FOCUS LOSS / GAIN
    #
    # Probably should pause the game on focus loss
    ##################################################################
    if the_event.type == pygame.WINDOWFOCUSLOST:
      if GAME_STATE['DEBUG_EVENTS']:
        print(f"[EVENT] [WINDOW] [FOCUSLOST]")
    
    if the_event.type == pygame.WINDOWFOCUSGAINED:
      if GAME_STATE['DEBUG_EVENTS']:
        print(f"[EVENT] [WINDOW] [FOCUSGAINED]")

  ####################################################################
  # Draw Layer One (The Map Tiles)
  #
  #
  ####################################################################
  if GAME_STATE['LAYER_1']:
    a = 1


  ####################################################################
  # Draw the HUD (Heads Up Display)
  #
  # This is the last (before debug) set of things to add to the
  # screen.  This is here because we want this on top of everything
  # else from the game.
  ####################################################################

  #Top HUD
  pygame.draw.rect(THE_SCREEN, GAME_COLORS['STEEL_BLUE'], pygame.Rect(0,0,1280,32))

  #Mini Map HUD


  #Bottom HUD
  pygame.draw.rect(THE_SCREEN, GAME_COLORS['STEEL_BLUE'], pygame.Rect(0,640,1280,80))
  bottom_hud_test = GAME_FONTS['KENNEY_MINI_SQUARE_32'].render(f"TEST", True, GAME_COLORS['ALMOST_BLACK'])
  THE_SCREEN.blit(bottom_hud_test, bottom_hud_test.get_rect(topleft = (32, 640)))

  bottom_hud_test = GAME_FONTS['KENNEY_MINI_32'].render(f"TEST", True, GAME_COLORS['ALMOST_BLACK'])
  THE_SCREEN.blit(bottom_hud_test, bottom_hud_test.get_rect(topleft = (32, 672)))


  ####################################################################
  # Draw the DEBUG
  #
  # This is last, becasue we want all of this on top of everything
  # else!
  ####################################################################
  if GAME_STATE['DEBUG']:

    debug_x_offset = 0
    debug_y_offset = 80

    #### ***LESSON***
    #### A surface is created when the render method is called from our Font object.  Render takes in text, Anti-aliasing, color.
    #### https://www.pygame.org/docs/ref/font.html#pygame.font.Font.render
    time_passed_ms_text_surface = GAME_FONTS['KENNEY_MINI_16'].render(f"{ELAPSED_MS}ms", True, GAME_COLORS['GREEN'])

    #### ***LESSON*** Blit - What is blitting?  Blit stands for 
    #### Copies the contents of one surface to another.
    #### In our example here, we are copying the contents of time_passed_ms_text_surface to our THE_SCREEN surface.
    #### Effectively this will "paint" time_passed_ms_text_surface on THE_SCREEN in the location we tell it to (and we craete the rect for the surface and use that).
    THE_SCREEN.blit(time_passed_ms_text_surface, time_passed_ms_text_surface.get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - 5 - debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - 5 - debug_y_offset)))

    #Show other "Game Information" that we care about
    #Game Layers
    game_layer_1_text_surface = GAME_FONTS['KENNEY_MINI_16'].render(f"LAYER 1", True, GAME_COLORS['NOT_QUITE_BLACK'])
    if GAME_STATE['LAYER_1']:
      game_layer_1_text_surface = GAME_FONTS['KENNEY_MINI_16'].render(f"LAYER 1", True, GAME_COLORS['GREEN'])
    THE_SCREEN.blit(game_layer_1_text_surface, game_layer_1_text_surface.get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - 320 - debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - 590 - debug_y_offset)))

    game_layer_2_text_surface = GAME_FONTS['KENNEY_MINI_16'].render(f"LAYER 2", True, GAME_COLORS['NOT_QUITE_BLACK'])
    if GAME_STATE['LAYER_2']:
      game_layer_2_text_surface = GAME_FONTS['KENNEY_MINI_16'].render(f"LAYER 2", True, GAME_COLORS['GREEN'])
    THE_SCREEN.blit(game_layer_2_text_surface, game_layer_2_text_surface.get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - 224 - debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - 590 - debug_y_offset)))

    game_layer_3_text_surface = GAME_FONTS['KENNEY_MINI_16'].render(f"LAYER 3", True, GAME_COLORS['NOT_QUITE_BLACK'])
    if GAME_STATE['LAYER_3']:
      game_layer_3_text_surface = GAME_FONTS['KENNEY_MINI_16'].render(f"LAYER 3", True, GAME_COLORS['GREEN'])
    THE_SCREEN.blit(game_layer_3_text_surface, game_layer_3_text_surface.get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - 128 - debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - 590 - debug_y_offset)))

    game_layer_4_text_surface = GAME_FONTS['KENNEY_MINI_16'].render(f"LAYER 4", True, GAME_COLORS['NOT_QUITE_BLACK'])
    if GAME_STATE['LAYER_4']:
      game_layer_4_text_surface = GAME_FONTS['KENNEY_MINI_16'].render(f"LAYER 4", True, GAME_COLORS['GREEN'])
    THE_SCREEN.blit(game_layer_4_text_surface, game_layer_4_text_surface.get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - 32 - debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - 590 - debug_y_offset)))

    #Camera
    camera_text_surface = GAME_FONTS['KENNEY_MINI_16'].render(f"CAMERA X: {CAMERA['X']}", True, GAME_COLORS['GREEN'])
    THE_SCREEN.blit(camera_text_surface, camera_text_surface.get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - 64 - debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - 560 - debug_y_offset)))
    camera_text_surface = GAME_FONTS['KENNEY_MINI_16'].render(f"CAMERA Y: {CAMERA['Y']}", True, GAME_COLORS['GREEN'])
    THE_SCREEN.blit(camera_text_surface, camera_text_surface.get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - 64 - debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - 542 - debug_y_offset)))

    #Show input keys from keyboard
    wasd_debug_x_offset = 152 + debug_x_offset
    wasd_debug_y_offset = 3 + debug_y_offset
    if GAME_CONTROLS['w']:
      THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['W_WHITE'], GAME_SURFACES['INPUT_PROMPTS']['W_WHITE'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - 28 - wasd_debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - 30 - wasd_debug_y_offset)))
    else:
      THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['W_GRAY'], GAME_SURFACES['INPUT_PROMPTS']['W_GRAY'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - 28 - wasd_debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - 30 - wasd_debug_y_offset)))
    if GAME_CONTROLS['a']:
      THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['A_WHITE'], GAME_SURFACES['INPUT_PROMPTS']['A_WHITE'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - 56 - wasd_debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - 0 - wasd_debug_y_offset)))
    else:
      THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['A_GRAY'], GAME_SURFACES['INPUT_PROMPTS']['A_GRAY'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - 56 - wasd_debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - 0 - wasd_debug_y_offset)))
    if GAME_CONTROLS['s']:
      THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['S_WHITE'], GAME_SURFACES['INPUT_PROMPTS']['S_WHITE'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - 28 - wasd_debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - 0 - wasd_debug_y_offset)))
    else:
      THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['S_GRAY'], GAME_SURFACES['INPUT_PROMPTS']['S_GRAY'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - 28 - wasd_debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - 0 - wasd_debug_y_offset)))
    if GAME_CONTROLS['d']:
      THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['D_WHITE'], GAME_SURFACES['INPUT_PROMPTS']['D_WHITE'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - 0 - wasd_debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - 0 - wasd_debug_y_offset)))
    else:
      THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['D_GRAY'], GAME_SURFACES['INPUT_PROMPTS']['D_GRAY'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - 0 - wasd_debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - 0 - wasd_debug_y_offset)))

    arrow_debug_x_offset = 48 + debug_x_offset
    arrow_debug_y_offset = 3 + debug_y_offset
    if GAME_CONTROLS['up_arrow']:
      THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['UP_ARROW_WHITE'], GAME_SURFACES['INPUT_PROMPTS']['UP_ARROW_WHITE'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - 28 - arrow_debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - 30 - arrow_debug_y_offset)))
    else:
      THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['UP_ARROW_GRAY'], GAME_SURFACES['INPUT_PROMPTS']['UP_ARROW_GRAY'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - 28 - arrow_debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - 30 - arrow_debug_y_offset)))
    if GAME_CONTROLS['left_arrow']:
      THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['LEFT_ARROW_WHITE'], GAME_SURFACES['INPUT_PROMPTS']['LEFT_ARROW_WHITE'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - 56 - arrow_debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - 0 - arrow_debug_y_offset)))
    else:
      THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['LEFT_ARROW_GRAY'], GAME_SURFACES['INPUT_PROMPTS']['LEFT_ARROW_GRAY'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - 56 - arrow_debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - 0 - arrow_debug_y_offset)))
    if GAME_CONTROLS['down_arrow']:
      THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['DOWN_ARROW_WHITE'], GAME_SURFACES['INPUT_PROMPTS']['DOWN_ARROW_WHITE'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - 28 - arrow_debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - 0 - arrow_debug_y_offset)))
    else:
      THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['DOWN_ARROW_GRAY'], GAME_SURFACES['INPUT_PROMPTS']['DOWN_ARROW_GRAY'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - 28 - arrow_debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - 0 - arrow_debug_y_offset)))
    if GAME_CONTROLS['right_arrow']:
      THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['RIGHT_ARROW_WHITE'], GAME_SURFACES['INPUT_PROMPTS']['RIGHT_ARROW_WHITE'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - 0 - arrow_debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - 0 - arrow_debug_y_offset)))
    else:
      THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['RIGHT_ARROW_GRAY'], GAME_SURFACES['INPUT_PROMPTS']['RIGHT_ARROW_GRAY'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - 0 - arrow_debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - 0 - arrow_debug_y_offset)))

    left_alt_debug_x_offset = 170 + debug_x_offset
    left_alt_debug_y_offset = 96 + debug_y_offset
    if GAME_CONTROLS['left_alt']:
      THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['ALT_WHITE'], GAME_SURFACES['INPUT_PROMPTS']['ALT_WHITE'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - left_alt_debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - left_alt_debug_y_offset)))
    else:
      THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['ALT_GRAY'], GAME_SURFACES['INPUT_PROMPTS']['ALT_GRAY'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - left_alt_debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - left_alt_debug_y_offset)))

    spacebar_debug_x_offset = 94 + debug_x_offset
    spacebar_debug_y_offset = 96 + debug_y_offset
    if GAME_CONTROLS['space_bar']:
      THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['SPACEBAR_WHITE'], GAME_SURFACES['INPUT_PROMPTS']['SPACEBAR_WHITE'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - spacebar_debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - spacebar_debug_y_offset)))
    else:
      THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['SPACEBAR_GRAY'], GAME_SURFACES['INPUT_PROMPTS']['SPACEBAR_GRAY'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - spacebar_debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - spacebar_debug_y_offset)))

    right_alt_debug_x_offset = 32 + debug_x_offset
    right_alt_debug_y_offset = 96 + debug_y_offset
    if GAME_CONTROLS['right_alt']:
      THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['ALT_WHITE'], GAME_SURFACES['INPUT_PROMPTS']['ALT_WHITE'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - right_alt_debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - right_alt_debug_y_offset)))
    else:
      THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['ALT_GRAY'], GAME_SURFACES['INPUT_PROMPTS']['ALT_GRAY'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - right_alt_debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - right_alt_debug_y_offset)))


    #If we have a joystick plugged in, we will show the joystick controls
    if len(JOYSTICKS) > 0:
      joystick_buttons_x_offset = 176 + debug_x_offset
      joystick_buttons_y_offset = 128 + debug_y_offset

      if GAME_CONTROLS['controller_a']:
        THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_A_GREEN_WHITE'], GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_A_GREEN_WHITE'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_buttons_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_buttons_y_offset)))
      else:
        THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_A_GRAY'], GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_A_GRAY'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_buttons_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_buttons_y_offset)))
      if GAME_CONTROLS['controller_b']:
        THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_B_RED_WHITE'], GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_B_RED_WHITE'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_buttons_x_offset + 32, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_buttons_y_offset)))
      else:
        THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_B_GRAY'], GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_B_GRAY'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_buttons_x_offset + 32, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_buttons_y_offset)))
      if GAME_CONTROLS['controller_x']:
        THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_X_BLUE_WHITE'], GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_X_BLUE_WHITE'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_buttons_x_offset + 64, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_buttons_y_offset)))
      else:
        THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_X_GRAY'], GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_X_GRAY'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_buttons_x_offset + 64, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_buttons_y_offset)))
      if GAME_CONTROLS['controller_y']:
        THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_Y_YELLOW_WHITE'], GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_Y_YELLOW_WHITE'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_buttons_x_offset + 96, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_buttons_y_offset)))
      else:
        THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_Y_GRAY'], GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_Y_GRAY'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_buttons_x_offset + 96, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_buttons_y_offset)))

      #Left Axis
      joystick_axis_x_offset = 256 + debug_x_offset
      joystick_axis_y_offset = 3 + debug_y_offset
      THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['JOY_AXIS_BASE_GRAY'], GAME_SURFACES['INPUT_PROMPTS']['JOY_AXIS_BASE_GRAY'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_axis_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_axis_y_offset)))
      THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['JOY_AXIS_DIRECTIONAL_WHITE'], GAME_SURFACES['INPUT_PROMPTS']['JOY_AXIS_DIRECTIONAL_WHITE'].get_rect(center = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_axis_x_offset - 15 + GAME_CONTROLS['axis_0'] * 8, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_axis_y_offset - 16 + GAME_CONTROLS['axis_1'] * 8)))

      #Right Axis
      joystick_axis_x_offset = 0 + debug_x_offset
      joystick_axis_y_offset = 3 + debug_y_offset
      THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['JOY_AXIS_BASE_GRAY'], GAME_SURFACES['INPUT_PROMPTS']['JOY_AXIS_BASE_GRAY'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_axis_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_axis_y_offset)))
      THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['JOY_AXIS_DIRECTIONAL_WHITE'], GAME_SURFACES['INPUT_PROMPTS']['JOY_AXIS_DIRECTIONAL_WHITE'].get_rect(center = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_axis_x_offset - 15 + GAME_CONTROLS['axis_2'] * 8, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_axis_y_offset - 16 + GAME_CONTROLS['axis_3'] * 8)))

      joystick_dpad_x_offset = 128 + debug_x_offset
      joystick_dpad_y_offset = 48 + debug_y_offset
      
      THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['JOY_DPAD_BASE_GRAY'], GAME_SURFACES['INPUT_PROMPTS']['JOY_DPAD_BASE_GRAY'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_dpad_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_dpad_y_offset)))
      for joystick_to_debug in JOYSTICKS:
        #Xbox Hat
        if JOYSTICKS[joystick_to_debug].get_name() == 'Xbox 360 Controller':
          if GAME_CONTROLS['hat_up']:
            THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['UP_ARROW_GOLD'], GAME_SURFACES['INPUT_PROMPTS']['UP_ARROW_GOLD'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_dpad_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_dpad_y_offset - 16)))
          if GAME_CONTROLS['hat_down']:
            THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['DOWN_ARROW_GOLD'], GAME_SURFACES['INPUT_PROMPTS']['DOWN_ARROW_GOLD'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_dpad_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_dpad_y_offset)))
          if GAME_CONTROLS['hat_left']:
            THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['LEFT_ARROW_GOLD'], GAME_SURFACES['INPUT_PROMPTS']['LEFT_ARROW_GOLD'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_dpad_x_offset - 16, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_dpad_y_offset)))
          if GAME_CONTROLS['hat_right']:
            THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['RIGHT_ARROW_GOLD'], GAME_SURFACES['INPUT_PROMPTS']['RIGHT_ARROW_GOLD'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_dpad_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_dpad_y_offset)))
        #PowerA D-Pad
        if JOYSTICKS[joystick_to_debug].get_name() == 'PowerA NSW Wired controller':
          if GAME_CONTROLS['dpad_up']:
            THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['UP_ARROW_GOLD'], GAME_SURFACES['INPUT_PROMPTS']['UP_ARROW_GOLD'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_dpad_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_dpad_y_offset - 16)))
          if GAME_CONTROLS['dpad_down']:
            THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['DOWN_ARROW_GOLD'], GAME_SURFACES['INPUT_PROMPTS']['DOWN_ARROW_GOLD'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_dpad_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_dpad_y_offset)))
          if GAME_CONTROLS['dpad_left']:
            THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['LEFT_ARROW_GOLD'], GAME_SURFACES['INPUT_PROMPTS']['LEFT_ARROW_GOLD'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_dpad_x_offset - 16, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_dpad_y_offset)))
          if GAME_CONTROLS['dpad_right']:
            THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['RIGHT_ARROW_GOLD'], GAME_SURFACES['INPUT_PROMPTS']['RIGHT_ARROW_GOLD'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_dpad_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_dpad_y_offset)))

    #Show Actual Game Control Inputs
    direction_x_offset = 10 + debug_x_offset
    direction_y_offset = 10 + debug_y_offset
    THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['DIRECTION_BASE'], GAME_SURFACES['INPUT_PROMPTS']['DIRECTION_BASE'].get_rect(bottomleft = (direction_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - direction_y_offset)))
    if GAME_CONTROLS['UP']:
      THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['DIRECTION_UP_WHITE'], GAME_SURFACES['INPUT_PROMPTS']['DIRECTION_UP_WHITE'].get_rect(bottomleft = (direction_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - direction_y_offset)))
    if GAME_CONTROLS['LEFT']:
      THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['DIRECTION_LEFT_WHITE'], GAME_SURFACES['INPUT_PROMPTS']['DIRECTION_LEFT_WHITE'].get_rect(bottomleft = (direction_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - direction_y_offset)))
    if GAME_CONTROLS['DOWN']:
      THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['DIRECTION_DOWN_WHITE'], GAME_SURFACES['INPUT_PROMPTS']['DIRECTION_DOWN_WHITE'].get_rect(bottomleft = (direction_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - direction_y_offset)))
    if GAME_CONTROLS['RIGHT']:
      THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['DIRECTION_RIGHT_WHITE'], GAME_SURFACES['INPUT_PROMPTS']['DIRECTION_RIGHT_WHITE'].get_rect(bottomleft = (direction_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - direction_y_offset)))

    game_buttons_x_offset = 48 + debug_x_offset
    game_buttons_y_offset = 8 + debug_y_offset
    if GAME_CONTROLS['GREEN']:
      THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['GREEN_BUTTON_DOWN'], GAME_SURFACES['INPUT_PROMPTS']['GREEN_BUTTON_DOWN'].get_rect(bottomleft = (game_buttons_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - game_buttons_y_offset)))
    else:
      THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['GREEN_BUTTON_UP'], GAME_SURFACES['INPUT_PROMPTS']['GREEN_BUTTON_UP'].get_rect(bottomleft = (game_buttons_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - game_buttons_y_offset)))
    if GAME_CONTROLS['RED']:
      THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['RED_BUTTON_DOWN'], GAME_SURFACES['INPUT_PROMPTS']['RED_BUTTON_DOWN'].get_rect(bottomleft = (game_buttons_x_offset + 32, GAME_CONSTANTS['SCREEN_HEIGHT'] - game_buttons_y_offset)))
    else:
      THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['RED_BUTTON_UP'], GAME_SURFACES['INPUT_PROMPTS']['RED_BUTTON_UP'].get_rect(bottomleft = (game_buttons_x_offset + 32, GAME_CONSTANTS['SCREEN_HEIGHT'] - game_buttons_y_offset)))
    if GAME_CONTROLS['BLUE']:
      THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['BLUE_BUTTON_DOWN'], GAME_SURFACES['INPUT_PROMPTS']['BLUE_BUTTON_DOWN'].get_rect(bottomleft = (game_buttons_x_offset + 64, GAME_CONSTANTS['SCREEN_HEIGHT'] - game_buttons_y_offset)))
    else:
      THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['BLUE_BUTTON_UP'], GAME_SURFACES['INPUT_PROMPTS']['BLUE_BUTTON_UP'].get_rect(bottomleft = (game_buttons_x_offset + 64, GAME_CONSTANTS['SCREEN_HEIGHT'] - game_buttons_y_offset)))

    if GAME_CONTROLS['YELLOW']:
      THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['YELLOW_BUTTON_DOWN'], GAME_SURFACES['INPUT_PROMPTS']['YELLOW_BUTTON_DOWN'].get_rect(bottomleft = (game_buttons_x_offset + 96, GAME_CONSTANTS['SCREEN_HEIGHT'] - game_buttons_y_offset)))
    else:
      THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['YELLOW_BUTTON_UP'], GAME_SURFACES['INPUT_PROMPTS']['YELLOW_BUTTON_UP'].get_rect(bottomleft = (game_buttons_x_offset + 96, GAME_CONSTANTS['SCREEN_HEIGHT'] - game_buttons_y_offset)))

    if GAME_STATE['DEBUG_GRID']:
      pygame.draw.lines(THE_SCREEN, GAME_COLORS['GREEN'], False, GAME_CONSTANTS['DEBUG_GRID'], width=1)
  ####################################################################
  # FINAL UPDATES FOR OUR GAME LOOP
  #
  # ***LESSON*** ***GAME LOOP***
  #
  # Tell the game to update what's on screen visually.
  #
  # Calculate how much time has elapsed so we can update our game
  # on the next frame.
  ####################################################################
  if GAME_CLI_ARGUMENTS.double_buffer:
    pygame.display.flip() #Updates the whole screen, with double buffering, we want to use flip
  else:
    pygame.display.update() #show the updates
  
  ELAPSED_MS = GAME_CLOCK.tick(60)
  ELAPSED_S = ELAPSED_MS / 1000.0

pygame.quit()