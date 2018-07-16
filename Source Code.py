#Paint Project.Py
#Noor Nasri
#Dec. 1st/2017 - Feb. 1st/2018
#This is the program made for 15% of my computer science mark, to provide the essentials to creating media arts. A paint Program with a nintendo switch/mario theme.


#############
##Extra Features (The ones that are useful):
## - Program is Resizeable with ratio constraints. All measurements are compatible with diffrent resolutions.
## - Custom load menu allows painters to see a small demo of the paint before loading it
## - Fill Tool
## - Text Tool
## - Spray Paint, Eye Dropper, and Marker Tools
## - Polygon Tool
## - An additional 9 extra shapes (Triangle, Diamond, Parallelogram, Star, Arrow, Lightning Bolt, Mail, Cross, Custom shape)
## - You can have seperate filled and outline colours for shapes (By changing the colour in gradient slider first)
## - Holding Shift while making the shapes (and most tools under "Extras") turns their selection box into a square
## - Extra Stamps, which are also resized according to thickness
## - Crop Tool
## - Magnify Tool
## - Rotate Tool, Move Tool
## - Flip V Tool, Flip H Tool
## - Inverse Colour Tool
## - Dark Tint Tool
## - Inverse V Tool, Inverse H Tool
## - Gradient slider that switches the L from the hsl of the colour
## - Volume Slider
## - Undo/Redo
## - Animation playing for when a page is flipped or category selected
## - Animation for when a button is hovered on, and for when it is selected (for nearly all buttons in all menus)
## - Save User online (Could not fix saving paint online in time)
## - They can unequip a tool
##
#############
##Attention To Detail:
## - The shape outlines are all drawn with a custom polygon technique, so that they all look nice and even have curved corners
## - Resizing keeps the screen in the same ratio
## - When using stamps, magnify, crop, etc; your mouse holds the center, not the corner
## - Even though there are gifs and lots of effects for visuals, items are only blit in single moments to reduce latency 
## - The Undo/Redo list is added upon when an action is complete, not simply when they fire a MouseButtonUp within the canvas
## - Text shown to user has outline (except the ones drawn)
## - Tested for bugs (Probably none?)
## - Responsive
## - The text font is as large as possible to fit in a given rectangle, so that it looks the same with resize
## - When displaying a list of options (ex. load menu), the text font is as large as possible for the one that takes the most space, so they have the same text font
## - PixelArray to quicken fill and inverse colour tools
#############

####################################
#Importing modules
import os
import time
import random
import functools
import math
import pygame
import requests


####################################
#Game Variables
starting_time = time.time() #Specifies the time the program started running
normal_buttons = [] #The button rects to check if they are being clicked
loop_end = None #The time the last loop started
running = True #Variable to know when to end the loop

original_screen = [1050, 500] 
size_ratio = 1 #Ratio to original screen. x and y are constrainted so that the ratio remains the same.

window_chosen = "Main Menu" #Variable to know which screen they are on (Main Menu, Paint, Load, Log-in, Settings)
next_window = "Main Menu" #When shading in, it stays as current, when starting to shade out, it switches to next window
transition_value = -4
current_shade = 255 #Shade for the transition value
transition_image = None #After putting a transparent shade, we need to blit the image of how it was before, so that the transparent shades do not overlap and make it all black

path_way = os.path.dirname(os.path.realpath(__file__)) #Directory to the python file


last_selected = {"Bottom_Left":False,"Paint Category":False, "Paint Tools": False, "chosen_filled": False, "Top Bar": False} #Dictionary to tell us which buttons were clicked, in whichever area

#Images that are used later on with subsurface to undo certain animations
nintendo_alone = None
orig_top_right = None
orig_bottom_right = None

#Adding all local saves and storing them in a dictionary when the program starts
local_saves = {}
for image in os.listdir(path_way+"\Saves"):
    save_path = "Saves\\" + image
    if image[-3:]=="png":
        local_saves[image[:-4]] = pygame.image.load(save_path)
        
        
user_info = {"Username":"Guest","Logged in": False,"Online saves":{}} #Holds the status the user is in for online connection
docs_url = "https://script.google.com/macros/s/AKfycbzelmKX_fQkRYUVSrwqb_Yshr8pNP4WkPJwZorKX1wm9o9HuLTi/exec" #Link to the google docs which holds all online saves
#The docs url has javascript running to detect Get and Post requests, and will return according to parameters



gif_delays = {"Main Menu":0.06,"Account":0.08,"Select Paint":0.02} #Holds how many seconds should b
images_sizing = {} #Original sizing for images

#Holds original images so they don't pixilate as we transform them
non_touched_gifs = {}
non_touched_images = {}

#Loading all png images in GIF Frames folder into the dictionary 
for file in os.listdir(path_way+"\GIF Frames"):
    non_touched_gifs[file] = []
    for image in os.listdir(path_way+"\GIF Frames"+ "\\" +file):
        image_path = "GIF Frames"+ "\\" +file+"\\"+image
        if image[-3:]=="png":
            non_touched_gifs[file].append([pygame.image.load(image_path),file[-3:]])

#Loading all png and jpg images in Images folder into the dictionary with the size indicated in their names
for image in os.listdir(path_way+"\Images"):
    image_path = "Images"+ "\\" +image
    if image[-3:]=="png" or image[-3:]=="jpg":
        wished_x,wished_y = [int(e) for e in image.split()[0].split("-")]
        non_touched_images[image[image.find(" ")+1:-4]] = pygame.image.load(image_path)#(int(wished_x*size_ratio),int(wished_y*size_ratio)))
        images_sizing[image[image.find(" ")+1:-4]] = [wished_x,wished_y]

#Dictionaries that hold the transformed images. Remade when the resize event is fired
gif_frames = {} 
images_folder = {} 



####################################
#Paint specific Variables:
    
paint_status = 0 #Mouse status while painting, 0 = Just Ended, 1 = Just Started, 2 = Holding, 3= Not clicking at all

#Dictionary that specifies what kind of things to look for in each tool
info_required = {"Tools":{"Everything":"Drag","Dropper":"Special","Fill":"Special","Text":"Special"},
                 "Shapes":{"Everything":"S+E","Polygon":"Special"},
                 "Stamps":{"Everything":"Click"},
                 "Extras":{"Everything":"S+E", "Magnify":"Special", "Rotate":"Special", "Move":"Special"}}

#List of tools in each category, every 6 are displayed on a page
extra_info = {"Tools":["Pencil","Eraser","Dropper","Fill","Spray","Text",   "Marker"],
              "Shapes":["Line","Ellipse","Rectangle","Triangle","Diamond","Parallelogram",  "Star","Arrow","Lightning","Envelope","Cross","Falcon",   "Polygon"],
              "Stamps":["Mario","Luigi","Mario and Luigi","Yoshi","Bowser","Donkey Kong",  "Red Mushroom","Orange Mushroom","Toad","Pipe","Peach"],
              "Extras":["Crop","Magnify","Rotate","Flip V","Flip H","Move",   "Inverse Color","Darken","Inverse V","Inverse H"]} 

#Loading all the stamps
loaded_stamps = {}
for stamp in extra_info["Stamps"]:
    loaded_image = pygame.image.load("Stamps\\"+stamp+".png")
    x,y = loaded_image.get_size()
    loaded_stamps[stamp] = [loaded_image, y/x]

    
#Flags and variables used for specefic special tools
polygon_start = None
magnify_start = False
move_selected = None
move_started = False
typing_started = False
typing_text = ""


paint_buttons = {} #Paint rects to see if any category is pressed
tool_select_buttons = {} #Paint rects to see if any tool is pressed

selection_page = 0 #Each page holds 6 tools in the category, this variable holds which page they are on. 

####################################
#Account specific variables:
account_menu = "Sign in" #Sign in or Register, holds which menu they are on

#Text box's and their variables for username and password
login_fields = {"Username":{"Editing":False,"Text":"","Button":None,"Buttonpos":[235,240]},"Password":{"Editing":False,"Text":"","Button":None,"Buttonpos":[235,335]}}
sign_failure = [0,""] #when they fail to sign in, for the next 5 or so seconds, they are given a message. [time of failure, failure reason]


####################################
#Paint select menu variables:
selection_menu = "New" #New or Load, holds which meny 
new_paint = "" #Name of the paint they select
typing_paint = False #They are typing a new name
select_save_page = {"Local saves":[300,160,0],"Online saves":[600,160,0]} #positioning for the rectangles [pos_x,pos_y,scroll variable]

####################################
#Initilizing modules
pygame.init()
pygame.mixer.init()
pygame.font.init()

####################################
#Displaying the screen
os.environ['SDL_VIDEO_WINDOW_POS'] = '0,25'

screen = pygame.display.set_mode([1260,600],pygame.RESIZABLE)

pygame.display.set_caption("Noor Nasri's Paint Program!")

####################################
#Putting on the music
pygame.mixer.music.load("Gusty Garden Galaxy - Super Mario Galaxy.mp3")
pygame.mixer.music.set_volume(0.2)
pygame.mixer.music.play(-1)

####################################
# Game functions:

def make_frames(gifs): #Makes the gif frames wanted according to time, instead of clogging up space in main code 
    for item in gifs: #items are in this format: [gif,loop_time,cooldown,x,y]
        frames = gif_frames[item[0]] 
        chosen = int((item[1] - starting_time)/item[2]) % len(frames)
        screen.blit(frames[chosen],(int(item[3]*size_ratio),int(item[4]*size_ratio)))
    
def draw_images(dict_to_draw,x,y,need_type): #draw images wanted, and return all the surfaces that collide or the image they clicked
    image_rects = {} #Dictionary with the key being the name of the image, the value being the rectangle
    image_clicked = "None"
    for image_name in dict_to_draw: #images that need to be drawn
        item = dict_to_draw[image_name]
        image = screen.blit(images_folder[image_name],(int(item[0]*size_ratio),int(item[1]*size_ratio)))
        if len(item)==2: #If the length is over 2, we don't wish for the image to count towards the image_clicked and image_rects (We purposely make the length 3)
            image_rects[image_name] = image
            if image.collidepoint((x,y)):
                image_clicked = image_name
    if need_type == "Clicked":
        return image_clicked
    elif need_type == "Rects":
        return image_rects
    
#make text with outline colour by blitting around it.
def text_with_outline(text,myfont,col_main, col_outline, x, y, outline_width, scale_needed): 
    main_text = myfont.render(text, True, col_main) #The main colour text
    outline_text = myfont.render(text, True, col_outline) #The text rendered with the outline colour

    #Blit the outline text 4 times around the main text, then blit the main text
    stuff = [[int(e*size_ratio) if scale_needed else e for e in [x,y]] for a in range(5)]
    extra = [[outline_width,0],[outline_width*-1,0],[0,outline_width],[0,outline_width*-1]]
    for a in range(4):
        stuff[a][0] += extra[a][0]
        stuff[a][1] += extra[a][1]
    for outlinePos in stuff[:-1]:
        screen.blit(outline_text,outlinePos)
    screen.blit(main_text,stuff[-1])

#Given hsl, return the correct rgb. Could not find a module for hsl to rgb but there is a way to turn rgb into hsl.
def hsl_to_rgb(hsl):
    h,s,l = hsl
    c = (1- abs(2*l-1))*s
    x = c*(1-abs((h/60)%2-1))
    m = l - c/2
    if h<60:
        R,G,B = (c,x,0)        
    elif h<120:
        R,G,B = (x,c,0) 
    elif h<180:
        R,G,B = (0,c,x) 
    elif h<240:
        R,G,B = (0,x,c) 
    elif h<300:
        R,G,B = (x,0,c) 
    else:
        R,G,B = (c,0,x) 
    r,g,b = [int(e) for e in ((R+m)*255, (G+m)*255, (B+m)*255)]
    return(r,g,b)

#Sets the colour display once colour is changed or screen is resized
def make_color(): 
    background = nintendo_alone.subsurface([int(e*size_ratio) for e in [30,195,125,65]])
    screen.blit(background,[int(e*size_ratio) for e in (30,195)])
    lue_pos = 90+65*pygame.Color(chosen_colour[0],chosen_colour[1],chosen_colour[2]).hsla[2]/100 #calculate new position for the gradient slider
    
    pygame.draw.circle(screen,chosen_colour,(int(60*size_ratio),int(220*size_ratio)),int((12.5+chosen_thickness/2)*size_ratio)) #Draw new colour properties
    
    screen.blit(images_folder["Gradient"],[int(e*size_ratio) for e in (90,200)]) #Gradient Meter
    pygame.draw.line(screen,(255,255,255),(int(lue_pos*size_ratio),int(200*size_ratio)),(int(lue_pos*size_ratio),int(220*size_ratio)),math.ceil(size_ratio))
    
    pygame.draw.line(screen,0,(int(90*size_ratio),int(235*size_ratio)),(int(155*size_ratio),int(235*size_ratio)),1)
    pygame.draw.line(screen,0,(int(90*size_ratio),int(225*size_ratio)),(int(90*size_ratio),int(245*size_ratio)),math.ceil(size_ratio))
    pygame.draw.line(screen,0,(int(155*size_ratio),int(225*size_ratio)),(int(155*size_ratio),int(245*size_ratio)),math.ceil(size_ratio))
    pygame.draw.line(screen, (255, 255, 255), (int(90*size_ratio+65*size_ratio*chosen_thickness/25), int(225*size_ratio)),(int(90*size_ratio+65*size_ratio*chosen_thickness/25), int(245*size_ratio)))

#Sets volume mixer when volume is changed or when screen is resized
def volume_mixer(): 
    background = nintendo_alone.subsurface([int(e*size_ratio) for e in [45,309,105,17]])
    screen.blit(background,[int(e*size_ratio) for e in [45, 309]])
    cur = pygame.mixer.music.get_volume() #Volume bar
    pygame.draw.ellipse(screen,(27,27,27),[int(e*size_ratio) for e in [47,310,100,15]])
    pygame.draw.ellipse(screen,(200,200,200),[int(e*size_ratio) for e in [47,310,100*cur,15]])
    pygame.draw.line(screen,(0,0,0),[int(e*size_ratio) for e in [47,310]],[int(e*size_ratio) for e in [47,325]],2)
    pygame.draw.line(screen,(0,0,0),[int(e*size_ratio) for e in [147,310]],[int(e*size_ratio) for e in [147,325]],2)


#Given the width and height wanted, find the largest possible size for the font
@functools.lru_cache(maxsize=None)
def font_size(font,text,max_width,max_height,size):#Recurssion with memoization
    myfont = pygame.font.SysFont(font, size)
    x,y = pygame.font.Font.size(myfont,text) 
    if x<max_width and y<max_height or size<4:
        return [size,x,y,myfont]
    return font_size(font,text,max_width,max_height,size-3)

#Makes the tool page. Each page holds 6 tools, and they switch pages by scrolling while mouse is over the page. If animation_wanted is true, then flip the screen while making it
def tool_page(animation_wanted):
    screen.blit(nintendo_alone.subsurface([int(e*size_ratio) for e in (890,210,120,155)]),[int(e*size_ratio) for e in (890,210)])
    if animation_wanted:
        pygame.display.flip()
        
    tool_select_buttons = {}
    c=0 #Counter for which image we are blitting
    for item in extra_info[chosen_category][selection_page*6:(selection_page+1)*6]: #Tiny slide for the 6 tools
        image = images_folder[chosen_category + " " + item]
        tool_select_buttons[item] = screen.blit(image,[int(e*size_ratio) for e in [900+60*(c%2),220+50*(c//2)]])
        
        if animation_wanted:
            pygame.display.update(tuple(int(e*size_ratio) for e in [900+60*(c%2),220+50*(c//2),35,35]))
            pygame.time.wait(75)

        c+=1
        
    orig_bottom_right = screen.copy().subsurface([int(e*size_ratio) for e in [890,210,120,155]])

    return (tool_select_buttons, orig_bottom_right)

#Displays the filled colour box. Called when they resize, change categories, or change the filled colour
def change_filled(): 
    dim = [int(e*size_ratio) for e in (930,370,35,35)]
    if chosen_category == "Shapes":
        if chosen_filled: #Show them their chosen filled colour and display options
            pygame.draw.rect(screen, chosen_filled, dim) 
            pygame.draw.rect(screen, (255,255,255), dim, math.ceil(size_ratio))
        else: #Show them where to click to turn their shapes into filled
            pygame.draw.rect(screen, (100,100,103), dim)
            pygame.draw.rect(screen, (255,255,255), dim, math.ceil(size_ratio))
    else:
        screen.blit(nintendo_alone.subsurface((dim[0],dim[1],dim[2]+math.ceil(size_ratio),dim[3]+math.ceil(size_ratio))) , (dim[0],dim[1]))

#Called when a new menu is put, or when the menu is resized to minimize the number of blits. 
def update_menu():
    global normal_buttons
    global screen
    global nintendo_alone

    #Making the background and the left hand controls
    screen.fill((195,195,195)) 

    #Add our name on there to give proper credits
    largest_size, x_taken, y_taken, myfont = font_size("timesnewroman","Made by Noor Nasri",int(150*size_ratio),int(50*size_ratio),100)
    text_with_outline("Made by Noor Nasri",myfont, (0,0,0), (255,255,255),(size_ratio*original_screen[0]-x_taken)//2, int(size_ratio*original_screen[1]-y_taken), 1, False)
    
    draw_images({'Nintendo Switch': [25, 25, 'Background, do not check collide']},0,0,"Rects")
    nintendo_alone = screen.copy()
    
    images_database = {'Home': [75, 350], 'Volume': [47, 275], 'Minus': [82, 270], 'Plus': [115, 270]}
    normal_buttons = draw_images(images_database,0,0,"Rects")
    volume_mixer()
    
    if window_chosen == "Paint": #Draw extra controls for the sides
        global paint_buttons
        global tool_select_buttons
        global paint_canvas
        global orig_top_right
        global orig_bottom_right
        global top_buttons
        
        images_db = {"Colours":[35,65,"Don't bother checking"],"Tools":[920,65],"Stamps":[920,125],"Shapes":[890,95],"Extras":[950,95]}
        paint_buttons = draw_images(images_db,0,0,"Rects")

        images_db = {"Undo":[0,0],"Redo":[60,0], "Save":[1005,0]}
        top_buttons = draw_images(images_db,0,0,"Rects")
        
        tool_select_buttons, orig_bottom_right = tool_page(False)
        
        if chosen_item != "None": #Draw rectangle after orig_bottom_right had been subsurfaced so the rectangle is not part of it 
            c = extra_info[chosen_category].index(chosen_item)
            c = c%6
            pygame.draw.rect(screen,0,[int(e*size_ratio) for e in [900+60*(c%2),220+50*(c//2),35,35]],math.ceil(size_ratio))

        canvas_args = [int(e*size_ratio) for e in [180,45,690,415]]
        if len(undo_list)>0: #If the list is empty, just make a rectangle instead
            paint_canvas = screen.blit(pygame.transform.scale(undo_list[-1],canvas_args[2:]),canvas_args[:2])
        else:
            paint_canvas = pygame.draw.rect(screen, (210,210,210),canvas_args)
            
    
        screen_copy = screen.copy()
        
        orig_top_right = screen_copy.subsurface([int(e*size_ratio) for e in [875,25,140,140]])
        make_color()    

        largest_size, x_taken, y_taken, myfont = font_size("timesnewroman","Stamps",int(75*size_ratio),int(50*size_ratio),100)
        text_with_outline(chosen_category,myfont,(255,255,255), (0,0,0), 890, 175, 1, True)

        change_filled()
#Makes a line with a bunch of circles 
def make_line(start_pos, end_pos, radius, colour): 
    # Ax + By + C = 0 aka. y = (-Ax - C)/B
    A = (end_pos[1]-start_pos[1])*-1
    B = end_pos[0]-start_pos[0]
    C = -1*(A*start_pos[0] + B*start_pos[1])
    #Checks all x values and finds their corresponding y
    for x in range (min(start_pos[0], end_pos[0]),max(start_pos[0], end_pos[0])):
        y = int((-1*A*x - C)/B)
        pygame.draw.circle(screen, colour, (x,y), radius)
    #Checks all y values and finds their corresponding x
    for y in range (min(start_pos[1], end_pos[1]),max(start_pos[1], end_pos[1])):
        x = int((-1*B*y - C)/A)
        pygame.draw.circle(screen, colour, (x,y), radius)

####################################
# Game loop
while running:
    #Round variables
    clicked = False
    new_text = ""
    pressed_enter = False
    scrolled = 0
    del_clicked = 0
    
    for event in pygame.event.get(): #event loop
        if event.type == pygame.QUIT: #They left the project
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button==1: #They clicked with the left click
            clicked = True
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button==5: #They scrolled downwards
            scrolled = 1
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button==4: #They scrolled upwards
            scrolled = -1
        elif event.type == pygame.VIDEORESIZE: #They resized the screen
            
            #Resize the screen but constraint the ratio, then resize all our images
            requested_size = [event.w,event.h]
            ratio_wanted = original_screen[0]/original_screen[1] #Original ratio we must have
            ratio_requested = requested_size[0]/requested_size[1] #The ratio the size they made has

            #Find the best way to make the screen as large as possible while following the ratio_wanted
            if ratio_requested > ratio_wanted + 0.01: 
                requested_size[0] = int(requested_size[1]*ratio_wanted)
            elif ratio_requested < ratio_wanted - 0.01:
                requested_size[1] = int(requested_size[0]/ratio_wanted)
            
            size_ratio = requested_size[1]/original_screen[1] #Changes the size ratio to be a ratio of the original screen
            screen = pygame.display.set_mode(requested_size,pygame.RESIZABLE)

            #Reload and resize images so they fit and don't look pixalated
            gif_frames = {}
            for ind in non_touched_gifs:
                gif_frames[ind] = non_touched_gifs[ind][:]
            for folder in gif_frames:
                for i in range(len(gif_frames[folder])):
                    image = gif_frames[folder][i]
                    if image[1] == "Gif":
                        gif_frames[folder][i] = pygame.transform.scale(image[0],[int(e*size_ratio) for e in [75,75]])
                    else:
                        gif_frames[folder][i] = pygame.transform.scale(image[0],[int(e*size_ratio) for e in [600,370]])
                        
            images_folder = {}
            for ind in non_touched_images:
                images_folder[ind] = non_touched_images[ind]
            for image in images_folder:
                images_folder[image] = pygame.transform.scale(images_folder[image],[int(e*size_ratio) for e in images_sizing[image]])
                
            update_menu() #Remake the menu    
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                del_clicked += 1
            elif event.key == pygame.K_KP_ENTER or event.key == pygame.K_RETURN:
                pressed_enter = True
            elif event.key < 256:
                new_text += event.unicode
            
    #Round variables after loop
    mouse_x,mouse_y = pygame.mouse.get_pos()
    mouse_press = pygame.mouse.get_pressed()
    loop_start = time.time()

    #When transitioning menus, black shades are put on top
    #This removes traces of black shading by blitting how the screen would have looked without it
    if transition_image:
        screen.blit(transition_image,(0,0))
        transition_image = None
        
    #Drawing corner gifs
    make_frames([["Mario Gif",loop_start,0.08,-10,440],["Luigi Gif",loop_start,0.1,985,430]])
    
    #Checking if left side control is clicked or hovered on
    veiwing_image = None
    for item in normal_buttons:
        if normal_buttons[item].collidepoint((mouse_x,mouse_y)):
            veiwing_image = item
            break    
    #Check if they were animated last loop, if so, unanimate them
    if last_selected["Bottom_Left"]:
        screen.blit(last_selected["Bottom_Left"][1], last_selected["Bottom_Left"][0])
        last_selected["Bottom_Left"] = False
        
    if veiwing_image:
        #If they are hovering over it, blit the items needed. If they clicked on it, do the actions required 
        if clicked and (veiwing_image=="Plus" or veiwing_image=="Minus"):
            extra = {"Plus":0.1,"Minus":-0.1}[veiwing_image]
            new = pygame.mixer.music.get_volume()+extra
            if new<0 or new>1:
                new = round(new)
            pygame.mixer.music.set_volume(new)
            volume_mixer() #Show new volume
            
        elif clicked and veiwing_image=="Home" and transition_value==0:
            next_window = "Main Menu"
            transition_value = 5

        #Display the name of what they are hovering on
        largest_size, x_taken, y_taken, myfont = font_size("calibri",veiwing_image,int(55*size_ratio),int(20*size_ratio),70) 
        pos = [int(mouse_x + 12 + int(55*size_ratio)/2-x_taken*size_ratio/2),int(mouse_y + int(20*size_ratio)/2-y_taken*size_ratio/2)]
        
        #How the subsurface looked before the text is blit, to be put on top next loop
        last_selected["Bottom_Left"] = [(pos[0]-2,pos[1]-2),screen.copy().subsurface((pos[0]-2,pos[1]-2,x_taken+4, y_taken+4))]
        
        text_with_outline(veiwing_image,myfont,(255,255,255), (0,0,0), pos[0], pos[1], 1, False)

    #Drawing current menu in the center if there is a background gif
    if gif_delays.get(window_chosen) != None:
        make_frames([[window_chosen,loop_start,gif_delays[window_chosen],230,65]])

    ####################################
    #Making specific windows
        
    if window_chosen == "Main Menu":
        #Give the three options: Play, Paint, Account
        images_database = {'Play Button': [240, 340],'Paint Button': [445, 340],'Account Button': [645, 340]}
        image_clicked = draw_images(images_database,mouse_x,mouse_y,"Clicked") #Blit and see if they are clicked
        
        if image_clicked != "None": #If they are hovering on one, make it bigger, and change windows if they click
            x,y = images_database[image_clicked]
            image = screen.blit(pygame.transform.scale(images_folder[image_clicked],[int(i*size_ratio) for i in [200,80]]),(int((x-15)*size_ratio),int((y-10)*size_ratio)))
            if clicked:
                next_window = {"Play Button":"Play","Paint Button":"Select Paint","Account Button":"Account"}[image_clicked]
                transition_value = 5
        #Display the "Welcome, Player" text at the top left
        largest_size, x_taken, y_taken, myfont = font_size("timesnewroman","Welcome, %s!"%(user_info["Username"]),int(300*size_ratio),int(150*size_ratio),100) #"Welcome, Player"
        text_with_outline("Welcome, %s!"%(user_info["Username"]),myfont,(255,255,255), (0,0,0), 240, 90, 1, True)
        
    elif window_chosen == "Paint":
        #Check to see if they clicked on the colour picker
        if clicked and (35*size_ratio<=mouse_x<=160*size_ratio and 120*size_ratio<=mouse_y<=140*size_ratio or 65*size_ratio<=mouse_y<=190*size_ratio and 89*size_ratio<=mouse_x<=109*size_ratio):
            if chosen_colour == chosen_filled:
                chosen_filled = screen.get_at((mouse_x,mouse_y))
                change_filled()
            chosen_colour = screen.get_at((mouse_x,mouse_y))
            make_color() 

        #Check to see if they are dragging the colour slider 
        elif mouse_press[0] and 90*size_ratio<=mouse_x<=155*size_ratio and 200*size_ratio<=mouse_y<=220*size_ratio:
            hsl = list(pygame.Color(chosen_colour[0],chosen_colour[1],chosen_colour[2]).hsla)
            hsl[2] = (mouse_x-90*size_ratio)/(65*size_ratio)
            hsl[1] /= 100
            if hsl[2] <0.01: #Make sure the colour doesn't go all the way black or white so that they can scroll back and the colour returns
                hsl[2]=0.01
            elif hsl[2]>0.99:
                hsl[2] = 0.99
            chosen_colour = hsl_to_rgb(hsl[:3])
            make_color()

        #Check to see if they are dragging the thickness slider
        elif mouse_press[0] and 90*size_ratio<=mouse_x<=155*size_ratio and 225*size_ratio<=mouse_y<=245*size_ratio:
            chosen_thickness = int(25*(mouse_x-90*size_ratio)/(65*size_ratio))
            if chosen_thickness < 1:
                chosen_thickness = 1
            elif chosen_thickness > 25:
                chosen_thickness = 25
            make_color()

        #Check to see if they changed pages for the tools.
        elif scrolled != 0 and 890*size_ratio<=mouse_x<=1010*size_ratio and 210*size_ratio<=mouse_y<=410*size_ratio: 
            selection_page += scrolled
            if selection_page<0:
                selection_page = 0
            elif len(extra_info[chosen_category])-selection_page*6 <= 0: #If it is above the limit, set it to the limit
                selection_page = (len(extra_info[chosen_category])-1)//6 
            else:
                chosen_item = "None"
                tool_select_buttons, orig_bottom_right = tool_page(True)

        #Check to see if they clicked on the filled/unfilled button while the category is shapes
        elif 930*size_ratio<=mouse_x<=965*size_ratio and 370*size_ratio<=mouse_y<=425*size_ratio and chosen_category == "Shapes": 
            if not last_selected["chosen_filled"]: #Subsurface before we blit text on top so that we can blit it when the mouse moves away
                bf_filled_text = nintendo_alone.subsurface(([int(e*size_ratio) for e in [910,410,75,50]]))
      
            if clicked: #if clicked, change it to the other (filled becomes unfilled, and vice versa)
                if not chosen_filled:
                    chosen_filled = chosen_colour
                else:
                    chosen_filled = None
                change_filled()
                last_selected["chosen_filled"] = False
                screen.blit(bf_filled_text, (int(910*size_ratio), int(410*size_ratio)))
                
            else: #While hovered on, display the status of the filled/unfilled
                last_selected["chosen_filled"] = True
                largest_size, x_taken, y_taken, myfont = font_size("timesnewroman","Unfilled",int(60*size_ratio),int(48*size_ratio),100)
                text_with_outline({True:"Filled", False:"Unfilled"}[bool(chosen_filled)],myfont,(255,255,255),(0,0,0),915,410,1,True)                
            
        elif last_selected["chosen_filled"]: #If we blit text last frame, remove text animation
            last_selected["chosen_filled"] = False
            screen.blit(bf_filled_text, (int(910*size_ratio), int(410*size_ratio)))
            
                
        ####################################
        #Check upper right side being clicked (Only paint has right side buttons)
            
        veiwing_image = None
        for item in paint_buttons: #Given the 4 categories check if any are hovered on
            if paint_buttons[item].collidepoint((mouse_x,mouse_y)):
                veiwing_image = item
                break
            
        if veiwing_image:
            #Make hovered category larger, and set it to the new category if clicked
            
            last_selected["Paint Category"] = True
            x,y = {"Tools":[920,65],"Stamps":[920,125],"Shapes":[890,95],"Extras":[950,95]}[veiwing_image] #Find the position for the new image
            screen.blit(orig_top_right,[int(e*size_ratio) for e in (875,25)]) #Put the old version first

            #Blit the image larger, and a little up and a little to the left
            image = screen.blit(pygame.transform.smoothscale(images_folder[veiwing_image],[int(i*size_ratio) for i in [45,45]]),(int((x-7.5)*size_ratio),int((y-7.5)*size_ratio)))
            if clicked:
                chosen_category = veiwing_image
                selection_page = 0
                chosen_item = "None"
                last_selected["Paint Tools"] = False
                
                #Make slide for category name
                largest_size, x_taken, y_taken, myfont = font_size("timesnewroman","Stamps",int(75*size_ratio),int(50*size_ratio),100) #Stamps is the longest one
                dimensions = [int(e*size_ratio) for e in (890,175,110,280)]
                screen.blit(nintendo_alone.subsurface(dimensions),(dimensions[0],dimensions[1]))
                
                for a in range(len(chosen_category)):
                    text_with_outline(chosen_category[:a+1],myfont,(255,255,255), (0,0,0), 890, 175, 1, True)
                    pygame.display.flip()
                    pygame.time.wait(50)
                    
                #Call function to animate the new page
                tool_select_buttons, orig_bottom_right = tool_page(True)

                change_filled() #Displays the fill rect if they are on shapes, else hides it
                
        elif last_selected["Paint Category"]:
            last_selected["Paint Category"] = False
            screen.blit(orig_top_right,[int(e*size_ratio) for e in (875,25)]) #Put the old version since they are done hovering over the categories

        ####################################
        #Check lower right side being clicked (Only paint has right side buttons)
             
        c = 0 #c for Counter, used to figure out where the tool needs to be positioned 
        
        something_changed = False #Flag to know if any of the tools are hovered on
        
        for item in extra_info[chosen_category][selection_page*6:(selection_page+1)*6]: #Loop through the 6 tools on the page
            #If they are hovered on, blit the animation and check if they are clicked
            if tool_select_buttons[item].collidepoint((mouse_x,mouse_y)): 
                last_selected["Paint Tools"] = True
                something_changed = True
                screen.blit(orig_bottom_right,[int(e*size_ratio) for e in (890,210)]) #Remove any traces by swiping from another one
                image = images_folder[chosen_category + " " + item]

                if chosen_item != "None": #Draw rectangle for old one since we blit orig_bottom_right, which does not include the rectangle
                    item_index = extra_info[chosen_category].index(chosen_item)%6
                    pygame.draw.rect(screen,0,[int(e*size_ratio) for e in [900+60*(item_index%2),220+50*(item_index//2),35,35]],math.ceil(size_ratio))
                    
                screen.blit(pygame.transform.smoothscale(image,(int(50*size_ratio),int(50*size_ratio))),[int(e*size_ratio) for e in [890+60*(c%2),210+50*(c//2)]])
                
                if clicked:
                    screen.blit(orig_bottom_right,[int(e*size_ratio) for e in (890,210)])
                    chosen_item = item!= chosen_item and item or "None" #Change item to be the selected one, or none if it is the same tool they have.
            c+=1
        if not something_changed and last_selected["Paint Tools"]: #If they are not hovering on anything, but were last frame, remove animation
            last_selected["Paint Tools"] = False
            screen.blit(orig_bottom_right,[int(e*size_ratio) for e in (890,210)]) #Remove any traces of animation
            if chosen_item != "None": #Draw rectangle for old one since we blit orig_bottom_right
                item_index = extra_info[chosen_category].index(chosen_item)%6
                pygame.draw.rect(screen,0,[int(e*size_ratio) for e in [900+60*(item_index%2),220+50*(item_index//2),35,35]],math.ceil(size_ratio))


        ####################################
        #Drawing on the canvas

        #Identify what they are doing with a paint_status variable:
                
        #Check for status, 0 = Just Ended, 1 = Just Started, 2 = Holding, 3= Not clicking at all
        if not mouse_press[0] or not paint_canvas.collidepoint((mouse_x,mouse_y)): #They're not clicking or are not in range
            paint_status = paint_status==3 and 3 or paint_status==0 and 3 or 0
        elif clicked or paint_status==3: #Clicked or dragged into the screen, which should count as a new click
            paint_status = 1
        else: #Else, they are just dragging
            paint_status = 2                        

        #Set cliping and only edit inside
        screen.set_clip((paint_canvas))       
        if chosen_item != "None":
            #If they have a tool on:
            #needed specifies the kind of information we need, and thickness_drawn is the thickness, based off of their chosen thickness and the size_ratio
            
            needed = chosen_item in info_required[chosen_category] and info_required[chosen_category][chosen_item] or info_required[chosen_category]["Everything"]
            thickness_drawn = math.ceil(chosen_thickness*size_ratio) #Draws larger or smaller thickness according to screen size
                           
            if needed == "Drag":
                #We need to do something at every step while they drag, and it is complete once they let go
                if paint_status==2:
                    if chosen_item == "Pencil" or chosen_item=="Eraser": #Connect lines to make pencil and eraser
                        col = chosen_item == "Eraser" and (210,210,210) or chosen_colour
                        pygame.draw.circle(screen,col,(mouse_x,mouse_y),thickness_drawn//2)
                        pygame.draw.line(screen,col,(mouse_x,mouse_y),(last_x,lasy_y),thickness_drawn+2)
                    elif chosen_item == "Spray":
                        r = int(thickness_drawn*1.5)
                        for repeat in range (thickness_drawn):
                            #Randomize X, and plug it into the formula to find Y.
                            chosen_x = random.randint(r*-1, r)
                            max_y = int((r**2-chosen_x**2)**0.5)
                            chosen_y = random.randint(max_y*-1,max_y)
                            screen.set_at((mouse_x+chosen_x,mouse_y+chosen_y),chosen_colour)
                    elif chosen_item == "Marker":
                        make_line((mouse_x,mouse_y),(last_x,lasy_y), thickness_drawn, chosen_colour)
                        
                elif paint_status == 0: #The action is complete, screenshot what they have so far and add it to the undo list.
                    undo_list.append(screen.copy().subsurface(paint_canvas))
                    redo_list = []
                    
            elif needed == "Click": #Stamps
                #We only need to do something the instant they click, and can save the screen right after.
                #But while they drag, we show them how it will look if they let go
                
                if paint_status == 1: #Set up all the variables when they just start clicking
                     bf_drawing_canvas = screen.copy().subsurface(paint_canvas)
                     image_wanted = loaded_stamps[chosen_item]
                     len_image = (thickness_drawn*10,int(thickness_drawn*10*image_wanted[1]))
                     stamp_image = pygame.transform.smoothscale(image_wanted[0], len_image)
                     
                elif paint_status == 2: #Blit the original, then the stamp centered on their mouse
                     screen.blit(bf_drawing_canvas, (int(180*size_ratio),int(45*size_ratio)))
                     screen.blit(stamp_image, ([[mouse_x,mouse_y][e]-len_image[e]/2 for e in range (2)]))
                     
                elif paint_status == 0: #Blit the original, and if in bounds, blit the stamp
                    screen.blit(bf_drawing_canvas, (int(180*size_ratio),int(45*size_ratio)))
                    if paint_canvas.collidepoint((mouse_x,mouse_y)):
                        screen.blit(stamp_image, ([[mouse_x,mouse_y][e]-len_image[e]/2 for e in range (2)]))
                        undo_list.append(screen.copy().subsurface(paint_canvas))
                        redo_list = []

                                   
            elif needed == "S+E": #Most shapes and Extras
                #We only care about the starting position and the ending position when they drag.
                #We also let them hold shift to make the selection box a square
                
                if paint_status==1: #Save the original and save the starting position
                    bf_drawing_canvas = screen.copy().subsurface(paint_canvas)
                    shape_start = [mouse_x,mouse_y]

                elif paint_status == 2 or paint_status==0: #Check for shift
                    cur = [mouse_x, mouse_y]
                    shift_held = pygame.key.get_mods() & pygame.KMOD_SHIFT
                    if shift_held:
                        dif = min([abs(a-b) for a,b in zip(shape_start, cur)])
                        for a in range(2):
                            if shape_start[a]>cur[a]:
                                cur[a] = shape_start[a] - dif
                            else:
                                cur[a] = shape_start[a] + dif
                                
                if paint_status==2:
                    #They are dragging. If it is a shape, show them how it looks so far. If it is an extra, show them the selection box
                    
                    screen.blit(bf_drawing_canvas, (int(180*size_ratio),int(45*size_ratio)))

                    #Variables used repetively in dictionary are layed out here to make dictionary a little more clear
                    sx,sy = shape_start
                    mx,my = cur

                    #Note to future self: It took me years to get all of these values for the dictionary, don't change anything unless you know what you're doing
                    
                    connectors = { #This dictionary holds all the vertice locations so that these shapes can all be drawn the same way
                    "Line": [shape_start,cur, shape_start], "Rectangle": [shape_start, [sx, my], cur, [mx,sy]],"Triangle": [cur, [sx,my], [(sx+mx)//2,sy]],
                    "Diamond": [[(sx+mx)//2,sy], [mx,(sy+my)//2], [(sx+mx)//2,my], [sx,(sy+my)//2]], "Parallelogram": [shape_start, [mx + (mx-sx)//5,sy],cur , [sx + (sx-mx)//5,my]],
                    "Falcon": [[(sx+mx)//2,sy], [mx, (sy+my)//2], [mx + (sx-mx)//3,my],[(sx+mx)//2,(sy+my)//2] , [sx + (mx-sx)//3,my], [sx, (sy+my)//2] ],
                    "Star": [[(sx+mx)//2,sy], [sx + (mx-sx)//3,sy + (my-sy)//3],  [sx, sy + (my-sy)//3], [sx + (mx-sx)//4, my + (sy-my)//3], [sx + (mx-sx)//6, my],
                             [(sx+mx)//2, my + (sy - my)//4], [mx + (sx-mx)//6, my], [mx + (sx-mx)//4, my + (sy-my)//3], [mx, sy + (my-sy)//3], [mx + (sx-mx)//3, sy + (my-sy)//3]],
                    "Arrow":[[mx,sy+(my-sy)//3],[mx,my+(sy-my)//3],[sx+(mx-sx)//3, my+(sy-my)//3],[sx+(mx-sx)//3,my],[sx, (my+sy)//2],[sx+(mx-sx)//3,sy],[sx+(mx-sx)//3,sy+(my-sy)//3]],
                    "Envelope":[[sx,sy], [sx,my], cur, [mx,sy], [(mx+sx)//2, (sy+my)//2], [sx,sy], [mx,sy]],
                    "Lightning":[[sx+(mx-sx)//7,sy],[sx+(mx-sx)//3,sy+(my-sy)//4], [(sx+mx)//2, sy+(my-sy)//4], cur, [(sx+mx)//2, (sy+my)//2], [sx+(mx-sx)//4,(sy+my)//2], [sx,sy+(my-sy)//7]],
                    "Cross":[[mx+(sx-mx)//3,sy],[mx+(sx-mx)//3,sy+(my-sy)//3],[mx,sy+(my-sy)//3],[mx,my+(sy-my)//3],[mx+(sx-mx)//3,my+(sy-my)//3],[mx+(sx-mx)//3,my],
                             [sx+(mx-sx)//3,my],[sx+(mx-sx)//3,my+(sy-my)//3],[sx,my+(sy-my)//3],[sx,sy+(my-sy)//3],[sx+(mx-sx)//3,sy+(my-sy)//3],[sx+(mx-sx)//3,sy]]
                        }
                    if chosen_item in connectors: #One of the 11 shapes in the dictionary
                        #If they chose to fill it, make the filled polygon. Then, make the outline by creating lines from all the vertices. The lines are made with circles
                        if chosen_filled:
                            pygame.draw.polygon(screen,chosen_filled,connectors[chosen_item])

                        for st, en in zip(connectors[chosen_item], connectors[chosen_item][1:]+[connectors[chosen_item][0]]):
                            make_line(st, en, thickness_drawn//2, chosen_colour)
                            
                    elif chosen_item == "Ellipse": #Draw the elipse since it cannot be done with draw.polygon
                        if chosen_filled:
                            pygame.draw.ellipse(screen, chosen_filled, (min(mx,sx),min(my,sy),abs(mx-sx),abs(my-sy)))
                        if not (abs(mx-sx)<thickness_drawn*2 or abs(my-sy)<thickness_drawn*2):
                            pygame.draw.ellipse(screen, chosen_colour, (min(mx,sx)-1,min(my,sy),abs(mx-sx),abs(my-sy)), thickness_drawn)
                            pygame.draw.ellipse(screen, chosen_colour, (min(mx,sx)+1,min(my,sy),abs(mx-sx),abs(my-sy)), thickness_drawn)
                            pygame.draw.ellipse(screen, chosen_colour, (min(mx,sx),min(my,sy)-1,abs(mx-sx),abs(my-sy)), thickness_drawn)
                            pygame.draw.ellipse(screen, chosen_colour, (min(mx,sx),min(my,sy)+1,abs(mx-sx),abs(my-sy)), thickness_drawn)
                        else:
                            pygame.draw.ellipse(screen, chosen_colour, (min(mx,sx),min(my,sy),abs(mx-sx),abs(my-sy)))
                    else: #One of the extras (ex. crop)
                        layer = pygame.Surface((abs(mx-sx),abs(my-sy)))
                        layer.set_alpha(100)
                        screen.blit(layer, (min(mx,sx),min(my,sy))) 

                        
                elif paint_status == 0: #They just let go
                    if chosen_category == "Extras": #If it was an extra, do the effect wanted
                        screen.blit(bf_drawing_canvas, (int(180*size_ratio),int(45*size_ratio)))
                        
                        sx,sy = shape_start
                        mx,my = cur

                        rect_args = [min(mx,sx),min(my,sy),abs(mx-sx),abs(my-sy)]
                        canvas_args = list(paint_canvas)
                        cur_screen = screen.copy()
                        
                        if paint_canvas.collidepoint(mx,my):
                            #They are in range. Make the special effect they asked for
                            
                            if chosen_item == "Crop": #Take the part they selected and make it the screen
                                cropped_part = pygame.transform.scale(cur_screen.subsurface(rect_args), (canvas_args[2],canvas_args[3]))
                                screen.blit(cropped_part, (canvas_args[0],canvas_args[1]))
                                
                            elif chosen_item == "Flip V" or chosen_item == "Flip H": #Flip the selection along the x/y axis
                                x_bool, y_bool = [True,False] if chosen_item == "Flip H" else [False,True]
                                flipped_part = pygame.transform.flip(cur_screen.subsurface(rect_args),x_bool, y_bool)
                                screen.blit(flipped_part, (rect_args[0],rect_args[1]))
                                
                            elif chosen_item == "Darken": #Create a transluecent layer on top to darken the selection
                                layer = pygame.Surface(rect_args[2:])
                                layer.set_alpha(150)
                                screen.blit(layer, rect_args[0:2])
                                
                            elif chosen_item == "Inverse V": #Split the selection in two, and flip each. This creates a folding effect
                                inversed_part = cur_screen.subsurface(rect_args)
                                upper_inverse = pygame.transform.flip(inversed_part.subsurface((0,0,rect_args[2],rect_args[3]//2)),False, True)
                                lower_inversed = pygame.transform.flip(inversed_part.subsurface((0,rect_args[3]//2,rect_args[2],rect_args[3]//2)),False, True)
                                screen.blit(upper_inverse, rect_args[:2])
                                screen.blit(lower_inversed, (rect_args[0],rect_args[1] + rect_args[3]//2))
                                
                            elif chosen_item == "Inverse H": #Same as Inversing V, but this one goes left and right
                                inversed_part = cur_screen.subsurface(rect_args)
                                left_inverse = pygame.transform.flip(inversed_part.subsurface((0,0,rect_args[2]//2,rect_args[3])),True, False)
                                right_inversed = pygame.transform.flip(inversed_part.subsurface((rect_args[2]//2,0,rect_args[2]//2,rect_args[3])),True, False)
                                screen.blit(left_inverse, rect_args[:2])
                                screen.blit(right_inversed, (rect_args[0] + rect_args[2]//2, rect_args[1]))
                                
                            elif chosen_item == "Inverse Color": #Change every pixel within range to the inverse of itself (255-r,255-g,255-b)
                                pxarray = pygame.PixelArray(screen)
                                for pixel_x in range (rect_args[0],rect_args[0]+rect_args[2]+1):
                                    for pixel_y in range (rect_args[1],rect_args[1]+rect_args[3]+1):
                                        pixel_colour = pxarray[pixel_x,pixel_y]
                                        new_col = 16777215 - pixel_colour
                                        pxarray[pixel_x,pixel_y] = new_col
                                del pxarray

                    undo_list.append(screen.copy().subsurface(paint_canvas))
                    redo_list = []
                    
                    
            elif needed == "Special":
                #These tools are unique and have features that can't be easily categorized
                
                canvas_args = list(paint_canvas)
                if chosen_item == "Fill" and paint_status==1: #Fills with pixel array by using BFS
                    
                    pxarray = pygame.PixelArray(screen)
                    orig_col = pxarray[mouse_x,mouse_y] #The first colour they click
                    wanted_col = screen.map_rgb(chosen_colour) #The colour they want to turn the orig_col into
                    
                    if orig_col != wanted_col: #Check to see if action must be done
                        checking = set(["%s,%s"%(mouse_x,mouse_y)]) #Set of positions to check
                        #Since we needed a set, and lists are not hashable, I stored the positions as strings, x and y seperated by a comma
                        while checking:
                            next_level = [] #List of items to check next time the loop runs
                            for item in checking:
                                x,y = [int(e) for e in item.split(",")]
                                if paint_canvas.collidepoint(x,y) and pxarray[x,y] == orig_col:
                                    pxarray[x,y] = wanted_col
                                    next_level += ["%s,%s"%(x+1,y), "%s,%s"%(x-1,y),"%s,%s"%(x,y+1),"%s,%s"%(x,y-1)]
                                    
                            checking = set(next_level)
                            
                        undo_list.append(screen.copy().subsurface(paint_canvas))
                        redo_list = []
                        
                    del pxarray
                    
                elif chosen_item == "Move" or chosen_item == "Rotate":
                    #first, they select a box to move/rotate
                    #then, they move their mouse around and it follows them
                    #When they click again, it is done
                    #If they go out of the canvas, it is cancelled
                    
                    if paint_status == 0: #They just stopped holding
                        if not move_selected and move_started and paint_canvas.collidepoint(mouse_x,mouse_y): #They selected an area (STEP 3)
                            mx,my = mouse_x,mouse_y
                            sx,sy = shape_start
                            rect_args = [min(mx,sx), min(my,sy), abs(mx-sx), abs(my-sy)]

                            screen.blit(bf_drawing_canvas, (int(180*size_ratio),int(45*size_ratio)))
                            move_selected = screen.copy().subsurface(rect_args)
                            move_selected.set_colorkey((210,210,210))
                            
                            pygame.draw.rect(screen,(210,210,210),rect_args)
                                                        
                            third_step_canvas = screen.copy().subsurface(paint_canvas)

                        elif move_started: #They selected out of bounds
                            screen.blit(bf_drawing_canvas, (int(180*size_ratio),int(45*size_ratio)))
                            move_selected = None
                            move_started = False
                            
                    elif paint_status == 1: #They just clicked
                        if move_selected: #They have chosen the final place to move it, and are clicking to change it (STEP 5)
                            #(Final Step)
                            screen.blit(third_step_canvas, (int(180*size_ratio),int(45*size_ratio)))

                            if chosen_item == "Move":
                                #Center the part that must be moved
                                screen.blit(move_selected,[mouse_x-rect_args[2]//2,mouse_y-rect_args[3]//2])
                                
                            elif chosen_item == "Rotate":
                                mid_x,mid_y = ((sx+mx)//2, (sy+my)//2)
                                x,y = (mouse_x - mid_x, mouse_y - mid_y)

                                angle_wanted = math.degrees(math.atan2(x,y)) - 90  #Calculating the angle we need to rotate it

                                #Take the image, rotate it by the angle we want, then position it on the same mid point so that it rotates around it's center
                                
                                rotated_image = pygame.transform.rotate(move_selected, angle_wanted)
                                rotated_rect = rotated_image.get_rect()
                                
                                screen.blit(rotated_image, (mid_x - rotated_rect.width//2 ,mid_y - rotated_rect.height//2))
                            
                            move_selected = None
                            move_started = False
                            
                            undo_list.append(screen.copy().subsurface(paint_canvas))
                            redo_list = []
                    
                        else: #They are starting (STEP 1)
                            bf_drawing_canvas = screen.copy().subsurface(paint_canvas)
                            shape_start = [mouse_x,mouse_y]
                            move_started = True

                    #They are holding on the mouse    
                    elif paint_status == 2 and not move_selected and move_started: #They are selecting an area to move (STEP 2)
                        mx,my = mouse_x,mouse_y
                        sx,sy = shape_start

                        #Show them the layer they are selecting so far
                        screen.blit(bf_drawing_canvas, (int(180*size_ratio),int(45*size_ratio)))
                        layer = pygame.Surface((abs(mx-sx),abs(my-sy)))
                        layer.set_alpha(100)
                        screen.blit(layer, (min(mx,sx),min(my,sy)))

                        
                    elif paint_status == 3 and move_selected and paint_canvas.collidepoint(mouse_x,mouse_y):
                        #They already selected an area, and are now choosing the new position (STEP 4)
                        screen.blit(third_step_canvas, (int(180*size_ratio),int(45*size_ratio)))
                        if chosen_item == "Move":
                            screen.blit(move_selected,[mouse_x-rect_args[2]//2,mouse_y-rect_args[3]//2])
                        else:
                            mid_x,mid_y = ((sx+mx)//2, (sy+my)//2)
                            x,y = (mouse_x - mid_x, mouse_y - mid_y)

                            angle_wanted = math.degrees(math.atan2(x,y)) - 90#Calculating the angle we need to rotate it

                            #Take the image, rotate it by the angle we want, then position it on the same mid point so that it rotates around it's center
                            
                            rotated_image = pygame.transform.rotate(move_selected, angle_wanted)
                            rotated_rect = rotated_image.get_rect()
                            
                            screen.blit(rotated_image, (mid_x - rotated_rect.width//2 ,mid_y - rotated_rect.height//2))
                        
                    elif paint_status == 3 and move_selected: #They hovered away from the canvas
                        #Cancel what they have done so far
                        screen.blit(bf_drawing_canvas, (int(180*size_ratio),int(45*size_ratio)))
                        move_selected = None
                        move_started = False
                    
                elif chosen_item == "Text":
                    #Track when they are typing and display it on the screen
                    
                    if paint_status == 1 and not typing_started: #They just started typing, make the variables
                        typing_started = [mouse_x,mouse_y]
                        typing_text = ""
                        bf_drawing_canvas = screen.copy().subsurface(paint_canvas)

                    elif typing_started and (paint_status == 1 or not paint_canvas.collidepoint(mouse_x,mouse_y) or pressed_enter):
                        #They finished by clicking, entering, or moving mouse away
                        
                        screen.blit(bf_drawing_canvas, (int(180*size_ratio),int(45*size_ratio)))
                        font_size_w = thickness_drawn*2
                        myfont = pygame.font.SysFont("arial", font_size_w)
                        text_surface = myfont.render(typing_text, True, chosen_colour)
                        screen.blit(text_surface,typing_started)
                        
                        undo_list.append(screen.copy().subsurface(paint_canvas))
                        redo_list = []
                        
                        typing_started = False
                        
                    elif typing_started: #They are typing right now
                        
                        typing_text += new_text #Adding the text they type
                        typing_text = typing_text[:len(typing_text)-del_clicked] #Delete any that they delete
                        
                        #Make the shown text include a | every couple seconds for a second
                        shown_text = typing_text
                        if loop_start % 2 < 1:
                            shown_text += "|"

                        #Blit the original canvas, then the text they have typed so far
                        screen.blit(bf_drawing_canvas, (int(180*size_ratio),int(45*size_ratio)))
                        font_size_w = thickness_drawn*2
                        myfont = pygame.font.SysFont("arial", font_size_w)
                        text_surface = myfont.render(shown_text, True, chosen_colour)
                        screen.blit(text_surface,typing_started)
                        
                elif chosen_item == "Magnify":
                    #While they hover around the canvas, it shows them the rectangle they can see
                    #While they hold, they magnify it
                    
                    if paint_status == 2: #They are holding it, so show them the magified image
                        screen.blit(bf_drawing_canvas, canvas_args[:2])
                        rect_args = [mouse_x-thickness_drawn*3,mouse_y-thickness_drawn*3, thickness_drawn*6,thickness_drawn*6]

                        #Don't subsurface out of bounds, check if you're going over
                        if rect_args[1]<0:
                            rect_args[1] = 0
                        elif rect_args[1] + rect_args[3]>499:
                            rect_args[3] = 499-rect_args[1]

                        #Blit the part they are magnifying
                        magnified_part = screen.copy().subsurface(rect_args)
                        screen.blit(pygame.transform.scale(magnified_part, canvas_args[2:]),canvas_args[:2])
                        
                    elif (paint_status == 3 or paint_status==1) and paint_canvas.collidepoint(mouse_x,mouse_y): #Hovering around without clicking
                        if magnify_start: #They have already started magnifying
                            screen.blit(bf_drawing_canvas, canvas_args[:2])
                        else: #They just started hovering, take an image first
                            bf_drawing_canvas = screen.copy().subsurface(paint_canvas)
                            magnify_start = True
                            
                        layer = pygame.Surface((thickness_drawn*6,thickness_drawn*6))
                        layer.set_alpha(75)
                        screen.blit(layer, ([e-thickness_drawn*3 for e in [mouse_x,mouse_y]]))
        
                    elif paint_status == 3 and magnify_start: #They were magnifying before, return the screen to normal state
                        screen.blit(bf_drawing_canvas, (int(180*size_ratio),int(45*size_ratio)))
                        magnify_start = False 
                
                elif chosen_item == "Dropper" and paint_status==1: #Change their chosen colour
                    screen.set_clip(None) #We need to adjust colour outside, so we must get rid of the clipping
                    chosen_colour = screen.get_at((mouse_x,mouse_y))
                    make_color()
                elif chosen_item == "Polygon":
                    #Let them connect vertices, and we draw circles. If they click on the first one, it makes the polygon in order.
                    #If they go out of the canvas or connect it back with less than 3 vertices, ignore the action
                    
                    if not polygon_start and paint_status==1: #First point they click, keep track of the variables
                        polygon_start = [mouse_x,mouse_y]
                        polygon_points = [polygon_start]
                        
                        bf_drawing_canvas = screen.copy().subsurface(paint_canvas)
                        polygon_start = pygame.draw.circle(screen, chosen_colour, polygon_start, 15, 1) #The rect of the first circle, to check if they click on it
                        
                    elif paint_status==1: 
                        if polygon_start.collidepoint((mouse_x,mouse_y)): #They are clicking the first point to finish the polygon
                            screen.blit(bf_drawing_canvas, (int(180*size_ratio),int(45*size_ratio)))
                            if len(polygon_points)>2: #They made more than 2 points, draw the polygon like the other shapes
                                if chosen_filled:
                                    pygame.draw.polygon(screen,chosen_filled,polygon_points)
                                    
                                for st, en in zip(polygon_points, polygon_points[1:]+[polygon_points[0]]):
                                    make_line(st, en, thickness_drawn//2, chosen_colour)
                                    
                                undo_list.append(screen.copy().subsurface(paint_canvas))
                                redo_list = []
                                
                            else: #They didnt not select enough points, cancel the polygon
                                polygon_points = [] 
                            polygon_start = None
                            
                        else: #They're connecting more points
                            pygame.draw.circle(screen, chosen_colour, (mouse_x,mouse_y), 15, 1)
                            polygon_points.append([mouse_x,mouse_y])
                            
                    elif not paint_canvas.collidepoint((mouse_x,mouse_y)) and polygon_start: #They hovered out
                        screen.blit(bf_drawing_canvas, (int(180*size_ratio),int(45*size_ratio)))
                        polygon_points = []
                        polygon_start = None
                                                       
                        
        screen.set_clip(None) #Remove clipping since it is done


        ####################################
        #Check top bottons (Undo/Redo/Save)
        
        veiwing_image = None #Look for any image hovered on
        for item in top_buttons:
            if top_buttons[item].collidepoint((mouse_x,mouse_y)):
                veiwing_image = item
                break

        if last_selected["Top Bar"]: #If they had an animation last time, blit it back to how it should be
            screen.blit(last_selected["Top Bar"][0],last_selected["Top Bar"][1])
            last_selected["Top Bar"] = None
            
        if veiwing_image: #If they are hovering on it, animate it to have a layer and selection box
            
            dimensions = list(top_buttons[veiwing_image])
            pos, size = dimensions[:2], dimensions[2:]
        
            last_selected["Top Bar"] = [screen.copy().subsurface(pos, size), pos] #[surface, position]. If it is not None earlier, the surface is blit at the pos, removing the animation

            #Making the animation
            overlay = pygame.Surface(size)
            overlay.set_alpha(100)
            screen.blit(overlay,pos)
            pygame.draw.rect(screen,(255,255,255),(pos,size),1)
            
            if clicked:
                #They clicked one of them
                canvas_args = list(paint_canvas)
                if veiwing_image == "Undo" and len(undo_list)>0:
                    #They clicked undo. Move the last action to the redo list, and then take the last frame we have since the last action and put it on top.
                    #undo_list is a list of images of how the states the canvas is in after every action is complete
                    
                    last = undo_list.pop()
                    redo_list.append(last)
                    if len(undo_list)>0:
                        screen.blit(pygame.transform.scale(undo_list[-1],canvas_args[2:]),canvas_args[:2])
                    else:
                        pygame.draw.rect(screen, (210,210,210),canvas_args)
                    
                elif veiwing_image == "Redo" and len(redo_list)>0:
                    #They clicked redo. Move the last image we moved from undo back into redo, and blit that image back on top
                    last = redo_list.pop()
                    undo_list.append(last)
                    screen.blit(pygame.transform.scale(last,canvas_args[2:]),canvas_args[:2])
                    
                elif veiwing_image == "Save":
                    #Save their file according to the file_name they chose at the very start
                    local_saves[file_name] = screen.copy().subsurface(canvas_args)
                    pygame.image.save(screen.copy().subsurface(canvas_args), "Saves//"+file_name+".png") #file_name

    ####################################
    # Make the custom select paint menu
                    
    elif window_chosen == "Select Paint":
        #Give them the option between save and load at the top
        largest_size, x_taken, y_taken, myfont = font_size("timesnewroman","Load",int(100*size_ratio),int(50*size_ratio),100)
        items_positions = {"New":[280,80],"Load":[400,80]}
        for item in items_positions:
            stuff = items_positions[item]
            text_with_outline(item,myfont,(0,0,0), (255,255,255), stuff[0], stuff[1], 1, True) #Create the text
            
            if selection_menu == item: #If it is the selected one, make an elipse under it 
                pygame.draw.ellipse(screen,(255,255,255),(int(stuff[0]*size_ratio),int(stuff[1]*size_ratio)+y_taken,x_taken,int(20*size_ratio)))
                
            elif clicked and stuff[0]*size_ratio<=mouse_x<=stuff[0]*size_ratio+x_taken and stuff[1]*size_ratio<=mouse_y<=stuff[1]*size_ratio+y_taken:
                #It is selected, switch menus
                selection_menu = item

                
        if selection_menu == "New":
            #Allow them to name their project and start a new one

            position = [235,335]
            
            #Make the text label on top of the text box
            largest_size, x_taken, y_taken, myfont = font_size("calibri","Name your project:",int(250*size_ratio),int(35*size_ratio),100)
            text_with_outline("Name your project:",myfont,(255,255,255), (0,0,0), position[0], position[1]-35, 1, True)
            
            #Make the text box
            outer_box = pygame.draw.rect(screen,0, ([int(e*size_ratio) for e in position],[int(i*size_ratio) for i in [250,50]]),1)
            
            field_box = pygame.Surface([int(i*size_ratio) for i in [250,50]])  
            field_box.set_alpha(150)
            field_box.fill((200,200,200))
            screen_button = screen.blit(field_box,[int(e*size_ratio) for e in position])

            #Check if they selected the text box
            if screen_button.collidepoint((mouse_x,mouse_y)) and clicked:
                typing_paint = True 
                new_paint = ""
                
            elif clicked or pressed_enter: #Check if they had it selected, but they clicked away or enter
                typing_paint = False

            #Add to the text and remove from it according to user input
            if typing_paint:
                new_paint += new_text
                new_paint = new_paint[:len(new_paint)-del_clicked]

            #Change the text shown to include | every second for half a second
            text = new_paint
            if loop_start%1>0.5 and typing_paint:
                text += "|"

            #Display the name they have chosen
            largest_size, x_taken, y_taken, myfont = font_size("calibri",text,int(250*size_ratio),int(50*size_ratio),100)
            text_with_outline(text,myfont,(255,255,255), (0,0,0), position[0], position[1], 1, True)

            #Make the create button and see if it is clicked
            image_clicked = draw_images({"Create":[630, 350]},mouse_x,mouse_y,"Clicked")
            
            if image_clicked != "None":
                #Animate it to be larger
                screen.blit(pygame.transform.scale(images_folder["Create"],[int(i*size_ratio) for i in [200,80]]),(int((615)*size_ratio),int((340)*size_ratio)))
                
                if clicked: #Make a brand new paint, and let them start painting
                    transition_value = 6
                    next_window = "Paint"
                    if new_paint == "":
                        new_paint = " "
                    file_name = new_paint
                    chosen_thickness = 5 #This is the thickness they choose from the thickness slider
                    chosen_colour = (0,0,0) #This is their colour of choice
                    chosen_filled = None #This is their colour for the filled portions of the shapes, or None if it is not filled
                    chosen_category = "Tools" #Indicates if you are looking at Tools, Shapes, Stamps, or Extras
                    chosen_item = "Pencil" #Variable for the Selected item
                    undo_list = []
                    redo_list = []
                    
        elif selection_menu == "Load": #if they wish to load a saved file
            saved_items = {"Online saves":user_info["Online saves"],"Local saves":local_saves}
            #Display both online and local menus
            for item in select_save_page:
                #Display the option rectangles (Online Saves and Local Saves), one of each side of the screen

                #Show the text above the rectangle to diffrenciate them
                largest_size, x_taken, y_taken, myfont = font_size("calibri",item,int(250*size_ratio),int(35*size_ratio),100)
                properties = select_save_page[item] #[x position, y position, scroll value]
                
                text_with_outline(item,myfont,(255,255,255), (0,0,0), properties[0], properties[1], 1, True)

                #Make the transparent rectangles
                trans_screen = pygame.Surface((x_taken,int(200*size_ratio)))
                trans_screen.set_alpha(50)
                background_trans = screen.blit(trans_screen,(int(properties[0]*size_ratio),int(properties[1]*size_ratio)+y_taken))
                
                if background_trans.collidepoint((mouse_x,mouse_y)): #Account for scrolling if they are on the rectangle
                    properties[2] += scrolled
                    if properties[2]>=len(saved_items[item].keys())-3: #Over the limit
                        properties[2]= len(saved_items[item].keys())-4
                    if properties[2]<0: #Under the minimum.
                        properties[2] = 0

                #Figure out which name takes the largest size, and follow the font it needs
                        
                save_keys = list(saved_items[item].keys()) #Names of all the saves
                
                largest_size2, x_taken2, y_taken2, myfont2 = 99999,0,0,None #Variables used to hold the largest size that fits all of them 
                size = (x_taken,int(200*size_ratio/4)) #The size needed for text c
                
                for save_key in save_keys: #Get the max size for the text that fits all of them to make it look professional 
                    largest_size3, x_taken3, y_taken3, myfont3 = font_size("calibri",save_key,size[0],size[1],100)
                    if largest_size3<largest_size2:
                        largest_size2, x_taken2, y_taken2, myfont2 = largest_size3, x_taken3, y_taken3, myfont3
                        
                for current_save in range(properties[2],properties[2]+4): #Make up to 4 saves shown
                    if 0<= current_save < len(save_keys): #Check if there are even that many
                        #Figure out the spot for the save
                        spot = (int(properties[0]*size_ratio),int(properties[1]*size_ratio+y_taken +size[1]*(current_save - properties[2])))

                        #Make a transparent surface on top
                        trans_screen = pygame.Surface(size)
                        if spot[0]<=mouse_x<=spot[0]+size[0] and spot[1]<=mouse_y<=spot[1]+size[1]: #If they are hovering, make it lighter
                            trans_screen.set_alpha(100)
                            
                            #Make sample of the program so they know what they are clicking
                            file_name = save_keys[current_save]
                            wanted_file = saved_items[item][file_name]
                            trans_file = pygame.transform.scale(wanted_file,[int(e*size_ratio) for e in [100,75]])
                            screen.blit(trans_file,([int(e*size_ratio) for e in [468,310]]))
                            
                            if clicked: #Transition into the loaded file because they clicked
                                transition_value = 6
                                next_window = "Paint"
                                chosen_thickness = 5
                                chosen_colour = (0,0,0)
                                chosen_filled = None
                                chosen_category = "Tools" #Tools, Shapes, Stickers, Animations
                                chosen_item = "Pencil" #Selected item
                                
                                undo_list = [wanted_file]
                                redo_list = []
                        else:
                            trans_screen.set_alpha(170)
                            
                        #Blit the transparent surface then make the text for the save on top
                        screen.blit(trans_screen,spot)                        
                        text_with_outline(save_keys[current_save],myfont2,(255,255,255), (0,0,0), spot[0], int(spot[1]+((size[1]-y_taken2)/2)), 1, False)

    ####################################
    # They are checking their account
    elif window_chosen == "Account":
        if user_info["Logged in"]:
            #They are logged in, tell them that they are
            image_clicked = draw_images({'Checkbox Y': [240, 90,"Don't check collide"],"Sign Out": [630, 340]},mouse_x,mouse_y,"Clicked")
            largest_size, x_taken, y_taken, myfont = font_size("timesnewroman","You are signed in",int(300*size_ratio),int(150*size_ratio),100) #"Welcome, Player"
            text_with_outline("You are signed in",myfont,(190,197,197), (0,40,0), 290, 90, 1, True)
            
            if image_clicked=="Sign Out" and clicked: #They logged out, revert the variables back to logged off status
                user_info = {"Username":"Guest","Logged in": False,"Online saves":[]}
                
            elif image_clicked == "Sign Out": #They are hovering on the button, make it larger for them
                image = screen.blit(pygame.transform.scale(images_folder["Sign Out"],[int(i*size_ratio) for i in [220,70.4]]),(int(625*size_ratio),int(335*size_ratio)))

        else:
            #They are signing in

            #Display a message at the top to tell them what to do

            if sign_failure[0] != 0: #If they have recently messed up signging in, tell them why
                message = sign_failure[1]
                if loop_start - sign_failure[0] > 5: #If it has been long enough, change the variable so that it does not tell them anymore
                    sign_failure = [0,""]
            else:
                message = "You are not signed in"

            #Display the message at the top
            largest_size, x_taken, y_taken, myfont = font_size("timesnewroman",message,int(300*size_ratio),int(150*size_ratio),100) #"Welcome, Player"
            text_with_outline(message,myfont,(190,197,197), (60,0,0), 290, 90, 1, True)

            #Display the X button to show that they are not logged in, and the buttons
            image_database= {'Checkbox X': [240, 90,"Just a btton to show"],'Register': [630, 280],"Sign in": [630, 350]}
            image_clicked = draw_images(image_database,mouse_x,mouse_y,"Clicked")

            #Make the text box for username and password
            field_box = pygame.Surface([int(i*size_ratio) for i in [250,50]])  
            field_box.set_alpha(150)
            field_box.fill((200,200,200))
            
            for field in login_fields: #Check their textboxes
                position = login_fields[field]["Buttonpos"]   #The position of the text box
                
                #Tell them to enter their username or password into the box:
                largest_size, x_taken, y_taken, myfont = font_size("calibri",field,int(250*size_ratio),int(35*size_ratio),100)
                text_with_outline(field,myfont,(255,255,255), (0,0,0), position[0], position[1]-35, 1, True)

                #Make the box
                outer_box = pygame.draw.rect(screen,0, ([int(e*size_ratio) for e in position],[int(i*size_ratio) for i in [250,50]]),1)

                #Put the transparent layer on top to make it seem like a text box
                screen_button = screen.blit(field_box,[int(e*size_ratio) for e in position]) #The text box rectangle
                
                if screen_button.collidepoint((mouse_x,mouse_y)) and clicked: #They just selected the rectangle
                    login_fields[field]["Editing"] = True
                    login_fields[field]["Text"] = ""
                    
                elif clicked or pressed_enter: #They just finished typing
                    login_fields[field]["Editing"] = False
                    
                if login_fields[field]["Editing"]: #They're typing, account for any changes
                    login_fields[field]["Text"] += new_text
                    login_fields[field]["Text"] = login_fields[field]["Text"][:len(login_fields[field]["Text"])-del_clicked] #When they click delete

                #Display all hashtags for password but display the username fully
                text = field != "Password" and login_fields[field]["Text"] or len(login_fields[field]["Text"])*"#"
                
                #Add a | to the text every second for half a second
                if loop_start%1>0.5 and login_fields[field]["Editing"]:
                    text += "|"

                #Display the text in the box, fitting it all inside the box
                largest_size, x_taken, y_taken, myfont = font_size("calibri",text,int(250*size_ratio),int(50*size_ratio),100)
                text_with_outline(text,myfont,(255,255,255), (0,0,0), position[0], position[1], 1, True)
                
            if image_clicked != "None": #Check for the sign in/register options
                #Animate the option to be larger
                x,y = image_database[image_clicked]
                image = screen.blit(pygame.transform.scale(images_folder[image_clicked],[int(i*size_ratio) for i in [200,80]]),(int((x-15)*size_ratio),int((y-10)*size_ratio)))
                
                if clicked: #Check if they clicked on the option
                    #Send a log in /register request to the server
                    params = {"Request":image_clicked,"Username":login_fields["Username"]["Text"],"Password":login_fields["Password"]["Text"]}
                    response = requests.get(docs_url,params)

                    given = response.json() #The response, in a string
                    
                    if given=="Incorrect username" or given=="Username taken" or given=="Incorrect password":
                        # They messed up one of them: Username taken/ incorrect username/ incorrect password
                        sign_failure = [time.time(),given] #Switch the variable to the time and message, which will be shown for the next few seconds
                        
                    elif given == "Account Created": #Sign up worked!
                        user_info = {"Username":login_fields["Username"]["Text"],"Logged in": True,"Online saves":{}} #Log them in
                    else: #Sign in worked!
                        user_info = {"Username":login_fields["Username"]["Text"],"Logged in": True,"Online saves":eval(given)} #Log them in


            
    #Transition if wanted to (Shades the screen in and out from menu to menu)
    if transition_value !=0: #The shade is changing
        
        current_shade += transition_value*(loop_start-(loop_end or loop_start))*20 #Change the shade according to the transition value
        
        if current_shade < 0 and transition_value<0: #It has fading from opaque to completely transparent, job finished
            transition_value = 0
            current_shade = 0
            
        elif current_shade > 255 and transition_value>0: #It has faded from the menu to a black screen, now transition
            transition_value *= -1 #Switch it to fade the other way
            current_shade = 255
            window_chosen=next_window #Switch windows
            update_menu() #Change the menu according to the new window
            pygame.time.wait(150) #Leave the black screen on for 150 miliseconds
            
        transition_image = screen.copy() #Take a copy of the screen before putting on the surface

        #Put on the shade
        transparent_screen = pygame.Surface([int(i*size_ratio) for i in original_screen])  
        transparent_screen.set_alpha(current_shade)    
        screen.blit(transparent_screen, (0,0))

    pygame.display.flip() #Display all the changes to the player
    loop_end = loop_start #Keep track of when the loop started to compare it to the next loop
    last_x,lasy_y = mouse_x,mouse_y #Keep track of old mouse positions to connect them to future ones

#Quit everything
pygame.quit()
pygame.mixer.init()
pygame.mixer.music.stop()
