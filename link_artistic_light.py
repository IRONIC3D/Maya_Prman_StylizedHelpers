# This script will allow an artist to select a Pixar Light and a PxrStylizedControl shader
# and create expressions that link the light rotation to the shader rotation attributes.
# The script will also set the "Convert Unit" to "None" for stability.
# Notice, this will work with PxrSurface nodes only.

import maya.cmds as cmds

def create_rotation_expressions(light_name, shader_name):
    """
    Create expressions that link light rotation to shader rotation attributes.
    Sets "Convert Unit" to "None" for stability.
    
    Args:
        light_name (str): Name of the light
        shader_name (str): Name of the PxrStylizedControl shader
    """
    # Check if objects exist
    if not cmds.objExists(light_name):
        cmds.confirmDialog(title="Error", 
                          message=f"Light '{light_name}' does not exist in the scene.\nPlease check the name and try again.", 
                          button=["OK"])
        return False
        
    if not cmds.objExists(shader_name):
        cmds.confirmDialog(title="Error", 
                          message=f"Shader '{shader_name}' does not exist in the scene.\nPlease check the name and try again.", 
                          button=["OK"])
        return False
    
    # Check if required attributes exist
    for axis in ['X', 'Y', 'Z']:
        if not cmds.attributeQuery(f"rotate{axis}", node=light_name, exists=True):
            cmds.confirmDialog(title="Error", 
                              message=f"Light attribute '{light_name}.rotate{axis}' does not exist.", 
                              button=["OK"])
            return False
            
        if not cmds.attributeQuery(f"Artistic_Light_Rotation{axis}", node=shader_name, exists=True):
            cmds.confirmDialog(title="Error", 
                              message=f"Shader attribute '{shader_name}.Artistic_Light_Rotation{axis}' does not exist.", 
                              button=["OK"])
            return False
    
    # Delete any existing expressions with similar names
    for axis in ['X', 'Y', 'Z']:
        expr_name = f"{shader_name}_rotation{axis}_expr"
        if cmds.objExists(expr_name):
            cmds.delete(expr_name)
    
    # Create expressions for each axis
    for axis in ['X', 'Y', 'Z']:
        expr_string = f"{shader_name}.Artistic_Light_Rotation{axis} = {light_name}.rotate{axis} * 57.2958;"
        expr_name = f"{shader_name}_rotation{axis}_expr"
        
        cmds.expression(name=expr_name, 
                         string=expr_string, 
                         object=shader_name, 
                         alwaysEvaluate=True, 
                         unitConversion="none")
    
    cmds.confirmDialog(title="Success", 
                      message=f"Created expressions linking {light_name} rotation to {shader_name}\nAll expressions have 'Convert Unit' set to 'None'", 
                      button=["OK"])
    return True

def create_gui():
    """
    Create a simple GUI to input light name and shader name
    """
    # Check if window exists and delete it
    if cmds.window("rotationExpressionWindow", exists=True):
        cmds.deleteUI("rotationExpressionWindow")

    # Create window
    window = cmds.window("rotationExpressionWindow",
                        title="Create Rotation Expressions",
                        widthHeight=(400, 150),
                        sizeable=False)

    # Create layout
    main_layout = cmds.columnLayout(adjustableColumn=True, columnAttach=("both", 10))

    cmds.separator(height=10, style="none")
    cmds.text(label="Set light and shader names to create rotation expressions")
    cmds.separator(height=10, style="none")

    # Input fields
    cmds.rowLayout(numberOfColumns=3, columnWidth3=(120, 200, 50), adjustableColumn=2)  # Added a column
    cmds.text(label="Light Name: ")
    light_field = cmds.textField("light_field", width=200)  # Named the textField

    def set_light_field(*args):  # Accept *args (Maya's button command arguments)
        selected = cmds.ls(selection=True)
        if selected:
            cmds.textField("light_field", edit=True, text=selected[0])  # Simply set the first selected
        else:
            cmds.textField("light_field", edit=True, text="")

    cmds.button(label="Select", command=set_light_field)
    cmds.setParent('..')

    cmds.rowLayout(numberOfColumns=3, columnWidth3=(120, 200, 50), adjustableColumn=2)  # Added a column
    cmds.text(label="Shader Name: ")
    shader_field = cmds.textField("shader_field", width=200)  # Named the textField

    def set_shader_field(*args):  # Accept *args (Maya's button command arguments)
        selected = cmds.ls(selection=True)
        if selected:
            cmds.textField("shader_field", edit=True, text=selected[0])  # Simply set the first selected
        else:
            cmds.textField("shader_field", edit=True, text="")

    cmds.button(label="Select", command=set_shader_field)
    cmds.setParent('..')

    cmds.separator(height=15, style="in")

    # Create button
    cmds.button(label="Create Expressions",
                command=lambda x: execute_script(
                    cmds.textField(light_field, query=True, text=True),
                    cmds.textField(shader_field, query=True, text=True)
                ))

    # Show window
    cmds.showWindow(window)

def execute_script(light_name, shader_name):
    """
    Validate inputs and execute the main function
    
    Args:
        light_name (str): Name of the light from the GUI
        shader_name (str): Name of the shader from the GUI
    """
    # Validate that both fields are filled
    if not light_name or not shader_name:
        cmds.confirmDialog(title="Error", 
                          message="Both Light Name and Shader Name fields must be filled.", 
                          button=["OK"])
        return
    
    # Execute the main function
    create_rotation_expressions(light_name, shader_name)

# Create the GUI when the script is run
create_gui()