from scipy import stats
import pandas as pd
import numpy as np
import sys


OUTPUT_TEMPLATE = (
    '"Did more/less users use the search feature?" p-value: {more_users_p:.3g}\n'
    '"Did users search more/less?" p-value: {more_searches_p:.3g}\n'
    '"Did more/less instructors use the search feature?" p-value: {more_instr_p:.3g}\n'
    '"Did instructors search more/less?" p-value: {more_instr_searches_p:.3g}'
)


def main():
    searchdata_file = sys.argv[1]
    data = pd.read_json(searchdata_file, orient='records', lines=True)
    # ...
    data_new = data[data['uid'] %2 ==1]
    data_old = data[data['uid'] %2 == 0]
    data_old_count = data_old.count(0)

    data_new_searched = data_new[data_new['search_count'] != 0]
    data_new_searched_count = data_new_searched.count(0)

    data_new_nosearched = data_new[data_new['search_count'] == 0]
    data_new_nosearched_count = data_new_nosearched.count(0)

    data_old_searched = data_old[data_old['search_count'] != 0]
    data_old_searched_count = data_old_searched.count(0)

    data_old_nosearched = data_old[data_old['search_count'] == 0]
    data_old_nosearched_count = data_old_nosearched.count(0)

    # instruction
    data_new_instr = data_new[data_new['is_instructor'] != 0]
    data_old_instr = data_old[data_old['is_instructor'] != 0]

    data_new_instr_searched = data_new_instr[data_new_instr['search_count'] != 0]
    data_old_instr_searched = data_old_instr[data_old_instr['search_count'] != 0]
    data_new_instr_nosearched = data_new_instr[data_new_instr['search_count'] == 0]
    data_old_instr_nosearched = data_old_instr[data_old_instr['search_count'] == 0]

    data_new_instr_searched_count =data_new_instr_searched.count(0)
    data_old_instr_searched_count = data_old_instr_searched.count(0)
    data_new_instr_nosearched_count =data_new_instr_nosearched.count(0)
    data_old_instr_nosearched_count = data_old_instr_nosearched.count(0)

    contingency_all = [[data_old_searched_count['uid'], data_old_nosearched_count['uid']],
                       [data_new_searched_count['uid'], data_new_nosearched_count['uid']]]
    chi2, p1, dof, expected = stats.chi2_contingency(contingency_all)
    p2 = stats.mannwhitneyu(data_new['search_count'], data_old['search_count']).pvalue

    contingency_instr = [[data_old_instr_searched_count['uid'], data_old_instr_nosearched_count['uid']],
                       [data_new_instr_searched_count['uid'], data_new_instr_nosearched_count['uid']]]
    chi2, p3, dof, expected = stats.chi2_contingency(contingency_instr)
    p4 = stats.mannwhitneyu(data_new_instr['search_count'], data_old_instr['search_count']).pvalue
    


    # Output
    print(OUTPUT_TEMPLATE.format(
        more_users_p=p1,
        more_searches_p=p2,
        more_instr_p=p3,
        more_instr_searches_p=p4,
    ))


if __name__ == '__main__':
    main()