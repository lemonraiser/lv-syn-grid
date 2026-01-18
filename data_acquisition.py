class DataAcquisitionInfrastructure:
    """
    Handles data acquisition and data preparation.
    """
    def __init__(self):
        #self.__debug = False
        #self.__S = gp.GeoDataFrame()
        #self.__S_proj = gp.GeoDataFrame()

        #self.__B = gp.GeoDataFrame()
        #self.__B_proj = gp.GeoDataFrame()

        # pandas data frame for synthetic load profiles
        self.__slp_df = pd.DataFrame()

        # geo data frames for residential buildings and non-residential buildings
        self.__res_b_gdf = gp.GeoDataFrame()
        self.__nonres_b_gdf = gp.GeoDataFrame()
        self.__b_gdf = gp.GeoDataFrame()

        # geo data frame for the streets
        self.__s_raw_gdf = gp.GeoDataFrame()
        self.__s_f_gdf = gp.GeoDataFrame()
        self.__s_gdf = gp.GeoDataFrame()

        self.__polygon = None
        self.__lines_gdf = None
        self.__tr_gdf = None
        self.__nodes_assigned_gdf = None

        # variables for transformer clustering
        self.__model = None
        self.__scores = []

        # building specific parameters
        #self.__average_room_height = 2.6    # [m]


    def get_scores(self) -> list:
        """
        returns silhouette scores

        Parameters:
        -----------
        None

        Returns:
        --------
        list
            list of silhouette scores
        """

        return self.__scores
    

    def flatten_nodes(self, value):
        """
        flattens nodes in a list of lists

        Parameters:
        -----------

        Returns:
        --------
        """
        if isinstance(value, list):
            # check if it is a list of lists [[], [], [], ...]
            if any(isinstance(i, list) for i in value):
                return list(itertools.chain(*value))  # flatten those lists
            else:
                return value  # if it is a normal list, keep it
        return value  # also if it is no list-type, keep it
    

    def extract_streets_from_polygon(self, polygon, tags) -> None:
        """
        generates the street network by a given polygon and osm-tags
        
        Parameters:
        -----------
        None

        Returns:
        --------
        None
        """
        polygon_coords = shp.get_coordinates(polygon)   # retrieves the coordinates of the given polygon for the selected map area

        # extract the geometries from OpenStreetMap within the selected map area according to the given tags
        self.__s_raw_gdf = ox.features_from_polygon(polygon, tags)

        # it could be the case that street are also retrieved outside of the polygon, this snippet cut-off the street segments which are polygon "outliers"
        # iterate over every street
        for i in range(len(self.__s_raw_gdf)):
            coordinates = []
            mask = np.empty(shape=(0,), dtype=int)

            geometry = self.__s_raw_gdf.iloc[i].geometry
            if isinstance(geometry, Polygon):
                geometry = LineString(geometry.exterior.coords)
            
            nodes = np.array(self.__s_raw_gdf.iloc[i].nodes) # alt
    
            # iterate over every coordinate and check if point lies in polygon or not. If the coordinate lies within the polygon add 1 to a mask array, otherwise 0
            for coord in geometry.coords:
                if ski.measure.points_in_poly(np.array(coord).reshape(1, 2), polygon_coords):
                    coordinates.append(coord)
                    mask = np.append(mask, 1)
                else:
                    mask = np.append(mask, 0)
           
            if len(coordinates) > 1:
                line = LineString(coordinates)
                nodes = nodes[mask == 1]
                length = line.length

                data = {'geometry': [line],
                        'nodes': [nodes],
                        'length': length}
                
                df_data_row = pd.DataFrame(data)
                gp_data_row = gp.GeoDataFrame(df_data_row, geometry='geometry', crs='EPSG:4326')
                self.__s_f_gdf = pd.concat([self.__s_f_gdf, gp_data_row], ignore_index=True)

        # project into metric crs
        self.__s_gdf = ox.projection.project_gdf(self.__s_f_gdf, to_crs="EPSG:9273", to_latlong=False) # project the geo data frame to an xy crs
        self.__s_gdf["length"] = self.__s_gdf.geometry.length # calculate the length of each street

        # keep only specific columns, other columns are deleted
        columns_to_keep = ['geometry', 'nodes', 'length', 'id']
        columns_to_drop = [col for col in self.__s_gdf.columns if col not in columns_to_keep]
        self.__s_gdf.drop(columns=columns_to_drop, inplace=True)

    
    def get_buildings(self) -> gp.GeoDataFrame:
        """
        Returns buildings GeoDataFrame.
        
        Parameters:
        -----------
        None

        Returns:
        --------
        gopandas.GeoDataFrame
            GeoDataFrame containing the building data
        """
        return self.__b_gdf
    

    def get_residential_buildings(self) -> gp.GeoDataFrame:
        """
        Returns residential buildings GeoDataFrame
        
        Parameters:
        -----------
        None

        Returns:
        --------
        gopandas.GeoDataFrame
            GeoDataFrame containing the building data.
        """
        return self.__res_b_gdf
    

    def get_streets(self) -> gp.GeoDataFrame:
        """
        Returns the street data frame.
        
        Parameters:
        -----------
        None

        Returns:
        --------
        gopandas.GeoDataFrame
            GeoDataFrame containing the street data.
        """
        return self.__s_gdf
    

    def get_transformers(self) -> gp.GeoDataFrame:
        """
        Returns the transformers GeoDataFrame.
        
        Parameters:
        -----------
        None

        Returns:
        --------
        gopandas.GeoDataFrame
            GeoDataFrame containing the transformers.
        """
        return self.__tr_gdf
    

    def load_polygon(self) -> Polygon:
        """
        Loads the polygon geometry from a .csv file.
        
        Parameters:
        -----------
        None

        Returns:
        --------
        shapely.geometry.Polygon
            Polygon geometry defining the area of interest.
        """
        self.__polygon_gdf = gp.read_file(prm.FILEPATH_DATA + prm.FILENAME_POLYGON_CSV)   # read the csv file and store it into a geopandas data frame
        self.__polygon_gdf.crs = 'EPSG:4326'    # set the coordinate reference system
        self.__polygon = self.__polygon_gdf.iloc[0]['geometry']  # extract only the geometry of the geopandas data frame and store it separately

        return self.__polygon


    def get_polygon(self) -> Polygon:
        """
        returns the polygon
        
        Parameters:
        -----------
        None

        Returns:
        --------
        shapely.geometry.Polygon
            Polygon geometry defining the area of interest
        """
        return self.__polygon


    def extract_non_residential_buildings_from_polygon(self, polygon, tags) -> None:
        """
        extracts non-residential buildings within the given polygon
        
        Parameters:
        -----------
        polygon:    shapely.geometry.Polygon
            Polygon geometry defining the area of interest
        tags:       dict
            OSM tags used to filter non-residential buildings

        Returns:
        --------
        None
        """
        self.__nonres_b_gdf = ox.features_from_polygon(polygon, tags)

        # delete all not needed columns
        columns_to_keep = ['amenity', 'geometry', 'nodes', 'addr:housenumber']
        columns_to_drop = [col for col in self.__nonres_b_gdf.columns if col not in columns_to_keep]
        self.__nonres_b_gdf.drop(columns=columns_to_drop, inplace=True)

        self.__nonres_b_gdf = self.__nonres_b_gdf[self.__nonres_b_gdf['amenity'].isin(set(prm.AMENITIES.keys()))]
        self.__nonres_b_gdf = ox.projection.project_gdf(self.__nonres_b_gdf, to_crs="EPSG:9273", to_latlong=False) # project the geo data frame to an xy crs

        self.__nonres_b_gdf['centroid'] = self.__nonres_b_gdf.geometry.centroid # calculate the centroid of each amenity
        self.__nonres_b_gdf['area'] = self.__nonres_b_gdf.geometry.area # calculate the area of each building
        self.__nonres_b_gdf['residential'] = False
        self.__nonres_b_gdf = self.__nonres_b_gdf[self.__nonres_b_gdf['area'] > 0] # consider only non-residential buildings with an calculated area > 0

        self.__nonres_b_gdf['nodes'] = self.__nonres_b_gdf['nodes'].apply(self.flatten_nodes)# some nodes are saved in lists of lists, hence those are going to be flattened


    def get_non_residential_buildings(self) -> gp.GeoDataFrame:
        """
        Returns the non-residential buildings GeoDataFrame within the given polygon 
        
        Parameters:
        -----------
        None

        Returns:
        --------
        geopandas.GeoDataFrame
            GeoDataFrame containing non-residential building geometries and attributes
        """
        return self.__nonres_b_gdf


    def extract_residential_buildings_from_polygon(self, polygon, tags) -> None:
        """
        Extracts residential buildings within the given polygon.
        
        Parameters:
        -----------
        polygon:    shapely.geometry.Polygon
            Polygon geometry defining the area of interest
        tags:       dict
            OSM tags used to filter non-residential buildings

        Returns:
        --------
        None
        """
        self.__res_b_gdf = ox.features_from_polygon(polygon, tags)  # raw GeoDataFrame, non projected with lat, lon values inside
        self.__res_b_gdf = ox.projection.project_gdf(self.__res_b_gdf, to_crs="EPSG:9273", to_latlong=False)  # project the GeoDataFrame to crs=EPSG:9273, values in meters
        
        self.__res_b_gdf['centroid'] = self.__res_b_gdf.geometry.centroid # calculate the centroid of each building
        self.__res_b_gdf['area'] = self.__res_b_gdf.geometry.area   # calculate the area of each building
        self.__res_b_gdf['amenity'] = None
        self.__res_b_gdf['residential'] = True
        
        self.__res_b_gdf = self.__res_b_gdf[self.__res_b_gdf['area'] >= prm.FOOTPRINT_AREA_THRESHHOLD]  # filter small outbuildings (garage, barn, etc.)
        
        columns_to_keep = ['geometry', 'nodes', 'centroid', 'area', 'amenity', 'residential', 'addr:housenumber']
        columns_to_drop = [col for col in self.__res_b_gdf.columns if col not in columns_to_keep]
        self.__res_b_gdf.drop(columns=columns_to_drop, inplace=True)
        
        self.__b_gdf['nodes'] = self.__res_b_gdf['nodes'].apply(self.flatten_nodes)# some nodes are saved in lists of lists, hence those are going to be flattened

    
    def extract_buildings_from_polygon(self, polygon, tags_nonres, tags_res) -> None:
        """
        Extracts residential and non-residential buildings within the given polygon.
        
        Parameters:
        -----------
        polygon : shapely.geometry.Polygon
            Polygon defining the area of interest.
        tags_nonres : dict
            OSM tags used to filter non-residential buildings.
        tags_res : dict
            OSM tags used to filter residential buildings.

        Returns:
        --------
        None
        """
        self.extract_non_residential_buildings_from_polygon(polygon, tags_nonres)
        self.extract_residential_buildings_from_polygon(polygon, tags_res)

        # combine residential and non-residential buildings
        self.__res_b_gdf = self.__res_b_gdf[~self.__res_b_gdf["centroid"].isin(self.__nonres_b_gdf["centroid"])].drop(columns=["centroid"])
        self.__b_gdf = gp.GeoDataFrame(pd.concat([self.__nonres_b_gdf, self.__res_b_gdf], ignore_index=True))   # combine the geo data frames for non-residential and residential buildings
        l = self.__b_gdf.shape[0]
        self.__b_gdf['id'] = [f'BD{str(i).zfill(6)}' for i in range(1, l + 1)]

        self.__b_gdf['centroid'] = self.__b_gdf.geometry.centroid # calculate the centroid of each building
        self.__b_gdf['area'] = self.__b_gdf.geometry.area   # calculate the area of each building

        for i in range(0, 3):
            self.__b_gdf['nodes'] = self.__b_gdf['nodes'].apply(self.flatten_nodes)# some nodes are saved in lists of lists, hence those are going to be flattened


    def load_synthetic_profiles(self):
        """
        Loads synthetic load profiles for load estimation.
        
        Parameters:
        -----------
        None

        Returns:
        --------
        None
        """
        self.__slp_df = pd.read_excel(prm.FILEPATH_DATA + prm.FILE_SYNTHETIC_LOAD_PROFILES)   # load the excel file into a pandas data frame
        self.__slp_df['ts'] = pd.to_datetime(self.__slp_df['ts'])   # convert the timestamps
        start_time = pd.Timestamp(prm.SLP_START_DATE) # select the start time of the synthetic load profile (value stored in parameters)
        end_time = pd.Timestamp(prm.SLP_END_DATE) # select the end time of the synthetic load profile (value stored in parameters)

        self.__slp_df = self.__slp_df[(self.__slp_df['ts'] >= start_time) & (self.__slp_df['ts'] <= end_time)]
        self.__slp_df = self.__slp_df.set_index('ts')
        columns_to_keep = prm.SLPS
        columns_to_drop = [col for col in self.__slp_df.columns if col not in columns_to_keep]
        self.__slp_df.drop(columns=columns_to_drop, inplace=True)


    def calculate_peak_power(self, energy_demand, building_type, slp, residential_units) -> float:
        """
        Calculates the peak power for each building type.
        
        Parameters:
        -----------
        energy_demand : float
            Annual energy demand of the building.
        building_type : str
            Type of the building.
        slp : object
            Synthetic load profile used for the calculation.
        residential_units : int
            Number of residential units in the building.

        Returns:
        --------
        float
            Calculated peak power.
        """
        if building_type == prm.NODE_TYPE_AMENTY:
            if slp == 'G0':
                slp_arr = np.array(self.__slp_df['G0']) * energy_demand / 1000
            if slp == 'G1':
                slp_arr = np.array(self.__slp_df['G1']) * energy_demand / 1000
            if slp == 'G2':
                slp_arr = np.array(self.__slp_df['G2']) * energy_demand / 1000
            if slp == 'G3':
                slp_arr = np.array(self.__slp_df['G3']) * energy_demand / 1000
            if slp == 'G6':
                slp_arr = np.array(self.__slp_df['G6']) * energy_demand / 1000
            
            #p_peak = np.mean(np.convolve(slp_arr, np.ones(4, dtype=int), 'valid')/0.25) # wurde verwendet
            #p_peak = np.mean(np.convolve(slp_arr/0.25, np.ones(4, dtype=int), 'valid'))
            p_peak = np.max(slp_arr/0.25)
    
        if building_type == prm.NODE_TYPE_HOUSE:
            slp_arr = np.array(self.__slp_df['H0']) * energy_demand / 1000
            #p_peak = np.mean(np.convolve(slp_arr, np.ones(4, dtype=int), 'valid')/0.25) # wurde verwendet
            p_peak = np.max(slp_arr/0.25)
            #p_peak = np.mean(np.convolve(slp_arr/0.25, np.ones(4, dtype=int), 'valid'))
            
        if building_type == prm.NODE_TYPE_MULTI:
            slp_arr = np.array(self.__slp_df['H0']) * energy_demand / 1000

            g_f = 0.07
            g = (g_f + (1 - g_f) * residential_units**(-3/4))

            #p_peak = g * residential_units * np.max(slp_arr/0.25)
            p_peak = g * residential_units * 2.0

        return p_peak


    def load_estimation(self):
        """
        Calculates the load estimation for each building type.
        
        Parameters:
        -----------
        None

        Returns:
        --------
        None
        """
        self.__b_gdf['energy_demand_m2'] = 0
        self.__b_gdf['building_type'] = prm.NODE_TYPE_HOUSE
        self.__b_gdf['slp'] = 'H0'
        self.__b_gdf['energy_demand'] = np.nan

        # calculate the whole area for each building
        self.__b_gdf['area_sum'] = self.__b_gdf.apply(lambda row: row['area'] * row['floors'], axis=1)

        # calculate the quartil of the area
        q3 = self.__b_gdf[self.__b_gdf['residential'] == True]["area_sum"].quantile(0.75)
        self.__b_gdf.loc[self.__b_gdf['residential'] == False, 'building_type'] = prm.NODE_TYPE_AMENTY
        self.__b_gdf.loc[self.__b_gdf['residential'] & (self.__b_gdf['area_sum'] > q3), 'building_type'] = prm.NODE_TYPE_MULTI
        
        # assign the load profiles for the amenities
        for index, row in self.__b_gdf.iterrows():
            amenity = row.get('amenity')
            if amenity in prm.AMENITIES:
                self.__b_gdf.at[index, 'energy_demand_m2'] = prm.AMENITIES[amenity][2]
                self.__b_gdf.at[index, 'slp'] = prm.AMENITIES[amenity][1]
            else:
                self.__b_gdf.at[index, 'energy_demand_m2'] = np.nan


        # calculate the numer of residential units of each building with apartments
        self.__b_gdf['residential_units'] = np.nan
        mask = self.__b_gdf['building_type'] == prm.NODE_TYPE_MULTI

        self.__b_gdf.loc[mask, 'residential_units'] = (
            np.floor(self.__b_gdf.loc[mask, 'area_sum'] / prm.AVERAGE_FLAT_AREA)
        ).round().astype('Int64')

        self.__b_gdf.loc[self.__b_gdf['building_type'] == prm.NODE_TYPE_HOUSE, 'residential_units'] = 1   # set the number of residents for each house to 1

        # calculate the residents of each building
        self.__b_gdf['residents'] = self.__b_gdf.apply(lambda row: row['residential_units'] * prm.AVERAGE_RESIDENTS, axis=1)#calculate_residents(row['cluster'], row['residential_units']), axis=1)

        # calculate the energy demand of each amenity
        mask = self.__b_gdf['building_type'] == prm.NODE_TYPE_AMENTY

        self.__b_gdf.loc[mask, 'energy_demand'] = (
           np.clip(self.__b_gdf.loc[mask, 'area_sum'] * self.__b_gdf.loc[mask, 'energy_demand_m2'], None, 1e5)
        )

        # calculate the energy consumption of all houses
        mask = self.__b_gdf['building_type'] == prm.NODE_TYPE_HOUSE

        self.__b_gdf.loc[mask, 'energy_demand'] = (
            prm.AVERAGE_RESIDENTS * prm.CONSUMPTION_PER_RESIDENT +
            self.__b_gdf.loc[mask, 'area_sum'] * prm.CONSUMPTION_PER_AREA +
            prm.NUMBER_OF_DEVICES * prm.CONSUMPTION_OF_DEVICES
        )

        # calculate the energy consumption of each apartments
        mask = self.__b_gdf['building_type'] == prm.NODE_TYPE_MULTI

        self.__b_gdf.loc[mask, 'energy_demand'] = (
            prm.AVERAGE_RESIDENTS * prm.CONSUMPTION_PER_RESIDENT +
            prm.AVERAGE_FLAT_AREA * prm.CONSUMPTION_PER_AREA +
            prm.NUMBER_OF_DEVICES * prm.CONSUMPTION_OF_DEVICES
        )

        # now the power peak is calculated
        self.__b_gdf['p_peak'] = self.__b_gdf.apply(lambda row: self.calculate_peak_power(row['energy_demand'], row['building_type'], row['slp'], row['residential_units']), axis=1)
        
        # filter buildings as outliers
        q1_peak = self.__b_gdf["p_peak"].quantile(0.25)
        q3_peak = self.__b_gdf["p_peak"].quantile(0.75)
        iqr = q3_peak - q1_peak

        upper_threshold = q3_peak + 3 * iqr

        self.__b_gdf = self.__b_gdf[(self.__b_gdf["p_peak"] < upper_threshold)]


    def assign_buildings_to_nodes(self) -> gp.GeoDataFrame:
        """
        Assigns buildings to street nodes.
        
        Parameters:
        -----------
        None

        Returns:
        --------
        geopandas.GeoDataFrame
            GeoDataFrame with buildings assigned to their corresponding street nodes.
        """
        xy = []
        n = []

        # iterate over every street and then over every node of each street
        for idx, row in self.__s_gdf.iterrows():
            geometry = list(row['geometry'].coords)
            nodes = row['nodes']

            for i in range(len(nodes)):
                if nodes[i] not in n:
                    n.append(nodes[i])
                    xy.append(geometry[i])

        # create new geo data frame
        self.__nodes_assigned_gdf = gp.GeoDataFrame(columns=['geometry'])
        self.__nodes_assigned_gdf.set_crs(epsg=4326, inplace=True)

        self.__nodes_assigned_gdf['node'] = n
        geometry = [Point(xy) for xy in xy]

        self.__nodes_assigned_gdf['geometry'] = geometry
        self.__nodes_assigned_gdf['buildings'] = [[] for _ in range(len(self.__nodes_assigned_gdf))]
        self.__nodes_assigned_gdf['transformers'] = [[] for _ in range(len(self.__nodes_assigned_gdf))]
        
        # create the C matrix of the buildings geometry
        C = np.vstack((     np.ravel(   np.reshape(np.array(self.__b_gdf["centroid"].geometry.x), (np.array(self.__b_gdf["centroid"].geometry.x).shape[0], 1))), 
                            np.ravel(np.reshape(np.array(self.__b_gdf["centroid"].geometry.y), (np.array(self.__b_gdf["centroid"].geometry.y).shape[0], 1)))  )).T

        # create the N matrix of the street nodes geometry
        N = np.column_stack((   self.__nodes_assigned_gdf['geometry'].apply(lambda point: point.x),
                                self.__nodes_assigned_gdf['geometry'].apply(lambda point: point.y)  ))

        # calculate distance matrix D
        D = distance_matrix(C, N)

        # find the minimum values of the distance matrix D
        min_indices_per_row = np.argmin(D, axis=1)

        # iterate over the index matrix for the minimum distances
        for i in range(len(min_indices_per_row)):
            # get the index of each row
            idx = min_indices_per_row[i]
            # check if the matched house id is not in the assigned buildings columns, if so add it
            if self.__b_gdf.iloc[i]['id'] not in self.__nodes_assigned_gdf.iloc[idx]['buildings']:
                self.__nodes_assigned_gdf.iloc[idx]['buildings'].append(self.__b_gdf.iloc[i]['id'])

        return self.__nodes_assigned_gdf


    def assign_transformers_to_nodes(self) -> gp.GeoDataFrame:
        """
        Assigns transformers to street nodes.
        
        Parameters:
        -----------
        None

        Returns:
        --------
        geopandas.GeoDataFrame
            GeoDataFrame with transformers assigned to their corresponding street nodes.
        """
        C = np.vstack((     np.ravel(   np.reshape(np.array(self.__tr_gdf["geometry"].geometry.x), (np.array(self.__tr_gdf["geometry"].geometry.x).shape[0], 1))), 
                            np.ravel(np.reshape(np.array(self.__tr_gdf["geometry"].geometry.y), (np.array(self.__tr_gdf["geometry"].geometry.y).shape[0], 1)))  )).T
    
        # create the N matrix of the street nodes geometry
        N = np.column_stack((   self.__nodes_assigned_gdf['geometry'].apply(lambda point: point.x),
                                self.__nodes_assigned_gdf['geometry'].apply(lambda point: point.y)  ))
    
        # calculate distance matrix D
        D = distance_matrix(C, N)
        
        # find the minimum values of the distance matrix D
        min_indices_per_row = np.argmin(D, axis=1)

        # iterate over the index matrix for the minimum distances
        for i in range(len(min_indices_per_row)):
            # get the index of each row
            idx = min_indices_per_row[i]
            # check if the matched house id is not in the assigned buildings columns, if so add it
            if self.__tr_gdf.iloc[i]['id'] not in self.__nodes_assigned_gdf.iloc[idx]['transformers']:
                self.__nodes_assigned_gdf.iloc[idx]['transformers'].append(self.__tr_gdf.iloc[i]['id'])

        self.__nodes_assigned_gdf['node_type'] = self.__nodes_assigned_gdf.apply(lambda row: 'POWCON' if (len(row['buildings']) > 0 or len(row['transformers']) > 0) else 'COMMON', axis=1)
        self.__nodes_assigned_gdf['node_role'] = 'DEMAND'

        return self.__nodes_assigned_gdf
    

    def get_nodes_assigned(self) -> gp.GeoDataFrame:
        """
        Returns the GeoDataFrame of nodes with assigned objects.
        
        Parameters:
        -----------
        None

        Returns:
        --------
        geopandas.GeoDataFrame
            GeoDataFrame containing nodes and their assigned objects.
        """
        return self.__nodes_assigned_gdf
    

    def extract_lines(self) -> gp.GeoDataFrame:
        """
        Extracts line segments between consecutive nodes from the network geometry.
        
        Parameters:
        -----------
        None

        Returns:
        --------
        geopandas.GeoDataFrame
            GeoDataFrame containing line segments with start and end nodes,
            geometric representation, and associated attributes.
        """
        line_id = []
        start_node = []
        end_node = []
        start_pos = []
        end_pos = []
        loading = []
        geometry = []
        color = []


        for idx, row in self.__s_gdf.iterrows():
            linestring = row['geometry']
            nodes = row['nodes']

            if isinstance(linestring, LineString):
                points = list(linestring.coords)

                for i in range(len(points) - 1):
                    start_node.append(nodes[i])
                    end_node.append(nodes[i + 1])
                    start_pos.append(points[i])
                    end_pos.append(points[i + 1])
                    loading.append(0)
                    color.append('')
                    geometry.append(LineString([points[i], points[i + 1]]))

        line_id = [f'LI{str(i).zfill(6)}' for i in range(1, len(geometry) + 1)]

        data = {
            'line_id': line_id,
            'start_node': start_node,
            'end_node': end_node,
            'start_pos': start_pos,
            'end_pos': end_pos,
            'loading': loading,
            'color': color,
            'geometry': geometry
        }

        # create new geo data frame
        self.__lines_gdf = gp.GeoDataFrame(data, geometry='geometry')
        self.__lines_gdf.set_crs(epsg=4326, inplace=True)

        self.__lines_gdf["start_node"] = "ND" + self.__lines_gdf["start_node"].astype(str)
        self.__lines_gdf["end_node"]   = "ND" + self.__lines_gdf["end_node"].astype(str)
        
        return self.__lines_gdf
    

    def get_lines(self) -> gp.GeoDataFrame:
        """
        Returns the GeoDataFrame containing the extracted line segments.
        
        Parameters:
        -----------
        None

        Returns:
        --------
        Geopandas.GeoDataFrame
            GeoDataFrame of network line segments.
        """
        return self.__lines_gdf
    

    def estimate_synthetic_transformers(self) -> tuple:
        """
        Estimates synthetic transformer locations and ratings based on clustered building loads.
        
        Parameters:
        -----------
        None

        Returns:
        --------
        tuple
            Tuple containing:
            - geopandas.GeoDataFrame
                GeoDataFrame with synthetic transformer locations and assigned rated power.
            - object
                Fitted clustering model used for the estimation (e.g., KMeans).
            - numpy.ndarray
                Normalized coordinate array used as input for clustering.
        """

        transformer_rated_power = prm.TRANSFORMER_RATED_POWER

        def calc_cluster_power(model) -> gp.GeoDataFrame:
            """
            Calculates the aggregated peak power per cluster.
        
            Parameters:
            -----------
            model : object
                Fitted clustering model providing cluster labels.

            Returns:
            --------
            geopandas.GeoDataFrame
                GeoDataFrame containing the summed peak power and transformed
                peak power per cluster.
            """
            labels = model.labels_

            self.__b_gdf['cluster'] = labels

            # calculate the power of each cluster and save it into a data frame
            c_p_df = self.__b_gdf.groupby('cluster', as_index=False)['p_peak'].sum()
            c_p_df["p_peak_t"] = c_p_df["p_peak"] / (prm.POWER_FACTOR * prm.WORKLOAD)
    
            return c_p_df


        def all_supply_possible(c_p_df: gp.GeoDataFrame, available_transformers: list) -> bool:
            """
            Checks whether all clusters can be supplied by the available transformer ratings.
        
            Parameters:
            -----------
            c_p_df : geopandas.GeoDataFrame
                GeoDataFrame containing the required peak power per cluster.
            available_transformers : list
                List of available transformer rated powers.

            Returns:
            --------
            bool
                True if all clusters can be supplied, otherwise False.
            """
            c_power = c_p_df["p_peak_t"]

            for p in c_power:
                if not any(p <= t for t in available_transformers):
                    return False
            return True

        pos_x = np.array(self.__b_gdf["centroid"].x)
        pos_y = np.array(self.__b_gdf["centroid"].y)
        coords = np.vstack((pos_x, pos_y)).T
        power = np.array(self.__b_gdf["p_peak"]/(prm.POWER_FACTOR * prm.WORKLOAD))

        n_t = np.ceil(np.sum(power)/prm.POWER_TRANSFORMER).astype(int)
        
        if n_t == 1:
            cx = np.sum(pos_x * power) / np.sum(power)
            cy = np.sum(pos_y * power) / np.sum(power)

            c = Point(cx, cy)

            # create DataFrame
            tr_syn_df = pd.DataFrame([{"x": c.x, "y": c.y}])

            tr_syn_gdf = gp.GeoDataFrame(
                tr_syn_df,
                geometry=gp.points_from_xy(tr_syn_df["x"], tr_syn_df["y"]),
                crs=self.__b_gdf.crs
            )


            # transformer sizing
            tr_syn_gdf['p_peak_t'] = np.sum(power)
            tr_syn_gdf["power"] = tr_syn_gdf["p_peak_t"].apply(
                lambda p: next((t for t in transformer_rated_power if p <= t), transformer_rated_power[-1])
            )
            
            tr_syn_gdf["id"] = ["TR00000001"]

        if n_t > 1:
            scaler = MinMaxScaler()
            X = scaler.fit_transform(coords)
            delta = prm.DELTA

            n_t_range = list(range(2, min(n_t + delta, len(X))))

            scores = []
            models = []
            sup_pos = []
            dfs = []

            for num_clusters in n_t_range:
                print(f'num_clusters: {num_clusters}')
                kmeans = KMeans(n_clusters=num_clusters, random_state=42)   # initialize kmeans
                kmeans.fit(X, sample_weight=power)

                # calculate the dataframe and the power for each cluster
                c_p_df = calc_cluster_power(kmeans)
                dfs.append(c_p_df)

                # check if every cluster can be supplied by a transformer
                sup_pos.append(all_supply_possible(c_p_df, transformer_rated_power))
                scores.append(silhouette_score(X, kmeans.labels_))
                models.append(kmeans)

            valid_indices = np.where(sup_pos)[0].astype(int)
            relative_best_index = np.argmax(np.array(scores)[valid_indices])
            best_index = valid_indices[relative_best_index]

            model_opt = models[best_index]
            self.__model = model_opt

            centroids = scaler.inverse_transform(model_opt.cluster_centers_)[:, :2]

            # add geometry
            tr_syn_df = pd.DataFrame(centroids, columns=['x', 'y'])
            tr_syn_df['geometry'] = tr_syn_df.apply(lambda row: Point(row['x'], row['y']), axis=1)

            dfs = dfs[best_index]

            dfs['power'] = dfs['p_peak_t'].apply(
                lambda p: next((t for t in transformer_rated_power if p <= t), None)
            )

            tr_syn_df = pd.concat([tr_syn_df, dfs], axis=1)
            tr_syn_gdf = gp.GeoDataFrame(tr_syn_df, geometry='geometry', crs='EPSG:9273')
            tr_syn_gdf['id'] = [f"TR{str(i).zfill(8)}" for i in range(1, self.__model.n_clusters + 1)]
            tr_syn_gdf = tr_syn_gdf[tr_syn_gdf['p_peak_t'] >= 0.5 * tr_syn_gdf["p_peak_t"].mean()]
        
        self.__tr_gdf = tr_syn_gdf
    
        return tr_syn_gdf, model_opt, X
    

    def get_coordinates_for_noe_atlas(self) -> pd.DataFrame:
        """
        Returns coordinates formatted for the NOE Atlas.
        
        Parameters:
        -----------
        None

        Returns:
        --------
        pandas.DataFrame
            DataFrame containing the coordinates in the required NOE Atlas format.
        """
        temp = ox.projection.project_gdf(self.__b_gdf, to_crs="EPSG:4326", to_latlong=False)#temp.to_crs(crs='EPSG:3857')
        temp['centroid'] = temp.geometry.centroid
        
        header = ['#', 'Rechtswert', 'Hochwert']
        coords = pd.DataFrame(data=(np.vstack((np.array(temp['id']), np.array(temp['centroid'].x), np.array(temp['centroid'].y)))).T,
                              columns=header)
        coords['#'] = coords['#']
        
        # calculate the number of files
        num_files = (len(coords) // prm.NOE_ATLAS_MAX_ROWS) + (1 if len(coords) % prm.NOE_ATLAS_MAX_ROWS > 0 else 0)

        # iterate over the number of necessary files
        for i in range(num_files):
            idx_s = i * prm.NOE_ATLAS_MAX_ROWS
            idx_e = idx_s + prm.NOE_ATLAS_MAX_ROWS
            df_c = coords.iloc[idx_s:idx_e]

            df_c.to_csv(f'{prm.FILEPATH_DATA}' + f'coords_atlas_noe_WGS84_{i+1}.csv', sep=";", decimal= ",", index=False)

        return coords


    def set_building_heights(self) -> None:
        """
        Sets building heights and number of floors based on external height data.
        
        Parameters:
        -----------
        None

        Returns:
        --------
        None
        """
        surface = []
        sea_level = []
        heights = []
        pattern = r'[-+](\d+(?:,\d+)?)m (Gelände|Oberfläche)'

        paths = sorted(glob.glob(prm.FILEPATH_DATA + prm.FILENAME_BUILDINGS_HEIGHTS_CSV))
        paths = [os.path.normpath(f).replace('\\', '/') for f in paths]

        try:
            df = pd.concat([pd.read_csv(path, sep=";", decimal=',', encoding='latin1') for path in paths])
        except:
            print("Error - No files found. Please use NOE Atlas for get the height information")
            return None

        input_strings = df["Höhe"]

        for input_string in input_strings:
            matches = re.findall(pattern, input_string)
            sea_level.append(float(matches[0][0].replace(",", ".")))
            surface.append(float(matches[1][0].replace(",", ".")))

        heights = np.subtract(surface, sea_level)
        floors = np.floor(np.divide(    heights, 
                                        prm.AVERAGE_ROOM_HEIGHT  )).astype(int)
        
        self.__b_gdf["surface"] = surface
        self.__b_gdf["sea_level"] = sea_level
        self.__b_gdf["height"] = heights
        self.__b_gdf["floors"] = floors

        self.__b_gdf['height'] = self.__b_gdf['height'].apply(lambda h: max(h , prm.MINIMUM_BUILDING_HEIGHT))
        self.__b_gdf['floors'] = self.__b_gdf['floors'].replace(0, prm.MINIMUM_BUILDING_FLOORS)


    def export_data(self) -> None:
        """
        Exports all GeoDataFrames to Parquet files.
        
        Parameters:
        -----------
        None

        Returns:
        --------
        None
        """
        self.__s_gdf.to_parquet(prm.FILEPATH_DATA + prm.FILENAME_STREETS_PARQUET)
        self.__b_gdf.to_parquet(prm.FILEPATH_DATA + prm.FILENAME_BUILDINGS_PARQUET)
        self.__lines_gdf.to_parquet(prm.FILEPATH_DATA + prm.FILENAME_LINES_PARQUET)
        self.__tr_gdf.to_parquet(prm.FILEPATH_DATA + prm.FILENAME_TRANSFORMERS_PARQUET)
        self.__nodes_assigned_gdf.to_parquet(prm.FILEPATH_DATA + prm.FILENAME_NODES_PARQUET)
