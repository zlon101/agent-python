import json


def process_yunxiao_data():
    """
    Process the Yunxiao task statistics JSON file by adding a new field "版本/迭代"
    to each item in the data array. The value is taken from either "版本" or "迭代" field.
    """
    # Read the input JSON file
    with open('test_云效任务统计.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Process each item in the data array
    for item in data['data']:
        # Check if "版本" field exists and is not "--"
        if '版本' in item and item['版本'] != '--':
            item['版本/迭代'] = item['版本']
        # Otherwise use "迭代" field if it exists and is not "--"
        elif '迭代' in item and item['迭代'] != '--':
            item['版本/迭代'] = item['迭代']
        # If both are "--" or missing, set to empty string
        else:
            item['版本/迭代'] = ''
        del item['版本']
        del item['迭代']

    # Write the modified data to the output file
    with open('test_云效任务2.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def count_unique_versions():
    """
    Count the number of unique values in the "版本/迭代" field in test_云效任务2.json.

    Returns:
        int: The number of unique "版本/迭代" values
    """
    # Read the processed JSON file
    with open('test_云效任务2.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Extract all "版本/迭代" values and create a set to get unique values
    versions = set()
    for item in data['data']:
        if '版本/迭代' in item:
            versions.add(item['版本/迭代'])

    # Return the count of unique values
    return versions


if __name__ == '__main__':
    # process_yunxiao_data()
    versions = count_unique_versions()
    unique_count = len(versions)
    print(f"Number of unique '版本/迭代' values: {unique_count}")
    print("Unique '版本/迭代' values:", versions)