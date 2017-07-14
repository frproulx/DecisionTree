import dtree
import pandas as pd

crash_data = pd.read_excel('C:/Users/fproulx/Desktop/MiDOT_Sidepaths/20170706_Kent and Oakland data.xlsx',
                           sheetname='Raw cleaned', skiprows=2)

crash_data.columns = map(lambda x: x.replace(' ', '_'), crash_data.columns)

reload(dtree)
tree = dtree.dtree(crash_data)
tree
tree.split_tree(['Bike_Facility_Type',
                'Intersection_or_Non_Intersection_or_Driveway',
                  'Direction_of_Travel'])

tree
tree.pretty_print()
