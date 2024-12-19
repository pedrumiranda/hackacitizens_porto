# Quasi-Identifiers (QIs): Attributes that do not directly identify an individual but can be used 
# in combination to re-identify them, such as birth date, ZIP code, and gender.
# It is crucial to correctly identify all QIs since k-anonymity revolves around ensuring that each 
# quasi-identifier pattern corresponds to a group of size ≥ k.

# Replace specific attribute values with more general categories or broader intervals. 
# For example, turning "29" into "20–30" or changing a ZIP code "12345" into "123**" or "123xx".

# Suppression:
# Completely remove outlier values or portions of quasi-identifying fields that cannot be safely 
# generalized without harming utility too much.

from mondrian.classes.data_frame_manager import DataFrameManager
from mondrian.classes.mondrian import Mondrian
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import random
import pandas as pd

def plot_test(dfm, qi):
    print('Started ananomyzation testing for different k values - this operation can take several minutes')

    k_list = [ 2, 10, 20, 40, 60, 80, 100 ]

    avg_list = [ ]

    for k_value in k_list:
        print('[DEBUG] - Started ananomyzation for k = %d' % k_value)

        mondrian = Mondrian(k_value, dfm, qi)
        mondrian.anonymize_aux()
        avg_list.append(round(mondrian.get_normalized_avg_equivalence_class_size(), 2))
        
        print('[DEBUG] - Finished ananomyzation for k = %d' % k_value)

    fig, ax = plt.subplots(figsize=(12,8))
    plt.plot(k_list, avg_list, marker='o')
    plt.xlabel('k')
    plt.ylabel('Normalized average equivalence class size metric (C AVG)')
    plt.title('Normalized average equivalence class size metric (C AVG) vs k')

    for index in range(len(k_list)):
        ax.text(k_list[index], avg_list[index], avg_list[index])

    plt.xticks(k_list)
    plt.grid()
    plt.savefig('./plot_output.jpg')


def main(input_path, qi, k, rid, plt_flag, output_path):

    # qi: variables that need to be generalized
    # k: number of paritions/groups identifiable
    # rid: to drop Pk if we want
    # plt_flag: test different k values to determine the best one

    df = pd.read_csv(input_path)

    if 'y' == rid:
        df.drop('id', inplace=True, axis=1) 

    print('[DEBUG] - ORIGINAL DATASET')
    print(df)

    dfm = DataFrameManager(df, qi)

    mondrian = Mondrian(k, dfm, qi)

    print('Starting anonymization for k = %d' % k)
    start = datetime.now()
    mondrian.anonymize_aux()
    end = (datetime.now() - start).total_seconds()

    print('Finished in %.2f seconds (%.3f minutes (%.2f hours))' % (end, end / 60, end / 60 / 60))
    print('Normalized average equivalence class size metric AVG %.2f' % mondrian.get_normalized_avg_equivalence_class_size())
    
    print('Writing anonymized data on file')
    mondrian.write_on_file(output_path)

    # used to test anonymization for different k values
    if 'y' == plt_flag:
        plot_test(dfm, qi)
    

if __name__ == '__main__':
    pass
