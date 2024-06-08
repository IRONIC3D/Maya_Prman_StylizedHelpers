# This script will look for the PxrStylizedControl node that is connected to PxrSurface and applied
# a PxrManifold2D and a PxrToFloat3 node to the PxrStylizedControl textureCoordinates port
# to allow for the PxrStylizedHatching to use TextureCoordinates for the hatching instead of Triplanar
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
        
        # If no connection found, check for 'surfaceShader' connection
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
                # Check if there is a node connected to its inputTextureCoords
                connected_nodes = cmds.listConnections(pxr_stylized_control_node + '.inputTextureCoords')
                if connected_nodes is None:
                    # Create and connect the nodes
                    pxr_manifold_2D_node = cmds.shadingNode('PxrManifold2D', asUtility=True)
                    pxr_to_float_3_node = cmds.shadingNode('PxrToFloat3', asUtility=True)
                    cmds.connectAttr(pxr_manifold_2D_node + '.resultS', pxr_to_float_3_node + '.inputR')
                    cmds.connectAttr(pxr_manifold_2D_node + '.resultT', pxr_to_float_3_node + '.inputG')
                    cmds.connectAttr(pxr_to_float_3_node + '.resultRGB', pxr_stylized_control_node + '.inputTextureCoords')
                else:
                    print('A node is already connected to PxrStylizedControl inputTextureCoords')
            else:
                print('No proper PxrStylizedControl is connected to PxrSurface')
