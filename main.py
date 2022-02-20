import color

import os
import pypresence

import time
import random

import pygame
from pygame.locals import *

import json

print("\n"*10000)

clock = pygame.time.Clock()

################################################
###### REPORTING NUMBER OF MODULES LOADED ######
################################################

_, __ = pygame.init()
pygame.mixer.init()
print(f"{_} modules loaded, {__} modules failed to load")
print(f"{(_ // _+__)*100}% modules loaded")


###############################################
####### ERRORING IF MODULES ARE MISSING #######
###############################################

if __ > 0:
    print("ERROR: Some modules are not installed correctly, please reinstall pygame")
    exit(1)

width = 1000
height = 800

display = pygame.display.set_mode((width, height), pygame.RESIZABLE)
pygame.display.set_caption(time.strftime("Crypto Simulator"))

saves_folder = "saves/"

################################
######### ASSET LOADER #########
################################

asset_path = "assets/"
print("Loading assets . . .")
assets = {
    "title_screen": {
        "play": pygame.image.load(asset_path + "titlescreen/play.png"),
        "exit": pygame.image.load(asset_path + "titlescreen/exit.png"),
        "logo": pygame.image.load(asset_path + "titlescreen/logo.png"),
        "options": pygame.image.load(asset_path + "titlescreen/options.png"),
        # HOVER ASSETS
        "play_hover": pygame.image.load(asset_path + "titlescreen/play_hover.png"),
        "exit_hover": pygame.image.load(asset_path + "titlescreen/exit_hover.png"),
        "options_hover": pygame.image.load(asset_path + "titlescreen/options_hover.png"),
    },
    "mouse": {
        "cursors": {
            "main": pygame.image.load(asset_path + "mouse/cursors/main.png"),
        },
    },
    "level_select": {
        "back": pygame.image.load(asset_path + "level-select/back.png"),
        "create_new": pygame.image.load(asset_path + "level-select/create_new.png"),
        "delete": pygame.image.load(asset_path + "level-select/delete.png"),
        "play": pygame.image.load(asset_path + "level-select/play.png"),
        # HOVER ASSETS
        "back_hover": pygame.image.load(asset_path + "level-select/back_hover.png"),
        "create_new_hover": pygame.image.load(asset_path + "level-select/create_new_hover.png"),
        "delete_hover": pygame.image.load(asset_path + "level-select/delete_hover.png"),
        "play_hover": pygame.image.load(asset_path + "level-select/play_hover.png"),
    },
    "options": {
        "back": pygame.image.load(asset_path + "options/back.png"),
        "back_hover": pygame.image.load(asset_path + "options/back_hover.png"),
        "restart_to_apply": pygame.image.load(asset_path + "options/restart_to_apply.png"),

        "discord_rpc": {
            "on": pygame.image.load(asset_path + "options/discord_rpc/on.png"),
            "off": pygame.image.load(asset_path + "options/discord_rpc/off.png"),
            # HOVER ASSETS
            "on_hover": pygame.image.load(asset_path + "options/discord_rpc/on_hover.png"),
            "off_hover": pygame.image.load(asset_path + "options/discord_rpc/off_hover.png"),
        }
    },
    "sound_effects": {
        "button_click": pygame.mixer.Sound(asset_path + "sound-effects/button_click.mp3"),
    }
}


scene = "title-screen"
running = True

mouse_clicked = False
mouse_pressed = False


################################
##### RENDER TEXT FUNCTION #####
################################


def render_text(text="Test", x=1, y=1, font_size=16, color=color.black, return_wh=False, draw_text=None):
    """
    Attribute draw_text is True if return_wh is False, else True
    """
    font = pygame.font.Font(asset_path+"fonts/default.ttf", font_size)
    text = font.render(text, True, color)
    if draw_text == None:
        if return_wh:
            draw_text = False
        elif not return_wh:
            draw_text = True
    if draw_text:
        display.blit(text, (x, y))
    if return_wh:
        return (text.get_width(), text.get_height())


################################
#### RENDER BUTTON FUNCTION ####
################################

def render_button(image=None, image_hover=None, text="Button", x = 1, y =  1, mx = 30, my = 10, font_size=16, font_color=color.white, background_color = color.black, background_image = None, return_whc = False, render = None):
    width = 0
    height = 0
    clicked = False
    button_click = assets["sound_effects"]["button_click"]
    if render == None:
        render = True if return_whc else False
    if image == None:
        # Therefore, Render the text for the button
        width, height = render_text(text=text, font_size=font_size, return_wh=True)
        

        mWidth = width + mx
        mHeight = height + my

        left = x
        top  = y
        background = pygame.Rect((left, top), (mWidth, mHeight))
        pygame.draw.rect(display, background_color, background)
        
        if (pygame.mouse.get_pos()[0] > left and pygame.mouse.get_pos()[0] < left + mWidth and
                pygame.mouse.get_pos()[1] > top and pygame.mouse.get_pos()[1] < top + mHeight):
            border = pygame.Rect((left, top), (mWidth, mHeight))
            pygame.draw.rect(display, color.white, background, 2)
            if mouse_clicked:
                clicked = True
                button_click.play()
        left = mx//2 + x
        top  = my//2 + y

        render_text(text=text, font_size=font_size, x=left, y=top, color=font_color)


    else:
        # It means that the image is supplied, so just blit it!
        width = image.get_width()
        height = image.get_height()
        if not return_whc:pass
        display.blit(image, (x, y))
        if (pygame.mouse.get_pos()[0] > x and pygame.mouse.get_pos()[0] < x + image.get_width() and
                pygame.mouse.get_pos()[1] > y and pygame.mouse.get_pos()[1] < y + image.get_height()):
            if image_hover != None:
                display.blit(image_hover, (x, y))
            if mouse_clicked:
                button_click.play()
                clicked = True
    

    if return_whc:
        return (width, height, clicked)
    else:
        return clicked


###############################
###### INITIALIZE CONFIG ######
###############################
options = None
try:
    with open('options.json') as f:
        options = json.load(f)
except:
    print("Options File Not Found")
    template = {
        "video": {
            "custom_cursor": True,
            "fullscreen": False,
        },
        "discord_rpc": True
    }
    print("Overwriting/Generating File . . .")
    with open("options.json", "w") as f:
        f.seek(0)
        f.truncate()
        json.dump(template, f)
    options = template
options_new = options

##############################
######## OPTIONS INIT ########
##############################


def options_reInitialize():
    pygame.mouse.set_visible(not options["video"]["custom_cursor"])


def save_options():
    with open("options.json", "w") as f:
        json.dump(options, f)


###############################
######### DISCORD RPC #########
###############################

def try_discord_rpc():
    try:
        # Connect to Discord
        cid = int(931778898994290719)
        rpc = pypresence.Presence(cid)
        rpc.connect()
        # Set RPC
        rpc.update(small_image='small')  # , large_image = 'large')
        print('RPC set successfully.')
    except:
        print("Could'nt Detect Discord!")
        print("Turning Discord RPC Off . . .")
        options["discord_rpc"] = False


if options["discord_rpc"]:
    try_discord_rpc()


################################
######### TITLE SCREEN #########
################################

def title_screen():
    global running
    global scene
    play = assets["title_screen"]["play"]
    play_hover = assets["title_screen"]["play_hover"]
    exit = assets["title_screen"]["exit"]
    exit_hover = assets["title_screen"]["exit_hover"]
    logo = assets["title_screen"]["logo"]
    options = assets["title_screen"]["options"]
    options_hover = assets["title_screen"]["options_hover"]
    display.blit(logo, ((width/2) - (logo.get_width()/2), height*0.25))
    button_click = assets["sound_effects"]["button_click"]

    # Blit + Event Play
    play_properties = {
        "x": width/2 - play.get_width()/2,
        "y": height/2 - play.get_height()/2,
    }
    if (pygame.mouse.get_pos()[0] > play_properties["x"] and pygame.mouse.get_pos()[0] < play_properties["x"] + play.get_width() and
            pygame.mouse.get_pos()[1] > play_properties["y"] and pygame.mouse.get_pos()[1] < play_properties["y"] + play.get_height()):
        display.blit(play_hover, (play_properties["x"], play_properties["y"]))
        if mouse_clicked:
            scene = "level-select"
            button_click.play()
    else:
        display.blit(play, (play_properties["x"], play_properties["y"]))

    # Blit + Event Options
    options_properties = {
        "x": width/2 - options.get_width()/2,
        "y": height/1.4 - options.get_height()/2,
    }

    if (pygame.mouse.get_pos()[0] > options_properties["x"] and pygame.mouse.get_pos()[0] < options_properties["x"] + options.get_width() and
            pygame.mouse.get_pos()[1] > options_properties["y"] and pygame.mouse.get_pos()[1] < options_properties["y"] + options.get_height()):
        display.blit(
            options_hover, (options_properties["x"], options_properties["y"]))
        if mouse_clicked:
            scene = "options"
    else:
        display.blit(
            options, (options_properties["x"], options_properties["y"]))

    # Blit + Event Exit
    exit_properties = {
        "x": width - exit.get_width()*1.1,
        "y": height - exit.get_height()*1.1,
    }
    if (pygame.mouse.get_pos()[0] > exit_properties["x"] and pygame.mouse.get_pos()[0] < exit_properties["x"] + exit.get_width() and
            pygame.mouse.get_pos()[1] > exit_properties["y"] and pygame.mouse.get_pos()[1] < exit_properties["y"] + exit.get_height()):
        display.blit(exit_hover, (exit_properties["x"], exit_properties["y"]))
        if mouse_clicked:
            running = False
    else:
        display.blit(exit, (exit_properties["x"], exit_properties["y"]))

###############################
##### LEVEL SELECT SCREEN #####
###############################


def level_selector():
    global scene
    back = assets["level_select"]["back"]
    create_new = assets["level_select"]["create_new"]
    delete = assets["level_select"]["delete"]
    play = assets["level_select"]["play"]
    # HOVER ASSETS
    back_hover = assets["level_select"]["back_hover"]
    create_new_hover = assets["level_select"]["create_new_hover"]
    delete_hover = assets["level_select"]["delete_hover"]
    play_hover = assets["level_select"]["play_hover"]

    # DRAWING THE RECTANGLES
    pygame.draw.rect(display, pygame.Color('gray19'),
                     (width*0.2, 0, width*0.6, height*0.9))
    pygame.draw.rect(display, pygame.Color('gray2'),
                     (0, height*0.9, width, height*0.1))

    # BUTTON BACK
    back_properties = {
        "x": 0,
        "y": 0,
        "w": back.get_width(),
        "h": back.get_height(),
    }
    if (pygame.mouse.get_pos()[0] > back_properties["x"] and pygame.mouse.get_pos()[0] < back_properties["x"] + back_properties["w"] and
            pygame.mouse.get_pos()[1] > back_properties["y"] and pygame.mouse.get_pos()[1] < back_properties["y"] + back_properties["h"]):
        display.blit(back_hover, (back_properties["x"], back_properties["y"]))
        if mouse_clicked:
            scene = "title-screen"
    else:
        display.blit(back, (back_properties["x"], back_properties["y"]))

    # BUTTON CREATE NEW
    create_new_properties = {
        "x": (width//2) - (create_new.get_width()//2),
        "y": (height*0.9) + 5,
        "w": create_new.get_width(),
        "h": create_new.get_height(),
    }
    if (pygame.mouse.get_pos()[0] > create_new_properties["x"] and pygame.mouse.get_pos()[0] < create_new_properties["x"] + create_new_properties["w"] and
            pygame.mouse.get_pos()[1] > create_new_properties["y"] and pygame.mouse.get_pos()[1] < create_new_properties["y"] + create_new_properties["h"]):
        display.blit(create_new_hover,
                     (create_new_properties["x"], create_new_properties["y"]))
        if mouse_clicked:
            pass
    else:
        display.blit(
            create_new, (create_new_properties["x"], create_new_properties["y"]))

    # BUTTON PLAY SELECTED
    play_properties = {
        "x": create_new_properties['x'] - play.get_width() - 20,
        "y": (height*0.9) + 5,
        "w": play.get_width(),
        "h": play.get_height(),
    }

    if (pygame.mouse.get_pos()[0] > play_properties["x"] and pygame.mouse.get_pos()[0] < play_properties["x"] + play_properties["w"] and
            pygame.mouse.get_pos()[1] > play_properties["y"] and pygame.mouse.get_pos()[1] < play_properties["y"] + play_properties["h"]):
        display.blit(play_hover, (play_properties["x"], play_properties["y"]))
        if mouse_clicked:
            pass
    else:
        display.blit(play, (play_properties["x"], play_properties["y"]))

    # BUTTON DELETE SELECTED
    delete_properties = {
        "x": create_new_properties['w'] + create_new_properties['x'] + 20,
        "y": (height*0.9) + 5,
        "w": delete.get_width(),
        "h": delete.get_height(),
    }
    if (pygame.mouse.get_pos()[0] > delete_properties["x"] and pygame.mouse.get_pos()[0] < delete_properties["x"] + delete_properties["w"] and
            pygame.mouse.get_pos()[1] > delete_properties["y"] and pygame.mouse.get_pos()[1] < delete_properties["y"] + delete_properties["h"]):
        display.blit(
            delete_hover, (delete_properties["x"], delete_properties["y"]))
        if mouse_clicked:
            pass
    else:
        display.blit(delete, (delete_properties["x"], delete_properties["y"]))


def options_menu(options_screen=None):
    global scene
    global options
    global options_new

    back = assets["options"]["back"]
    back_hover = assets["options"]["back_hover"]

    discord_rpc_on = assets["options"]["discord_rpc"]["on"]
    discord_rpc_off = assets["options"]["discord_rpc"]["off"]
    discord_rpc_on_hover = assets["options"]["discord_rpc"]["on_hover"]
    discord_rpc_off_hover = assets["options"]["discord_rpc"]["off_hover"]
    restart_to_apply = assets["options"]["restart_to_apply"]

    row_left = width//2 - 50
    row_right = width//2 + 50

    if render_button(image=back, image_hover=back_hover, x = 0, y = 0):
        with open("options.json", "w") as f:
            json.dump(options, f)
        scene = "title-screen"

    temp_width = discord_rpc_on.get_width()
    if options_new["discord_rpc"]:
        if render_button(image=discord_rpc_on, image_hover=discord_rpc_on_hover, x=row_left - temp_width, y=100):
            options_new["discord_rpc"] = False
    elif not options_new["discord_rpc"]:
        if render_button(image=discord_rpc_off, image_hover=discord_rpc_off_hover, x=row_left - temp_width, y=100):
            options_new["discord_rpc"] = True

    with open("options.json") as f:
        options = json.load(f)

    if options_new["discord_rpc"] != options["discord_rpc"]:
        display.blit(restart_to_apply, (width//2 - restart_to_apply.get_width() //
                     2, height-restart_to_apply.get_height()-5))

    clock.tick(15)


user_text = ""
eventkey = ""

options_reInitialize()

###############################
########## MAIN LOOP ##########
###############################


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYUP:
            eventkey = event.key
            if event.key == K_BACKSPACE:
                user_text = user_text[0:-1]
            elif event.key == K_RETURN:
                pass
            elif event.key == K_ESCAPE:
                pass
            elif event.key == K_F11:
                pygame.display.toggle_fullscreen()
            else:
                user_text += event.unicode
            print(f"{user_text} ({len(user_text)})")
        if event.type == pygame.MOUSEMOTION:
            print()
            print("Mouse X:", pygame.mouse.get_pos()[0])
            print("Mouse Y:", pygame.mouse.get_pos()[1])
  
    if scene == "title-screen":
        title_screen()
    elif scene == "level-select":
        if user_text == "back":
            scene = "title-screen"
            user_text = ""
        level_selector()
    elif scene == "options":
        options_menu()

    width, height = pygame.display.get_surface().get_size()
    if options["video"]["custom_cursor"]:
        main_cursor = assets["mouse"]["cursors"]["main"]
        display.blit(main_cursor, (pygame.mouse.get_pos()[
            0] - main_cursor.get_width()/2, pygame.mouse.get_pos()[1] - main_cursor.get_height()/2))
    # FPS COUNTER
    fps = str(int(clock.get_fps()))
    render_text(text="FPS: "+fps, x=5, y=5, color=color.black)
    if render_button(font_size=32): print("Clicking Works!")
    pygame.display.update()
    display.fill((64, 64, 64))

    # Mouse Clicked Events
    temp = mouse_pressed
    mouse_pressed = pygame.mouse.get_pressed(num_buttons=3)[0]
    
    if temp == True and mouse_pressed == False:
        mouse_clicked = True
    else:
        mouse_clicked = False


    clock.tick(10000)


options = options_new

# Saving Options.json
save_options()