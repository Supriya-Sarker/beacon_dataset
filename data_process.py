
import numpy as np
import pandas as pd
import os
from parse_output import parse_output, calculate_offset

def process_data(base_path, dataset_name):
    # dataset = 'intersection_2'
    dataset = os.path.splitext(os.path.basename(dataset_name))[0]
    complete_file_path = os.path.join(base_path, dataset_name)
    df = pd.read_csv(complete_file_path)
    print(f"{complete_file_path}")

    trim_spaces = lambda x: x.strip() if isinstance(x, str) else x
    df = df.applymap(trim_spaces)

    cols_with_nan = df.columns[df.isna().any()].tolist()
    if cols_with_nan:
        print("Columns with NaN values:", cols_with_nan)
    else:
        print("No NaN values found in any column.")
##################################################################
    # df = pd.read_csv(complete_file_path)

    # df = pd.read_csv(file_path)
    new_df = pd.DataFrame(df['timestep'])
    new_df['timestep_as_string'] = df['timestep'].astype(str)
    new_df['timestep_as_string'] = new_df['timestep_as_string'].str.replace(':00', '')

    new_df['minute'] = 0
    new_df['second'] = 0

    for index, row in new_df.iterrows():
        time_str = row['timestep_as_string']
        if ':' in row['timestep_as_string']:
            minutes, seconds = map(int, time_str.split(':'))
            new_df.at[index, 'minute'] = minutes
            new_df.at[index, 'second'] = seconds
        else:
            time_int = int(time_str)
            new_df.at[index, 'second'] = time_int
            new_df.at[index, 'minute'] = 0

    new_df['step'] = new_df['minute'] * 60 + new_df['second']

    columns = df.columns
    columns_new_df = new_df.columns

    df = pd.concat([df, new_df[['minute', 'second', 'step']]], axis=1)
    df_step_counts = df['step'].value_counts().reset_index()
    df_step_counts.columns = ['step', 'n_veh']
    df_step_counts = df_step_counts.sort_values(by='step', ascending=True)

    vehicle_ids = []
    step_id = []

    for index, row in df_step_counts.iterrows():
        step = row['step']
        count = row['n_veh']
        for i in range(1, count + 1):
            veh_id = f'veh_{step}_{i}'
            vehicle_ids.append(veh_id)
            step_id.append(step)

    vehicle_df = pd.DataFrame({'step': step_id, 'veh_id': vehicle_ids})

    df = pd.concat([df, vehicle_df[['veh_id']]], axis=1)
    nan_rows = df[df.isna().any(axis=1)]
    print("Rows with NaN values in any column:")
    print(nan_rows)


    df['start_lane'] = pd.to_numeric(df['start_lane'], errors='coerce').astype('int')
    # df['start_lane'] = pd.to_numeric(df['start_lane'], errors='coerce')
    # nan_rows = df[df['start_lane'].isna()]
    # print(f'nan_rows \n {nan_rows}')
    # print(f'nan_rows.index \n {nan_rows.index}')

    df['end_lane'] = pd.to_numeric(df['end_lane'], errors='coerce')
    df = df.dropna(subset=['end_lane'])
    df['end_lane'] = df['end_lane'].astype(int)
    count_start_lane = df['start_lane'].count()
    # print(count_start_lane)

    def generate_route_id(start_lane, end_lane):
        return f"route_{start_lane}_{end_lane}"

    df['route_id'] = df.apply(lambda row: generate_route_id(row['start_lane'], row['end_lane']), axis=1)
    # df['lane_change_time'] = df['step'] + 300  #no need
    # df['lane_change_time'] = df['lane_change_time'].astype(int)
    # print(f'df \n {df}')
    
    df_columns = df.columns
    # print(df_columns)
    
    used_df = df[['step', 'veh_id', 'route_id', 'start_lane', 'end_lane']]
    # unique_start_lane = used_df['start_lane'].unique()
    # unique_end_lane = used_df['end_lane'].unique()

    # used_file_name = f'used_df_{dataset}.csv'
    # # print(f'used_file_name: \n {used_file_name}')
    # if not os.path.exists(used_file_name):
    #     os.makedirs(used_file_name)
    # file_path = os.path.join(base_path, used_file_name)
    # # print(f'file_path: \n {file_path}')
    # used_df.to_csv(file_path, index=False)

    dataset_directory = f'processed_data'
    directory_path = os.path.join(base_path, dataset_directory)
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

    used_file_name = f'{dataset}.csv' 
    file_path = os.path.join(directory_path, used_file_name)

    used_df.to_csv(file_path, index=False)


    used_df_unique_veh_ids = used_df['veh_id'].nunique()
    print(f'Number of input unique veh_ids: {used_df_unique_veh_ids}')
    print(f"processed_data\n {used_df}")
    return used_df


# base_path = 'C:/Users/ssarker8/Desktop/beacon/beacon_dataset/'

# dataset_name = 'raw_data/WGM_AN.csv'
# result_df = process_data(base_path, dataset_name)
# print(result_df[:])
