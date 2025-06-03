import os
# Import from cocktail_manager:
# - get_all_recipes: to get the list of CocktailRecipe objects.
# - save_cocktail_recipes_to_json: to save them using the centralized logic.
# - CURATED_COCKTAILS_FILE: to use the consistent file path.
from cocktail_manager import get_all_recipes, save_cocktail_recipes_to_json, CURATED_COCKTAILS_FILE

def main():
    print(f"Attempting to populate/refresh {CURATED_COCKTAILS_FILE}...")
    # This will either load from CURATED_COCKTAILS_FILE if it exists and is valid,
    # or fetch from API and save to CURATED_COCKTAILS_FILE if it doesn't exist/is empty.
    recipes = get_all_recipes() #

    if recipes:
        # Even if get_all_recipes saved it, calling this explicitly ensures
        # that running populate_cocktails.py uses the save_cocktail_recipes_to_json
        # logic, which is good if the saving logic or CocktailRecipe structure evolves.
        # It will overwrite the file with the (potentially just loaded) data.
        print(f"Re-saving {len(recipes)} recipes to {CURATED_COCKTAILS_FILE} to ensure format consistency...")
        project_root = os.path.dirname(os.path.dirname(__file__)) # Get to 'src' parent
        out_file_path = os.path.join(project_root, CURATED_COCKTAILS_FILE) # CURATED_COCKTAILS_FILE is like "data/cocktails.json"
        
        # Ensure the output directory from CURATED_COCKTAILS_FILE exists
        out_dir = os.path.dirname(out_file_path)
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir)
            print(f"Created directory: {out_dir}")
            
        save_cocktail_recipes_to_json(recipes, out_file_path)
        print(f"Finished populating. {len(recipes)} recipes are in {out_file_path}")
    else:
        print(f"No recipes were found or fetched. {CURATED_COCKTAILS_FILE} might be empty or there was an issue.")

if __name__ == "__main__":
    main()