import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from dotenv import load_dotenv
import pathlib
import re # For parsing limit values

# --- Constants for Pythonic Names ---
# Keys MUST be the exact 'model_id' from the API (e.g., "models/gemini-1.5-pro-latest")
PYTHONIC_NAME_MAP = {
    "models/gemini-1.5-pro-latest": "GEMINI_1_5_PRO_LATEST_MODEL", # Example, verify exact ID
    "models/gemini-1.0-pro": "GEMINI_1_0_PRO_MODEL",             # Example, verify exact ID
    "models/gemini-1.5-flash-latest": "GEMINI_1_5_FLASH_LATEST_MODEL", # Example
    # Add your specific model_id to pythonic_name mappings here.
    # For "Gemini 2.5 Pro Experimental 03-25", if its API model_id is
    # "models/gemini-2.5-pro-exp-03-25", the map entry would be:
    "models/gemini-2.5-pro-exp-03-25": "REASONING_MODEL_EXP_03_25", # Example for specific experimental
    # Ensure the keys match what m.name returns from genai.list_models()
}

def generate_pythonic_name(api_model_id):
    """
    Generates a pythonic name for a given API model ID.
    Removes the leading 'models/' if present, and returns the rest as the pythonic name.
    """
    if api_model_id.startswith("models/"):
        return api_model_id[len("models/"):]
    return api_model_id

def parse_limit_value(text, limit_type_expected):
    """
    Extracts a numeric value for a specific limit type (RPM, TPM, RPD) from a text string.
    Returns only the number (as a string with commas, e.g., "250,000") or "N/A".
    """
    if not text or text.strip() == '--' or text.strip() == '—': # Handle en-dash or em-dash
        return "N/A"

    text = text.strip()
    value_to_return = "N/A"

    # Patterns to find numbers associated with specific units
    # We want the number part, (\d[\d,]*)
    patterns = {
        "RPM": r"(\d[\d,]*)\s*(?:RPM|requests\s*per\s*minute)",
        "TPM": r"(\d[\d,]*)\s*(?:TPM|tokens\s*per\s*minute)",
        "RPD": r"(\d[\d,]*)\s*(?:RPD|requests\s*per\s*day)"
    }
    # Generic number pattern if no unit is specified in the cell
    generic_num_pattern = r"^(\d[\d,]*)$" # Matches if the cell ONLY contains a number

    if limit_type_expected in patterns:
        match = re.search(patterns[limit_type_expected], text, re.IGNORECASE)
        if match:
            value_to_return = match.group(1) # Get the number
        elif re.fullmatch(generic_num_pattern, text): # If cell is just "60" and we expect RPM
             value_to_return = text

    # If still "N/A" but the cell might contain other numbers not matching the specific unit,
    # we stick with "N/A" because we want the value for limit_type_expected.
    # Example: if cell is "100 TPD" and limit_type_expected is "TPM", result is "N/A".
    
    # If value_to_return is still N/A, but the text has some digits, it means parsing failed.
    # For strict "only numbers" output, this is fine.
    return value_to_return


# --- Function to get model details from Google Generative AI API ---
def fetch_models_from_api():
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is not set.")
    genai.configure(api_key=api_key)

    models_data_api = []
    print("Fetching available models from the API...")
    try:
        for m in genai.list_models():
            # Consider all models initially, filter later if needed by supported_generation_methods
            models_data_api.append({
                "model_name_api": m.display_name,
                "model_id": m.name, # This is the key for PYTHONIC_NAME_MAP
                "version": m.version,
                "description": m.description,
                "input_token_limit": m.input_token_limit if hasattr(m, 'input_token_limit') else 'N/A',
                "output_token_limit": m.output_token_limit if hasattr(m, 'output_token_limit') else 'N/A',
                "supported_generation_methods": ", ".join(m.supported_generation_methods),
            })
    except Exception as e:
        print(f"Error fetching models from API: {e}")
        return pd.DataFrame()
        
    if not models_data_api:
        print("No models found via API.") # Changed message slightly
        return pd.DataFrame()
    
    df_api_models = pd.DataFrame(models_data_api)
    df_api_models['pythonic_name'] = df_api_models['model_id'].apply(generate_pythonic_name)
    return df_api_models

# --- Function to scrape free-tier rate limits ---
def scrape_free_tier_rates():
    rate_limits_url = "https://ai.google.dev/gemini-api/docs/rate-limits"
    scraped_limits_data = []

    try:
        print(f"Fetching rate limits from {rate_limits_url}...")
        response = requests.get(rate_limits_url, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        print(f"Successfully fetched and parsed {rate_limits_url}.")
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve {rate_limits_url}: {e}")
        return pd.DataFrame()

    print("\nLooking for the 'Free tier' section and its rate limits table...")
    free_tier_anchor = soup.find(id="free-tier")
    
    if not free_tier_anchor:
        print("Could not find the 'Free tier' anchor (id='free-tier').")
        return pd.DataFrame()

    print(f"Found anchor element for 'Free tier': <{free_tier_anchor.name}> {free_tier_anchor.text[:50]}...")
    
    free_tier_table = None
    current_element = free_tier_anchor.find_next_sibling() # Start searching *after* the anchor
    while current_element:
        if current_element.name == 'table':
            # Check if this table looks like a rate limits table (e.g. by checking headers)
            # This is to avoid picking up unrelated tables if the structure is complex.
            temp_headers = [th.text.strip().lower() for th in current_element.find_all('th', recursive=False)] # Only direct children th
            if not temp_headers and current_element.find('thead'): # check thead if no direct th
                temp_headers = [th.text.strip().lower() for th in current_element.find('thead').find_all('th')]

            if any(kw in hdr for hdr in temp_headers for kw in ["rpm", "requests per minute", "model"]):
                free_tier_table = current_element
                print("Found a rate limits table associated with the 'Free tier' section.")
                break
        current_element = current_element.find_next_sibling()
    
    if not free_tier_table: # Fallback if the direct sibling search didn't work as expected
        free_tier_table = free_tier_anchor.find_next('table')
        if free_tier_table:
            print("Found rate limits table (using general find_next) for 'Free tier'.")
        else:
            print("Could not find the table for 'Free tier' rate limits.")
            return pd.DataFrame()

    headers = [th.text.strip().lower().replace('\n', ' ').strip() for th in free_tier_table.find_all('th')]
    if not headers and free_tier_table.find('thead'): # Check thead again
         headers = [th.text.strip().lower().replace('\n', ' ').strip() for th in free_tier_table.find('thead').find_all('th')]

    if not headers: # Try inferring from first data row if no <th> or <thead>
        first_data_row = free_tier_table.find('tbody').find('tr') if free_tier_table.find('tbody') else free_tier_table.find('tr')
        if first_data_row:
            headers = [td.text.strip().lower().replace('\n', ' ').strip() for td in first_data_row.find_all('td')]
            # If we infer headers from <td>, we assume this row IS NOT data for the loop later.
    print(f"Table Headers: {headers}")

    if not headers or "model" not in headers : # Need 'model' header to identify model names
        print("Could not determine valid table headers (missing 'model' or all headers).")
        return pd.DataFrame()

    data_rows_source = free_tier_table.find('tbody') if free_tier_table.find('tbody') else free_tier_table
    data_rows = data_rows_source.find_all('tr')
    
    # If headers were properly found via <th> or <thead>, skip the header row from data_rows
    start_row_index = 0
    if free_tier_table.find('thead') or (free_tier_table.find_all('th') and data_rows and data_rows[0].find('th')):
        start_row_index = 1 

    for row in data_rows[start_row_index:]:
        cols = row.find_all('td') # Free tier table typically uses <td> for data cells
        if not cols or len(cols) < 1: continue # Need at least one column for model name

        row_data = {}
        model_name_scraped = "N/A"
        
        # Determine model name column index from headers
        try:
            model_col_idx = headers.index("model")
            if model_col_idx < len(cols):
                model_name_scraped = cols[model_col_idx].text.strip()
        except ValueError: # 'model' header not found or issue with indexing
            print("Warning: 'model' header not found, attempting first column for model name.")
            if len(cols) > 0:
                model_name_scraped = cols[0].text.strip()
        
        if model_name_scraped.lower() == "model" or not model_name_scraped or model_name_scraped == "N/A":
            continue # Skip header-like rows or empty model names

        row_data['model_name_scraped'] = model_name_scraped
        rpm_val, tpm_val, rpd_val = "N/A", "N/A", "N/A"

        for i, header_text in enumerate(headers):
            if i < len(cols):
                cell_text = cols[i].text.strip()
                if "requests per minute" in header_text or header_text == "rpm":
                    rpm_val = parse_limit_value(cell_text, "RPM")
                elif "tokens per minute" in header_text or header_text == "tpm":
                    tpm_val = parse_limit_value(cell_text, "TPM")
                elif "requests per day" in header_text or header_text == "rpd":
                    rpd_val = parse_limit_value(cell_text, "RPD")
        
        row_data['rpm_free_tier'] = rpm_val
        row_data['tpm_free_tier'] = tpm_val
        row_data['rpd_free_tier'] = rpd_val
        
        scraped_limits_data.append(row_data)
            
    if scraped_limits_data:
        print(f"\nSuccessfully extracted {len(scraped_limits_data)} entries from the Free tier table.")
    else:
        print("\nNo data extracted from the Free tier table. Check headers or table structure.")
    
    return pd.DataFrame(scraped_limits_data)

# --- Main execution block ---
if __name__ == "__main__":
    OUTPUT_DIR = pathlib.Path(__file__).parent
    OUTPUT_FILE = OUTPUT_DIR / "model_info.csv"

    try:
        df_api_models = fetch_models_from_api()
        df_scraped_rates = scrape_free_tier_rates()

        df_final_display = pd.DataFrame() 

        if not df_api_models.empty:
            df_api_models.rename(columns={'model_name_api': 'model_name'}, inplace=True)
            if not df_scraped_rates.empty:
                print("\nCombining API model data with scraped free tier rates...")
                # Normalize match keys more aggressively
                df_api_models['match_key'] = df_api_models['model_name'].str.lower().str.strip().str.replace(" api", "", regex=False).str.replace(r'\s*\(.*\)', '', regex=True)
                df_scraped_rates['match_key'] = df_scraped_rates['model_name_scraped'].str.lower().str.strip().str.replace(" api", "", regex=False).str.replace(r'\s*\(.*\)', '', regex=True)
                
                df_combined = pd.merge(df_api_models, 
                                       df_scraped_rates[['match_key', 'rpm_free_tier', 'tpm_free_tier', 'rpd_free_tier']],
                                       on='match_key', 
                                       how='left')
                
                for col in ['rpm_free_tier', 'tpm_free_tier', 'rpd_free_tier']:
                    if col not in df_combined.columns: 
                        df_combined[col] = "N/A"
                    else:
                        df_combined[col] = df_combined[col].fillna("N/A")
                df_final_display = df_combined
            else: 
                print("\nScraper found no data or failed. Using API model data only.")
                df_api_models['rpm_free_tier'] = "N/A"
                df_api_models['tpm_free_tier'] = "N/A"
                df_api_models['rpd_free_tier'] = "N/A"
                df_final_display = df_api_models
        elif not df_scraped_rates.empty: 
            print("\nAPI fetch failed. Using scraped rate data only (limited information).")
            df_scraped_rates.rename(columns={'model_name_scraped': 'model_name'}, inplace=True)
            for col in ['pythonic_name', 'model_id', 'version', 'description', 
                        'input_token_limit', 'output_token_limit', 'supported_generation_methods']:
                df_scraped_rates[col] = "N/A (API data missing)"
            df_final_display = df_scraped_rates
        else:
            print("No data could be fetched from API or scraper.")

        if not df_final_display.empty:
            final_columns = [
                'model_name', 'pythonic_name', 'model_id', 'version', 'description', 
                'input_token_limit', 'output_token_limit', 'supported_generation_methods', 
                'rpm_free_tier', 'tpm_free_tier', 'rpd_free_tier'
            ]
            for col in final_columns: 
                if col not in df_final_display.columns:
                    df_final_display[col] = "N/A" # Ensure column exists
            
            df_to_save = df_final_display[final_columns].copy()
            
            print("\n--- Combined Model Information (API & Scraped Free Tier Rates) ---")
            print(df_to_save.to_string())

            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            df_to_save.to_csv(OUTPUT_FILE, index=False)
            print(f"\nData successfully saved to: {OUTPUT_FILE.resolve()}")
        else:
            print("No final data to display or save.")

    except ValueError as ve:
        print(f"Configuration Error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()