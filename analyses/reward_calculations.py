# -*- coding: utf-8 -*-
"""
Calculation of effective RPL and expected rewards under different schemes

@author: Cruncher
"""
import pdb


import pandas as pd
import numpy as np
import plotly.graph_objects as go

total_RPL = 20599081 / (1+0.05/13)
inflation = total_RPL * 0.05 *28/365 * 0.7
RPL_ratio =  0.005009384

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
under['weight'] =  100*under['staked_rpl_value_in_eth']# 1000 * under['staked_rpl_value_in_eth']**2 / under['pETH']

mid['weight'] = 100*mid['staked_rpl_value_in_eth']

over['weight'] = (13.6137+2*np.log(100*over['borrowed']-13))*over['pETH']

total_weight = under['weight'].sum() + mid['weight'].sum() + over['weight'].sum()
old_weight = mid['weight'].sum() + over['weight'].sum()
reduction = 1- old_weight / total_weight

my_rpl_in_eth = 15743.60 * RPL_ratio 
expected_rewards = my_rpl_in_eth * 100 / total_weight * inflation * RPL_ratio * 365/28

print(f'{expected_rewards=}')
print(f'{total_weight=}')
print(f'{reduction=}')

fraction_lst = []
percent_borrowed_list = []
for percent_borrowed in np.arange(50, 70, 0.1):
  weight = 0
  for group in [under, mid, over]:
    for node in group.iterrows():
      node = node[1]
      if node['borrowed'] >= percent_borrowed/100:
        weight += node['weight']
      # if np.isnan(node['weight']):
      #   pdb.set_trace()
  fraction_lst.append(weight/total_weight)
  percent_borrowed_list.append(percent_borrowed)

def plot_data(x_data, y_data:dict, drag_line = None, title = 'Worst Case Earnings for Reducing', x_title = 'Percent Borrowed', y_title = 'Bonus Earnings relative to LEB8', renderer = 'png', graph_type = 'line'):
  """Plotting function using plotly."""
  fig = go.Figure()
  for legend, y in y_data.items():
    if graph_type == 'line':
      fig.add_trace(go.Scatter(x=x_data, y=np.array(y),
                          mode='lines',
                          name=legend))
    elif graph_type == 'bar':
      fig.add_trace(go.Bar(x=x_data, y=np.array(y),
                          name=legend))
    else:
      raise TypeError


    
  if drag_line is not None:
    fig.add_trace(go.Scatter(x=[drag_line[0], drag_line[0]],
                             y = [drag_line[1], drag_line[2]],
                             name = 'Drag',
                             line = {'color':'red', 'width':4},
                             mode = 'lines',
                             ))
    
  fig.update_layout(title=title,
                   xaxis_title=x_title,
                   yaxis_title=y_title,
                   template = None,
                   xaxis = {'range':[0, 1+max(x_data)]})
  fig.show(renderer = renderer, width = 800, height = 600, scale = 2)
  
plot_data(percent_borrowed_list, {'Fraction Reduced':fraction_lst}, title = 'RPL Weighting Fraction at Percent Borrowed', y_title = 'Fraction of RPL Weight')


    
APR = 100 / total_weight * inflation  * RPL_ratio * 365/28