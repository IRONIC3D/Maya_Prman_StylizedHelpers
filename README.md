# RenderMan Stylized Helper Scripts for Maya

This repo include the following scripts to help with working with RenderMan Stylized Looks in Maya as well as other node wrangling
and copying and pasting that I perform on a regular basis when shading in Maya.

## General Maya shading helper scripts

### Hex to RGB:
This script allows you to apply a hex value to a diffuse channel of a RenderMan, 3delight or Arnold surface

### Copy Ramp
This script allows you to copy only the ramp gradient from one node to another without needing to save the ramp as a preset. This works really well with shading where the ramp is one of a dozen other attributes and you only want to copy the same initial values from one node to another. Works with RenderMan, 3delight, Arnold and Native Maya ramp nodes, which happens to be the nodes supported by RedShift for Maya

## RenderMan Stylized Looks specific helper scripts

### Create PxrManifold2D for PxrStylizedControl
This script will allow you to select an object that has a PxrStylizedControl shader attached and it will create a PxrManifold2D node to it's texCoordinate port

### Select PxrManfold2D from PxrStylizedControl
This script does what the name implies. Selecting an object and executing the script will select only the PxrManfold2D node that is attached to the PxrStylizedControl node. Often times when I'm shading using the PxrStylizedHatching node I tend to set the hatching mapping to Texture Coordinates. Which allows the hatching to attach to a UV coordinates if I have attached a PxrManifold2D node into the PxrStylizedControl. When that happens and there are a dozen objects in the scene, the only way to unify the scaling of the UV frequency/repeat is by modifying the PxrManofold2D node for each object. This is a fast and streamlined way to just select that node and start editing those attributes without needs to open the Hypershade and select the node manually.

### Select PxrStylizedControl
This is similar to the node above, in that it is a fast way to select the attached PxrStylizedControl for any object to start tweaking those render values from within the viewport without the need to open the hypershade and select the node manually.

### Link Artistic Light
This script will allow you to select any RenderMan light, and a PxrStylizedControl and it will create an expression likning the light rotation to the Artici Toon light rotation.