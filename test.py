import dtree
import numpy as np
import pandas as pd
import jenkspy

from xlsxwriter import Workbook

crash_data = pd.read_excel('C:/Users/fproulx/Working/MiDOT_Sidepaths/20170706_Kent and Oakland data.xlsx',
                           sheetname='Raw cleaned', skiprows=2)

crash_data.columns = map(lambda x: x.replace(' ', '_'), crash_data.columns)

reload(dtree)
tree = dtree.dtree(crash_data)

output_folder = 'C:/Users/fproulx/Desktop/MiDOT_Sidepaths/trees/'

tree.data.columns

tree_formulae = {'BikeDirection': ['Intersection_or_Non_Intersection_or_Driveway',
                                    'Bike_Facility_Type',
                                    'Direction_of_Travel'],
                 'BikeAction': ['Intersection_or_Non_Intersection_or_Driveway',
                                                     'Bike_Facility_Type',
                                                     'Bike_Action'],
                 'VehicleAction': ['Intersection_or_Non_Intersection_or_Driveway',
                                                     'Bike_Facility_Type',
                                                     'Vehicle_action'],
                 'CrashType': ['Intersection_or_Non_Intersection_or_Driveway',
                                                     'Bike_Facility_Type',
                                                     'Bike_Crash_Coding']}


tree.many_trees_to_excel(tree_formulae, Workbook('./test.xlsx'))
