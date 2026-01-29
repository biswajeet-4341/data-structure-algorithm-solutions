/**
 * Definition for singly-linked list.
 * struct ListNode {
 *     int val;
 *     struct ListNode *next;
 * };
 */
struct ListNode* mergeTwoLists(struct ListNode* list1, struct ListNode* list2) {
    if (list1 == NULL) {
        return list2;
    } else if (list2 == NULL) {
        return list1;
    }

    struct ListNode *list3, *head;
    if (list1->val <= list2->val) {
        head = list3 = list1;
        list1 = list1->next;
    } else {
        head = list3 = list2;
        list2 = list2->next;
    }

    while (list1 != NULL && list2 != NULL) {
        if (list1->val <= list2->val) {
            list3->next = list1;
            list3 = list3->next;
            list1 = list1->next;
        } else {
            list3->next = list2;
            list3 = list3->next;
            list2 = list2->next;
        }
    }

    if (list1 == NULL) {
        list3->next = list2;
    } else {
        list3->next = list1;
    }

    return head;
}
