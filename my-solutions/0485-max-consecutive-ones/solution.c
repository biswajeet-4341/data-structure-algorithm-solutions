#define MAX(a, b) (((a) > (b)) ? (a) : (b))

int findMaxConsecutiveOnes(int* nums, int numsSize) {
    int count = 0, max_count = 0;
    
    for (int i = 0; i < numsSize; i++) {
        if (nums[i] == 1) {
            count++;
        } else {
            max_count = MAX(max_count, count);
            count = 0;
        }
    }

    return MAX(max_count, count);
}
