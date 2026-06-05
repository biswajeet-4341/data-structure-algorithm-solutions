/**
 * @param {number[][]} accounts
 * @return {number}
 */
var maximumWealth = function(accounts) {
    let maxWealth = 0

    for (let customer of accounts) {
        let wealth = customer.reduce((sum, bal) => sum + bal, 0)
        if (wealth > maxWealth) maxWealth = wealth
    }

    return maxWealth
};
