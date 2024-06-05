# -*- coding: utf-8 -*-
"""
Script to compare the benefits of staying at LEB8 or reducing to LEB4.

Uses the RPL staking state in staking_snapshot (currently 17 April).

Assumes the worst case scenario i.e everyone with more RPL than you reduces and everyone with less doesn't
"""

import random

import plotly.graph_objects as go
import numpy as np
import pandas as pd

df = pd.read_csv(r'./staking_snapshot.csv')

rpl_selection = 'staked_rpl_value_in_eth' #could change to 'liquid_rpl_node_value_in_eth' if desired
solo_apr = 0.04

# SETTINGS
voter_share = 0.05
LEB8_comm = 0.14
NO_comm = 0.035
ETH_only_pools = 0  #How many ETH-only pools join the protocol


#Graph settings
# draft_template = go.layout.Template()
# draft_template.layout.annotations = [
#     dict(
#         name="draft watermark",
#         text="DRAFT",
#         textangle=-30,
#         opacity=0.1,
#         font=dict(color="black", size=100),
#         xref="paper",
#         yref="paper",
#         x=0,
#         y=0,
#         showarrow=False,
#     )
# ]


def plot_data(x_data, y_data:dict, drag_line = None, title = 'Worst Case Earnings for Reducing', x_title = 'Percent Borrowed', y_title = 'Earnings relative to LEB8', renderer = 'png'):
  """Plotting function using plotly."""
  fig = go.Figure()
  for legend, y in y_data.items():
    fig.add_trace(go.Scatter(x=x_data, y=np.array(y),
                        mode='lines',
                        name=legend))
    
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
  
percent_borrowed_list = []
reduced_incentive = []
reward_if_stay = 24*solo_apr*LEB8_comm  #benefit of staying a LEB8
percent_reduced = []
total_minipools = df['nETH'].sum() / 8  # Convert everyone to LEB8 since we are comparing reducing further
  # (df['nETH'].sum()+df['pETH'].sum())/32

for percent_borrowed in np.arange(30, 50, 0.1):
  minipools_reduced = 0
  total_eligible_RPL = 0

  for node in df.iterrows():
    node = node[1]
    if node['nETH'] and node[rpl_selection] / (3*node['nETH']) > percent_borrowed/100:
      minipools_reduced += node['nETH'] / 8
      total_eligible_RPL += min(node[rpl_selection], node['nETH']*1.5)
    ## Could add randomness of people reducing anyway
    # elif random.random() < 0.25:
    #   minipools_reduced += node['nETH'] / 8
    #   total_eligible_RPL += min(node[rpl_selection], node['nETH']*1.5)
  new_minipools = 2 * minipools_reduced + ETH_only_pools
  ETH_to_voter_share = 28*new_minipools * solo_apr * voter_share
  ETH_per_RPL = ETH_to_voter_share / total_eligible_RPL
  reward_per_percent_borrowed = ETH_per_RPL *24/100
  reward_if_reduced = 56 * solo_apr * NO_comm + reward_per_percent_borrowed * percent_borrowed
  reduced_incentive.append(reward_if_reduced / reward_if_stay)
  percent_borrowed_list.append(percent_borrowed)
  percent_reduced.append(minipools_reduced / total_minipools)

  
# plot_data(percent_borrowed_list, {'Reduced Rewards':reduced_incentive}, title = f'Relative Earnings with {ETH_only_pools} ETH-only pools')
plot_data(percent_borrowed_list, {'Fraction Reduced':percent_reduced}, title = 'Minipool Fraction Reduced at Percent', y_title = 'Fraction of Pools')
