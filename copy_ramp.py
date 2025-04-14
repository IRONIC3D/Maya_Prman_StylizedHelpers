# This script will allow an artist to copy ramp data from one node to another in the same render type family.
# The script will has a UI for the artist to select the source and target nodes, and the renderer type.
# Once exectured it will copy the just the ramp data from the source node and paste it to the target node without copying the entire node.
# The script will also check if the source and target nodes are of the same renderer type before copying the data.
#
# The current supported render engines are:
#   - RenderMan
#   - 3Delight
#   - Arnold
#   - Maya (this also include RedShift for Maya as RedShift uses Maya native ramp node).

import maya.cmds as cmds

def get_ramp_attribute_data(node, renderer):
    """
    Determines the base name of the ramp attributes based on the node and renderer.
    """
    if renderer == 'RenderMan' and cmds.attributeQuery('colorRamp', node=node, exists=True):
        return 'colorRamp'
    elif renderer == '3Delight' and cmds.attributeQuery('color', node=node, exists=True):
        return 'color'
    elif renderer == 'Arnold' and cmds.attributeQuery('ramp', node=node, exists=True):
        return 'ramp'
    elif renderer == 'Maya' and cmds.attributeQuery('colorEntryList', node=node, exists=True):
        return 'colorEntryList'
    return None

def copy_ramp_data(source_node, renderer):
    """
    Copies ramp data from the source node.
    """
    ramp_base = get_ramp_attribute_data(source_node, renderer)
    if not ramp_base:
        cmds.error(f"Could not find ramp attributes in node: {source_node} (Renderer: {renderer})")
        return None

    ramp_data = []
    if renderer != 'Maya':
        num_entries = cmds.getAttr(f'{source_node}.{ramp_base}', size=True)
        for i in range(num_entries):
            position = cmds.getAttr(f'{source_node}.{ramp_base}[{i}].{ramp_base}_Position')
            value = cmds.getAttr(f'{source_node}.{ramp_base}[{i}].{ramp_base}_Color')[0]
            interpolation = cmds.getAttr(f'{source_node}.{ramp_base}[{i}].{ramp_base}_Interp')
            ramp_data.append({'position': position, 'value': value, 'interpolation': interpolation})
    else:  # Maya ramp
        num_entries = cmds.getAttr(f'{source_node}.{ramp_base}', size=True)
        for i in range(num_entries):
            position = cmds.getAttr(f'{source_node}.{ramp_base}[{i}].position')
            value = cmds.getAttr(f'{source_node}.{ramp_base}[{i}].color')[0]
            interpolation = cmds.getAttr(f'{source_node}.interpolation')
            ramp_data.append({'position': position, 'value': value, 'interpolation': interpolation})
    return ramp_data

def paste_ramp_data(target_node, ramp_data, renderer):
    """
    Pastes ramp data to the target node.
    """
    ramp_base = get_ramp_attribute_data(target_node, renderer)
    if not ramp_base:
        cmds.error(f"Could not find ramp attributes in node: {target_node} (Renderer: {renderer})")
        return

    # Clear existing ramp entries
    num_existing = cmds.getAttr(f'{target_node}.{ramp_base}', size=True)
    if num_existing > 0:
        for i in reversed(range(num_existing)):
            if renderer != 'Maya':
                cmds.removeMultiInstance(f'{target_node}.{ramp_base}[{i}]', b=True)
            else:  # Maya ramp
                cmds.removeMultiInstance(f'{target_node}.{ramp_base}[{i}]', b=True)  # Using the index directly

    # Add the copied ramp entries
    for i, data in enumerate(ramp_data):
        try:
            if renderer != 'Maya':
                cmds.setAttr(f'{target_node}.{ramp_base}[{i}].{ramp_base}_Position', data['position'])
                cmds.setAttr(f'{target_node}.{ramp_base}[{i}].{ramp_base}_Color', *data['value'], type='double3')
                cmds.setAttr(f'{target_node}.{ramp_base}[{i}].{ramp_base}_Interp', data['interpolation'])
            else:  # Maya ramp
                cmds.setAttr(f'{target_node}.{ramp_base}[{i}].position', data['position'])
                cmds.setAttr(f'{target_node}.{ramp_base}[{i}].color', *data['value'], type='double3')
                cmds.setAttr(f'{target_node}.interpolation', data['interpolation'])
        except Exception as e:
            cmds.warning(f"Error setting ramp attribute for index {i}: {e}")
            cmds.warning(f"Attempting to add a new multi-instance for index {i}.")
            try:
                if renderer != 'Maya':
                    cmds.addMultiInstance(f'{target_node}.{ramp_base}', b=True)
                else:
                    cmds.addMultiInstance(f'{target_node}.{ramp_base}', f'{target_node}.{ramp_base}')  # Adding a new entry
                if renderer != 'Maya':
                    cmds.setAttr(f'{target_node}.{ramp_base}[{i}].{ramp_base}_Position', data['position'])
                    cmds.setAttr(f'{target_node}.{ramp_base}[{i}].{ramp_base}_Color', *data['value'], type='double3')
                    cmds.setAttr(f'{target_node}.{ramp_base}[{i}].{ramp_base}_Interp', data['interpolation'])
                else:  # Maya ramp
                    cmds.setAttr(f'{target_node}.{ramp_base}[{i}].position', data['position'])
                    cmds.setAttr(f'{target_node}.{ramp_base}[{i}].color', *data['value'], type='double3')
                    cmds.setAttr(f'{target_node}.interpolation', data['interpolation'])
            except Exception as e2:
                cmds.error(f"Failed to set ramp attribute even after adding multi-instance for index {i}: {e2}")
                return

def get_node_renderer(node):
    """
    Attempts to determine the renderer associated with a node.
    """
    node_type = cmds.nodeType(node)
    if node_type.startswith('Pxr'):
        return 'RenderMan'
    elif node_type.startswith('ai'):
        return 'Arnold'
    elif node_type.startswith('dl'):
        return '3Delight'
    elif node_type == 'ramp':  # Maya ramp nodeType is 'ramp'
        return 'Maya'
    return None

def copy_paste_ramp_ui():
    """
    Creates the UI for copying and pasting ramp data.
    """
    window_id = 'copyPasteRampUI'
    if cmds.window(window_id, exists=True):
        cmds.deleteUI(window_id, window=True)

    cmds.window(window_id, title="Copy/Paste Ramp", sizeable=False)
    cmds.columnLayout(adjustableColumn=True, width=300)

    # Renderer Selection
    cmds.optionMenu('renderer_menu', label='Renderer:')
    cmds.menuItem(label='RenderMan')
    cmds.menuItem(label='Arnold')
    cmds.menuItem(label='3Delight')
    cmds.menuItem(label='Maya')  # Changed from Redshift to Maya

    # Source Node
    cmds.rowLayout(numberOfColumns=2, columnAttach=(1, 'left', 5), columnAlign=(2, 'left'))
    cmds.textField('source_node_field', width=200, text='')
    cmds.button(label='Select Source', command=lambda *args: cmds.textField('source_node_field', edit=True, text=cmds.ls(selection=True)[0] if cmds.ls(selection=True) else ''))
    cmds.setParent('..')

    # Target Node
    cmds.rowLayout(numberOfColumns=2, columnAttach=(1, 'left', 5), columnAlign=(2, 'left'))
    cmds.textField('target_node_field', width=200, text='')
    cmds.button(label='Select Target', command=lambda *args: cmds.textField('target_node_field', edit=True, text=cmds.ls(selection=True)[0] if cmds.ls(selection=True) else ''))
    cmds.setParent('..')

    # Copy/Paste Button
    cmds.button(label='Copy Ramp to Target', command=run_copy_paste_ramp)

    cmds.showWindow(window_id)

def run_copy_paste_ramp(*args):
    """
    Main function to get source and target nodes and execute the copy/paste.
    """
    source_node = cmds.textField('source_node_field', query=True, text=True).strip()
    target_node = cmds.textField('target_node_field', query=True, text=True).strip()
    renderer = cmds.optionMenu('renderer_menu', query=True, value=True)

    if not source_node or not target_node:
        cmds.warning("Please select or enter both a source and a target node.")
        return

    source_renderer = get_node_renderer(source_node)
    target_renderer = get_node_renderer(target_node)

    if source_renderer != renderer or target_renderer != renderer:
        cmds.error(f"Source and target nodes do not appear to be from the selected renderer: {renderer}")
        return

    ramp_data = copy_ramp_data(source_node, renderer)
    if ramp_data:
        paste_ramp_data(target_node, ramp_data, renderer)
        cmds.inViewMessage(amg='<hl>Ramp data copied and pasted successfully!</hl>', pos='midCenter', fade=True)

# Create the UI
copy_paste_ramp_ui()