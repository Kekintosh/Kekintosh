#from game.blocks.CraftingTable import CraftingTable
from game.world.Explosion import Explosion
from game.entity.Inventory import *

def openBlockInventory(playerClass, blockClass, gl):
    if blockClass.name == "crafting_table":
        playerClass.inventory.showCraftingTable()
    if blockClass.name == "chest":
        playerClass.inventory.showChestWindow()
    if blockClass.name == "furnace":
        playerClass.inventory.showFurnaceWindow()
    
    if blockClass.name == "tnt":
        gl.blockSound.playBoomSound()
        exp = Explosion(gl, blockClass.p, 5, blockClass)
        exp.run()


def canOpenBlock(playerClass, blockClass, gl):
    if blockClass.name == "crafting_table":
        return True
    if blockClass.name == "chest":
        return True
    if blockClass.name == "furnace":        
        return True
    if blockClass.name == "tnt":
        return True

    return False
