// SPDX-License-Identifier: GPL-3.0-or-later

pragma solidity 0.6.8;

import './HegicOptions.sol';
import './HegicCallOptions.sol';
import './HegicPutOptions.sol';

/**
 * @author jmonteer
 * @title Hegic AutoHedge
 * @notice XX
 */

 // TODO: Implement Hedge status
 // TODO: Implement hedging of Buy of ETH (simple: buy ATM puts)
 // TODO: Improve validations & checks using require()
 // TODO: Any implications of Hedge Expiry without exercising? Any way to implement auto close?
 // TODO: Remove double call to CalcHedge when calculating Hedge + Hedge Cost
 // TODO: comment code

 contract HegicHedgeContract {
    using SafeMath for uint256;

    string public name;
    HegicCallOptions public callProvider;
    HegicPutOptions public putProvider;
    Hedge[] public hedges;

    enum Trade{
        Buy,
        Sell
    }

    struct Hedge {
        uint256 hedgeID;
        address holder;
        string asset;
        uint256 amount;
        uint256 period;
        uint256 strike;
        Trade direction;
        uint256 optionID;
    }

    event Hedged(
        uint256 hedgeID,
        address payable holder,
        string asset,
        uint256 amount,
        uint256 period,
        uint256 strike,
        Trade direction,
        uint256 optionID
    );

    event ClosedHedge(
        uint256 hedgeID,
        address holder, 
        uint256 profit
    );

    constructor(HegicCallOptions cp, HegicPutOptions pp) public {
        name = "Hegic - AutoHedge";
        callProvider = cp;
        putProvider = pp;
    }

    /*
     * @nonce xx
     **/
    receive() external payable {}

     /**
     * @notice xx
     * @param _ETHAmount aaa
     */
     function hedge(uint256 _ETHAmount) public payable {
        require(_ETHAmount > 0, "Ups! Hedged amount must be valid!");

        uint256 totalFees = this.calcHedgeCost(_ETHAmount);
        require(totalFees == msg.value, "Ups! Fees are higher than msg.value...");

        // compute what specific options are needed to buy to hedge position
        (HegicOptions.OptionType optionType, uint256 strike, uint256 period, uint256 amount) = calcHedge(_ETHAmount);
        
        // buy calculated options through HegicOptions
        buyHedge(period, amount, strike);

        // log Hedge
     }

    /**
     * @notice xx
     * @param _ETHAmount aaa
     */
    function calcHedgeCost(uint256 _ETHAmount) external view returns (uint256 totalFees){
        (HegicOptions.OptionType optionType, uint256 strike, uint256 period, uint256 amount) = calcHedge(_ETHAmount);
        HegicOptions provider = callProvider;
        (totalFees, , ,) = provider.fees(period, amount, strike);
    }

     /**
     * @notice xx
     * @param _ETHAmount aaa
     */
     function calcHedge(uint256 _ETHAmount) internal view returns (HegicOptions.OptionType, uint256 strike, uint256 period, uint256 amount){
        HegicOptions provider = callProvider;
        AggregatorInterface priceProvider = callProvider.priceProvider();
         // basic ETH sale hedge for the next two weeks
         // buying equivalent amount of ATM Call Options, period: 2W
        HegicOptions.OptionType optionType = HegicOptions.OptionType.Call;
        strike = uint256(priceProvider.latestAnswer());
        period = 3600 * 24 * 7 * 2; // 2 weeks in seconds
        amount = _ETHAmount;
        return (optionType, strike, period, amount);
     }

     /**
     * @notice xx
     * @param _period aaa
     * @param _amount aaa
     * @param _strike aaa
     */
    function buyHedge(uint256 _period, uint256 _amount, uint256 _strike) public payable returns (uint256 optionID){
        // switch depending on hedge
        HegicOptions provider = callProvider;
        HegicETHPool pool = callProvider.pool();

        require(pool.availableBalance() >= _amount, "Ups! There is no enough available liquidity...");

        optionID = provider.create{value: msg.value}(_period, _amount, _strike);

        // need to check that it went right
        //require(optionID, "Ups! There was an error buying your hedge");
        uint256 hedgeID = hedges.length;
        Hedge memory h = Hedge(
            hedgeID,
            msg.sender,
            'ETH',
            _amount,
            _period,
            _strike,
            Trade.Sell,
            optionID
        );
        hedges.push(h);

        require(hedges.length == hedgeID + 1, 'There was an error saving your Hedge position');
        emit Hedged(hedgeID, msg.sender, 'ETH', _amount, _period, _strike, Trade.Sell, optionID);

    }

     /**
     * @notice xx
     */
     function closeHedge(uint256 _hedgeID) public {
         // retrieve position from Hegic
        HegicOptions provider = callProvider;
        Hedge storage h = hedges[_hedgeID];
        (HegicOptions.State oState, address payable oHolder, uint256 oStrike, uint256 oAmount, uint256 oPremium, uint256 oExpiration) = provider.options(h.optionID);
         // validations
        require(oPremium != 0, "Option not found in options provider!");
        // require(oHolder == h.holder, "Option retrieved has other holders address on it");

         // exercise position from Hegic
         provider.exercise(h.optionID);
        //How to check that everything executed correctly?

         // pay user (holder of hedge)
        uint256 profit = calcHedgeProfit(_hedgeID);
         // calc obtained profit
        payable(h.holder).transfer(profit);
         // save hedge's new state
        // importante: change memory to storage when declaring h

         // emit event
        emit ClosedHedge(_hedgeID, h.holder, profit);
     }

    // function toString(bytes memory data) public pure returns(string memory) {
    //     bytes memory alphabet = "0123456789abcdef";

    //     bytes memory str = new bytes(2 + data.length * 2);
    //     str[0] = '0';
    //     str[1] = 'x';
    //     for (uint i = 0; i < data.length; i++) {
    //         str[2+i*2] = alphabet[uint(uint8(data[i] >> 4))];
    //         str[3+i*2] = alphabet[uint(uint8(data[i] & 0x0f))];
    //     }
    //     return string(str);
    // }

     /**
     * @notice xx
     */
     function calcHedgeProfit(uint256 _hedgeID) public returns (uint256 profit) {
         HegicOptions provider = callProvider;
         Hedge memory h = hedges[_hedgeID];
         AggregatorInterface priceProvider = provider.priceProvider();
         uint256 currentPrice = uint256(priceProvider.latestAnswer());
         profit = currentPrice.sub(h.strike).mul(h.amount).div(currentPrice);

         return profit;
     }

     

 }