def merge_two_arrays(arr1, arr2, do_unique=False) -> list:
    merged_array = list(arr1) + list(arr2)

    # Handle uniqueness if requested
    if do_unique:
        # Preserve order while removing duplicates
        seen = set()
        unique_array = []
        for item in merged_array:
            if item not in seen:
                seen.add(item)
                unique_array.append(item)
        return unique_array

    return merged_array
