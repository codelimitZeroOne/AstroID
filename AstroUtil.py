import pygame

# This class defines a generic slider which could be used to change many values
class Slider:
    def __init__(self, screen, limiterX, limiterY, limiterWidth, limiterHeight, limiterColour, limiterHighlighted, sliderX, sliderY, sliderWidth, sliderHeight, sliderColour, sliderHighligted, minVal, maxVal):
        self.screen = screen
        self.limiterX = limiterX
        self.limiterY = limiterY
        self.limiterWidth = limiterWidth
        self.limiterHeight = limiterHeight
        self.limiterColour = limiterColour
        self.limiterHighlighted = limiterHighlighted
        self.sliderX = sliderX
        self.sliderY = sliderY
        self.sliderWidth = sliderWidth
        self.sliderHeight = sliderHeight
        self.sliderColour = sliderColour
        self.sliderHighlighted = sliderHighligted
        self.minVal = minVal
        self.maxVal = maxVal
        self.limiterRect = pygame.Rect(self.limiterX, self.limiterY, self.limiterWidth, self.limiterHeight)
        self.sliderRect = pygame.Rect(self.sliderX, self.sliderY, self.sliderWidth, self.sliderHeight)

    # This function draws the actual slider and the limiter
    def draw(self):
        pygame.draw.rect(self.screen, self.limiterColour, self.limiterRect)
        pygame.draw.rect(self.screen, self.sliderColour, self.sliderRect)

    # This function checks the position of the mouse to see if it's within the slider so it could be moved
    def checkMouse(self, mousePos, framesPerDay):
        # Checks if the mouse is within the x boundaries
        if mousePos[0] > self.limiterX and mousePos[0] < (self.limiterX + self.limiterWidth):
            # Checks if the mouse is within the y boundaries
            if mousePos[1] > self.limiterY and mousePos[1] < (self.limiterY + self.limiterHeight):
                # Moves the position of the slider to the position of the mouse
                self.sliderRect.x = mousePos[0]
                out = self.minVal + ((self.maxVal - self.minVal) * (float((mousePos[0] - self.limiterX)) / float(self.limiterWidth)))
                return out
        return False

# This is a class for any generic button with text inside
class Button:
    def __init__(self, screen, posX, posY, width, height, boxColour, text, textX, textY, textColour, outlineColour, thickness):
        textFont = pygame.font.SysFont("Arial Black", 15)
        self.screen = screen
        self.posX = posX
        self.posY = posY
        self.width = width
        self.height = height
        self.boxColour = boxColour
        self.text = text
        self.textX = textX
        self.textY = textY
        self.textColour = textColour
        self.outlineColour = outlineColour
        self.thickness = thickness
        self.boxRect = pygame.Rect(self.posX, self.posY, self.width, self.height)
        self.outlineRect = pygame.Rect(self.posX - self.thickness, self.posY - self.thickness, self.width + (self.thickness * 2), self.height + (self.thickness * 2))
        self.textRender = textFont.render(text, 1, textColour)

    def draw(self):
        pygame.draw.rect(self.screen, self.outlineColour, self.outlineRect)
        pygame.draw.rect(self.screen, self.boxColour, self.boxRect)
        self.screen.blit(self.textRender, (self.textX, self.textY))


    # This function is very similar to the checkMouse in the slider class, however this has a different output
    def checkMouse(self, mousePos):
        # Checks if the mouse is within the x boundaries
        if mousePos[0] > self.posX and mousePos[0] < (self.posX + self.width):
            # Checks if the mouse is within the y boundaries
            if mousePos[1] > self.posY and mousePos[1] < (self.posY + self.height):
                return True
        return False