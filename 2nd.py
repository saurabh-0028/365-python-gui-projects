#2Given a set of numbers, return the additive inverse of each. Each positive becomes negatives, and the negatives become positives.
#[1, 2, 3, 4, 5] --> [-1, -2, -3, -4, -5]
#[1, -2, 3, -4, 5] --> [-1, 2, -3, 4, -5]
#[] --> []
#You can assume that all values are integers. Do not mutate the input array.
# Function to find additive inverse
def invert_list(arr):
    result = []
    for i in arr:
        result.append(-i)
    return result

# Input
arr = list(map(int, input("Enter numbers: ").split()))

# Output
print(invert_list(arr))