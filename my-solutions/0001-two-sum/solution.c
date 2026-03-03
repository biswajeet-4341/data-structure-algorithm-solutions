/**
 * Note: The returned array must be malloced, assume caller calls free().
 */

typedef struct Node {
    int key;
    int value;
    struct Node *next;
} Node;

Node** create_table(int table_size) {
    Node **table = (Node**)malloc(table_size * sizeof(Node*));

    for (int i = 0; i < table_size; i++) {
        table[i] = NULL;
    }

    return table;
}

unsigned int hash_function(int key, int table_size) {
    long hash_value = (long)key;

    if (hash_value < 0) {
        hash_value = -hash_value;
    }

    return hash_value % table_size;
}

void insert(int key, int value, int table_size, Node **table) {
    unsigned int index = hash_function(key, table_size);

    Node* newNode = (Node*)malloc(sizeof(Node));
    newNode->key = key;
    newNode->value = value;
    newNode->next = table[index];
    table[index] = newNode;
}

Node* search(int key, int table_size, Node **table) {
    unsigned int index = hash_function(key, table_size);
    Node *current = table[index];

    while (current != NULL && current->key != key) {
        current = current->next;
    }

    return current;
}

void free_table(Node **table, int table_size) {
    for (int i = 0; i < table_size; i++) {
        Node *current = table[i];
        
        while (current != NULL) {
            Node *temp = current;
            current = current->next;
            free(temp);
        }
    }

    free(table);
}

int* twoSum(int* nums, int numsSize, int target, int* returnSize) {
    Node **table = create_table(numsSize);
    int *arr = (int*)malloc(2 * sizeof(int));

    for (int i = 0; i < numsSize; i++) {
        int curr_num = nums[i], curr_index = i;
        int complement = target - curr_num;

        Node* val_node = search(complement, numsSize, table);

        if (val_node == NULL) {
            insert(curr_num, curr_index, numsSize, table);
        } else {
            arr[0] = val_node->value;
            arr[1] = curr_index;
            break;
        }
    }

    *returnSize = 2;
    free_table(table, numsSize);
    return arr;
}
