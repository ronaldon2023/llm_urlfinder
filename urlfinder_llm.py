"""
urlfinder.py

A resilient, multi-engine data intelligence tool designed to generate, validate, 
and assess confidence in search queries derived from structured data using a 
local Large Language Model (LLM).

Author: Ronald N. (Placeholder for your name/initials)
Date: 2025-10-31
"""

import os
import csv
import json
import webbrowser
from typing import List, Dict, Any
from urllib.parse import quote_plus

import jinja2
import ollama
from json_repair import repair_json 

# --- Configuration ---
MODEL_NAME = 'llama3'

class UrlFinder:
    """Handles data loading, template merging, and communication with the LLM."""
    def __init__(self, template_dir='templates', model_name=MODEL_NAME):
        self.template_dir = template_dir
        self.model_name = model_name
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.template_dir),
        )
        
    def get_template(self, template_name: str) -> jinja2.Template:
        """Loads the Jinja2 template by name."""
        try:
            return self.env.get_template(template_name)
        except jinja2.TemplateNotFound:
            raise FileNotFoundError(f"Template '{template_name}' not found in directory '{self.template_dir}'")
    
    def load_data_from_csv(self, file_path: str) -> List[Dict[str, Any]]:
        """Reads a CSV file (with headers) and returns a list of dictionaries."""
        data = []
        try:
            with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    data.append(row)
        except FileNotFoundError:
            raise FileNotFoundError(f"CSV file '{file_path}' not found.")
        return data
    
    def merge_template_and_data(self, template_name: str, data_file: str) -> List[str]:
        """Loads data, loads the template, and renders the template once for each data row."""
        data_rows = self.load_data_from_csv(data_file)
        template = self.get_template(template_name)
        
        rendered_outputs = []
        for row_data in data_rows:
            output = template.render(**row_data)
            rendered_outputs.append(output)
            
        return rendered_outputs
        
    def get_llm_response(self, user_prompt: str) -> str:
        """Calls the Ollama API to generate a structured search query."""
        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[
                    {'role': 'user', 'content': user_prompt.strip()},
                ],
                format='json'  
            )
            return response['message']['content']
        except Exception as e:
            return f"OLLAMA_ERROR: {e}"

# --------------------------------------------------------------------
# --- Search and Validation Functions ---
# --------------------------------------------------------------------

def create_search_url(query: str, engine: str) -> str:
    """Safely URL-encodes the query and builds a direct search link."""
    safe_query = quote_plus(query)
    
    if engine == 'google':
        return f"https://www.google.com/search?q={safe_query}"
    elif engine == 'bing':
        return f"https://www.bing.com/search?q={safe_query}"
    elif engine == 'duckduckgo':
        return f"https://duckduckgo.com/?q={safe_query}"
    else:
        return ""

def simulate_search_result(query: str, engine: str) -> bool:
    """
    *** TEMPORARY MOCK FUNCTION ***
    
    This function simulates fetching search results to demonstrate the 
    cross-validation logic and confidence scoring. The hardcoded logic 
    is used to generate predictable MATCH/FAIL results.

    When a search API key is available, this entire function must be replaced
    by an actual API call (e.g., Google Custom Search API) that retrieves
    the top search results and checks if the 'G2 Reviews' link exists.
    """
    query = query.lower()
    
    # Simulation Logic (Designed to produce varied results for demonstration)
    if engine == 'google':
        return 'diebold' in query or 'paccar' in query

    elif engine == 'bing':
        return 'paccar' in query and 'g2' in query
    
    elif engine == 'duckduckgo':
        return query == "diebold g2 reviews" 
        
    return False

def assess_confidence(query: str) -> tuple[str, str]:
    """
    Performs cross-validation against three search engines (simulated) 
    and assigns a confidence score based on source agreement.
    """
    engines = ['google', 'bing', 'duckduckgo']
    matches = []
    
    for engine in engines:
        is_found = simulate_search_result(query, engine)
        matches.append((engine, is_found))
    
    match_count = sum(1 for _, found in matches if found)
    
    # Confidence Scoring Logic
    if match_count == 3:
        confidence = "HIGH 🟢"
    elif match_count == 2:
        confidence = "MEDIUM 🟡"
    else:
        confidence = "LOW 🔴"

    summary = f"({match_count}/3 matches) — " + " | ".join([f"{e}: {'MATCH' if f else 'FAIL'}" for e, f in matches])
    
    return confidence, summary

# --------------------------------------------------------------------
# --- Main Execution ---
# --------------------------------------------------------------------

def main():
    finder = UrlFinder()
    
    template_name = 'instructions.txt'
    data_file = 'businesses.txt'
    
    print(f"Loading data from '{data_file}' and template '{template_name}'...")
    
    try:
        rendered_prompts = finder.merge_template_and_data(template_name, data_file)
        
        for i, prompt in enumerate(rendered_prompts):
            print(f"\n--- Processing Business {i + 1} ---")
            
            llm_response_str = finder.get_llm_response(prompt)
            
            if llm_response_str.startswith("OLLAMA_ERROR:"):
                print(llm_response_str)
                continue
                
            parsed_data = None

            try:
                # Attempt standard JSON parse
                parsed_data = json.loads(llm_response_str.strip())
                
            except json.JSONDecodeError:
                # Fallback to repair if standard parse fails
                try:
                    repaired_string = repair_json(llm_response_str.strip())
                    parsed_data = json.loads(repaired_string)
                except Exception:
                    print(f"CRITICAL ERROR: Failed to parse or repair JSON. Raw output:\n{llm_response_str.strip()}")
                    parsed_data = None 
            
            
            if parsed_data:
                search_query = None
                
                # Extract the query key/value pair
                if isinstance(parsed_data, dict):
                    for key, value in parsed_data.items():
                        if isinstance(key, str) and ("Reviews" in key or "Query" in key):
                            search_query = key 
                            break
                        if isinstance(value, str) and ("Reviews" in value or "Query" in value):
                            search_query = value
                            break
                
                if search_query:
                    print(f"Extracted Query: {search_query}")
                    
                    # Confidence Assessment
                    confidence, summary = assess_confidence(search_query)
                    print(f"\n[ Confidence: {confidence} ]")
                    print(f"Validation Summary: {summary}")
                    
                    # Display the links for manual validation
                    print("\nVerification Links (Copy & Paste to Check):")
                    print(f"  Google: {create_search_url(search_query, 'google')}")
                    print(f"  Bing: {create_search_url(search_query, 'bing')}")
                    print(f"  DuckDuckGo: {create_search_url(search_query, 'duckduckgo')}")
                    
                else:
                    print(f"Could not reliably extract the query. Data received: {parsed_data}")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        
if __name__ == '__main__':
    main()