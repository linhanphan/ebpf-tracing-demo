# finding the maximum length of a subarray with elements that have difference of at most 1
# Time complexity: O(n)
# Space complexity: O(n)
# Test case: [1, 2, 2, 3, 1, 2] -> 5
# Test case: [1, 2, 3, 4, 5, 6, 7, 8, 9] -> 2
# Test case: [1, 1, 1, 1, 1, 1, 1, 1, 1] -> 9
# Test case: [1, 1, 2, 2, 2, 3, 3, 3, 4, 4] -> 6


def find_max_lenght(numbers) -> int:
    """
    Finds the maximum length of a subarray with elements that have difference of at most 1.
    Args:
        numbers (list): A list of integers.
    Returns:
        int: The maximum length of a subarray with elements that have difference of at most 1.
    """
    # create a dictionary to store the count of each element
    count = {}
    for num in numbers:
        if num not in count:
            count[num] = 1
        else:
            count[num] += 1
    # create a variable to store the maximum length
    max_length = 0
    # iterate through the dictionary
    for k in count:
        # find the maximum length with the previous and next element if they exist
        max_length = max(
            max_length,
            count[k] + count.get(k + 1, 0),
            count[k] + count.get(k - 1, 0),
        )
    # return the maximum length
    return max_length


# test cases
print(find_max_lenght([1, 2, 2, 3, 1, 2]))  # 5
print(find_max_lenght([1, 2, 3, 4, 5, 6, 7, 8, 9]))  # 2
print(find_max_lenght([1, 1, 1, 1, 1, 1, 1, 1, 1]))  # 9
print(find_max_lenght([1, 1, 2, 2, 2, 3, 3, 3, 4, 4]))  # 6
