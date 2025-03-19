import pandas as pd

# Load the CSV file
file_path = '05_Sep_Aug_all_files.csv'  # Replace with your actual file path
df = pd.read_csv(file_path)

# Trim the cell values of ['GPT3.5_Rigidity'] and ['GPT3.5_Unity'] to remove any leading/trailing spaces
df['GPT3.5_Rigidity'] = df['GPT3.5_Rigidity'].str.strip()
df['GPT3.5_Unity'] = df['GPT3.5_Unity'].str.strip()

# Define the conditions for each check
conditions = [
    (df['Upper_tier_category_GPT_3.5'] == 'Agent') & (df['GPT3.5_Rigidity'] == '+R'),
    (df['Upper_tier_category_GPT_3.5'] == 'Group') & (df['GPT3.5_Unity'] == '+U'),
    (df['Upper_tier_category_GPT_3.5'] == 'Amount of Matter') & (df['GPT3.5_Unity'] == '+U')
]

# Apply conditions to determine if each row meets the anti-property criteria
df['anti_property_criteria'] = ['No' if any(cond) else 'Yes' for cond in zip(*conditions)]

# Save the updated dataframe back to the same CSV file
df.to_csv(file_path, index=False)

print(f"The updated CSV file has been saved with the new column 'anti_property_criteria'.")
