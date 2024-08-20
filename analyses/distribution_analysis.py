# -*- coding: utf-8 -*-
"""
Created on Sat Aug 17 13:55:00 2024

@author: Cruncher
"""
import pdb
import glob
import json

import pandas as pd
import plotly.graph_objects as go
import numpy as np
from scipy import stats

directory = r'../../rp-snapshot/snapshot/'

intervals = [15451165, 15637542, 15839520, 16038366, 16238906, 16439406, 16639856, 16841781, 17037278, 17235705, 17434106, 17633377, 17832789, 18032731, 18232825, 18432450, 18632502, 18832296, 19031794, 19231376, 19431307, 19631250, 19830533, 20030845, 20231194, 20431741]


def get_snapshot_df():

  frames = []
  valid_intervals = []
  for i, block_id in enumerate(intervals):
    if glob.glob(f'{directory}{block_id}.csv'):
      frames.append(pd.read_csv(f'{directory}{block_id}.csv'))
      valid_intervals.append(i)
  df = pd.concat(frames, keys = valid_intervals)
    

  return df

def get_prices_df():
  df = pd.read_csv(f'{directory}prices.csv')
  return df

def gini_coefficient(x):
    """Compute Gini coefficient of array of values"""
    diffsum = 0
    for i, xi in enumerate(x[:-1], 1):
        diffsum += np.sum(np.abs(xi - x[i:]))
    return diffsum / (len(x)**2 * np.mean(x))

def process_data(weight_strategy = 'Node'):
  df = get_snapshot_df()
  prices = get_prices_df()
  
  columns = ['num_safe', 'num_safe_topped', 'num_topped', 'num_full_exit', 'num_exit_buy', 'num_exit_safe', 'num_stake_existing', 'num_dead', 'num_died', 'num_other', 'num_growing', 'inflow', 'outflow', 'minipools', "gini"]
  results = pd.DataFrame(columns = columns)
  full_exit_dist = []
  non_exit_dist = []
  for interval in range(10, 26):
    # start_block = intervals[interval-1]
    # end_block = intervals[interval]
    
    num_safe = 0            # started and ended above 10% without needing to add RPL
    num_safe_topped = 0     # would have ended over 10% but added RPL anyway
    num_topped = 0          # topped up to be over 10%
    num_full_exit = 0        # exited all minipools
    num_exit_buy = 0        # exited at least one minipool and bought RPL
    num_exit_safe = 0       # exited to stay above 10%
    num_stake_existing = 0  # staked RPL they had on their node / withdrawal to stay above 10%
    num_dead = 0            # started and ended below 10%
    num_died = 0            # started over 10% and ended below 10% without adding RPL
    num_other = 0   
    num_growing = 0         # pETH increased     
    staked_rpl_inflow = 0
    staked_rpl_outflow = 0
    eff_rpl = 0
    total_staked = 0
    minipools = 0
    gini_array = []
    
    start_ratio = prices.loc[interval-1, 'ratio']
    end_ratio = prices.loc[interval, 'ratio']
    previous_rewards_data = open_rewards(interval-1)
    rewards_data = open_rewards(interval)
    
    for node_index in range(len(df.loc[interval-1])):
      end = df.loc[interval, node_index]
      total_staked += end['staked_RPL']
      minipools += (end['nETH']+end['pETH'])/32
      start = df.loc[interval-1, node_index]
      
      if weight_strategy == 'Node':
        weighting = 1# end['staked_RPL']
      elif weight_strategy == 'Staked RPL':
        weighting = end['staked_RPL']
      elif weight_strategy == 'nETH':
        weighting = start['nETH']
      elif weight_strategy == 'pETH':
        weighting = start['pETH']
      else:
        raise ValueError
        
      if end['pETH'] > start['pETH']:
        num_growing += 1
        continue
      if start['nETH'] == 0 and end['nETH'] == 0:
        continue
      if end['pETH'] != 0:
        gini_array.append(end['staked_RPL']/end['pETH'])
      
      address = start['address'].lower()
      # with_address = start['withdrawal_address'].lower()

        
      # change_in_nETH = end['nETH'] - start['nETH']
      if address in previous_rewards_data:
        rewards_received = int(previous_rewards_data[address]['collateralRpl'])/1e18
      else:
        rewards_received=0
        
      # change_in_rpl = end['staked_RPL'] - start['staked_RPL'] - rewards_received
      if end['staked_RPL'] - start['staked_RPL'] - rewards_received > 0:
        staked_rpl_inflow += end['staked_RPL'] - start['staked_RPL'] - rewards_received
      elif end['staked_RPL'] - start['staked_RPL'] < 0:
        staked_rpl_outflow -= end['staked_RPL'] - start['staked_RPL']
      
      total_start_rpl = start['staked_RPL']+start['node_RPL']+start['withdrawal_RPL']
      total_end_rpl = end['staked_RPL']+end['node_RPL']+end['withdrawal_RPL']
      required_rpl_at_end = 0.1* end['pETH']/end_ratio
      
      if address in rewards_data and int(rewards_data[address]['collateralRpl']):
        non_exit_dist.append(start['staked_RPL']/start['pETH']*start_ratio)
        eff_rpl += end['staked_RPL']
        if start['staked_RPL'] >= required_rpl_at_end:
          if end['staked_RPL'] == start['staked_RPL'] or end['staked_RPL'] == start['staked_RPL']+rewards_received:
            num_safe += weighting
          else:
            num_safe_topped += weighting
        else:
          if end['nETH'] < start['nETH']:
            if total_start_rpl == total_end_rpl or total_start_rpl+rewards_received == total_end_rpl:
              # exited to top
              num_exit_safe += weighting
            elif total_start_rpl+rewards_received < total_end_rpl:
              num_exit_buy += weighting
            else:
              num_other +=weighting
              # pdb.set_trace()
          elif end['nETH'] == start['nETH']:
            if total_end_rpl - total_start_rpl - rewards_received > 1:
              num_topped += weighting
            else:
              num_stake_existing +=weighting
          else:
            num_other +=weighting
            # pdb.set_trace()
      else:
        if end['nETH'] == 0 and start['nETH']:
          num_full_exit +=weighting
          full_exit_dist.append(start['staked_RPL']/start['pETH']*start_ratio)
        else:
          non_exit_dist.append(start['staked_RPL']/start['pETH']*start_ratio)
          if start['staked_RPL']*start_ratio >= 0.1 * start['pETH']:
            num_died += weighting
          else:
            num_dead +=weighting
    fraction_eff = eff_rpl / total_staked
    gini = gini_coefficient(gini_array)
    # print(f'{interval=} {fraction_eff=}')
    total_counted = num_safe+num_safe_topped+num_topped+num_full_exit+num_exit_buy+num_exit_safe+num_stake_existing+num_dead+num_died+num_other+num_growing        
    results.loc[interval] = [num_safe/total_counted, num_safe_topped/total_counted, num_topped/total_counted, num_full_exit/total_counted, num_exit_buy/total_counted, num_exit_safe/total_counted, num_stake_existing/total_counted, num_dead/total_counted, num_died/total_counted, num_other/total_counted, num_growing/total_counted, staked_rpl_inflow, staked_rpl_outflow, minipools, gini]
    
  # plot_distribution(full_exit_dist, non_exit_dist)

  return results

def plot_distribution(exit_distribution, non_exit_distribution):
    exit_buckets = np.histogram(exit_distribution, bins=40, range=(0, 0.2))
    non_exit_buckets = np.histogram(non_exit_distribution, bins=40, range=(0, 0.2))
    
    plot_data(exit_buckets[1], {'hist':exit_buckets[0]/non_exit_buckets[0]}, title = 'Rate of Full Exit by % Borrowed', 
              x_title = '% Borrowed', y_title = 'Rate per Period', x_unit = 'pct', y_unit = 'pct')
    
    results = np.histogram(exit_distribution, bins=40, range=(0, 0.2))
    plot_data(results[1], {'hist':results[0]}, title = '% Borrowed at Previous Period for Full Exiting Nodes', 
              x_title = '% Borrowed', y_title = 'Count', graph_type = 'bar', x_unit = 'pct', y_unit = '')

def graph_results(results, weight_strategy = 'Node'):
  plot_data(results.index, {
                            "Didn't need to Top Up":results['num_safe'].to_numpy(),
                            'Topped up Anyway': results['num_safe_topped'].to_numpy(),
                            'Topped Up': results['num_topped'].to_numpy(),
                            # 'exited and bought':results['num_exit_buy'].to_numpy(),
                            # 'exited for rewards':results['num_exit_safe'].to_numpy(),
                            # 'staked existing RPL':results['num_stake_existing'].to_numpy(),
                            # 'full exit':results['num_full_exit'].to_numpy(),
                            'New Non-Top':results['num_died'].to_numpy(),
                            'Previous Non-Top':results['num_dead'].to_numpy(),
                            # 'Other':results['num_other'].to_numpy(),
                            # 'Increasing pETH':results['num_growing'].to_numpy(),
                            }, 
            title = f'Distribution weighted by {weight_strategy}', x_title = 'Interval', y_title = 'Fraction')
  plot_data(results.index, {
                            # 'Topped Up': results['num_topped'].to_numpy(),
                            'exited and bought':results['num_exit_buy'].to_numpy(),
                            'exited for rewards':results['num_exit_safe'].to_numpy(),
                            'staked existing RPL':results['num_stake_existing'].to_numpy(),
                            'full exit':results['num_full_exit'].to_numpy(),
                            'Increasing pETH':results['num_growing'].to_numpy(),
                            'Other':results['num_other'].to_numpy(),
                            }, 
            title = f'Distribution weighted by {weight_strategy}', x_title = 'Interval', y_title = 'Fraction')
  
  plot_data(results.index, {'gini':results['gini'].to_numpy()},
            title = 'Staked RPL Inequality Over Time', x_title = 'Interval', y_title = 'Gini Coefficient', y_unit = '')

def graph_flows_and_prices(results):
  plot_data(results.index, {
                            'Inflow': results['inflow'].to_numpy(),
                            'Outflow':results['outflow'].to_numpy(),
                            }, 
            title = f'Staked RPL Flows', x_title = 'Interval', y_title = 'RPL', y_unit = '')
  results['net_flow'] = results['inflow']-results['outflow']


  prices = get_prices_df()

  for i in range(len(prices)-1):
    prices.loc[i+1, 'change'] = (prices.loc[i+1, 'ratio'] - prices.loc[i, 'ratio']) / prices.loc[i, 'ratio']
  for i in results.index[:-1]:
    results.loc[i+1, 'minipool_flow'] = results.loc[i+1, 'minipools'] - results.loc[i, 'minipools']
  prices = prices.loc[10:]
  
  # # create trend lines
  # bestfit = stats.linregress(prices['change'], results['net_flow'])
  # results['rpl_flow_trendline'] = prices['change'] * bestfit[0] + bestfit[1]
  # bestfit = stats.linregress(prices['change'], results['minipool_flow'])
  # results['minipool_flow_trendline'] = prices['change'] * bestfit[0] + bestfit[1]
  
  
  
  plot_data(prices.index, {'Ratio':prices['ratio'].to_numpy()},
            title = 'End Price by Interval', x_title = 'Interval', y_title = 'Ratio', y_unit = '')  
  plot_data(prices.index, {'Change in Ratio':prices['change'].to_numpy()},
            title = 'Price Change by Interval', x_title = 'Interval', y_title = 'Change', y_unit = 'pct')  
  
  plot_data(prices['change'], {'correlation':results['net_flow']}, 
            x_title = 'Percent Change in RPL Ratio', y_title = 'Net Flow (RPL)', title = 'RPL Flows vs Ratio Change', 
            graph_type = 'markers+text', x_unit = 'pct', y_unit = '', text = list(prices.index))
  plot_data(prices['change'], {'correlation':results['minipool_flow']}, 
            x_title = 'Percent Change in RPL Ratio', y_title = 'Change in Minipools', title = 'Minipool Flows vs Ratio Change', 
            graph_type = 'markers+text', x_unit = 'pct', y_unit = '', text = list(prices.index))
  
  
    
def plot_data(x_data, y_data:dict, drag_line = None, title = 'Worst Case Earnings for Reducing', x_title = 'Percent Borrowed', y_title = 'Bonus Earnings relative to LEB8', renderer = 'png', graph_type = 'line', y_unit = 'pct', x_unit = '', text = None):
  """Plotting function using plotly."""
  fig = go.Figure()
  if y_unit == 'pct':
    yaxis = {'ticksuffix':' %'}
    y_mult = 100
  else:
    yaxis = {}
    y_mult = 1
  if x_unit == 'pct':
    xaxis = {'ticksuffix':' %'}
    x_mult = 100
  else:
    xaxis = {}
    x_mult = 1
  for legend, y in y_data.items():
    if graph_type == 'line':
      fig.add_trace(go.Scatter(x=x_data*x_mult, y=np.array(y)*y_mult,
                          mode='lines',
                          text = text,
                          name=legend))
    elif graph_type == 'bar':
      fig.add_trace(go.Bar(x=x_data*x_mult, y=np.array(y)*y_mult,
                          name=legend))
    elif graph_type == 'markers':
      fig.add_trace(go.Scatter(x=x_data*x_mult, y=np.array(y)*y_mult,
                          mode='markers',
                          text = text,
                          name=legend))
    elif graph_type == 'markers+text':
      fig.add_trace(go.Scatter(x=x_data*x_mult, y=np.array(y)*y_mult,
                          mode='markers+text',
                          text = text,
                          textposition = 'bottom center',
                          name=legend))
    else:
      raise TypeError


  fig.update_layout(title=title,
                   xaxis_title=x_title,
                   yaxis_title=y_title,
                   template = None,
                   yaxis = yaxis,
                   xaxis = xaxis,
                   # xaxis = {'range':[0, 1+max(x_data)]},
                   )
  fig.show(renderer = renderer, width = 800, height = 600, scale = 2)
    
def open_rewards(interval):
  with open(f'../../rp-snapshot/rewards/rp-rewards-mainnet-{interval}.json') as file:
    data = json.load(file)
  return data['nodeRewards']


if __name__ == '__main__':
  # df = get_snapshot_df()
  # prices = get_prices_df()
  for weight_strategy in ['Node', 'Staked RPL', 'nETH', 'pETH']:
    results = process_data(weight_strategy = weight_strategy)
    graph_results(results, weight_strategy = weight_strategy)
  graph_flows_and_prices(results)

