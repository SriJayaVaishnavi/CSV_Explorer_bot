import requests
import os

TOOLS = ["summary", "scatter", "line", "bar", "histogram", "correlation", "pie"]

KEYWORD_MAP = {
    "line": ["trend", "change", "pattern", "evolution", "timeline", "over time", "progression", "time series"],
    "bar": ["comparison", "compare", "highest", "lowest", "top", "summary", "categorical"],
    "scatter": ["relationship", "correlation", "association", "relate", "versus", "vs", "against"],
    "histogram": ["distribution", "spread", "frequency", "range"],
    "pie": ["composition", "parts", "proportions", "share", "percentage", "breakdown"],
    "correlation": ["correlation matrix", "correlations between", "relationships between all"],
    "summary": ["summarize", "describe", "overview", "statistics", "stats", "information", "tell me about", "what's in"]
}

# Priority order for plot selection
PLOT_PRIORITY = ["summary", "line", "bar", "scatter", "histogram", "pie", "correlation"]

# Use an environment variable to store the API key
API_KEY = os.getenv("GEMMA_API_KEY")

# Ensure to instruct the user to set the environment variable in their system or deployment environment

OPENAI_URL = "https://litellm.dev.ai-cloud.me/v1/chat/completions"

def route_query_to_tool(query: str) -> str:
    """Route a query to the appropriate tool based on keywords and context."""
    if not query:
        return "summary"  # Default to summary if no query
        
    query_lower = query.lower()
    print(f"Debug: Processing query: '{query_lower}'")
    
    # First check for explicit tool mentions
    for tool in TOOLS:
        if tool.lower() in query_lower:
            print(f"Debug: Found explicit tool mention: {tool}")
            return tool
    
    # Then check keyword matches in priority order
    for tool in PLOT_PRIORITY:
        keywords = KEYWORD_MAP[tool]
        if any(keyword in query_lower for keyword in keywords):
            print(f"Debug: Found match for tool: {tool}")
            return tool
    
    # If no matches found, use LLM for more nuanced understanding
    keyword_hint = "\n".join([f"- {tool}: {', '.join(words)}" for tool, words in KEYWORD_MAP.items()])
    
    prompt = f"""
You are a tool router for a CSV analyst bot. Select exactly one tool from this list:
{TOOLS}

Here's when to use each tool:
{keyword_hint}

Consider these priorities:
1. Summary for general dataset information and statistics
2. Line plots for trends and changes over time
3. Bar plots for comparisons and categorical data
4. Scatter plots for relationships between variables
5. Histograms for distributions
6. Pie charts for proportions
7. Correlation matrix for multiple variable relationships

User Query: "{query}"

Respond with ONLY the tool name, nothing else.
Tool:
"""
    try:
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gemma-3-27b",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }
        response = requests.post(OPENAI_URL, json=payload, headers=headers)
        response_data = response.json()
        content = response_data["choices"][0]["message"]["content"].strip().lower()
        print(f"Debug: LLM response: '{content}'")
        
        if content in TOOLS:
            return content
        else:
            print(f"Debug: Invalid tool name received: '{content}'")
            return "summary"  # Default to summary for unclear queries
    except:
        print("Debug: LLM call failed, defaulting to summary")
        return "summary"  # Default to summary if LLM fails
