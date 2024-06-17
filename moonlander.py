import glob
import os
import re
import pandas as pd
import matplotlib.pyplot as plt
from pandas.tseries.offsets import YearBegin
import numpy as np

# Get ids of participants
block_trials_files = glob.glob('data/*_block_trials.csv')
participants = [name.removeprefix('data/').removesuffix('_block_trials.csv') for name in block_trials_files]
print(f'Number of participants: {len(participants)}')

# Function to retrieve the indeces of switches for a trial
def get_switch_indeces(df) -> list[int]:
    switch_indeces = []
    was_active = False
    for index, row in df.iterrows():
        if was_active == True and row.active_task == False:
            switch_indeces.append(index)

        was_active = row.active_task

    return switch_indeces

# Function to retrieve the indeces of actions for a trial
def get_action_indeces(df) -> list[int]:
    action_indeces = []
    for index, row in df.iterrows():
        if not pd.isna(row.current_input):
            action_indeces.append(index)
        
    return action_indeces


difficulties = ['easy_easy', 'hard_easy']
tasks = ['avoid', 'collect']

action_switch_relations = {}

# Retrieve the action-switch relation of every participant for every trial
for participant in participants[:3]:
    # print(f'\r\nParticipant {participant}')
    participant_relations = {}
    for difficulty in difficulties:
        # print(f'   Difficulty {difficulty}')
        difficulty_relations = {}
        for task in tasks:
            # Get all trials for the current configuration
            regex = re.compile(f'{participant}_{difficulty}_no_{task}_[0-2].csv')
            trials_files = list(filter(regex.match, os.listdir('data')))

            # Retrieve action and switches for every trial
            trials_action_switch_relation = {}
            for trial in trials_files:
                trial_number = trial[-5]
                df = pd.read_csv(f'data/{trial}')
                actions = get_action_indeces(df)
                switches = get_switch_indeces(df)
                action_switch_relation = (len(actions)/len(switches))
                trials_action_switch_relation[trial_number] = action_switch_relation

            sorted_trials = dict(sorted(trials_action_switch_relation.items()))
            difficulty_relations[task] = sorted_trials

            # Print every single relation
            # for key, value in sorted_trials.items():
            #     print(f'      {task} - {key}: {value}' )
        
        participant_relations[difficulty] = difficulty_relations
    action_switch_relations[participant] = participant_relations



# Plotting
fig, ax = plt.subplots()
n_part = 3

for participant in participants[:n_part]:
    print(difficulties)
    for i, difficulty in enumerate(difficulties):
        relations = action_switch_relations[participant][difficulty]['avoid']
        avg_relation = sum(relations.values())/len(relations)
        min_relation = min(relations.values())
        max_relation = max(relations.values())
        print(f'{participant} - {difficulty} - Average: {avg_relation} Min: {min_relation} Max: {max_relation}')


# example data
# x = np.arange(0.1, 4, 0.5)
x = []
for n in range(n_part):
    x.append([n+0.25,n+0.4,n+0.55,n+0.7])

print(x)

y = np.exp(-x)
print(x)

# example error bar values that vary with x-position
error = 0.1 + 0.2 * x

fig, ax1 = plt.subplots(nrows=1, sharex=True)
# error bar values w/ different -/+ errors that
# also vary with the x-position
lower_error = 0.4 * error
upper_error = error
asymmetric_error = [lower_error, upper_error]

ax1.errorbar(x, y, yerr=asymmetric_error, fmt='o')
ax1.set_title('variable, asymmetric error')
ax1.set_yscale('log')
plt.show()