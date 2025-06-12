import os
import time
from random import randint
import pyglet
from OpenGL.GL import *
from settings import *


def load_textures(self):
    print("Loading textures...")
    t = self.texture
    dirs = ['textures']
    while dirs:
        d = dirs.pop(0)
        textures = os.listdir(d)
        for file in textures:
            if os.path.isdir(d + '/' + file):
                dirs += [d + '/' + file]
            else:
                if ".png" not in file or d == "textures/blocks/block_destroy":
                    continue

                n = file.split('.')[0]
                self.texture_dir[n] = d
                image = pyglet.image.load(d + '/' + file)
                texture = image.get_mipmapped_texture()
                self.texture[n] = pyglet.graphics.TextureGroup(texture)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

                print("Successful loaded", n, "texture!")
    done = []
    items = sorted(self.texture_dir.items(), key=lambda i: i[0])
    for n1, d in items:
        n = n1.split(' ')[0]
        if n in done:
            continue
        done += [n]
        if d.startswith('textures/blocks'):
            if d == 'textures/blocks':
                self.inventory_textures[n] = pyglet.resource.image(f"{d}/{n}.png")
                self.block[n] = t[n], t[n], t[n], t[n], t[n], t[n]
            elif d == 'textures/blocks/tbs':
                self.inventory_textures[n] = pyglet.resource.image(f"{d}/{n} s.png")
                self.block[n] = t[n + ' s'], t[n + ' s'], t[n + ' b'], t[n + ' t'], t[n + ' s'], t[n + ' s']
            elif d == 'textures/blocks/ts':
                self.inventory_textures[n] = pyglet.resource.image(f"{d}/{n} s.png")
                self.block[n] = t[n + ' s'], t[n + ' s'], t[n + ' t'], t[n + ' t'], t[n + ' s'], t[n + ' s']
            if n in self.inventory_textures:
                self.inventory_textures[n].width = 22
                self.inventory_textures[n].height = 22


def translateSeed(seed):
    res = ""
    if seed == "":
        seed = str(randint(998, 43433))
    for i in seed:
        res += str(ord(i))
    while len(res) < 10:
        res += res[:-1]
    return int(res[0:10])


def cube_vertices(pos, n=0.5):
    x, y, z = pos
    v = tuple((x + X, y + Y, z + Z) for X in (-n, n) for Y in (-n, n) for Z in (-n, n))
    return tuple(tuple(k for j in i for k in v[j]) for i in
                 ((0, 1, 3, 2), (5, 4, 6, 7), (0, 4, 5, 1), (3, 7, 6, 2), (4, 0, 2, 6), (1, 5, 7, 3)))

def plant_vertices(pos, n=0.5):
    """Generate vertices for cross-shaped plant geometry (2 intersecting planes)"""
    x, y, z = pos
    
    # First plane (diagonal from corner to corner)
    plane1 = (
        x - n, y - n, z - n,  # bottom-left
        x + n, y - n, z + n,  # bottom-right  
        x + n, y + n, z + n,  # top-right
        x - n, y + n, z - n   # top-left
    )
    
    # Second plane (perpendicular diagonal)
    plane2 = (
        x + n, y - n, z - n,  # bottom-left
        x - n, y - n, z + n,  # bottom-right
        x - n, y + n, z + n,  # top-right  
        x + n, y + n, z - n   # top-left
    )
    
    return (plane1, plane2)
# Slab vertices (half-height cube)
def slab_vertices(pos, n=0.5):
    """Generate vertices for a slab (half-height block)"""
    x, y, z = pos
    
    # Bottom half of a normal cube
    v = tuple((x + X, y + Y, z + Z) for X in (-n, n) for Y in (-n, 0) for Z in (-n, n))
    
    # Return faces: left, right, bottom, top, back, front
    return tuple(tuple(k for j in i for k in v[j]) for i in
                 ((0, 1, 3, 2), (5, 4, 6, 7), (0, 4, 5, 1), (3, 7, 6, 2), (4, 0, 2, 6), (1, 5, 7, 3)))

def stairs_vertices(pos, facing='north', n=0.5):
    """Generate vertices for stairs based on facing direction"""
    x, y, z = pos
    
    if facing == 'north':  # stairs going up towards north
        # Bottom step (full width, half height, half depth)
        bottom_step = [
            # Bottom face
            (x-n, y-n, z-n, x+n, y-n, z-n, x+n, y-n, z, x-n, y-n, z),
            # Top face of bottom step
            (x-n, y, z-n, x+n, y, z-n, x+n, y, z, x-n, y, z),
            # Front face of bottom step
            (x-n, y-n, z-n, x+n, y-n, z-n, x+n, y, z-n, x-n, y, z-n),
            # Back face of bottom step
            (x-n, y-n, z, x+n, y-n, z, x+n, y, z, x-n, y, z),
            # Left face of bottom step
            (x-n, y-n, z-n, x-n, y-n, z, x-n, y, z, x-n, y, z-n),
            # Right face of bottom step
            (x+n, y-n, z-n, x+n, y-n, z, x+n, y, z, x+n, y, z-n)
        ]
        
        # Top step (full width, half height, half depth, offset up and back)
        top_step = [
            # Top face of top step
            (x-n, y+n, z, x+n, y+n, z, x+n, y+n, z+n, x-n, y+n, z+n),
            # Front face of top step
            (x-n, y, z, x+n, y, z, x+n, y+n, z, x-n, y+n, z),
            # Back face of top step
            (x-n, y, z+n, x+n, y, z+n, x+n, y+n, z+n, x-n, y+n, z+n),
            # Left face of top step
            (x-n, y, z, x-n, y, z+n, x-n, y+n, z+n, x-n, y+n, z),
            # Right face of top step
            (x+n, y, z, x+n, y, z+n, x+n, y+n, z+n, x+n, y+n, z)
        ]
        
        return bottom_step + top_step
    
    # Add other facing directions (south, east, west) as needed
    elif facing == 'south':
        # Mirror the north case
        return stairs_vertices((x, y, z), 'north', n)  # Simplified for now
    
    # Default to north for now
    return stairs_vertices((x, y, z), 'north', n)

def door_vertices(pos, facing='north', is_open=False, hinge='left', n=0.5):
    """Generate vertices for a door (thin vertical rectangle)"""
    x, y, z = pos
    thickness = 0.1875  # 3/16 of a block (like Minecraft doors)
    
    if facing == 'north':  # door faces north
        if not is_open:
            # Closed door (thin rectangle along X axis)
            door_faces = [
                # Front face (south side)
                (x-n, y-n, z-thickness, x+n, y-n, z-thickness, x+n, y+n, z-thickness, x-n, y+n, z-thickness),
                # Back face (north side)
                (x-n, y-n, z+thickness, x+n, y-n, z+thickness, x+n, y+n, z+thickness, x-n, y+n, z+thickness),
                # Left face
                (x-n, y-n, z-thickness, x-n, y-n, z+thickness, x-n, y+n, z+thickness, x-n, y+n, z-thickness),
                # Right face
                (x+n, y-n, z-thickness, x+n, y-n, z+thickness, x+n, y+n, z+thickness, x+n, y+n, z-thickness),
                # Top face
                (x-n, y+n, z-thickness, x+n, y+n, z-thickness, x+n, y+n, z+thickness, x-n, y+n, z+thickness),
                # Bottom face
                (x-n, y-n, z-thickness, x+n, y-n, z-thickness, x+n, y-n, z+thickness, x-n, y-n, z+thickness)
            ]
        else:
            # Open door (rotated 90 degrees)
            if hinge == 'left':
                # Door opens to the right (from viewer's perspective)
                door_faces = [
                    # Front face (when open, faces east)
                    (x-thickness, y-n, z-n, x+thickness, y-n, z-n, x+thickness, y+n, z-n, x-thickness, y+n, z-n),
                    # Back face
                    (x-thickness, y-n, z+n, x+thickness, y-n, z+n, x+thickness, y+n, z+n, x-thickness, y+n, z+n),
                    # Left face
                    (x-thickness, y-n, z-n, x-thickness, y-n, z+n, x-thickness, y+n, z+n, x-thickness, y+n, z-n),
                    # Right face
                    (x+thickness, y-n, z-n, x+thickness, y-n, z+n, x+thickness, y+n, z+n, x+thickness, y+n, z-n),
                    # Top face
                    (x-thickness, y+n, z-n, x+thickness, y+n, z-n, x+thickness, y+n, z+n, x-thickness, y+n, z+n),
                    # Bottom face
                    (x-thickness, y-n, z-n, x+thickness, y-n, z-n, x+thickness, y-n, z+n, x-thickness, y-n, z+n)
                ]
            else:
                # Door opens to the left (hinge on right)
                door_faces = [
                    # Similar but mirrored
                    (x-thickness, y-n, z-n, x+thickness, y-n, z-n, x+thickness, y+n, z-n, x-thickness, y+n, z-n),
                    (x-thickness, y-n, z+n, x+thickness, y-n, z+n, x+thickness, y+n, z+n, x-thickness, y+n, z+n),
                    (x-thickness, y-n, z-n, x-thickness, y-n, z+n, x-thickness, y+n, z+n, x-thickness, y+n, z-n),
                    (x+thickness, y-n, z-n, x+thickness, y-n, z+n, x+thickness, y+n, z+n, x+thickness, y+n, z-n),
                    (x-thickness, y+n, z-n, x+thickness, y+n, z-n, x+thickness, y+n, z+n, x-thickness, y+n, z+n),
                    (x-thickness, y-n, z-n, x+thickness, y-n, z-n, x+thickness, y-n, z+n, x-thickness, y-n, z+n)
                ]
    else:
        # For other facings, we'd rotate the coordinates
        # For now, default to north
        return door_vertices(pos, 'north', is_open, hinge, n)
    
    return door_faces


def flatten(lst): return sum(map(list, lst), [])


def roundPos(pos):
    x, y, z = pos
    return round(x), round(y), round(z)


def getSum(s):
    res = 0
    for i in s:
        res += int(i)

    return res


def adjacent(x, y, z):
    for p in ((x - 1, y, z), (x + 1, y, z), (x, y - 1, z), (x, y + 1, z), (x, y, z - 1), (x, y, z + 1)): yield p


def drawInfoLabel(gl, text, xx=0, yy=0, style=None, size=15, anchor_x='left', anchor_y='baseline', opacity=1, rotate=0,
                  label_color=(255, 255, 255), shadow_color=(56, 56, 56), scale=0, shadow=True):
    if style is None:
        style = []
    y = -21
    ms = size / 6
    for i in text.split("\n"):
        ix = ms
        iy = gl.HEIGHT + y + yy - ms
        if xx:
            ix = xx + ms
        if yy:
            iy = yy - ms
        shadow_lbl = pyglet.text.Label(i,
                                       font_name='Minecraft Rus',
                                       color=(shadow_color[0], shadow_color[1], shadow_color[2], round(opacity * 255)),
                                       font_size=size,
                                       x=ix, y=iy,
                                       anchor_x=anchor_x,
                                       anchor_y=anchor_y)
        lbl = pyglet.text.Label(i,
                                font_name='Minecraft Rus',
                                color=(label_color[0], label_color[1], label_color[2], round(opacity * 255)),
                                font_size=size,
                                x=ix - ms, y=iy + ms,
                                anchor_x=anchor_x,
                                anchor_y=anchor_y)
        if not style:
            lbl.set_style("background_color", (69, 69, 69, 100))
        else:
            for st in style:
                lbl.set_style(st[0], st[1])
                shadow_lbl.set_style(st[0], st[1])
        if rotate:
            glRotatef(rotate, 0.0, 0.0, 1.0)
        if scale:
            glScalef(scale, scale, 0)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        if shadow:
            shadow_lbl.draw()
        lbl.draw()
        if rotate:
            glRotatef(-rotate, 0.0, 0.0, 1.0)
        y -= 21


def getElpsTime():
    return time.perf_counter_ns() * 1000 / 1000000000


def checkHover(ox, oy, ow, oh, mx, my):
    if ox < mx < ox + ow and oy < my < oy + oh:
        return True
    return False
