/**
 * @param {string} sentence
 * @return {boolean}
 */
var checkIfPangram = function(sentence) {
    let sentenceSet = new Set(sentence)

    for (let i = 97; i <= 122; i++) {
        if (!sentenceSet.has(String.fromCharCode(i))) return false
    }

    return true
};
