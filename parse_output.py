import pandas as pd
import xml.etree.ElementTree as ET
import os
import sys

def parse_output(file_path):
    print(f'{file_path}')
    # file_path = os.path.join(base_path, dataset_name)
    tree = ET.parse(file_path)
    root = tree.getroot()

    columns = ['Timestep', 'veh_id', 'Route_ID', 'Lane_ID', 'Position']
    df = pd.DataFrame(columns=columns)

    for timestep in root.iter('data'):
        timestep_value = float(timestep.get('timestep'))
        for vehicle in timestep.iter('vehicle'):
            vehicle_id = vehicle.get('id')
            route = vehicle.get('route')
            lane = vehicle.get('lane')
            position = vehicle.get('pos')
            x = vehicle.get('x')
            y = vehicle.get('y')

            df = pd.concat([df, pd.DataFrame({
                'Timestep': [timestep_value],
                'veh_id': [vehicle_id],
                'Route_ID': [route],
                'Lane_ID': [lane],
                'Position': [position],
                'x': [x],
                'y': [y]
            })], ignore_index=True)

    df['Timestep'] = pd.to_numeric(df['Timestep'], errors='coerce')
    # print(f"parsed data \n {df}")
    return df

result_df = pd.DataFrame(columns=['Veh_id', 'Lane_ID', 'Route_ID', 'Timestep', 'Position'])
offset_df = pd.DataFrame(columns=['Veh_id', 'lane_id', 'start_time', 'end_time', 'time_offset'])

# for vehicle_id in df['Vehicle_ID'].unique():
#     vehicle_rows = df[df['Vehicle_ID'] == vehicle_id]
#     for lane_id in vehicle_rows['Lane_ID'].unique():
#         lane_rows = vehicle_rows[vehicle_rows['Lane_ID'] == lane_id]
#         result_df = pd.concat([result_df, lane_rows[['Vehicle_ID', 'Lane_ID', 'Route_ID', 'Timestep', 'Position']]], ignore_index=True)

def calculate_offset(df, dataset_name):
    offset_df = pd.DataFrame(columns=['veh_id', 'lane_id', 'start_time', 'end_time', 'time_offset'])

    for vehicle_id in df['veh_id'].unique():
        vehicle_rows = df[df['veh_id'] == vehicle_id]
        start_time = 0.0
        end_time = 0.0
        for lane_id in vehicle_rows['Lane_ID'].unique():
            # timestep = vehicle_rows['Timestep']
            lane_rows = vehicle_rows[vehicle_rows['Lane_ID'] == lane_id]
            start_time = float(lane_rows['Timestep'].min())
            end_time = float(lane_rows['Timestep'].max())
            time_offset = (end_time - start_time)
            if end_time < start_time:
                print(f"Timestep: {lane_rows['Timestep']}")
                print(f"veh_id: {vehicle_id}, lane_id: {lane_id}, start_time: {start_time}, end_time: {end_time}")
            offset_df = pd.concat([offset_df, pd.DataFrame({
                    # 'timestep': [timestep],
                    'veh_id': [vehicle_id],
                    'lane_id': [lane_id],
                    'start_time': [start_time],
                    'end_time': [end_time],
                    'time_offset': [time_offset]
                })
            ], ignore_index=True)

    offset_df['veh_id'] = offset_df['veh_id'].astype('str')
    # offset_file_name = f'offset_df_{dataset_name}.csv'
    # file_path = os.path.join(base_path, offset_file_name)
    # offset_df.to_csv(file_path, index=False)   ## comment for now
    # print(f"offset_df \n {offset_df}")
    return offset_df


# Add the following code to test the function
# base_path = '/home/tvillarr/Supriya/dataset/'
# output_xml = 'intersection_4_output.xml'  # for single run of this file
# file_path = os.path.join(base_path, output_xml)  # for single run of this file
# result_with_offset = calculate_offset(output_file_path)
# print(result_with_offset)
