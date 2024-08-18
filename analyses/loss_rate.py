# -*- coding: utf-8 -*-
"""
Created on Thu Aug  1 08:48:25 2024

@author: Cruncher
"""

lido_rate = 95616 #eth per week
solo_apr = 0.035
rp_share = 0.3
eth_value = 3400
payback_period = 15 #years

yearly_loss = 0.09 * solo_apr * rp_share * lido_rate * 52 * eth_value/1000000

rpl_delta = yearly_loss * payback_period

dao_loss = rpl_delta * 0.015

print(f'{yearly_loss=}m')
print(f'{dao_loss=}m')