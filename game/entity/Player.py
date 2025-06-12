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
        self.speed = 0.03
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

            # Initialize movement state if not exists
            if not hasattr(self, 'move_forward'):
                self.move_forward = 0.0
            if not hasattr(self, 'move_strafe'):
                self.move_strafe = 0.0
            if not hasattr(self, 'is_sprinting'):
                self.is_sprinting = False

            key = pygame.key.get_pressed()
        
            # Reset movement input
            self.move_forward = 0.0
            self.move_strafe = 0.0
        
            # Handle input - Minecraft style
            if self.kW > 0 or key[pygame.K_w]:
                self.move_forward += 1.0
                if self.kW > 0:
                    self.kW -= 0.08
                
            if self.kS > 0 or key[pygame.K_s]:
                self.move_forward -= 1.0
                if self.kS > 0:
                    self.kS -= 0.08
                
            if self.kA > 0 or key[pygame.K_a]:
                self.move_strafe += 1.0
                if self.kA > 0:
                    self.kA -= 0.08
                
            if self.kD > 0 or key[pygame.K_d]:
                self.move_strafe -= 1.0
                if self.kD > 0:
                    self.kD -= 0.08

            # Sprint handling - exact Minecraft behavior
            if key[pygame.K_LCTRL] and self.move_forward > 0:
                self.is_sprinting = True
            else:
                self.is_sprinting = False

            # Sneak handling
            is_sneaking = key[pygame.K_LSHIFT]
            if is_sneaking:
                self.setShift(True)
            else:
                self.setShift(False)

            # Jump - only trigger once per press
            if key[pygame.K_SPACE]:
                if not hasattr(self, 'space_pressed') or not self.space_pressed:
                    self.jump()
                    self.space_pressed = True
            else:
                self.space_pressed = False

            # Calculate movement - EXACT Minecraft mechanics
            movement_speed = self.get_movement_speed(is_sneaking)
        
            # Apply movement multipliers
            forward = self.move_forward * movement_speed
            strafe = self.move_strafe * movement_speed
        
            # Diagonal movement normalization (Minecraft does this)
            if self.move_forward != 0 and self.move_strafe != 0:
                forward *= 0.7071067811865476  # 1/sqrt(2)
                strafe *= 0.7071067811865476

            # Convert to world coordinates
            rotY = self.rotation[1] / 180 * math.pi
            sin_yaw = math.sin(rotY)
            cos_yaw = math.cos(rotY)
        
            dx = strafe * cos_yaw - forward * sin_yaw
            dz = forward * cos_yaw + strafe * sin_yaw
        
            # Camera shake for footsteps
            if (abs(dx) > 0 or abs(dz) > 0) and abs(self.dy) < 0.1:
                self.setCameraShake()

            self.position = [self.position[0] + dx, self.position[1], self.position[2] + dz]

            # Physics update
            physics_dt = self.speed
            if physics_dt < 0.2:
                physics_dt /= 10
                dx /= 10
                dz /= 10
                for i in range(10):
                    self.move(physics_dt, dx, 0, dz)
            else:
                self.move(physics_dt, dx, 0, dz)
        else:
            self.move(self.speed, 0, 0, 0)

        glPushMatrix()
        glRotatef(self.rotation[0], 1, 0, 0)
        glRotatef(self.rotation[1], 0, 1, 0)
        glTranslatef(-self.position[0],
                     -self.position[1] + self.shift + self.cameraShake[0],
                     -self.position[2])

    def get_movement_speed(self, is_sneaking):
        """Get movement speed based on current state - exact Minecraft values"""
        # Use your existing speed as base multiplier
        base_multiplier = self.speed * 50  # Convert 0.03 to reasonable movement
    
        if self.GODMODE == 1:
            # Creative mode flying speed
            if self.is_sprinting:
                return base_multiplier * 4.0
            else:
                return base_multiplier * 2.0
        else:
            # Survival mode
            if is_sneaking:
                return base_multiplier * 0.3  # Sneaking
            elif self.is_sprinting:
                return base_multiplier * 1.3  # Sprinting
            else:
                return base_multiplier  # Walking

    def jump(self):
        if self.GODMODE == 1:
            # Creative mode - no jumping, handled in move()
            pass
        else:
            # Survival mode - can only jump when on ground
            if abs(self.dy) < 0.1:  # On ground
                self.dy = 7.0  # Use a value that works with your physics

    def move(self, dt, dx, dy, dz):
        if self.GODMODE == 1:
            # Creative mode flight
            keys = pygame.key.get_pressed()
        
            # Vertical movement in creative
            if keys[pygame.K_SPACE]:
                self.dy = 0.2 * (dt * 20)  # Scale with dt
            elif keys[pygame.K_LSHIFT]:
                self.dy = -0.2 * (dt * 20)  # Scale with dt
            else:
                self.dy = 0  # Hover
            
            dy = self.dy * dt
        else:
            # Survival mode gravity - use your existing values
            if not hasattr(self, 'dy'):
                self.dy = 0
            
            # Apply gravity using your existing gravity value
            self.dy -= self.gravity * dt
        
            # Terminal velocity using your existing tVel
            if self.dy < -self.tVel:
                self.dy = -self.tVel
            
            dy = self.dy * dt

        # Store original position for collision detection
        old_x, old_y, old_z = self.position

        # Collision detection
        x, y, z = self.position
        new_pos = self.collide((x + dx, y + dy, z + dz))

        # Handle collision effects
        if self.GODMODE != 1:
            # Ground collision - reset falling velocity
            if dy < 0 and new_pos[1] >= old_y:
                self.dy = 0
            # Ceiling collision - reset upward velocity  
            elif dy > 0 and new_pos[1] <= old_y:
                self.dy = 0

        # Ground checks and sounds
        if self.GODMODE != 1:
            col2 = roundPos((new_pos[0], new_pos[1] - 2, new_pos[2]))
        
            # Footstep sounds
            if (self.position[0] != new_pos[0] or self.position[2] != new_pos[2]):
                if col2 in self.gl.cubes.cubes and self.shift <= 0:
                    self.gl.blockSound.playStepSound(self.gl.cubes.cubes[col2].name)

        self.position = new_pos

    def collide(self, pos):
        # Void damage
        if -90 > pos[1] > -9000:
            if not self.playerDead:
                self.hp -= 2
                self.gl.blockSound.damageByBlock("ahh", 1)
                if self.hp <= 0:
                    self.dead()

        x, y, z = pos

        # Minecraft collision order: Y, X, Z
        new_y = self.collide_axis(self.position[0], y, self.position[2], 1)
        new_x = self.collide_axis(x, new_y, self.position[2], 0)
        new_z = self.collide_axis(new_x, new_y, z, 2)

        return (new_x, new_y, new_z)

    def collide_axis(self, x, y, z, axis):
        """Single axis collision - exact Minecraft AABB collision"""
        pos = [x, y, z]
        np = roundPos(pos)

        # Player hitbox: 0.6 wide, 1.8 tall
        # Minecraft uses 0.3 padding on X/Z, 0.0 on Y bottom, 1.8 on Y top
    
        if axis == 0:  # X axis
            faces = [(-1, 0, 0), (1, 0, 0)]
            pad = 0.3
        elif axis == 1:  # Y axis  
            faces = [(0, -1, 0), (0, 1, 0)]
            pad = 0.0 if pos[1] < np[1] else 1.8  # Different padding for up/down
        else:  # Z axis
            faces = [(0, 0, -1), (0, 0, 1)]
            pad = 0.3

        for face in faces:
            if not face[axis]:
                continue
            
            d = (pos[axis] - np[axis]) * face[axis]
        
            if axis == 1:  # Y axis special case
                if face[1] == -1:  # Moving down
                    pad = 0.0
                    if d < pad:
                        continue
                else:  # Moving up
                    pad = 1.8
                    if d < pad:
                        continue
            else:
                if d < pad:
                    continue
        
            # Check collision boxes
            collision_found = False
        
            if axis == 1:  # Y axis - check full player width
                for dx in [-1, 0, 1]:
                    for dz in [-1, 0, 1]:
                        op = [np[0] + dx, np[1] + face[1], np[2] + dz]
                        if tuple(op) in self.gl.cubes.collidable:
                            collision_found = True
                            break
                    if collision_found:
                        break
            else:  # X/Z axis - check player height
                for dy in [0, 1]:
                    op = list(np)
                    op[1] -= dy
                    op[axis] += face[axis]
                
                    if tuple(op) in self.gl.cubes.collidable:
                        collision_found = True
                        break
        
            if collision_found:
                pos[axis] -= (d - pad) * face[axis]
                break

        return pos[axis]

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
