def main(csvfile_1, csvfile_2, age, sa2_1, sa2_2):
    area_headers, area_data, population_headers, population_data = read_csv_file(csvfile_1, csvfile_2)

    age_range = findAgeRange(population_headers, age)
    
    sa2_list = [sa2_1, sa2_2]
    results = []

    for sa2 in sa2_list:
        sa3_code, related_sa2s = get_sa3_and_related_sa2(area_headers, area_data, sa2)
        if sa3_code is None:
            # If not found, return default values
            results.append([None, 0, 0])
        else:
            avg, sd = calculate_age_stats(population_headers, population_data, related_sa2s, age_range)
            if avg is None:
                results.append([sa3_code, 0, 0])
            else:
                results.append([sa3_code, round(avg, 4), sd])

    
    op3_result = statewise_sa3_agegroup_percentages(area_headers, area_data, population_headers, population_data, age_range)
    
    r = calculate_correlation(population_headers, population_data, sa2_1, sa2_2)
    
    return age_range, results, op3_result, r
        
def read_csv_file(csvfile_1, csvfile_2):
    # Read SampleData_Areas.csv
    with open(csvfile_1, 'r') as f:
        area_lines = f.readlines()

    area_headers = area_lines[0].strip().split(',')
    area_data = [[] for _ in range(len(area_headers))]

    for line in area_lines[1:]:
        d = line.strip().split(',')
        for i in range(len(area_headers)):
            if i < len(d):
                area_data[i].append(d[i])
                                
    # Read SampleData_Populations.csv
    with open(csvfile_2, 'r') as f:
        population_lines = f.readlines()

    population_headers = population_lines[0].strip().split(',')
    population_data = [[] for _ in range(len(population_headers))]

    for line in population_lines[1:]:
        d = line.strip().split(',')
        for i in range(len(population_headers)):
            if i < len(d):
                population_data[i].append(d[i])
                
    return area_headers, area_data, population_headers, population_data                           

def findAgeRange(headers, age):
    headers = [col for col in headers if col.startswith('Age ')]

    for col in headers:
        if ' and over' in col:
            lower = int(col.split('Age')[1].split(' and over')[0].strip())
            if age >= lower:
                return col
        else:
            parts = col.split('Age')[1].split('-')
            lower = int(parts[0].strip())
            upper = int(parts[1].strip())
            if lower <= age <= upper:
                return [lower, upper]  # return only when age is found in range

    return None  # if no match found

def get_sa3_and_related_sa2(area_headers, area_data, target_sa2_code):
    sa2_code_index = area_headers.index('SA2 code')
    sa3_code_index = area_headers.index('SA3 code')

    sa2_codes = area_data[sa2_code_index]
    sa3_codes = area_data[sa3_code_index]

    sa3_code = None
    for i in range(len(sa2_codes)):
        if sa2_codes[i] == target_sa2_code:
            sa3_code = sa3_codes[i]
            break

    if sa3_code is None:
        return None, []

    related_sa2_codes = []
    for i in range(len(sa3_codes)):
        if sa3_codes[i] == sa3_code:
            related_sa2_codes.append(sa2_codes[i])

    return sa3_code, related_sa2_codes

def calculate_age_stats(population_headers, population_data, related_sa2_codes, age_range_list):
    age_range_str = f'Age {age_range_list[0]}-{age_range_list[1]}'
    sa2_index = population_headers.index('Area_Code_Level2')
    age_index = population_headers.index(age_range_str)

    matched_values = []
    for i in range(len(population_data[0])):
        sa2_code = population_data[sa2_index][i]
        if sa2_code in related_sa2_codes:
            val = population_data[age_index][i]
            if val.isdigit():
                matched_values.append(int(val))

    if not matched_values:
        print(f"[Info] No population data found for related SA2s in age range {age_range_str}. Returning None.")
        return None, None

    average = sum(matched_values) / len(matched_values)

    if len(matched_values) == 1:
        print(f"[Info] Only one data point available for SD calculation in age range {age_range_str}. SD set to 0.")
        standard_deviation = 0
    else:
        variance = sum((val - average) ** 2 for val in matched_values) / (len(matched_values) - 1)
        standard_deviation = variance ** 0.5

    return average, round(standard_deviation, 4)

def statewise_sa3_agegroup_percentages(area_headers, area_data, population_headers, population_data, age_range):
    state_index = area_headers.index('S_T name')
    sa3_code_index = area_headers.index('SA3 code')
    sa3_name_index = area_headers.index('SA3 name')
    sa2_code_index = area_headers.index('SA2 code')

    pop_sa2_index = population_headers.index('Area_Code_Level2')
    age_col_name = "Age " + str(age_range[0]) + "-" + str(age_range[1])
    age_index = population_headers.index(age_col_name)

    # Prepare SA2 population map
    sa2_pop_map = {}
    for i in range(len(population_data[0])):
        sa2_code = population_data[pop_sa2_index][i]
        age_pop = int(population_data[age_index][i])
        total_pop = 0
        for j in range(2, len(population_headers)):
            total_pop += int(population_data[j][i])
        sa2_pop_map[sa2_code] = {
            'age_pop': age_pop,
            'total_pop': total_pop
        }

    # Map SA3s to population grouped by state
    state_sa3_map = {}

    for i in range(len(area_data[0])):
        state = area_data[state_index][i]
        sa3_code = area_data[sa3_code_index][i]
        sa3_name = area_data[sa3_name_index][i]
        sa2_code = area_data[sa2_code_index][i]

        if sa2_code not in sa2_pop_map:
            continue

        if state not in state_sa3_map:
            state_sa3_map[state] = {}

        if sa3_code not in state_sa3_map[state]:
            state_sa3_map[state][sa3_code] = {
                'sa3_name': sa3_name,
                'age_pop': 0,
                'total_pop': 0
            }

        state_sa3_map[state][sa3_code]['age_pop'] += sa2_pop_map[sa2_code]['age_pop']
        state_sa3_map[state][sa3_code]['total_pop'] += sa2_pop_map[sa2_code]['total_pop']

    # For each state, find SA3 with max age_pop (break tie using sa3_code alphabetically)
    result = []

    for state in state_sa3_map:
        max_age_pop = -1
        chosen_sa3_code = ""
        chosen_sa3_name = ""
        chosen_total_pop = 0
        for sa3_code in state_sa3_map[state]:
            entry = state_sa3_map[state][sa3_code]
            age_pop = entry['age_pop']
            total_pop = entry['total_pop']
            sa3_name = entry['sa3_name']
            if age_pop > max_age_pop:
                max_age_pop = age_pop
                chosen_sa3_code = sa3_code
                chosen_sa3_name = sa3_name
                chosen_total_pop = total_pop
            elif age_pop == max_age_pop:
                if sa3_code < chosen_sa3_code:
                    chosen_sa3_code = sa3_code
                    chosen_sa3_name = sa3_name
                    chosen_total_pop = total_pop

        if chosen_total_pop > 0:
            percentage = max_age_pop / chosen_total_pop
        else:
            percentage = 0.0

        result.append([
            state.lower(),
            chosen_sa3_name.lower(),
            round(percentage, 4)
        ])

    # Simple alphabetical sort by state name (first element of each inner list)
    for i in range(len(result)):
        for j in range(i + 1, len(result)):
            if result[i][0] > result[j][0]:
                temp = result[i]
                result[i] = result[j]
                result[j] = temp

    return result

def calculate_correlation(population_headers, population_data, sa2_1, sa2_2):
    # Step 1: Find the index of the SA2 code column
    sa2_index = -1
    for i in range(len(population_headers)):
        if population_headers[i] == "Area_Code_Level2":
            sa2_index = i
            break
    if sa2_index == -1:
        print("Error: 'Area_Code_Level2' column not found")
        return 0.0

    sa2_codes = population_data[sa2_index]

    # Step 2: Find the indexes of the age group columns
    age_indexes = []
    for i in range(len(population_headers)):
        if "Age" in population_headers[i]:
            age_indexes.append(i)

    if len(age_indexes) == 0:
        print("Error: No age group columns found")
        return 0.0

    # Step 3: Find the positions of sa2_1 and sa2_2
    pos1 = -1
    pos2 = -1
    for i in range(len(sa2_codes)):
        if sa2_codes[i] == sa2_1:
            pos1 = i
        if sa2_codes[i] == sa2_2:
            pos2 = i

    if pos1 == -1:
        print(f"Error: SA2 code '{sa2_1}' not found in population data")
        return 0.0
    if pos2 == -1:
        print(f"Error: SA2 code '{sa2_2}' not found in population data")
        return 0.0

    # Step 4: Extract age group values for both SA2s
    x_values = []
    y_values = []
    for idx in age_indexes:
        x_val = population_data[idx][pos1]
        y_val = population_data[idx][pos2]

        if x_val.replace('.', '', 1).isdigit() and y_val.replace('.', '', 1).isdigit():
            x_values.append(float(x_val))
            y_values.append(float(y_val))
        else:
            print("Error: Non-numeric value found in age data")
            return 0.0

    # Step 5: Calculate correlation
    n = len(x_values)
    if n == 0:
        print("Error: No valid age data to compute correlation")
        return 0.0

    x_mean = sum(x_values) / n
    y_mean = sum(y_values) / n

    numerator = 0
    x_denominator = 0
    y_denominator = 0

    for i in range(n):
        x_diff = x_values[i] - x_mean
        y_diff = y_values[i] - y_mean
        numerator += x_diff * y_diff
        x_denominator += x_diff ** 2
        y_denominator += y_diff ** 2

    if x_denominator == 0 or y_denominator == 0:
        print("Error: Zero variance encountered")
        return 0.0

    r = numerator / ((x_denominator ** 0.5) * (y_denominator ** 0.5))
    return round(r, 4)

"""
Debugging Documentation:

Issue 1 (Date 2025 April 09):
- Error Description:
Incorrect age range returned: `None` instead of a list like [15, 19]
- Erroneous Code Snippet:
age_range = findAgeRange(population_headers, age)
- Test Case:
main('SampleData_Areas.csv', 'SampleData_Populations.csv', 17, '401011001', '401021003')
- Variable Values:
age = 17
population_headers = [..., 'Age 15-19', 'Age 20-24', ...]
- Reflection:
The `findAgeRange()` function did not output a correct range for all the ages.
I discovered that the loop was missing valid matches whenever the header was not matched exactly with the parsing logic.
The solution was to enhance the logic to support all correct age header formats and ensure the return type was a list.
This taught me the value of verifying expected output formats and edge conditions like unmatched values.

---

Issue 2 (Date 2025 April 10):
- Error Description:
TypeError: type NoneType doesn't define __round__ method
- Erroneous Code Snippet:
results.append([sa3_code, round(avg, 4), sd]) 
- Test Case:
main('SampleData_Areas.csv', 'SampleData_Populations.csv', 65, '401011002', '4010210064')
- Variable Values:
avg = None, sa3_code = None (due to missing SA2 code)
- Reflection:
This mistake happened because `calculate_age_stats()` returned `None` in case there were no matching data.
and I simply forwarded that value to `round()`.
I fixed it by checking that `avg` is `None` and replacing it with 0.
This was a lesson, when handling missing or optional data.

---

Issue 3 (Date 2025 April 15):
- Error Description:
Incorrect ordering of final output – not sorted by state name alphabetically
- Erroneous Code Snippet:
result.sort()  # Removed in final version
- Test Case:
statewise_sa3_agegroup_percentages(area_headers, area_data, population_headers, population_data, (15, 19))
- Reflection:
I began utilizing Python's default `sort()` function believing that it would automatically sort the result by state names but it did not.
I implemented a simple nested loop sort to order the result by the first entry of each inner list (state name).
This learning experience taught me to think algorithmically and code with the bare basics of Python, alone.
"""




