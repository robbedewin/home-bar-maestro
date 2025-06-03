# src/api_client.py
import requests
import json
import os
import time # For simple rate limiting, if needed

API_BASE_URL = "https://www.thecocktaildb.com/api/json/v1/1/"
CACHE_DIR = "data/api_cache/" # Store API responses here

# Ensure cache directory exists
os.makedirs(CACHE_DIR + "cocktails/", exist_ok=True)
os.makedirs(CACHE_DIR + "ingredients/", exist_ok=True)

def _fetch_from_api(endpoint: str, params: dict) -> dict | None:
    """Helper function to fetch data from the API."""
    try:
        response = requests.get(API_BASE_URL + endpoint, params=params, timeout=10) # 10 second timeout
        response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API request error: {e}")
        return None

def search_cocktail_by_name(cocktail_name: str) -> dict | None:
    """
    Searches for a cocktail by its name.
    Caches the result to avoid repeated API calls.
    """
    cache_file = os.path.join(CACHE_DIR, "cocktails", f"{cocktail_name.lower().replace(' ', '_')}.json")

    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r') as f:
                print(f"Loading '{cocktail_name}' from cache.")
                return json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            print(f"Cache read error for '{cocktail_name}': {e}. Fetching from API.")

    print(f"Fetching '{cocktail_name}' from API...")
    data = _fetch_from_api("search.php", {"s": cocktail_name})

    if data and data.get("drinks"): # The API returns {"drinks": null} if not found
        # Save to cache
        try:
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=4)
        except IOError as e:
            print(f"Cache write error for '{cocktail_name}': {e}")
        return data
    elif data and data.get("drinks") is None:
        print(f"Cocktail '{cocktail_name}' not found by API.")
        # Cache the "not found" result to avoid re-fetching
        try:
            with open(cache_file, 'w') as f:
                json.dump({"drinks": None}, f, indent=4) # Store the null result
        except IOError as e:
            print(f"Cache write error for '{cocktail_name}' (not found): {e}")
        return {"drinks": None} # Explicitly return the "not found" structure
    return None


def search_ingredient_by_name(ingredient_name: str) -> dict | None:
    """
    Searches for an ingredient by its name.
    Caches the result.
    """
    cache_file = os.path.join(CACHE_DIR, "ingredients", f"{ingredient_name.lower().replace(' ', '_')}.json")

    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r') as f:
                print(f"Loading ingredient '{ingredient_name}' from cache.")
                return json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            print(f"Cache read error for ingredient '{ingredient_name}': {e}. Fetching from API.")
            
    print(f"Fetching ingredient '{ingredient_name}' from API...")
    data = _fetch_from_api("search.php", {"i": ingredient_name})

    if data and data.get("ingredients"):
        try:
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=4)
        except IOError as e:
            print(f"Cache write error for ingredient '{ingredient_name}': {e}")
        return data
    elif data and data.get("ingredients") is None:
        print(f"Ingredient '{ingredient_name}' not found by API.")
        try:
            with open(cache_file, 'w') as f:
                json.dump({"ingredients": None}, f, indent=4)
        except IOError as e:
            print(f"Cache write error for ingredient '{ingredient_name}' (not found): {e}")
        return {"ingredients": None}
    return None

# Example usage (you can test this by running this file directly: python src/api_client.py)
if __name__ == "__main__":
    # Test cocktail search
    margarita_data = search_cocktail_by_name("Margarita")
    if margarita_data and margarita_data.get("drinks"):
        print(f"\nMargarita Data (first result): {margarita_data['drinks'][0]['strDrink']}, ID: {margarita_data['drinks'][0]['idDrink']}")
        print(f"Image: {margarita_data['drinks'][0]['strDrinkThumb']}")
    
    non_existent_cocktail = search_cocktail_by_name("Super Fake Cocktail 123")
    if non_existent_cocktail and non_existent_cocktail.get("drinks") is None:
        print("\nCorrectly handled non-existent cocktail.")

    # Test ingredient search
    vodka_data = search_ingredient_by_name("Vodka")
    if vodka_data and vodka_data.get("ingredients"):
        print(f"\nVodka Data (first result): {vodka_data['ingredients'][0]['strIngredient']}")
        print(f"Description: {vodka_data['ingredients'][0]['strDescription'][:100]}...") # First 100 chars

    gin_data = search_ingredient_by_name("Gin") # Second call, should use cache if run again soon