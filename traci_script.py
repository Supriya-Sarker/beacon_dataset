
import os
import sys
from optparse import OptionParser
from sumolib import checkBinary
import traci
import pandas as pd
import data_process
from parse_output import parse_output, calculate_offset


base_path = 'C:/Users/ssarker8/Desktop/beacon/beacon_dataset/' 
used_file = 'WGM_AN.csv' 
# dataset_name = 'raw_data/GWG_AN.csv'
output_file = "C:/Users/ssarker8/Desktop/beacon/beacon_dataset/output/"
# dataset_name = 'raw_data/WGM_N.csv' 
dataset_name = 'raw_data/WGM_AN.csv'
# dataset_name = 'raw_data/GWG_N.csv' 

base_dataset_name = os.path.splitext(os.path.basename(dataset_name))[0]

result_df = data_process.process_data(base_path, dataset_name) #direct call to process data then use it
result_df_unique_veh_ids = result_df['veh_id'].nunique()

# output_xml = f"{base_dataset_name}_output.xml" 
# output_xml = "intersection_4_output.xml"
output_xml = f"{base_dataset_name}_output.xml"
output_file_path = os.path.join(output_file, output_xml)
# # output_file_path = os.path.join(base_path, output_xml)
# print(f'P{output_file_path}')


##############################################  
parse_df = parse_output(output_file_path)
offset_df = calculate_offset(parse_df, dataset_name)

##############################################

def get_options():
    parser = OptionParser()
    parser.add_option("-f", "--nogui", action="store_true", default=False, help="run the commandline version of sumo", metavar="FILE")
    (options, args) = parser.parse_args()
    return options

def add_vehicle(vehicle_id, route, depart_time, depart_lane, arrival_lane, vehicle_type, color=None):
    traci.vehicle.add(
        vehID=vehicle_id,
        routeID=route,
        depart=depart_time,
        departLane=depart_lane,
        arrivalLane=arrival_lane,
        typeID=vehicle_type 

    )   
    if color is not None:
        traci.vehicle.setColor(vehicle_id, color)

def map_to_element(value, dataset_name):
    if (dataset_name == 'raw_data/GWG_AN.csv') or (dataset_name == 'raw_data/GWG_N.csv') :
        element_mapping = {
        1: 'e_1_2_0',
        2: 'e_1_2_1',
        3: 'e_6_5_4_3_3',
        4: 'e_6_5_4_3_2',
        5: 'e_6_5_4_3_1',
        6: 'e_6_5_4_3_0',
        7: 'e_7_8_0',
        8: 'e_7_8_1',
        9: 'e_9_10_11_2',
        10: 'e_9_10_11_1',
        11: 'e_9_10_11_0',
        12: 'e_12_13_0',
        13: 'e_12_13_1',
        14: 'e_14_15_16_17_3',
        15: 'e_14_15_16_17_2',
        16: 'e_14_15_16_17_1',
        17: 'e_14_15_16_17_0',
        18: 'e_18_19_0',
        19: 'e_18_19_1',
        20: 'e_20_21_22_2',
        21: 'e_20_21_22_1',
        22: 'e_20_21_22_0'
        }
    elif (dataset_name == 'raw_data/WGM_N.csv') or (dataset_name == 'raw_data/WGM_AN.csv') :
        element_mapping = {
        1: 'e_1_2_0',
        2: 'e_1_2_1',
        3: 'e_6_5_4_3_3',
        4: 'e_6_5_4_3_2',
        5: 'e_6_5_4_3_1',
        6: 'e_6_5_4_3_0',
        7: 'e_7_8_0',
        8: 'e_7_8_1',
        9: 'e_9_10_11_12_3',
        10: 'e_9_10_11_12_2',
        11: 'e_9_10_11_12_1',
        12: 'e_9_10_11_12_0',
        13: 'e_13_14_0',
        14: 'e_13_14_1',
        15: 'e_15_16_17_2',
        16: 'e_15_16_17_1',
        17: 'e_15_16_17_0',
        18: 'e_18_19_0',
        19: 'e_18_19_1',
        20: 'e_20_21_22_2',
        21: 'e_20_21_22_1',
        22: 'e_20_21_22_0'
        }
    else:
        raise ValueError("Invalid dataset")

    return element_mapping.get(value, None)

def extract_rightmost_int(element):
    parts = element.split('_')
    for part in reversed(parts):
        if part.isdigit():
            return int(part)

vehicle_colors = {
    'veh_40_1': (255, 0, 0),  # Red
    'veh_261_1': (0, 255, 0),  # Green
    'veh_264_1': (0, 0, 255),  # Blue
    'veh_1042_3': (255, 255, 0),  # Yellow
    'veh_1769_1': (255, 0, 255),  # Magenta
    'veh_2973_1': (0, 255, 255),  # Cyan
    'veh_3066_1': (128, 128, 128),  # Gray
}

def run(result_df):
    total_steps = int(result_df['step'].max()) + 1 
    simulation_data = []
    for step in range(1, total_steps + 1):
        print(f"Simulation step {step}")
        step_df = result_df[result_df['step'] == step]
        print(f"step_df: {step_df}")
        for _, row in step_df.iterrows():
            vehicle_id = row['veh_id']
            route_id = row['route_id']
            print(f"route_id: {route_id}")
            depart_lane = row['start_lane']
            print(f"depart_lane: {depart_lane}")
            arrival_lane = row['end_lane']
            print(f"arrival_lane: {arrival_lane}")
            if route_id in traci.route.getIDList():
                if vehicle_id not in traci.vehicle.getIDList():
                    departLane = extract_rightmost_int(map_to_element(depart_lane, dataset_name))
                    arrivalLane = extract_rightmost_int(map_to_element(arrival_lane, dataset_name))
                    color = vehicle_colors.get(vehicle_id)
                    add_vehicle(vehicle_id, route_id, step, departLane, arrivalLane, "idmCar", color)
                    print(f"{vehicle_id} added successfully in {route_id}")
                else:
                    print(f"{vehicle_id} already exists")
            else: 
                print(f"Invalid route_id: {route_id}")
        
        traci.simulationStep()
        vehicle_ids = traci.vehicle.getIDList()

        for vehicle_id in vehicle_ids:
            lane_id = traci.vehicle.getLaneID(vehicle_id)
            position = traci.vehicle.getPosition(vehicle_id)
            simulation_data.append({
                'step': step,
                'vehicle_id': vehicle_id,
                'lane_id': lane_id,
                'position_x': position[0],
                'position_y': position[1]
            })

        step += 1
    traci.close()
    simulation_df = pd.DataFrame(simulation_data)
    return simulation_df
    # sys.stdout.flush()


if __name__ == '__main__':
    options = get_options()
    
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else: 
        sumoBinary = checkBinary('sumo-gui')

    base_dataset_name = os.path.splitext(os.path.basename(dataset_name))[0]
    sumo_config_path = os.path.join(base_path, f"{base_dataset_name}.sumocfg")
    full_output_path = os.path.join(output_file, f"{base_dataset_name}_output.xml")
    print(f'sumo_config_path: {sumo_config_path} \n full_output_path {full_output_path} \n ')

    traci.start([
    sumoBinary, 
    "-c", sumo_config_path, 
    "--full-output", full_output_path 
    ])
    
    print("Starting SUMO")
    simulation_results = run(result_df)
    print(simulation_results)
    base_name = used_file.replace('.csv', '')
    save_dir = 'C:/Users/ssarker8/Desktop/beacon/beacon_dataset/output/'
    new_file_name = f"{base_name}_simulation_results.csv"
    save_path = os.path.join(save_dir, new_file_name)
    # save_path = '/home/tvillarr/Supriya/output/simulation_results.csv'
    simulation_results.to_csv(save_path, index=False)
    print(f"Simulation results saved to {save_path}")







