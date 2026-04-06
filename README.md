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


### Study Area
In progress ...

### Data Sources
In progress ...

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
