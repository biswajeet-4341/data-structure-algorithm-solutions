/**
 * @param {number} n
 * @return {number[]}
 */
var lexicalOrder = function(n) {
    let result = []

    for (let i = 1; i <= n; i++) {
        result.push(i)
    }

    return result.sort()
};
