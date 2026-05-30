

/**
 * Note: The returned array must be malloced, assume caller calls free().
 */
int* shuffle(int* nums, int numsSize, int n, int* returnSize){
    int* ans = (int*)malloc(numsSize * sizeof(int));

    /*for (int i = 0, j = n, k = 0; i < n, j < 2 * n, k < numsSize; i++, j++, k += 2) {
        ans[k] = nums[i];
        ans[k + 1] = nums[j];
    }*/

    for (int i = 0; i < numsSize; i++) {
        if (i % 2 == 0) {
            ans[i] = nums[i / 2];
        } else {
            ans[i] = nums[n + i / 2]; // or nums[(2 * n + i) / 2]
        }
    }

    *returnSize = numsSize;
    return ans;
}
