
import os
import sys
from optparse import OptionParser
from sumolib import checkBinary
import traci
import pandas as pd
# from parse_output import parse_output  
sys.path.append('C:/Users/ssarker8/Desktop/beacon/beacon_dataset')
import data_process

base_path = 'C:/Users/ssarker8/Desktop/beacon/beacon_dataset/' 
signalized_cfg_path = 'C:/Users/ssarker8/Desktop/beacon/beacon_dataset/signalized/' 
# dataset_name = 'raw_data/GWG_AN.csv'
# dataset_name = 'raw_data/GWG_N.csv' 
# dataset_name = 'raw_data/WGM_N.csv' 
dataset_name = 'raw_data/WGM_AN.csv'

result_df = data_process.process_data(base_path, dataset_name)
print(result_df)



# output_xml = f"{dataset_name.split('.')[0]}_output.xml"
# output_file_path = os.path.join(base_path, output_xml)
# output_file_path = os.path.join(base_path, output_xml)
# print(f'P{output_file_path}')


# ##############################################
# parse_df = parse_output(output_file_path)
# offset_df = calculate_offset(parse_df, dataset_name)

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


def run(result_df):
    # total_steps = int(result_df['step'].max()) + 1 
    total_steps = int(result_df['step'].max()) + 1
    print(f"total_steps: {total_steps}")
    if (dataset_name == 'raw_data/GWG_AN.csv') or (dataset_name == 'raw_data/GWG_N.csv') :
        extra_steps = 15000  
    elif (dataset_name == 'raw_data/WGM_N.csv') or (dataset_name == 'raw_data/WGM_AN.csv') : 
        extra_steps = 200  
    extended_steps = total_steps + extra_steps
    simulation_data = []
    for step in range(1, extended_steps + 1):
    # for step in range(1, total_steps + 1):
        print(f"Simulation step {step}")
        step_df = result_df[result_df['step'] == step]

        for _, row in step_df.iterrows():
            vehicle_id = row['veh_id']
            route_id = row['route_id']
            depart_lane = row['start_lane']
            arrival_lane = row['end_lane']
            if route_id in traci.route.getIDList():
                if vehicle_id not in traci.vehicle.getIDList():
                    departLane = extract_rightmost_int(map_to_element(depart_lane, dataset_name))
                    arrivalLane = extract_rightmost_int(map_to_element(arrival_lane, dataset_name))
                    if vehicle_id == 'veh_181_1':
                        color = (255, 0, 0)  # Red
                    elif vehicle_id == 'veh_177_1':
                        color = (0, 255, 0)  # Green
                    else:
                        color = None  # Default color
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

        # step += 1
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
    sumo_config_path = os.path.join(signalized_cfg_path, f"{base_dataset_name}.sumocfg")
    full_output_path = os.path.join(base_path, "signalized", f"{base_dataset_name}_output.xml")
    print(f'sumo_config_path: {sumo_config_path} \n full_output_path {full_output_path} \n ')

    traci.start([
    sumoBinary, 
    "-c", sumo_config_path, 
    "--full-output", full_output_path 
    ])
    
    print("Starting SUMO")
    simulation_results = run(result_df)
    print(simulation_results)
    save_path = 'C:/Users/ssarker8/Desktop/beacon/beacon_dataset/signalized/simulation_results.csv'
    simulation_results.to_csv(save_path, index=False)
    print(f"Simulation results saved to {save_path}")
    

############################
###Conabd to run this python script

# sumo-gui -c /home/tvillarr/Supriya/intersection_2.sumocfg






