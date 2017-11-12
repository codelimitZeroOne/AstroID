# Importing necessary libraries
import pygame
import AstroUtil
import math
import sys
import threading
from win32api import GetSystemMetrics

# Initiate pygame
pygame.init()

# Preset colours
BLACK = (0, 0, 0)
GREY = (10, 10, 10)
WHITE = (255, 255, 255)
LIGHTGREY = (100, 100, 100)
GREEN = (100, 200, 0)
RED = (255, 0, 0)
DARKRED = (255, 20, 0)

# Gravitational Constant, used in Newton's law of universal gravitation (equation)
G = 6.6740831e-11

# Number of earth days per orbit for each planet in this list
# Used to find a ratio when determining the speed change
INITIALEARTHDAYS = [88, 224.7, 365.256, 686.93, 4330.6, 10755.7, 30687, 60190, 90583.488]
EARTHDAYS = [88, 224.7, 365.256, 686.93, 4330.6, 10755.7, 30687, 60190, 90583.488]

# Default and current velocity lists
# Used to find ratios when determining speed changes as well
defVel = []
nowVel = []

# This list represents number of frames per revolution for each body
framesPerRev = []

# The win32api library retrieves the native resolution of the screen, then sets that to the size of the pygame window
# Enables a better user experience
size = (GetSystemMetrics(0), GetSystemMetrics(1))
screen = pygame.display.set_mode(size, pygame.FULLSCREEN)

# This variable is used at the end of the mainloop to keep to a fixed framerate
clock = pygame.time.Clock()

# This variable determines how many frames represent one earth day
# Variable is changed when the speed changes
framesPerDay = 6

# This variable determines which system is currently being viewed
system = "MENU"

""" These are the variables for displaying the planetary information
Initially, the information for the sun is displayed """

# File name of selected body
file = "Systems\Solar System\Sun.png"
# Orbit radius of the body
orbitRad = 0
# Index of the body in the bodies list
listNum = 0
# minMass and maxMass are forms of validation so the mass of the body doesn't go too high or too low
# Otherwise it'll be going too fast/too slow
# Minimum mass the mass slider allows the body to be
minMass = 1e28
# Maximum mass the mass slider allows the body to be
maxMass = 1e32

""" CAN'T REMEMBER WHAT THIS DOES TBH"""
""" COME BACK TO IT"""
""""""
""""""
currentMin = 0
currentMax = 0

""""""
""""""

# If the user is left clicking then this variable turns true
# Used for the system/body buttons
clickOnL = False
# If the user is right clicking then this variable turns true
# Used to display the mini-menu for adding/removing bodies and systems
clickOnR = False

# If this variable is true, system buttons are displayed, "add system"/"remove system" etc
sysButs = False
# If this variable is true, body buttons are displayed, "add body"/"remove body" etc
bodButs = False

# System number that is selected, used for entering systems
sysNum = 0

# These two variables are used to detect which system/body is selected to be deleted
sysSelected = 0
bodSelected = 0

# This variable is a boolean and it can be used if I want to execute something a frame late
nextFZoom = False

# The variable is for the orbit lines; by default they are off
orbLines = False

""" CLASSES """

# This is the class which can define any celestial body, whether it be a planet or a star or a satellite
class Body(pygame.sprite.Sprite):
    def __init__(self, filename, orbit, radius, mass, order, minMass, maxMass, SYS):
        # Making the body a sprite makes it easier to deal with collisions
        # There's built in function for collisions, no need to check coordinates manually
        super(Body, self).__init__()
        self.filename = filename
        self.orbit = orbit
        self.radius = radius
        self.mass = mass
        self.order = order
        self.minMass = minMass
        self.maxMass = maxMass
        self.SYS = SYS
        # Loading the image and drawing it to the screen
        self.image = pygame.image.load(self.filename)
        self.image = pygame.transform.scale(self.image, (self.radius*2, self.radius*2))
        self.rect = self.image.get_rect(center=(size[0]/2 + self.orbit, size[1]/2))

    def orbitSun(self, angle):
        # This gets the current position of the body, and changes the angle it is at relative to the sun using trigonometry
        self.rect = self.image.get_rect(center=((size[0]/2) + (self.orbit * math.cos(angle)), (size[1]/2) - (self.orbit * math.sin(angle))))

    def planetInfo(self):
        # Retrieving variables needed for displaying the planetary information from outside this scope
        global file
        global orbitRad
        global listNum
        global minMass
        global maxMass
        global selected

        # If the user presses on the body, the relevant information is displayed in the info box
        if self.rect.colliderect(mouseRect):
            if pygame.mouse.get_pressed()[0] == 1:
                file = self.filename
                orbitRad = self.orbit
                listNum = self.order
                minMass = self.minMass
                maxMass = self.maxMass
                selected = self

    def CheckCollide(self, mousePos, rightClick):
        global bodSelected

        if rightClick and self.rect.colliderect(mouseRect):
            bodSelected = self

# This class is for any background images that will be used for any of the systems
# The image is loaded and scaled to fit the screen
class Background(pygame.sprite.Sprite):
    def __init__(self, filename):
        super(Background, self).__init__()
        self.filename = filename
        self.image = pygame.image.load(filename)
        # Retrieves and scales the background image to the screen size
        self.image = pygame.transform.scale(self.image, (size[0], size[1]))
        self.rect = self.image.get_rect()

# This class defines any system icon in the main menu
class SystemIcon(pygame.sprite.Sprite):
    def __init__(self, filename, xPos, yPos, diameter):
        # As with the Body class, this is a sprite to make dealing with collisions much easier
        super(SystemIcon, self).__init__()
        self.filename = filename
        self.xPos = xPos
        self.yPos = yPos
        self.diameter = diameter
        self.image = pygame.image.load(filename)
        self.image = pygame.transform.scale(self.image, (diameter, diameter))
        self.rect = self.image.get_rect(center=(xPos, yPos))

    # This functions checks for collisions with the mouse, whether it be a left click or right click
    def checkCollide(self, mousePos, rightClick):
        # The sysNum and sysSelected variables are made global to retrieve from outer scope
        global sysNum
        global sysSelected

        textFont = pygame.font.SysFont("Arial Black", 10)

        # If the mouse is hovered over the icon, the name of the system is shown next to the mouse
        if self.rect.colliderect(mouseRect):
            # To make it seem like a box with an outline, a white box is drawn before the black box and is made slightly thicker
            pygame.draw.rect(screen, WHITE, pygame.Rect(mousePos[0] + 20, mousePos[1], 120, 15))
            pygame.draw.rect(screen, BLACK, pygame.Rect(mousePos[0] + 22, mousePos[1] + 2, 116, 11))
            systemText = textFont.render(self.filename[8:-4], 1, WHITE)
            screen.blit(systemText, (mousePos[0] + 23, mousePos[1]))

            # If the user presses on any of the icons with the left mouse button the program checks which icon has been pressed
            if pygame.mouse.get_pressed()[0] == 1 and rightClick == False:
                if self.filename[8:-4] == "Solar System":
                    sysNum = 0
                    return "SOLAR SYSTEM"
                if self.filename[8:-4] == "Custom System I":
                    sysNum = 1
                    return "CUSTOM SYSTEM I"
                if self.filename[8:-4] == "Custom System II":
                    sysNum = 2
                    return "CUSTOM SYSTEM II"
                if self.filename[8:-4] == "Custom System III":
                    sysNum = 3
                    return "CUSTOM SYSTEM III"
                if self.filename[8:-4] == "Custom System IV":
                    sysNum = 4
                    return "CUSTOM SYSTEM IV"
                if self.filename[8:-4] == "Custom System V":
                    sysNum = 5
                    return "CUSTOM SYSTEM V"
                if self.filename[8:-4] == "Custom System VI":
                    sysNum = 6
                    return "CUSTOM SYSTEM VI"

            # If the user right clicks, the program checks if the mouse was hovered over an icon while right clicking
            # This is so if the user chooses to delete the system, the correct one is removed
            if rightClick:
                sysSelected = False
                if self.filename[8:-4] == "Custom System I":
                    sysSelected = "CUSTOM SYSTEM I"
                elif self.filename[8:-4] == "Custom System II":
                    sysSelected = "CUSTOM SYSTEM II"
                elif self.filename[8:-4] == "Custom System III":
                    sysSelected = "CUSTOM SYSTEM III"
                elif self.filename[8:-4] == "Custom System IV":
                    sysSelected = "CUSTOM SYSTEM IV"
                elif self.filename[8:-4] == "Custom System V":
                    sysSelected = "CUSTOM SYSTEM V"
                elif self.filename[8:-4] == "Custom System VI":
                    sysSelected = "CUSTOM SYSTEM VI"

        return "MENU"

""" FUNCTIONS """

# This function is called when the user clicks on a planet to display the information
def DisplayInfo():
    # Global variables are retrieved from outer scope to use inside function
    global currentMin
    global currentMax
    global selected

    textFont = pygame.font.SysFont("Arial Black", 15)

    # If the minimum and maximum max values aren't what they should be, the program changes them to be correct
    if currentMin != minMass and currentMax != maxMass:
        MassSlideChange(minMass, maxMass)

    currentMin = minMass
    currentMax = maxMass

    # The information is formulated then blitted to the screen in position
    planetText = textFont.render(file[21:-4], 1, WHITE)
    screen.blit(planetText, (10, size[1] - 240))

    massText = textFont.render("Mass: " + str(masses[listNum]) + " kg", 1, WHITE)
    screen.blit(massText, (10, size[1] - 210))

    velText = textFont.render("Vel: " + str(OrbitVel(masses[0], orbitRad)) + " m/s", 1, WHITE)
    screen.blit(velText, (10, size[1] - 190))

    forceText = textFont.render("Force: %.5e " % NewtonGrav(masses[0], masses[listNum], orbitRad) + " N", 1, WHITE)
    screen.blit(forceText, (10, size[1] - 170))

    centAccText = 0
    angText = 0

    for i in range(len(bodies) - 1):
        if bodies[i] == selected:
            x = defVel[i]
            if x == 0:
                x = 0.0000000000000001
            angVelText = textFont.render("Ang Vel: %.5f " % AngularVel(framesPerRev[i], float(nowVel[i]) / float(x)) + "rad/s", 1, WHITE)
            centAccText = textFont.render("C.Acc: %.5e" % CentAccel(AngularVel(framesPerRev[i], float(nowVel[i]) / float(x)), radii[i]) + " ms^-2", 1, WHITE)
            angText = textFont.render("Angle: %.5f " % math.degrees(angles[i-1]) + " deg", 1, WHITE)

    if centAccText:
        screen.blit(centAccText, (10, size[1] - 150))
        screen.blit(angText, (10, size[1] - 130))
        screen.blit(angVelText, (10, size[1] - 110))

    # This checks if the user has selected a body, and if so then it draws a circle around the body
    # This makes it easier visually to the user, so they know which body is selected
    if selected != "":
        pygame.draw.circle(screen, WHITE, selected.rect.center, selected.radius+2, 2)

    massSlide.draw()

# This function determines how much to increase the angle of the orbit for each planet per frame
def FrameInc():
    # Before starting the calculations, the program calls on a separate function
    # CalcFramesPerRev calculates how many frames it takes for 1 revolution for every planet
    CalcFramesPerRev()
    # Each body in the list is checked
    for i in range(len(bodies) - 1):
        # If the defVel variable is 0, it means there is no body in that position of the list
        # If the variable value isn't 0, there is a body so the calculations are performed
        if defVel[i] != 0:
            # Try/except statement is used as validation
            try:
                # The angle to increase by per frame is the value returned by the AngularVel function
                # Which calculates the angular velocity
                incPerFrame[i] = AngularVel(framesPerRev[i], float(nowVel[i]) / float(defVel[i]))
            except ZeroDivisionError:
                # If there is an error where there is a zero division then an arbitrary value is used
                # This is to not crash the program
                #print "ZeroDivisonError"
                incPerFrame[i] = ((float(2*math.pi) / 10000) * (float(nowVel[i]) / float(defVel[i])))

# This function applies newton's law of universal gravitation to work out the force between the two bodies
def NewtonGrav(mA, mB, r):
    if r == 0:
        # If the radius between the two objects is 0 i.e if it's working out the force between the same object
        # Returns 0 as to avoid a DivisionByZero error
        # The closer the two objects are (sun + planet or planet + moon) the larger the force
        return 0
    return G * ((mA * mB) / (r ** 2))

# This function uses the orbital velocity equation to work out the velocity of a body in orbit
def OrbitVel(M, r):
    if r == 0:
        # If the radius between the two objects is 0 i.e if it's the same object
        # Returns 0 as to avoid a DivisionByZero error
        # There is no orbital velocity because the body doesn't orbit itself
        return 0
    return int(math.sqrt((G * M) / r))

# This function uses the time taken per revolution to work out the angular velocity
# Multiplies by the ratio of default velocity and current velocity as a multiplier
def AngularVel(frames, ratio):
    if frames != 0:
        return (float(2 * math.pi) / frames) * ratio
    return 0

# This function takes the distance between the two objects and the angular velocity to work out centripetal acceleration
def CentAccel(w, r):
    return r * (w**2)

# This function calculates the frames required per revolution (full orbit) for each body
def CalcFramesPerRev():
    # The list framesPerRev is retrieved from outer scope to be used in formula
    global framesPerRev
    # The framesPerRev list is emptied to make the calculations for each body again in case of a change
    framesPerRev = []
    for i in range(len(bodies) - 1):
        # For each body, the formula is used to calculate the number of frames per revolution
        framesPerRev.append(EARTHDAYS[i] * framesPerDay)

# This function saves all necessary variables/lists to be retrieved from a .ids file when loaded by the user
def Save():
    global clickOnL
    # These variables are to detect whether the user has picked a slot or clicked the back button
    saveChosen = False
    saveBackClick = False
    # As long as the user hasn't picked which slot to save in, this will loop until either the user has chosen a slot
    # Or if the user clicks the back button
    while not saveChosen:
        # The 3 save slot buttons are drawn each frame along with the back button
        save1.draw()
        save2.draw()
        save3.draw()
        saveBack.draw()
        if pygame.mouse.get_pressed()[0] == 1:
            clickOnL = True
        if pygame.mouse.get_pressed()[0] == 0 and clickOnL == True:
            # After the user has clicked fully (so pressed down then released) each button is checked to see if the mouse is above them
            # If so, the relevant file is opened and the saveChosen variable is changed to True
            # To exit the loop and save the information to .ids file
            if save1.checkMouse(mousePos):
                file = open("Save Files\Slot1.ids", "w")
                saveChosen = True
            if save2.checkMouse(mousePos):
                file = open("Save Files\Slot2.ids", "w")
                saveChosen = True
            if save3.checkMouse(mousePos):
                file = open("Save Files\Slot3.ids", "w")
                saveChosen = True
            if saveBack.checkMouse(mousePos):
                # If the back button is pressed then both variables are changed to True
                # Exits loop and the slots available disappear off the screen
                saveChosen = True
                saveBackClick = True

    # After the loop is ended (user has chosen a slot or pressed the back button) this if statement executed
    # If the user hasn't pressed the back button (i.e they have chosen a slot) this is executed
    if not saveBackClick:
        # All the values for mass/radius/angle/default velocity/current velocity/increase per frame are all saved
        for mass in masses:
            file.write("%.20f" %mass + "\n")
        for radius in radii:
            file.write(str(radius) + "\n")
        for angle in angles:
            file.write(str(angle) + "\n")
        for vel in defVel:
            file.write(str(vel) + "\n")
        for now in nowVel:
            file.write(str(now) + "\n")
        for inc in incPerFrame:
            file.write(str(inc) + "\n")

def Load():
    # Same as Save function, the exact same principle is applied
    # Only difference is a different menu
    global clickOnL
    loadChosen = False
    loadBackClick = False
    while not loadChosen:
        load1.draw()
        load2.draw()
        load3.draw()
        loadBack.draw()
        if pygame.mouse.get_pressed()[0] == 1:
            clickOnL = True
        if pygame.mouse.get_pressed()[0] == 0 and clickOnL == True:
            if load1.checkMouse(mousePos):
                file = open("Save Files\Slot1.ids", "r")
                loadChosen = True
            if load2.checkMouse(mousePos):
                file = open("Save Files\Slot2.ids", "r")
                loadChosen = True
            if load3.checkMouse(mousePos):
                file = open("Save Files\Slot3.ids", "r")
                loadChosen = True
            if loadBack.checkMouse(mousePos):
                loadChosen = True
                loadBackClick = True

    if not loadBackClick:
        # Same logic applied as Save function
        # The relevant lists are updated by reading from text file in the same order the lists were saved
        for x in range(len(masses)):
            masses[x] = float(file.readline())
        for y in range(len(radii)):
            radii[y] = float(file.readline())
        for z in range(len(angles)):
            angles[z] = float(file.readline())
        for a in range(len(defVel)):
            defVel[a] = float(file.readline())
        for b in range(len(nowVel)):
            nowVel[b] = float(file.readline())
        for c in range(len(incPerFrame)):
            incPerFrame[c] = float(file.readline())
        for i in range(len(bodies) - 10):
            # All the bodies after the default ones are run through and checked to see if one exists in its place
            # If so, an object is created in the list and added to it
            if radii[i + 10] != 0:
                bodies[i + 10] = Body("Systems\Custom\Default.png", radii[i+10], 9, masses[i+10], 1, 1e22, 1e25, system)


# This function is for the slider which changes the mass of the selected body
def MassSlideChange(min, max):
    # The massSlide variable is retrieved from outer scope
    global massSlide
    # The massSlide variable is updated with the new minimum and maximum values
    massSlide = AstroUtil.Slider(screen, 260, size[1] - 210, 200, 30, WHITE, GREY, 270, size[1] - 215, 20, 40, RED, DARKRED, min, max)

# This function is called to display the buttons relating to the systems (add system, delete system...)
# The x and y position of the mouse taken as parameters to determine the position of the drop down menu
def SystemButtons(mouseX, mouseY):
    # The buttons are displayed just below the mouse
    addSystem = AstroUtil.Button(screen, mouseX, mouseY, 110, 30, BLACK, "Add System", mouseX + 3, mouseY + 1, WHITE, WHITE, 2)
    delSystem = AstroUtil.Button(screen, mouseX, mouseY + 30, 110, 30, BLACK, "Del System", mouseX + 3, mouseY + 31, WHITE, WHITE, 2)

    # Buttons are returned as values to where they were called from
    return addSystem, delSystem

# This function is exactly the same as SystemButtons function, just displays drop down menu for bodies
def BodyButtons(mouseX, mouseY):
    addBody = AstroUtil.Button(screen, mouseX, mouseY, 110, 30, BLACK, "Add Body", mouseX + 3, mouseY + 1, WHITE, WHITE, 2)
    delBody = AstroUtil.Button(screen, mouseX, mouseY + 30, 110, 30, BLACK, "Del Body", mouseX + 3, mouseY + 31, WHITE, WHITE, 2)
    zoomIn = AstroUtil.Button(screen, mouseX, mouseY + 60, 110, 30, BLACK, "Zoom In", mouseX + 3, mouseY + 61, WHITE, WHITE, 2)

    return addBody, delBody, zoomIn

# This function takes in the position of the body as a parameter
def GetOrbitRad(bodPos):
    # This simply takes the position of the body relative to the centre (position of body it's orbiting)
    # This returns the orbit radius
    return int(math.sqrt(((bodPos[0] - (size[0]/2))**2) + ((bodPos[1] - (size[1]/2))**2)))

# The mass of each body is stored in this list, and can be changed
masses = [1.989e30, 3.285e23, 4.867e24, 5.972e24, 6.39e23, 1.898e27, 5.683e26, 8.681e25, 1.024e26, 1.309e22]

# This list will hold the orbit radii of the bodies
radii = [0, 108, 158, 199, 220, 300, 400, 500, 550, 650]

# Initialising all the default planets
sun = Body("Systems\Solar System\Sun.png", radii[0], 90, masses[0], 0, 1e28, 1e32, "SOLAR SYSTEM")
mercury = Body("Systems\Solar System\Mercury.png", radii[1], 3, masses[1], 1, 1e21, 1e24, "SOLAR SYSTEM")
venus = Body("Systems\Solar System\Venus.png", radii[2], 6, masses[2], 2, 1e22, 1e25, "SOLAR SYSTEM")
earth = Body("Systems\Solar System\Earth.png", radii[3], 6, masses[3], 3, 1e22, 1e25, "SOLAR SYSTEM")
mars = Body("Systems\Solar System\Mars.png", radii[4], 3, masses[4], 4, 1e21, 1e24, "SOLAR SYSTEM")
jupiter = Body("Systems\Solar System\Jupiter.png", radii[5], 35, masses[5], 5, 1e25, 1e28, "SOLAR SYSTEM")
saturn = Body("Systems\Solar System\Saturn.png", radii[6], 29, masses[6], 6, 1e24, 1e27, "SOLAR SYSTEM")
uranus = Body("Systems\Solar System\Uranus.png", radii[7], 12, masses[7], 7, 1e23, 1e26, "SOLAR SYSTEM")
neptune = Body("Systems\Solar System\Neptune.png", radii[8], 12, masses[8], 8, 1e24, 1e27, "SOLAR SYSTEM")
pluto = Body("Systems\Solar System\Pluto.png", radii[9], 3, masses[9], 9, 1e20, 1e24, "SOLAR SYSTEM")

# Setting the framerate to 60
FPS = 60

# This is the group that all The Solar System sprites go into
solarSystemSprites = pygame.sprite.Group()
centre = pygame.sprite.Group()

# The angle of each body relative to the body in the middle is stored in this list
angles = [0, 0, 0, 0, 0, 0, 0, 0, 0]

# All the bodies are stored in this list, the first 10 are in by default
bodies = [sun, mercury, venus, earth, mars, jupiter, saturn, uranus, neptune, pluto]

# The increase of angle per frame for each body will be stored in this list
incPerFrame = []

# This loop calculates the default values for the bodies
# And allows up to 350 total bodies (50 bodies per system max)
# This serves as validation to not slow down the program
for i in range(350):
    if i < 9:
        defVel.append(OrbitVel(masses[0], radii[i+1]))
    else:
        bodies.append(0)
        defVel.append(0)
        masses.append(0)
        radii.append(0)
        INITIALEARTHDAYS.append(0)
        EARTHDAYS.append(0)
        angles.append(0)
    incPerFrame.append(0)

# By default, the selected body is the sun, meaning the sun's information will be displayed in the info box
selected = sun

# This is the group for all the system icons to be displayed in the menu
systemIcons = pygame.sprite.Group()

# The icon for the default solar system is created here
solarSystem = SystemIcon("Systems\Solar System.png", size[0] / 8 * 6, size[1] / 10, 50)

# All the custom system variables are set to 0 by default and stored in a list
# The variables then change when accessed via the list and used where appropriate
sysI = 0
sysII = 0
sysIII = 0
sysIV = 0
sysV = 0
sysVI = 0
systems = [sysI, sysII, sysIII, sysIV, sysV, sysVI]

# The default solar system icon is added to the icons group
systemIcons.add(solarSystem)

# These are the variables for the speed buttons which change playback speed
speed = AstroUtil.Button(screen, 3, 3, 65, 30, BLACK, "Speed: ", 6, 6, WHITE, WHITE, 3)
normal = AstroUtil.Button(screen, 73, 3, 30, 30, BLACK, "1x", 76, 6, WHITE, WHITE, 3)
twice = AstroUtil.Button(screen, 108, 3, 30, 30, BLACK, "2x", 111, 6, WHITE, WHITE, 3)
four = AstroUtil.Button(screen, 143, 3, 30, 30, BLACK, "4x", 146, 6, WHITE, WHITE, 3)
eight = AstroUtil.Button(screen, 178, 3, 30, 30, BLACK, "8x", 181, 6, WHITE, WHITE, 3)
sixteen = AstroUtil.Button(screen, 213, 3, 38, 30, BLACK, "16x", 216, 6, WHITE, WHITE, 3)
thirtyTwo = AstroUtil.Button(screen, 256, 3, 38, 30, BLACK, "32x", 259, 6, WHITE, WHITE, 3)
sixtyFour = AstroUtil.Button(screen, 299, 3, 38, 30, BLACK, "64x", 302, 6, WHITE, WHITE, 3)

# This list stores all the variables for the speed buttons to be drawn on screen
speedButtons = [normal, twice, four, eight, sixteen, thirtyTwo, sixtyFour]
# The default bodies in the solar system are added to the group before the program begins
solarSystemSprites.add(mercury, venus, earth, mars, jupiter, saturn, uranus, neptune, pluto)

# The rest of the buttons which are displayed on screen are initialised here
saveBut = AstroUtil.Button(screen, 3, 50, 100, 25, RED, "Save", 5, 50, WHITE, WHITE, 3)
loadBut = AstroUtil.Button(screen, 3, 100, 100, 25, RED, "Load", 5, 100, WHITE, WHITE, 3)
menuBut = AstroUtil.Button(screen, 3, 150, 100, 25, RED, "Menu", 5, 150, WHITE, WHITE, 3)
toggleOrbitBut = AstroUtil.Button(screen, 3, 200, 160, 25, RED, "Toggle Orbit Lines", 5, 200, WHITE, WHITE, 3)
exitBut = AstroUtil.Button(screen, size[0] - 24, 2, 22, 22, RED, "X", size[0] - 20, 2, WHITE, LIGHTGREY, 2)
# These are the save slot buttons
save1 = AstroUtil.Button(screen, 110, 50, 100, 25, BLACK, "SLOT 1", 130, 51, WHITE, WHITE, 3)
save2 = AstroUtil.Button(screen, 220, 50, 100, 25, BLACK, "SLOT 2", 240, 51, WHITE, WHITE, 3)
save3 = AstroUtil.Button(screen, 330, 50, 100, 25, BLACK, "SLOT 3", 350, 51, WHITE, WHITE, 3)
saveBack = AstroUtil.Button(screen, 440, 50, 20, 25, BLACK, "<", 444, 51, WHITE, WHITE, 3)
# These are the load slot buttons
load1 = AstroUtil.Button(screen, 110, 100, 100, 25, BLACK, "SLOT 1", 130, 101, WHITE, WHITE, 3)
load2 = AstroUtil.Button(screen, 220, 100, 100, 25, BLACK, "SLOT 2", 240, 101, WHITE, WHITE, 3)
load3 = AstroUtil.Button(screen, 330, 100, 100, 25, BLACK, "SLOT 3", 350, 101, WHITE, WHITE, 3)
loadBack = AstroUtil.Button(screen, 440, 100, 20, 25, BLACK, "<", 444, 101, WHITE, WHITE, 3)

# The orbit radius slider is initialised here
# Minimum orbit radius is 100 and maximum is 700
# Stops any bodies being too close to the sun or off the screen
radiusSlide = AstroUtil.Slider(screen, 260, size[1] - 120, 200, 30, WHITE, GREY, 270, size[1] - 125, 20, 40, RED, DARKRED, 100, 700)

# The body in the centre by default for any system is the sun
centre.add(sun)

# This is the mainloop, everything in the loop is executed each frame
while True:
    # The variable mousePos is set to the position of the mouse on the screen
    mousePos = pygame.mouse.get_pos()
    # This will create a rect around the mouse so collisions with sprites could be detected
    mouseRect = pygame.Rect(mousePos[0], mousePos[1], 10, 10)

    # This will check for any events happening, such as mouse clicks
    for event in pygame.event.get():
        # If the user has clicked the left mouse button, clickOnL is set to true
        if pygame.mouse.get_pressed()[0] == 1:
            clickOnL = True
        # The next instructions are executed if clickOnL is true (user has pressed down on the mouse) and then released
        if pygame.mouse.get_pressed()[0] == 0 and clickOnL == True:
            # The program checks if the user released the mouse button on the exit button
            exBut = exitBut.checkMouse(mousePos)
            # The program halts if the user has pressed on the exit button
            if exBut:
                sys.exit()

            # The program checks each speed button to see if the user has pressed on any of them
            for i in range(len(speedButtons)):
                speedBut = speedButtons[i].checkMouse(mousePos)
                if speedBut:
                    # If the user has pressed on a speed button, the framesPerDay variable is reset
                    # Then the playback speed is changed depending on which speed button has been pressed
                    framesPerDay = 6
                    framesPerDay /= float(2**i)

    # Before anything else is displayed, the screen is filled with a black background
    screen.fill(BLACK)

    """ MENU """

    # If the user is in the main menu, then everything under this if statement is executed per frame
    if system == "MENU":
        # The background of the menu is an image of the milkyway
        bg = Background("Backgrounds\Milkyway.png")
        screen.blit(bg.image, bg.rect)

        # If the user has clicked the right mouse button, clickOnR is set to true
        if pygame.mouse.get_pressed()[2] == 1:
            clickOnR = True
        # This set of instructions is executed after the user releases the right mouse button
        if pygame.mouse.get_pressed()[2] == 0 and clickOnR == True:
            # The add/delete system buttons are initialised to appear using the SystemButtons function
            addSystem, delSystem = SystemButtons(mousePos[0], mousePos[1])
            # The program runs through every icon in the systemIcons list and called the checkCollid function
            # Which checks which icon was "right clicked" on, so any actions (deleting the system) are acted on it
            for ic in systemIcons:
                ic.checkCollide(mousePos, True)
            # The sysButs is true, meaning the buttons can appear
            # clickOnR is false to indicate the user isn't holding on the mouse button
            sysButs = True
            clickOnR = False

        # If the sysButs variable is true, the following will executed
        # It displays the relevant buttons and allows them to be used
        if sysButs:
            # the add/delete system buttons are displayed
            addSystem.draw()
            delSystem.draw()
            # If the user has clicked the left mouse button, clickOnL is set to true
            if pygame.mouse.get_pressed()[0]:
                clickOnL = True
            # This set of instructions is executed after the user releases the left mouse button
            if pygame.mouse.get_pressed()[0] == 0 and clickOnL == True:
                # The program calls the checkMouse function on the addSystem variable, with current mouse position as parameter
                # If the function returns true (i.e the user has pressed on the "add system" button, the next instruction set is executed
                if addSystem.checkMouse(mousePos):
                    # Every item in the systems list is checked to see if it's empty
                    # If it's empty, then a new system is added to it
                    for x in range(len(systems)):
                        if systems[x] == 0:
                            if x == 0:
                                systems[x] = SystemIcon("Systems\Custom System I.png", mousePos[0], mousePos[1], 50)
                            elif x == 1:
                                systems[x] = SystemIcon("Systems\Custom System II.png", mousePos[0], mousePos[1], 50)
                            elif x == 2:
                                systems[x] = SystemIcon("Systems\Custom System III.png", mousePos[0], mousePos[1], 50)
                            elif x == 3:
                                systems[x] = SystemIcon("Systems\Custom System IV.png", mousePos[0], mousePos[1], 50)
                            elif x == 4:
                                systems[x] = SystemIcon("Systems\Custom System V.png", mousePos[0], mousePos[1], 50)
                            else:
                                systems[x] = SystemIcon("Systems\Custom System VI.png", mousePos[0], mousePos[1], 50)

                            systemIcons.add(systems[x])
                            sysButs = False
                            break
                # The program calls the checkMouse function on the delSystem variable, with current mouse position as parameter
                # If the function returns true (i.e the user has pressed on the "del system" button, the next instruction set is executed
                if delSystem.checkMouse(mousePos):
                    rem = "No"
                    if sysSelected == "CUSTOM SYSTEM I":
                        rem = 0
                    elif sysSelected == "CUSTOM SYSTEM II":
                        rem = 1
                    elif sysSelected == "CUSTOM SYSTEM III":
                        rem = 2
                    elif sysSelected == "CUSTOM SYSTEM IV":
                        rem = 3
                    elif sysSelected == "CUSTOM SYSTEM V":
                        rem = 4
                    elif sysSelected == "CUSTOM SYSTEM VI":
                        rem = 5
                    if rem != "No":
                        systemIcons.remove(systems[rem])
                        systems[rem] = 0
                    sysButs = False

                clickOnL = False

        # After all the checks are done, the system icons are drawn
        systemIcons.draw(screen)

        for x in systemIcons:
            # The program checks every icon to see if it has been pressed
            # If so, the corresponding system is loaded
            click = 0
            system = x.checkCollide(mousePos, False)
            if system != "MENU":
                file = "Systems\Solar System\Sun.png"
                orbitRad = 0
                listNum = 0
                selected = ""
                break

    """ ANY SYSTEM """

    # If the system is not the menu (i.e it's another system) the following instructions are executed each frame
    if system != "MENU" and system != "ZOOMIN":
        # This draws all the speed changing buttons
        speed.draw()
        for button in speedButtons:
            button.draw()

        # The current velocity of each planet may change by frame
        # So the nowVel list is reset and re-calculates velocity for each body each frame
        nowVel = []
        for i in range(len(bodies) - 1):
            # If the value inside the bodies list at the index i isn't empty
            if bodies[i] != 0:
                # The nowVel list is updated with a new calculated orbital velocity
                nowVel.append(OrbitVel(masses[0], radii[i + 1]))
            else:
                # Otherwise the list is appended with a value of 0
                nowVel.append(0)

        # The FrameInc function is called to calculate how much to increase the angle of each body by per frame
        FrameInc()

        for i in range(len(bodies) - 1):
            # If the default velocity value in the specified index i isn't empty (i.e a body exists at that index)
            if defVel[i] != 0:
                # try/except statement used to not cause the program to crash in case there is a division by zero
                try:
                    # The program calculates the total frames required for one orbit
                    totalFrames = int(((2 * math.pi) / float(incPerFrame[i])) * (float(nowVel[i]) / float(defVel[i])))
                except ZeroDivisionError:
                    totalFrames = int(((2 * math.pi) / 0.5 * (float(nowVel[i]) / float(defVel[i]))))
                # The number of earth days this requires for the body is calculated
                EARTHDAYS[i] = totalFrames / framesPerDay

        # The save/load/menu buttons are drawn to the screen
        saveBut.draw()
        loadBut.draw()
        menuBut.draw()
        toggleOrbitBut.draw()

        if pygame.mouse.get_pressed()[0] == 1:
            clickOnL = True
        if pygame.mouse.get_pressed()[2] == 1:
            clickOnR = True
        if pygame.mouse.get_pressed()[2] == 0 and clickOnR == True:
            # The add/delete body buttons are initialised to appear using the BodyButtons function
            addBod, delBod, zoomIn = BodyButtons(mousePos[0], mousePos[1])
            for body in bodies:
                if body != 0:
                    body.CheckCollide(mousePos, True)
            bodButs = True
            clickOnR = False

        if nextFZoom:
            system = "ZOOMIN"
            centre.empty()
            centre.add(nextFZoom)
            onNextF = False

        # If the bodButs variable is true, the following will executed
        # It displays the relevant buttons and allows them to be used
        if bodButs:
            # The add/delete body buttons are displayed
            addBod.draw()
            delBod.draw()
            zoomIn.draw()
            # If the user has released the left mouse button the following is executed
            if pygame.mouse.get_pressed()[0] == 0 and clickOnL == True:
                # If the checkMouse function for the addBod variable returns true, the following executes
                if addBod.checkMouse(mousePos):
                    # This statement is a validation check to make sure the body doesn't spawn inside the sun
                    if GetOrbitRad(mousePos) > (sun.radius + 10):
                        doneAppend = False
                        for i in range(50):
                            # The next available slot is found and the relevant variables are appended
                            # Mass, orbit radius, default velocity, angle per frame...
                            if bodies[(sysNum * 50) + i + 1] == 0 and not doneAppend:
                                bodies[(sysNum * 50) + i + 1] = Body("Systems\Custom\Default.png", GetOrbitRad(mousePos), 9, 1e24, 1, 1e22, 1e25, system)
                                masses[(sysNum * 50) + i + 1] = 5.972e24
                                radii[(sysNum * 50) + i + 1] = GetOrbitRad(mousePos)
                                defVel[(sysNum * 50) + i] = OrbitVel(masses[0], radii[(sysNum * 50) + i + 1])
                                incPerFrame[(sysNum * 50) + i + 1] = 0.0016666667
                                doneAppend = True

                # If the del body button is pressed, the body is removed
                # By removing the values in the relevant lists
                elif delBod.checkMouse(mousePos):
                    # Every body is checked
                    for i in range(len(bodies) - 1):
                        if bodies[i] != 0 and bodies[i].SYS == system and bodies[i] == bodSelected:
                            # If all the criteria are met
                            # (A body exists in the index, it's in the correct system and is the one selected)
                            # All the lists access the index of the body and put in a value of 0
                            bodies[i] = masses[i] = radii[i] = defVel[i] = incPerFrame[i+1] = 0

                # If the zoom in button is pressed
                # The orbit radius of the body is set to 0 (so it's in the centre)
                elif zoomIn.checkMouse(mousePos):
                    for i in range(len(bodies) - 1):
                        if bodies[i] != 0 and bodies[i].SYS == system and bodies[i] == bodSelected:
                            bodies[i].orbit = radii[i] = 0
                            nextFZoom = bodies[i]
                bodButs = False

        # If the user presses the left mouse button
        if pygame.mouse.get_pressed()[0] == 0 and clickOnL == True:
            if menuBut.checkMouse(mousePos):
                # Goes back to the main menu by changing the system variable
                system = "MENU"
            if toggleOrbitBut.checkMouse(mousePos):
                orbLines = not orbLines
            if saveBut.checkMouse(mousePos):
                # Saves required variables/lists
                saveThread = threading.Thread(target = Save)
                saveThread.start()
            if loadBut.checkMouse(mousePos):
                # Loads the variables/lists by getting the values and changing default variables
                loadThread = threading.Thread(target = Load)
                loadThread.start()
            clickOnL = False

        # The centre object is drawn to the centre of the screen
        centre.draw(screen)

        # This will check if the mouse is over one of the planets, and display appropriate information
        for i in range(len(bodies)):
            if bodies[i] != 0:
                bodies[i].planetInfo()

        # The solarSystemSprites group is emptied to check which bodies to add to it
        solarSystemSprites.empty()
        for i in range(len(bodies) - 1):
            # The program runs through each body and checks if it's empty and if it's in the correct system
            if bodies[i+1] != 0 and bodies[i+1].SYS == system:
                # If it's not empty and is in the correct system then the body is appended to the group
                solarSystemSprites.add(bodies[i+1])
                # If the orbit radius is larger than 1 (i.e it's not the centre body)
                if int(radii[i+1]) > 1 and orbLines == True:
                    # A circle is drawn at the orbit radius to show the path the body will follow
                    pygame.draw.circle(screen, WHITE, (size[0] / 2, size[1] / 2), int(radii[i+1]), 1)
                try:
                    # The orbitSun function is called to make various calculations
                    bodies[i+1].orbitSun(angles[i])
                    angles[i] += incPerFrame[i]
                    angles[i] %= (2*math.pi)
                except IndexError:
                    print "Error at " + str(i+1)

        # The bodies in the solarSystemSprites group are drawn to the screen
        solarSystemSprites.draw(screen)

        # Draws the box in the corner which will hold the information
        outlineInfoBox = pygame.Rect(0, size[1] - 250, 250, 250)
        infoBox = pygame.Rect(5, size[1] - 245, 240, 240)

        variableChangeOutline = pygame.Rect(250, size[1] - 250, 250, 250)
        variableChangeBox = pygame.Rect(255, size[1] - 245, 240, 240)

        pygame.draw.rect(screen, WHITE, outlineInfoBox)
        pygame.draw.rect(screen, BLACK, infoBox)

        pygame.draw.rect(screen, WHITE, variableChangeOutline)
        pygame.draw.rect(screen, BLACK, variableChangeBox)

        textFont = pygame.font.SysFont("Arial Black", 15)

        # The mass/orbit radius sliders are initalised here
        massSlideText = textFont.render("Mass", 1, WHITE)
        screen.blit(massSlideText, (265, size[1] - 240))

        radiusSlideText = textFont.render("Orbit Radius", 1, WHITE)
        screen.blit(radiusSlideText, (265, size[1] - 150))

        radiusSlide.draw()

        # Calls the function which draws the information to the screen
        DisplayInfo()

        # If the user is holding down the left mouse button
        if pygame.mouse.get_pressed()[0] == 1:
            # If the checkMouse function returns true (i.e the user is holding down the mouse on the slider)
            if massSlide.checkMouse(mousePos, framesPerDay):
                # The mass of the body selected is changed relative to where the mouse is on the slider
                masses[listNum] = massSlide.checkMouse(mousePos, framesPerDay)
            # If the checkMouse function returns true (i.e the user is holding down the mouse on the slider)
            if radiusSlide.checkMouse(mousePos, framesPerDay):
                # This if statement serves as a validation
                # If the listNum isn't 0 (i.e the sun isn't the body selected) the instructions are executed
                # The orbit radius of the sun is always 0
                if listNum != 0:
                    # The orbit radius of the body is changed relative to where the mouse is on the slider
                    radii[listNum] = int(radiusSlide.checkMouse(mousePos, framesPerDay))
                    bodies[listNum].orbit = radii[listNum]

    """ A ZOOMED IN PLANET TO VIEW MOONS """
    if system == "ZOOMIN":
        centre.draw(screen)

    # The "x" button in the top right of the screen is drawn
    exitBut.draw()

    # The display is updated at the end of the frame
    pygame.display.flip()
    # This makes sure that it's accurate, exactly 60 FPS
    clock.tick_busy_loop(FPS)
