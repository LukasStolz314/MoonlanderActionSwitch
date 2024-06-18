import glob
import os
import re
import pandas as pd
import matplotlib.pyplot as plt
from pandas.tseries.offsets import YearBegin
import numpy as np
from statistics import median
import matplotlib.transforms as transforms

# Get ids of participants
block_trials_files = glob.glob('data\\*_block_trials.csv')
participants = [name.removeprefix('data\\').removesuffix('_block_trials.csv') for name in block_trials_files]
print(f'Number of participants: {len(participants)}')

# Meta information
difficulties = ['easy_easy', 'easy_hard', 'hard_easy', 'hard_hard']
tasks = ['avoid', 'collect']
n_part = len(participants)


# Function to retrieve the indeces of switches for a trial
def get_switch_indeces(df) -> list[int]:
    switch_indeces = []
    start_status = df.iloc[0].active_task
    was_active = start_status
    for index, row in df.iterrows():
        if start_status == True and was_active == True and row.active_task == False:
            switch_indeces.append(index)
        if start_status == False and was_active == False and row.active_task == True:
            switch_indeces.append(index)
        was_active = row.active_task

    if len(switch_indeces) == 0:
        switch_indeces = [-1]

    return switch_indeces

# Function to retrieve the indeces of actions for a trial
def get_action_indeces(df) -> list[int]:
    action_indeces = []
    for index, row in df.iterrows():
        if not pd.isna(row.current_input):
            action_indeces.append(index)
        
    return action_indeces

def process_and_plot(task, action_switch_relations, input_noise_on, y_limit):
    # Check average relation of every participant with min-max per difficulty
    fig, ax = plt.subplots(2, 2, figsize=(15, 5))
    ax = ax.flatten()
    fig.suptitle('Average relation of each participant per difficulty while performing task {task}')

    for i_diff, difficulty in enumerate(difficulties):
        min_error = []
        max_error = []
        average = []
        for i_part, participant in enumerate(participants[:n_part]):
            relations = action_switch_relations[participant][difficulty][task]
            avg_relation = sum(relations.values())/len(relations)
            min_relation = min(relations.values())
            max_relation = max(relations.values())
            print(f'{participant} - {difficulty} - Average: {round(avg_relation, 2)} Min: {round(min_relation, 2)} Max: {round(max_relation, 2)}')

            min_error.append(avg_relation - min_relation)
            max_error.append(max_relation - avg_relation)
            average.append(avg_relation)

        # Get all outliers
        overall_avg_median = median(average)
        print(f'Median average for difficulty {difficulty}: {round(overall_avg_median, 2)}')
        outlier = [i for i, v in enumerate(average) if v > y_limit]
        print(f'Removed following participants as outliers from difficulty {difficulty}: {outlier}')

        # Remove all outliers
        clean_average = list(np.delete(average, outlier))
        x = list(np.delete(np.arange(n_part), outlier))
        min_error = np.delete(min_error, outlier)
        max_error = np.delete(max_error, outlier)

        # Plot relations per difficulty
        error = [min_error, max_error]
        overall_avg_average = sum(clean_average)/len(clean_average)
        overall_min_average = overall_avg_average - sum(min_error)/len(min_error)
        overall_max_average = sum(max_error)/len(max_error) + overall_avg_average

        ax[i_diff].errorbar(x, clean_average, yerr=error, fmt='o')
        ax[i_diff].set_xticks(x)
        ax[i_diff].set_xlabel("Participants")
        ax[i_diff].set_title(difficulty)
        ax[i_diff].set_ylim(bottom=0, top=y_limit)

        # Setting average lines over participants for plot
        ax[i_diff].axhline(y=overall_avg_average, color='r', linestyle='-')
        ax[i_diff].axhline(y=overall_min_average, color='g', linewidth=0.5)
        ax[i_diff].axhline(y=overall_max_average, color='g', linewidth=0.5)

        trans = transforms.blended_transform_factory(ax[i_diff].get_yticklabels()[0].get_transform(), ax[i_diff].transData)
        ax[i_diff].text(0, overall_avg_average, round(overall_avg_average, 2), color="r", transform=trans, ha="right", va="center")
        ax[i_diff].text(0, overall_min_average, round(overall_min_average, 2), color="g", transform=trans, ha="right", va="center")
        ax[i_diff].text(0, overall_max_average, round(overall_max_average, 2), color="g", transform=trans, ha="right", va="center")

        print("")
        
    plt.tight_layout()
    #plt.show()
    plt.savefig(f"relation_difficulty_comparison_{task}_{input_noise_on}.png")
    print(f"Saved figure to: relation_difficulty_comparison_{task}_{input_noise_on}.png")

action_switch_relations = {}

def analyse_data(input_noise_on):
    # Retrieve the action-switch relation of every participant for every trial
    for participant in participants[:n_part]:
        # print(f'\r\nParticipant {participant}')
        participant_relations = {}
        for difficulty in difficulties:
            # print(f'   Difficulty {difficulty}')
            difficulty_relations = {}
            for task in tasks:
                # Get all trials for the current configuration
                regex = re.compile(f'{participant}_{difficulty}_{input_noise_on}_{task}_[0-2].csv')
                trials_files = list(filter(regex.match, os.listdir('data')))

                # Retrieve action and switches for every trial
                trials_action_switch_relation = {}
                for trial in trials_files:
                    trial_number = trial[-5]
                    df = pd.read_csv(f'data\\{trial}')
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
    return action_switch_relations

rel_no = analyse_data('no')
process_and_plot('avoid', rel_no, 'no', 8)
process_and_plot('collect', rel_no, 'no', 20)

rel_yes = analyse_data('yes')
process_and_plot('avoid', rel_yes, 'yes', 8)
process_and_plot('collect', rel_yes, 'yes', 20)

    


