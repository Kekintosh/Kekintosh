import math
from random import randint

import pyglet
from OpenGL.GL import *

from game.blocks.BlockEvent import *
from functions import roundPos, flatten, cube_vertices
from game.blocks.DestroyBlock import DestroyBlock
from settings import *


class Player:
    def __init__(self, x=0, y=0, z=0, rotation=[0, 0], gl=None):
        print("Init Player class...")

        self.last_mouse_pos = None
        self.position, self.rotation = [x, y, z], rotation
        self.speed = 0.06
        self.gl = gl
        self.gravity = 5.8
        self.tVel = 50
        self.dy = 0
        self.shift = 0
        self.cameraShake = [0, False]
        self.canShake = True
        
        self.lastShiftPos = self.position
        self.cameraType = 1
        self.hp = -1
        self.bInAir = False
        self.playerDead = False
        self.inventory = None
        self.GODMODE = 0
        self.lastPlayerPosOnGround = [0, 0, 0]
        self.playerFallY = 0

        self.kW, self.kS, self.kA, self.kD = 0, 0, 0, 0

    def setCameraShake(self):
        if not self.canShake or self.shift > 0:
            return

        if not self.cameraShake[1]:
            self.cameraShake[0] -= 0.007
            if self.cameraShake[0] < -0.1:
                self.cameraShake[1] = True
        else:
            self.cameraShake[0] += 0.007
            if self.cameraShake[0] > 0.1:
                self.cameraShake[1] = False

    def setShift(self, b):
        if b:
            if self.shift < 0.17:
                self.shift += 0.05
        else:
            if self.shift > 0:
                self.shift -= 0.05


    def updatePosition(self, dt):
        if self.gl.allowEvents["movePlayer"]:
            mx, my = pygame.mouse.get_pos()
            center_x, center_y = self.gl.WIDTH // 2, self.gl.HEIGHT // 2
            rdx, rdy = mx - center_x, my - center_y

            if abs(rdx) > 1 or abs(rdy) > 1:
                rdx /= 8
                rdy /= 8

                self.rotation[0] += rdy
                self.rotation[1] += rdx

                if self.rotation[0] > 90:
                    self.rotation[0] = 90
                elif self.rotation[0] < -90:
                    self.rotation[0] = -90

            DX, DY, DZ = 0, 0, 0
            minKd = 0.08

            # Initialize movement state if not exists
            if not hasattr(self, 'is_sprinting'):
                self.is_sprinting = False

            key = pygame.key.get_pressed()
        
            # Calculate base movement speed
            rotY = self.rotation[1] / 180 * math.pi
            base_speed = self.speed
        
            # Handle sprinting
            key = pygame.key.get_pressed()
            if key[pygame.K_LCTRL]:
                self.current_fov = 110  # Sprint FOV
                base_speed += 0.012  # Sprint boost
            else:
                self.current_fov = 100  # Normal FOV
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            gluPerspective(self.current_fov, (self.gl.WIDTH/self.gl.HEIGHT), 0.1, RENDER_DISTANCE)
            glMatrixMode(GL_MODELVIEW)
            
            # Handle sneaking
            if key[pygame.K_LSHIFT]:
                self.setShift(True)
                base_speed -= 0.01  # Sneak slowdown
            else:
                self.setShift(False)

            dx = base_speed * math.sin(rotY)
            dz = base_speed * math.cos(rotY)

            # Movement input handling
            if self.kW > 0 or key[pygame.K_w]:
                DX += dx
                DZ -= dz
                self.setCameraShake()
                if self.kW > 0:
                    self.kW -= minKd
                
            if self.kS > 0 or key[pygame.K_s]:
                DX -= dx
                DZ += dz
                self.setCameraShake()
                if self.kS > 0:
                    self.kS -= minKd
                
            if self.kA > 0 or key[pygame.K_a]:
                DX -= dz
                DZ -= dx
                self.setCameraShake()
                if self.kA > 0:
                    self.kA -= minKd
                
            if self.kD > 0 or key[pygame.K_d]:
                DX += dz
                DZ += dx
                self.setCameraShake()
                if self.kD > 0:
                    self.kD -= minKd

            # Jump handling
            if key[pygame.K_SPACE]:
                if not hasattr(self, 'space_pressed') or not self.space_pressed:
                    self.jump()
                    self.space_pressed = True
                    # Maintain momentum when jumping
                    if key[pygame.K_w]:
                        self.kW = 1
                    if key[pygame.K_a]:
                        self.kA = 1
                    if key[pygame.K_s]:
                        self.kS = 1
                    if key[pygame.K_d]:
                        self.kD = 1
            else:
                self.space_pressed = False

            dt = self.speed
            self.position = [self.position[0] + DX, self.position[1] + DY, self.position[2] + DZ]

            # Physics subdivision for smooth movement
            if dt < 0.2:
                dt /= 10
                DX /= 10
                DY /= 10
                DZ /= 10
                for i in range(10):
                    self.move(dt, DX, DY, DZ)
            else:
                self.move(dt, DX, DY, DZ)
        else:
            self.move(self.speed, 0, 0, 0)

        glPushMatrix()
        glRotatef(self.rotation[0], 1, 0, 0)
        glRotatef(self.rotation[1], 0, 1, 0)
        glTranslatef(-self.position[0],
                     -self.position[1] + self.shift + self.cameraShake[0],
                     -self.position[2])

    def jump(self):
        if hasattr(self, 'GODMODE') and self.GODMODE == 1:
            # Creative mode - handled in move()
            pass
        else:
            # Use your original jump value that worked
            if not self.dy:
                self.dy = 4

    def move(self, dt, dx, dy, dz):
        if hasattr(self, 'GODMODE') and self.GODMODE == 1:
            # Creative mode flight
            keys = pygame.key.get_pressed()
        
            if keys[pygame.K_SPACE]:
                self.dy = 0.2 * (dt * 20)
            elif keys[pygame.K_LSHIFT]:
                self.dy = -0.2 * (dt * 20)
            else:
                self.dy = 0
            
            dy = self.dy * dt
        else:
            # Original physics system
            self.dy -= dt * self.gravity
            self.dy = max(self.dy, -self.tVel)
            dy += self.dy * dt

            if self.dy > 19.8:
                self.dy = 19.8

        # Store original position for collision detection
        old_x, old_y, old_z = self.position

        # Use your original collision system
        x, y, z = self.position
        new_pos = self.collide((x + dx, y + dy, z + dz))

        # Ground checks and sounds (from your original)
        col2 = roundPos((new_pos[0], new_pos[1] - 2, new_pos[2]))
        self.canShake = self.position[1] == new_pos[1]
    
        if self.position[0] != new_pos[0] or self.position[2] != new_pos[2]:
            if col2 in self.gl.cubes.cubes and self.shift <= 0:
                self.gl.blockSound.playStepSound(self.gl.cubes.cubes[col2].name)

        # Fall damage system (from your original)
        if not hasattr(self, 'bInAir'):
            self.bInAir = False
            self.lastPlayerPosOnGround = [0, 0, 0]
            self.playerFallY = 0

        if not self.bInAir:
            for i in range(1, 6):
                col21 = roundPos((new_pos[0], new_pos[1] - i, new_pos[2]))
                if col21 not in self.gl.cubes.cubes:
                    self.bInAir = True
                    if self.playerFallY < new_pos[1]:
                        self.playerFallY = round(new_pos[1] - self.lastPlayerPosOnGround[1])
                else:
                    self.bInAir = False
                    break
        else:
            self.lastPlayerPosOnGround = new_pos

        if self.bInAir and col2 in self.gl.cubes.cubes:
            if hasattr(self, 'hp') and self.hp > 0:
                if 3 < self.playerFallY:
                    self.hp -= 1
                    if self.playerFallY < 10:
                        self.hp -= 3
                    elif self.playerFallY < 16:
                        self.hp -= 5
                    elif self.playerFallY < 23:
                        self.hp -= 8
                    elif self.playerFallY < 30:
                        self.hp -= 11
                    else:
                        self.hp = 0
                    self.gl.blockSound.cntr = 99
                    self.gl.blockSound.damageByBlock(self.gl.cubes.cubes[col2].name, self.hp)
            
                if self.hp <= 0 and not self.playerDead:
                    self.dead()

            self.bInAir = False
            if hasattr(self.gl, 'particles'):
                self.gl.particles.addParticle((new_pos[0], new_pos[1] - 1, new_pos[2]),
                                            self.gl.cubes.cubes[col2],
                                            direction="down",
                                            count=10)

        self.position = new_pos

    def collide(self, pos):
        # Void damage (from your original)
        if -90 > pos[1] > -9000:
            if not self.playerDead:
                self.hp -= 2
                self.gl.blockSound.damageByBlock("ahh", 1)
                if self.hp <= 0:
                    self.dead()

        # Use your original collision system that worked
        p = list(pos)
        np = roundPos(pos)
        for face in ((-1, 0, 0), (1, 0, 0), (0, -1, 0), (0, 1, 0), (0, 0, -1), (0, 0, 1)):
            for i in (0, 1, 2):
                if not face[i]:
                    continue
                d = (p[i] - np[i]) * face[i]
                pad = 0.25
                if d < pad:
                    continue
                for dy in (0, 1):
                    op = list(np)
                    op[1] -= dy
                    op[i] += face[i]
                    if tuple(op) in self.gl.cubes.collidable:
                        p[i] -= (d - pad) * face[i]
                        if face[1]:
                            self.dy = 0
                        break
        return tuple(p)

    # Keep existing methods unchanged
    def dead(self):
        self.playerDead = True
        self.gl.deathScreen()
        for i in self.inventory.inventory.items():
            for j in range(i[1][1]):
                self.gl.droppedBlock.addBlock((
                    self.position[0] + randint(-2, 2), self.position[1], self.position[2] + randint(-2, 2)
                ), i[1][0])
            self.inventory.inventory[i[0]] = [i[1][0], 0]

    def mouseEvent(self, button):
        blockByVec = self.gl.cubes.hitTest(self.position, self.get_sight_vector())

        if button == 1 and blockByVec[0]:
            self.gl.destroy.destroy(self.gl.cubes.cubes[blockByVec[0]].name, blockByVec)
        else:
            self.gl.destroy.destroyStage = -1

        if button == 2 and blockByVec[0]:
            if self.inventory.inventory[self.inventory.activeInventory][1] == 0:
                itm = -1
                for item in self.inventory.inventory.items():
                    i = item[1]
                    if i[0] == self.gl.cubes.cubes[blockByVec[0]].name and i[1] != 0:
                        itm = item[0]
                        break
                if itm != -1:
                    self.inventory.inventory[self.inventory.activeInventory] = [
                        self.inventory.inventory[itm][0], self.inventory.inventory[itm][1]]
                    self.inventory.inventory[itm][1] = 0
                    self.gl.gui.showText(self.inventory.inventory[itm][0])
        if button == 3:
            if blockByVec[0] and self.shift <= 0:
                if blockByVec[0] in self.gl.cubes.cubes:
                    if canOpenBlock(self, self.gl.cubes.cubes[blockByVec[0]], self.gl):
                        openBlockInventory(self, self.gl.cubes.cubes[blockByVec[0]], self.gl)
                        return
            if blockByVec[1] and self.shift <= 0:
                if blockByVec[1] in self.gl.cubes.cubes:
                    if canOpenBlock(self, self.gl.cubes.cubes[blockByVec[1]], self.gl):
                        openBlockInventory(self, self.gl.cubes.cubes[blockByVec[1]], self.gl)
                        return
            if blockByVec[1]:
                playerPos = tuple(roundPos((self.position[0], self.position[1] - 1, self.position[2])))
                playerPos2 = tuple(roundPos((self.position[0], self.position[1], self.position[2])))
                blockByVec = blockByVec[1][0], blockByVec[1][1], blockByVec[1][2]
                if self.inventory.inventory[self.inventory.activeInventory][0] and \
                        self.inventory.inventory[self.inventory.activeInventory][1] and blockByVec != playerPos and \
                        blockByVec != playerPos2:
                    self.gl.cubes.add(blockByVec, self.inventory.inventory[self.inventory.activeInventory][0], now=True)
                    self.gl.blockSound.playBlockSound(self.gl.cubes.cubes[blockByVec].name)
                    self.inventory.inventory[self.inventory.activeInventory][1] -= 1

    def get_sight_vector(self):
        rotX, rotY = -self.rotation[0] / 180 * math.pi, self.rotation[1] / 180 * math.pi
        dx, dz = math.sin(rotY), -math.cos(rotY)
        dy, m = math.sin(rotX), math.cos(rotX)
        return dx * m, dy, dz * m

    def x(self):
        return self.position[0]

    def y(self):
        return self.position[1]

    def z(self):
        return self.position[2]

    def update(self):
        dt = clock.tick(MAX_FPS)
        prev_x, prev_y, prev_z = self.x(), self.y(), self.z()
        self.updatePosition(dt)
        self.moving = (self.x() != prev_x or self.y() != prev_y or self.z() != prev_z)

    def is_moving(self):
        return self.moving

    def setCameraShake(self):
        if not self.canShake or self.shift > 0:
            return

        if not self.cameraShake[1]:
            self.cameraShake[0] -= 0.007
            if self.cameraShake[0] < -0.1:
                self.cameraShake[1] = True
        else:
            self.cameraShake[0] += 0.007
            if self.cameraShake[0] > 0.1:
                self.cameraShake[1] = False

    def setShift(self, b):
        if b:
            if self.shift < 0.17:
                self.shift += 0.05
        else:
            if self.shift > 0:
                self.shift -= 0.05
