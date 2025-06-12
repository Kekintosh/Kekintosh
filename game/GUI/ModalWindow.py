import pygame
from OpenGL.GL import *
from functions import checkHover



class ModalWindow:
    def __init__(self, gl):
        self.gl = gl
        self.cellPositions = {}
        self.updateFunctions = []
        self.clickEvent = None
        self.lastClickCall = []
        self.burning = False
        self.clickWait = 1
        self.windowId = 0
        self.window = None

    def setWindow(self, win):
        self.window = win

    def destroyWindow(self):
        self.gl.allowEvents["keyboardAndMouse"] = True
        self.gl.allowEvents["grabMouse"] = True
        self.gl.allowEvents["movePlayer"] = True
        self.gl.allowEvents["showCrosshair"] = True

        self.gl.updateEvents.pop(self.windowId)

    def drawWindow(self):
        self.clickWait += 1
        if self.clickWait == 25:
            self.clickWait = 1
            self.lastClickCall = []

        self.gl.allowEvents["keyboardAndMouse"] = False
        self.gl.allowEvents["grabMouse"] = False
        self.gl.allowEvents["movePlayer"] = False
        self.gl.allowEvents["showCrosshair"] = False

        win = self.window
        win.blit(self.gl.WIDTH // 2 - (win.width // 2), self.gl.HEIGHT // 2 - (win.height // 2))

        mp = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed(3)

        hover = self.gl.gui.GUI_TEXTURES["selected"]
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        for i in self.cellPositions.items():
            w, h = 32, 32
            if len(i[1][0]) > 2:
                w, h = i[1][0][2], i[1][0][3]
            x, y, block = i[1][0][0], i[1][0][1], i[1][1]
            x += self.gl.WIDTH // 2 - (win.width // 2)
            y += self.gl.HEIGHT // 2 - (win.height // 2)
            if checkHover(x, y, w, h, mp[0], mp[1]):
                if click[0] or click[1] or click[2]:
                    if self.clickEvent and self.lastClickCall != [click, i[0]]:
                        self.clickEvent(click, i[0])
                        self.lastClickCall = [click, i[0]]
                hover.width = w
                hover.height = h
                hover.blit(x, self.gl.HEIGHT - y - h)

        for i in self.updateFunctions:
            i(win, mp)

        key = pygame.key.get_pressed()
        if key[pygame.K_ESCAPE]:
            self.destroyWindow()
            if len(self.gl.updateEvents) > self.windowId:
               self.gl.updateEvents.pop(self.windowId)
            return

    def show(self):
        self.gl.updateEvents.append(self.drawWindow)
        self.windowId = len(self.gl.updateEvents) - 1
class litFurnaceWindow():
    def __init__(self, gl):
        self.gl = gl
        self.windowId = 1
        
        self.window = None
    def setWindow(self, win):
        self.window = win
    #def destroyWindow(self):
        #self.gl.allowEvents["keyboardAndMouse"] = True
        #self.gl.allowEvents["grabMouse"] = True
        #self.gl.allowEvents["movePlayer"] = True
        #self.gl.allowEvents["showCrosshair"] = True

        #self.gl.updateEvents.pop(self.windowId)
    def drawWindow(self):
        self.burning = True
        self.gl.allowEvents["keyboardAndMouse"] = False
        self.gl.allowEvents["grabMouse"] = False
        self.gl.allowEvents["movePlayer"] = False
        self.gl.allowEvents["showCrosshair"] = False
        win = self.window
        if not hasattr(self, 'original_height'):
            self.original_height = win.height
            self.window_start_time = pygame.time.get_ticks()

        # Calculate time-based height reduction
        current_time = pygame.time.get_ticks()
        elapsed_seconds = (current_time - self.window_start_time) / 1000.0
        shrink_speed = 0.35  # pixels per second
        height_reduction = int(elapsed_seconds * shrink_speed)

        # Calculate new height - don't modify win.height directly
        new_height = max(1, self.original_height - height_reduction)
        original_y = 720 // 2 - self.original_height // 2
        
        # Temporarily modify height for rendering
        temp_height = win.height
        win.height = new_height
        win.blit(830 // 2 - win.width // 2, original_y)
        win.height = temp_height  # Restore immediately after blit
        
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    

    def show(self):
        self.gl.updateEvents.append(self.drawWindow)
        self.windowId = len(self.gl.updateEvents) - 1