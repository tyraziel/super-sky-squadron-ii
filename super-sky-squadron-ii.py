############################################################################################################################################
# Game Title:
# Super Sky Squadron II - The Flying Ace Follies
#############################################################################################################################################
import pygame
import argparse
import random
from datetime import datetime
import time
import math

import xml.etree.ElementTree as element_tree

#Import of Key Constants to make evaluation a bit easier
from pygame.locals import (
    K_ESCAPE, K_F1, K_F2, K_F3, K_F4, K_F5, K_F6, K_F7, K_F8, K_F9, K_F10, K_F11, K_F12,
    K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_9, K_0, K_MINUS, K_PLUS,
    K_w, K_a, K_s, K_d,
    K_t, K_y, K_u, K_i, K_o, K_p,
    K_g, K_h, K_j, K_k, K_l,
    K_b, K_n, K_m, K_SLASH,
    K_r, K_g,
    K_UP, K_DOWN, K_LEFT, K_RIGHT,
    K_SPACE, K_LALT, K_RALT, K_LCTRL, K_RCTRL, K_LSHIFT, K_RSHIFT,
    KMOD_SHIFT, KMOD_CTRL, KMOD_ALT,
    KEYDOWN, KEYUP, QUIT
)

######################################################################
# Classes Created to support game objects
######################################################################
class GameSprite(pygame.sprite.Sprite):
  def __init__(self, x=0, y=0, speed_x=0, speed_y=0, rotation=0, speed=0, image=None):
    super().__init__()
    self.x = x
    self.y = y
    self.rect = (self.x, self.y)
    self.image = None
    self.rotation = rotation
    if image != None:
      self.image = image.copy()
      self.rect = self.image.get_rect(center=(self.x, self.y))
    self.speed = speed
    self.speed_x = speed_x
    self.speed_y = speed_y
    self.speed_delta = 0
    self.max_speed = 0
    self.min_speed = 0
    self.speed_rotation = 0
    self.speed_rotation_delta = 0
    self.max_speed_rotation = 0
    self.min_speed_rotation = 0
    self.activated = True
    self.effect_1_active = False
    self.effect_2_active = False
    self.effect_3_active = False
    self.effect_1_ttl = 0
    self.effect_2_ttl = 0
    self.effect_3_ttl = 0
    self.effect_1_ttl_default = 0
    self.effect_2_ttl_default = 0
    self.effect_3_ttl_default = 0
    self.size_modifier = 1

  def set_image(self, image):
    self.image = image.copy()
    self.rect = self.image.get_rect(center=(self.x, self.y))

  def set_location(self, x, y):
    self.x = x
    self.y = y
    self.rect = self.image.get_rect(center=(self.x, self.y))

  def set_location_delta(self, x, y):
    self.set_location(self.x + x, self.y + y)

  #We're going to assume that rotation is set something reasonable so our "fix" will help the rotation of the object stay smooth and within a reasonable number
  def set_rotation(self, rotation):
    self.rotation = rotation
    if self.rotation < 0:
      self.rotation = self.rotation + 360
    if self.rotation > 360:
      self.rotation = self.rotation - 360
  
  def set_rotation_delta(self, rotation):
    self.set_rotation(self.rotation + rotation)

  def set_alpha(self, alpha):
    self.image.set_alpha(alpha)

  def randomize_alpha(self):
    self.image.set_alpha(random.choice(range(0,255)))
  
  def randomize_alpha_damage(self):
    self.image.set_alpha(random.choice(range(32,255)))

class Plane(GameSprite):
  PLANE_DEATH_TTL = 1500

  def __init__(self, x=0, y=0, rotation=0, image=None):
    super().__init__(x, y, 0, 0, rotation, 0, image)
    self.health = 0
    self.weapon_1_cooldown = 0
    self.weapon_2_cooldown = 0
    self.weapon_3_cooldown = 0
    self.weapon_1_cooldown_default = 0
    self.weapon_2_cooldown_default = 0
    self.weapon_3_cooldown_default = 0
    self.weapon_1_speed = 0
    self.weapon_2_speed = 0
    self.weapon_3_speed = 0

class Player(Plane):
  def __init__(self):
    super().__init__()
    self.lives = 0
    self.score = 0

class Base(GameSprite):
  def __init__(self, x=0, y=0, style=0):
    super().__init__(x, y, 0, 0, 0, 0, None)
    self.style = style

class Bullet(GameSprite):
  def __init__(self, x=0, y=0, speed_x=0, speed_y=0, rotation=0, speed=0, image=None, bomb=False):
    super().__init__(x, y, speed_x, speed_y, rotation, speed, image)
    self.bomb = bomb

######################################################################
# Functions Created to support game initialization and transitions
######################################################################
def reset_game_state():
  global GAME_STATE
  GAME_STATE['LAYER_1'] = True 
  GAME_STATE['LAYER_2'] = True 
  GAME_STATE['LAYER_3'] = True 
  GAME_STATE['LAYER_4'] = True 
  GAME_STATE['LAYER_5'] = True 
  GAME_STATE['RUNNING'] = True 
  GAME_STATE['GAME_OVER'] = False
  GAME_STATE['PAUSED'] = False
  GAME_STATE['MULTIPLAYER'] = False
  random.seed(round(time.time() * 1000))

def reset_screens():
  global GAME_STATE
  GAME_STATE['TITLE_SCREEN'] = False
  GAME_STATE['GAME_MODE_SCREEN'] = False
  GAME_STATE['INSTRUCTIONS_SCREEN'] = False
  GAME_STATE['DOGFIGHT_MODE'] = False
  GAME_STATE['MISSION_MODE'] = False
  GAME_STATE['ARENA_MODE'] = False
  GAME_STATE['GAME_OVER_SCREEN'] = False

def reset_transitions():
  global GAME_STATE
  GAME_STATE['TRANSITION_TO_TITLE_SCREEN'] = False
  GAME_STATE['TRANSITION_TO_GAME_MODE_SCREEN'] = False
  GAME_STATE['TRANSITION_TO_INSTRUCTIONS_SCREEN'] = False
  GAME_STATE['TRANSITION_TO_DOGFIGHT_MODE'] = False
  GAME_STATE['TRANSITION_TO_MISSION_MODE'] = False
  GAME_STATE['TRANSITION_TO_ARENA_MODE'] = False
  GAME_STATE['TRANSITION_TO_GAME_OVER_SCREEN'] = False
  GAME_STATE_TRANSITION_TTL['TRANSITION_TO_TITLE_SCREEN'] = TTL_DEFAULTS['TRANSITION_TO_TITLE_SCREEN']
  GAME_STATE_TRANSITION_TTL['TRANSITION_TO_GAME_MODE_SCREEN'] = TTL_DEFAULTS['TRANSITION_TO_GAME_MODE_SCREEN']
  GAME_STATE_TRANSITION_TTL['TRANSITION_TO_INSTRUCTIONS_SCREEN'] = TTL_DEFAULTS['TRANSITION_TO_INSTRUCTIONS_SCREEN']
  GAME_STATE_TRANSITION_TTL['TRANSITION_TO_DOGFIGHT_MODE'] = TTL_DEFAULTS['TRANSITION_TO_DOGFIGHT_MODE']
  GAME_STATE_TRANSITION_TTL['TRANSITION_TO_MISSION_MODE'] = TTL_DEFAULTS['TRANSITION_TO_MISSION_MODE']
  GAME_STATE_TRANSITION_TTL['TRANSITION_TO_ARENA_MODE'] = TTL_DEFAULTS['TRANSITION_TO_ARENA_MODE']
  GAME_STATE_TRANSITION_TTL['TRANSITION_TO_GAME_OVER_SCREEN'] = TTL_DEFAULTS['TRANSITION_TO_GAME_OVER_SCREEN']

def stop_all_sounds():
  if MUSIC_TITLE_SCREEN != None:
    MUSIC_TITLE_SCREEN.fadeout(MUSIC_FADE_OUT)
  if MUSIC_PRE_GAME != None:
    MUSIC_PRE_GAME.fadeout(MUSIC_FADE_OUT)
  if MUSIC_DOG_FIGHTING != None:
    MUSIC_DOG_FIGHTING.fadeout(MUSIC_FADE_OUT)


def destroy_dogfight_objects():
  global player_1_bullets
  global player_2_bullets
  global explosions
  global PLAYER_1_BASE
  global PLAYER_2_BASE

  #clean up the objects
  for bullet in reversed(player_1_bullets.sprites()):
    bullet.kill()
  for bullet in reversed(player_2_bullets.sprites()):
    bullet.kill()
  for explosion in reversed(explosions.sprites()):
    explosion.kill()
  
  player_1_bullets = pygame.sprite.Group()
  player_2_bullets = pygame.sprite.Group()
  explosions = pygame.sprite.Group()
  PLAYER_1_BASE = Base()
  PLAYER_1_BASE.activated = False
  PLAYER_2_BASE = Base()
  PLAYER_2_BASE.activated = False

def destroy_mission_objects():
  return

def destroy_mission_level_objects():
  return

def destroy_all():
  destroy_dogfight_objects()
  destroy_mission_level_objects()
  destroy_mission_objects()
  reset_players()

def reset_players():
  global PLAYER_1
  global PLAYER_2

  PLAYER_1 = Player()
  PLAYER_2 = Player()

def reset_for_game_state_transition():
  destroy_all()
  reset_screens()
  reset_transitions()
  destroy_alert()

def create_alert(color, font, txt_1, txt_2, ttl, fadeout, fadeout_ttl):
  global alert_ttl 
  global alert_txt_1
  global alert_txt_2
  global alert_color
  global alert_active
  global alert_fadeout
  global alert_fadeout_ttl
  global alert_font

  alert_txt_1 = txt_1
  alert_txt_2 = txt_2

  alert_color = color
  if color == "":
    alert_color = GAME_COLORS['SHMUP_RED']

  alert_font = font
  if font == "":
    alert_font = GAME_FONTS['KENNEY_MINI_SQUARE_64']
  alert_fadeout = fadeout
  alert_fadeout_ttl = fadeout_ttl

  alert_ttl = ttl
  if ttl < 1:
    alert_ttl = TTL_DEFAULTS['ALERT']
  
  alert_active = True

def destroy_alert():
  global alert_active
  global alert_txt_1
  global alert_txt_2
  global alert_fadeout
  global alert_font

  alert_active = False
  alert_ttl = 0
  alert_txt_1 = ""
  alert_txt_2 = ""
  alert_fadeout = False
  alert_fadeout_ttl = TTL_DEFAULTS['ALERT_FADEOUT']
  alert_font = GAME_FONTS['KENNEY_MINI_SQUARE_64']

def initialize_title_screen():
  global GAME_STATE
  global press_start_color
  global press_start_blink_ttl

  press_start_color = GAME_COLORS['SHMUP_ROYAL_PURPLE']
  press_start_blink_ttl = TTL_DEFAULTS['PRESS_START_BLINK']

  reset_for_game_state_transition()
  reset_players()

  stop_all_sounds()

  if MUSIC_TITLE_SCREEN != None:
    MUSIC_TITLE_SCREEN.set_volume(1.0)
    MUSIC_TITLE_SCREEN.play(loops=-1, fade_ms=MUSIC_FADE_IN)
  
  GAME_STATE['TITLE_SCREEN'] = True
  GAME_STATE['MULTIPLAYER'] = False

def initialize_game_mode_screen():
  global GAME_STATE

  reset_for_game_state_transition()
  stop_all_sounds()

  if MUSIC_PRE_GAME != None:
    MUSIC_PRE_GAME.set_volume(1.0)
    MUSIC_PRE_GAME.play(loops=-1, fade_ms=MUSIC_FADE_IN)

  GAME_STATE['GAME_MODE_SCREEN'] = True
  GAME_STATE['MULTIPLAYER'] = False
  GAME_MODE_OPTIONS['PLAYERS'] = True
  GAME_MODE_OPTIONS['GAME_MODE'] = False
  GAME_MODE_OPTIONS['STARTING_LIVES'] = False
  GAME_MODE_OPTIONS['START_GAME'] = False

def initialize_instructions_screen():
  global GAME_STATE
  global instructions_screen_ttl

  reset_for_game_state_transition()

  if MUSIC_PRE_GAME != None:
    if MUSIC_PRE_GAME.get_num_channels() < 1:
      stop_all_sounds()
      MUSIC_PRE_GAME.set_volume(1.0)
      MUSIC_PRE_GAME.play(loops=-1, fade_ms=MUSIC_FADE_IN)

  GAME_STATE['INSTRUCTIONS_SCREEN'] = True

  instructions_screen_ttl = TTL_DEFAULTS['INSTRUCTIONS_SCREEN']
  

def setup_for_dogfight_mode_quick_jump():
  global GAME_MODE_OPTIONS

  GAME_MODE_OPTIONS['ONE_PLAYER'] = False
  GAME_MODE_OPTIONS['TWO_PLAYERS'] = True
  GAME_MODE_OPTIONS['MISSION'] = False
  GAME_MODE_OPTIONS['ARENA'] = False
  GAME_MODE_OPTIONS['DOGFIGHT'] = True
  #GAME_MODE_OPTIONS['LIVES_COUNT'] = 3
  GAME_STATE['MULTIPLAYER'] = True

def initialize_dogfight_mode():
  global GAME_STATE
  global PLAYER_1
  global PLAYER_2
  global MAP
  global CAMERA
  global dogfighting_pvp_active
  global dogfighting_pvp_ready_ttl
  global dogfighting_pvp_set_ttl
  global dogfighting_pvp_fight_ttl
  global dogfighting_pvp_fight_shown
  global dogfighting_base_creation_ttl
  global player_1_bullets
  global player_2_bullets

  dogfighting_pvp_active = False
  dogfighting_pvp_ready_ttl = TTL_DEFAULTS['READY']
  dogfighting_pvp_set_ttl = TTL_DEFAULTS['SET']
  dogfighting_pvp_fight_ttl = TTL_DEFAULTS['FIGHT']
  dogfighting_pvp_fight_shown = False
  dogfighting_base_creation_ttl = random.choice(range(TTL_DEFAULTS['BASE_CREATION_MIN'], TTL_DEFAULTS['BASE_CREATION_MAX']))

  reset_for_game_state_transition()
  reset_players()

  stop_all_sounds()

  if MUSIC_DOG_FIGHTING != None:
    MUSIC_DOG_FIGHTING.set_volume(1.0)
    MUSIC_DOG_FIGHTING.play(loops=-1, fade_ms=MUSIC_FADE_IN)

  CAMERA = {'X': 0, 'Y': 0}

  ### Initialize the map
  MAP = []
  for i in range(19):
    for j in range (40):
      if j == 0:
        MAP.append([])
      if j == 19 or j == 20:
        MAP[i].append("W0") 
      elif j == 18:
        MAP[i].append("GBR")
      elif j < 18:
        MAP[i].append("G0")
      elif j == 21:
        MAP[i].append("BBL")
      elif j > 21:
        MAP[i].append("B0")
      else:
        MAP[i].append("G0")

  GAME_STATE['DOGFIGHT_MODE'] = True
  GAME_STATE['MULTIPLAYER'] = True #Dogfighting can only be multiplayer

  PLAYER_1.lives = GAME_MODE_OPTIONS['LIVES_COUNT']
  PLAYER_2.lives = GAME_MODE_OPTIONS['LIVES_COUNT']

  PLAYER_1.set_image(GAME_SURFACES['PIXEL_SHMUP_SHIPS']['RED_B_FIGHTER'])
  PLAYER_2.set_image(GAME_SURFACES['PIXEL_SHMUP_SHIPS']['BLUE_B_FIGHTER'])

  PLAYER_1.set_location(GAME_CONSTANTS['SCREEN_WIDTH'] / 4, GAME_CONSTANTS['SCREEN_HEIGHT'] / 2 - GAME_CONSTANTS['SQUARE_SIZE'])
  PLAYER_2.set_location((GAME_CONSTANTS['SCREEN_WIDTH'] / 4) * 3, GAME_CONSTANTS['SCREEN_HEIGHT'] / 2 - GAME_CONSTANTS['SQUARE_SIZE'])

  PLAYER_1.set_rotation(270)
  PLAYER_2.set_rotation(90)

  PLAYER_1.speed = 64
  PLAYER_2.speed = 64

  PLAYER_1.speed_delta = 96
  PLAYER_2.speed_delta = 96

  PLAYER_1.min_speed = 64
  PLAYER_2.min_speed = 64

  PLAYER_1.max_speed = 256
  PLAYER_2.max_speed = 256

  PLAYER_1.speed_rotation = 180
  PLAYER_2.speed_rotation = 180

  PLAYER_1.speed_rotation_delta = 45
  PLAYER_2.speed_rotation_delta = 45

  PLAYER_1.min_speed_rotation = 90
  PLAYER_2.min_speed_rotation = 90

  PLAYER_1.max_speed_rotation = 180
  PLAYER_2.max_speed_rotation = 180

  PLAYER_1.weapon_1_cooldown = 0
  PLAYER_1.weapon_2_cooldown = 0
  PLAYER_1.weapon_1_cooldown_default = 250
  PLAYER_1.weapon_2_cooldown_default = 1000
  PLAYER_1.weapon_1_speed = 256
  PLAYER_1.weapon_2_speed = 128

  PLAYER_2.weapon_1_cooldown = 0
  PLAYER_2.weapon_2_cooldown = 0
  PLAYER_2.weapon_1_cooldown_default = 250
  PLAYER_2.weapon_2_cooldown_default = 1000
  PLAYER_2.weapon_1_speed = 256
  PLAYER_2.weapon_2_speed = 128

  PLAYER_1.effect_1_ttl = 3000
  PLAYER_2.effect_1_ttl = 3000

  PLAYER_1.effect_1_ttl_default = 3000
  PLAYER_2.effect_1_ttl_default = 3000

  PLAYER_1.effect_1_active = True
  PLAYER_2.effect_1_active = True

  player_1_bullets = pygame.sprite.Group()
  player_2_bullets = pygame.sprite.Group()
  explosions = pygame.sprite.Group()

def initialize_mission_mode():
  global GAME_STATE

  reset_for_game_state_transition()

  GAME_STATE['MISSION_MODE'] = True
  ### Re-Initialize player 1 - 3 lives - if GAME_STATE['LIVES_CHEAT_CODE'] is active then 10
  ### Re-Initialize player 2 - 3 lives
  ### Load Level

def initialize_arena_mode():
  global GAME_STATE

  reset_for_game_state_transition()

  GAME_STATE['ARENA_MODE'] = True
  ### Re-Initialize player 1 - 1 life - if GAME_STATE['LIVES_CHEAT_CODE'] is active then 3
  ### Re-Initialize player 2 - 1 life
  ### Dynamically load the level based on YYYYMMDD seed, so this will always seed the same per day (could possibly do this for week though?)
  random.seed(int(datetime.today().strftime("%Y%m%d")))

def initialize_game_over_screen():
  global GAME_STATE

  reset_for_game_state_transition()

  GAME_STATE['GAME_OVER_SCREEN'] = True

######################################################################
# ***LESSON 0 - Argument Parsing***
#
# Argument parsing to make running the game in different modes 
# slightly easier
######################################################################

argument_parser = argparse.ArgumentParser(description="CodeMash 2025 Divez - So you want to make video games? - Super Sky Squadron II: The Flying Ace Follies")

argument_parser.add_argument("--test", "--test-mode", help="Enter Test/Dev Mode (Also turned on with any debug flag)", action="store_true", dest="test_mode")
argument_parser.add_argument("--debug", help="Enter Debug Mode", action="store_true", dest="debug")
argument_parser.add_argument("--debug-grid", help="Show Debug Grid", action="store_true", dest="debug_grid")
argument_parser.add_argument("--debug-to-console", help="Debug to Console only (does not need to be used in conjunction with --debug, does not debug events)", action="store_true", dest="debug_to_console")
argument_parser.add_argument("--debug-events", help="Debug Events to Console (does not need --debug or --debug-to-console)", action="store_true", dest="debug_events")
argument_parser.add_argument("--debug-joystick-events", help="Debug Events to Console (does not need --debug or --debug-to-console or --debug-events)", action="store_true", dest="debug_joystick_events")
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

#Game Constants are generally held within this dictionary
#These are 'indexed' by GAME_CONSTANTS['KEY']
######################################################################
# ***LESSON 3*** - SCREEN COORDINATES
######################################################################
GAME_CONSTANTS = {'SCREEN_WIDTH': 1280, 'SCREEN_HEIGHT': 720, 'SCREEN_FLAGS': 0, 'SQUARE_SIZE': 32,
                  'MAX_CONNECTED_JOYSTICKS': 2}

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
               'SHMUP_BLUE': (51, 153, 218),
               'SHMUP_RED': (218, 52, 72),
               'SHMUP_ORANGE': (218, 116, 52),
               'SHMUP_YELLOW': (218, 199, 52),
               'SHMUP_GREEN': (51, 153, 77),
               'SHMUP_ROYAL_PURPLE': (75, 52, 218),
               'SHMUP_PURPLE': (128, 51, 153),
               'SHMUP_BLACK': (51, 51, 51),
               'SHMUP_GRAY': (153, 153, 153),
               'SHMUP_WHITE': (218, 218, 218),
              }

#Time to live defaults are within this dictionary
# ***LESSON***
TTL_DEFAULTS = {'TRANSITION_TO_TITLE_SCREEN': 5000, 'TRANSITION_TO_GAME_MODE_SCREEN': 750, 'TRANSITION_TO_INSTRUCTIONS_SCREEN': 750, 'TRANSITION_TO_DOGFIGHT_MODE': 1000, 'TRANSITION_TO_MISSION_MODE': 1000, 'TRANSITION_TO_ARENA_MODE': 1000, 'TRANSITION_TO_GAME_OVER_SCREEN': 5000,
                'PRESS_START_BLINK': 750, 'ALERT': 1500, 'ALERT_FADEOUT': 1000, 'GAME_OVER': 3500,
                'READY': 1500, 'SET': 1500, 'FIGHT': 750, 'BASE_CREATION_MIN':7500, 'BASE_CREATION_MAX': 10000,
                'INSTRUCTIONS_SCREEN': 25500}

######################################################################
# SET GAME DEFAULTS
# ***LESSON 4*** - State Machine
######################################################################
#Game State is generally held within this dictionary
#These are 'indexed' by GAME_STATE['KEY']
GAME_STATE = {'DEBUG': GAME_CLI_ARGUMENTS.debug, 'DEBUG_GRID': GAME_CLI_ARGUMENTS.debug_grid, 'DEBUG_TO_CONSOLE': GAME_CLI_ARGUMENTS.debug_to_console, 'DEBUG_EVENTS': GAME_CLI_ARGUMENTS.debug_events, 'DEBUG_JOYSTICK_EVENTS': GAME_CLI_ARGUMENTS.debug_joystick_events, 'DEBUG_EVENTS_VERBOSE': GAME_CLI_ARGUMENTS.debug_events_verbose, 
              'TEST_MODE': GAME_CLI_ARGUMENTS.test_mode or GAME_CLI_ARGUMENTS.debug or GAME_CLI_ARGUMENTS.debug_grid or GAME_CLI_ARGUMENTS.debug_to_console or GAME_CLI_ARGUMENTS.debug_events or GAME_CLI_ARGUMENTS.debug_events_verbose,
              'LAYER_1': True, 'LAYER_2': True, 'LAYER_3': True, 'LAYER_4': True, 'LAYER_5': True,
              'RUNNING': True, 'GAME_OVER': False, 'PAUSED': False, 'LIVES_CHEAT_CODE': False,
              'MULTIPLAYER': False,
              'TITLE_SCREEN': False, 'GAME_MODE_SCREEN': False, 'INSTRUCTIONS_SCREEN': False, 'DOGFIGHT_MODE': False, 'MISSION_MODE': False, 'ARENA_MODE': False, 'GAME_OVER_SCREEN': False,
              'TRANSITION_TO_TITLE_SCREEN': False, 'TRANSITION_TO_GAME_MODE_SCREEN': False, 'TRANSITION_TO_INSTRUCTIONS_SCREEN': False, 'TRANSITION_TO_DOGFIGHT_MODE': False, 'TRANSITION_TO_MISSION_MODE': False, 'TRANSITION_TO_ARENA_MODE': False, 'TRANSITION_TO_GAME_OVER_SCREEN': False,
             }

GAME_MODE_OPTIONS = {'PLAYERS': True, 'GAME_MODE': False, 'STARTING_LIVES': False, 'START_GAME': False,
                     'ONE_PLAYER': True, 'TWO_PLAYERS': False, 
                     'MISSION': True, 'ARENA': False, 'DOGFIGHT': False,
                     'DOGFIGHT_BASES': True,
                     'LIVES_COUNT': 3}

GAME_STATE_TRANSITION_TTL = {'TRANSITION_TO_TITLE_SCREEN': TTL_DEFAULTS['TRANSITION_TO_TITLE_SCREEN'], 'TRANSITION_TO_GAME_MODE_SCREEN': TTL_DEFAULTS['TRANSITION_TO_GAME_MODE_SCREEN'], 'TRANSITION_TO_INSTRUCTIONS_SCREEN': TTL_DEFAULTS['TRANSITION_TO_INSTRUCTIONS_SCREEN'], 'TRANSITION_TO_DOGFIGHT_MODE': TTL_DEFAULTS['TRANSITION_TO_DOGFIGHT_MODE'], 'TRANSITION_TO_MISSION_MODE': TTL_DEFAULTS['TRANSITION_TO_MISSION_MODE'], 'TRANSITION_TO_ARENA_MODE': TTL_DEFAULTS['TRANSITION_TO_ARENA_MODE'], 'TRANSITION_TO_GAME_OVER_SCREEN': TTL_DEFAULTS['TRANSITION_TO_GAME_OVER_SCREEN']}

######################################################################
# INITIALIZE PYGAME AND OTHER ELEMENTS FOR THE GAME
######################################################################
if GAME_CLI_ARGUMENTS.debug_to_console:
  print(f"[INIT] Initializing Pygame")
(init_pass, init_fail) = pygame.init()
if GAME_CLI_ARGUMENTS.debug_to_console:
  print(f"[INIT] Complete!  (P: {init_pass} // F: {init_fail})")

#We create a separate dictionary for the game controls so we can do stuff according to the state of the controls
# ***LESSON***
#'indexed' by GAME_CONTROLS['key']
GAME_CONTROLS = {'PLAYER_1': {'UP': False, 'LEFT': False, 'DOWN' : False, 'RIGHT': False,
                              'GREEN': False, 'BLUE': False, 'RED': False, 'YELLOW': False},
                 'PLAYER_2': {'UP': False, 'LEFT': False, 'DOWN' : False, 'RIGHT': False,
                              'GREEN': False, 'BLUE': False, 'RED': False, 'YELLOW': False},

                 'w': False, 'a': False, 's': False, 'd': False,
                 'up_arrow': False, 'left_arrow': False, 'down_arrow': False, 'right_arrow': False,
                 'space_bar': False, 'left_alt': False, 'right_alt': False, 
                 'left_ctrl': False, 'right_ctrl': False, 'left_shift': False, 'right_shift': False,
                 'front_slash': False,

                 'JOYSTICK_1': { 'hat_up': False, 'hat_left': False, 'hat_down': False, 'hat_right': False,
                                 'dpad_up': False, 'dpad_left': False, 'dpad_down': False, 'dpad_right': False,
                                 'axis_0': 0.0, 'axis_1': 0.0, 'axis_2': 0.0, 'axis_3': 0.0, 'axis_4': 0.0, 'axis_5': 0.0,
                                 'controller_a': False, 'controller_b': False, 'controller_x': False, 'controller_y': False,
                                 'controller_lb': False, 'controller_rb': False, 'controller_back': False, 'controller_start': False
                               },
                 'JOYSTICK_2': { 'hat_up': False, 'hat_left': False, 'hat_down': False, 'hat_right': False,
                                 'dpad_up': False, 'dpad_left': False, 'dpad_down': False, 'dpad_right': False,
                                 'axis_0': 0.0, 'axis_1': 0.0, 'axis_2': 0.0, 'axis_3': 0.0, 'axis_4': 0.0, 'axis_5': 0.0,
                                 'controller_a': False, 'controller_b': False, 'controller_x': False, 'controller_y': False,
                                 'controller_lb': False, 'controller_rb': False, 'controller_back': False, 'controller_start': False
                               },
                }

#For joystick controllers
JOYSTICKS = {}
JOYSTICK_MAPPER = {}

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
              'KENNEY_MINI_SQUARE_48': pygame.font.Font('./fonts/Kenney Mini Square.ttf', 48),
              'KENNEY_MINI_SQUARE_64': pygame.font.Font('./fonts/Kenney Mini Square.ttf', 64),
              'KENNEY_MINI_SQUARE_80': pygame.font.Font('./fonts/Kenney Mini Square.ttf', 80),
              'KENNEY_MINI_SQUARE_96': pygame.font.Font('./fonts/Kenney Mini Square.ttf', 96),
              'KENNEY_MINI_SQUARE_128': pygame.font.Font('./fonts/Kenney Mini Square.ttf', 128),
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
# Load individual surfaces as needed.
# After the full sheet is loaded we are then going to pull out the parts of the spritesheet (subsurface) that we want and we're making them twice as large (scale)
######################################################################
GAME_SURFACES = {}

if GAME_CLI_ARGUMENTS.debug_to_console:
  print(f"[INIT] [TEXTURE] Loading")

if GAME_CLI_ARGUMENTS.debug_to_console:
  print(f"[INIT] [TEXTURE-LOAD] [INDIVIDUAL]: ui-pack")

GAME_SURFACES['UI_PACK'] = {}
GAME_SURFACES['UI_PACK']['GREY'] = {}
GAME_SURFACES['UI_PACK']['RED'] = {}
GAME_SURFACES['UI_PACK']['GREY']['BUTTON_SQUARE_FLAT'] = pygame.image.load("./sprites/ui-pack/grey/default/button_square_flat.png")
GAME_SURFACES['UI_PACK']['RED']['CHECK_SQUARE_GREY'] = pygame.image.load("./sprites/ui-pack/red/default/check_square_grey.png")
GAME_SURFACES['UI_PACK']['RED']['CHECK_SQUARE_COLOR'] = pygame.image.load("./sprites/ui-pack/red/default/check_square_color.png")

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

##### CONSIDER REFACTORING THIS INTO A METHOD/FUNCTION IN A SEPARATE FILE
if GAME_CLI_ARGUMENTS.debug_to_console:
  print(f"[INIT] [TEXTURE-LOAD] [FULL-SHEET]: pixel-shmup-tiles")
GAME_SURFACES['PIXEL_SHMUP_TILES'] = {}
GAME_SURFACES['PIXEL_SHMUP_TILES']['FULL_SHEET'] = pygame.image.load("./sprites/pixel-shmup/tiles_packed.png") #192x160
pixel_shmup_tiles_xml_subtextures = element_tree.parse("./sprites/pixel-shmup/tiles_sheet.xml").getroot().findall("SubTexture")
for subtexture in pixel_shmup_tiles_xml_subtextures:
  subsurface_name = subtexture.attrib['name'].upper().split(".")[0]
  if GAME_CLI_ARGUMENTS.debug_to_console:
    print(f"[INIT] [TEXTURE-LOAD] [SUBSURFACE]: {subsurface_name}")
  subsurface_x = int(subtexture.attrib['x'])
  subsurface_y = int(subtexture.attrib['y'])
  subsurface_width = int(subtexture.attrib['width'])
  subsurface_height = int(subtexture.attrib['height'])
  GAME_SURFACES['PIXEL_SHMUP_TILES'][subsurface_name] = pygame.transform.scale(GAME_SURFACES['PIXEL_SHMUP_TILES']['FULL_SHEET'].subsurface(pygame.Rect(subsurface_x, subsurface_y, subsurface_width, subsurface_height)), (subsurface_width*2, subsurface_height*2))

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
# LOAD SOUNDS
# **** LESSON ****
# 
# Load individual sound files as needed.
######################################################################
MUSIC_TITLE_SCREEN = None
MUSIC_PRE_GAME = None
MUSIC_DOG_FIGHTING = None
MUSIC_MISSION = None

MUSIC_FADE_IN = 250
MUSIC_FADE_OUT = 250

SOUND_EFFECT_SELECT = None
SOUND_EFFECT_UI_MOVE = None

SOUND_EFFECT_SHOT_1 = None
SOUND_EFFECT_SHOT_2 = None
SOUND_EFFECT_BOMB = None
SOUND_EFFECT_PLANE_HIT = None
SOUND_EFFECT_EXPLOSION_1 = None
SOUND_EFFECT_EXPLOSION_2 = None
SOUND_EFFECT_GROUND_HIT = None
SOUND_EFFECT_ENGINE_1 = None
SOUND_EFFECT_ENGINE_2 = None
SOUND_EFFECT_OBJECTIVE_ACHIEVED = None
SOUND_EFFECT_FIGHT = None

if(not GAME_CLI_ARGUMENTS.mute_audio):
  if GAME_CLI_ARGUMENTS.debug_to_console:
    print(f"[INIT] [AUDIO] Loading")

  if GAME_CLI_ARGUMENTS.debug_to_console:
    print(f"[INIT] [AUDIO-MIXER] Loading")

  pygame.mixer.init()

  if GAME_CLI_ARGUMENTS.debug_to_console:
    print(f"[INIT] [AUDIO-MIXER] Completed")

  if GAME_CLI_ARGUMENTS.debug_to_console:
    print(f"[INIT] [AUDIO-MUSIC] Loading Title Music")  
  try:
    MUSIC_TITLE_SCREEN = pygame.mixer.Sound("./music/Mission Plausible.ogg")
  except Exception as exception:
    print(f"[INIT] [AUDIO-MUSIC-FAILURE] Title Music Failed to load: {exception}")

  if GAME_CLI_ARGUMENTS.debug_to_console:
    print(f"[INIT] [AUDIO-MUSIC] Loading Pre-Game Music")  
  try:
    MUSIC_PRE_GAME = pygame.mixer.Sound("./music/Retro Beat.ogg")
  except Exception as exception:
    print(f"[INIT] [AUDIO-MUSIC-FAILURE] Pre-Game Music Failed to load: {exception}")

  if GAME_CLI_ARGUMENTS.debug_to_console:
    print(f"[INIT] [AUDIO-MUSIC] Loading Dogfighting Music")  
  try:
    MUSIC_DOG_FIGHTING = pygame.mixer.Sound("./music/Drumming Sticks.ogg")
  except Exception as exception:
    print(f"[INIT] [AUDIO-MUSIC-FAILURE] Dogfighting Music Failed to load: {exception}")

  if GAME_CLI_ARGUMENTS.debug_to_console:
    print(f"[INIT] [AUDIO-SFX] Loading Select SFX")  
  try:
    SOUND_EFFECT_SELECT = pygame.mixer.Sound("./sfx/confirmation_001.ogg")
  except Exception as exception:
    print(f"[INIT] [AUDIO-SFX-FAILURE] Select SFX Failed to load: {exception}")

  if GAME_CLI_ARGUMENTS.debug_to_console:
    print(f"[INIT] [AUDIO-SFX] Loading UI Move SFX")  
  try:
    SOUND_EFFECT_UI_MOVE = pygame.mixer.Sound("./sfx/select_007.ogg")
  except Exception as exception:
    print(f"[INIT] [AUDIO-SFX-FAILURE] UI Move SFX Failed to load: {exception}")

  if GAME_CLI_ARGUMENTS.debug_to_console:
    print(f"[INIT] [AUDIO-SFX] Loading Shot 1 SFX")  
  try:
    SOUND_EFFECT_SHOT_1 = pygame.mixer.Sound("./sfx/laserSmall_001.ogg")
  except Exception as exception:
    print(f"[INIT] [AUDIO-SFX-FAILURE] Shot 1 SFX Failed to load: {exception}")

  if GAME_CLI_ARGUMENTS.debug_to_console:
    print(f"[INIT] [AUDIO-SFX] Loading Shot 2 SFX")  
  try:
    SOUND_EFFECT_SHOT_2 = pygame.mixer.Sound("./sfx/laserSmall_003.ogg")
  except Exception as exception:
    print(f"[INIT] [AUDIO-SFX-FAILURE] Shot 2 SFX Failed to load: {exception}")

  if GAME_CLI_ARGUMENTS.debug_to_console:
    print(f"[INIT] [AUDIO-SFX] Loading Bomb SFX")  
  try:
    SOUND_EFFECT_BOMB = pygame.mixer.Sound("./sfx/fall1.ogg")
  except Exception as exception:
    print(f"[INIT] [AUDIO-SFX-FAILURE] Shot 2 SFX Failed to load: {exception}")

  if GAME_CLI_ARGUMENTS.debug_to_console:
    print(f"[INIT] [AUDIO-SFX] Plane Hit SFX")  
  try:
    SOUND_EFFECT_PLANE_HIT = pygame.mixer.Sound("./sfx/hit1.ogg")
  except Exception as exception:
    print(f"[INIT] [AUDIO-SFX-FAILURE] Plane Hit SFX Failed to load: {exception}")

  if GAME_CLI_ARGUMENTS.debug_to_console:
    print(f"[INIT] [AUDIO-SFX] Explosion 1 (Plane) SFX")  
  try:
    SOUND_EFFECT_EXPLOSION_1 = pygame.mixer.Sound("./sfx/explosion1.ogg")
  except Exception as exception:
    print(f"[INIT] [AUDIO-SFX-FAILURE] Explosion 1 (Plane) SFX Failed to load: {exception}")

  if GAME_CLI_ARGUMENTS.debug_to_console:
    print(f"[INIT] [AUDIO-SFX] Explosion 2 (Ground) SFX")  
  try:
    SOUND_EFFECT_EXPLOSION_2 = pygame.mixer.Sound("./sfx/explosionCrunch_003.ogg")
  except Exception as exception:
    print(f"[INIT] [AUDIO-SFX-FAILURE] Explosion 2 (Ground) SFX Failed to load: {exception}")

  if GAME_CLI_ARGUMENTS.debug_to_console:
    print(f"[INIT] [AUDIO-SFX] Ground Hit SFX")  
  try:
    SOUND_EFFECT_GROUND_HIT = pygame.mixer.Sound("./sfx/rumble3.ogg")
  except Exception as exception:
    print(f"[INIT] [AUDIO-SFX-FAILURE] Ground Hit SFX Failed to load: {exception}")

  if GAME_CLI_ARGUMENTS.debug_to_console:
    print(f"[INIT] [AUDIO-SFX] Engine 1 SFX")  
  try:
    SOUND_EFFECT_ENGINE_1 = pygame.mixer.Sound("./sfx/engine3.ogg")
  except Exception as exception:
    print(f"[INIT] [AUDIO-SFX-FAILURE] Engine 1 SFX Failed to load: {exception}")

  if GAME_CLI_ARGUMENTS.debug_to_console:
    print(f"[INIT] [AUDIO-SFX] Engine 2 SFX")  
  try:
    SOUND_EFFECT_ENGINE_2 = pygame.mixer.Sound("./sfx/engine4.ogg")
  except Exception as exception:
    print(f"[INIT] [AUDIO-SFX-FAILURE] Engine 2 SFX Failed to load: {exception}")

  if GAME_CLI_ARGUMENTS.debug_to_console:
    print(f"[INIT] [AUDIO-SFX] Objective Achieved SFX")  
  try:
    SOUND_EFFECT_OBJECTIVE_ACHIEVED = pygame.mixer.Sound("./sfx/objective achieved.ogg")
  except Exception as exception:
    print(f"[INIT] [AUDIO-SFX-FAILURE] Objective Achieved SFX Failed to load: {exception}")

  if GAME_CLI_ARGUMENTS.debug_to_console:
    print(f"[INIT] [AUDIO-SFX] Fight SFX")  
  try:
    SOUND_EFFECT_FIGHT = pygame.mixer.Sound("./sfx/fight.ogg")
  except Exception as exception:
    print(f"[INIT] [AUDIO-SFX-FAILURE] Fight SFX Failed to load: {exception}")


  if GAME_CLI_ARGUMENTS.debug_to_console:
    print(f"[INIT] [AUDIO] Completed")

else:
  if GAME_CLI_ARGUMENTS.debug_to_console:
    print(f"[INIT] [AUDIO] Skipping due to mute_audio being True")


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

pygame.display.set_caption("CodeMash 2025 Divez - So you want to make video games? - Super Sky Squadron II: The Flying Ace Follies")

# Create the main screen object
THE_SCREEN = pygame.display.set_mode((GAME_CONSTANTS['SCREEN_WIDTH'], GAME_CONSTANTS['SCREEN_HEIGHT']), GAME_CONSTANTS['PYGAME_SCREEN_FLAGS'])
THE_SCREEN.fill(GAME_COLORS['DEEP_PURPLE'])
pygame.display.update()

print(f"PyGame Driver:  {pygame.display.get_driver()}")
print(f"PyGame Display Info:\n{pygame.display.Info()}")

######################################################################
# ***LESSON***
# Initialize other game elements
######################################################################

# Create our "Camera"
CAMERA = {'X': 0, 'Y': 0}

# Build out a default map 19 high and 40 wide
MAP = []
for i in range(19):
  for j in range (40):
    if j == 0:
      MAP.append([])
    MAP[i].append("G0")

#Initialize press start
press_start_color = GAME_COLORS['SHMUP_ROYAL_PURPLE']
press_start_blink_ttl = TTL_DEFAULTS['PRESS_START_BLINK']

#Initialize Alerts
alert_ttl = TTL_DEFAULTS['ALERT']
alert_txt_1 = ""
alert_txt_2 = ""
alert_color = GAME_COLORS['SHMUP_RED']
alert_active = False
alert_fadeout = False
alert_fadeout_ttl = TTL_DEFAULTS['ALERT_FADEOUT']
alert_font = GAME_FONTS['KENNEY_MINI_SQUARE_64']

# Initialize Players
PLAYER_1 = Player()
PLAYER_2 = Player()

# Initialize Player Bases (for DogFighting)
PLAYER_1_BASE = Base()
PLAYER_1_BASE.activated = False
PLAYER_2_BASE = Base()
PLAYER_2_BASE.activated = False

#Initialize Player Bullets
player_1_bullets = pygame.sprite.Group()
player_2_bullets = pygame.sprite.Group()

#Initialize Explosions
explosions = pygame.sprite.Group()

#Initialize Instruction Variables
instructions_screen_ttl = TTL_DEFAULTS['INSTRUCTIONS_SCREEN']

#Initialize DogFighting Variables
dogfighting_pvp_active = False
dogfighting_base_creation_ttl = random.choice(range(TTL_DEFAULTS['BASE_CREATION_MIN'], TTL_DEFAULTS['BASE_CREATION_MAX']))
dogfighting_pvp_ready_ttl = TTL_DEFAULTS['READY']
dogfighting_pvp_set_ttl = TTL_DEFAULTS['SET']
dogfighting_pvp_fight_ttl = TTL_DEFAULTS['FIGHT']
dogfighting_pvp_fight_shown = False

# Set to Title Screen
reset_game_state()
initialize_title_screen()

######################################################################
# ***LESSON 2*** ESTABLISH THE GAME CLOCK
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
FRAME_COUNTER = 0

######################################################################
# MAIN GAME LOOP
# ***LESSON 1*** ***GAME LOOP***
######################################################################
while GAME_STATE['RUNNING']:
  ####################################################################
  # RESET THE SCREEN COLOR
  #
  # ***LESSON 6***
  # For the screen to be "wiped clean" so we can start fresh.  This
  # fill operation needs to take place.
  ####################################################################
  THE_SCREEN.fill(GAME_COLORS['DEEP_PURPLE'])

  ####################################################################
  # HANDLE EVENTS
  #
  # ***LESSON 5***
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
      if the_event.key == K_RCTRL:
        GAME_CONTROLS['right_ctrl'] = True
      if the_event.key == K_SLASH:
        GAME_CONTROLS['front_slash'] = True
      if the_event.key == K_LCTRL:
        GAME_CONTROLS['left_ctrl'] = True
      if the_event.key == K_RSHIFT:
        GAME_CONTROLS['right_shift'] = True
      if the_event.key == K_LSHIFT:
        GAME_CONTROLS['left_shift'] = True

      #If we are in TEST_MODE a bunch of additional keys not generally available are now activated for us to manage the
      #game to test various things out.  Helpful if we need to test a level and we don't want to have to play through
      #the game to get there (or even test out powerups / score / other things / and final boss battles!)
      #
      #Enter test mode by hitting the SHIFT+F12 key sequence
      if GAME_STATE['TEST_MODE']:
        if the_event.key == K_1 and (the_event.mod & KMOD_SHIFT):
          print(f"[TEST-MODE] [LAYER_1] MODE TOGGLED TO {(str(not GAME_STATE['LAYER_1'])).upper()}")
          GAME_STATE['LAYER_1'] = not GAME_STATE['LAYER_1']
        if the_event.key == K_2 and (the_event.mod & KMOD_SHIFT):
          print(f"[TEST-MODE] [LAYER_2] MODE TOGGLED TO {(str(not GAME_STATE['LAYER_2'])).upper()}")
          GAME_STATE['LAYER_2'] = not GAME_STATE['LAYER_2']
        if the_event.key == K_3 and (the_event.mod & KMOD_SHIFT):
          print(f"[TEST-MODE] [LAYER_3] MODE TOGGLED TO {(str(not GAME_STATE['LAYER_3'])).upper()}")
          GAME_STATE['LAYER_3'] = not GAME_STATE['LAYER_3']
        if the_event.key == K_4 and (the_event.mod & KMOD_SHIFT):
          print(f"[TEST-MODE] [LAYER_4] MODE TOGGLED TO {(str(not GAME_STATE['LAYER_4'])).upper()}")
          GAME_STATE['LAYER_4'] = not GAME_STATE['LAYER_4']
        if the_event.key == K_5 and (the_event.mod & KMOD_SHIFT):
          print(f"[TEST-MODE] [LAYER_5] MODE TOGGLED TO {(str(not GAME_STATE['LAYER_5'])).upper()}")
          GAME_STATE['LAYER_5'] = not GAME_STATE['LAYER_5']

        #t,g,b over for additional testing keystrokes
        if the_event.key == K_m and (the_event.mod & KMOD_SHIFT) and (the_event.mod & KMOD_CTRL):
          GAME_STATE['MULTIPLAYER'] = not GAME_STATE['MULTIPLAYER']

        #Alert testing
        #def create_alert(color, font, txt_1, txt_2, ttl, fadeout, fadeout_ttl):
        if the_event.key == K_p and (the_event.mod & KMOD_SHIFT) and (the_event.mod & KMOD_CTRL):
          destroy_alert()
        if the_event.key == K_t and (the_event.mod & KMOD_SHIFT) and (the_event.mod & KMOD_CTRL):
          create_alert(GAME_COLORS['SHMUP_YELLOW'], GAME_FONTS['KENNEY_MINI_SQUARE_96'], "SINGLE LINE TEST", "", 0, False, 0)
        if the_event.key == K_y and (the_event.mod & KMOD_SHIFT) and (the_event.mod & KMOD_CTRL):
          create_alert(GAME_COLORS['SHMUP_YELLOW'], "", "SINGLE LINE TEST FADEOUT", "", 2500, True, 1500)
        if the_event.key == K_u and (the_event.mod & KMOD_SHIFT) and (the_event.mod & KMOD_CTRL):
          create_alert(GAME_COLORS['SHMUP_YELLOW'], "", "MULTIPLE LINE", "ALERT TESTING", 2500, True, 1500)

        #Other Resets
        if the_event.key == K_r and (the_event.mod & KMOD_SHIFT) and (the_event.mod & KMOD_CTRL):
          reset_game_state()
        if the_event.key == K_g and (the_event.mod & KMOD_SHIFT) and (the_event.mod & KMOD_CTRL):
          reset_game_state()
          reset_screens()
          reset_transitions()
          reset_players()

        if the_event.key == K_F1:
          initialize_title_screen()
        if the_event.key == K_F2:
          initialize_game_mode_screen()
        if the_event.key == K_F3:
          initialize_instructions_screen()
        if the_event.key == K_F4:
          setup_for_dogfight_mode_quick_jump()
          initialize_dogfight_mode()
        if the_event.key == K_F5:
          initialize_mission_mode()
        if the_event.key == K_F6:
          initialize_arena_mode()
        if the_event.key == K_F7:
          initialize_game_over_screen()

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
          print(f"[TEST-MODE] [LAYER_ALL] ACTIVATED")
          GAME_STATE['LAYER_1'] = True
          GAME_STATE['LAYER_2'] = True
          GAME_STATE['LAYER_3'] = True
          GAME_STATE['LAYER_4'] = True
          GAME_STATE['LAYER_5'] = True
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
      if the_event.key == K_RCTRL:
        GAME_CONTROLS['right_ctrl'] = False
      if the_event.key == K_SLASH:
        GAME_CONTROLS['front_slash'] = False
      if the_event.key == K_LCTRL:
        GAME_CONTROLS['left_ctrl'] = False
      if the_event.key == K_RSHIFT:
        GAME_CONTROLS['right_shift'] = False
      if the_event.key == K_LSHIFT:
        GAME_CONTROLS['left_shift'] = False

    ##################################################################
    # HANDLE USER I/O (JOYSTICK)
    # 
    # ***LESSON 5a*** 
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
    #
    # We have other joysticks that we haven't programmed for yet
    ##################################################################
    
    # Handle hotplugging
    # This event will be generated when the program starts for every
    # joystick, filling up the list without needing to create them manually.
    if not GAME_CLI_ARGUMENTS.disable_joystick and the_event.type == pygame.JOYDEVICEADDED:
      if GAME_STATE['DEBUG_EVENTS'] or GAME_STATE['DEBUG_JOYSTICK_EVENTS']:
        print(f"[EVENT] [JOYSTICK-{the_event.device_index}] [CONNECT] ID:{the_event.device_index}")

      #Get the joystick that caused this event  
      joystick = pygame.joystick.Joystick(the_event.device_index)
      joystick_instance_id = joystick.get_instance_id()
      JOYSTICK_MAPPER[joystick_instance_id] = {'JOYSTICK': joystick, 'PLAYER': 0}

      if len(JOYSTICKS) < GAME_CONSTANTS['MAX_CONNECTED_JOYSTICKS']:
        if GAME_STATE['DEBUG_EVENTS'] or GAME_STATE['DEBUG_JOYSTICK_EVENTS']:
          print(f"[EVENT] [JOYSTICK-{joystick.get_instance_id()}] [CONNECT] ID:{joystick.get_instance_id()} - {joystick} - {joystick.get_name()} - Patching into JOYSTICK")
        #Check if we have player 1's Joystick attached, if not, add the connected joystick for that player
        if JOYSTICKS.get(1) == None:
          JOYSTICK_MAPPER[joystick_instance_id]['PLAYER'] = 1
          if GAME_STATE['DEBUG_EVENTS'] or GAME_STATE['DEBUG_JOYSTICK_EVENTS']:
            print(f"[EVENT] [JOYSTICK-{joystick.get_instance_id()}] [CONNECT] ID:{joystick.get_instance_id()} - {joystick} - {joystick.get_name()} - PLAYER 1 JOYSTICK CONNECTED")
        #Check if we have player 2's Joystick attached, if not, add the connected joystick for that player
        elif JOYSTICKS.get(2) == None:
          JOYSTICK_MAPPER[joystick_instance_id]['PLAYER'] = 2
          if GAME_STATE['DEBUG_EVENTS'] or GAME_STATE['DEBUG_JOYSTICK_EVENTS']:
            print(f"[EVENT] [JOYSTICK-{joystick.get_instance_id()}] [CONNECT] ID:{joystick.get_instance_id()} - {joystick} - {joystick.get_name()} - PLAYER 2 JOYSTICK CONNECTED")

        #Patch the joystick into the old code
        JOYSTICKS[JOYSTICK_MAPPER[joystick_instance_id]['PLAYER']] = joystick

        if GAME_STATE['DEBUG_EVENTS'] or GAME_STATE['DEBUG_JOYSTICK_EVENTS']:
          print(f"[EVENT] [JOYSTICK-{joystick.get_instance_id()}] [CONNECT] ID:{joystick.get_instance_id()} - {joystick} - {joystick.get_name()} - PATCHED AS {JOYSTICK_MAPPER[joystick_instance_id]['PLAYER']}")

    if not GAME_CLI_ARGUMENTS.disable_joystick and the_event.type == pygame.JOYDEVICEREMOVED:
      if GAME_STATE['DEBUG_EVENTS'] or GAME_STATE['DEBUG_JOYSTICK_EVENTS']:
        print(f"[EVENT] [JOYSTICK-{the_event.instance_id}] [DISCONNECT] ID:{the_event.instance_id} FOR PLAYER {JOYSTICK_MAPPER[the_event.instance_id]['PLAYER']}")
      
      joystick_instance_id = the_event.instance_id

      if JOYSTICK_MAPPER.get(joystick_instance_id) != None:
        del JOYSTICKS[JOYSTICK_MAPPER[joystick_instance_id]['PLAYER']]
        del JOYSTICK_MAPPER[joystick_instance_id]

      #Check if we need to do any kind of remapping for additional controllers that may have been attached (Maybe? - or we just force it to the next one added, which may already happen)

    if not GAME_CLI_ARGUMENTS.disable_joystick and len(JOYSTICKS) <= GAME_CONSTANTS['MAX_CONNECTED_JOYSTICKS'] and (the_event.type == pygame.JOYBUTTONDOWN or the_event.type == pygame.JOYBUTTONUP or the_event.type == pygame.JOYAXISMOTION or the_event.type == pygame.JOYHATMOTION):
      if GAME_STATE['DEBUG_EVENTS']:
          print(f"[EVENT] [JOYSTICK-{the_event.instance_id}] [EVENT_PROCESSING]")
      
      controller_instance_id = the_event.instance_id
      actual_player_controller = JOYSTICK_MAPPER[controller_instance_id]
      actual_player = actual_player_controller['PLAYER']

      if GAME_STATE['DEBUG_EVENTS']:
          print(f"[EVENT] [JOYSTICK-{controller_instance_id}] [MAPPING] ")

      if the_event.type == pygame.JOYBUTTONDOWN:
        if GAME_STATE['DEBUG_EVENTS']:
          print(f"[EVENT] [JOYSTICK-{controller_instance_id}] [BUTTONDOWN] {the_event.button}")

        if JOYSTICKS[actual_player].get_name() == 'Xbox 360 Controller' or JOYSTICKS[actual_player].get_name() == 'PowerA NSW Wired controller':
          if the_event.button == 0:
            GAME_CONTROLS[f'JOYSTICK_{actual_player}']['controller_a'] = True
          if the_event.button == 1:
            GAME_CONTROLS[f'JOYSTICK_{actual_player}']['controller_b'] = True
          if the_event.button == 2:
            GAME_CONTROLS[f'JOYSTICK_{actual_player}']['controller_x'] = True
          if the_event.button == 3:
            GAME_CONTROLS[f'JOYSTICK_{actual_player}']['controller_y'] = True

        if JOYSTICKS[actual_player].get_name() == 'PowerA NSW Wired controller':
          if the_event.button == 11:
            GAME_CONTROLS[f'JOYSTICK_{actual_player}']['dpad_up'] = True
          if the_event.button == 12:
            GAME_CONTROLS[f'JOYSTICK_{actual_player}']['dpad_down'] = True
          if the_event.button == 13:
            GAME_CONTROLS[f'JOYSTICK_{actual_player}']['dpad_left'] = True
          if the_event.button == 14:
            GAME_CONTROLS[f'JOYSTICK_{actual_player}']['dpad_right'] = True

      if the_event.type == pygame.JOYBUTTONUP:
        if GAME_STATE['DEBUG_EVENTS']:
          print(f"[EVENT] [JOYSTICK-{controller_instance_id}] [BUTTONUP] {the_event.button}")

        if JOYSTICKS[actual_player].get_name() == 'Xbox 360 Controller' or JOYSTICKS[actual_player].get_name() == 'PowerA NSW Wired controller':
          if the_event.button == 0:
            GAME_CONTROLS[f'JOYSTICK_{actual_player}']['controller_a'] = False
          if the_event.button == 1:
            GAME_CONTROLS[f'JOYSTICK_{actual_player}']['controller_b'] = False
          if the_event.button == 2:
            GAME_CONTROLS[f'JOYSTICK_{actual_player}']['controller_x'] = False
          if the_event.button == 3:
            GAME_CONTROLS[f'JOYSTICK_{actual_player}']['controller_y'] = False

        if JOYSTICKS[actual_player].get_name() == 'PowerA NSW Wired controller':
          if the_event.button == 11:
            GAME_CONTROLS[f'JOYSTICK_{actual_player}']['dpad_up'] = False
          if the_event.button == 12:
            GAME_CONTROLS[f'JOYSTICK_{actual_player}']['dpad_down'] = False
          if the_event.button == 13:
            GAME_CONTROLS[f'JOYSTICK_{actual_player}']['dpad_left'] = False
          if the_event.button == 14:
            GAME_CONTROLS[f'JOYSTICK_{actual_player}']['dpad_right'] = False

      if the_event.type == pygame.JOYAXISMOTION:
        if GAME_STATE['DEBUG_EVENTS']:
          print(f"[EVENT] [JOYSTICK-{actual_player}] [AXISMOTION] {the_event.axis} value {the_event.value}")
        GAME_CONTROLS[f'JOYSTICK_{actual_player}'][f'axis_{the_event.axis}'] = the_event.value

      if the_event.type == pygame.JOYHATMOTION:
        if GAME_STATE['DEBUG_EVENTS']:
          print(f"[EVENT] [JOYSTICK-{actual_player}] [HATMOTION] ({the_event.value[0]}, {the_event.value[1]})")

        if the_event.value[0] == 0:
          GAME_CONTROLS[f'JOYSTICK_{actual_player}']['hat_left'] = False
          GAME_CONTROLS[f'JOYSTICK_{actual_player}']['hat_right'] = False
        elif the_event.value[0] == 1:
          GAME_CONTROLS[f'JOYSTICK_{actual_player}']['hat_left'] = False
          GAME_CONTROLS[f'JOYSTICK_{actual_player}']['hat_right'] = True
        elif the_event.value[0] == -1:
          GAME_CONTROLS[f'JOYSTICK_{actual_player}']['hat_left'] = True
          GAME_CONTROLS[f'JOYSTICK_{actual_player}']['hat_right'] = False
        if the_event.value[1] == 0:
          GAME_CONTROLS[f'JOYSTICK_{actual_player}']['hat_up'] = False
          GAME_CONTROLS[f'JOYSTICK_{actual_player}']['hat_down'] = False
        elif the_event.value[1] == 1:
          GAME_CONTROLS[f'JOYSTICK_{actual_player}']['hat_up'] = True
          GAME_CONTROLS[f'JOYSTICK_{actual_player}']['hat_down'] = False
        elif the_event.value[1] == -1:
          GAME_CONTROLS[f'JOYSTICK_{actual_player}']['hat_up'] = False
          GAME_CONTROLS[f'JOYSTICK_{actual_player}']['hat_down'] = True

    ###################################
    #
    # Apply I/O to actual Game Controls
    # Not sure why this won't work when it's pulled out of the i/o loop
    # 
    # ***LESSON 5b***
    # Note here that we have slightly different controls for single player mode and multiplayer mode.
    ###################################
    directional_axis_tolleration = 0.50

    if not GAME_STATE['MULTIPLAYER']:
      GAME_CONTROLS['PLAYER_1']['UP'] = GAME_CONTROLS['w'] or GAME_CONTROLS['up_arrow'] or GAME_CONTROLS['JOYSTICK_1']['hat_up'] or GAME_CONTROLS['JOYSTICK_1']['dpad_up'] or GAME_CONTROLS['JOYSTICK_1']['axis_1'] < -directional_axis_tolleration or GAME_CONTROLS['JOYSTICK_1']['axis_3'] < -directional_axis_tolleration or GAME_CONTROLS['JOYSTICK_2']['hat_up'] or GAME_CONTROLS['JOYSTICK_2']['dpad_up'] or GAME_CONTROLS['JOYSTICK_2']['axis_1'] < -directional_axis_tolleration or GAME_CONTROLS['JOYSTICK_2']['axis_3'] < -directional_axis_tolleration
      GAME_CONTROLS['PLAYER_1']['LEFT'] = GAME_CONTROLS['a'] or GAME_CONTROLS['left_arrow'] or GAME_CONTROLS['JOYSTICK_1']['hat_left'] or GAME_CONTROLS['JOYSTICK_1']['dpad_left'] or GAME_CONTROLS['JOYSTICK_1']['axis_0'] < -directional_axis_tolleration or GAME_CONTROLS['JOYSTICK_1']['axis_2'] < -directional_axis_tolleration  or GAME_CONTROLS['JOYSTICK_2']['hat_left'] or GAME_CONTROLS['JOYSTICK_2']['dpad_left'] or GAME_CONTROLS['JOYSTICK_2']['axis_0'] < -directional_axis_tolleration or GAME_CONTROLS['JOYSTICK_2']['axis_2'] < -directional_axis_tolleration
      GAME_CONTROLS['PLAYER_1']['DOWN'] = GAME_CONTROLS['s'] or GAME_CONTROLS['down_arrow'] or GAME_CONTROLS['JOYSTICK_1']['hat_down'] or GAME_CONTROLS['JOYSTICK_1']['dpad_down'] or GAME_CONTROLS['JOYSTICK_1']['axis_1'] > directional_axis_tolleration or GAME_CONTROLS['JOYSTICK_1']['axis_3'] > directional_axis_tolleration  or GAME_CONTROLS['JOYSTICK_2']['hat_down'] or GAME_CONTROLS['JOYSTICK_2']['dpad_down'] or GAME_CONTROLS['JOYSTICK_2']['axis_1'] > directional_axis_tolleration or GAME_CONTROLS['JOYSTICK_2']['axis_3'] > directional_axis_tolleration
      GAME_CONTROLS['PLAYER_1']['RIGHT'] = GAME_CONTROLS['d'] or GAME_CONTROLS['right_arrow'] or GAME_CONTROLS['JOYSTICK_1']['hat_right'] or GAME_CONTROLS['JOYSTICK_1']['dpad_right'] or GAME_CONTROLS['JOYSTICK_1']['axis_0'] > directional_axis_tolleration or GAME_CONTROLS['JOYSTICK_1']['axis_2'] > directional_axis_tolleration  or GAME_CONTROLS['JOYSTICK_2']['hat_right'] or GAME_CONTROLS['JOYSTICK_2']['dpad_right'] or GAME_CONTROLS['JOYSTICK_2']['axis_0'] > directional_axis_tolleration or GAME_CONTROLS['JOYSTICK_2']['axis_2'] > directional_axis_tolleration

      GAME_CONTROLS['PLAYER_1']['GREEN'] = GAME_CONTROLS['space_bar'] or GAME_CONTROLS['right_shift'] or GAME_CONTROLS['left_shift'] or GAME_CONTROLS['JOYSTICK_1']['controller_a'] or GAME_CONTROLS['JOYSTICK_2']['controller_a']
      GAME_CONTROLS['PLAYER_1']['RED'] = GAME_CONTROLS['left_ctrl'] or GAME_CONTROLS['right_ctrl'] or GAME_CONTROLS['front_slash'] or GAME_CONTROLS['JOYSTICK_1']['controller_b'] or GAME_CONTROLS['JOYSTICK_2']['controller_b']
      GAME_CONTROLS['PLAYER_1']['BLUE'] = GAME_CONTROLS['left_alt'] or GAME_CONTROLS['right_alt'] or GAME_CONTROLS['JOYSTICK_1']['controller_x'] or GAME_CONTROLS['JOYSTICK_2']['controller_x']
      GAME_CONTROLS['PLAYER_1']['YELLOW'] = GAME_CONTROLS['JOYSTICK_1']['controller_y'] or GAME_CONTROLS['JOYSTICK_2']['controller_y']
    else:
      GAME_CONTROLS['PLAYER_1']['UP'] = GAME_CONTROLS['w'] or GAME_CONTROLS['JOYSTICK_1']['hat_up'] or GAME_CONTROLS['JOYSTICK_1']['dpad_up'] or GAME_CONTROLS['JOYSTICK_1']['axis_1'] < -directional_axis_tolleration or GAME_CONTROLS['JOYSTICK_1']['axis_3'] < -directional_axis_tolleration
      GAME_CONTROLS['PLAYER_1']['LEFT'] = GAME_CONTROLS['a'] or GAME_CONTROLS['JOYSTICK_1']['hat_left'] or GAME_CONTROLS['JOYSTICK_1']['dpad_left'] or GAME_CONTROLS['JOYSTICK_1']['axis_0'] < -directional_axis_tolleration or GAME_CONTROLS['JOYSTICK_1']['axis_2'] < -directional_axis_tolleration
      GAME_CONTROLS['PLAYER_1']['DOWN'] = GAME_CONTROLS['s'] or GAME_CONTROLS['JOYSTICK_1']['hat_down'] or GAME_CONTROLS['JOYSTICK_1']['dpad_down'] or GAME_CONTROLS['JOYSTICK_1']['axis_1'] > directional_axis_tolleration or GAME_CONTROLS['JOYSTICK_1']['axis_3'] > directional_axis_tolleration
      GAME_CONTROLS['PLAYER_1']['RIGHT'] = GAME_CONTROLS['d'] or GAME_CONTROLS['JOYSTICK_1']['hat_right'] or GAME_CONTROLS['JOYSTICK_1']['dpad_right'] or GAME_CONTROLS['JOYSTICK_1']['axis_0'] > directional_axis_tolleration or GAME_CONTROLS['JOYSTICK_1']['axis_2'] > directional_axis_tolleration

      GAME_CONTROLS['PLAYER_1']['GREEN'] = GAME_CONTROLS['left_shift'] or GAME_CONTROLS['JOYSTICK_1']['controller_a']
      GAME_CONTROLS['PLAYER_1']['RED'] = GAME_CONTROLS['left_ctrl'] or GAME_CONTROLS['JOYSTICK_1']['controller_b']
      GAME_CONTROLS['PLAYER_1']['BLUE'] = GAME_CONTROLS['left_alt'] or GAME_CONTROLS['JOYSTICK_1']['controller_x']
      GAME_CONTROLS['PLAYER_1']['YELLOW'] = GAME_CONTROLS['JOYSTICK_1']['controller_y']

      GAME_CONTROLS['PLAYER_2']['UP'] = GAME_CONTROLS['up_arrow'] or GAME_CONTROLS['JOYSTICK_2']['hat_up'] or GAME_CONTROLS['JOYSTICK_2']['dpad_up'] or GAME_CONTROLS['JOYSTICK_2']['axis_1'] < -directional_axis_tolleration or GAME_CONTROLS['JOYSTICK_2']['axis_3'] < -directional_axis_tolleration
      GAME_CONTROLS['PLAYER_2']['LEFT'] = GAME_CONTROLS['left_arrow'] or GAME_CONTROLS['JOYSTICK_2']['hat_left'] or GAME_CONTROLS['JOYSTICK_2']['dpad_left'] or GAME_CONTROLS['JOYSTICK_2']['axis_0'] < -directional_axis_tolleration or GAME_CONTROLS['JOYSTICK_2']['axis_2'] < -directional_axis_tolleration
      GAME_CONTROLS['PLAYER_2']['DOWN'] = GAME_CONTROLS['down_arrow'] or GAME_CONTROLS['JOYSTICK_2']['hat_down'] or GAME_CONTROLS['JOYSTICK_2']['dpad_down'] or GAME_CONTROLS['JOYSTICK_2']['axis_1'] > directional_axis_tolleration or GAME_CONTROLS['JOYSTICK_2']['axis_3'] > directional_axis_tolleration
      GAME_CONTROLS['PLAYER_2']['RIGHT'] = GAME_CONTROLS['right_arrow'] or GAME_CONTROLS['JOYSTICK_2']['hat_right'] or GAME_CONTROLS['JOYSTICK_2']['dpad_right'] or GAME_CONTROLS['JOYSTICK_2']['axis_0'] > directional_axis_tolleration or GAME_CONTROLS['JOYSTICK_2']['axis_2'] > directional_axis_tolleration

      GAME_CONTROLS['PLAYER_2']['GREEN'] = GAME_CONTROLS['right_shift'] or GAME_CONTROLS['JOYSTICK_2']['controller_a']
      GAME_CONTROLS['PLAYER_2']['RED'] = GAME_CONTROLS['right_ctrl'] or GAME_CONTROLS['front_slash'] or GAME_CONTROLS['JOYSTICK_2']['controller_b']
      GAME_CONTROLS['PLAYER_2']['BLUE'] = GAME_CONTROLS['right_alt'] or GAME_CONTROLS['JOYSTICK_2']['controller_x']
      GAME_CONTROLS['PLAYER_2']['YELLOW'] = GAME_CONTROLS['JOYSTICK_2']['controller_y']

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
  # *** LESSON ***
  # 
  # Out of the I/O section of the game loop, now we're going to see
  # where we are at in terms of game state to figure out what to do
  #
  #
  #
  #
  #
  ####################################################################

  total_sprite_objects = 0
  total_map_tiles = 0

  ####################################################################
  # TITLE_SCREEN - If we're at the title screen, draw that screen
  #
  ####################################################################
  if GAME_STATE['TITLE_SCREEN']:
    
    press_start_blink_ttl = press_start_blink_ttl - ELAPSED_MS
    if press_start_blink_ttl < 1:
      press_start_blink_ttl = TTL_DEFAULTS['PRESS_START_BLINK']
      if press_start_color == GAME_COLORS['SHMUP_ROYAL_PURPLE']:
        press_start_color = GAME_COLORS['ALMOST_BLACK']
      else:
        press_start_color = GAME_COLORS['SHMUP_ROYAL_PURPLE']

    potozniak_electronics = GAME_FONTS['KENNEY_MINI_SQUARE_64'].render(f"POTOZNIAK ELECTRONICS", True, GAME_COLORS['SHMUP_BLUE'])
    THE_SCREEN.blit(potozniak_electronics, potozniak_electronics.get_rect(midtop = (GAME_CONSTANTS['SCREEN_WIDTH'] / 2, GAME_CONSTANTS['SCREEN_HEIGHT'] / 8)))
    presents = GAME_FONTS['KENNEY_MINI_SQUARE_64'].render(f"PRESENTS", True, GAME_COLORS['SHMUP_BLUE'])
    THE_SCREEN.blit(presents, presents.get_rect(midtop = (GAME_CONSTANTS['SCREEN_WIDTH'] / 2, (GAME_CONSTANTS['SCREEN_HEIGHT'] / 8) + (GAME_CONSTANTS['SQUARE_SIZE'] * 2))))

    game_title = GAME_FONTS['KENNEY_MINI_SQUARE_64'].render(f"Super Sky Squadron II:", True, GAME_COLORS['SHMUP_RED'])
    THE_SCREEN.blit(game_title, game_title.get_rect(midtop = (GAME_CONSTANTS['SCREEN_WIDTH'] / 2, GAME_CONSTANTS['SCREEN_HEIGHT'] / 8 * 3)))
    game_title_2 = GAME_FONTS['KENNEY_MINI_SQUARE_64'].render(f"The Flying Ace Follies", True, GAME_COLORS['SHMUP_ORANGE'])
    THE_SCREEN.blit(game_title_2, game_title_2.get_rect(midtop = (GAME_CONSTANTS['SCREEN_WIDTH'] / 2, (GAME_CONSTANTS['SCREEN_HEIGHT'] / 8 * 3) + (GAME_CONSTANTS['SQUARE_SIZE'] * 2))))

    red_plane = pygame.transform.rotozoom(GAME_SURFACES['PIXEL_SHMUP_SHIPS']['RED_A_FIGHTER'], 0, 2)
    THE_SCREEN.blit(red_plane, red_plane.get_rect(center=(GAME_CONSTANTS['SCREEN_WIDTH'] / 4 + GAME_CONSTANTS['SQUARE_SIZE'] / 2, GAME_CONSTANTS['SCREEN_HEIGHT'] / 8 * 5.5 + GAME_CONSTANTS['SQUARE_SIZE'])))

    green_plane = pygame.transform.rotozoom(GAME_SURFACES['PIXEL_SHMUP_SHIPS']['GREEN_A_FIGHTER'], 270, 2)
    THE_SCREEN.blit(green_plane, green_plane.get_rect(center=(GAME_CONSTANTS['SCREEN_WIDTH'] / 4 - 3.5 * GAME_CONSTANTS['SQUARE_SIZE'], GAME_CONSTANTS['SCREEN_HEIGHT'] / 8 * 5.5 + GAME_CONSTANTS['SQUARE_SIZE'])))

    blue_plane = pygame.transform.rotozoom(GAME_SURFACES['PIXEL_SHMUP_SHIPS']['BLUE_A_FIGHTER'], 0, 2)
    THE_SCREEN.blit(blue_plane, blue_plane.get_rect(center=(GAME_CONSTANTS['SCREEN_WIDTH'] / 4 * 3 - GAME_CONSTANTS['SQUARE_SIZE'] / 2, GAME_CONSTANTS['SCREEN_HEIGHT'] / 8 * 5.5 + GAME_CONSTANTS['SQUARE_SIZE'])))

    yellow_plane = pygame.transform.rotozoom(GAME_SURFACES['PIXEL_SHMUP_SHIPS']['YELLOW_A_FIGHTER'], 90, 2)
    THE_SCREEN.blit(yellow_plane, yellow_plane.get_rect(center=(GAME_CONSTANTS['SCREEN_WIDTH'] / 4 * 3 + 3.5 * GAME_CONSTANTS['SQUARE_SIZE'], GAME_CONSTANTS['SCREEN_HEIGHT'] / 8 * 5.5 + GAME_CONSTANTS['SQUARE_SIZE'])))

    if GAME_STATE['TRANSITION_TO_GAME_MODE_SCREEN']:
      press_start_color = GAME_COLORS['SHMUP_WHITE']
      
    press_start = GAME_FONTS['KENNEY_MINI_SQUARE_64'].render(f"PRESS START", True, press_start_color)

    if GAME_STATE['TRANSITION_TO_GAME_MODE_SCREEN']:
      press_start.set_alpha(int((GAME_STATE_TRANSITION_TTL['TRANSITION_TO_GAME_MODE_SCREEN'] / TTL_DEFAULTS['TRANSITION_TO_GAME_MODE_SCREEN']) * 255))
    
    THE_SCREEN.blit(press_start, press_start.get_rect(midtop = (GAME_CONSTANTS['SCREEN_WIDTH'] / 2, GAME_CONSTANTS['SCREEN_HEIGHT'] / 8 * 5.5 - GAME_CONSTANTS['SQUARE_SIZE'] / 2)))

    #Evaluate pressing start and then transitioning to the next state of the game after TTL expires
    if not GAME_STATE['TRANSITION_TO_GAME_MODE_SCREEN'] and (GAME_CONTROLS['PLAYER_1']['GREEN'] or GAME_CONTROLS['PLAYER_1']['RED'] or GAME_CONTROLS['PLAYER_1']['BLUE'] or GAME_CONTROLS['PLAYER_1']['YELLOW'] or GAME_CONTROLS['PLAYER_2']['GREEN'] or GAME_CONTROLS['PLAYER_2']['RED'] or GAME_CONTROLS['PLAYER_2']['BLUE'] or GAME_CONTROLS['PLAYER_2']['YELLOW']):
      if SOUND_EFFECT_SELECT != None:
        SOUND_EFFECT_SELECT.stop()
        SOUND_EFFECT_SELECT.set_volume(1.00)
        SOUND_EFFECT_SELECT.play(loops=0)
      GAME_STATE['TRANSITION_TO_GAME_MODE_SCREEN'] = True
    if GAME_STATE['TRANSITION_TO_GAME_MODE_SCREEN']:
      GAME_STATE_TRANSITION_TTL['TRANSITION_TO_GAME_MODE_SCREEN'] = GAME_STATE_TRANSITION_TTL['TRANSITION_TO_GAME_MODE_SCREEN'] - ELAPSED_MS
      if GAME_STATE_TRANSITION_TTL['TRANSITION_TO_GAME_MODE_SCREEN'] <= 0:
        initialize_game_mode_screen()

  ####################################################################
  # GAME_MODE_SCREEN - If we're at the game mode screen, draw that screen
  #
  ####################################################################
  if GAME_STATE['GAME_MODE_SCREEN']:
    if not GAME_STATE['TRANSITION_TO_INSTRUCTIONS_SCREEN']:
      ## UPDATE THE GAME MODE BASED ON CONTROLS
      if GAME_CONTROLS['PLAYER_1']['DOWN']:
        GAME_CONTROLS['PLAYER_1']['DOWN'] = False
        if SOUND_EFFECT_UI_MOVE != None:
          SOUND_EFFECT_UI_MOVE.stop()
          SOUND_EFFECT_UI_MOVE.set_volume(1.00)
          SOUND_EFFECT_UI_MOVE.play(loops=0)
        if GAME_MODE_OPTIONS['PLAYERS']:
          GAME_MODE_OPTIONS['PLAYERS'] = False
          GAME_MODE_OPTIONS['GAME_MODE'] = True
          GAME_MODE_OPTIONS['STARTING_LIVES'] = False
          GAME_MODE_OPTIONS['START_GAME'] = False
        elif GAME_MODE_OPTIONS['GAME_MODE']:
          GAME_MODE_OPTIONS['PLAYERS'] = False
          GAME_MODE_OPTIONS['GAME_MODE'] = False
          if GAME_MODE_OPTIONS['DOGFIGHT']:
            GAME_MODE_OPTIONS['STARTING_LIVES'] = True
            GAME_MODE_OPTIONS['START_GAME'] = False
          else:
            GAME_MODE_OPTIONS['STARTING_LIVES'] = False
            GAME_MODE_OPTIONS['START_GAME'] = True
        elif GAME_MODE_OPTIONS['STARTING_LIVES']:
          GAME_MODE_OPTIONS['PLAYERS'] = False
          GAME_MODE_OPTIONS['GAME_MODE'] = False
          GAME_MODE_OPTIONS['STARTING_LIVES'] = False
          GAME_MODE_OPTIONS['START_GAME'] = True
        elif GAME_MODE_OPTIONS['START_GAME']:
          GAME_MODE_OPTIONS['PLAYERS'] = True
          GAME_MODE_OPTIONS['GAME_MODE'] = False
          GAME_MODE_OPTIONS['STARTING_LIVES'] = False
          GAME_MODE_OPTIONS['START_GAME'] = False

      if GAME_CONTROLS['PLAYER_1']['UP']:
        GAME_CONTROLS['PLAYER_1']['UP'] = False
        if SOUND_EFFECT_UI_MOVE != None:
          SOUND_EFFECT_UI_MOVE.stop()
          SOUND_EFFECT_UI_MOVE.set_volume(1.00)
          SOUND_EFFECT_UI_MOVE.play(loops=0)
        if GAME_MODE_OPTIONS['PLAYERS']:
          GAME_MODE_OPTIONS['PLAYERS'] = False
          GAME_MODE_OPTIONS['GAME_MODE'] = False
          GAME_MODE_OPTIONS['STARTING_LIVES'] = False
          GAME_MODE_OPTIONS['START_GAME'] = True
        elif GAME_MODE_OPTIONS['GAME_MODE']:
          GAME_MODE_OPTIONS['PLAYERS'] = True
          GAME_MODE_OPTIONS['GAME_MODE'] = False
          GAME_MODE_OPTIONS['STARTING_LIVES'] = False
          GAME_MODE_OPTIONS['START_GAME'] = False
        elif GAME_MODE_OPTIONS['STARTING_LIVES']:
          GAME_MODE_OPTIONS['PLAYERS'] = False
          GAME_MODE_OPTIONS['GAME_MODE'] = True
          GAME_MODE_OPTIONS['STARTING_LIVES'] = False
          GAME_MODE_OPTIONS['START_GAME'] = False
        elif GAME_MODE_OPTIONS['START_GAME']:
          GAME_MODE_OPTIONS['PLAYERS'] = False
          if GAME_MODE_OPTIONS['DOGFIGHT']:
            GAME_MODE_OPTIONS['GAME_MODE'] = False
            GAME_MODE_OPTIONS['STARTING_LIVES'] = True
          else:
            GAME_MODE_OPTIONS['GAME_MODE'] = True
            GAME_MODE_OPTIONS['STARTING_LIVES'] = False
          GAME_MODE_OPTIONS['START_GAME'] = False

      if GAME_CONTROLS['PLAYER_1']['RIGHT']:
        GAME_CONTROLS['PLAYER_1']['RIGHT'] = False
        if SOUND_EFFECT_UI_MOVE != None:
          SOUND_EFFECT_UI_MOVE.stop()
          SOUND_EFFECT_UI_MOVE.set_volume(1.00)
          SOUND_EFFECT_UI_MOVE.play(loops=0)
        if GAME_MODE_OPTIONS['PLAYERS']:
          if GAME_MODE_OPTIONS['ONE_PLAYER']:
            GAME_MODE_OPTIONS['ONE_PLAYER'] = False
            GAME_MODE_OPTIONS['TWO_PLAYERS'] = True
          elif GAME_MODE_OPTIONS['TWO_PLAYERS']:
            GAME_MODE_OPTIONS['ONE_PLAYER'] = True
            GAME_MODE_OPTIONS['TWO_PLAYERS'] = False
            if GAME_MODE_OPTIONS['DOGFIGHT']:
              GAME_MODE_OPTIONS['DOGFIGHT'] = False
              GAME_MODE_OPTIONS['MISSION'] = True
        if GAME_MODE_OPTIONS['GAME_MODE']:
          if GAME_MODE_OPTIONS['MISSION']:
            GAME_MODE_OPTIONS['MISSION'] = False
            GAME_MODE_OPTIONS['ARENA'] = True
            GAME_MODE_OPTIONS['DOGFIGHT'] = False
          elif GAME_MODE_OPTIONS['ARENA']:
            if GAME_MODE_OPTIONS['ONE_PLAYER']:
              GAME_MODE_OPTIONS['MISSION'] = True
            else:
              GAME_MODE_OPTIONS['MISSION'] = False
            GAME_MODE_OPTIONS['ARENA'] = False
            if GAME_MODE_OPTIONS['TWO_PLAYERS']:
              GAME_MODE_OPTIONS['DOGFIGHT'] = True
            else:
              GAME_MODE_OPTIONS['DOGFIGHT'] = False
          elif GAME_MODE_OPTIONS['DOGFIGHT']:
            GAME_MODE_OPTIONS['MISSION'] = True
            GAME_MODE_OPTIONS['ARENA'] = False
            GAME_MODE_OPTIONS['DOGFIGHT'] = False
        if GAME_MODE_OPTIONS['STARTING_LIVES']:
          GAME_MODE_OPTIONS['LIVES_COUNT'] = GAME_MODE_OPTIONS['LIVES_COUNT'] + 1
          if GAME_MODE_OPTIONS['LIVES_COUNT'] > 5:
            GAME_MODE_OPTIONS['LIVES_COUNT'] = 1

      if GAME_CONTROLS['PLAYER_1']['LEFT']:
        GAME_CONTROLS['PLAYER_1']['LEFT'] = False
        if SOUND_EFFECT_UI_MOVE != None:
          SOUND_EFFECT_UI_MOVE.stop()
          SOUND_EFFECT_UI_MOVE.set_volume(1.00)
          SOUND_EFFECT_UI_MOVE.play(loops=0)
        if GAME_MODE_OPTIONS['PLAYERS']:
          if GAME_MODE_OPTIONS['ONE_PLAYER']:
            GAME_MODE_OPTIONS['ONE_PLAYER'] = False
            GAME_MODE_OPTIONS['TWO_PLAYERS'] = True
          elif GAME_MODE_OPTIONS['TWO_PLAYERS']:
            GAME_MODE_OPTIONS['ONE_PLAYER'] = True
            GAME_MODE_OPTIONS['TWO_PLAYERS'] = False
            if GAME_MODE_OPTIONS['DOGFIGHT']:
              GAME_MODE_OPTIONS['DOGFIGHT'] = False
              GAME_MODE_OPTIONS['MISSION'] = True
        if GAME_MODE_OPTIONS['GAME_MODE']:
          if GAME_MODE_OPTIONS['MISSION']:
            GAME_MODE_OPTIONS['MISSION'] = False
            if GAME_MODE_OPTIONS['ONE_PLAYER']:
              GAME_MODE_OPTIONS['ARENA'] = True
            else:
              GAME_MODE_OPTIONS['ARENA'] = False
            if GAME_MODE_OPTIONS['TWO_PLAYERS']:
              GAME_MODE_OPTIONS['DOGFIGHT'] = True
            else:
              GAME_MODE_OPTIONS['DOGFIGHT'] = False
          elif GAME_MODE_OPTIONS['ARENA']:
            GAME_MODE_OPTIONS['MISSION'] = True
            GAME_MODE_OPTIONS['ARENA'] = False
            GAME_MODE_OPTIONS['DOGFIGHT'] = False
          elif GAME_MODE_OPTIONS['DOGFIGHT']:
            GAME_MODE_OPTIONS['MISSION'] = False
            GAME_MODE_OPTIONS['ARENA'] = True
            GAME_MODE_OPTIONS['DOGFIGHT'] = False
        if GAME_MODE_OPTIONS['STARTING_LIVES']:
          GAME_MODE_OPTIONS['LIVES_COUNT'] = GAME_MODE_OPTIONS['LIVES_COUNT'] - 1
          if GAME_MODE_OPTIONS['LIVES_COUNT'] < 1:
            GAME_MODE_OPTIONS['LIVES_COUNT'] = 5

    players = GAME_FONTS['KENNEY_MINI_SQUARE_48'].render(f"PLAYERS:", True, GAME_COLORS['ALMOST_BLACK'])
    if GAME_MODE_OPTIONS['PLAYERS']:
      players = GAME_FONTS['KENNEY_MINI_SQUARE_48'].render(f"PLAYERS:", True, GAME_COLORS['SHMUP_ORANGE'])
    THE_SCREEN.blit(players, players.get_rect(topright = (GAME_CONSTANTS['SQUARE_SIZE'] * 15, GAME_CONSTANTS['SQUARE_SIZE'] * 2.5)))

    red_plane = pygame.transform.rotozoom(GAME_SURFACES['PIXEL_SHMUP_SHIPS']['RED_A_FIGHTER_GRAY'], 0, 2)
    if GAME_MODE_OPTIONS['ONE_PLAYER']:
      red_plane = pygame.transform.rotozoom(GAME_SURFACES['PIXEL_SHMUP_SHIPS']['RED_A_FIGHTER'], 0, 2)
    THE_SCREEN.blit(red_plane, red_plane.get_rect(center=(GAME_CONSTANTS['SQUARE_SIZE'] * 19.5, GAME_CONSTANTS['SQUARE_SIZE'] * 3.5)))

    red_plane_multiplayer = pygame.transform.rotozoom(GAME_SURFACES['PIXEL_SHMUP_SHIPS']['RED_A_FIGHTER_GRAY'], 0, 2)
    blue_plane_multiplayer = pygame.transform.rotozoom(GAME_SURFACES['PIXEL_SHMUP_SHIPS']['BLUE_A_FIGHTER_GRAY'], 0, 2)
    if GAME_MODE_OPTIONS['TWO_PLAYERS']:
      red_plane_multiplayer = pygame.transform.rotozoom(GAME_SURFACES['PIXEL_SHMUP_SHIPS']['RED_A_FIGHTER'], 0, 2)
      blue_plane_multiplayer = pygame.transform.rotozoom(GAME_SURFACES['PIXEL_SHMUP_SHIPS']['BLUE_A_FIGHTER'], 0, 2)

    THE_SCREEN.blit(red_plane_multiplayer, red_plane_multiplayer.get_rect(center=(GAME_CONSTANTS['SQUARE_SIZE'] * 24.5, GAME_CONSTANTS['SQUARE_SIZE'] * 3.5)))
    THE_SCREEN.blit(blue_plane_multiplayer, blue_plane_multiplayer.get_rect(center=(GAME_CONSTANTS['SQUARE_SIZE'] * 27, GAME_CONSTANTS['SQUARE_SIZE'] * 3.5)))

    game_mode = GAME_FONTS['KENNEY_MINI_SQUARE_48'].render(f"GAME MODE:", True, GAME_COLORS['ALMOST_BLACK'])
    if GAME_MODE_OPTIONS['GAME_MODE']:
      game_mode = GAME_FONTS['KENNEY_MINI_SQUARE_48'].render(f"GAME MODE:", True, GAME_COLORS['SHMUP_ORANGE'])
    THE_SCREEN.blit(game_mode, game_mode.get_rect(topright = (GAME_CONSTANTS['SQUARE_SIZE'] * 15, GAME_CONSTANTS['SQUARE_SIZE'] * 6.5)))

    mission_mode = GAME_FONTS['KENNEY_MINI_SQUARE_32'].render(f"MISSION", True, GAME_COLORS['SHMUP_GRAY'])
    if GAME_MODE_OPTIONS['MISSION']:
      mission_mode = GAME_FONTS['KENNEY_MINI_SQUARE_32'].render(f"MISSION", True, GAME_COLORS['SHMUP_GREEN'])
    THE_SCREEN.blit(mission_mode, mission_mode.get_rect(topleft = (GAME_CONSTANTS['SQUARE_SIZE'] * 18, GAME_CONSTANTS['SQUARE_SIZE'] * 6.85)))

    arena_mode = GAME_FONTS['KENNEY_MINI_SQUARE_32'].render(f"ARENA", True, GAME_COLORS['SHMUP_GRAY'])
    if GAME_MODE_OPTIONS['ARENA']:
      arena_mode = GAME_FONTS['KENNEY_MINI_SQUARE_32'].render(f"ARENA", True, GAME_COLORS['SHMUP_GREEN'])
    THE_SCREEN.blit(arena_mode, arena_mode.get_rect(topleft = (GAME_CONSTANTS['SQUARE_SIZE'] * 23, GAME_CONSTANTS['SQUARE_SIZE'] * 6.85)))

    dogfight_mode = GAME_FONTS['KENNEY_MINI_SQUARE_32'].render(f"DOGFIGHT", True, GAME_COLORS['ALMOST_BLACK'])
    if GAME_MODE_OPTIONS['TWO_PLAYERS']:
      dogfight_mode = GAME_FONTS['KENNEY_MINI_SQUARE_32'].render(f"DOGFIGHT", True, GAME_COLORS['SHMUP_GRAY'])
      if GAME_MODE_OPTIONS['DOGFIGHT']:
        dogfight_mode = GAME_FONTS['KENNEY_MINI_SQUARE_32'].render(f"DOGFIGHT", True, GAME_COLORS['SHMUP_GREEN'])
    
    THE_SCREEN.blit(dogfight_mode, dogfight_mode.get_rect(topleft = (GAME_CONSTANTS['SQUARE_SIZE'] * 27.5, GAME_CONSTANTS['SQUARE_SIZE'] * 6.85)))

    if GAME_MODE_OPTIONS['DOGFIGHT']:
      starting_lives = GAME_FONTS['KENNEY_MINI_SQUARE_48'].render(f"STARTING LIVES:", True, GAME_COLORS['ALMOST_BLACK'])
      if GAME_MODE_OPTIONS['STARTING_LIVES']:
        starting_lives = GAME_FONTS['KENNEY_MINI_SQUARE_48'].render(f"STARTING LIVES:", True, GAME_COLORS['SHMUP_ORANGE'])
      THE_SCREEN.blit(starting_lives, starting_lives.get_rect(topright = (GAME_CONSTANTS['SQUARE_SIZE'] * 15, GAME_CONSTANTS['SQUARE_SIZE'] * 10.5)))

      yellow_plane_lives_1 = pygame.transform.rotozoom(GAME_SURFACES['PIXEL_SHMUP_SHIPS']['YELLOW_A_FIGHTER'], 0, 2)
      yellow_plane_lives_2 = pygame.transform.rotozoom(GAME_SURFACES['PIXEL_SHMUP_SHIPS']['YELLOW_A_FIGHTER_GRAY'], 0, 2)
      yellow_plane_lives_3 = pygame.transform.rotozoom(GAME_SURFACES['PIXEL_SHMUP_SHIPS']['YELLOW_A_FIGHTER_GRAY'], 0, 2)
      yellow_plane_lives_4 = pygame.transform.rotozoom(GAME_SURFACES['PIXEL_SHMUP_SHIPS']['YELLOW_A_FIGHTER_GRAY'], 0, 2)
      yellow_plane_lives_5 = pygame.transform.rotozoom(GAME_SURFACES['PIXEL_SHMUP_SHIPS']['YELLOW_A_FIGHTER_GRAY'], 0, 2)

      if GAME_MODE_OPTIONS['LIVES_COUNT'] >= 2:
        yellow_plane_lives_2 = pygame.transform.rotozoom(GAME_SURFACES['PIXEL_SHMUP_SHIPS']['YELLOW_A_FIGHTER'], 0, 2)
      if GAME_MODE_OPTIONS['LIVES_COUNT'] >= 3:
        yellow_plane_lives_3 = pygame.transform.rotozoom(GAME_SURFACES['PIXEL_SHMUP_SHIPS']['YELLOW_A_FIGHTER'], 0, 2)
      if GAME_MODE_OPTIONS['LIVES_COUNT'] >= 4:
        yellow_plane_lives_4 = pygame.transform.rotozoom(GAME_SURFACES['PIXEL_SHMUP_SHIPS']['YELLOW_A_FIGHTER'], 0, 2)
      if GAME_MODE_OPTIONS['LIVES_COUNT'] >= 5:
        yellow_plane_lives_5 = pygame.transform.rotozoom(GAME_SURFACES['PIXEL_SHMUP_SHIPS']['YELLOW_A_FIGHTER'], 0, 2)

      THE_SCREEN.blit(yellow_plane_lives_1, yellow_plane_lives_1.get_rect(center=(GAME_CONSTANTS['SQUARE_SIZE'] * 19.5, GAME_CONSTANTS['SQUARE_SIZE'] * 11.5)))
      THE_SCREEN.blit(yellow_plane_lives_2, yellow_plane_lives_2.get_rect(center=(GAME_CONSTANTS['SQUARE_SIZE'] * 22.0, GAME_CONSTANTS['SQUARE_SIZE'] * 11.5)))
      THE_SCREEN.blit(yellow_plane_lives_3, yellow_plane_lives_3.get_rect(center=(GAME_CONSTANTS['SQUARE_SIZE'] * 24.5, GAME_CONSTANTS['SQUARE_SIZE'] * 11.5)))
      THE_SCREEN.blit(yellow_plane_lives_4, yellow_plane_lives_4.get_rect(center=(GAME_CONSTANTS['SQUARE_SIZE'] * 27.0, GAME_CONSTANTS['SQUARE_SIZE'] * 11.5)))
      THE_SCREEN.blit(yellow_plane_lives_5, yellow_plane_lives_5.get_rect(center=(GAME_CONSTANTS['SQUARE_SIZE'] * 29.5, GAME_CONSTANTS['SQUARE_SIZE'] * 11.5)))

    start_game = GAME_FONTS['KENNEY_MINI_SQUARE_48'].render(f"START GAME", True, GAME_COLORS['ALMOST_BLACK'])
    if GAME_MODE_OPTIONS['START_GAME']:
      start_game = GAME_FONTS['KENNEY_MINI_SQUARE_48'].render(f"START GAME", True, GAME_COLORS['SHMUP_ORANGE'])
    if GAME_STATE['TRANSITION_TO_INSTRUCTIONS_SCREEN']:
      start_game = GAME_FONTS['KENNEY_MINI_SQUARE_48'].render(f"START GAME", True, GAME_COLORS['SHMUP_WHITE'])
      start_game.set_alpha(int((GAME_STATE_TRANSITION_TTL['TRANSITION_TO_INSTRUCTIONS_SCREEN'] / TTL_DEFAULTS['TRANSITION_TO_INSTRUCTIONS_SCREEN']) * 255))
      

    THE_SCREEN.blit(start_game, start_game.get_rect(center = (GAME_CONSTANTS['SCREEN_WIDTH'] / 2, GAME_CONSTANTS['SQUARE_SIZE'] * 16.0)))

    if GAME_MODE_OPTIONS['START_GAME'] and not GAME_STATE['TRANSITION_TO_INSTRUCTIONS_SCREEN'] and (GAME_CONTROLS['PLAYER_1']['GREEN'] or GAME_CONTROLS['PLAYER_1']['RED'] or GAME_CONTROLS['PLAYER_1']['BLUE'] or GAME_CONTROLS['PLAYER_1']['YELLOW'] or GAME_CONTROLS['PLAYER_2']['GREEN'] or GAME_CONTROLS['PLAYER_2']['RED'] or GAME_CONTROLS['PLAYER_2']['BLUE'] or GAME_CONTROLS['PLAYER_2']['YELLOW']):
      if SOUND_EFFECT_SELECT != None:
        SOUND_EFFECT_SELECT.stop()
        SOUND_EFFECT_SELECT.set_volume(1.0)
        SOUND_EFFECT_SELECT.play(loops=0)
      GAME_STATE['TRANSITION_TO_INSTRUCTIONS_SCREEN'] = True
    if GAME_STATE['TRANSITION_TO_INSTRUCTIONS_SCREEN']:
      GAME_STATE_TRANSITION_TTL['TRANSITION_TO_INSTRUCTIONS_SCREEN'] = GAME_STATE_TRANSITION_TTL['TRANSITION_TO_INSTRUCTIONS_SCREEN'] - ELAPSED_MS
      if GAME_STATE_TRANSITION_TTL['TRANSITION_TO_INSTRUCTIONS_SCREEN'] <= 0:
        initialize_instructions_screen()

  ####################################################################
  # INSTRUCTIONS_SCREEN - If we're at the instructions screen, draw that screen
  #
  ####################################################################
  if GAME_STATE['INSTRUCTIONS_SCREEN']:
    instructions_screen_ttl = instructions_screen_ttl - ELAPSED_MS

    if (GAME_CONTROLS['PLAYER_1']['GREEN'] or GAME_CONTROLS['PLAYER_1']['RED'] or GAME_CONTROLS['PLAYER_1']['BLUE'] or GAME_CONTROLS['PLAYER_1']['YELLOW'] or GAME_CONTROLS['PLAYER_2']['GREEN'] or GAME_CONTROLS['PLAYER_2']['RED'] or GAME_CONTROLS['PLAYER_2']['BLUE'] or GAME_CONTROLS['PLAYER_2']['YELLOW']):
      GAME_CONTROLS['PLAYER_1']['GREEN'] = False
      GAME_CONTROLS['PLAYER_1']['RED'] = False
      GAME_CONTROLS['PLAYER_1']['BLUE'] = False
      GAME_CONTROLS['PLAYER_1']['YELLOW'] = False
      GAME_CONTROLS['PLAYER_2']['GREEN'] = False
      GAME_CONTROLS['PLAYER_2']['RED'] = False
      GAME_CONTROLS['PLAYER_2']['BLUE'] = False
      GAME_CONTROLS['PLAYER_2']['YELLOW'] = False
      instructions_screen_ttl = instructions_screen_ttl - 500
      instructions_screen_ttl = int(instructions_screen_ttl / 1000) * 1000
      if SOUND_EFFECT_UI_MOVE != None:
        SOUND_EFFECT_UI_MOVE.stop()
        SOUND_EFFECT_UI_MOVE.set_volume(1.00)
        SOUND_EFFECT_UI_MOVE.play(loops=0)

    if GAME_MODE_OPTIONS['DOGFIGHT']:
      dogfight_mode = GAME_FONTS['KENNEY_MINI_SQUARE_80'].render(f"DOGFIGHT MODE", True, GAME_COLORS['ALMOST_BLACK'])
      THE_SCREEN.blit(dogfight_mode, dogfight_mode.get_rect(center = (GAME_CONSTANTS['SCREEN_WIDTH'] / 2, 96)))

      intro = GAME_FONTS['KENNEY_MINI_SQUARE_32'].render(f"Player One       plays against Player Two       in a BATTLE ROYALE!", True, GAME_COLORS['SHMUP_GREEN'])
      THE_SCREEN.blit(intro, intro.get_rect(center = (GAME_CONSTANTS['SCREEN_WIDTH'] / 2, 176)))

      THE_SCREEN.blit(GAME_SURFACES['PIXEL_SHMUP_SHIPS']['RED_B_FIGHTER'], GAME_SURFACES['PIXEL_SHMUP_SHIPS']['RED_B_FIGHTER'].get_rect(center = (342, 176)))
      THE_SCREEN.blit(GAME_SURFACES['PIXEL_SHMUP_SHIPS']['BLUE_B_FIGHTER'], GAME_SURFACES['PIXEL_SHMUP_SHIPS']['BLUE_B_FIGHTER'].get_rect(center = (816, 176)))

      game_over = GAME_FONTS['KENNEY_MINI_SQUARE_32'].render("Once one, or both players, are out of lives, the DOGFIGHT is over.", True, GAME_COLORS['SHMUP_GREEN'])
      THE_SCREEN.blit(game_over, game_over.get_rect(center = (GAME_CONSTANTS['SCREEN_WIDTH'] / 2, 244)))

      movement = GAME_FONTS['KENNEY_MINI_SQUARE_32'].render("Control the direction of the plane by pressing [A/LEFT] or [D/RIGHT].", True, GAME_COLORS['SHMUP_GREEN'])
      THE_SCREEN.blit(movement, movement.get_rect(center = (GAME_CONSTANTS['SCREEN_WIDTH'] / 2, 324)))

      controls = GAME_FONTS['KENNEY_MINI_SQUARE_32'].render("[SHIFT/A] Fires, [CTRL/B] Drops a Bomb, [ALT/X] speeds the plane up.", True, GAME_COLORS['SHMUP_GREEN'])
      THE_SCREEN.blit(controls, controls.get_rect(center = (GAME_CONSTANTS['SCREEN_WIDTH'] / 2, 356)))

      controls = GAME_FONTS['KENNEY_MINI_SQUARE_32'].render("Defend your landmarks!  Failure to do so will cost you a life!", True, GAME_COLORS['SHMUP_GREEN'])
      THE_SCREEN.blit(controls, controls.get_rect(center = (GAME_CONSTANTS['SCREEN_WIDTH'] / 2, 436)))

      good_luck = GAME_FONTS['KENNEY_MINI_SQUARE_32'].render("Good Luck, and may the best pilot win!", True, GAME_COLORS['SHMUP_GREEN'])
      THE_SCREEN.blit(good_luck, good_luck.get_rect(center = (GAME_CONSTANTS['SCREEN_WIDTH'] / 2, 468)))

    elif GAME_MODE_OPTIONS['MISSION']:
      dogfight_mode = GAME_FONTS['KENNEY_MINI_SQUARE_80'].render(f"MISSION MODE", True, GAME_COLORS['ALMOST_BLACK'])
      THE_SCREEN.blit(dogfight_mode, dogfight_mode.get_rect(center = (GAME_CONSTANTS['SCREEN_WIDTH'] / 2, 96)))
    elif GAME_MODE_OPTIONS['ARENA']:
      dogfight_mode = GAME_FONTS['KENNEY_MINI_SQUARE_80'].render(f"ARENA MODE", True, GAME_COLORS['ALMOST_BLACK'])
      THE_SCREEN.blit(dogfight_mode, dogfight_mode.get_rect(center = (GAME_CONSTANTS['SCREEN_WIDTH'] / 2, 96)))
    else:
      invalid_mode = GAME_FONTS['KENNEY_MINI_SQUARE_80'].render(f"INVALID MODE", True, GAME_COLORS['SHMUP_ORANGE'])
      THE_SCREEN.blit(invalid_mode, invalid_mode.get_rect(center = (GAME_CONSTANTS['SCREEN_WIDTH'] / 2, 96)))

    instructions_seconds = int(instructions_screen_ttl / 1000)

    seconds_text = GAME_FONTS['KENNEY_MINI_SQUARE_96'].render(f"{instructions_seconds}", True, GAME_COLORS['ALMOST_BLACK'])
    THE_SCREEN.blit(seconds_text, seconds_text.get_rect(center = (GAME_CONSTANTS['SCREEN_WIDTH'] / 2, GAME_CONSTANTS['SCREEN_HEIGHT'] - 160)))

    if instructions_screen_ttl < 0:
      if GAME_MODE_OPTIONS['DOGFIGHT']:
        initialize_dogfight_mode()
      elif GAME_MODE_OPTIONS['MISSION']:
        initialize_title_screen()
      elif GAME_MODE_OPTIONS['ARENA']:
        initialize_title_screen()
      else:
        initialize_title_screen()

  ####################################################################
  # DOGFIGHT_MODE - If we're in dog fight mode, draw that screen
  #
  ####################################################################
  if GAME_STATE['DOGFIGHT_MODE']:
    ####################################################################
    # Draw Layer One (The Map Tiles)
    ####################################################################
    if GAME_STATE['LAYER_1']:
      for i in range(len(MAP)):
        for j in range(len(MAP[i])):
          map_tile = GAME_SURFACES['PIXEL_SHMUP_TILES'][MAP[i][j]]
          THE_SCREEN.blit(map_tile, map_tile.get_rect(topleft = (j*GAME_CONSTANTS['SQUARE_SIZE'], (i+1)*GAME_CONSTANTS['SQUARE_SIZE'])))
          total_map_tiles = total_map_tiles + 1



    if dogfighting_pvp_active:
      ###BASE CREATION
      if GAME_MODE_OPTIONS['DOGFIGHT_BASES']:
        dogfighting_base_creation_ttl = dogfighting_base_creation_ttl - ELAPSED_MS

        if dogfighting_base_creation_ttl <= 0:
          if not PLAYER_1_BASE.activated:
            base = random.choice(range(3))
            PLAYER_1_BASE.style = base
            if base == 0:
              PLAYER_1_BASE.set_image(GAME_SURFACES['PIXEL_SHMUP_TILES']['MAP_GREEN_RED_HOUSE'])
            elif base == 1:
              PLAYER_1_BASE.set_image(GAME_SURFACES['PIXEL_SHMUP_TILES']['MAP_GREEN_RED_TENT'])
            elif base == 2:
              PLAYER_1_BASE.set_image(GAME_SURFACES['PIXEL_SHMUP_TILES']['MAP_GREEN_RED_FLAG'])
            PLAYER_1_BASE.activated = True
            base_x = random.choice(range(3, 9))
            base_y = random.choice(range(5, 15))
            PLAYER_1_BASE.set_location(base_x * GAME_CONSTANTS['SQUARE_SIZE'], base_y * GAME_CONSTANTS['SQUARE_SIZE'])

          if not PLAYER_2_BASE.activated:
            base = random.choice(range(3))
            PLAYER_2_BASE.style = base
            if base == 0:
              PLAYER_2_BASE.set_image(GAME_SURFACES['PIXEL_SHMUP_TILES']['MAP_BROWN_BLUE_HOUSE'])
            elif base == 1:
              PLAYER_2_BASE.set_image(GAME_SURFACES['PIXEL_SHMUP_TILES']['MAP_BROWN_BLUE_TENT'])
            elif base == 2:
              PLAYER_2_BASE.set_image(GAME_SURFACES['PIXEL_SHMUP_TILES']['MAP_BROWN_BLUE_FLAG'])
            PLAYER_2_BASE.activated = True
            base_x = random.choice(range(33, 39))
            base_y = random.choice(range(5, 15))
            PLAYER_2_BASE.set_location(base_x * GAME_CONSTANTS['SQUARE_SIZE'], base_y * GAME_CONSTANTS['SQUARE_SIZE'])

          dogfighting_base_creation_ttl = random.choice(range(TTL_DEFAULTS['BASE_CREATION_MIN'], TTL_DEFAULTS['BASE_CREATION_MAX']))

      if PLAYER_1.activated:
        PLAYER_1.weapon_1_cooldown = PLAYER_1.weapon_1_cooldown - ELAPSED_MS
        PLAYER_1.weapon_2_cooldown = PLAYER_1.weapon_2_cooldown - ELAPSED_MS
        PLAYER_1.effect_1_ttl = PLAYER_1.effect_1_ttl - ELAPSED_MS

        if GAME_CONTROLS['PLAYER_1']['LEFT']:
          PLAYER_1.set_rotation_delta(PLAYER_1.speed_rotation * ELAPSED_S)
        if GAME_CONTROLS['PLAYER_1']['RIGHT']:
          PLAYER_1.set_rotation_delta(-PLAYER_1.speed_rotation * ELAPSED_S)

        if GAME_CONTROLS['PLAYER_1']['BLUE']:
          PLAYER_1.speed = PLAYER_1.speed + PLAYER_1.speed_delta * ELAPSED_S
          PLAYER_1.speed_rotation = PLAYER_1.speed_rotation - PLAYER_1.speed_rotation_delta * ELAPSED_S
          if SOUND_EFFECT_ENGINE_1 != None:
            if SOUND_EFFECT_ENGINE_1.get_num_channels() < 1:
              SOUND_EFFECT_ENGINE_1.play()
            else:
              SOUND_EFFECT_ENGINE_1.set_volume(0.30)
        else:
          PLAYER_1.speed = PLAYER_1.speed - PLAYER_1.speed_delta * ELAPSED_S
          PLAYER_1.speed_rotation = PLAYER_1.speed_rotation + PLAYER_1.speed_rotation_delta * ELAPSED_S
          if SOUND_EFFECT_ENGINE_1 != None:
            if SOUND_EFFECT_ENGINE_1.get_num_channels() < 1:
              SOUND_EFFECT_ENGINE_1.play()
            else:
              SOUND_EFFECT_ENGINE_1.set_volume(0.15)

        if GAME_CONTROLS['PLAYER_1']['GREEN']:
          if PLAYER_1.weapon_1_cooldown <= 0:
            #Fire weapon 1
            bullet = Bullet(PLAYER_1.x, PLAYER_1.y, 0, 0, PLAYER_1.rotation, PLAYER_1.weapon_1_speed + PLAYER_1.speed, GAME_SURFACES['PIXEL_SHMUP_TILES']['SINGLE_SHOT'], False)
            bullet.size_modifier = 0.5
            player_1_bullets.add(bullet)

            #GAME_CONTROLS['PLAYER_1']['GREEN'] = False
            PLAYER_1.weapon_1_cooldown = PLAYER_1.weapon_1_cooldown_default
            if SOUND_EFFECT_SHOT_1 != None:
              SOUND_EFFECT_SHOT_1.stop()
              SOUND_EFFECT_SHOT_1.set_volume(1.00)
              SOUND_EFFECT_SHOT_1.play(loops=0)

        if GAME_CONTROLS['PLAYER_1']['RED']:
          if PLAYER_1.weapon_2_cooldown <= 0:
            #Fire weapon 2
            bullet = Bullet(PLAYER_1.x, PLAYER_1.y, 0, 0, PLAYER_1.rotation, PLAYER_1.weapon_2_speed, GAME_SURFACES['PIXEL_SHMUP_TILES']['SINGLE_BOMB'], True)
            bullet.effect_1_ttl = 750
            bullet.effect_1_ttl_default = 750
            bullet.effect_1_active = True
            player_1_bullets.add(bullet)

            #GAME_CONTROLS['PLAYER_1']['RED'] = False
            PLAYER_1.weapon_2_cooldown = PLAYER_1.weapon_2_cooldown_default
            if SOUND_EFFECT_BOMB != None:
              SOUND_EFFECT_BOMB.stop()
              SOUND_EFFECT_BOMB.set_volume(0.25)
              SOUND_EFFECT_BOMB.play(loops=0)
        
        if PLAYER_1.speed > PLAYER_1.max_speed:
          PLAYER_1.speed = PLAYER_1.max_speed
        if PLAYER_1.speed < PLAYER_1.min_speed:
          PLAYER_1.speed = PLAYER_1.min_speed

        if PLAYER_1.speed_rotation > PLAYER_1.max_speed_rotation:
          PLAYER_1.speed_rotation = PLAYER_1.max_speed_rotation
        if PLAYER_1.speed_rotation < PLAYER_1.min_speed_rotation:
          PLAYER_1.speed_rotation = PLAYER_1.min_speed_rotation

        PLAYER_1.speed_x = math.cos(math.radians(PLAYER_1.rotation + 90)) * PLAYER_1.speed * ELAPSED_S
        PLAYER_1.speed_y = -math.sin(math.radians(PLAYER_1.rotation + 90)) * PLAYER_1.speed * ELAPSED_S
        PLAYER_1.set_location_delta(PLAYER_1.speed_x, PLAYER_1.speed_y)

        if PLAYER_1.x < 0:
          PLAYER_1.set_location(0, PLAYER_1.y)
        if PLAYER_1.x > GAME_CONSTANTS['SCREEN_WIDTH']:
          PLAYER_1.set_location(GAME_CONSTANTS['SCREEN_WIDTH'], PLAYER_1.y)
        if PLAYER_1.y < GAME_CONSTANTS['SQUARE_SIZE']:
          PLAYER_1.set_location(PLAYER_1.x, GAME_CONSTANTS['SQUARE_SIZE'])
        if PLAYER_1.y > GAME_CONSTANTS['SCREEN_HEIGHT'] - GAME_CONSTANTS['SQUARE_SIZE'] * 2.5:
          PLAYER_1.set_location(PLAYER_1.x, GAME_CONSTANTS['SCREEN_HEIGHT'] - GAME_CONSTANTS['SQUARE_SIZE'] * 2.5)

        if PLAYER_1.effect_1_ttl > 0:
          PLAYER_1.effect_1_active = True
          PLAYER_1.randomize_alpha()
          if PLAYER_1_BASE.activated:
            PLAYER_1_BASE.randomize_alpha()
        else:
          PLAYER_1.effect_1_active = False
          PLAYER_1.set_alpha(255)
          if PLAYER_1_BASE.activated:
            PLAYER_1_BASE.set_alpha(255)

      if PLAYER_2.activated:
        PLAYER_2.weapon_1_cooldown = PLAYER_2.weapon_1_cooldown - ELAPSED_MS
        PLAYER_2.weapon_2_cooldown = PLAYER_2.weapon_2_cooldown - ELAPSED_MS
        PLAYER_2.effect_1_ttl = PLAYER_2.effect_1_ttl - ELAPSED_MS

        if GAME_CONTROLS['PLAYER_2']['LEFT']:
          PLAYER_2.set_rotation_delta(PLAYER_2.speed_rotation * ELAPSED_S)
        if GAME_CONTROLS['PLAYER_2']['RIGHT']:
          PLAYER_2.set_rotation_delta(-PLAYER_2.speed_rotation * ELAPSED_S)
        if GAME_CONTROLS['PLAYER_2']['BLUE']:
          PLAYER_2.speed = PLAYER_2.speed + PLAYER_2.speed_delta * ELAPSED_S
          PLAYER_2.speed_rotation = PLAYER_2.speed_rotation - PLAYER_2.speed_rotation_delta * ELAPSED_S
          if SOUND_EFFECT_ENGINE_2 != None:
            if SOUND_EFFECT_ENGINE_2.get_num_channels() < 1:
              SOUND_EFFECT_ENGINE_2.play()
            else:
              SOUND_EFFECT_ENGINE_2.set_volume(0.30)
        else:
          PLAYER_2.speed = PLAYER_2.speed - PLAYER_2.speed_delta * ELAPSED_S
          PLAYER_2.speed_rotation = PLAYER_2.speed_rotation + PLAYER_2.speed_rotation_delta * ELAPSED_S
          if SOUND_EFFECT_ENGINE_2 != None:
            if SOUND_EFFECT_ENGINE_2.get_num_channels() < 1:
              SOUND_EFFECT_ENGINE_2.play()
            else:
              SOUND_EFFECT_ENGINE_2.set_volume(0.15)
        
        if GAME_CONTROLS['PLAYER_2']['GREEN']:
          if PLAYER_2.weapon_1_cooldown <= 0:
            #Fire weapon 1
            bullet = Bullet(PLAYER_2.x, PLAYER_2.y, 0, 0, PLAYER_2.rotation, PLAYER_2.weapon_1_speed + PLAYER_2.speed, GAME_SURFACES['PIXEL_SHMUP_TILES']['SINGLE_SHOT'], False)
            bullet.size_modifier = 0.5
            player_2_bullets.add(bullet)

            #GAME_CONTROLS['PLAYER_2']['GREEN'] = False
            PLAYER_2.weapon_1_cooldown = PLAYER_2.weapon_1_cooldown_default
            if SOUND_EFFECT_SHOT_2 != None:
              SOUND_EFFECT_SHOT_2.stop()
              SOUND_EFFECT_SHOT_2.set_volume(1.00)
              SOUND_EFFECT_SHOT_2.play(loops=0)

        if GAME_CONTROLS['PLAYER_2']['RED']:
          if PLAYER_2.weapon_2_cooldown <= 0:
            #Fire weapon 2
            bullet = Bullet(PLAYER_2.x, PLAYER_2.y, 0, 0, PLAYER_2.rotation, PLAYER_2.weapon_2_speed, GAME_SURFACES['PIXEL_SHMUP_TILES']['SINGLE_BOMB'], True)
            bullet.effect_1_ttl = 750
            bullet.effect_1_ttl_default = 750
            bullet.effect_1_active = True
            player_2_bullets.add(bullet)

            #GAME_CONTROLS['PLAYER_2']['RED'] = False
            PLAYER_2.weapon_2_cooldown = PLAYER_2.weapon_2_cooldown_default
            if SOUND_EFFECT_BOMB != None:
              SOUND_EFFECT_BOMB.stop()
              SOUND_EFFECT_BOMB.set_volume(0.25)
              SOUND_EFFECT_BOMB.play(loops=0)

        if PLAYER_2.speed > PLAYER_2.max_speed:
          PLAYER_2.speed = PLAYER_2.max_speed
        if PLAYER_2.speed < PLAYER_2.min_speed:
          PLAYER_2.speed = PLAYER_2.min_speed

        if PLAYER_2.speed_rotation > PLAYER_2.max_speed_rotation:
          PLAYER_2.speed_rotation = PLAYER_2.max_speed_rotation
        if PLAYER_2.speed_rotation < PLAYER_2.min_speed_rotation:
          PLAYER_2.speed_rotation = PLAYER_2.min_speed_rotation

        PLAYER_2.speed_x = math.cos(math.radians(PLAYER_2.rotation + 90)) * PLAYER_2.speed * ELAPSED_S
        PLAYER_2.speed_y = -math.sin(math.radians(PLAYER_2.rotation + 90)) * PLAYER_2.speed * ELAPSED_S
        PLAYER_2.set_location_delta(PLAYER_2.speed_x, PLAYER_2.speed_y)

        if PLAYER_2.x < 0:
          PLAYER_2.set_location(0, PLAYER_2.y)
        if PLAYER_2.x > GAME_CONSTANTS['SCREEN_WIDTH']:
          PLAYER_2.set_location(GAME_CONSTANTS['SCREEN_WIDTH'], PLAYER_2.y)
        if PLAYER_2.y < GAME_CONSTANTS['SQUARE_SIZE']:
          PLAYER_2.set_location(PLAYER_2.x, GAME_CONSTANTS['SQUARE_SIZE'])
        if PLAYER_2.y > GAME_CONSTANTS['SCREEN_HEIGHT'] - GAME_CONSTANTS['SQUARE_SIZE'] * 2.5:
          PLAYER_2.set_location(PLAYER_2.x, GAME_CONSTANTS['SCREEN_HEIGHT'] - GAME_CONSTANTS['SQUARE_SIZE'] * 2.5)

        if PLAYER_2.effect_1_ttl > 0:
          PLAYER_2.effect_1_active = True
          PLAYER_2.randomize_alpha()
          if PLAYER_2_BASE.activated:
            PLAYER_2_BASE.randomize_alpha()
        else:
          PLAYER_2.effect_1_active = False
          PLAYER_2.set_alpha(255)
          if PLAYER_2_BASE.activated:
            PLAYER_2_BASE.set_alpha(255)

      ### Update/Move the bullets and check collisions
      ### LESSON - Collision Detection
      bullets = player_1_bullets.sprites()
      bullets.extend(player_2_bullets.sprites())
      for bullet in reversed(bullets):
        if bullet.effect_1_active:
          bullet.effect_1_ttl = bullet.effect_1_ttl - ELAPSED_MS
        
        bullet.speed_x = math.cos(math.radians(bullet.rotation + 90)) * bullet.speed * ELAPSED_S
        bullet.speed_y = -math.sin(math.radians(bullet.rotation + 90)) * bullet.speed * ELAPSED_S
        bullet.set_location_delta(bullet.speed_x, bullet.speed_y)
        if bullet.bomb == True:
          bullet.size_modifier = bullet.effect_1_ttl / bullet.effect_1_ttl_default
          if bullet.size_modifier < 0.25:
            bullet.size_modifier = 0.25
          if bullet.effect_1_ttl < 0 and bullet.effect_1_active:
            bullet.kill()
            explosion = GameSprite(bullet.x, bullet.y, 0, 0, bullet.rotation, 0, GAME_SURFACES['PIXEL_SHMUP_TILES']['STAR_SHOT'])
            explosion.effect_1_ttl = 350
            explosion.effect_2_ttl = 150
            explosion.effect_3_ttl = 150
            explosion.effect_1_active = True
            explosion.size_modifier = 0.5
            explosions.add(explosion)
            if SOUND_EFFECT_GROUND_HIT != None:
              SOUND_EFFECT_GROUND_HIT.stop()
              SOUND_EFFECT_GROUND_HIT.set_volume(0.65)
              SOUND_EFFECT_GROUND_HIT.play(loops=0)
        if bullet.x < 0 or bullet.y < 0 or bullet.x > GAME_CONSTANTS['SCREEN_WIDTH'] or bullet.y > GAME_CONSTANTS['SCREEN_HEIGHT']:
          bullet.kill()
        
      if pygame.sprite.collide_circle_ratio(0.45)(PLAYER_1, PLAYER_2): #a simpler approach, courtesy of nuclear pasta
        if not PLAYER_1.effect_1_active and not PLAYER_2.effect_1_active:
          explosion = GameSprite(PLAYER_1.x, PLAYER_1.y, 0, 0, PLAYER_1.rotation, 0, GAME_SURFACES['PIXEL_SHMUP_TILES']['STAR_SHOT'])
          explosion.effect_1_ttl = 350
          explosion.effect_2_ttl = 150
          explosion.effect_3_ttl = 150
          explosion.effect_1_active = True
          explosions.add(explosion)
          explosion = GameSprite(PLAYER_2.x, PLAYER_2.y, 0, 0, PLAYER_2.rotation, 0, GAME_SURFACES['PIXEL_SHMUP_TILES']['STAR_SHOT'])
          explosion.effect_1_ttl = 350
          explosion.effect_2_ttl = 150
          explosion.effect_3_ttl = 150
          explosion.effect_1_active = True
          explosions.add(explosion)
          if SOUND_EFFECT_EXPLOSION_1 != None:
            SOUND_EFFECT_EXPLOSION_1.stop()
            SOUND_EFFECT_EXPLOSION_1.set_volume(1.00)
            SOUND_EFFECT_EXPLOSION_1.play(loops=0)

          PLAYER_1.lives = PLAYER_1.lives - 1
          PLAYER_1.set_location(GAME_CONSTANTS['SCREEN_WIDTH'] / 4, GAME_CONSTANTS['SCREEN_HEIGHT'] / 2 - GAME_CONSTANTS['SQUARE_SIZE'])
          PLAYER_1.set_rotation(270)
          PLAYER_1.speed = 64
          PLAYER_1.effect_1_ttl = 3000
          PLAYER_1.effect_1_active = True
          PLAYER_2.lives = PLAYER_2.lives - 1
          PLAYER_2.set_location((GAME_CONSTANTS['SCREEN_WIDTH'] / 4) * 3, GAME_CONSTANTS['SCREEN_HEIGHT'] / 2 - GAME_CONSTANTS['SQUARE_SIZE'])
          PLAYER_2.set_rotation(90)
          PLAYER_2.speed = 64
          PLAYER_2.effect_1_ttl = 3000
          PLAYER_2.effect_1_active = True

      collisions = pygame.sprite.spritecollide(PLAYER_1, player_2_bullets, False, collided=pygame.sprite.collide_circle_ratio(0.45))
      if len(collisions) > 0:
        for bullet in collisions:
          if not bullet.bomb:
            explosion = GameSprite(bullet.x, bullet.y, 0, 0, bullet.rotation, 0, GAME_SURFACES['PIXEL_SHMUP_TILES']['STAR_SHOT'])
            explosion.effect_1_ttl = 350
            explosion.effect_2_ttl = 150
            explosion.effect_3_ttl = 150
            explosion.effect_1_active = True
            explosions.add(explosion)
            bullet.kill()
            if not PLAYER_1.effect_1_active:
              PLAYER_1.lives = PLAYER_1.lives - 1
              PLAYER_1.set_location(GAME_CONSTANTS['SCREEN_WIDTH'] / 4, GAME_CONSTANTS['SCREEN_HEIGHT'] / 2 - GAME_CONSTANTS['SQUARE_SIZE'])
              PLAYER_1.set_rotation(270)
              PLAYER_1.speed = 64
              PLAYER_1.effect_1_ttl = 3000
              PLAYER_1.effect_1_active = True
              if SOUND_EFFECT_EXPLOSION_1 != None:
                SOUND_EFFECT_EXPLOSION_1.stop()
                SOUND_EFFECT_EXPLOSION_1.set_volume(1.00)
                SOUND_EFFECT_EXPLOSION_1.play(loops=0)
            else:
              if SOUND_EFFECT_PLANE_HIT != None:
                SOUND_EFFECT_PLANE_HIT.stop()
                SOUND_EFFECT_PLANE_HIT.set_volume(1.00)
                SOUND_EFFECT_PLANE_HIT.play(loops=0)

      collisions = pygame.sprite.spritecollide(PLAYER_2, player_1_bullets, False, collided=pygame.sprite.collide_circle_ratio(0.45))
      if len(collisions) > 0:
        for bullet in collisions:
          if not bullet.bomb:
            explosion = GameSprite(bullet.x, bullet.y, 0, 0, bullet.rotation, 0, GAME_SURFACES['PIXEL_SHMUP_TILES']['STAR_SHOT'])
            explosion.effect_1_ttl = 350
            explosion.effect_2_ttl = 150
            explosion.effect_3_ttl = 150
            explosion.effect_1_active = True
            explosions.add(explosion)
            bullet.kill()
            if not PLAYER_2.effect_1_active:
              PLAYER_2.lives = PLAYER_2.lives - 1
              PLAYER_2.set_location((GAME_CONSTANTS['SCREEN_WIDTH'] / 4) * 3, GAME_CONSTANTS['SCREEN_HEIGHT'] / 2 - GAME_CONSTANTS['SQUARE_SIZE'])
              PLAYER_2.set_rotation(90)
              PLAYER_2.speed = 64
              PLAYER_2.effect_1_ttl = 3000
              PLAYER_2.effect_1_active = True
              if SOUND_EFFECT_EXPLOSION_1 != None:
                SOUND_EFFECT_EXPLOSION_1.stop()
                SOUND_EFFECT_EXPLOSION_1.set_volume(1.00)
                SOUND_EFFECT_EXPLOSION_1.play(loops=0)
            else:
              if SOUND_EFFECT_PLANE_HIT != None:
                SOUND_EFFECT_PLANE_HIT.stop()
                SOUND_EFFECT_PLANE_HIT.set_volume(1.00)
                SOUND_EFFECT_PLANE_HIT.play(loops=0)

      #Check collisions for "bases" and make life loss accordingly
      if PLAYER_1_BASE.activated:
        collisions = pygame.sprite.spritecollide(PLAYER_1_BASE, player_2_bullets, False, collided=pygame.sprite.collide_circle_ratio(0.55))
        for bullet in collisions:
          if bullet.bomb and bullet.size_modifier <= 0.25:
            explosion = GameSprite(bullet.x, bullet.y, 0, 0, bullet.rotation, 0, GAME_SURFACES['PIXEL_SHMUP_TILES']['STAR_SHOT'])
            explosion.effect_1_ttl = 350
            explosion.effect_2_ttl = 150
            explosion.effect_3_ttl = 150
            explosion.effect_1_active = True
            explosion.size_modifier = 0.75
            explosions.add(explosion)
            bullet.kill()
            if not PLAYER_1.effect_1_active:
              PLAYER_1_BASE.activated = False
              PLAYER_1.lives = PLAYER_1.lives - 1
              PLAYER_1.set_location(GAME_CONSTANTS['SCREEN_WIDTH'] / 4, GAME_CONSTANTS['SCREEN_HEIGHT'] / 2 - GAME_CONSTANTS['SQUARE_SIZE'])
              PLAYER_1.set_rotation(270)
              PLAYER_1.speed = 64
              PLAYER_1.effect_1_ttl = 3000
              PLAYER_1.effect_1_active = True
              dogfighting_base_creation_ttl = random.choice(range(TTL_DEFAULTS['BASE_CREATION_MIN'], TTL_DEFAULTS['BASE_CREATION_MAX']))
              if SOUND_EFFECT_EXPLOSION_2 != None:
                SOUND_EFFECT_EXPLOSION_2.stop()
                SOUND_EFFECT_EXPLOSION_2.set_volume(1.00)
                SOUND_EFFECT_EXPLOSION_2.play(loops=0)
            else:
              if SOUND_EFFECT_GROUND_HIT != None:
                SOUND_EFFECT_GROUND_HIT.stop()
                SOUND_EFFECT_GROUND_HIT.set_volume(0.65)
                SOUND_EFFECT_GROUND_HIT.play(loops=0)

      if PLAYER_2_BASE.activated:
        collisions = pygame.sprite.spritecollide(PLAYER_2_BASE, player_1_bullets, False, collided=pygame.sprite.collide_circle_ratio(0.55))
        for bullet in collisions:
          if bullet.bomb and bullet.size_modifier <= 0.25:
            explosion = GameSprite(bullet.x, bullet.y, 0, 0, bullet.rotation, 0, GAME_SURFACES['PIXEL_SHMUP_TILES']['STAR_SHOT'])
            explosion.effect_1_ttl = 350
            explosion.effect_2_ttl = 150
            explosion.effect_3_ttl = 150
            explosion.effect_1_active = True
            explosion.size_modifier = 0.75
            explosions.add(explosion)
            bullet.kill()
            if not PLAYER_2.effect_1_active:
              PLAYER_2_BASE.activated = False
              PLAYER_2.lives = PLAYER_2.lives - 1
              PLAYER_2.set_location((GAME_CONSTANTS['SCREEN_WIDTH'] / 4) * 3, GAME_CONSTANTS['SCREEN_HEIGHT'] / 2 - GAME_CONSTANTS['SQUARE_SIZE'])
              PLAYER_2.set_rotation(90)
              PLAYER_2.speed = 64
              PLAYER_2.effect_1_ttl = 3000
              PLAYER_2.effect_1_active = True
              dogfighting_base_creation_ttl = random.choice(range(TTL_DEFAULTS['BASE_CREATION_MIN'], TTL_DEFAULTS['BASE_CREATION_MAX']))
              if SOUND_EFFECT_EXPLOSION_2 != None:
                SOUND_EFFECT_EXPLOSION_2.stop()
                SOUND_EFFECT_EXPLOSION_2.set_volume(1.00)
                SOUND_EFFECT_EXPLOSION_2.play(loops=0)
            else:
              if SOUND_EFFECT_GROUND_HIT != None:
                SOUND_EFFECT_GROUND_HIT.stop()
                SOUND_EFFECT_GROUND_HIT.set_volume(0.65)
                SOUND_EFFECT_GROUND_HIT.play(loops=0)

      for explosion in reversed(explosions.sprites()):
        if explosion.effect_1_active and explosion.effect_1_ttl <= 0:
          explosion.effect_1_active = False
          explosion.effect_2_active = True
          explosion.set_image(GAME_SURFACES['PIXEL_SHMUP_TILES']['EXPLOSION'])
        elif explosion.effect_1_active:
          explosion.effect_1_ttl = explosion.effect_1_ttl - ELAPSED_MS
        
        if explosion.effect_2_active and explosion.effect_2_ttl <= 0:
          explosion.effect_2_active = False
          explosion.effect_3_active = True
          explosion.set_image(GAME_SURFACES['PIXEL_SHMUP_TILES']['EXPLOSION_SMOKE'])
        elif explosion.effect_2_active:
          explosion.effect_2_ttl = explosion.effect_2_ttl - ELAPSED_MS

        if explosion.effect_3_active and explosion.effect_3_ttl <= 0:
          explosion.kill()
        elif explosion.effect_3_active:
          explosion.effect_3_ttl = explosion.effect_3_ttl - ELAPSED_MS

      ### DISPLAY THE GRAPHICS
      if GAME_STATE['LAYER_2']:
        if PLAYER_1_BASE.activated:
          THE_SCREEN.blit(PLAYER_1_BASE.image, PLAYER_1_BASE.image.get_rect(topleft = (PLAYER_1_BASE.x, PLAYER_1_BASE.y)))
        if PLAYER_2_BASE.activated:
          THE_SCREEN.blit(PLAYER_2_BASE.image, PLAYER_2_BASE.image.get_rect(topleft = (PLAYER_2_BASE.x, PLAYER_2_BASE.y)))

      if PLAYER_1.lives <= 0 or PLAYER_2.lives <= 0:
        if MUSIC_DOG_FIGHTING != None:
          MUSIC_DOG_FIGHTING.fadeout(MUSIC_FADE_OUT)

        dogfighting_pvp_active = False
        if PLAYER_1.lives > PLAYER_2.lives:
          ace = ""
          if PLAYER_1.lives == GAME_MODE_OPTIONS['LIVES_COUNT']:
            ace = "*****ACE*****"
            if SOUND_EFFECT_OBJECTIVE_ACHIEVED != None:
              SOUND_EFFECT_OBJECTIVE_ACHIEVED.stop()
              SOUND_EFFECT_OBJECTIVE_ACHIEVED.set_volume(0.65)
              SOUND_EFFECT_OBJECTIVE_ACHIEVED.play(loops=0)
          create_alert(GAME_COLORS['SHMUP_RED'], GAME_FONTS['KENNEY_MINI_SQUARE_80'], "PLAYER 1 WINS!", ace, 4750, False, 0)
        elif PLAYER_1.lives < PLAYER_2.lives:
          ace = ""
          if PLAYER_2.lives == GAME_MODE_OPTIONS['LIVES_COUNT']:
            ace = "*****ACE*****"
            if SOUND_EFFECT_OBJECTIVE_ACHIEVED != None:
              SOUND_EFFECT_OBJECTIVE_ACHIEVED.stop()
              SOUND_EFFECT_OBJECTIVE_ACHIEVED.set_volume(0.65)
              SOUND_EFFECT_OBJECTIVE_ACHIEVED.play(loops=0)
          create_alert(GAME_COLORS['SHMUP_BLUE'], GAME_FONTS['KENNEY_MINI_SQUARE_80'], "PLAYER 2 WINS!", ace, 4750, False, 0)
        elif PLAYER_1.lives == PLAYER_2.lives:
          create_alert(GAME_COLORS['SHMUP_ORANGE'], GAME_FONTS['KENNEY_MINI_SQUARE_96'], "DRAW!", "", 4750, False, 0)
        else:
          create_alert(GAME_COLORS['SHMUP_YELLOW'], GAME_FONTS['KENNEY_MINI_SQUARE_96'], "GAME STATE FAILURE", "", 4750, False, 0)
      else:
        ### DISPLAY THE BULLETS (if layer 3 is active!)
        if GAME_STATE['LAYER_3']:
          for bullet in (player_1_bullets.sprites()):
            temp_bullet = pygame.transform.rotozoom(bullet.image, bullet.rotation, bullet.size_modifier)
            THE_SCREEN.blit(temp_bullet, temp_bullet.get_rect(center = (bullet.x, bullet.y)))
          for bullet in (player_2_bullets.sprites()):
            temp_bullet = pygame.transform.rotozoom(bullet.image, bullet.rotation, bullet.size_modifier)
            THE_SCREEN.blit(temp_bullet, temp_bullet.get_rect(center = (bullet.x, bullet.y)))

        ### DISPLAY THE PLAYERS (if layer 4 is active!)
        if GAME_STATE['LAYER_4']:
          player_one_plane = pygame.transform.rotozoom(PLAYER_1.image, PLAYER_1.rotation, 1)
          THE_SCREEN.blit(player_one_plane, player_one_plane.get_rect(center = (PLAYER_1.x, PLAYER_1.y)))
          player_two_plane = pygame.transform.rotozoom(PLAYER_2.image, PLAYER_2.rotation, 1)
          THE_SCREEN.blit(player_two_plane, player_two_plane.get_rect(center = (PLAYER_2.x, PLAYER_2.y)))

        ### DISPLAY THE EXPLOSIONS (if layer 3 is active!)
        if GAME_STATE['LAYER_3']:
          for explosion in (explosions.sprites()):
            temp_explosion = pygame.transform.rotozoom(explosion.image, explosion.rotation, explosion.size_modifier)
            THE_SCREEN.blit(temp_explosion, temp_explosion.get_rect(center = (explosion.x, explosion.y)))

        total_sprite_objects = total_sprite_objects + 2 #(for the planes)
        total_sprite_objects = total_sprite_objects + len(player_1_bullets.sprites())
        total_sprite_objects = total_sprite_objects + len(player_2_bullets.sprites())
        total_sprite_objects = total_sprite_objects + len(explosions.sprites())

    elif PLAYER_1.lives != 0 and PLAYER_2.lives != 0:
      if dogfighting_pvp_ready_ttl > 0:
        dogfighting_pvp_ready_ttl = dogfighting_pvp_ready_ttl - ELAPSED_MS
        size_zoom = dogfighting_pvp_ready_ttl / TTL_DEFAULTS['READY']
        if size_zoom < 0.45:
          size_zoom = 0.45
        ready = GAME_FONTS['KENNEY_MINI_SQUARE_96'].render(f"READY", True, GAME_COLORS['SHMUP_PURPLE'])
        ready = pygame.transform.rotozoom(ready, 0, size_zoom)
        THE_SCREEN.blit(ready, ready.get_rect(center = (GAME_CONSTANTS['SCREEN_WIDTH'] / 2, GAME_CONSTANTS['SCREEN_HEIGHT'] / 3)))
      elif dogfighting_pvp_set_ttl > 0:
        dogfighting_pvp_set_ttl = dogfighting_pvp_set_ttl - ELAPSED_MS
        size_zoom = dogfighting_pvp_set_ttl / TTL_DEFAULTS['SET']
        if size_zoom < 0.45:
          size_zoom = 0.45
        set_text = GAME_FONTS['KENNEY_MINI_SQUARE_96'].render(f"SET", True, GAME_COLORS['SHMUP_ORANGE'])
        set_text = pygame.transform.rotozoom(set_text, 0, size_zoom)
        THE_SCREEN.blit(set_text, set_text.get_rect(center = (GAME_CONSTANTS['SCREEN_WIDTH'] / 2, GAME_CONSTANTS['SCREEN_HEIGHT'] / 3)))
      elif dogfighting_pvp_fight_ttl > 0:
        dogfighting_pvp_fight_ttl = dogfighting_pvp_fight_ttl - ELAPSED_MS
        if not dogfighting_pvp_fight_shown:
          dogfighting_pvp_fight_shown = True
          # if SOUND_EFFECT_FIGHT != None:
          #   SOUND_EFFECT_FIGHT.stop()
          #   SOUND_EFFECT_FIGHT.set_volume(1.00)
          #   SOUND_EFFECT_FIGHT.play(loops=0)
        size_zoom = 1.0
        if(dogfighting_pvp_fight_ttl > 150):
          size_zoom = 1.0 + 1 / (dogfighting_pvp_fight_ttl / TTL_DEFAULTS['FIGHT'])
        else:
          size_zoom  = 7.5
        if size_zoom > 3.0:
          size_zoom = 3.0
        alpha_blend = (dogfighting_pvp_fight_ttl / TTL_DEFAULTS['FIGHT']) * 255
        fight = GAME_FONTS['KENNEY_MINI_SQUARE_96'].render(f"FIGHT!", True, GAME_COLORS['SHMUP_RED'])
        fight = pygame.transform.rotozoom(fight, 0, size_zoom)
        fight.set_alpha(alpha_blend)
        THE_SCREEN.blit(fight, fight.get_rect(center = (GAME_CONSTANTS['SCREEN_WIDTH'] / 2, GAME_CONSTANTS['SCREEN_HEIGHT'] / 3)))
      else:
        dogfighting_pvp_active = True
    else:        #DOG FIGHT IS OVER AND SOMEONE WON!  EXECUTE TRANSITION
      if GAME_STATE['LAYER_4']:
        if PLAYER_1.lives > 0:
          PLAYER_1.set_alpha(255)
          player_one_plane = pygame.transform.rotozoom(PLAYER_1.image, PLAYER_1.rotation, 1)
          THE_SCREEN.blit(player_one_plane, player_one_plane.get_rect(center = (PLAYER_1.x, PLAYER_1.y)))
        if PLAYER_2.lives > 0:
          PLAYER_2.set_alpha(255)
          player_two_plane = pygame.transform.rotozoom(PLAYER_2.image, PLAYER_2.rotation, 1)
          THE_SCREEN.blit(player_two_plane, player_two_plane.get_rect(center = (PLAYER_2.x, PLAYER_2.y)))

      ### DISPLAY THE EXPLOSIONS (if layer 3 is active!)
      if GAME_STATE['LAYER_3']:
        for explosion in (explosions.sprites()):
          temp_explosion = pygame.transform.rotozoom(explosion.image, explosion.rotation, explosion.size_modifier)
          THE_SCREEN.blit(temp_explosion, temp_explosion.get_rect(center = (explosion.x, explosion.y)))

      GAME_STATE['TRANSITION_TO_TITLE_SCREEN'] = True
      if GAME_STATE['TRANSITION_TO_TITLE_SCREEN']:
        GAME_STATE_TRANSITION_TTL['TRANSITION_TO_TITLE_SCREEN'] = GAME_STATE_TRANSITION_TTL['TRANSITION_TO_TITLE_SCREEN'] - ELAPSED_MS
        if GAME_STATE_TRANSITION_TTL['TRANSITION_TO_TITLE_SCREEN'] <= 0:
          initialize_title_screen()

  ####################################################################
  # Draw Layer One (The Map Tiles)
  #
  #
  ####################################################################
  # if GAME_STATE['LAYER_1']:
  #   a = 1


  ####################################################################
  # Draw the HUD (Heads Up Display)
  #
  # This is the last (before debug) set of things to add to the
  # screen.  This is here because we want this on top of everything
  # else from the game.
  ####################################################################
  if GAME_STATE['LAYER_5']:
    #Top HUD
    pygame.draw.rect(THE_SCREEN, GAME_COLORS['STEEL_BLUE'], pygame.Rect(0,0,1280,32))

    top_hud_player_one = GAME_FONTS['KENNEY_MINI_SQUARE_32'].render(f"PLAYER 1", True, GAME_COLORS['ALMOST_BLACK'])
    THE_SCREEN.blit(top_hud_player_one, top_hud_player_one.get_rect(topleft = (16, -6)))

    player_one_life_5 = GAME_SURFACES['PIXEL_SHMUP_SHIPS']['RED_B_FIGHTER_GRAY']
    player_one_life_4 = GAME_SURFACES['PIXEL_SHMUP_SHIPS']['RED_B_FIGHTER_GRAY']
    player_one_life_3 = GAME_SURFACES['PIXEL_SHMUP_SHIPS']['RED_B_FIGHTER_GRAY']
    player_one_life_2 = GAME_SURFACES['PIXEL_SHMUP_SHIPS']['RED_B_FIGHTER_GRAY']
    player_one_life_1 = GAME_SURFACES['PIXEL_SHMUP_SHIPS']['RED_B_FIGHTER_GRAY']

    if PLAYER_1.lives > 4:
      player_one_life_5 = GAME_SURFACES['PIXEL_SHMUP_SHIPS']['RED_B_FIGHTER']
    if PLAYER_1.lives > 3:
      player_one_life_4 = GAME_SURFACES['PIXEL_SHMUP_SHIPS']['RED_B_FIGHTER']
    if PLAYER_1.lives > 2:
      player_one_life_3 = GAME_SURFACES['PIXEL_SHMUP_SHIPS']['RED_B_FIGHTER']
    if PLAYER_1.lives > 1:
      player_one_life_2 = GAME_SURFACES['PIXEL_SHMUP_SHIPS']['RED_B_FIGHTER']
    if PLAYER_1.lives > 0:
      player_one_life_1 = GAME_SURFACES['PIXEL_SHMUP_SHIPS']['RED_B_FIGHTER']

    THE_SCREEN.blit(player_one_life_5, player_one_life_5.get_rect(topleft = (160, 0)))
    THE_SCREEN.blit(player_one_life_4, player_one_life_4.get_rect(topleft = (192, 0)))
    THE_SCREEN.blit(player_one_life_3, player_one_life_3.get_rect(topleft = (224, 0)))
    THE_SCREEN.blit(player_one_life_2, player_one_life_2.get_rect(topleft = (256, 0)))
    THE_SCREEN.blit(player_one_life_1, player_one_life_1.get_rect(topleft = (288, 0)))

    top_hud_player_two = GAME_FONTS['KENNEY_MINI_SQUARE_32'].render(f"PLAYER 2", True, GAME_COLORS['ALMOST_BLACK'])
    THE_SCREEN.blit(top_hud_player_two, top_hud_player_two.get_rect(topleft = (912, -6)))

    player_two_life_5 = GAME_SURFACES['PIXEL_SHMUP_SHIPS']['BLUE_B_FIGHTER_GRAY']
    player_two_life_4 = GAME_SURFACES['PIXEL_SHMUP_SHIPS']['BLUE_B_FIGHTER_GRAY']
    player_two_life_3 = GAME_SURFACES['PIXEL_SHMUP_SHIPS']['BLUE_B_FIGHTER_GRAY']
    player_two_life_2 = GAME_SURFACES['PIXEL_SHMUP_SHIPS']['BLUE_B_FIGHTER_GRAY']
    player_two_life_1 = GAME_SURFACES['PIXEL_SHMUP_SHIPS']['BLUE_B_FIGHTER_GRAY']

    if PLAYER_2.lives > 4:
      player_two_life_5 = GAME_SURFACES['PIXEL_SHMUP_SHIPS']['BLUE_B_FIGHTER']
    if PLAYER_2.lives > 3:
      player_two_life_4 = GAME_SURFACES['PIXEL_SHMUP_SHIPS']['BLUE_B_FIGHTER']
    if PLAYER_2.lives > 2:
      player_two_life_3 = GAME_SURFACES['PIXEL_SHMUP_SHIPS']['BLUE_B_FIGHTER']
    if PLAYER_2.lives > 1:
      player_two_life_2 = GAME_SURFACES['PIXEL_SHMUP_SHIPS']['BLUE_B_FIGHTER']
    if PLAYER_2.lives > 0:
      player_two_life_1 = GAME_SURFACES['PIXEL_SHMUP_SHIPS']['BLUE_B_FIGHTER']

    THE_SCREEN.blit(player_two_life_5, player_two_life_5.get_rect(topleft = (1056+16, 0)))
    THE_SCREEN.blit(player_two_life_4, player_two_life_4.get_rect(topleft = (1088+16, 0)))
    THE_SCREEN.blit(player_two_life_3, player_two_life_3.get_rect(topleft = (1120+16, 0)))
    THE_SCREEN.blit(player_two_life_2, player_two_life_2.get_rect(topleft = (1152+16, 0)))
    THE_SCREEN.blit(player_two_life_1, player_two_life_1.get_rect(topleft = (1184+16, 0)))
    
    top_hud_high_score_text = GAME_FONTS['KENNEY_MINI_SQUARE_32'].render(f"HI-SCORE:", True, GAME_COLORS['ALMOST_BLACK'])
    THE_SCREEN.blit(top_hud_high_score_text, top_hud_high_score_text.get_rect(topleft = (480, -6)))

    top_hud_high_score = GAME_FONTS['KENNEY_MINI_SQUARE_32'].render(f"000000000", True, GAME_COLORS['ALMOST_BLACK'])
    THE_SCREEN.blit(top_hud_high_score, top_hud_high_score.get_rect(topleft = (640, -6)))

    #Mini Map HUD


    #Bottom HUD
    pygame.draw.rect(THE_SCREEN, GAME_COLORS['STEEL_BLUE'], pygame.Rect(0,640,1280,80))

    #If we're in DOGFIGHT_MODE, then show the lower HUD with the cooldowns for the planes
    if GAME_STATE['DOGFIGHT_MODE']:
      player_1_weapon_1 = GAME_SURFACES['UI_PACK']['GREY']['BUTTON_SQUARE_FLAT'].copy()
      player_1_weapon_1.blit(GAME_SURFACES['PIXEL_SHMUP_TILES']['SINGLE_SHOT'], GAME_SURFACES['PIXEL_SHMUP_TILES']['SINGLE_SHOT'].get_rect(center=(32,32)))
      player_1_weapon_1_cooldown_arc = pygame.Surface((128,128))
      cooldown_min = PLAYER_1.weapon_1_cooldown
      if cooldown_min < 0:
        cooldown_min = 0
      cooldown_math = (((PLAYER_1.weapon_1_cooldown_default - cooldown_min) / PLAYER_1.weapon_1_cooldown_default)) * 360
      pygame.draw.arc(player_1_weapon_1_cooldown_arc, GAME_COLORS['SHMUP_GRAY'], player_1_weapon_1_cooldown_arc.get_rect(center=(64,64)), math.radians(90), math.radians(cooldown_math+90), 64)
      player_1_weapon_1_cooldown_arc.set_alpha(128)
      player_1_weapon_1.blit(player_1_weapon_1_cooldown_arc, player_1_weapon_1_cooldown_arc.get_rect(center=(32,32)))
      THE_SCREEN.blit(player_1_weapon_1, player_1_weapon_1.get_rect(center=(GAME_CONSTANTS['SQUARE_SIZE']*2.5,GAME_CONSTANTS['SCREEN_HEIGHT']-40)))

      player_1_weapon_2 = GAME_SURFACES['UI_PACK']['GREY']['BUTTON_SQUARE_FLAT'].copy()
      player_1_weapon_2.blit(GAME_SURFACES['PIXEL_SHMUP_TILES']['SINGLE_BOMB'], GAME_SURFACES['PIXEL_SHMUP_TILES']['SINGLE_BOMB'].get_rect(center=(32,32)))
      player_1_weapon_2_cooldown_arc = pygame.Surface((128,128))
      cooldown_min = PLAYER_1.weapon_2_cooldown
      if cooldown_min < 0:
        cooldown_min = 0
      cooldown_math = (((PLAYER_1.weapon_2_cooldown_default - cooldown_min) / PLAYER_1.weapon_2_cooldown_default)) * 360
      pygame.draw.arc(player_1_weapon_2_cooldown_arc, GAME_COLORS['SHMUP_GRAY'], player_1_weapon_2_cooldown_arc.get_rect(center=(64,64)), math.radians(90), math.radians(cooldown_math+90), 64)
      player_1_weapon_2_cooldown_arc.set_alpha(128)
      player_1_weapon_2.blit(player_1_weapon_2_cooldown_arc, player_1_weapon_2_cooldown_arc.get_rect(center=(32,32)))
      THE_SCREEN.blit(player_1_weapon_2, player_1_weapon_2.get_rect(center=(GAME_CONSTANTS['SQUARE_SIZE']*5.5,GAME_CONSTANTS['SCREEN_HEIGHT']-40)))

      player_1_throttle = pygame.transform.scale(GAME_SURFACES['UI_PACK']['RED']['CHECK_SQUARE_GREY'], (128, 32))
      max_speed_normalized = PLAYER_1.max_speed - PLAYER_1.min_speed
      speed_normalized = PLAYER_1.speed - PLAYER_1.min_speed
      throttle_math = 96 - (((max_speed_normalized - speed_normalized) / max_speed_normalized)) * 96
      player_1_throttle_value = pygame.transform.scale(GAME_SURFACES['UI_PACK']['RED']['CHECK_SQUARE_COLOR'], (throttle_math, 24))
      player_1_throttle.blit(player_1_throttle_value, player_1_throttle_value.get_rect(center=(64, 16)))
      THE_SCREEN.blit(player_1_throttle, player_1_throttle.get_rect(center=(GAME_CONSTANTS['SQUARE_SIZE']*9.5,GAME_CONSTANTS['SCREEN_HEIGHT']-40)))

      player_2_weapon_1 = GAME_SURFACES['UI_PACK']['GREY']['BUTTON_SQUARE_FLAT'].copy()
      player_2_weapon_1.blit(GAME_SURFACES['PIXEL_SHMUP_TILES']['SINGLE_SHOT'], GAME_SURFACES['PIXEL_SHMUP_TILES']['SINGLE_SHOT'].get_rect(center=(32,32)))
      player_2_weapon_1_cooldown_arc = pygame.Surface((128,128))
      cooldown_min = PLAYER_2.weapon_1_cooldown
      if cooldown_min < 0:
        cooldown_min = 0
      cooldown_math = (((PLAYER_2.weapon_1_cooldown_default - cooldown_min) / PLAYER_2.weapon_1_cooldown_default)) * 360
      pygame.draw.arc(player_2_weapon_1_cooldown_arc, GAME_COLORS['SHMUP_GRAY'], player_2_weapon_1_cooldown_arc.get_rect(center=(64,64)), math.radians(90), math.radians(cooldown_math+90), 64)
      player_2_weapon_1_cooldown_arc.set_alpha(128)
      player_2_weapon_1.blit(player_2_weapon_1_cooldown_arc, player_2_weapon_1_cooldown_arc.get_rect(center=(32,32)))
      THE_SCREEN.blit(player_2_weapon_1, player_2_weapon_1.get_rect(center=(GAME_CONSTANTS['SQUARE_SIZE']*29.5,GAME_CONSTANTS['SCREEN_HEIGHT']-40)))

      player_2_weapon_2 = GAME_SURFACES['UI_PACK']['GREY']['BUTTON_SQUARE_FLAT'].copy()
      player_2_weapon_2.blit(GAME_SURFACES['PIXEL_SHMUP_TILES']['SINGLE_BOMB'], GAME_SURFACES['PIXEL_SHMUP_TILES']['SINGLE_BOMB'].get_rect(center=(32,32)))
      player_2_weapon_2_cooldown_arc = pygame.Surface((128,128))
      cooldown_min = PLAYER_2.weapon_2_cooldown
      if cooldown_min < 0:
        cooldown_min = 0
      cooldown_math = (((PLAYER_2.weapon_2_cooldown_default - cooldown_min) / PLAYER_2.weapon_2_cooldown_default)) * 360
      pygame.draw.arc(player_2_weapon_2_cooldown_arc, GAME_COLORS['SHMUP_GRAY'], player_2_weapon_2_cooldown_arc.get_rect(center=(64,64)), math.radians(90), math.radians(cooldown_math+90), 64)
      player_2_weapon_2_cooldown_arc.set_alpha(128)
      player_2_weapon_2.blit(player_2_weapon_2_cooldown_arc, player_2_weapon_2_cooldown_arc.get_rect(center=(32,32)))
      THE_SCREEN.blit(player_2_weapon_2, player_2_weapon_2.get_rect(center=(GAME_CONSTANTS['SQUARE_SIZE']*32.5,GAME_CONSTANTS['SCREEN_HEIGHT']-40)))

      player_2_throttle = pygame.transform.scale(GAME_SURFACES['UI_PACK']['RED']['CHECK_SQUARE_GREY'], (128, 32))
      max_speed_normalized = PLAYER_2.max_speed - PLAYER_2.min_speed
      speed_normalized = PLAYER_2.speed - PLAYER_2.min_speed
      throttle_math = 96 - (((max_speed_normalized - speed_normalized) / max_speed_normalized)) * 96
      player_2_throttle_value = pygame.transform.scale(GAME_SURFACES['UI_PACK']['RED']['CHECK_SQUARE_COLOR'], (throttle_math, 24))
      player_2_throttle.blit(player_2_throttle_value, player_2_throttle_value.get_rect(center=(64, 16)))
      THE_SCREEN.blit(player_2_throttle, player_2_throttle.get_rect(center=(GAME_CONSTANTS['SQUARE_SIZE']*36.5,GAME_CONSTANTS['SCREEN_HEIGHT']-40)))

  ####################################################################
  # Draw ALERTS
  #
  # We want this on top of everything except for the debug
  ####################################################################
  if alert_active:
    if alert_ttl > 0:
      alert_ttl = alert_ttl - ELAPSED_MS
      alert_text_surface_1 = alert_font.render(f"{alert_txt_1}", True, alert_color)  
      alert_text_surface_2 = alert_font.render(f"{alert_txt_2}", True, alert_color)
      if alert_fadeout:
        alert_text_surface_1.set_alpha(int((alert_ttl / alert_fadeout_ttl) * 255))
        alert_text_surface_2.set_alpha(int((alert_ttl / alert_fadeout_ttl) * 255))

      if alert_txt_2 == "":
        THE_SCREEN.blit(alert_text_surface_1, alert_text_surface_1.get_rect(midtop = (GAME_CONSTANTS['SCREEN_WIDTH'] / 2, GAME_CONSTANTS['SQUARE_SIZE'] * 7)))
      else:
        THE_SCREEN.blit(alert_text_surface_1, alert_text_surface_1.get_rect(midtop = (GAME_CONSTANTS['SCREEN_WIDTH'] / 2, GAME_CONSTANTS['SQUARE_SIZE'] * 6)))
        THE_SCREEN.blit(alert_text_surface_2, alert_text_surface_2.get_rect(midtop = (GAME_CONSTANTS['SCREEN_WIDTH'] / 2, GAME_CONSTANTS['SQUARE_SIZE'] * 8)))
    else:
      destroy_alert()

  ####################################################################
  # Draw the DEBUG
  #
  # This is last, becasue we want all of this on top of everything
  # else!
  ####################################################################
  if GAME_STATE['DEBUG']:

    debug_x_offset = 0
    debug_y_offset = 80

    ######################################################################
    # Show "Game Information" that we care about
    #
    # Milliseconds elapsed between each frame
    #
    # ***LESSON***
    # A surface is created when the render method is called from our Font object.  Render takes in text, Anti-aliasing, color.
    # https://www.pygame.org/docs/ref/font.html#pygame.font.Font.render
    #
    # ***LESSON*** Blit - What is blitting?  Blit stands for 
    # Copies the contents of one surface to another.
    # In our example here, we are copying the contents of time_passed_ms_text_surface to our THE_SCREEN surface.
    # Effectively this will "paint" time_passed_ms_text_surface on THE_SCREEN in the location we tell it to (and we craete the rect for the surface and use that).

    #From my friend and pygame-ce maintainer - Andrew (oddbookworm) - from the pygame-ce community
    #It’s actually called “bit blit”, and it means “bit block transfer (bit blt)”. It’s a generic term for combining multiple bitmaps into one output bitmap using some set of bool operations.
    #Graphics however, has generally taken the name and replaced that definition with some form of mathematical operation, usually with some form of alpha compositing
    #I’d just call it block transfer. It’s not bit-wise, and alpha is complicated
    #it’s just easier to say blit than blt lol
    #Basic form: copies and pastes pixels and does no math (or rather, math is just pixel_out = pixel_in)
    #More advanced form: applies alphas from source and destination and blends the two together to create a composite image

    ######################################################################
    time_passed_ms_text_surface = GAME_FONTS['KENNEY_MINI_16'].render(f"{ELAPSED_MS}ms", True, GAME_COLORS['GREEN'])
    THE_SCREEN.blit(time_passed_ms_text_surface, time_passed_ms_text_surface.get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - 5 - debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - 494 - debug_y_offset)))

    total_sprite_objects_surface = GAME_FONTS['KENNEY_MINI_16'].render(f"Sprites: {total_sprite_objects}", True, GAME_COLORS['GREEN'])
    THE_SCREEN.blit(total_sprite_objects_surface, total_sprite_objects_surface.get_rect(bottomleft = (GAME_CONSTANTS['SCREEN_WIDTH'] - 128 - debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - 518 - debug_y_offset)))

    total_map_tiles_surface = GAME_FONTS['KENNEY_MINI_16'].render(f"Map Tiles: {total_map_tiles}", True, GAME_COLORS['GREEN'])
    THE_SCREEN.blit(total_map_tiles_surface, total_map_tiles_surface.get_rect(bottomleft = (GAME_CONSTANTS['SCREEN_WIDTH'] - 140 - debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - 534 - debug_y_offset)))

    ######################################################################
    # Show "Game Information" that we care about
    #
    # Camera details
    # *** LESSON ***
    ######################################################################
    game_state_running_text_surface = GAME_FONTS['KENNEY_MINI_16'].render(f"RUNNING", True, GAME_COLORS['NOT_QUITE_BLACK'])
    if GAME_STATE['RUNNING']:
      game_state_running_text_surface = GAME_FONTS['KENNEY_MINI_16'].render(f"RUNNING", True, GAME_COLORS['GREEN'])
    THE_SCREEN.blit(game_state_running_text_surface, game_state_running_text_surface.get_rect(bottomleft = (GAME_CONSTANTS['SCREEN_WIDTH'] - 512 - debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - 590 - debug_y_offset)))

    game_state_game_over_text_surface = GAME_FONTS['KENNEY_MINI_16'].render(f"GAME OVER", True, GAME_COLORS['NOT_QUITE_BLACK'])
    if GAME_STATE['GAME_OVER']:
      game_state_game_over_text_surface = GAME_FONTS['KENNEY_MINI_16'].render(f"GAME OVER", True, GAME_COLORS['GREEN'])
    THE_SCREEN.blit(game_state_game_over_text_surface, game_state_game_over_text_surface.get_rect(bottomleft = (GAME_CONSTANTS['SCREEN_WIDTH'] - 416 - debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - 590 - debug_y_offset)))

    game_state_paused_text_surface = GAME_FONTS['KENNEY_MINI_16'].render(f"PAUSED", True, GAME_COLORS['NOT_QUITE_BLACK'])
    if GAME_STATE['PAUSED']:
      game_state_paused_text_surface = GAME_FONTS['KENNEY_MINI_16'].render(f"PAUSED", True, GAME_COLORS['GREEN'])
    THE_SCREEN.blit(game_state_paused_text_surface, game_state_paused_text_surface.get_rect(bottomleft = (GAME_CONSTANTS['SCREEN_WIDTH'] - 288 - debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - 590 - debug_y_offset)))

    game_state_multiplayer_text_surface = GAME_FONTS['KENNEY_MINI_16'].render(f"MULTIPLAYER", True, GAME_COLORS['NOT_QUITE_BLACK'])
    if GAME_STATE['MULTIPLAYER']:
      game_state_multiplayer_text_surface = GAME_FONTS['KENNEY_MINI_16'].render(f"MULTIPLAYER", True, GAME_COLORS['GREEN'])
    THE_SCREEN.blit(game_state_multiplayer_text_surface, game_state_multiplayer_text_surface.get_rect(bottomleft = (GAME_CONSTANTS['SCREEN_WIDTH'] - 192 - debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - 590 - debug_y_offset)))

    game_state_lives_cheat_code_text_surface = GAME_FONTS['KENNEY_MINI_16'].render(f"LIVES CHEAT CODE", True, GAME_COLORS['NOT_QUITE_BLACK'])
    if GAME_STATE['LIVES_CHEAT_CODE']:
      game_state_lives_cheat_code_text_surface = GAME_FONTS['KENNEY_MINI_16'].render(f"MULTIPLAYER", True, GAME_COLORS['GREEN'])
    THE_SCREEN.blit(game_state_lives_cheat_code_text_surface, game_state_lives_cheat_code_text_surface.get_rect(bottomleft = (16 - debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - 590 - debug_y_offset)))

    game_state_title_screen_text_surface = GAME_FONTS['KENNEY_MINI_16'].render(f"TITLE SCREEN", True, GAME_COLORS['NOT_QUITE_BLACK'])
    if GAME_STATE['TITLE_SCREEN']:
      game_state_title_screen_text_surface = GAME_FONTS['KENNEY_MINI_16'].render(f"TITLE SCREEN", True, GAME_COLORS['GREEN'])
    THE_SCREEN.blit(game_state_title_screen_text_surface, game_state_running_text_surface.get_rect(bottomleft = (GAME_CONSTANTS['SCREEN_WIDTH'] - 672 - debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - 574 - debug_y_offset)))

    game_state_game_mode_text_surface = GAME_FONTS['KENNEY_MINI_16'].render(f"GAME MODE SCREEN", True, GAME_COLORS['NOT_QUITE_BLACK'])
    if GAME_STATE['GAME_MODE_SCREEN']:
      game_state_game_mode_text_surface = GAME_FONTS['KENNEY_MINI_16'].render(f"GAME MODE SCREEN", True, GAME_COLORS['GREEN'])
    THE_SCREEN.blit(game_state_game_mode_text_surface, game_state_game_mode_text_surface.get_rect(bottomleft = (GAME_CONSTANTS['SCREEN_WIDTH'] - 544 - debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - 574 - debug_y_offset)))

    game_state_game_instructions_text_surface = GAME_FONTS['KENNEY_MINI_16'].render(f"INSTRUCTIONS SCREEN", True, GAME_COLORS['NOT_QUITE_BLACK'])
    if GAME_STATE['INSTRUCTIONS_SCREEN']:
      game_state_game_instructions_text_surface = GAME_FONTS['KENNEY_MINI_16'].render(f"INSTRUCTIONS SCREEN", True, GAME_COLORS['GREEN'])
    THE_SCREEN.blit(game_state_game_instructions_text_surface, game_state_game_instructions_text_surface.get_rect(bottomleft = (GAME_CONSTANTS['SCREEN_WIDTH'] - 352 - debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - 574 - debug_y_offset)))

    game_state_game_over_screen_text_surface = GAME_FONTS['KENNEY_MINI_16'].render(f"GAME OVER SCREEN", True, GAME_COLORS['NOT_QUITE_BLACK'])
    if GAME_STATE['GAME_OVER_SCREEN']:
      game_state_game_over_screen_text_surface = GAME_FONTS['KENNEY_MINI_16'].render(f"GAME OVER SCREEN", True, GAME_COLORS['GREEN'])
    THE_SCREEN.blit(game_state_game_over_screen_text_surface, game_state_game_over_screen_text_surface.get_rect(bottomleft = (GAME_CONSTANTS['SCREEN_WIDTH'] - 160 - debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - 574 - debug_y_offset)))

    game_state_dogfight_text_surface = GAME_FONTS['KENNEY_MINI_16'].render(f"DOGFIGHT MODE", True, GAME_COLORS['NOT_QUITE_BLACK'])
    if GAME_STATE['DOGFIGHT_MODE']:
      game_state_dogfight_text_surface = GAME_FONTS['KENNEY_MINI_16'].render(f"DOGFIGHT MODE", True, GAME_COLORS['GREEN'])
    THE_SCREEN.blit(game_state_dogfight_text_surface, game_state_dogfight_text_surface.get_rect(bottomleft = (GAME_CONSTANTS['SCREEN_WIDTH'] - 448 - debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - 558 - debug_y_offset)))

    game_state_mission_text_surface = GAME_FONTS['KENNEY_MINI_16'].render(f"MISSION MODE", True, GAME_COLORS['NOT_QUITE_BLACK'])
    if GAME_STATE['MISSION_MODE']:
      game_state_mission_text_surface = GAME_FONTS['KENNEY_MINI_16'].render(f"MISSION MODE", True, GAME_COLORS['GREEN'])
    THE_SCREEN.blit(game_state_mission_text_surface, game_state_mission_text_surface.get_rect(bottomleft = (GAME_CONSTANTS['SCREEN_WIDTH'] - 288 - debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - 558 - debug_y_offset)))

    game_state_arena_text_surface = GAME_FONTS['KENNEY_MINI_16'].render(f"ARENA MODE", True, GAME_COLORS['NOT_QUITE_BLACK'])
    if GAME_STATE['ARENA_MODE']:
      game_state_arena_text_surface = GAME_FONTS['KENNEY_MINI_16'].render(f"ARENA MODE", True, GAME_COLORS['GREEN'])
    THE_SCREEN.blit(game_state_arena_text_surface, game_state_arena_text_surface.get_rect(bottomleft = (GAME_CONSTANTS['SCREEN_WIDTH'] - 128 - debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - 558 - debug_y_offset)))

    alert_active_surface = GAME_FONTS['KENNEY_MINI_16'].render(f"ALERT", True, GAME_COLORS['NOT_QUITE_BLACK'])
    if alert_active:
      alert_active_surface = GAME_FONTS['KENNEY_MINI_16'].render(f"ALERT", True, GAME_COLORS['GREEN'])
    THE_SCREEN.blit(alert_active_surface, alert_active_surface.get_rect(bottomleft = (GAME_CONSTANTS['SCREEN_WIDTH'] - 608 - debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - 494 - debug_y_offset)))

    game_layer_1_text_surface = GAME_FONTS['KENNEY_MINI_16'].render(f"LAYER 1", True, GAME_COLORS['NOT_QUITE_BLACK'])
    if GAME_STATE['LAYER_1']:
      game_layer_1_text_surface = GAME_FONTS['KENNEY_MINI_16'].render(f"LAYER 1", True, GAME_COLORS['GREEN'])
    THE_SCREEN.blit(game_layer_1_text_surface, game_layer_1_text_surface.get_rect(bottomleft = (GAME_CONSTANTS['SCREEN_WIDTH'] - 512 - debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - 494 - debug_y_offset)))

    game_layer_2_text_surface = GAME_FONTS['KENNEY_MINI_16'].render(f"LAYER 2", True, GAME_COLORS['NOT_QUITE_BLACK'])
    if GAME_STATE['LAYER_2']:
      game_layer_2_text_surface = GAME_FONTS['KENNEY_MINI_16'].render(f"LAYER 2", True, GAME_COLORS['GREEN'])
    THE_SCREEN.blit(game_layer_2_text_surface, game_layer_2_text_surface.get_rect(bottomleft = (GAME_CONSTANTS['SCREEN_WIDTH'] - 416 - debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - 494 - debug_y_offset)))

    game_layer_3_text_surface = GAME_FONTS['KENNEY_MINI_16'].render(f"LAYER 3", True, GAME_COLORS['NOT_QUITE_BLACK'])
    if GAME_STATE['LAYER_3']:
      game_layer_3_text_surface = GAME_FONTS['KENNEY_MINI_16'].render(f"LAYER 3", True, GAME_COLORS['GREEN'])
    THE_SCREEN.blit(game_layer_3_text_surface, game_layer_3_text_surface.get_rect(bottomleft = (GAME_CONSTANTS['SCREEN_WIDTH'] - 320 - debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - 494 - debug_y_offset)))

    game_layer_4_text_surface = GAME_FONTS['KENNEY_MINI_16'].render(f"LAYER 4", True, GAME_COLORS['NOT_QUITE_BLACK'])
    if GAME_STATE['LAYER_4']:
      game_layer_4_text_surface = GAME_FONTS['KENNEY_MINI_16'].render(f"LAYER 4", True, GAME_COLORS['GREEN'])
    THE_SCREEN.blit(game_layer_4_text_surface, game_layer_4_text_surface.get_rect(bottomleft = (GAME_CONSTANTS['SCREEN_WIDTH'] - 224 - debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - 494 - debug_y_offset)))

    game_layer_5_text_surface = GAME_FONTS['KENNEY_MINI_16'].render(f"LAYER 5", True, GAME_COLORS['NOT_QUITE_BLACK'])
    if GAME_STATE['LAYER_5']:
      game_layer_5_text_surface = GAME_FONTS['KENNEY_MINI_16'].render(f"LAYER 5", True, GAME_COLORS['GREEN'])
    THE_SCREEN.blit(game_layer_5_text_surface, game_layer_5_text_surface.get_rect(bottomleft = (GAME_CONSTANTS['SCREEN_WIDTH'] - 128 - debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - 494 - debug_y_offset)))

    camera_text_surface = GAME_FONTS['KENNEY_MINI_16'].render(f"CAMERA X: {CAMERA['X']}", True, GAME_COLORS['GREEN'])
    THE_SCREEN.blit(camera_text_surface, camera_text_surface.get_rect(bottomleft = (GAME_CONSTANTS['SCREEN_WIDTH'] - 170 - debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - 464 - debug_y_offset)))
    camera_text_surface = GAME_FONTS['KENNEY_MINI_16'].render(f"CAMERA Y: {CAMERA['Y']}", True, GAME_COLORS['GREEN'])
    THE_SCREEN.blit(camera_text_surface, camera_text_surface.get_rect(bottomleft = (GAME_CONSTANTS['SCREEN_WIDTH'] - 170 - debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - 446 - debug_y_offset)))

    ######################################################################
    # Show the Player Information
    ######################################################################
    # PLAYER_1.activated

    ######################################################################
    # Show the Player Controls Debug
    ######################################################################

    wasd_debug_x_offset = 152 + debug_x_offset
    wasd_debug_y_offset = 3 + debug_y_offset

    arrow_debug_x_offset = 48 + debug_x_offset
    arrow_debug_y_offset = 3 + debug_y_offset

    left_shift_debug_x_offset = 222 + debug_x_offset
    left_shift_debug_y_offset = 126 + debug_y_offset

    front_slash_debug_x_offset = 58 + debug_x_offset
    front_slash_debug_y_offset = 126 + debug_y_offset

    right_shift_debug_x_offset = -2 + debug_x_offset
    right_shift_debug_y_offset = 126 + debug_y_offset

    left_ctrl_debug_x_offset = 222 + debug_x_offset
    left_ctrl_debug_y_offset = 96 + debug_y_offset

    left_alt_debug_x_offset = 170 + debug_x_offset
    left_alt_debug_y_offset = 96 + debug_y_offset

    right_alt_debug_x_offset = 32 + debug_x_offset
    right_alt_debug_y_offset = 96 + debug_y_offset

    right_ctrl_debug_x_offset = -12 + debug_x_offset
    right_ctrl_debug_y_offset = 96 + debug_y_offset

    if GAME_STATE['MULTIPLAYER']:
      wasd_debug_x_offset = 1188 + debug_x_offset
      wasd_debug_y_offset = 67 + debug_y_offset

      arrow_debug_x_offset = 3 + debug_x_offset
      arrow_debug_y_offset = 67 + debug_y_offset

      left_shift_debug_x_offset = 1212 + debug_x_offset
      left_shift_debug_y_offset = 174 + debug_y_offset

      front_slash_debug_x_offset = 66 + debug_x_offset
      front_slash_debug_y_offset = 174 + debug_y_offset

      right_shift_debug_x_offset = 6 + debug_x_offset
      right_shift_debug_y_offset = 174 + debug_y_offset

      left_ctrl_debug_x_offset = 1212 + debug_x_offset
      left_ctrl_debug_y_offset = 144 + debug_y_offset

      left_alt_debug_x_offset = 1160 + debug_x_offset
      left_alt_debug_y_offset = 144 + debug_y_offset

      right_alt_debug_x_offset = 40 + debug_x_offset
      right_alt_debug_y_offset = 144 + debug_y_offset

      right_ctrl_debug_x_offset = -4 + debug_x_offset
      right_ctrl_debug_y_offset = 144 + debug_y_offset  

    # Show input keys from keyboard

    # WASD KEYS
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

    # ARROW KEYS
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

    # SHIFT / CTRLl / AlT / SPACEBAR 
    if GAME_CONTROLS['left_shift']:
      THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['SHIFT_WHITE'], GAME_SURFACES['INPUT_PROMPTS']['SHIFT_WHITE'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - left_shift_debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - left_shift_debug_y_offset)))
    else:
      THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['SHIFT_GRAY'], GAME_SURFACES['INPUT_PROMPTS']['SHIFT_GRAY'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - left_shift_debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - left_shift_debug_y_offset)))

    if GAME_CONTROLS['left_ctrl']:
      THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['CTRL_WHITE'], GAME_SURFACES['INPUT_PROMPTS']['CTRL_WHITE'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - left_ctrl_debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - left_ctrl_debug_y_offset)))
    else:
      THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['CTRL_GRAY'], GAME_SURFACES['INPUT_PROMPTS']['CTRL_GRAY'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - left_ctrl_debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - left_ctrl_debug_y_offset)))

    if GAME_CONTROLS['left_alt']:
      THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['ALT_WHITE'], GAME_SURFACES['INPUT_PROMPTS']['ALT_WHITE'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - left_alt_debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - left_alt_debug_y_offset)))
    else:
      THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['ALT_GRAY'], GAME_SURFACES['INPUT_PROMPTS']['ALT_GRAY'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - left_alt_debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - left_alt_debug_y_offset)))

    if GAME_CONTROLS['front_slash']:
      THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['FRONT_SLASH_WHITE'], GAME_SURFACES['INPUT_PROMPTS']['FRONT_SLASH_WHITE'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - front_slash_debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - front_slash_debug_y_offset)))
    else:
      THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['FRONT_SLASH_GRAY'], GAME_SURFACES['INPUT_PROMPTS']['FRONT_SLASH_GRAY'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - front_slash_debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - front_slash_debug_y_offset)))

    if GAME_CONTROLS['right_shift']:
      THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['SHIFT_WHITE'], GAME_SURFACES['INPUT_PROMPTS']['SHIFT_WHITE'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - right_shift_debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - right_shift_debug_y_offset)))
    else:
      THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['SHIFT_GRAY'], GAME_SURFACES['INPUT_PROMPTS']['SHIFT_GRAY'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - right_shift_debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - right_shift_debug_y_offset)))

    if GAME_CONTROLS['right_ctrl']:
      THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['CTRL_WHITE'], GAME_SURFACES['INPUT_PROMPTS']['CTRL_WHITE'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - right_ctrl_debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - right_ctrl_debug_y_offset)))
    else:
      THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['CTRL_GRAY'], GAME_SURFACES['INPUT_PROMPTS']['CTRL_GRAY'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - right_ctrl_debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - right_ctrl_debug_y_offset)))

    if GAME_CONTROLS['right_alt']:
      THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['ALT_WHITE'], GAME_SURFACES['INPUT_PROMPTS']['ALT_WHITE'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - right_alt_debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - right_alt_debug_y_offset)))
    else:
      THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['ALT_GRAY'], GAME_SURFACES['INPUT_PROMPTS']['ALT_GRAY'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - right_alt_debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - right_alt_debug_y_offset)))

    if not GAME_STATE['MULTIPLAYER']:
      spacebar_debug_x_offset = 94 + debug_x_offset
      spacebar_debug_y_offset = 96 + debug_y_offset
      if GAME_CONTROLS['space_bar']:
        THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['SPACEBAR_WHITE'], GAME_SURFACES['INPUT_PROMPTS']['SPACEBAR_WHITE'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - spacebar_debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - spacebar_debug_y_offset)))
      else:
        THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['SPACEBAR_GRAY'], GAME_SURFACES['INPUT_PROMPTS']['SPACEBAR_GRAY'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - spacebar_debug_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - spacebar_debug_y_offset)))

      #If we have a joystick plugged in, we will show the joystick controls
    
    if len(JOYSTICKS) > 0:
      if not GAME_STATE['MULTIPLAYER']:
        joystick_buttons_x_offset = 176 + debug_x_offset
        joystick_buttons_y_offset = 160 + debug_y_offset

        if GAME_CONTROLS['JOYSTICK_1']['controller_a'] or GAME_CONTROLS['JOYSTICK_2']['controller_a']:
          THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_A_GREEN_WHITE'], GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_A_GREEN_WHITE'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_buttons_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_buttons_y_offset)))
        else:
          THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_A_GRAY'], GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_A_GRAY'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_buttons_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_buttons_y_offset)))
        if GAME_CONTROLS['JOYSTICK_1']['controller_b'] or GAME_CONTROLS['JOYSTICK_2']['controller_b']:
          THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_B_RED_WHITE'], GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_B_RED_WHITE'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_buttons_x_offset + 32, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_buttons_y_offset)))
        else:
          THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_B_GRAY'], GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_B_GRAY'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_buttons_x_offset + 32, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_buttons_y_offset)))
        if GAME_CONTROLS['JOYSTICK_1']['controller_x'] or GAME_CONTROLS['JOYSTICK_2']['controller_x']:
          THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_X_BLUE_WHITE'], GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_X_BLUE_WHITE'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_buttons_x_offset + 64, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_buttons_y_offset)))
        else:
          THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_X_GRAY'], GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_X_GRAY'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_buttons_x_offset + 64, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_buttons_y_offset)))
        if GAME_CONTROLS['JOYSTICK_1']['controller_y'] or GAME_CONTROLS['JOYSTICK_2']['controller_y']:
          THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_Y_YELLOW_WHITE'], GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_Y_YELLOW_WHITE'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_buttons_x_offset + 96, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_buttons_y_offset)))
        else:
          THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_Y_GRAY'], GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_Y_GRAY'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_buttons_x_offset + 96, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_buttons_y_offset)))

        #Left Axis
        joystick_axis_x_offset = 256 + debug_x_offset
        joystick_axis_y_offset = 3 + debug_y_offset
        THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['JOY_AXIS_BASE_GRAY'], GAME_SURFACES['INPUT_PROMPTS']['JOY_AXIS_BASE_GRAY'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_axis_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_axis_y_offset)))
        THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['JOY_AXIS_DIRECTIONAL_WHITE'], GAME_SURFACES['INPUT_PROMPTS']['JOY_AXIS_DIRECTIONAL_WHITE'].get_rect(center = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_axis_x_offset - 15 + GAME_CONTROLS['JOYSTICK_2']['axis_0'] * 8, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_axis_y_offset - 16 + GAME_CONTROLS['JOYSTICK_2']['axis_1'] * 8)))
        THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['JOY_AXIS_DIRECTIONAL_WHITE'], GAME_SURFACES['INPUT_PROMPTS']['JOY_AXIS_DIRECTIONAL_WHITE'].get_rect(center = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_axis_x_offset - 15 + GAME_CONTROLS['JOYSTICK_1']['axis_0'] * 8, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_axis_y_offset - 16 + GAME_CONTROLS['JOYSTICK_1']['axis_1'] * 8)))

        #Right Axis
        joystick_axis_x_offset = 0 + debug_x_offset
        joystick_axis_y_offset = 3 + debug_y_offset
        THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['JOY_AXIS_BASE_GRAY'], GAME_SURFACES['INPUT_PROMPTS']['JOY_AXIS_BASE_GRAY'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_axis_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_axis_y_offset)))
        THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['JOY_AXIS_DIRECTIONAL_WHITE'], GAME_SURFACES['INPUT_PROMPTS']['JOY_AXIS_DIRECTIONAL_WHITE'].get_rect(center = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_axis_x_offset - 15 + GAME_CONTROLS['JOYSTICK_2']['axis_2'] * 8, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_axis_y_offset - 16 + GAME_CONTROLS['JOYSTICK_2']['axis_3'] * 8)))
        THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['JOY_AXIS_DIRECTIONAL_WHITE'], GAME_SURFACES['INPUT_PROMPTS']['JOY_AXIS_DIRECTIONAL_WHITE'].get_rect(center = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_axis_x_offset - 15 + GAME_CONTROLS['JOYSTICK_1']['axis_2'] * 8, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_axis_y_offset - 16 + GAME_CONTROLS['JOYSTICK_1']['axis_3'] * 8)))

        joystick_dpad_x_offset = 128 + debug_x_offset
        joystick_dpad_y_offset = 48 + debug_y_offset
        
        THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['JOY_DPAD_BASE_GRAY'], GAME_SURFACES['INPUT_PROMPTS']['JOY_DPAD_BASE_GRAY'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_dpad_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_dpad_y_offset)))
        for joystick_to_debug in JOYSTICKS:
          #Xbox Hat
          if JOYSTICKS[joystick_to_debug].get_name() == 'Xbox 360 Controller':
            if GAME_CONTROLS['JOYSTICK_1']['hat_up'] or GAME_CONTROLS['JOYSTICK_2']['hat_up']:
              THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['UP_ARROW_GOLD'], GAME_SURFACES['INPUT_PROMPTS']['UP_ARROW_GOLD'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_dpad_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_dpad_y_offset - 16)))
            if GAME_CONTROLS['JOYSTICK_1']['hat_down'] or GAME_CONTROLS['JOYSTICK_2']['hat_down']:
              THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['DOWN_ARROW_GOLD'], GAME_SURFACES['INPUT_PROMPTS']['DOWN_ARROW_GOLD'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_dpad_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_dpad_y_offset)))
            if GAME_CONTROLS['JOYSTICK_1']['hat_left'] or GAME_CONTROLS['JOYSTICK_2']['hat_left']:
              THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['LEFT_ARROW_GOLD'], GAME_SURFACES['INPUT_PROMPTS']['LEFT_ARROW_GOLD'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_dpad_x_offset - 16, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_dpad_y_offset)))
            if GAME_CONTROLS['JOYSTICK_1']['hat_right'] or GAME_CONTROLS['JOYSTICK_2']['hat_right']:
              THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['RIGHT_ARROW_GOLD'], GAME_SURFACES['INPUT_PROMPTS']['RIGHT_ARROW_GOLD'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_dpad_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_dpad_y_offset)))
          #PowerA D-Pad
          if JOYSTICKS[joystick_to_debug].get_name() == 'PowerA NSW Wired controller':
            if GAME_CONTROLS['JOYSTICK_1']['dpad_up'] or GAME_CONTROLS['JOYSTICK_2']['dpad_up']:
              THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['UP_ARROW_GOLD'], GAME_SURFACES['INPUT_PROMPTS']['UP_ARROW_GOLD'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_dpad_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_dpad_y_offset - 16)))
            if GAME_CONTROLS['JOYSTICK_1']['dpad_down'] or GAME_CONTROLS['JOYSTICK_2']['dpad_down']:
              THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['DOWN_ARROW_GOLD'], GAME_SURFACES['INPUT_PROMPTS']['DOWN_ARROW_GOLD'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_dpad_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_dpad_y_offset)))
            if GAME_CONTROLS['JOYSTICK_1']['dpad_left'] or GAME_CONTROLS['JOYSTICK_2']['dpad_left']:
              THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['LEFT_ARROW_GOLD'], GAME_SURFACES['INPUT_PROMPTS']['LEFT_ARROW_GOLD'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_dpad_x_offset - 16, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_dpad_y_offset)))
            if GAME_CONTROLS['JOYSTICK_1']['dpad_right'] or GAME_CONTROLS['JOYSTICK_2']['dpad_right']:
              THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['RIGHT_ARROW_GOLD'], GAME_SURFACES['INPUT_PROMPTS']['RIGHT_ARROW_GOLD'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_dpad_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_dpad_y_offset)))
      else: #MULTIPLAYER
        if JOYSTICKS.get(1) != None: #Player 2 has a controller plugged in
          joystick_1_buttons_x_offset = 1072 + debug_x_offset
          joystick_1_buttons_y_offset = 128 + debug_y_offset

          if GAME_CONTROLS['JOYSTICK_1']['controller_a']:
            THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_A_GREEN_WHITE'], GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_A_GREEN_WHITE'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_1_buttons_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_1_buttons_y_offset)))
          else:
            THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_A_GRAY'], GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_A_GRAY'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_1_buttons_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_1_buttons_y_offset)))
          if GAME_CONTROLS['JOYSTICK_1']['controller_b']:
            THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_B_RED_WHITE'], GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_B_RED_WHITE'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_1_buttons_x_offset + 32, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_1_buttons_y_offset)))
          else:
            THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_B_GRAY'], GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_B_GRAY'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_1_buttons_x_offset + 32, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_1_buttons_y_offset)))
          if GAME_CONTROLS['JOYSTICK_1']['controller_x']:
            THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_X_BLUE_WHITE'], GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_X_BLUE_WHITE'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_1_buttons_x_offset + 64, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_1_buttons_y_offset)))
          else:
            THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_X_GRAY'], GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_X_GRAY'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_1_buttons_x_offset + 64, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_1_buttons_y_offset)))
          if GAME_CONTROLS['JOYSTICK_1']['controller_y']:
            THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_Y_YELLOW_WHITE'], GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_Y_YELLOW_WHITE'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_1_buttons_x_offset + 96, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_1_buttons_y_offset)))
          else:
            THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_Y_GRAY'], GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_Y_GRAY'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_1_buttons_x_offset + 96, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_1_buttons_y_offset)))

          #Left Axis
          joystick_1_axis_x_offset = 1088 + debug_x_offset
          joystick_1_axis_y_offset = 96 + debug_y_offset
          THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['JOY_AXIS_BASE_GRAY'], GAME_SURFACES['INPUT_PROMPTS']['JOY_AXIS_BASE_GRAY'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_1_axis_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_1_axis_y_offset)))        
          THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['JOY_AXIS_DIRECTIONAL_WHITE'], GAME_SURFACES['INPUT_PROMPTS']['JOY_AXIS_DIRECTIONAL_WHITE'].get_rect(center = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_1_axis_x_offset - 15 + GAME_CONTROLS['JOYSTICK_1']['axis_0'] * 8, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_1_axis_y_offset - 16 + GAME_CONTROLS['JOYSTICK_1']['axis_1'] * 8)))

          #Right Axis
          joystick_1_axis_x_offset = 960 + debug_x_offset
          joystick_1_axis_y_offset = 96 + debug_y_offset
          THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['JOY_AXIS_BASE_GRAY'], GAME_SURFACES['INPUT_PROMPTS']['JOY_AXIS_BASE_GRAY'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_1_axis_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_1_axis_y_offset)))
          THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['JOY_AXIS_DIRECTIONAL_WHITE'], GAME_SURFACES['INPUT_PROMPTS']['JOY_AXIS_DIRECTIONAL_WHITE'].get_rect(center = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_1_axis_x_offset - 15 + GAME_CONTROLS['JOYSTICK_1']['axis_2'] * 8, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_1_axis_y_offset - 16 + GAME_CONTROLS['JOYSTICK_1']['axis_3'] * 8)))

          #D-Pad
          joystick_1_dpad_x_offset = 1024 + debug_x_offset
          joystick_1_dpad_y_offset = 96 + debug_y_offset
          THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['JOY_DPAD_BASE_GRAY'], GAME_SURFACES['INPUT_PROMPTS']['JOY_DPAD_BASE_GRAY'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_1_dpad_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_1_dpad_y_offset)))
          for joystick_1_to_debug in JOYSTICKS:
            #Xbox Hat
            if JOYSTICKS[joystick_1_to_debug].get_name() == 'Xbox 360 Controller':
              if GAME_CONTROLS['JOYSTICK_1']['hat_up']:
                THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['UP_ARROW_GOLD'], GAME_SURFACES['INPUT_PROMPTS']['UP_ARROW_GOLD'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_1_dpad_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_1_dpad_y_offset - 16)))
              if GAME_CONTROLS['JOYSTICK_1']['hat_down']:
                THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['DOWN_ARROW_GOLD'], GAME_SURFACES['INPUT_PROMPTS']['DOWN_ARROW_GOLD'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_1_dpad_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_1_dpad_y_offset)))
              if GAME_CONTROLS['JOYSTICK_1']['hat_left']:
                THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['LEFT_ARROW_GOLD'], GAME_SURFACES['INPUT_PROMPTS']['LEFT_ARROW_GOLD'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_1_dpad_x_offset - 16, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_1_dpad_y_offset)))
              if GAME_CONTROLS['JOYSTICK_1']['hat_right']:
                THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['RIGHT_ARROW_GOLD'], GAME_SURFACES['INPUT_PROMPTS']['RIGHT_ARROW_GOLD'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_1_dpad_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_1_dpad_y_offset)))
            #PowerA D-Pad
            if JOYSTICKS[joystick_1_to_debug].get_name() == 'PowerA NSW Wired controller':
              if GAME_CONTROLS['JOYSTICK_1']['dpad_up']:
                THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['UP_ARROW_GOLD'], GAME_SURFACES['INPUT_PROMPTS']['UP_ARROW_GOLD'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_1_dpad_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_1_dpad_y_offset - 16)))
              if GAME_CONTROLS['JOYSTICK_1']['dpad_down']:
                THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['DOWN_ARROW_GOLD'], GAME_SURFACES['INPUT_PROMPTS']['DOWN_ARROW_GOLD'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_1_dpad_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_1_dpad_y_offset)))
              if GAME_CONTROLS['JOYSTICK_1']['dpad_left']:
                THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['LEFT_ARROW_GOLD'], GAME_SURFACES['INPUT_PROMPTS']['LEFT_ARROW_GOLD'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_1_dpad_x_offset - 16, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_1_dpad_y_offset)))
              if GAME_CONTROLS['JOYSTICK_1']['dpad_right']:
                THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['RIGHT_ARROW_GOLD'], GAME_SURFACES['INPUT_PROMPTS']['RIGHT_ARROW_GOLD'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_1_dpad_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_1_dpad_y_offset)))

        if JOYSTICKS.get(2) != None: #Player 2 has a controller plugged in

          joystick_2_buttons_x_offset = 272 + debug_x_offset
          joystick_2_buttons_y_offset = 128 + debug_y_offset

          if GAME_CONTROLS['JOYSTICK_2']['controller_a']:
            THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_A_GREEN_WHITE'], GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_A_GREEN_WHITE'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_2_buttons_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_2_buttons_y_offset)))
          else:
            THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_A_GRAY'], GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_A_GRAY'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_2_buttons_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_2_buttons_y_offset)))
          if GAME_CONTROLS['JOYSTICK_2']['controller_b']:
            THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_B_RED_WHITE'], GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_B_RED_WHITE'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_2_buttons_x_offset + 32, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_2_buttons_y_offset)))
          else:
            THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_B_GRAY'], GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_B_GRAY'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_2_buttons_x_offset + 32, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_2_buttons_y_offset)))
          if GAME_CONTROLS['JOYSTICK_2']['controller_x']:
            THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_X_BLUE_WHITE'], GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_X_BLUE_WHITE'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_2_buttons_x_offset + 64, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_2_buttons_y_offset)))
          else:
            THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_X_GRAY'], GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_X_GRAY'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_2_buttons_x_offset + 64, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_2_buttons_y_offset)))
          if GAME_CONTROLS['JOYSTICK_2']['controller_y']:
            THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_Y_YELLOW_WHITE'], GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_Y_YELLOW_WHITE'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_2_buttons_x_offset + 96, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_2_buttons_y_offset)))
          else:
            THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_Y_GRAY'], GAME_SURFACES['INPUT_PROMPTS']['JOY_BUTTON_Y_GRAY'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_2_buttons_x_offset + 96, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_2_buttons_y_offset)))

          #Left Axis
          joystick_2_axis_x_offset = 288 + debug_x_offset
          joystick_2_axis_y_offset = 96 + debug_y_offset
          THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['JOY_AXIS_BASE_GRAY'], GAME_SURFACES['INPUT_PROMPTS']['JOY_AXIS_BASE_GRAY'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_2_axis_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_2_axis_y_offset)))        
          THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['JOY_AXIS_DIRECTIONAL_WHITE'], GAME_SURFACES['INPUT_PROMPTS']['JOY_AXIS_DIRECTIONAL_WHITE'].get_rect(center = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_2_axis_x_offset - 15 + GAME_CONTROLS['JOYSTICK_2']['axis_0'] * 8, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_2_axis_y_offset - 16 + GAME_CONTROLS['JOYSTICK_2']['axis_1'] * 8)))

          #Right Axis
          joystick_2_axis_x_offset = 160 + debug_x_offset
          joystick_2_axis_y_offset = 96 + debug_y_offset
          THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['JOY_AXIS_BASE_GRAY'], GAME_SURFACES['INPUT_PROMPTS']['JOY_AXIS_BASE_GRAY'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_2_axis_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_2_axis_y_offset)))
          THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['JOY_AXIS_DIRECTIONAL_WHITE'], GAME_SURFACES['INPUT_PROMPTS']['JOY_AXIS_DIRECTIONAL_WHITE'].get_rect(center = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_2_axis_x_offset - 15 + GAME_CONTROLS['JOYSTICK_2']['axis_2'] * 8, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_2_axis_y_offset - 16 + GAME_CONTROLS['JOYSTICK_2']['axis_3'] * 8)))

          #D-Pad
          joystick_2_dpad_x_offset = 224 + debug_x_offset
          joystick_2_dpad_y_offset = 96 + debug_y_offset
          THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['JOY_DPAD_BASE_GRAY'], GAME_SURFACES['INPUT_PROMPTS']['JOY_DPAD_BASE_GRAY'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_2_dpad_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_2_dpad_y_offset)))
          for joystick_2_to_debug in JOYSTICKS:
            #Xbox Hat
            if JOYSTICKS[joystick_2_to_debug].get_name() == 'Xbox 360 Controller':
              if GAME_CONTROLS['JOYSTICK_2']['hat_up']:
                THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['UP_ARROW_GOLD'], GAME_SURFACES['INPUT_PROMPTS']['UP_ARROW_GOLD'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_2_dpad_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_2_dpad_y_offset - 16)))
              if GAME_CONTROLS['JOYSTICK_2']['hat_down']:
                THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['DOWN_ARROW_GOLD'], GAME_SURFACES['INPUT_PROMPTS']['DOWN_ARROW_GOLD'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_2_dpad_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_2_dpad_y_offset)))
              if GAME_CONTROLS['JOYSTICK_2']['hat_left']:
                THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['LEFT_ARROW_GOLD'], GAME_SURFACES['INPUT_PROMPTS']['LEFT_ARROW_GOLD'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_2_dpad_x_offset - 16, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_2_dpad_y_offset)))
              if GAME_CONTROLS['JOYSTICK_2']['hat_right']:
                THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['RIGHT_ARROW_GOLD'], GAME_SURFACES['INPUT_PROMPTS']['RIGHT_ARROW_GOLD'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_2_dpad_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_2_dpad_y_offset)))
            #PowerA D-Pad
            if JOYSTICKS[joystick_2_to_debug].get_name() == 'PowerA NSW Wired controller':
              if GAME_CONTROLS['JOYSTICK_2']['dpad_up']:
                THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['UP_ARROW_GOLD'], GAME_SURFACES['INPUT_PROMPTS']['UP_ARROW_GOLD'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_2_dpad_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_2_dpad_y_offset - 16)))
              if GAME_CONTROLS['JOYSTICK_2']['dpad_down']:
                THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['DOWN_ARROW_GOLD'], GAME_SURFACES['INPUT_PROMPTS']['DOWN_ARROW_GOLD'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_2_dpad_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_2_dpad_y_offset)))
              if GAME_CONTROLS['JOYSTICK_2']['dpad_left']:
                THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['LEFT_ARROW_GOLD'], GAME_SURFACES['INPUT_PROMPTS']['LEFT_ARROW_GOLD'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_2_dpad_x_offset - 16, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_2_dpad_y_offset)))
              if GAME_CONTROLS['JOYSTICK_2']['dpad_right']:
                THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['RIGHT_ARROW_GOLD'], GAME_SURFACES['INPUT_PROMPTS']['RIGHT_ARROW_GOLD'].get_rect(bottomright = (GAME_CONSTANTS['SCREEN_WIDTH'] - joystick_2_dpad_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - joystick_2_dpad_y_offset)))

    #Show Actual Game Control Inputs for Player 1
    player_one_direction_x_offset = 10 + debug_x_offset
    player_one_direction_y_offset = 10 + debug_y_offset
    THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['DIRECTION_BASE'], GAME_SURFACES['INPUT_PROMPTS']['DIRECTION_BASE'].get_rect(bottomleft = (player_one_direction_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - player_one_direction_y_offset)))
    if GAME_CONTROLS['PLAYER_1']['UP']:
      THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['DIRECTION_UP_WHITE'], GAME_SURFACES['INPUT_PROMPTS']['DIRECTION_UP_WHITE'].get_rect(bottomleft = (player_one_direction_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - player_one_direction_y_offset)))
    if GAME_CONTROLS['PLAYER_1']['LEFT']:
      THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['DIRECTION_LEFT_WHITE'], GAME_SURFACES['INPUT_PROMPTS']['DIRECTION_LEFT_WHITE'].get_rect(bottomleft = (player_one_direction_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - player_one_direction_y_offset)))
    if GAME_CONTROLS['PLAYER_1']['DOWN']:
      THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['DIRECTION_DOWN_WHITE'], GAME_SURFACES['INPUT_PROMPTS']['DIRECTION_DOWN_WHITE'].get_rect(bottomleft = (player_one_direction_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - player_one_direction_y_offset)))
    if GAME_CONTROLS['PLAYER_1']['RIGHT']:
      THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['DIRECTION_RIGHT_WHITE'], GAME_SURFACES['INPUT_PROMPTS']['DIRECTION_RIGHT_WHITE'].get_rect(bottomleft = (player_one_direction_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - player_one_direction_y_offset)))

    player_one_game_buttons_x_offset = 48 + debug_x_offset
    player_one_game_buttons_y_offset = 8 + debug_y_offset
    if GAME_CONTROLS['PLAYER_1']['GREEN']:
      THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['GREEN_BUTTON_DOWN'], GAME_SURFACES['INPUT_PROMPTS']['GREEN_BUTTON_DOWN'].get_rect(bottomleft = (player_one_game_buttons_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - player_one_game_buttons_y_offset)))
    else:
      THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['GREEN_BUTTON_UP'], GAME_SURFACES['INPUT_PROMPTS']['GREEN_BUTTON_UP'].get_rect(bottomleft = (player_one_game_buttons_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - player_one_game_buttons_y_offset)))
    if GAME_CONTROLS['PLAYER_1']['RED']:
      THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['RED_BUTTON_DOWN'], GAME_SURFACES['INPUT_PROMPTS']['RED_BUTTON_DOWN'].get_rect(bottomleft = (player_one_game_buttons_x_offset + 32, GAME_CONSTANTS['SCREEN_HEIGHT'] - player_one_game_buttons_y_offset)))
    else:
      THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['RED_BUTTON_UP'], GAME_SURFACES['INPUT_PROMPTS']['RED_BUTTON_UP'].get_rect(bottomleft = (player_one_game_buttons_x_offset + 32, GAME_CONSTANTS['SCREEN_HEIGHT'] - player_one_game_buttons_y_offset)))
    if GAME_CONTROLS['PLAYER_1']['BLUE']:
      THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['BLUE_BUTTON_DOWN'], GAME_SURFACES['INPUT_PROMPTS']['BLUE_BUTTON_DOWN'].get_rect(bottomleft = (player_one_game_buttons_x_offset + 64, GAME_CONSTANTS['SCREEN_HEIGHT'] - player_one_game_buttons_y_offset)))
    else:
      THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['BLUE_BUTTON_UP'], GAME_SURFACES['INPUT_PROMPTS']['BLUE_BUTTON_UP'].get_rect(bottomleft = (player_one_game_buttons_x_offset + 64, GAME_CONSTANTS['SCREEN_HEIGHT'] - player_one_game_buttons_y_offset)))

    if GAME_CONTROLS['PLAYER_1']['YELLOW']:
      THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['YELLOW_BUTTON_DOWN'], GAME_SURFACES['INPUT_PROMPTS']['YELLOW_BUTTON_DOWN'].get_rect(bottomleft = (player_one_game_buttons_x_offset + 96, GAME_CONSTANTS['SCREEN_HEIGHT'] - player_one_game_buttons_y_offset)))
    else:
      THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['YELLOW_BUTTON_UP'], GAME_SURFACES['INPUT_PROMPTS']['YELLOW_BUTTON_UP'].get_rect(bottomleft = (player_one_game_buttons_x_offset + 96, GAME_CONSTANTS['SCREEN_HEIGHT'] - player_one_game_buttons_y_offset)))

    #If we are in multiplayer mode show actual game control inputs for Player 2
    if GAME_STATE['MULTIPLAYER']:
      player_two_direction_x_offset = 1098 + debug_x_offset
      player_two_direction_y_offset = 10 + debug_y_offset
      THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['DIRECTION_BASE'], GAME_SURFACES['INPUT_PROMPTS']['DIRECTION_BASE'].get_rect(bottomleft = (player_two_direction_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - player_two_direction_y_offset)))
      if GAME_CONTROLS['PLAYER_2']['UP']:
        THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['DIRECTION_UP_WHITE'], GAME_SURFACES['INPUT_PROMPTS']['DIRECTION_UP_WHITE'].get_rect(bottomleft = (player_two_direction_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - player_two_direction_y_offset)))
      if GAME_CONTROLS['PLAYER_2']['LEFT']:
        THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['DIRECTION_LEFT_WHITE'], GAME_SURFACES['INPUT_PROMPTS']['DIRECTION_LEFT_WHITE'].get_rect(bottomleft = (player_two_direction_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - player_two_direction_y_offset)))
      if GAME_CONTROLS['PLAYER_2']['DOWN']:
        THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['DIRECTION_DOWN_WHITE'], GAME_SURFACES['INPUT_PROMPTS']['DIRECTION_DOWN_WHITE'].get_rect(bottomleft = (player_two_direction_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - player_two_direction_y_offset)))
      if GAME_CONTROLS['PLAYER_2']['RIGHT']:
        THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['DIRECTION_RIGHT_WHITE'], GAME_SURFACES['INPUT_PROMPTS']['DIRECTION_RIGHT_WHITE'].get_rect(bottomleft = (player_two_direction_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - player_two_direction_y_offset)))

      player_two_game_buttons_x_offset = 1136 + debug_x_offset
      player_two_game_buttons_y_offset = 8 + debug_y_offset
      if GAME_CONTROLS['PLAYER_2']['GREEN']:
        THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['GREEN_BUTTON_DOWN'], GAME_SURFACES['INPUT_PROMPTS']['GREEN_BUTTON_DOWN'].get_rect(bottomleft = (player_two_game_buttons_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - player_two_game_buttons_y_offset)))
      else:
        THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['GREEN_BUTTON_UP'], GAME_SURFACES['INPUT_PROMPTS']['GREEN_BUTTON_UP'].get_rect(bottomleft = (player_two_game_buttons_x_offset, GAME_CONSTANTS['SCREEN_HEIGHT'] - player_two_game_buttons_y_offset)))
      if GAME_CONTROLS['PLAYER_2']['RED']:
        THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['RED_BUTTON_DOWN'], GAME_SURFACES['INPUT_PROMPTS']['RED_BUTTON_DOWN'].get_rect(bottomleft = (player_two_game_buttons_x_offset + 32, GAME_CONSTANTS['SCREEN_HEIGHT'] - player_two_game_buttons_y_offset)))
      else:
        THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['RED_BUTTON_UP'], GAME_SURFACES['INPUT_PROMPTS']['RED_BUTTON_UP'].get_rect(bottomleft = (player_two_game_buttons_x_offset + 32, GAME_CONSTANTS['SCREEN_HEIGHT'] - player_two_game_buttons_y_offset)))
      if GAME_CONTROLS['PLAYER_2']['BLUE']:
        THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['BLUE_BUTTON_DOWN'], GAME_SURFACES['INPUT_PROMPTS']['BLUE_BUTTON_DOWN'].get_rect(bottomleft = (player_two_game_buttons_x_offset + 64, GAME_CONSTANTS['SCREEN_HEIGHT'] - player_two_game_buttons_y_offset)))
      else:
        THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['BLUE_BUTTON_UP'], GAME_SURFACES['INPUT_PROMPTS']['BLUE_BUTTON_UP'].get_rect(bottomleft = (player_two_game_buttons_x_offset + 64, GAME_CONSTANTS['SCREEN_HEIGHT'] - player_two_game_buttons_y_offset)))

      if GAME_CONTROLS['PLAYER_2']['YELLOW']:
        THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['YELLOW_BUTTON_DOWN'], GAME_SURFACES['INPUT_PROMPTS']['YELLOW_BUTTON_DOWN'].get_rect(bottomleft = (player_two_game_buttons_x_offset + 96, GAME_CONSTANTS['SCREEN_HEIGHT'] - player_two_game_buttons_y_offset)))
      else:
        THE_SCREEN.blit(GAME_SURFACES['INPUT_PROMPTS']['YELLOW_BUTTON_UP'], GAME_SURFACES['INPUT_PROMPTS']['YELLOW_BUTTON_UP'].get_rect(bottomleft = (player_two_game_buttons_x_offset + 96, GAME_CONSTANTS['SCREEN_HEIGHT'] - player_two_game_buttons_y_offset)))

    ####################################################################
    # Debug Grid, useful for lining things up
    ####################################################################
    if GAME_STATE['DEBUG_GRID']:
      pygame.draw.lines(THE_SCREEN, GAME_COLORS['GREEN'], False, GAME_CONSTANTS['DEBUG_GRID'], width=1)

  ####################################################################
  # FINAL UPDATES FOR OUR GAME LOOP
  #
  # ***LESSON 1*** ***GAME LOOP***
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
  FRAME_COUNTER = FRAME_COUNTER + 1

pygame.quit()