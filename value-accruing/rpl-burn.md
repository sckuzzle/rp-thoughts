# RPL Capture and Burn

This proposal covers sckuzzles value-capture and burn of RPL, resulting in a value-accruing token.

## Commission Rates

With this proposal there would be no RPL requirements to spin up a new minipool.  Instead, a portion of the commission is redirected towards the protocol.  Three knobs that can be adjusted are:

* Commission to Node Operators (NO)
* Commission to Protocol (for use in RPL burn)
* Increased commission to nodes with staked RPL

with all remaining ETH going towards rETH.

While NO commission can be defined by Universal Variable Commission (to ensure rETH and NO demand are balanced), it is less clear how Protocol Commission should be determined.

## Node Operators

We want to retain governance incentives in which nodes stake both RPL and ETH in a way in which they are awarded for it and have incentives aligned to the protocol.  In order to encourage staking the two together and aiding in governance, additional commission is offered.  

Each 1% of borrowed ETH value in RPL staked gives an additional 0.1% commission rate to the NO.  This can follow the current reduced efficiency after 15% from RPIP-39 (with the only differences being that there is no cliff under 10% and RPL can be unstaked at any percentage).  

The system is set up such that it is always beneficial to stake more RPL or ETH. 

## Purchase Mechanism

See [Valdorff's Buying Mechanism]().

## Governance

In order to minimize how much the protocol needs to change, governance being concentrated in nodes staking both ETH and RPL is being retained.  We do not need to redefine what staked RPL is or how much vote power is needed with this proposal.  

## Protocol Funding

The protocol funding will still, at least initially, be funded through RPL inflation.  This allows expenditure to be stable, reliable, and exceed commission if necessary.  It is expected and desirable that when the protocol grows, funding will instead be through collecting a portion of the ETH commission to the protocol.  

RPL inflation is to be capped at 1.5% of RPL in circulation (not burned) per annum, and can only be changed with a pDAO vote.  The distribution of these funds remains the same (sans NOs getting a portion).

Note: This version accrues value to all RPL tokens.  For a version that accrues value only to staked RPL (at the cost of complexity), read [here](./value-accruing-token.md). 