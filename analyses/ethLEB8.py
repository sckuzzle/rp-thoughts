# -*- coding: utf-8 -*-
"""
Created on Wed Jul 31 12:40:11 2024

@author: Cruncher
"""

import pandas as pd
import numpy as np

total_RPL = 20599081 / (1+0.05/13)
inflation = total_RPL * 0.05 *28/365 * 0.7

df = pd.read_csv('staking_snapshot.csv')

df['borrowed'] = df['staked_rpl_value_in_eth'] / df['pETH']

#filter
df = df[df['nETH']>0]

# under 10%
under = df[df['borrowed'] < 0.10].copy()

# 10 to 15%
mid = df[df['borrowed'] <= 0.15].copy()
mid = mid[mid['borrowed'] >= 0.1]

# over 15%
over = df[df['borrowed'] > 0.15].copy()

# normal rewards use a cliff, set to 0
under['weight'] =  0*100*under['staked_rpl_value_in_eth']# 1000 * under['staked_rpl_value_in_eth']**2 / under['pETH']

mid['weight'] = 100*mid['staked_rpl_value_in_eth']

over['weight'] = (13.6137+2*np.log(100*over['borrowed']-13))*over['pETH']

total_weight = under['weight'].sum() + mid['weight'].sum() + over['weight'].sum()
old_weight = mid['weight'].sum() + over['weight'].sum()
reduction = old_weight / total_weight

my_rpl_in_eth = 15743.60 * 0.004586
expected_rewards = my_rpl_in_eth * 100 / total_weight * inflation

print(f'{expected_rewards=}')
print(f'{total_weight=}')
print(f'{reduction=}')

