# -*- coding: utf-8 -*-
"""
Script for calculating how profitable MEV theft is at various bond curves and comparing it to honest APR.
"""

import math


import plotly.graph_objects as go
import numpy as np

#globals
solo_apr = 0.05


def plot_data(x_data, y_data:dict, drag_line = None, title = None, x_title = 'Node ETH', y_title = 'Profitability (APR)', renderer = 'png'):
  """Plotting function using plotly."""
  fig = go.Figure()
  for legend, y in y_data.items():
    fig.add_trace(go.Scatter(x=x_data, y=np.array(y),
                        mode='markers',
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
                   yaxis_title=y_title)
  fig.show(renderer = renderer, width = 800, height = 600, scale = 2)


max_penalty = lambda node_eth, commission: node_eth/ (1-commission)  #max you can penalize the node for
unsmoothing_eq = lambda max_penalty: 0.23*math.exp(-0.69*math.log(max_penalty))  #eth at risk per validator per year


def generate_curves(nETH_per_pool: list, commission_per_pool: list):
  """Steps through each number of minipools, updating total nETH / pETH and calculating APRs at each point, before returning lists."""
  
  honest_total_profit = 0
  nETH = 0
  pETH = 0
  honest_apr = []
  theft_apr = []
  total_dishonest_apr = []

  protocol_apr = []
  honest_protocol_apr = []
  
  average_commission = 0
  
  for i in range(len(nETH_per_pool)):
    
    nETH += nETH_per_pool[i]
    pETH_in_new_pool = 32 - nETH_per_pool[i]
    pETH += pETH_in_new_pool
    
    # Update and record honest values
    honest_total_profit += solo_apr * (commission_per_pool[i] * (32-nETH_per_pool[i]) + nETH_per_pool[i])
    honest_total_apr = honest_total_profit / nETH
    
    honest_apr.append(honest_total_apr)
    
    # Update and record dishonest values
    average_commission = ( (pETH-pETH_in_new_pool) * average_commission + pETH_in_new_pool * commission_per_pool[i] ) / pETH
    max_penalizable = max_penalty(nETH, average_commission)
    unsmoothing_fee = unsmoothing_eq(max_penalizable)
    total_possible_theft = unsmoothing_fee * (i+1)
    
    theft_apr.append(total_possible_theft / nETH)
    
    total_dishonest_apr.append(total_possible_theft / nETH + honest_total_apr)
    
    assert not round(honest_total_apr - (pETH * average_commission  + nETH)*solo_apr/nETH, 7), "Methods don't match!"
    
    # Protocol Value
    total_protocol_value = pETH * (1-average_commission)*solo_apr
    
    protocol_apr.append((total_protocol_value - total_possible_theft) / pETH)
    honest_protocol_apr.append(total_protocol_value / pETH)

  return honest_apr, theft_apr, total_dishonest_apr, protocol_apr, honest_protocol_apr
  

def simple_example():
  """Looks at MEV theft and honest APR.  Does not calculate drag."""
  satellite_eth = 1.5
  initial_eth = [4, 4]
  pools_to_graph = 100
  
  nETH_per_pool = [*initial_eth, *[satellite_eth for n in range(pools_to_graph - len(initial_eth))]]
  
  # nETH_per_pool = [*initial_eth, *[initial_eth[-1]+satellite_eth*(1+n) for n in range(pools_to_graph - len(initial_eth))]]
  commission_per_pool = [0.025 for n in range(pools_to_graph)]
  
  # Calculate total nETH up to that point
  nETH = 0
  total_nETH = []
  for n in range(len(nETH_per_pool)):
    nETH += nETH_per_pool[n]
    total_nETH.append(nETH)
  
  honest_apr, theft_apr, total_dishonest_apr, _, _ = generate_curves(nETH_per_pool, commission_per_pool)
  
  
  plot_data(total_nETH, 
            {'Honest APR':honest_apr,
             'APR with Theft': total_dishonest_apr},
            title = 'MEV Theft Comparison',
            )
  
def example_with_drag(initial_eth = [4, 4], satellite_eth = 1.5):
  
  
  #Default.  ETH bond required per minipool will follow this list, then continue at satellite_eth for additional minipools
  pools_to_graph = 100
  NO_commission = 0.04
  protocol_cut = 0.14 - NO_commission #Used for calculated how much drag there is on the protocol
  
  # Construct lists of nETH and commission for each minipool
  nETH_per_pool = [*initial_eth, *[satellite_eth for n in range(pools_to_graph - len(initial_eth))]]
  commission_per_pool = [NO_commission for n in range(pools_to_graph)]
  
  # Calculate total nETH up to that point
  nETH = 0
  total_nETH = []
  for n in range(len(nETH_per_pool)):
    nETH += nETH_per_pool[n]
    total_nETH.append(nETH)
  
  #Create curves
  honest_apr, theft_apr, total_dishonest_apr, protocol_apr, honest_protocol_apr = generate_curves(nETH_per_pool, commission_per_pool)
  
  #Find where it is most profitable to steal MEV and then calculate what their APR is
  max_theft_index = total_dishonest_apr.index(max(total_dishonest_apr))
  max_theft_apr = total_dishonest_apr[max_theft_index]
  drag_lower = honest_apr[max_theft_index]
  rETH_drag = (honest_protocol_apr[max_theft_index] - protocol_apr[max_theft_index]) / honest_protocol_apr[max_theft_index]
  protocol_drag = rETH_drag / protocol_cut
  
  
  plot_data(total_nETH, 
            {'Honest APR':honest_apr,
             'APR with Theft': total_dishonest_apr},
            title = 'MEV Theft Comparison',
            drag_line = [total_nETH[max_theft_index], drag_lower, max_theft_apr],
            )
  
  print(f'rETH Drag: {rETH_drag*100}% or Protocol Drag:{protocol_drag*100}%')
  print(f'Max theft occurs at {max_theft_index+1} validators and {total_nETH[max_theft_index]} nETH')
  
  
  

if __name__ == '__main__':
  #samus
  # initial_eth = [4, 4, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 0.5, 0]
  
  #Default.  ETH bond required per minipool will follow this list, then continue at satellite_eth for additional minipools
  initial_eth = [4, 4]
  
  
  example_with_drag(initial_eth = initial_eth, satellite_eth = 1.5)