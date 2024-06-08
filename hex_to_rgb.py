import maya.cmds as cmds

applied_color = False

def hex_to_rgb(hex_value):
    hex_value = hex_value.lstrip('#')
    return tuple(int(hex_value[i:i+2], 16) for i in (0, 2, 4))

def apply_hex_color(hex_value, shader_type, color_slot):
    rgb_values = hex_to_rgb(hex_value)
    rgb_normalized = [x / 255.0 for x in rgb_values]
    
    selected_objects = cmds.ls(selection=True)
    if not selected_objects:
        print("No objects selected.")
        return

    for obj in selected_objects:
        shading_groups = []
        if cmds.nodeType(obj) == 'shadingEngine':
            shading_groups = [obj]
        else:
            shading_groups = cmds.listConnections(obj, type='shadingEngine')

        if not shading_groups:
            print(f"No shading group connected to {obj}.")
            continue

        for shading_group in shading_groups:
            shaders = cmds.listConnections(shading_group, type=shader_type)
            if not shaders:
                print(f"No {shader_type} shader connected to {shading_group}.")
                continue

            shader = shaders[0]
            cmds.setAttr(f"{shader}.{color_slot}", *rgb_normalized, type="double3")

def on_apply_color_button_click(*args):
    global applied_color
    hex_value = cmds.textFieldGrp(hex_value_field, query=True, text=True)
    shader_type = cmds.optionMenuGrp(shader_type_field, query=True, value=True)
    color_slot = cmds.optionMenuGrp(color_slot_field, query=True, value=True)
    apply_hex_color(hex_value, shader_type, color_slot)
    applied_color = True

def update_color_slots(*args):
    global applied_color
    if applied_color:
        cmds.warning("Please re-run the script after switching the shader type to avoid errors.")
    
    shader_type = cmds.optionMenuGrp(shader_type_field, query=True, value=True)
    color_slot_options = shader_color_slots[shader_type]
    global color_slot_field
    old_color_slot_field = color_slot_field
    color_slot_field = cmds.optionMenuGrp(label="Color Slot")
    for option in color_slot_options:
        cmds.menuItem(label=option)
    cmds.formLayout(form_layout, edit=True, attachControl=[(color_slot_field, 'left', 5, shader_type_field), (color_slot_field, 'top', 5, hex_value_field)])
    cmds.deleteUI(old_color_slot_field)


def create_ui():
    window_name = "hexColorPicker"
    if cmds.window(window_name, exists=True):
        cmds.deleteUI(window_name)

    cmds.window(window_name, title="Hex Color Picker", sizeable=False)
    global form_layout
    form_layout = cmds.formLayout()

    global hex_value_field, shader_type_field, color_slot_field
    hex_value_field = cmds.textFieldGrp(label="Hex Value", text="#FF5733")
    shader_type_field = cmds.optionMenuGrp(label="Shader Type", changeCommand=update_color_slots)

    cmds.menuItem(label="aiStandardSurface")
    cmds.menuItem(label="PxrSurface")
    cmds.menuItem(label="dlPrincipled")

    color_slot_field = cmds.optionMenuGrp(label="Color Slot")

    global shader_color_slots
    shader_color_slots = {
        "aiStandardSurface": ["baseColor", "specularColor", "transmissionColor", "transmissionScatter", "subsurfaceColor", "subsurfaceRadius", "coatColor", "sheenColor", "emissionColor", "opacity"],
        "PxrSurface": ["diffuseColor", "specularFaceColor", "specularEdgeColor", "clearcoatFaceColor", "clearcoatEdgeColor", "subsurfaceColor", "singlescatterColor", "irradianceTint", "refractionColor"],
        "dlPrincipled": ["color", "coating_color", "sss_color", "refract_color", "refract_scattering_color", "incandescence"]
    }

    # Set initial color slots based on the default shader type
    initial_shader_type = cmds.optionMenuGrp(shader_type_field, query=True, value=True)
    for option in shader_color_slots[initial_shader_type]:
        cmds.menuItem(label=option)

    apply_color_button = cmds.button(label="Apply Color", command=on_apply_color_button_click)
    cmds.formLayout(form_layout, edit=True, 
                attachForm=[(hex_value_field, 'left', 5), (hex_value_field, 'top', 5),
                            (shader_type_field, 'left', 5), 
                            (apply_color_button, 'left', 5), (apply_color_button, 'bottom', 5),
                            (apply_color_button, 'right', 5)],
                attachControl=[(shader_type_field, 'top', 5, hex_value_field),
                               (color_slot_field, 'left', 5, shader_type_field), (color_slot_field, 'top', 5, hex_value_field)])


    cmds.showWindow(window_name)

if __name__ == "__main__":
    create_ui()

