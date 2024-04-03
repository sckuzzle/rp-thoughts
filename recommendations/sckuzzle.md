# End State
This proposal suggests a combination of the following individual concepts as a state for the protocol to work towards.

* Val's Bond Curves
* Universal Variable Commission
* Sckuzzle's RPL Burn (discussed [here](../value-accruing/rpl-burn.md))
* Epi's Unsmoothing Fee

### Summary

For those familiar with tokenomics proposals already, a few highlights that differ from current thinking include:

* Including Epi's unsmoothing fee to protect against MEV theft
* A transition phase that phases down RPL requirements, ensuring those with the highest percent borrowed stake get priority from the deposit pool
* A Bonus Commission cut that is proportional to percent borrowed and the protocol's unstaked RPL 

## Individual Concepts

Each concept was selected for the following reasons:



### Universal Variable Commission

RocketPool has consistantly had an unbalanced demand for rETH and NOs which has significantly hampered growth of the protocol.  It is past time to implement UVC.  I am also advocating for doing this in a robust and automated fashion.

Integration Notes:
* With the addition of lower bond requirements and no-rpl-pools, I expect protocol growth with a bias towards onboarding new NOs.  UVC is essential to balance the rapidly changing forces we should expect to experience.
* pDAO voting on new commission rates occurs too slowly and inaccurately to properly handle the changing market forces.  It additionally has bad optics, as new users might be worried that the pDAO has too much power to rug part of the protocol.  An algorithm keeping things balanced makes for a stable and unbiased balancer that responds much faster than the pDAO can.  

Strengths:
* Balancing demand reduces the friction for more rETH minting and onboarding new NOs.  It helps to ensure that when someone decides to enter into the protocol that there is always room for them
* Provides incentives for whatever the protocol is lacking

Weaknesses:
* The details of the algorithm are difficult to grok.  Optics will have to focus on high-level overview
* It's possible some people will be hesitant to join when exact rewards are not known.  I think this is low-risk as ease of leaving means that people can leave if rewards fall (and further, this is a desirable balancing mechanism)

### Sckuzzle's RPL Burn

The basic idea is that minipools no longer require staked RPL.  Instead, the protocol takes a portion of the rewards and uses it to buy and burn RPL.

More detail can be read here [here](../value-accruing/rpl-burn.md).

Strengths:
* The existence of no-RPL-pools means that we should expect significantly more NOs, capturing more rewards for the protocol and increasing the expected value of RPL
* This approach has significant tax advantages as compared to other no-rpl-pool proposals
    * Taxable events are only created when a holder sells their RPL, meaning that they do not owe taxes on unrealized gains (from RPL inflation and ETH-commmission rewards) 
    * The number of taxable events are fewer, making it easier to file taxes
    * In countries with lower capital-gains taxes, this can signficantly increase take-home earnings (nearly doubling rewards in some cases)
* Much simpler than the value-accruing-tokens proposal submitted previously 

Weaknesses:
* This proposal increases the price of RPL, which means that wealth accrues to all RPL-holders rather than Nodes that stake RPL
* Mechanism for buying RPL to burn is not well-tested and could contain a portion of losses to MEV
* Will cause significantly increased supply of NOs (mitigated by UVC)



### Val's Bond Curves
[github link](https://github.com/Valdorff/rp-thoughts/tree/main/2024_02_strategy)


Strengths:
* Opens up greater capital efficiency for NOs, helping RP scale to meet high rETH demand
* Node-level capital increases safety while allowing for capital efficiency

Weaknesses:
* May cause NO supply to outpace pETH supply (mitigated by UVC)
* Less loss protection for 1-minipool nodes than current
* Favors large stakers with larger rewards (centralizing)

### Epi's Unsmoothing Fee

[Link](https://dao.rocketpool.net/t/options-forum-thread/2515/7?u=sckuzzle) to the forum post.  Dropdown 1. 

It has been estimated that Rocketpool could suffer losses in the 5-10% range by NOs intentionally and profitably stealing from the protocol at present.  This would eliminate this loss by allowing NOs to keep any MEV amount greater than their current maximum slashable bond level by instead paying a fee to the protocol for the privelege of being loaned the pETH.  

Strengths:
* Eliminates profitability of MEV theft
* Scales well with Val's bond curves 
    * Fee per minipool starts at 0.08 ETH/y but drops to 0.02 ETH/y at 15 pools (and continues dropping)

Weaknesses
* If the staking APR were to fall, this fee could cause the NO to have negative income with bad luck (no MEV)
* May be complicated to implement as MEV rates change over time

## Why they work well together

The most important thing to notice here is that we have several proposals which increase NO supply.  Universal Variable Commission is absolutely essential to balancing supply of pETH and NOs. 

With the lower bond curves, we also increase the potential losses due to theft.  Epi's unsmoothing fee eliminates this theft in a way that is fair to small stakers.  The two proposals complement each other nicely.

Lastly, Epi's unsmoothing fee makes income to the distributor more consistent over time, allowing UVC to use this assumption.  Without it it would be very difficult or impossible to implement UVC.

## Transition Phase

The combination of ETH-only pools and lower bond requirements has the potential to shift RocketPool from a nETH-limited protocol to pETH-limited, at least in the short term.  It would be most fair to ensure that NOs that have been with RocketPool already and have RPL staked are able to create minipools before ETH-only pools.  Therefor, there should be a 1-2 month long ramp-down phase where RPL bond requirements are steadily reduced, giving NOs with the largest amount of excess RPL staked first dibs on pETH in the deposit pool.  It could look something like

| Days to ETH-only pools | Percent Borrowed Requirement |
| -------- | ------- |
| 50 | 10% |
| 45 | 9% |
| 40 | 8% |
| etc. | ... |

Note: Epineph achieves the same effect through [queue priority](https://dao.rocketpool.net/t/2024-tokenomics-rework-drafts/2847/38?u=sckuzzle), which is probably easier to implement.  

### Alternate Intermediary

In addition to the time gate as above, it the intermediary phase could also include a DP-fullness gate.  The next-lower tier of percent borrowed would not open up until the deposit pool had at least 3000 ETH in it.  Gates would be forwards-only (once a gate is unlocked, it stays unlocked). 

## Other Notes

Upgrading the delegate would be required to benefit from any of the above.  Additionally, the delegate upgrade would opt you in to all of the above, from UVC to forced exits.  While some could stay on the old delegate and benefit both from their 14% commission and also the RPL-burn from the rest of the protocol, they would be stuck with LEB8s, not (potentially) benefit from UVC, and any other future upgrades.

I did not include rETH protection not because I don't think it would be good, but I haven't investigated it sufficiently to have an informed opinion.

## Requirements

AFAIK, the above proposals would require:

* Forced Exits
* Megapools (for ULEB1.5 to be profitable)
