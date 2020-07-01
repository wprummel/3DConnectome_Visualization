# Brain Connectome Visualisation

Contributors: Dr. Juan Prieto (NIRAl, UNC), Dr. Martin Styner, Wieke Prummel (CPE intern at NIRAL, UNC)

## What is it?
BCV (Brain Connectome Visualisation) is programmed in Python and with VTK, CTK and Qt libraries. 
As the name says it is a 3D cisualisation tool of the brain connectome. 
What we call a connectome is the mapping of all neural connections within the brain. 

## How it works?
Each connection is defined by its strength: visually it represents the thickness of the connection between two brain regions (nodes) and this value is found in the matrix given by the user.
The module takes three user inputs:
•	node graph as a Json file
•	node Table (AAL or Destrieux Matrix) that defines the size of each node in the brain regions 
•	normalized connection matrix that defines the thickness of the neural connections

The user can influence properties such as:
•	filter the brain regions to visualize (through search bar)
•	change color and size of nodes
•	change color and size of connections
•	change the connection distribution from default scale to log scale

### Node plotting after Json File and Node Table input
<!-- ![nodes](https://github.com/wprummel/3DConnectome_Visualization/blob/master/doc/node.png?raw=true) -->

![nodes](./docs/nodes.png?raw=true)

### Connections and Nodes after connection matrix input
<!-- ![brain_connectome](https://github.com/wprummel/3DConnectome_Visualization/blob/master/doc/brain_connectome.gif?raw=true) -->

![brain_connectome](./docs/brain_connectome.png?raw=true)

### Default and log connection distribution
<!-- ![connection_distributions](https://github.com/wprummel/3DConnectome_Visualization/blob/master/doc/connection_distributions.gif?raw=true) -->

![connection_distributions](./docs/connection_distributions.png?raw=true)

### Connectome with brain sample data
<!-- ![connectome_sample_data](https://github.com/wprummel/3DConnectome_Visualization/blob/master/doc/connectome_sample_data.gif?raw=true) -->

![connectome_sample_data](./docs/connectome_sample_data.png?raw=true)

## Running the code
Select the "Brain Connectome Visualization" module in Slicer3D. 

### Input files format

#### Json file
This is how the Json file should look like:
<!-- ![sample_json_file](https://github.com/wprummel/3DConnectome_Visualization/blob/master/doc/sample_json_file.gif?raw=true) -->

![sample_json_file](./docs/sample_json_file.png?raw=true)

### Connection matrix
This is how the connection matrix (csv file) should look like:
<!-- ![sample_connection_matrix](https://github.com/wprummel/3DConnectome_Visualization/blob/master/doc/sample_connection_matrix.gif?raw=true) -->

![sample_connection_matrix](./docs/sample_connection_matrix.png?raw=true)

If your csv file is a matrix (only integers), please add a header of string characters in the first row. 

### Tutorial

#### BCV Tutorial (PDF)
<!-- ![BCV_tuto](https://github.com/wprummel/3DConnectome_Visualization/tree/master/doc/BCV_tuto.pdf?raw=true) -->

![BCV_tuto](./docs/BCV_tuto.pdf?raw=true)

#### BCV Tutorial (video)

### Developper Handbook (Readme complement)
<!-- ![BCV_Handbook](https://github.com/wprummel/3DConnectome_Visualization/tree/master/doc/BCV_Handbook.pdf?raw=true) -->

![BCV_Handbook](./docs/BCV_Handbook.pdf?raw=true)
