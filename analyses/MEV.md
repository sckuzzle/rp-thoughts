[MEV Script](./MEV_theft.py)

# MEV Theft Profitability

## Abstract

Lower bonds are good for capital efficiency but also open up the protocol to MEV theft.  While traditionally the focus is on capital efficiency for stakers, we instead look at the potential profit an MEV thief could make at various bond levels to determine what a bond curve should look like. This document explains how bonds were selected such that thieves were incentivized to minimize harm to the protocol while still being friendly to small node operators.

## The Problem

One of the larger changes in the new tokenomics is node-level collateral.  Node-level collateral allows for increased protection from MEV theft as node size increases, allowing for smaller bond levels (per minipool) than were previously possible.  This increases the capital efficiency (protocol ETH staked per node operator ETH), allowing a node operator to earn more from staking an increased amount of pETH and an increased rETH capacity available for LST holders.  

Unfortunately MEV theft profitability goes up at smaller bond levels as more minipools results in a larger chance to get a lottery block (or reduced node collateral at risk that the protocol can use to reclaim losses).    

## Approach

While incentive for MEV theft can never be completely eliminated, what we can do is to align a thief's profit incentive with good of the protocol.  This is achieved by ensuring that the thiefs maximum APR with theft (the combination of honest APR along with profit from stealing) occurs at a point where 


## Related Work
