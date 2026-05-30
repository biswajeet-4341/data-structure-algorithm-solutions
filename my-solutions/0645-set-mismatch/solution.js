/**
 * @param {number[]} nums
 * @return {number[]}
 */
var findErrorNums = function(nums) {
    let map = new Map()

    for (let i of nums) {
        map.set(i, (map.get(i) || 0) + 1)
    }

    let ans = []
    for (let i = 1; i <= nums.length; i++) {
        if (!map.has(i)) ans[1] = i
        else if (map.get(i) > 1) ans[0] = i
    }

    return ans
};
