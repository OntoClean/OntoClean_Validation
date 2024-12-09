import pandas as pd
import openai
import nltk
from nltk.stem import WordNetLemmatizer

# Set your OpenAI API key here
openai.api_key = ""

# Initialize the WordNetLemmatizer
nltk.download('wordnet')
lemmatizer = WordNetLemmatizer()

def finding_taxonomy_placement(helper, story, cq, footer):
    prompt = f"{helper}\n\n{story}\n\n{cq}\n\n{footer}"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a highly knowledgeable assistant asked to categorize terms based on specific meta properties."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=250,
            temperature=0.25,
            top_p=0.9
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"An error occurred: {e}")
        return "Error generating response"

def refine_meta_property(property_name, initial_response):
    valid_rigidity = {'+R', '-R', '~R'}
    valid_identity = {'+I', '-I', '+O'}
    valid_unity = {'+U', '-U', '~U'}

    if property_name == 'rigidity' and initial_response not in valid_rigidity:
        correction_prompt = (
            f"Please extract the exact value such as +R, -R, or ~R from the '{initial_response}' without any explanations, ensuring it is only 2 characters."
        )
    elif property_name == 'identity' and initial_response not in valid_identity:
        correction_prompt = (
            f"Please extract the exact value such as +I, -I, or +O from the '{initial_response}' without any explanations, ensuring it is only 2 characters."
        )
    elif property_name == 'unity' and initial_response not in valid_unity:
        correction_prompt = (
            f"Please extract the exact value such as +U, -U, or ~U from the '{initial_response}' without any explanations, ensuring it is only 2 characters."
        )
    else:
        return initial_response  # The initial response is valid, no correction needed

    try:
        refined_response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a highly knowledgeable assistant asked to provide corrected meta properties based on initial inputs."},
                {"role": "user", "content": correction_prompt}
            ],
            max_tokens=10,
            temperature=0.5,
            top_p=0.9
        )
        # Extract only the correct value from the response
        extracted_value = refined_response['choices'][0]['message']['content'].strip()
        return extracted_value
    except Exception as e:
        print(f"An error occurred during refinement: {e}")
        return initial_response  # Fall back to the initial response if an error occurs

def main():
    # Ensure the API key is set
    if openai.api_key is None:
        print("Error: OpenAI API key is not set.")
        return

    
    file_path = '.csv'
    df = pd.read_csv(file_path, encoding='ISO-8859-1')

    #df = pd.read_csv(file_path)

    # Add new columns for results if not already present
    for col in ['Rigidity', 'Identity', 'Unity']:
        if col not in df.columns:
            df[col] = ""

    # Dictionary to store already processed terms
    processed_terms = {}

    helper_rigidity = (
        "Rigid (+R): A property is rigid if it is essential to all its instances across all possible contexts. Such a property cannot be lost without the entity ceasing to exist. "
        "It underlines the property's essential and unchangeable nature. For example, when we think about an individual vegetable such as broccoli or mushroom, in ontological theory it is assumed that being a vegetable is a rigid property and can clearly be isolated from each other.\n"
        "The property 'Animal' is considered rigid because it is essential to the identity of any instance categorized as an animal. If an entity is an animal, it must be an animal in every possible world where it exists. This property is inherent and unchangeable for the entity.\n"
        "Anti-Rigid (~R): A property is anti-rigid if it is not necessarily essential to its instances. Entities can gain or lose such properties without ceasing to exist, highlighting the property's variable and non-essential nature. "
        "An exemplary case of an anti-rigid property is 'Catalyst', where we define a catalyst as any factor that contributes causally to an occurrence, such as an individual, atmospheric conditions, or a chemical reaction. "
        "If any living being is in a stage of their life cycle the rigidity property is anti-rigid. In amphibians like frogs, the tadpole is a larval stage. Just as a butterfly was once a caterpillar, a frog was once a tadpole. Therefore their rigidity property is anti-rigid."
        "This stage is temporary and non-essential to the identity of the frog in its entirety. This is classified as anti-rigid.\n"
        "Non-Rigid (-R): A property that is not essential to some of its instances, indicating that it can vary or not be present at all in certain instances without affecting the core essence of the entity. "
        "For example, the property of being a student is non-rigid because an individual can be a student at one time and not a student at another time without changing their core identity."
    )
    helper_identity = (
        "In ontological studies, the concept of 'Identity' plays a crucial role in distinguishing and categorizing entities based on their intrinsic and relational properties. "
        "The meta-property 'Identity' refers to a system of criteria (IC) used to determine when two or more instances of a property are considered identical—that is, they represent the same entity or belong to the same class of entities. "
        "This determination is made through a set of necessary and sufficient conditions that enable the recognition and re-identification of entities across different contexts and times.\n"
        "The meta-property 'Identity' can be broken down into two main components, carrying identity (+I) and supplying identity (+O), each serving a distinct function within the ontology:\n"
        "Carrying Identity (+I): This aspect indicates that instances of a property inherit or carry a unique identification criterion from a superclass. It suggests that the property in question does not itself supply the criteria for its instances' identity "
        "but relies on a more fundamental or encompassing property to provide this basis. For example, the property 'Student' carries identity, as it inherits identity criteria from the more foundational property 'Person,' implying that a student's identity is contingent upon the identity of the person who is the student. Therefore 'Person' supplies an identity which is +O and the student carries an identity which is +I.\n"
        "The property 'Red' does not carry identity because it does not provide a unique criterion for identifying an entity. If two apples are both red, the property 'Red' does not help us distinguish one apple from the other. The identity of the apples comes from other properties, such as their shape, size, or origin, not from their color. Therefore, the property 'Red' does not carry identity and is labeled with -I."
    )

    helper_unity = (
        "The concept of Unity in the OntoClean methodology is about recognizing the parts and boundaries of objects such that we know what is part of the object, what is not, and under what conditions the object is considered whole.\n"
        "Unity can significantly inform the intended meaning of properties within an ontology. Some properties imply that all their instances are wholes, while others do not. For example, being an ocean implies a property that picks up whole objects as its instances, like Atlantic Ocean, which are recognizable as single entities. \n"
        "However, being an amount of water does not have wholes as instances, since each amount can be arbitrarily scattered or confused with other amounts, indicating that knowing an entity is an amount of water, doesn't tell us anything about its parts or how to recognize it as a single entity. "
        "The property 'Physical Object' is an example of unity because it denotes entities that are topological wholes. A physical object, like a chair or a car, has a clearly defined boundary and parts that together form a single, unified entity. For instance, removing a leg from a chair alters its identity as a whole chair, emphasizing that all parts are necessary for the object to be considered complete. Therefore property chair carries +U. The unity criterion here is the topological cohesion of the object.\n"
        "all instances must be wholes according to a common Unity Criterion (UC) and -U for properties where instances are not necessarily wholes 'Legal Agent' is considered to carry no unity (-U) because it includes both individuals (like a person) and organizations (like a company), each with different unifying criteria. A legal agent does not have a consistent unifying criterion across all its instances. For example, a person and a corporation are both recognized as legal agents, but they are unified in very different ways—one biologically, the other structurally and legally. Thus, the property lacks a single unity criterion that applies to all its instances​. \n"
        "The property 'Group' is considered to have anti-unity because it refers to a collection of entities that do not form a unified whole under a single criterion. For example, a group of people does not have a specific unifying criterion that makes it a cohesive entity. The members of the group can be scattered across different locations, and the group can still be considered the same group regardless of how its members are arranged. There is no inherent unity that ties the group together as a single, indivisible entity, which is why 'Group' is classified as having anti-unity (~U)./n"
        "Amount of Matter is typically assigned anti-unity (~U). because its instances are not cohesive wholes with intrinsic boundaries"
    
    )

    footer = (
        "Ensure to follow the definitions and examples provided in the helper section to classify the property accurately. Avoid common pitfalls such as misclassifying based on non-essential characteristics or providing explanations instead of the classification."
    )

    for index, row in df.iterrows():
        if pd.notna(row['Description']) and pd.notna(row['Category']):
            # Lemmatize the category
            category = lemmatizer.lemmatize(row['Category'].strip().lower())

            # Check if the lemmatized category is 'entity'
            if category == 'entity':
                term = row['Answer']
                description = row['Description']

                # Check if the term has already been processed
                if term in processed_terms:
                    # Use previously generated values
                    rigidity_response = processed_terms[term]['rigidity']
                    identity_response = processed_terms[term]['identity']
                    unity_response = processed_terms[term]['unity']
                    upper_tier_response = processed_terms[term]['upper_tier']
                else:
                    # Process the term if it hasn't been processed
                    story = f"The goal is to classify the meta properties for the term '{term}' based on its description and the context provided."

                    cq_rigidity = f"Competency Question: Provide the rigidity property for '{term}' (which means '{description}') as either +R, -R, or ~R without any explanations. The answer should be either +R, -R, or ~R."
                    cq_identity = f"Competency Question: Provide the identity property for '{term}' (which means '{description}') as either +O, +I, or -I without any explanations. The answer should be either +O, +I, or -I."
                    cq_unity = f"Competency Question: Provide the unity property for '{term}' (which means '{description}') as either +U, ~U, or -U without any explanations. The answer should be either +U, ~U, or -U."
                    

                    # Get initial responses
                    initial_rigidity_response = finding_taxonomy_placement(helper_rigidity, story, cq_rigidity, footer)
                    initial_identity_response = finding_taxonomy_placement(helper_identity, story, cq_identity, footer)
                    initial_unity_response = finding_taxonomy_placement(helper_unity, story, cq_unity, footer)
                    

                    # Refine responses based on initial responses
                    rigidity_response = refine_meta_property('rigidity', initial_rigidity_response)
                    identity_response = refine_meta_property('identity', initial_identity_response)
                    unity_response = refine_meta_property('unity', initial_unity_response)

                    # Store the results in the dictionary to avoid redundant processing
                    processed_terms[term] = {
                        'rigidity': rigidity_response,
                        'identity': identity_response,
                        'unity': unity_response,
                        'upper_tier': upper_tier_response
                    }

                # Update the DataFrame with the results
                df.at[index, 'Rigidity'] = rigidity_response
                df.at[index, 'Identity'] = identity_response
                df.at[index, 'Unity'] = unity_response
                

    # Save the updated DataFrame back to the CSV file
    
    df.to_csv(file_path, index=False)
    print("Results have been updated in the CSV file successfully.")

if __name__ == "__main__":
    main()
