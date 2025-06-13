from OpenGL.GL import *

from functions import *
from game.blocks.Cube import Cube



class CubeHandler:
    top_color = ('c3f', (1.0,) * 12)
    ns_color = ('c3f', (0.8,) * 12)
    ew_color = ('c3f', (0.6,) * 12)
    bottom_color = ('c3f', (0.5,) * 12)

    def __init__(self, batch, block, opaque, alpha_textures, gl):
        self.batch, self.block, self.alpha_textures, self.opaque = batch, block, alpha_textures, opaque
        self.cubes = {}
        self.transparent = gl.transparent
        self.gl = gl
        self.fluids = {}
        self.collidable = {}
        self.collidable_slabs = {}
        self.collidable_stairs = {}
        '''self.top_color = ('c3f', (0.1,) * 12)
        self.ns_color = ('c3f', (0.1,) * 12)
        self.ew_color = ('c3f', (0.1,) * 12)
        self.bottom_color = ('c3f', (0.1,) * 12)'''

        self.color = True

    def hitTest(self, p, vec, dist=4):
        m = 8
        x, y, z = p
        dx, dy, dz = vec
        dx /= m
        dy /= m
        dz /= m
        prev = None
        for i in range(dist * m):
            key = roundPos((x, y, z))
            if key in self.cubes and key not in self.fluids:
                return key, prev
            prev = key
            x, y, z = x + dx, y + dy, z + dz
        return None, None

    def show(self, v, t, i, clrC=None):
        if not clrC:
            if self.color:
                if i == "left" or i == "front":
                    clr = self.ns_color
                if i == "right" or i == "back":
                    clr = self.ew_color
                if i == "bottom":
                    clr = self.bottom_color
                if i == "top":
                    clr = self.top_color
        else:
            clr = clrC[i]

        return self.opaque.add(4, GL_QUADS, t, ('v3f', v), ('t2f', (0, 0, 1, 0, 1, 1, 0, 1)), clr)
    def _validate_texture(self, tex):
        """Ensure textures are usable before rendering"""
        if isinstance(tex, (tuple, list)):
            print(f"Warning: Texture is a tuple/list! Converting first element. Full tex: {tex}")
            return tex[0]  # Use first texture in tuple as fallback
        elif hasattr(tex, 'parent'):  # Already a valid TextureGroup
            return tex
        else:
            raise ValueError(f"Invalid texture type: {type(tex)}. Expected TextureGroup or tuple/list")
    def updateCube(self, cube, customColor=None):
        if cube.is_plant:
            # Handle plant rendering
            if not cube.plant_faces:
                v = plant_vertices(cube.p)
                cube.plant_faces = self.show_plant(v, cube.t[0] if isinstance(cube.t, list) else cube.t)
            return
    
        if cube.is_door:
            # Handle door rendering
            if not hasattr(cube, 'door_faces') or not cube.door_faces:
                v = door_vertices(cube.p, cube.door_facing, cube.door_open, cube.door_hinge)
                cube.door_faces = self.show_door(v, cube.t[0] if isinstance(cube.t, list) else cube.t)
            return
    
        if cube.is_slab:
            # Handle slab collision - half-height blocks
            shown = any(cube.shown.values())
            if shown:
                if (cube.name != 'water' and cube.name != 'lava') and cube.p not in self.collidable_slabs:
                    self.collidable_slabs[cube.p] = cube
                    print(f"Added slab at {cube.p} to collidable_slabs")
            else:
                if cube.p in self.collidable_slabs:
                    print(f"removed slab at {cube.p} to collidable_slabs")
                    del self.collidable_slabs[cube.p]
                return
            # Handle slab rendering
            if not hasattr(cube, 'slab_faces_rendered') or not cube.slab_faces_rendered:
                v = slab_vertices(cube.p)
                cube.slab_faces_rendered = True
            
                # Render slab faces that should be shown
                show = self.show_slab
                f = 'left', 'right', 'bottom', 'top', 'back', 'front'
                for i in (0, 1, 2, 3, 4, 5):
                    if cube.shown[f[i]] and not cube.faces[f[i]]:
                        cube.faces[f[i]] = show(v[i], cube.t[i] if isinstance(cube.t, list) else cube.t, f[i], clrC=customColor)
            return
    
        if cube.is_stairs:  
            # Handle stairs collision - stepped blocks
            shown = any(cube.shown.values())
            if shown:
                if (cube.name != 'water' and cube.name != 'lava') and cube.p not in self.collidable_stairs:
                    self.collidable_stairs[cube.p] = cube
                    print(f"Added stair at {cube.p} to collidable_slabs")
            else:
                if cube.p in self.collidable_stairs:
                    del self.collidable_stairs[cube.p]
                    print(f"Removed stair at {cube.p} from collidable_slabs")
                return
            # Handle stairs rendering
            if not hasattr(cube, 'stairs_faces') or not cube.stairs_faces:
                v = stairs_vertices(cube.p, cube.stairs_facing)
                cube.stairs_faces = self.show_stairs(v, cube.t[0] if isinstance(cube.t, list) else cube.t)
            return
    
        # Regular cube logic (unchanged)
        shown = any(cube.shown.values())
        if shown:
            if (cube.name != 'water' and cube.name != 'lava') and cube.p not in self.collidable:
                self.collidable[cube.p] = cube
        else:
            if cube.p in self.collidable:
                del self.collidable[cube.p]
            return









        show = self.show
        v = cube_vertices(cube.p)
        f = 'left', 'right', 'bottom', 'top', 'back', 'front'
        for i in (0, 1, 2, 3, 4, 5):
            if cube.shown[f[i]] and not cube.faces[f[i]]:
                cube.faces[f[i]] = show(v[i], cube.t[i], f[i], clrC=customColor)
            elif customColor:
                if cube.color[f[i]] != customColor[f[i]]:
                    if cube.shown[f[i]]:
                        cube.faces[f[i]].delete()
                        cube.faces[f[i]] = show(v[i], cube.t[i], f[i], clrC=customColor)
                    cube.color[f[i]] = customColor[f[i]]

    def set_adj(self, cube, adj, state):
        x, y, z = cube.p
        X, Y, Z = adj
        d = X - x, Y - y, Z - z
        f = 'left', 'right', 'bottom', 'top', 'back', 'front'
        for i in (0, 1, 2):
            if d[i]:
                j = i + i
                a, b = [f[j + 1], f[j]][::d[i]]
                cube.shown[a] = state
                if not state and cube.faces[a]:
                    cube.faces[a].delete()
                    face = cube.faces[a]
                    cube.faces[a] = None

    def add(self, p, t, now=False, facing='north'):
        if p in self.cubes:
            return
        cube = self.cubes[p] = Cube(t, p, self.block[t],
                                    'alpha' if t in self.alpha_textures else 'blend' if (t == 'water' or t == "lava")
                                    else 'solid')
    
        # Set stairs facing direction if it's a stairs block
        if cube.is_stairs:
            cube.stairs_facing = facing
    
        # Handle adjacency logic
        for adj in adjacent(*cube.p):
            if adj not in self.cubes:
                # For slabs and stairs, we might want different adjacency rules
                if cube.is_slab or cube.is_stairs:
                    # Slabs and stairs always show their faces (no culling for now)
                    self.set_adj(cube, adj, True)
                else:
                    self.set_adj(cube, adj, True)
            else:
                adj_cube = self.cubes[adj]
                a, b = cube.type, adj_cube.type
            
                # Special case: don't cull faces between slabs/stairs and other blocks
                if cube.is_slab or cube.is_stairs or adj_cube.is_slab or adj_cube.is_stairs:
                    self.set_adj(cube, adj, True)
                    self.set_adj(adj_cube, cube.p, True)
                else:
                    # Regular adjacency logic for normal blocks
                    if a == b and (a == 'solid' or b == 'blend'):
                        self.set_adj(adj_cube, cube.p, False)
                    elif a != 'blend' and b != 'solid':
                        self.set_adj(adj_cube, cube.p, False)
                        self.set_adj(cube, adj, True)
            
                if now:
                    self.updateCube(adj_cube)
    
        if now:
            self.updateCube(cube)

    def remove(self, p):
        if p not in self.cubes:
            return
        if self.cubes[p].name == "bedrock":
            return
        if p in self.fluids:
            self.fluids.pop(p)
        if p in self.collidable:
           self.collidable.pop(p)
    
        cube = self.cubes.pop(p)

        # Handle plant removal
        if cube.is_plant:
            if cube.plant_faces:
                for face in cube.plant_faces:
                    if face:
                        face.delete()
    
        # Handle door removal
        elif cube.is_door:
            if hasattr(cube, 'door_faces') and cube.door_faces:
                for face in cube.door_faces:
                    if face:
                        face.delete()
        
            # Remove the other half of the door
            x, y, z = p
            other_half_pos = None
            if cube.door_half == 'lower':
                other_half_pos = (x, y + 1, z)
            else:
                other_half_pos = (x, y - 1, z)
        
            if other_half_pos and other_half_pos in self.cubes:
                other_cube = self.cubes[other_half_pos]
                if other_cube.is_door:
                    if hasattr(other_cube, 'door_faces') and other_cube.door_faces:
                        for face in other_cube.door_faces:
                            if face:
                                face.delete()
                    del self.cubes[other_half_pos]
                
                    # Update adjacency for the other half
                    for adj in adjacent(*other_half_pos):
                        if adj in self.cubes:
                            self.set_adj(self.cubes[adj], other_half_pos, True)
                            self.updateCube(self.cubes[adj])
    
        # Handle stairs removal
        elif cube.is_stairs:
            if hasattr(cube, 'stairs_faces') and cube.stairs_faces:
                for face in cube.stairs_faces:
                    if face:
                        face.delete()
    
        elif cube.is_slab:  # <-- Explicit slab handling
            if hasattr(cube, 'faces') and cube.faces:
                f = 'left', 'right', 'bottom', 'top', 'back', 'front'
                for face_name in cube.collidable_slabs:
                    if cube.faces[face_name]:
                        cube.faces[face_name].delete()
                        cube.faces[face_name] = None
    
            # Reset the rendering flag so it can be re-rendered if needed
            if hasattr(cube, 'slab_faces_rendered'):
                cube.slab_faces_rendered = False
                    
    
        # Handle regular block removal
        else:
            for side, face in cube.faces.items():
                if face:
                    face.delete()
                cube.shown[side] = False
    
        # Update adjacent blocks
        for adj in adjacent(*p):
            if adj in self.cubes:
                self.set_adj(self.cubes[adj], p, True)
                self.updateCube(self.cubes[adj])

    def show_plant(self, v, t):
        """Render plant as two intersecting planes instead of cube"""
        faces = []
        texture = self._validate_texture(t)
        for plane_verts in v:
            # Each plane gets rendered twice (front and back faces)
            face = self.transparent.add(4, GL_QUADS, texture, 
                                      ('v3f', plane_verts), 
                                      ('t2f', (0, 0, 1, 0, 1, 1, 0, 1)))
            faces.append(face)
    
        return faces
    def show_slab(self, v, t, i, clrC=None):
        """Render slab faces - same as regular cube but with slab vertices"""
        texture = self._validate_texture(t)
        if not clrC:
            if self.color:
                if i == "left" or i == "front":
                    clr = self.ns_color
                if i == "right" or i == "back":
                    clr = self.ew_color
                if i == "bottom":
                    clr = self.bottom_color
                if i == "top":
                    clr = self.top_color
        else:
            clr = clrC[i]

        return self.opaque.add(4, GL_QUADS, texture, ('v3f', v), ('t2f', (0, 0, 1, 0, 1, 1, 0, 1)), clr)
    def show_stairs(self, faces_list, t):
        """Render stairs as multiple faces"""
        rendered_faces = []
        texture = self._validate_texture(t)
        for face_verts in faces_list:
            face = self.opaque.add(4, GL_QUADS, texture, 
                                 ('v3f', face_verts), 
                                 ('t2f', (0, 0, 1, 0, 1, 1, 0, 1)),
                                 self.top_color)  # Use consistent color for now
            rendered_faces.append(face)
    
        return rendered_faces
    def show_door(self, faces_list, t):
        """Render door as multiple faces (for both closed and open states)"""
        rendered_faces = []
        texture = self._validate_texture(t)
    
        for face_verts in faces_list:
            # Each face of the door gets rendered with the appropriate texture
            face = self.opaque.add(4, GL_QUADS, texture,
                                 ('v3f', face_verts),
                                 ('t2f', (0, 0, 1, 0, 1, 1, 0, 1)),
                                 self.top_color)  # Using top color for doors
            rendered_faces.append(face)
    
        return rendered_faces
    # Door interaction methods for CubeHandler:
    def toggle_door(self, pos):
        """Toggle a door between open and closed"""
        if pos not in self.cubes:
            return False
    
        cube = self.cubes[pos]
        if not cube.is_door:
            return False
    
        # Toggle the door state
        cube.door_open = not cube.door_open
    
        # Find the other half of the door
        x, y, z = pos
        other_half_pos = None
    
        if cube.door_half == 'lower':
            other_half_pos = (x, y + 1, z)
        else:
            other_half_pos = (x, y - 1, z)
    
        # Update both halves
        if other_half_pos in self.cubes and self.cubes[other_half_pos].is_door:
            other_cube = self.cubes[other_half_pos]
            other_cube.door_open = cube.door_open
        
            # Re-render both halves
            self._refresh_door(cube)
            self._refresh_door(other_cube)
        else:
            # Just update this half
            self._refresh_door(cube)
    
        return True

    def _refresh_door(self, cube):
        """Refresh door rendering after state change"""
        # Delete old faces
        if hasattr(cube, 'door_faces') and cube.door_faces:
            for face in cube.door_faces:
                if face:
                    face.delete()
    
        # Re-render with new state
        v = door_vertices(cube.p, cube.door_facing, cube.door_open, cube.door_hinge)
        cube.door_faces = self.show_door(v, cube.t[0] if isinstance(cube.t, list) else cube.t)

    def place_door(self, pos, door_type, facing='north', hinge='left'):
        """Place a complete door (both upper and lower halves)"""
        x, y, z = pos
        lower_pos = (x, y, z)
        upper_pos = (x, y + 1, z)
    
        # Check if both positions are free
        if lower_pos in self.cubes or upper_pos in self.cubes:
            return False
    
        # Place lower half
        self.add(lower_pos, f"{door_type}_door_lower", now=False, facing=facing)
        if lower_pos in self.cubes:
            lower_cube = self.cubes[lower_pos]
            lower_cube.door_half = 'lower'
            lower_cube.door_facing = facing
            lower_cube.door_hinge = hinge
    
        # Place upper half  
        self.add(upper_pos, f"{door_type}_door_upper", now=False, facing=facing)
        if upper_pos in self.cubes:
            upper_cube = self.cubes[upper_pos]
            upper_cube.door_half = 'upper'
            upper_cube.door_facing = facing
            upper_cube.door_hinge = hinge
    
        # Update both halves
        if lower_pos in self.cubes:
            self.updateCube(self.cubes[lower_pos])
        if upper_pos in self.cubes:
            self.updateCube(self.cubes[upper_pos])
    
        return True
