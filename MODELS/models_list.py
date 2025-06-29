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

    # Instead of scraping, use the provided HTML table for Free Tier
    from io import StringIO
    import pandas as pd
    free_tier_html = '''
<table>
  <thead>
    <tr>
      <th>Model</th>
      <th>RPM</th>
      <th>TPM</th>
      <th>RPD</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>Gemini 2.5 Pro</td><td>5</td><td>250,0000</td><td>100</td></tr>
    <tr><td>Gemini 2.5 Flash</td><td>10</td><td>250,000</td><td>250</td></tr>
    <tr><td>Gemini 2.5 Flash-Lite Preview 06-17</td><td>15</td><td>250,000</td><td>1,000</td></tr>
    <tr><td>Gemini 2.5 Flash Preview TTS</td><td>3</td><td>10,000</td><td>15</td></tr>
    <tr><td>Gemini 2.5 Pro Preview TTS</td><td>--</td><td>--</td><td>--</td></tr>
    <tr><td>Gemini 2.0 Flash</td><td>15</td><td>1,000,000</td><td>200</td></tr>
    <tr><td>Gemini 2.0 Flash Preview Image Generation</td><td>10</td><td>200,000</td><td>100</td></tr>
    <tr><td>Gemini 2.0 Flash-Lite</td><td>30</td><td>1,000,000</td><td>200</td></tr>
    <tr><td>Imagen 3</td><td>--</td><td>--</td><td>--</td></tr>
    <tr><td>Veo 2</td><td>--</td><td>--</td><td>--</td></tr>
    <tr><td>Gemini 1.5 Flash (Deprecated)</td><td>15</td><td>250,000</td><td>50</td></tr>
    <tr><td>Gemini 1.5 Flash-8B (Deprecated)</td><td>15</td><td>250,000</td><td>50</td></tr>
    <tr><td>Gemini 1.5 Pro (Deprecated)</td><td>--</td><td>--</td><td>--</td></tr>
    <tr><td>Gemma 3 & 3n</td><td>30</td><td>15,000</td><td>14,400</td></tr>
    <tr><td>Gemini Embedding Experimental 03-07</td><td>5</td><td>--</td><td>100</td></tr>
  </tbody>
</table>
'''
    free_tier_df = pd.read_html(StringIO(free_tier_html))[0]
    # Rename columns to match expected output
    free_tier_df.columns = ['model_name_scraped', 'rpm_free_tier', 'tpm_free_tier', 'rpd_free_tier']
    return free_tier_df

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

            # Filter out rows where any of the free tier columns are NA
            mask = (
                (df_to_save['rpm_free_tier'].str.upper() != 'N/A') &
                (df_to_save['tpm_free_tier'].str.upper() != 'N/A') &
                (df_to_save['rpd_free_tier'].str.upper() != 'N/A')
            )
            df_to_save = df_to_save[mask]

            print("\n--- Combined Model Information (API & Scraped Free Tier Rates, Filtered) ---")
            print(df_to_save.to_string())

            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            df_to_save.to_csv(OUTPUT_FILE, index=False)
            print(f"\nData successfully saved to: {OUTPUT_FILE.resolve()}")

            # --- Auto-update __init__.py with best-fit models ---
            init_path = OUTPUT_DIR / "__init__.py"
            def safe_int(val):
                try:
                    return int(str(val).replace(",", "").replace("-", "0"))
                except Exception:
                    return 0

            # Reasoning: pro model with most rpm (pythonic name)
            pro_mask = df_to_save['model_name'].str.lower().str.contains('pro')
            pro_models = df_to_save[pro_mask].copy()
            pro_models['rpm_int'] = pro_models['rpm_free_tier'].apply(safe_int)
            reasoning_row = pro_models.sort_values('rpm_int', ascending=False).head(1)
            reasoning_model = reasoning_row['pythonic_name'].values[0] if not reasoning_row.empty else ''

            # Flash: model with highest rpm * rpd (pythonic name)
            df_to_save['rpm_int'] = df_to_save['rpm_free_tier'].apply(safe_int)
            df_to_save['rpd_int'] = df_to_save['rpd_free_tier'].apply(safe_int)
            df_to_save['rpm_rpd'] = df_to_save['rpm_int'] * df_to_save['rpd_int']
            flash_row = df_to_save.sort_values('rpm_rpd', ascending=False).head(1)
            flash_model = flash_row['pythonic_name'].values[0] if not flash_row.empty else ''

            # Text-to-speech: model with highest rpm/rpd and tts capability (pythonic name)
            tts_mask = df_to_save['model_name'].str.lower().str.contains('tts')
            tts_models = df_to_save[tts_mask].copy()
            tts_models['rpm_rpd'] = tts_models['rpm_int'] * tts_models['rpd_int']
            tts_row = tts_models.sort_values('rpm_rpd', ascending=False).head(1)
            tts_model = tts_row['pythonic_name'].values[0] if not tts_row.empty else ''

            # Audio dialog: model with 'audio dialog' in name, highest rpm/rpd (pythonic name)
            audio_mask = df_to_save['model_name'].str.lower().str.contains('audio dialog')
            audio_models = df_to_save[audio_mask].copy()
            audio_models['rpm_rpd'] = audio_models['rpm_int'] * audio_models['rpd_int']
            audio_row = audio_models.sort_values('rpm_rpd', ascending=False).head(1)
            audio_model = audio_row['pythonic_name'].values[0] if not audio_row.empty else ''

            # Write to __init__.py
            with open(init_path, 'w', encoding='utf-8') as f:
                f.write("# MODELS/__init__.py\n")
                f.write(f'REASONING_MODEL = "{reasoning_model}"\n')
                f.write(f'FLASH_MODEL = "{flash_model}"\n')
                f.write(f'TEXT_TO_SPEECH_MODEL = "{tts_model}"\n')
                f.write(f'AUDIO_DIALOG_MODEL = "{audio_model}"\n')
                f.write("# ...add any other model constants here...\n")
        else:
            print("No final data to display or save.")

    except ValueError as ve:
        print(f"Configuration Error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()