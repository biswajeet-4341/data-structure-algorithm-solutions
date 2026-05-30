/**
 * @param {string} word1
 * @param {string} word2
 * @return {string}
 */
var mergeAlternately = function(word1, word2) {
    let minLen = Math.min(word1.length, word2.length);
    
    let merged = "";
    for (let i = 0; i < minLen; i++) {
        merged += word1[i] + word2[i];
    }
    if (minLen == word1.length) merged += word2.slice(minLen);
    else merged += word1.slice(minLen);

    return merged;
};
