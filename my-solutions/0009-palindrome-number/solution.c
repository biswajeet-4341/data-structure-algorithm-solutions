bool isPalindrome(int x) {
    if (x < 0)
        return false;
    long palindrome = 0, temp = x;
    while (temp != 0)
    {
        palindrome = (palindrome * 10) + temp % 10;
        temp = temp / 10;
    }
    if (x == palindrome)
        return true;
    return false;
}
