The input arguments for this function are:
• IP1 (csvfile_1): The name of the CSV file (as string) containing the relationship
data between different statistical levels of areas for each state. The first row of the
CSV file will contain the headings of the columns. A sample CSV file
“SampleData_Areas.csv” is provided with the project sheet on LMS and Moodle.
• IP2 (csvfile_2): The name of the CSV file (as string) containing the record of
the population. The first row of the CSV file will contain the headings of the
columns. A sample CSV file “SampleData_Populations.csv” is provided with the
project sheet on LMS and Moodle.
• IP3 (age): Age as an integer.
• IP4 (sa2_1): String containing the code of an SA2 area.
• IP5 (sa2_2): String containing the code of another SA2 area.

Output
We expect 4 outputs in the order below.
OP1: Output will be a list including two integers, indicating the lower bound and the upper
bound of the age group containing the input age (IP3: age). Use None as the list element
if one of the bounds does not exist.
Note: The age group identified in this output will be used to calculate the other outputs.
OP2: Output will be a list of two lists.
The first list includes three elements in the order below:
1. the code of the SA3 area where input IP4 (sa2_1) is located,
2. the average of populations in the identified age group (OP1), across all SA2 areas
in this SA3 area,
3. the standard deviations of populations in the identified age group (OP1), across all
SA2 areas in this SA3 area.
The second list is similar to the first one, but for input IP5 (sa2_2).
OP3: Output will be a list of list(s). Each inner list corresponds to a unique state in the
data, including three elements in the order below:
1. the state name,
2. the name of the SA3 area with the largest population in the identified age group
(OP1), in the state,
3. the percentage of the population which you found above with respect to the total
population across all age groups in the same SA3 area.
The inner list(s) should be sorted in alphabetically ascending order by the state name.
Hint: Look for sort() or sorted() function.
When there are multiple areas with the same largest population, choose the first one in
alphabetical order in terms of area code.
OP4: Output will be a float number which is the correlation coefficient between the
populations in each age group in the first input IP4 (sa2_1), and the second input IP5
(sa2_2).

All returned numeric outputs (both in lists and individual) must contain values rounded to
four decimal places (if required to be rounded off). Do not round the values during
calculations. Instead, round them only at the time when you save them into the final
output variables.

Examples
Download SampleData_Areas.csv and SampleData_Populations.csv files from the
folder of Project 1 on LMS or Moodle. An example of how you can call your program from
the Python shell and examine the results it returns, is provided below:
>> OP1, OP2, OP3, OP4 = main('SampleData_Areas.csv',
'SampleData_Populations.csv', 18, '401011001', '401021003')
The returned output variables are:
>> OP1
[15, 19]

>> OP2
[['40101', 782.5, 376.8879], ['40102', 689.625, 493.9609]]

>> OP3
[['south australia', 'onkaparinga', 0.0595], ['tasmania', 'launceston',0.0591], ['western australia', 'wanneroo', 0.0694]]

>> OP4
0.0154
