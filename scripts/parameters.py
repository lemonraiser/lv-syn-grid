# =============================================================================
# Project:  lv-syn-grid
# Author:   Roman S.
# Created:  2025
#
# Description:
# Project parameters
#
# License: MIT License
#
# =============================================================================

# imports
import os
from collections import namedtuple

# ******************* project specific parameters *******************
PROJECT = 'Test'   # <-- change for project

# folder structure for data export
FILEPATH_DATA = 'grids/' + PROJECT + '/data/'
FILEPATH_LV_GRID = 'grids/' + PROJECT + '/lvgrid/'
FILEPATH_MV_GRID = 'grids/' + PROJECT + '/mvgrid/'
FILEPATH_PLOTS = 'grids/' + PROJECT + '/plots/'
FILEPATH_SIMRES = 'grids/' + PROJECT + '/simresults/'

# file paths for data export
FILEPATH_STREETS_PARQUET = 'streets.parquet'
FILEPATH_BUILDINGS_PARQUET = 'buildings.parquet'
FILEPATH_NODES_PARQUET = 'nodes.parquet'
FILEPATH_LINES_PARQUET = 'lines.parquet'
FILEPATH_TRANSFORMERS_PARQUET = 'transformers.parquet'
FILEPATH_PV_PARQUET = 'photovoltaic.parquet'

FILE_STREETS_PARQUET = 'streets.parquet'
FILE_BUILDINGS_PARQUET = 'buildings.parquet'
FILE_NODES_PARQUET = 'nodes.parquet'
FILE_LINES_PARQUET = 'lines.parquet'
FILE_TRANSFORMERS_PARQUET = 'transformers.parquet'
FILE_PV_PARQUET = 'photovoltaic.parquet'

# file paths
FILENAME_POLYGON_CSV = 'polygon_coordinates.csv'
FILENAME_BUILDINGS_PARQUET = 'buildings.parquet'
FILENAME_STREETS_PARQUET = 'streets.parquet'
FILENAME_LINES_PARQUET = 'lines.parquet'
FILENAME_TRANSFORMERS_PARQUET = 'transformers.parquet'
FILENAME_NODES_PARQUET = 'nodes.parquet'

FILENAME_BUILDINGS_HEIGHTS_CSV = 'buildings_heights_*.csv'

FILE_SIMRES_BUSVOLTAGE = 'res_bus/vm_pu.xlsx'
FILE_SIMRES_LINELOADING = 'res_line/loading_percent.xlsx'
FILE_SIMRES_TRAFOLOADING ='res_trafo/loading_percent.xlsx'

# create folder structure
os.makedirs(FILEPATH_DATA, exist_ok=True)
os.makedirs(FILEPATH_LV_GRID, exist_ok=True)
os.makedirs(FILEPATH_MV_GRID, exist_ok=True)
os.makedirs(FILEPATH_PLOTS, exist_ok=True)
os.makedirs(FILEPATH_SIMRES, exist_ok=True)

CRS_GEO = 'EPSG:4326'
CRS_XY = 'EPSG:9273'

# ******************* transformer specific parameters *******************
# transformer types and their capacity in kVA, which should be used for the synthesis

#TRANSFORMER_RATED_POWER = [160, 250]        # countryside
TRANSFORMER_RATED_POWER = [160, 250, 400]   # village
#TRANSFORMER_RATED_POWER = [160, 250, 400, 630] # village, suburb
#TRANSFORMER_RATED_POWER = [160, 250, 400, 630, 800]    # suburb

WORKLOAD = 0.5          # workload, LT = 50 [%]
POWER_FACTOR = 0.95     # lambda   [1]
POWER_TRANSFORMER = 160 # RT = 400 [kVA]
DELTA = 15

# maximum datasets for NOE Atlas
NOE_ATLAS_MAX_ROWS = 100

# ******************* load profile specific parameters *******************
# synthetic load profiles
FILE_SYNTHETIC_LOAD_PROFILES = 'synthload2025.xlsx'
SLP_START_DATE = '2025-02-17T00:00:00'
SLP_END_DATE = '2025-02-17T23:45:00'
SLPS = ['H0', 'G0', 'G1', 'G2', 'G3', 'G6']

# constants for data acquisition and pre-processing
FOOTPRINT_AREA_THRESHHOLD = 60  #[m2]

TAGS_NONRESIDENTIAL_BUILDINGS = {
    'amenity': True
}

TAGS_RESIDENTIAL_BUILDINGS = {
    'building':'yes',
    'addr:housenumber': True
}

TAGS_STREETS = {
    'highway':  ['primary', 'secondary', 'tertiary', 'residential', 'road', 'unclassified']#, 'track', 'service']
}

# building types
PUBLIC = 'public'
APARTMENTS = 'apartments'
HOUSE = 'house'

# parameters for load estimation
AVERAGE_RESIDENTS = 2.74
CONSUMPTION_PER_RESIDENT = 200
CONSUMPTION_PER_AREA = 9
NUMBER_OF_DEVICES = 8.4
CONSUMPTION_OF_DEVICES = 200
AVERAGE_FLAT_AREA = 101.8
MINIMUM_BUILDING_HEIGHT = 5.0   # [m]
MINIMUM_BUILDING_FLOORS = 1
AVERAGE_ROOM_HEIGHT = 2.6       # [m]

#######################################################################
############## DO NOT CHANGE ##########################################
#######################################################################

# keys for storing the values supply / demand
KEY_SUPPLY_POWER = 'su'
KEY_DEMAND_POWER = 'dv'

# node roles
NODE_ROLE_DEMAND = 'DEMAND' # node is a demand node
NODE_ROLE_SUPPLY = 'SUPPLY' # node is a supply node

# node types
NODE_TYPE_COMMON = 'COMMON' # common node, no specific property, connects street segments
NODE_TYPE_POWCON = 'POWCON' # node works as power connector, either a supply or demand is connected to it
NODE_TYPE_RESDTL = 'RESDTL' # node is a residential building
NODE_TYPE_AMENTY = 'AMENTY' # node is an amenity building
NODE_TYPE_TRFORM = 'TRFORM' # node is a transformer
NODE_TYPE_HOUSE  = 'HOUSE'  # node is a single-family-house
NODE_TYPE_MULTI  = 'APTMNT' # node is a multi-family-building

LINE_MAIN = 'LIMAIN'    # main line, works as a line segment in the lv network
LINE_CONN = 'LICONN'    # represents a line which connects a building to the lv network (lower cross area section, shorter length, etc.)
LINE_TRFM = 'TRCONN'    # represents a line which connects a transformer to the lv network

LOAD_PROFILES = {
    'residential':  'H0',
    'education':    'G1',
    'retail':       'G1',
    'gastro':       'G2',
    'health':       'G3',
    'public':       'G3',
    'culture':      'G6',
    'religion':     'G6',
    'other':        'G0'
}

building_info = namedtuple('building_info', ['category', 'load_profile', 'energy_demand'])


# data from:
# https://www.dena.de/fileadmin/dena/Publikationen/PDFs/2023/STUDIE_Fit_fuer_2045_Zielparameter_fuer_Nichtwohngebaeude_im_Bestand.pdf
AMENITIES = {
    # retail
    'convenience':      building_info('retail', LOAD_PROFILES['retail'], 217),
    'bakery':           building_info('retail', LOAD_PROFILES['retail'], 217),
    'butcher':          building_info('retail', LOAD_PROFILES['retail'], 217),
    'marketplace':      building_info('retail', LOAD_PROFILES['retail'], 217),
    'supermarket':      building_info('retail', LOAD_PROFILES['retail'], 217),
    
    # health
    'clinic':           building_info('health', LOAD_PROFILES['health'], 38),
    'dentist':          building_info('health', LOAD_PROFILES['health'], 38),
    'doctors':          building_info('health', LOAD_PROFILES['health'], 38),
    'hospital':         building_info('health', LOAD_PROFILES['health'], 38),
    'nursing_home':     building_info('health', LOAD_PROFILES['health'], 38),
    'pharmacy':         building_info('health', LOAD_PROFILES['health'], 38),
    
    # public
    'fire_station':     building_info('public', LOAD_PROFILES['public'], 28),
    'police':           building_info('public', LOAD_PROFILES['public'], 28),
    'post_office':      building_info('public', LOAD_PROFILES['public'], 28),
    
    # culture
    'arts_centre':      building_info('culture', LOAD_PROFILES['culture'], 32),
    'cinema':           building_info('culture', LOAD_PROFILES['culture'], 32),
    'theatre':          building_info('culture', LOAD_PROFILES['culture'], 32),
    'stadium':          building_info('culture', LOAD_PROFILES['culture'], 32),
    'sports_centre':    building_info('culture', LOAD_PROFILES['culture'], 32),
    'swimming_pool':    building_info('culture', LOAD_PROFILES['culture'], 32),
    'gym':              building_info('culture', LOAD_PROFILES['culture'], 32),
    'place_of_worship': building_info('education', LOAD_PROFILES['culture'], 32),
    
    # gastro
    'restaurant':       building_info('gastro', LOAD_PROFILES['gastro'], 104),
    'cafe':             building_info('gastro', LOAD_PROFILES['gastro'], 104),
    'bar':              building_info('gastro', LOAD_PROFILES['gastro'], 104),
    'fast_food':        building_info('gastro', LOAD_PROFILES['gastro'], 104),
    'food_court':       building_info('gastro', LOAD_PROFILES['gastro'], 104),
    'pub':              building_info('gastro', LOAD_PROFILES['gastro'], 104),
    
    # education
    'kindergarten':     building_info('education', LOAD_PROFILES['education'], 19),
    'school':           building_info('education', LOAD_PROFILES['education'], 19),
    'college':          building_info('education', LOAD_PROFILES['education'], 29),
    'university':       building_info('education', LOAD_PROFILES['education'], 29),
}
