/**
 * Definition for singly-linked list.
 * struct ListNode {
 *     int val;
 *     struct ListNode *next;
 * };
 */
struct ListNode* rotateRight(struct ListNode* head, int k) {
    if (head == NULL || head->next == NULL) {
        return head;
    }

    int count = 1;
    struct ListNode *front = head, *end = head;
    
    while (end->next != NULL) {
        count++;
        end = end->next;
    }

    if (k % count == 0) {
        return head;
    } 
    
    if (k > count) {
        k = k - ((k / count) * count);
    }
    end->next = head;
    for (int i = 0; i < count - k - 1; i++) {
        front = front->next;
    }
    head = front->next;
    front->next = NULL;
    return head;
}
