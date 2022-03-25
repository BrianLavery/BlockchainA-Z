// Briancoins ICO

// Version of compiler
pragma solidity ^0.8.7; // May need to use ^0.4.11 to get MEW to work (to read data)

// We give the contract a name and then define inside the {} brackets
contract briancoin_ico {

    // Maximum number of Briancoins for sale - public variable
    uint public max_briancoins = 1_000_000;

    // Define conversion rate for USD to Briancoins
    uint public usd_to_briancoins = 1_000;

    // Total number of Briancoins bought by investors
    uint public total_briancoins_bought = 0;

    // Mapping from investor address to equity in Briancoins and USD
    // Mapping is somewhat like an array
    mapping(address => uint) equity_briancoins; // this mapping takes address as input and returns uint
    mapping(address => uint) equity_usd;

    // Checking if an investor can buy Briancoins (need to have some left to buy)
    // This is essentially a function
    modifier can_buy_briancoins(uint usd_investment_amount) {
        require (usd_investment_amount * usd_to_briancoins + total_briancoins_bought <= max_briancoins); // Condition must be true to continue 
        _; // Underscore means that any function linked to modifier can only run if modifier is true
    }

    // Getting the equity in Briancoins of an investor - function
    // "address" is a type and "investor" is variable name
    // External constant (view - in new versions of solidity) is because address is outside contract and never changes - applies to parameters
    function equity_in_briancoins(address investor) external view returns (uint) {
        // Mapping above takes address of investor as input
        return equity_briancoins[investor];
    }

    // Getting equity in USD of an investor
    function equity_in_usd(address investor) external view returns (uint) {
        return equity_usd[investor];
    }

    // Buying Briancoins - multiple parameters, we apply our modifier
    function buy_hadcoins(address investor, uint usd_investment_amount) external can_buy_briancoins(usd_investment_amount) {
        uint briancoins_bought = usd_investment_amount * usd_to_briancoins; // We need to declare new variable here
        equity_briancoins[investor] += briancoins_bought; // This is the mapping above
        equity_usd[investor] = equity_briancoins[investor] / usd_to_briancoins;
        total_briancoins_bought += briancoins_bought;
    }

    function sell_hadcoins(address investor, uint briancoins_sale_amount) external {
        equity_briancoins[investor] -= briancoins_sale_amount; // This is the mapping above
        equity_usd[investor] = equity_briancoins[investor] / usd_to_briancoins;
        total_briancoins_bought -= briancoins_sale_amount;
    }

}