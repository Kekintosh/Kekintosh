import math
from random import randint
import pyglet
from pyglet.gl import GL_QUADS
from pyglet.gl import *
from OpenGL.GL import *
from game.GUI.ModalWindow import ModalWindow
from game.GUI.ModalWindow import litFurnaceWindow
from settings import *
import threading
from ctypes import c_float
import time
class Inventory:
    def __init__(self, glClass):
        self.windowId = 0
        self.burning = False
        self.gl = glClass
        self.inventory = {}
        self.blocksLabel = {}
        self.activeInventory = 0
        self.heartAnimation = []
        self.draggingItem = []
        self.viewmodel = self.ViewModel(self)
        ls = list(self.gl.inventory_textures.items())
        old = False
        for i in range(10):
            old = not old
            self.heartAnimation.append([0, '-' if old else '+', randint(3, 8) / 10])
        for i in range(120):  # Increased to 54 slots to accommodate crafting table mapping
            self.inventory[i] = ["", 0]
            self.blocksLabel[i] = pyglet.text.Label("0",
                                                    font_name='Minecraft Rus',
                                                    color=(255, 255, 255, 255),
                                                    font_size=10,
                                                    x=self.gl.WIDTH // 2, y=60)
        self.inventory[0] = ["log_oak",16]
        self.inventory[2] = ["cobblestone",64]
        self.inventory[3] = ["sand",64]
        self.inventory[4] = ["crafting_table",1]
        self.inventory[5] = ["chest",1]
        self.inventory[6] = ["furnace",1]
        self.inventory[7] = ["coal_ore",10]
        self.inventory[8] = ["tnt",64]
    def initWindow(self):
        self.window = ModalWindow(self.gl)
        self.window.setWindow(self.gl.gui.GUI_TEXTURES["inventory_window"])
        self.window.clickEvent = self.windowClickEvent
        self.window.updateFunctions.append(self.updateWindow)

        x = 16
        for i in range(9):
            self.window.cellPositions[i] = [(x, 284), None]
            x += 36

        x, y = 196, 36
        self.window.cellPositions[37] = [(x, y), None]
        x += 36
        self.window.cellPositions[38] = [(x, y), None]
        x = 196
        y += 36
        self.window.cellPositions[39] = [(x, y), None]
        x += 36
        self.window.cellPositions[40] = [(x, y), None]

        self.window.cellPositions[41] = [(308, 56), None]  # TODO: crafting table in inventory

        x, y = 16, 168
        # for i in range(9 * 3, 0, -1): # original for loop?
        for i in range(9 * 3, 0, -1):   
            self.window.cellPositions[9 + i] = [(x, y), None]
            x += 36
            if x > 304:
                x = 16
                y += 36



    def initCraftingTableWindow(self):
        self.craftingWindow = ModalWindow(self.gl)
        self.craftingWindow.setWindow(self.gl.gui.GUI_TEXTURES["crafting_table"])
        self.craftingWindow.clickEvent = self.windowClickEvent
        self.craftingWindow.updateFunctions.append(self.updateCraftingWindow)

        
        self.craftingWindow.cellPositions = {
            42: [(60, 106), None], 43: [(96, 106), None], 44: [(132, 106), None],
            45: [(60, 70), None], 46: [(96, 70), None], 47: [(132, 70), None],
            48: [(60, 34), None], 49: [(96, 34), None], 50: [(132, 34), None],
            51: [(246.5, 71), None]  
        }

        
        x, y = 16, 168
        for i in range(9 * 4, 0, -1):
            if i != 9:
                self.craftingWindow.cellPositions[i] = [(x, y), None]
                x += 36
                if x > 304:
                    x = 16
                    y += 36

        
        x = 16
        for i in range(9):
            self.craftingWindow.cellPositions[i] = [(x, 284), None]
            x += 36
    def initChestWindow(self):
        self.ChestWindow = ModalWindow(self.gl)
        self.ChestWindow.setWindow(self.gl.gui.GUI_TEXTURES["chest_window"])
        self.ChestWindow.clickEvent = self.windowClickEvent
        self.ChestWindow.updateFunctions.append(self.updateChestWindow)
                # CHEST INV CELL POS
        x = 16
        y = 395
        for i in range(9):
            self.ChestWindow.cellPositions[i] = [(x, y), None]
            x += 36
            if x > 304:
                x = 16
                y -= 45
        x = 16
        y = 350
        for i in reversed(range(10,19)):
            self.ChestWindow.cellPositions[i] = [(x, y), None]
            x += 36
            if x > 304:
                x = 16
        x = 304
        y = 315
        for i in range(19,37):
            self.ChestWindow.cellPositions[i] = [(x, y), None]
            x -= 36
            if x < 16:
                x = 304
                y -= 36
        x = 304
        y = 215
        for i in range(52,107):
            self.ChestWindow.cellPositions[i] = [(x, y), None]
            x -= 36
            if x < 16:
                x = 304
                y -= 36

    def initFurnaceWindow(self):
        self.FurnaceWindow = ModalWindow(self.gl)
        self.FurnaceWindow.setWindow(self.gl.gui.GUI_TEXTURES["furnace_window"])
        self.FurnaceWindow.clickEvent = self.windowClickEvent
        self.FurnaceWindow.updateFunctions.append(self.updateFurnaceWindow)

        self.FurnaceWindow.cellPositions = {
            107: [(111, 33), None], 108: [(111, 105), None], 109: [(232.5, 70), None]
        }

        x, y = 16, 168
        for i in range(9 * 4, 0, -1):
            if i != 9:
                self.FurnaceWindow.cellPositions[i] = [(x, y), None]
                x += 36
                if x > 304:
                    x = 16
                    y += 36

        x = 16
        for i in range(9):
            self.FurnaceWindow.cellPositions[i] = [(x, 284), None]
            x += 36

    def initlitFurnaceWindow(self):
        self.litFurnaceWindow = litFurnaceWindow(self.gl)
        self.litFurnaceWindow.setWindow(self.gl.gui.GUI_TEXTURES["lit_progress"])
        #self.litFurnaceWindow.clickEvent = self.windowClickEvent
        #self.litFurnaceWindow.updateFunctions.append(self.updateFurnaceWindow)
        






    def showChestWindow(self):
        if not hasattr(self, 'ChestWindow'):
            self.initChestWindow()
        self.ChestWindow.show()
    def showFurnaceWindow(self):
        if not hasattr(self, 'FurnaceWindow'):
            self.initFurnaceWindow()
        self.FurnaceWindow.show()
        if self.burning == True:
            self.showlitFurnaceWindow()
    def showWindow(self):
        if not hasattr(self, 'UpdateWindow'):
            self.initWindow()
        self.window.show()
    def showlitFurnaceWindow(self):
        if not hasattr(self, 'litFurnaceWindow'):
            self.initlitFurnaceWindow()
        self.litFurnaceWindow.show()
    def showCraftingTable(self):
        if not hasattr(self, 'craftingWindow'):
            self.initCraftingTableWindow()
        self.craftingWindow.show()

    def windowClickEvent(self, button, cell):
        if button[0]:  # Left click
            try:
                print(self.FurnaceWindow.cellPositions[cell])
                print(cell)
            except:
                print(cell)
            if self.draggingItem:
                if self.inventory[cell][1] == 0:
                    self.inventory[cell] = self.draggingItem[:]
                    self.draggingItem = []
                else:
                    safe = [self.inventory[cell][0], self.inventory[cell][1]]
                    self.inventory[cell] = self.draggingItem[:]
                    self.draggingItem = safe
            else:
                if self.inventory[cell][1] != 0:
                    self.draggingItem = [self.inventory[cell][0], self.inventory[cell][1]]
                    self.inventory[cell] = ["", 0]
                    
        elif button[2]:  # Right click
            if self.draggingItem:
                if self.inventory[cell][0] == self.draggingItem[0] and self.draggingItem[1] > 0:
                    self.inventory[cell][1] += 1
                    self.draggingItem[1] -= 1
                    if self.draggingItem[1] == 0:
                        self.draggingItem = []
                elif self.inventory[cell][1] == 0 and self.draggingItem[1] > 0:
                    self.inventory[cell] = [self.draggingItem[0], 1]
                    self.draggingItem[1] -= 1
                    if self.draggingItem[1] == 0:
                        self.draggingItem = []
            else:
                # Take half stack
                if self.inventory[cell][1] > 1:
                    half = self.inventory[cell][1] // 2
                    remaining = self.inventory[cell][1] - half
                    self.draggingItem = [self.inventory[cell][0], half]
                    self.inventory[cell][1] = remaining
                elif self.inventory[cell][1] == 1:
                    self.draggingItem = [self.inventory[cell][0], 1]
                    self.inventory[cell] = ["", 0]


    def CraftingItem(self, objects, tableType=False):
        item = ["", 0]  # Default return (no crafting)
        if not hasattr(self, 'burning'):
            self.burning = False
        if not hasattr(self, 'sand_processed'):
            self.sand_processed = 0  # Track how much sand has been processed during burning
        if not hasattr(self, 'sand_processing'):
            self.sand_processing = False  # Track if sand is currently being processed
    
        if tableType == "furnace":
            def burning_furnace():
                self.burning = False
                self.sand_processed = 0  # Reset sand counter when burning stops
                self.sand_processing = False  # Reset processing state
                if len(self.gl.updateEvents) > self.windowId:
                    self.gl.updateEvents.pop(self.windowId)


            def add_glass():
                if self.inventory[109][0] == "glass" and self.inventory[109][1] <= 63:
                    self.inventory[109][1] += 1
                elif self.inventory[109][1] == 0 or "glass" not in self.inventory[109]:
                    self.inventory[109] = ["glass", 1]
            
                # Mark that sand processing is complete
                self.sand_processing = False

            def consume_sand_and_produce_glass():
                # Consume sand when glass production starts
                if self.inventory[107][1] > 0:
                    self.inventory[107][1] -= 1
                    if self.inventory[107][1] == 0:
                        self.inventory[107][0] = ""
                    self.sand_processed += 1  # Count this sand
            
                # Mark that sand is being processed
                self.sand_processing = True
            
                # Start glass production timer (10 seconds)
                timer2 = threading.Timer(10.0, add_glass)
                timer2.start()
        
            if objects == ["sand","coal_ore"] and self.inventory[109][1] <= 63:
                # Starting new burn cycle - reset counters
                self.sand_processed = 0
                self.sand_processing = False
            
                # Consume coal
                if self.inventory[108][1] > 0:
                    self.inventory[108][1] -= 1
                    if self.inventory[108][1] == 0:
                        self.inventory[108][0] = ""

                self.burning = True
                timer = threading.Timer(80.0, burning_furnace)   
                timer.start()
                self.showlitFurnaceWindow()

                # Start sand processing immediately
                consume_sand_and_produce_glass()

            elif (self.burning == True and objects == ["sand",""] and 
                  self.inventory[109][1] <= 63 and self.sand_processed < 8 and 
                  not self.sand_processing):
                # Only consume new sand if:
                # 1. Furnace is burning
                # 2. Less than 8 sand processed in this cycle
                # 3. No sand is currently being processed (previous glass production finished)
            
                consume_sand_and_produce_glass()

        #print(self.burning)
            return item
        if tableType == "crafting_table": # crafting_table crafting
###################### crafting_table
            if "log_oak" in objects and self.inventory[41][1] <= 63:
                for i in range(41, 51):  
                    if self.inventory[i][1] > 0:
                        self.inventory[i][1] -= 1
                        if self.inventory[i][1] == 0:
                            self.inventory[i][0] = ""

                if self.inventory[51][0] == "planks_oak" and self.inventory[51][1] <= 63:
                    self.inventory[51][1] += 4
                    return item

                elif self.inventory[51][1] == 0 and "planks_oak" not in self.inventory[51]:
                    self.inventory[51] = ["planks_oak", 4]
                    return item
########################## FURNACE
            if objects == ['cobblestone', 'cobblestone', 'cobblestone', 'cobblestone', '',
                          'cobblestone', 'cobblestone', 'cobblestone', 'cobblestone'] and "furnace" not in self.inventory[51]:
                for i in range(41, 51):  
                    if self.inventory[i][1] > 0:
                        self.inventory[i][1] -= 1
                        if self.inventory[i][1] == 0:
                            self.inventory[i][0] = ""

                if self.inventory[51][1] == 0 and "furnace" not in self.inventory[51]:
                    self.inventory[51] = ["furnace", 1]
                    return item
############################ chest
            if objects == ['planks_oak', 'planks_oak', 'planks_oak', 'planks_oak', '',
                          'planks_oak', 'planks_oak', 'planks_oak', 'planks_oak'] and "chest" not in self.inventory[51]:
                for i in range(41, 51):  
                    if self.inventory[i][1] > 0:
                        self.inventory[i][1] -= 1
                        if self.inventory[i][1] == 0:
                            self.inventory[i][0] = ""

                if self.inventory[51][1] == 0 and "chest" not in self.inventory[51]:
                    self.inventory[51] = ["chest", 1]
                    return item
#################################### 2x2 PLAYERINVENTORY CRAFTING
        if tableType == "playerinventory":  # 2x2 crafting
            if all(obj == "planks_oak" for obj in objects) and "crafting_table" not in self.inventory[41]:
                for i in range(37, 41):  
                    if self.inventory[i][1] > 0:
                        self.inventory[i][1] -= 1
                        if self.inventory[i][1] == 0:
                            self.inventory[i][0] = ""  

                    
                if self.inventory[41][1] == 0:  # Empty slot
                    self.inventory[41] = ["crafting_table", 1]
                    return item
                    
                    
            elif "stone" in objects and self.inventory[41][1] <= 63:
                for i in range(37, 41):  
                    if self.inventory[i][0] == "stone" and self.inventory[i][1] > 0:
                    
                        self.inventory[i][1] -= 1
                        if self.inventory[i][1] == 0:
                            self.inventory[i][0] = ""
                        
                if self.inventory[41][0] == "cobblestone" and self.inventory[41][1] <= 63:
                    self.inventory[41][1] += 1
                    return item

                elif self.inventory[41][1] == 0 and "cobblestone" not in self.inventory[41]:
                    self.inventory[41] = ["cobblestone", 1]
                    return item
                    
            elif all(obj == "sand" for obj in objects) and self.inventory[41][1] <= 63:
                for i in range(37, 41):
                    if self.inventory[i][1] > 0:
                        self.inventory[i][1] -= 1
                        if self.inventory[i][1] == 0:
                            self.inventory[i][0] = ""
                    
                if self.inventory[41][0] == "glass" and self.inventory[41][1] <= 63:
                    self.inventory[41][1] += 4
                    return item
                
                elif self.inventory[41][1] == 0 and "glass" not in self.inventory[41]:
                    self.inventory[41] = ["glass", 4]
                    return item
                    
            elif "log_oak" in objects and self.inventory[41][1] <= 63:
                for i in range(37, 41):  
                    if self.inventory[i][1] > 0:
                        self.inventory[i][1] -= 1
                        if self.inventory[i][1] == 0:
                            self.inventory[i][0] = ""

                if self.inventory[41][0] == "planks_oak" and self.inventory[41][1] <= 63:
                    self.inventory[41][1] += 4
                    return item

                elif self.inventory[41][1] == 0 and "planks_oak" not in self.inventory[41]:
                    self.inventory[41] = ["planks_oak", 4]
                    return item
                    

                        
            elif all(obj == "cobblestone" for obj in objects) and self.inventory[41][1] <= 63:
                for i in range(37, 41):  
                    if self.inventory[i][1] > 0:
                        self.inventory[i][1] -= 1
                        if self.inventory[i][1] == 0:
                            self.inventory[i][0] = "" 
                
                if self.inventory[41][1] == 0:
                    self.inventory[41] = ["stone_bricks", 1]
                    return item

                elif self.inventory[41][0] == "stone_bricks" and self.inventory[41][1] <= 63:
                    self.inventory[41][1] += 1
                    return item
                    
                        
            
        return item

    def updateWindow(self, win, mousePos):
        crafting_grid = [
            self.inventory[37][0] if self.inventory[37][1] else "",
            self.inventory[38][0] if self.inventory[38][1] else "",
            self.inventory[39][0] if self.inventory[39][1] else "",
            self.inventory[40][0] if self.inventory[40][1] else "",
        ]
        self.CraftingItem(crafting_grid,tableType="playerinventory")    

        for i in self.window.cellPositions.items():
            xx, yy = self.window.cellPositions[i[0]][0][0], self.window.cellPositions[i[0]][0][1]

            self.window.cellPositions[i[0]][1] = self.inventory[i[0]]
            inv = self.inventory[i[0]]

            if inv[1] == 0 or inv[0] == 0:
                continue
            self.gl.inventory_textures[inv[0]].blit((self.gl.WIDTH // 2 - (win.width // 2)) + xx + 5,
                                                    (self.gl.HEIGHT // 2 + (win.height // 2)) - yy - 27)
            if inv[1] > 1:
                lx = (self.gl.WIDTH // 2 - (win.width // 2)) + xx + 15
                ly = (self.gl.HEIGHT // 2 + (win.height // 2)) - yy - 32
                lbl = pyglet.text.Label(str(inv[1]),
                                        font_name='Minecraft Rus',
                                        color=(255, 255, 255, 255),
                                        font_size=10,
                                        x=lx, y=ly)
                lbl.draw()

        if self.draggingItem:
            if self.draggingItem[1]:
                drg = self.draggingItem
                mp = list(mousePos)
                mp[0] -= 11
                mp[1] += 11

                self.gl.inventory_textures[drg[0]].blit(mp[0], self.gl.HEIGHT - mp[1])

                lx = mp[0] + 11
                ly = self.gl.HEIGHT - mp[1] - 5
                lbl = pyglet.text.Label(str(drg[1]),
                                        font_name='Minecraft Rus',
                                        color=(255, 255, 255, 255),
                                        font_size=10,
                                        x=lx, y=ly)
                lbl.draw()

    def updateCraftingWindow(self, win, mousePos):
        crafting_grid = [
            self.inventory[42][0] if self.inventory[42][1] else "",
            self.inventory[43][0] if self.inventory[43][1] else "",
            self.inventory[44][0] if self.inventory[44][1] else "",
            self.inventory[45][0] if self.inventory[45][1] else "",
            self.inventory[46][0] if self.inventory[46][1] else "",
            self.inventory[47][0] if self.inventory[47][1] else "",
            self.inventory[48][0] if self.inventory[48][1] else "",
            self.inventory[49][0] if self.inventory[49][1] else "",
            self.inventory[50][0] if self.inventory[50][1] else "",

        ]
        self.CraftingItem(crafting_grid,tableType="crafting_table")
        for i in self.craftingWindow.cellPositions.items():
            xx, yy = self.craftingWindow.cellPositions[i[0]][0][0], self.craftingWindow.cellPositions[i[0]][0][1]

            self.craftingWindow.cellPositions[i[0]][1] = self.inventory[i[0]]
            inv = self.inventory[i[0]]

            
            if inv[1] == 0 or inv[0] == 0:
                continue
            if i[0] == 51 and inv[1] > 0:
                glPushMatrix()  # Save current OpenGL state
                scale = 1.5  # Desired size multiplier
                # Center the scaled texture in the slot
                glTranslatef(
                    (self.gl.WIDTH // 2 - (win.width // 2)) + xx + 5 - (16 * (scale-1)/2),
                    (self.gl.HEIGHT // 2 + (win.height // 2)) - yy - 27 - (16 * (scale-1)/2),
                    0
                )
                glScalef(scale, scale, 1)  # Apply scaling
                self.gl.inventory_textures[inv[0]].blit(0, 0)  # Draw at (0,0) due to translate
                glPopMatrix()  # Restore OpenGL state (CRITICAL!)
            else:
                self.gl.inventory_textures[inv[0]].blit((self.gl.WIDTH // 2 - (win.width // 2)) + xx + 5,
                                                     (self.gl.HEIGHT // 2 + (win.height // 2)) - yy - 27)
            if inv[1] > 1:
                lx = (self.gl.WIDTH // 2 - (win.width // 2)) + xx + 15
                ly = (self.gl.HEIGHT // 2 + (win.height // 2)) - yy - 32
                lbl = pyglet.text.Label(str(inv[1]),
                                        font_name='Minecraft Rus',
                                        color=(255, 255, 255, 255),
                                        font_size=10,
                                        x=lx, y=ly)
                lbl.draw()

        if self.draggingItem:
            if self.draggingItem[1]:
                drg = self.draggingItem
                mp = list(mousePos)
                mp[0] -= 11
                mp[1] += 11

                self.gl.inventory_textures[drg[0]].blit(mp[0], self.gl.HEIGHT - mp[1])

                lx = mp[0] + 11
                ly = self.gl.HEIGHT - mp[1] - 5
                lbl = pyglet.text.Label(str(drg[1]),
                                        font_name='Minecraft Rus',
                                        color=(255, 255, 255, 255),
                                        font_size=10,
                                        x=lx, y=ly)
                lbl.draw()

    def updateChestWindow(self, win, mousePos):
        for i in self.ChestWindow.cellPositions.items():
            xx, yy = self.ChestWindow.cellPositions[i[0]][0][0], self.ChestWindow.cellPositions[i[0]][0][1]

            self.ChestWindow.cellPositions[i[0]][1] = self.inventory[i[0]]
            inv = self.inventory[i[0]]

            if inv[1] == 0 or inv[0] == 0:
                continue
            self.gl.inventory_textures[inv[0]].blit((self.gl.WIDTH // 2 - (win.width // 2)) + xx + 5,
                                                    (self.gl.HEIGHT // 2 + (win.height // 2)) - yy - 27)
            if inv[1] > 1:
                lx = (self.gl.WIDTH // 2 - (win.width // 2)) + xx + 15
                ly = (self.gl.HEIGHT // 2 + (win.height // 2)) - yy - 32
                lbl = pyglet.text.Label(str(inv[1]),
                                        font_name='Minecraft Rus',
                                        color=(255, 255, 255, 255),
                                        font_size=10,
                                        x=lx, y=ly)
                lbl.draw()

        if self.draggingItem:
            if self.draggingItem[1]:
                drg = self.draggingItem
                mp = list(mousePos)
                mp[0] -= 11
                mp[1] += 11

                self.gl.inventory_textures[drg[0]].blit(mp[0], self.gl.HEIGHT - mp[1])

                lx = mp[0] + 11
                ly = self.gl.HEIGHT - mp[1] - 5
                lbl = pyglet.text.Label(str(drg[1]),
                                        font_name='Minecraft Rus',
                                        color=(255, 255, 255, 255),
                                        font_size=10,
                                        x=lx, y=ly)
                lbl.draw()
    def updateFurnaceWindow(self, win, mousePos):
        crafting_grid = [
            self.inventory[107][0] if self.inventory[107][1] else "",
            self.inventory[108][0] if self.inventory[108][1] else ""

        ]
        self.CraftingItem(crafting_grid,tableType="furnace")
        for i in self.FurnaceWindow.cellPositions.items():
            xx, yy = self.FurnaceWindow.cellPositions[i[0]][0][0], self.FurnaceWindow.cellPositions[i[0]][0][1]

            self.FurnaceWindow.cellPositions[i[0]][1] = self.inventory[i[0]]
            inv = self.inventory[i[0]]

            if inv[1] == 0 or inv[0] == 0:
                continue
            self.gl.inventory_textures[inv[0]].blit((self.gl.WIDTH // 2 - (win.width // 2)) + xx + 5,
                                                    (self.gl.HEIGHT // 2 + (win.height // 2)) - yy - 27)
            if inv[1] > 1:
                lx = (self.gl.WIDTH // 2 - (win.width // 2)) + xx + 15
                ly = (self.gl.HEIGHT // 2 + (win.height // 2)) - yy - 32
                lbl = pyglet.text.Label(str(inv[1]),
                                        font_name='Minecraft Rus',
                                        color=(255, 255, 255, 255),
                                        font_size=10,
                                        x=lx, y=ly)
                lbl.draw()

        if self.draggingItem:
            if self.draggingItem[1]:
                drg = self.draggingItem
                mp = list(mousePos)
                mp[0] -= 11
                mp[1] += 11

                self.gl.inventory_textures[drg[0]].blit(mp[0], self.gl.HEIGHT - mp[1])

                lx = mp[0] + 11
                ly = self.gl.HEIGHT - mp[1] - 5
                lbl = pyglet.text.Label(str(drg[1]),
                                        font_name='Minecraft Rus',
                                        color=(255, 255, 255, 255),
                                        font_size=10,
                                        x=lx, y=ly)
                lbl.draw()

    def addBlock(self, name):
        ext = False
        extech = -1
        sech = -1
        for item in self.inventory.items():
            i = item[1]
            if i[1] == 0 and sech == -1:
                sech = item[0]
            elif i[1] != 0:
                if i[0] == name and i[1] + 1 <= 64:
                    ext = True
                    extech = item[0]
                    break
        if ext:
            self.inventory[extech][1] += 1
        else:
            if self.inventory[self.activeInventory][1] == 0:
                sech = self.activeInventory
            self.inventory[sech] = [name, 1]

    def draw(self):
        inventory = self.gl.gui.GUI_TEXTURES["inventory"]
        sel_inventory = self.gl.gui.GUI_TEXTURES["sel_inventory"]
        fullheart = self.gl.gui.GUI_TEXTURES["fullheart"]
        halfheart = self.gl.gui.GUI_TEXTURES["halfheart"]
        heartbg = self.gl.gui.GUI_TEXTURES["heartbg"]
        inventory.blit(self.gl.WIDTH // 2 - (inventory.width // 2), 0)
        sel_inventory.blit((self.gl.WIDTH // 2 - (inventory.width // 2)) +
                           (40 * self.activeInventory), 0)

        for i in range(9):
            if i >= len(self.inventory):
                continue
            item_name, item_count = self.inventory[i]
    
            # Calculate the x position for this slot
            slot_x = (self.gl.WIDTH // 2 - (inventory.width // 2)) + (40 * i)
    
            if item_count > 0 and item_name:
                # Simple 3D effect without changing OpenGL state
                self._draw_simple_3d_item(item_name, slot_x + 11, 11, i)
            
                self.blocksLabel[i].text = str(item_count)
                # Position the label for this specific slot
                self.blocksLabel[i].x = slot_x + 25
                self.blocksLabel[i].y = 5
                self.blocksLabel[i].draw()
            else:
                self.blocksLabel[i].text = ""
                self.blocksLabel[i].draw()
    
        # Heart rendering (unchanged)
        for i in range(10):
            ay = 0
            if self.gl.player.hp <= 6:
                ay = self.heartAnimation[i][0]
                if self.heartAnimation[i][1] == "-":
                    self.heartAnimation[i][0] -= self.heartAnimation[i][2]
                else:
                    self.heartAnimation[i][0] += self.heartAnimation[i][2]

                if self.heartAnimation[i][0] > 1:
                    self.heartAnimation[i][1] = "-"
                elif self.heartAnimation[i][0] < -1:
                    self.heartAnimation[i][1] = "+"

            heartbg.blit((self.gl.WIDTH // 2 - (inventory.width // 2)) + ((heartbg.width - 1) * i),
                         inventory.height + 10 + ay)

        cntr = 0
        ch = 0
        x = (self.gl.WIDTH // 2 - (inventory.width // 2)) + 2
        for i in range(self.gl.player.hp):
            ay = 0
            if self.gl.player.hp <= 6:
                ay = self.heartAnimation[ch][0]

            if cntr == 0:
                hrt = halfheart
                cntr = 1
            else:
                cntr = 0
                hrt = fullheart

            hrt.blit(x, inventory.height + 12 + ay)

            if hrt == fullheart:
                x += heartbg.width - 1
                ch += 1

    def _draw_simple_3d_item(self, item_name, x, y, slot_index):
        """Draw item with simple 3D effect using multiple blits"""
        # Get animation time
        current_time = getattr(self, '_animation_time', 0)
    
        # Add floating animation for active slot
        float_offset = 0
        if slot_index == self.activeInventory:
            float_offset = int(math.sin(current_time * 3) * 2)
    
        # Get the texture
        texture = self.gl.inventory_textures[item_name]
    
        # Draw shadow/depth layers for 3D effect
        shadow_color = (0.3, 0.3, 0.3, 0.5)  # Dark shadow
    
        # Draw back layers (darker) for depth
        for i in range(3):
            offset = i + 1
            # You might need to implement a colored blit method or use OpenGL directly
            # For now, just draw the regular texture with slight offsets
            texture.blit(x + offset, y + offset + float_offset)
    
        # Draw the main texture on top
        texture.blit(x, y + float_offset)

    def update_animation_time(self):
        """Call this in your main update loop to animate the inventory items"""
        import time
        current_time = time.time()
        if not hasattr(self, '_last_update_time'):
            self._last_update_time = current_time
            self._animation_time = 0
    
        delta_time = current_time - self._last_update_time
        self._last_update_time = current_time
        self._animation_time += delta_time

    def draw_viewmodel(self):
        """Draw the viewmodel - call this from your main game loop"""
        self.viewmodel.draw()

    def get_active_item(self):
        return self.inventory_ref.inventory[self.inventory_ref.activeInventory][0]
   
    def change_active_item(self, new_index):
        if 0 <= new_index < len(self.inventory_ref.inventory):
            self.inventory_ref.activeInventory = new_index

    def update_viewmodel(self, current_time, walking=False):
        """Update the viewmodel - call this from your main game loop"""
        self.viewmodel.update(current_time, walking)

    def draw_viewmodel(self):
        """Draw the viewmodel - call this from your main game loop"""
        self.viewmodel.draw()

    def attack_single(self):
        """Call this for single attacks (right-click placing)"""
        self.viewmodel.start_attack()


    class ViewModel:
        def __init__(self, inventory_instance):
            self.attack_animation = 0  # 0 = not attacking, 1 = full swing
            self.last_attack_time = 0
            self.swing_direction = 1  # 1 or -1 for alternating swings
            self.inventory_ref = inventory_instance
            self.batch = pyglet.graphics.Batch()
            self.texture = None
            self.texture_name = None
            #original pos
            self.base_pos = [1.8, -1.0, -2.2]
            self.base_rot = [30, -55, 5]
            self.scale = 1.3
            self.is_attacking = False
            self.is_mining = False  # Continuous mining mode
            self.attack_start_time = 0
            self.attack_duration = 0.25  # Minecraft's attack duration
            self.attack_swing_amount = 30  # Rotation amount for swing
            self.attack_thrust_amount = 0.15  # Forward movement amount
            self.pos = self.base_pos.copy()
            self.rot = self.base_rot.copy()
        
            # Animation states
            self.sway_amount = [0, 0, 0]  # For mouse sway
            self.idle_rotation = 0
            self.item_switch_animation = 0
            self.last_active_item = 0
        
            self._create_cube()

        def attack(self):
            import time
            """Start the attack swing animation"""
            if self.attack_animation <= 0:  # Only start new swing if not already swinging
                self.attack_animation = 1.0
                self.swing_direction *= -1  # Alternate swing direction
                self.last_attack_time = time.time()

        def update(self, current_time, walking=False, mouse_dx=0, mouse_dy=0):
            # Update attack animation first
            if self.attack_animation > 0:
                self.attack_animation -= 0.1  # Adjust speed as needed
                if self.attack_animation < 0:
                    self.attack_animation = 0

        def _update_attack_animation(self):
            """Handle attack swing rotation"""
            if self.attack_animation > 0:
                # Calculate swing progress (0 to 1)
                swing_progress = 1.0 - self.attack_animation
        
                # Minecraft-like swing animation
                if swing_progress < 0.4:
                    # Initial fast swing
                    swing_amount = swing_progress / 0.4
                    self.rot[0] += swing_amount * 60 * self.swing_direction
                    self.rot[2] += swing_amount * 30 * self.swing_direction
                else:
                    # Slower return
                    swing_amount = (swing_progress - 0.4) / 0.6
                    swing_amount = 1.0 - swing_amount
                    self.rot[0] += swing_amount * 60 * self.swing_direction
                    self.rot[2] += swing_amount * 30 * self.swing_direction
        
                # Add some position movement during swing
                self.pos[0] += swing_progress * 0.2 * self.swing_direction
                self.pos[1] -= swing_progress * 0.1

        def _load_texture(self, texture_name):
            if self.inventory_ref.inventory[self.inventory_ref.activeInventory][0] != "":
                try:
                    texture = pyglet.image.load(f"textures/blocks/{texture_name}.png").get_texture()
                    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
                    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
                    return texture
                except:
                    texture = pyglet.image.load(f"textures/blocks/tbs/{texture_name} s.png").get_texture()
                    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
                    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
                    return texture
   
        def _create_cube(self):
            x = y = z = 0
            w = h = d = 1
            X, Y, Z = x + w, y + h, z + d
       
            vertex_data = [
                # Front face
                (x, y, Z,  X, y, Z,  X, Y, Z,  x, Y, Z),
                # Back face
                (X, y, z,  x, y, z,  x, Y, z,  X, Y, z),
                # Left face
                (x, y, z,  x, y, Z,  x, Y, Z,  x, Y, z),
                # Right face
                (X, y, Z,  X, y, z,  X, Y, z,  X, Y, Z),
                # Bottom face
                (x, y, z,  X, y, z,  X, y, Z,  x, y, Z),
                # Top face
                (x, Y, Z,  X, Y, Z,  X, Y, z,  x, Y, z),
            ]
       
            tex_coords = ('t2f', (0, 0, 1, 0, 1, 1, 0, 1))
       
            for face in vertex_data:
                self.batch.add(4, GL_QUADS, None,
                                ('v3f', face),
                                tex_coords)

        def start_attack(self):
            if not self.is_attacking and not self.is_mining:
                self.is_attacking = True
                self.attack_start_time = time.time()

        def start_mining(self):
            import time
            if not self.is_mining:
                self.is_mining = True
                self.attack_start_time = time.time()

        def stop_mining(self):
            """Call this method to stop continuous mining animation (release left-click)"""
            self.is_mining = False

        def update(self, current_time, walking=False, mouse_dx=0, mouse_dy=0):
            # Get active item from parent inventory
            active_item_name = self.inventory_ref.inventory[self.inventory_ref.activeInventory][0]
            current_active_slot = self.inventory_ref.activeInventory
  
            # Only reload texture if it changed
            if self.texture is None or self.texture_name != active_item_name:
                self.texture_name = active_item_name
                self.texture = self._load_texture(active_item_name)
   
            # Reset to base position and rotation
            self.pos = self.base_pos.copy()
            self.rot = self.base_rot.copy()
   
            # Apply various animations
            #self._update_idle_rotation(current_time)
        
            if walking:
                self._update_bobbing(current_time)
            if self.is_attacking or self.is_mining:
                self._update_attack_animation(current_time)

        def _update_bobbing(self, time):
            # Minecraft bobbing frequency - tied to footstep rhythm
            bob_frequency = 20  # Matches Minecraft's walking speed
       
            # Vertical bobbing - up and down movement
            vertical_bob = math.sin(time * bob_frequency) * 0.03
            self.pos[1] = self.base_pos[1] + vertical_bob
       
            # Horizontal sway - left/right movement (this is the key!)
            # Uses half frequency so it sways left-right-left-right with each step
            horizontal_sway = math.sin(time * bob_frequency * 0.5) * 0.04
            self.pos[0] = self.base_pos[0] + horizontal_sway
       
            # Rotational bobbing - tilts left and right with the sway
            tilt_amount = math.sin(time * bob_frequency * 0.5) * 3  # 3 degrees max tilt
            self.rot[2] = self.base_rot[2] + tilt_amount
       
            # Slight forward/back movement for more natural feel
            depth_bob = math.sin(time * bob_frequency * 0.7) * 0.01
            self.pos[2] = self.base_pos[2] + depth_bob

        def _update_attack_animation(self, current_time):
            """Handle the Minecraft-accurate attack animation"""
            elapsed = current_time - self.attack_start_time
       
            # For single attacks, stop after duration
            if self.is_attacking and elapsed >= self.attack_duration:
                self.is_attacking = False
                return
       
            # For mining, loop the animation
            if self.is_mining:
                # Use modulo to loop the animation
                elapsed = elapsed % self.attack_duration
            elif elapsed >= self.attack_duration:
                # Single attack finished
                self.is_attacking = False
                return
       
            # Calculate animation progress (0.0 to 1.0)
            progress = elapsed / self.attack_duration
       
            # Minecraft-style animation curve - fast down, quick back up
            if progress < 0.4:
                # Fast swing down (0.0 to 0.4) - 40% of animation
                swing_progress = progress / 0.4
                # Exponential ease-out for very fast initial swing
                swing_progress = 1 - math.pow(1 - swing_progress, 4)
            else:
                # Quick return to position (0.4 to 1.0) - 60% of animation
                return_progress = (progress - 0.4) / 0.6
                # Ease-out return
                return_progress = 1 - math.pow(1 - return_progress, 2)
                swing_progress = 1.0 - return_progress
       
            # Primary swing rotation - Minecraft swings across from right to left
            swing_rotation = swing_progress * self.attack_swing_amount
            self.rot[1] = self.base_rot[1] - swing_rotation
       
            # Secondary X-axis rotation for downward arc
            downward_rotation = swing_progress * 15  # Smaller downward component
            self.rot[0] = self.base_rot[0] + downward_rotation
       
            # Slight Z-axis tilt for natural swing feel
            tilt_rotation = math.sin(swing_progress * math.pi) * 8
            self.rot[2] = self.base_rot[2] + tilt_rotation
       
            # Forward thrust - peaks at middle of swing
            thrust_curve = math.sin(swing_progress * math.pi)
            thrust_offset = thrust_curve * self.attack_thrust_amount
            self.pos[2] = self.base_pos[2] + thrust_offset
       
            # Slight vertical bob - very subtle in Minecraft
            vertical_offset = math.sin(swing_progress * math.pi) * 0.05
            self.pos[1] = self.base_pos[1] - vertical_offset
       
            # Slight horizontal sway to match the swing
            horizontal_offset = swing_progress * 0.1
            self.pos[0] = self.base_pos[0] - horizontal_offset

        def draw(self):
            if self.texture is None:
                return
           
            glDisable(GL_FOG)
            glPushMatrix()
            glLoadIdentity()
        
            # Apply transformations in the right order for natural movement
            glTranslatef(*self.pos)
            glRotatef(self.rot[0], 1, 0, 0)  # Pitch
            glRotatef(self.rot[1], 0, 1, 0)  # Yaw
            glRotatef(self.rot[2], 0, 0, 1)  # Roll
            glScalef(self.scale, self.scale, self.scale)
        
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.texture.id)
       
            # Skip material properties to avoid OpenGL state issues
            glClear(GL_DEPTH_BUFFER_BIT)
       
            self.batch.draw()
       
            glDisable(GL_TEXTURE_2D)
            glPopMatrix()
            glEnable(GL_FOG)
        

   

   
