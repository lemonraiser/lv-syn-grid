# lv-syn-grid
An algorithmic approach for synthesizing realistic low-voltage distribution grids from spatial data using graph-based methods.

### Overview
This python-based tool provides an algorithmic workflow for generating synthetic low-voltage distribution grids from Open Data. Using publicly available OpenStreetMap data, the tool extracts buildings and road networks, estimates electricity demand, derives a radial grid topology with graph-based methods, places transformers, and builds a pandapower network model for power flow and time-series simulations.

### Core Features
- **Automated low-voltage grid synthesis**<br>
  Generation of low-voltage distribution networks based on publicly available geospatial data (e.g., OpenStreetMap, statistical data.
- **Demand estimation based on building data**<br>
  Estimation of electrical loads using building footprints, usage types, and attributes such as floor area and estimated bulding height.
- **Transformer Placement via Clustering**<br>
  Automatic sizing and placement of transformers based on load estimation using the K-Means algorithm.
- **Graph based network construction**<br>
  Representation of the network model using graph theory. A minimum spanning tree (MST) is applied to derive radial grid topologies typical for rural low-voltage grids.
- **Photovoltaic (PV) integration**<br>
Integration of PV systems into the synthesized grid model for simulation.
- **Load flow calculation**<br>
Automatic conversion of the generated graph into a pandapower model, enabling load flow and time series simulations. For the simulation of grid behavior over time standardized load profiles are used, allowing analysis of voltage levels, line loading.
- **Geospatial visualization**<br>
Visualization of networks, loads, and simulation results on geographic maps, enabling intuitive analysis.

### Study Area
Within the scope of the thesis, see section Citation, three rural regions in Lower Austria (Niederösterreich) were selected as case studies. Those areas were chosen primarily due to the availability of data required for model validation.<br>
<br>
While the implemented algorithm is demonstrated using these specific regions, it also can be applied to other geographical areas by adapting input data and parameters.

### Data Sources & Preprocessing
<ins>Main Data Sources:</ins><br>
The model is based on a combination of **geospatial, infrastructural, and statistical open data**. The primary data source consists of building and infrastructure data, which form the basis for network synthesis and load estimation.<br>
- **OpenStreetMap (OSM)**<br>
  Provides geospatial data such as:<br>
  - Building footprints (basis for load allocation)
  - Road networks (used for graph construction)
- **Building-related Data**<br>
  Additional attributes (e.g., building height or type) are used to improve load estimation by enabling approximations of usable floor area
- **Statistical Data**<br>
  Used for scaling and distribution of loads and generation:<br>
  - Population data
  - Regional energy statistics (e.g., PV capacity)
- **Photovoltaic Data**<br>
Locations of PV systems are derived and processed, with typical system parameters (e.g., 12 kWp per installation) assumed for modelling
- **Standardized Load Profiles**<br>
Used to model time-dependent electricity demand for different consumer types

<ins>Preprocessing Steps:</ins><br>
abc def

### Prerequisites
In progress ...

### Quick Start
In progress ...

### Scientific Background
This tool was developed as part of a master’s thesis at Vienna University of Technology (TU Wien). Further details on the methodology, assumptions, and results of the
presented approach for a selected set of rural areas can be found in the corresponding thesis: [Open-Data basierte Synthese bestehender Niederspannungsnetze ruraler Gebiete](https://repositum.tuwien.at/handle/20.500.12708/223910)

# License
This project is licensed under the MIT License.<br>
Please see the [LICENSE](LICENSE.txt) file for details.

# Citation
If you use this code in a scientific publication, please cite the associated thesis:
- Seiler, R. (2025). [Open-Data basierte Synthese bestehender Niederspannungsnetze ruraler Gebiete](https://repositum.tuwien.at/handle/20.500.12708/223910)
