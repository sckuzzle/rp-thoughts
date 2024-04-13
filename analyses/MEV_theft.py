# -*- coding: utf-8 -*-
"""
Created on Sat Apr 13 15:17:18 2024

@author: Cruncher
"""
import unittest
import math
import pdb

import plotly.graph_objects as go
import numpy as np

assertAlmostEqual = unittest.case.TestCase.assertAlmostEqual


#globals
solo_apr = 0.05


def plot_data(x_data, y_data:dict, drag_line = None, title = None, x_title = 'Node ETH', y_title = 'Profitability (APR)', renderer = 'png'):
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

# def profitability_curve(nETH_per_pool: list, commission_per_pool: list) -> list:
#   """Calculates the total APR for honest nodes at each minipool point."""
#   assert len(nETH_per_pool) == len(commission_per_pool), 'invalid list lengths!'
  
#   total_profit = 0
#   total_nETH = 0
#   apr = []
  
#   for i in range(len(nETH_per_pool)):
#     total_profit += solo_apr * (commission_per_pool[i] * (32-nETH_per_pool[i]) + nETH_per_pool[i])
#     total_nETH += nETH_per_pool[i]
#     total_apr = total_profit / total_nETH
    
#     apr.append(total_apr)
    
#   return apr

# def theft_curve(nETH_per_pool: list, commission_per_pool: list):
#   assert len(nETH_per_pool) == len(commission_per_pool), 'invalid list lengths!'
  
#   commission = 0
#   pETH = 0
#   nETH = 0
#   apr = []
  
#   for i in range(len(nETH_per_pool)):
    
#     pETH_in_new_pool = 32 - nETH_per_pool[i]
#     commission = ( pETH * commission + pETH_in_new_pool * commission_per_pool[i] ) / (pETH_in_new_pool + pETH)
    
#     pETH += pETH_in_new_pool
#     nETH += nETH_per_pool[i]

#     max_penalizable = max_penalty(nETH, commission)
#     unsmoothing_fee = unsmoothing_eq(max_penalizable)
#     total_possible_theft = unsmoothing_fee * i
    
#     apr.append(total_possible_theft / nETH)
    
#   return apr

def generate_curves(nETH_per_pool: list, commission_per_pool: list):
  
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
  
def example_with_drag():
  satellite_eth = 1.5
  
  #samus
  # initial_eth = [8, 0, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 0.5, 0]
  
  #Default 
  initial_eth = [4, 4]
  pools_to_graph = 50
  NO_commission = 0.025
  protocol_cut = 0.14 - NO_commission
  
  nETH_per_pool = [*initial_eth, *[satellite_eth for n in range(pools_to_graph - len(initial_eth))]]
  
  # nETH_per_pool = [*initial_eth, *[initial_eth[-1]+satellite_eth*(1+n) for n in range(pools_to_graph - len(initial_eth))]]
  commission_per_pool = [NO_commission for n in range(pools_to_graph)]
  
  # Calculate total nETH up to that point
  nETH = 0
  total_nETH = []
  for n in range(len(nETH_per_pool)):
    nETH += nETH_per_pool[n]
    total_nETH.append(nETH)
  
  honest_apr, theft_apr, total_dishonest_apr, protocol_apr, honest_protocol_apr = generate_curves(nETH_per_pool, commission_per_pool)
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
  
def protocol_value(honest_apr, nETH_per_pool):
  
  
  total_revenue = 0
  for i in range(len(nETH_per_pool)):
    pass
    
  
  

if __name__ == '__main__':
  example_with_drag()