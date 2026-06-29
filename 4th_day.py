# Function to add two numbers given as strings
def sum_strings(a, b):
    # If empty string, treat as 0
    if a == "":
        a = "0"
    if b == "":
        b = "0"
    
    # Convert to integer, add, then convert back to string
    result = int(a) + int(b)
    return str(result)

# Input
a = input("Enter first number: ")
b = input("Enter second number: ")

# Output
print("Result:", sum_strings(a, b))