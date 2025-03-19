import pandas as pd
import openai
import nltk
from nltk.stem import WordNetLemmatizer

# Initialize the lemmatizer
nltk.download('wordnet')
nltk.download('omw-1.4')
lemmatizer = WordNetLemmatizer()

# Load the CSV files
output_file_path = ''
criteria_file_path = 'Top_tier_Identity_Unity_criteria.csv'

df_output = pd.read_csv(output_file_path)
df_criteria = pd.read_csv(criteria_file_path)

# Ensure that required columns are available in df_criteria
required_columns = ['Upper_tier_category', 'Identity_criteria', 'Unity_criteria']
if not all(col in df_criteria.columns for col in required_columns):
    raise ValueError("The criteria file does not contain the required columns: 'Upper_tier_category', 'Identity_criteria', 'Unity_criteria'.")

# Initialize new columns
df_output['Identity_Criteria_Check'] = ''
#df_output['Identity_Criteria_Details'] = ''
df_output['Unity_Criteria_Check'] = ''
#df_output['Unity_Criteria_Details'] = ''
df_output['reason_to_fail_identity'] = ''
df_output['reason_to_fail_unity'] = ''

# # Filter to only rows where 'anti_property_criteria' is 'YES'
# df_output = df_output[df_output['anti_property_criteria'].str.upper() == 'YES']

# OpenAI API setup
openai.api_key = " "  # Replace with your actual API key

def ask_gpt3_turbo(question):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an expert in characteristics matching between properties."},
            {"role": "user", "content": question}
        ]
    )
    return response['choices'][0]['message']['content']

def ensure_yes_no_response(response):
    """Ensures the response from GPT-3.5 is 'Yes' or 'No'. If not, ask GPT-3.5 again."""
    while response.lower() not in ['yes', 'no']:
        follow_up_question = f"Extract 'Yes' or 'No' from this response: {response}"
        response = ask_gpt3_turbo(follow_up_question)
    return response

# Iterate over each row in the filtered output dataframe
for idx, row in df_output.iterrows():
    category = row['Category']
    
    # Ensure category is a string before processing
    if isinstance(category, str):
        lemmatized_category = lemmatizer.lemmatize(category.lower())
    else:
        lemmatized_category = None

    # Proceed only if the lemmatized category is 'entity'
    if lemmatized_category == 'entity':
        upper_tier_category = row['Upper_tier_category_GPT_3.5']
        term = row['Answer']
        description = row['Description']

        # Normalize the strings for consistent matching
        upper_tier_category = upper_tier_category.strip().lower() if pd.notna(upper_tier_category) else None
        
        # Filter the criteria dataframe for matching upper tier category
        criteria_match = df_criteria[df_criteria['Upper_tier_category'].str.strip().str.lower() == upper_tier_category]
        
        if not criteria_match.empty:
            # Extract the respective identity and unity criteria for the upper tier category
            identity_criteria = criteria_match['Identity_criteria'].values[0]
            unity_criteria = criteria_match['Unity_criteria'].values[0]

            # Check and handle Identity Criteria
            if pd.isna(identity_criteria) or identity_criteria.strip() == '':
                df_output.at[idx, 'Identity_Criteria_Check'] = 'Yes'
            else:
                identity_question = f"Does the term '{term}' (which means '{description}') have these characteristics such as {identity_criteria}? Provide 'Yes' or 'No' without any explanations."
                identity_response = ask_gpt3_turbo(identity_question)
                identity_response = ensure_yes_no_response(identity_response)

                if identity_response.lower() == 'yes':
                    df_output.at[idx, 'Identity_Criteria_Check'] = 'Yes'
                else:
                    # Ask for a short explanation if the response is 'No'
                    df_output.at[idx, 'Identity_Criteria_Check'] = 'No'
                    explanation_question = f"Why does the term '{term}' (which means '{description}') fail to meet these identity criteria: {identity_criteria}? Provide a brief explanation."
                    reason_to_fail_identity = ask_gpt3_turbo(explanation_question)
                    df_output.at[idx, 'reason_to_fail_identity'] = reason_to_fail_identity

                df_output.at[idx, 'Identity_Criteria_Details'] = identity_criteria
            
            # Check and handle Unity Criteria
            if pd.isna(unity_criteria) or unity_criteria.strip() == '':
                df_output.at[idx, 'Unity_Criteria_Check'] = 'Yes'
            else:
                unity_question = f"Does the term '{term}' (which means '{description}') have these characteristics {unity_criteria}? Provide 'Yes' or 'No' without any explanations."
                unity_response = ask_gpt3_turbo(unity_question)
                unity_response = ensure_yes_no_response(unity_response)

                if unity_response.lower() == 'yes':
                    df_output.at[idx, 'Unity_Criteria_Check'] = 'Yes'
                else:
                    # Ask for a short explanation if the response is 'No'
                    df_output.at[idx, 'Unity_Criteria_Check'] = 'No'
                    explanation_question = f"Why does the term '{term}' (which means '{description}') fail to meet these unity criteria: {unity_criteria}? Provide a brief explanation."
                    reason_to_fail_unity = ask_gpt3_turbo(explanation_question)
                    df_output.at[idx, 'reason_to_fail_unity'] = reason_to_fail_unity

                df_output.at[idx, 'Unity_Criteria_Details'] = unity_criteria

# Save the updated dataframe back to the same CSV file
df_output.to_csv(output_file_path, index=False)

print(f"Updated CSV file with new columns 'Identity_Criteria_Check', 'Identity_Criteria_Details', 'Unity_Criteria_Check', 'Unity_Criteria_Details', 'reason_to_fail_identity', 'reason_to_fail_unity' has been saved.")
