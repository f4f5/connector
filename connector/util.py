"""
some useful function
"""
def opush(arr, v):
    """
    only push if v is not in arr
    """
    if arr.count(v) == 0:
        arr.push(v)