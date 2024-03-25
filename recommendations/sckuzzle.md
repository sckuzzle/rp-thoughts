# End State
This proposal suggests a combination of the following individual concepts as a state for the protocol to work towards.

Val's Bond Curves
Universal Variable Commission
Sckuzzle's RPL Burn (discussed [here](../value-accruing/rpl-burn.md))
Epi's Unsmoothing Fee

## Individual Concepts

Each concept was selected for the following reasons:

### Epi's Unsmoothing Fee

It has been estimated that Rocketpool could suffer losses in the 5-10% range by NOs intentionally and profitably stealing from the protocol at present.  This would eliminate this loss.  

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

More detail can be read here [here](../value-accruing/rpl-burn.md)

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
[link]


Strengths:
* 

Weaknesses:
* Will likely cause NO supply to outpace pETH supply (mitigated by UVC)
* Weakened loss protection due to lower bond
* Favors large stakers with larger rewards

## Why they work well together

The most important thing to notice here is that we have several proposals which increase NO supply.  Universal Variable Commission is absolutely essential to balancing supply of pETH and NOs. 

With the lower bond curves, we also increase the potential losses due to theft.  Epi's unsmoothing fee eliminates this theft in a way that is fair to small stakers (rewards due favor large stakers, as in new bond curves).  