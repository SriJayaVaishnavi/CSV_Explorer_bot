# Column extractor using LLM
import ollama
import re

def normalize_column_name(name):
    """Normalize column name for comparison by removing special characters and spaces"""
    # Special handling for PM2.5 -> pm2_5
    name = name.lower()
    name = name.replace("pm2.5", "pm2_5")
    name = name.replace("pm10", "pm10")  # Preserve pm10
    return re.sub(r'[^a-zA-Z0-9_]', '', name)

def extract_columns(query, df_columns):
    print(f"Debug: Available columns: {df_columns}")
    print(f"Debug: Processing query: {query}")
    
    # Create normalized versions of column names for matching
    normalized_columns = {normalize_column_name(col): col for col in df_columns}
    
    # For scatter plots and relationships, try to identify both columns from the query first
    query_lower = query.lower()
    if any(word in query_lower for word in ["relate", "relationship", "correlation", "versus", "vs", "against", "compare"]):
        prompt = f"""
You are a data assistant. Given a user query and these dataframe columns: {df_columns},
identify the TWO columns being compared or related.

IMPORTANT: Respond with EXACTLY:
x=<column_name>,y=<column_name>

Choose the exact column names from: {', '.join(df_columns)}

Query: "{query}"
"""
        response = ollama.chat(model="gemma:2b", messages=[{"role": "user", "content": prompt}])
        try:
            text = response["message"]["content"].lower().strip()
            print(f"Debug: LLM response for relationship: '{text}'")
            
            if "x=" in text and "y=" in text:
                x = text.split("x=")[1].split(",")[0].strip()
                y = text.split("y=")[1].strip()
                print(f"Debug: Extracted relationship columns - x: '{x}', y: '{y}'")
                
                x_norm = normalize_column_name(x)
                y_norm = normalize_column_name(y)
                
                if x_norm in normalized_columns and y_norm in normalized_columns:
                    actual_x = normalized_columns[x_norm]
                    actual_y = normalized_columns[y_norm]
                    print(f"Debug: Matched relationship columns - x: '{actual_x}', y: '{actual_y}'")
                    return actual_x, actual_y
        except Exception as e:
            print(f"Debug: Error in relationship extraction: {str(e)}")
    
    # For single column cases (pie, bar, histogram) or if relationship extraction failed
    prompt = f"""
You are a data assistant. Given a user query and these dataframe columns: {df_columns},
identify the column mentioned or implied in the query.

IMPORTANT: For single column plots (pie, bar, histogram), respond with ONLY:
column=<column_name>

Choose the exact column names from: {', '.join(df_columns)}

Query: "{query}"
"""
    response = ollama.chat(model="gemma:2b", messages=[{"role": "user", "content": prompt}])
    try:
        text = response["message"]["content"].lower().strip()
        print(f"Debug: LLM response for single column: '{text}'")
        
        if "column=" in text:
            column = text.split("column=")[1].strip()
        elif "=" in text:
            column = text.split("=")[1].strip()
        else:
            column = text.strip()
            
        print(f"Debug: Extracted column: '{column}'")
        column_norm = normalize_column_name(column)
        
        if column_norm in normalized_columns:
            actual_column = normalized_columns[column_norm]
            print(f"Debug: Matched single column: '{actual_column}'")
            return actual_column, None
        else:
            print(f"Debug: Column '{column}' not found in available columns")
            return None, None
            
    except Exception as e:
        print(f"Debug: Error extracting columns: {str(e)}")
        print(f"Debug: Failed to extract columns from response: {text}")
        return None, None
