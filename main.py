bl_info = {
    "name": "CityGen Pro",
    "author": "Ombay & AI Assistant",
    "version": (1, 0),
    "blender": (3, 6, 0),
    "location": "View3D > N-Panel > City Gen",
    "description": "Generate Modular City with Auto-Roads",
    "category": "Object",
}

import bpy
import random
import math

# --- CORE LOGIC ---

def get_road_type(neighbors):
    """Logika Bitmasking untuk Jalan"""
    n, e, s, w = neighbors
    mask = (n * 1) + (e * 2) + (s * 4) + (w * 8)
    
    # Return format: (Type_Suffix, Rotation_Radians)
    # Mapping sesuai diskusi sebelumnya:
    # Straight: Utara-Selatan (0), Timur-Barat (90)
    # Corner: L (Utara-Timur)
    # T: T (Barat-Timur-Selatan)
    
    rad0 = 0
    rad90 = math.radians(90)
    rad180 = math.radians(180)
    rad270 = math.radians(270) # atau -90

    # 1 Koneksi (Buntu)
    if mask == 1: return ("Straight", rad0)
    if mask == 2: return ("Straight", rad90)
    if mask == 4: return ("Straight", rad0)
    if mask == 8: return ("Straight", rad90)
    
    # 2 Koneksi (Lurus)
    if mask == 5: return ("Straight", rad0)   # N+S
    if mask == 10: return ("Straight", rad90) # E+W
    
    # 2 Koneksi (Belokan)
    if mask == 3: return ("Corner", rad0)     # N+E
    if mask == 6: return ("Corner", rad270)   # E+S
    if mask == 12: return ("Corner", rad180)  # S+W
    if mask == 9: return ("Corner", rad90)    # W+N
    
    # 3 Koneksi (T-Junction)
    if mask == 14: return ("T", rad0)    # E+S+W (Default T bawah)
    if mask == 11: return ("T", rad90)   # N+E+W (Rotasi 90 CCW)
    if mask == 7: return ("T", rad180)   # N+E+S (T Atas)
    if mask == 13: return ("T", rad270)  # N+S+W (T Kiri)

    # 4 Koneksi (Cross)
    if mask == 15: return ("Cross", rad0)
    
    return None

def generate_city(context):
    props = context.scene.city_gen_props
    
    # 1. Validasi Collections
    road_col = bpy.data.collections.get(props.road_collection)
    bldg_col = bpy.data.collections.get(props.building_collection)
    
    if not road_col or not bldg_col:
        return {'CANCELLED'}

    # 2. Cleanup Old City
    coll_name = "Generated_City_Pro"
    if coll_name in bpy.data.collections:
        coll = bpy.data.collections[coll_name]
        for obj in coll.objects:
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(coll)
        
    final_coll = bpy.data.collections.new(coll_name)
    context.scene.collection.children.link(final_coll)
    
    # 3. Setup Grid Map (0=Building, 1=Road)
    size_x = props.size_x
    size_y = props.size_y
    grid = [[0 for _ in range(size_y)] for _ in range(size_x)]
    
    # Create Road Pattern (Grid sederhana)
    for x in range(size_x):
        for y in range(size_y):
            if x % props.road_interval == 0 or y % props.road_interval == 0:
                grid[x][y] = 1

    # 4. Generate Objects
    random.seed(props.seed)
    
    assets_road = {
        "Straight": road_col.objects.get("Road_Straight"),
        "Corner": road_col.objects.get("Road_Corner"),
        "T": road_col.objects.get("Road_T"),
        "Cross": road_col.objects.get("Road_Cross"),
    }
    
    buildings = [obj for obj in bldg_col.objects]

    for x in range(size_x):
        for y in range(size_y):
            loc_x = x * props.block_size
            loc_y = y * props.block_size
            
            # --- JIKA JALAN ---
            if grid[x][y] == 1:
                # Cek Tetangga
                n = grid[x][y+1] if y+1 < size_y else 0
                e = grid[x+1][y] if x+1 < size_x else 0
                s = grid[x][y-1] if y-1 >= 0 else 0
                w = grid[x-1][y] if x-1 >= 0 else 0
                
                res = get_road_type((n,e,s,w))
                if res:
                    r_type, r_rot = res
                    src = assets_road.get(r_type)
                    if src:
                        inst = bpy.data.objects.new(f"Road_{x}_{y}", src.data)
                        inst.location = (loc_x, loc_y, 0)
                        inst.rotation_euler = (0, 0, r_rot)
                        final_coll.objects.link(inst)
            
            # --- JIKA GEDUNG ---
            else:
                if buildings and random.random() < props.density:
                    src = random.choice(buildings)
                    inst = bpy.data.objects.new(f"Bldg_{x}_{y}", src.data)
                    inst.location = (loc_x, loc_y, 0)
                    
                    # Random Rotation (0, 90, 180, 270)
                    rot_deg = random.choice([0, 90, 180, 270])
                    inst.rotation_euler = (0, 0, math.radians(rot_deg))
                    
                    final_coll.objects.link(inst)

    return {'FINISHED'}

# --- UI & PROPERTIES ---

class CityGenProperties(bpy.types.PropertyGroup):
    size_x: bpy.props.IntProperty(name="Size X", default=15, min=2, max=100)
    size_y: bpy.props.IntProperty(name="Size Y", default=15, min=2, max=100)
    block_size: bpy.props.FloatProperty(name="Block Size", default=4.0, description="Size of one tile in meters")
    road_interval: bpy.props.IntProperty(name="Road Interval", default=3, min=2, description="Place road every N blocks")
    density: bpy.props.FloatProperty(name="Building Density", default=0.8, min=0.0, max=1.0)
    seed: bpy.props.IntProperty(name="Random Seed", default=42)
    
    # String inputs for collection names
    road_collection: bpy.props.StringProperty(name="Road Collection", default="My_Roads")
    building_collection: bpy.props.StringProperty(name="Bldg Collection", default="My_Buildings")

class CITYGEN_OT_Generate(bpy.types.Operator):
    """Generate the City"""
    bl_idname = "citygen.generate"
    bl_label = "Generate City"
    
    def execute(self, context):
        return generate_city(context)

class CITYGEN_PT_Panel(bpy.types.Panel):
    """City Gen UI Panel"""
    bl_label = "City Generator"
    bl_idname = "CITYGEN_PT_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'City Gen'

    def draw(self, context):
        layout = self.layout
        props = context.scene.city_gen_props

        box = layout.box()
        box.label(text="Settings")
        box.prop(props, "size_x")
        box.prop(props, "size_y")
        box.prop(props, "block_size")
        
        box = layout.box()
        box.label(text="Pattern")
        box.prop(props, "road_interval")
        box.prop(props, "density")
        box.prop(props, "seed")

        box = layout.box()
        box.label(text="Assets (Collection Name)")
        box.prop(props, "road_collection", icon='OUTLINER_COLLECTION')
        box.prop(props, "building_collection", icon='OUTLINER_COLLECTION')

        layout.separator()
        layout.operator("citygen.generate", icon='MOD_BUILD')

# --- REGISTRATION ---

classes = (CityGenProperties, CITYGEN_OT_Generate, CITYGEN_PT_Panel)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.city_gen_props = bpy.props.PointerProperty(type=CityGenProperties)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.city_gen_props

if __name__ == "__main__":
    register()
