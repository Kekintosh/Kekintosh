class Cube:
    def __init__(self, name, p, t, typ):
        self.name, self.p, self.t, self.type = name, p, t, typ
        self.color = {'left': None, 'right': None, 'bottom': None, 'top': None, 'back': None, 'front': None}
        self.shown = {'left': False, 'right': False, 'bottom': False, 'top': False, 'back': False, 'front': False}
        self.faces = {'left': None, 'right': None, 'bottom': None, 'top': None, 'back': None, 'front': None}
        # Add special block type attributes
        self.plant_faces = None
        self.is_plant = name in ('tall_grass', 'allium', 'poppy', 'oak_sapling')
        self.is_slab = name.endswith('_slab')
        self.is_stairs = name.endswith('_stairs')
        self.is_door = '_door_' in name or name.endswith('_door')
        # For stairs, we need to know orientation (will be set later)
        self.stairs_facing = 'north'  # default, should be set when placing
        # For doors
        self.door_facing = 'north'  # which way the door faces
        self.door_half = 'lower'    # 'lower' or 'upper'
        self.door_open = False      # is the door open?
        self.door_hinge = 'left'    # 'left' or 'right' hinge
