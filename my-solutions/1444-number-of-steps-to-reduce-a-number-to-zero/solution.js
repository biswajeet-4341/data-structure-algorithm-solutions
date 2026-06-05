/**
 * @param {number} num
 * @return {number}
 */
var numberOfSteps = function(num) {
    let steps = 0

    while (num > 0) {
        num = !(num & 1) ? num >> 1 : --num
        steps++
    }

    return steps
};
