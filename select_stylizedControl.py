# This script will select for the PxrStylizedControl for the selected object
# Notice, this will work with PxrSurface nodes only.

import maya.cmds as cmds

# Get the currently selected object
selected_objects = cmds.ls(selection=True, dag=True, leaf=True, noIntermediate=True, shapes=True)
if not selected_objects:
    print("No object selected.")
else:
    selected_object = selected_objects[0]

    # Check if the shape node has a shading group attached
    shading_groups = cmds.listConnections(selected_object, type='shadingEngine')
    if not shading_groups:
        print("No shading group found for selected object.")
    else:
        shading_group = shading_groups[0]

        # Check if the shading group has a PxrSurface shading node connected to its 'rman__surface'
        connected_nodes = cmds.listConnections(shading_group + '.rman__surface', type='PxrSurface')
        if not connected_nodes:
            connected_nodes = cmds.listConnections(shading_group + '.surfaceShader', type='PxrSurface')

        if not connected_nodes:
            print('No PxrSurface shading node found')
        else:
            pxr_surface_node = connected_nodes[0]

            # Check if there is a PxrStylizedControl node connected to the utilityPattern port
            connected_nodes = cmds.listConnections(pxr_surface_node + '.utilityPattern')
            pxr_stylized_control_node = None
            if connected_nodes is not None:
                for node in connected_nodes:
                    if cmds.nodeType(node) == 'PxrStylizedControl':
                        pxr_stylized_control_node = node
                        break

            # If a PxrStylizedControl node is connected
            if pxr_stylized_control_node:
                # Select the PxrStylizedControl node
                cmds.select(pxr_stylized_control_node, replace=True)
            else:
                print('No proper PxrStylizedControl is connected to PxrSurface')
