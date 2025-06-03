from inventory_manager import InventoryItem, Spirit, Mixer, Garnish, enhance_inventory_item_with_api_data
from cocktail_manager import get_all_recipes, find_makeable_cocktails, CocktailRecipe # Import cocktail related things
from data_handler import save_inventory, load_inventory, DEFAULT_INVENTORY_FILE
from api_client import search_ingredient_by_name # Import API handler for ingredient data


def run_bar_program():
    # --- 1. Build Your Inventory (Example - later this will be loaded or input by user) ---
    current_inventory = [
        Spirit(name="Hendrick's Gin", brand="Hendrick's", category="Gin", quantity="700ml", price=35.0,
               type_of_liquor="Scottish Gin", abv=41.4, origin="Scotland"),
        Spirit(name="Absolut Vodka", brand="Absolut", category="Vodka", quantity="1L", price=22.0,
               type_of_liquor="Swedish Vodka", abv=40.0, origin="Sweden"),
        Mixer(name="Schweppes Tonic", brand="Schweppes", category="Tonic Water", quantity="6x200ml", price=5.0,
              mixer_type="Tonic Water"),
        Mixer(name="Generic Orange Juice", brand="Juicy Co.", category="Orange Juice", quantity="1L", price=2.0,
              mixer_type="Juice"),
        Mixer(name="Noilly Prat", brand="Noilly Prat", category="Dry Vermouth", quantity="750ml", price=15.0,
              mixer_type="Vermouth"),
        # Add Campari for the Negroni example:
        # Option A: Campari as its own category
        # InventoryItem(name="Campari", brand="Campari", category="Campari", quantity="700ml", price=20.0),
        # Option B: Campari as a Liqueur with brand Campari
        Spirit(name="Campari", brand="Campari", category="Liqueur", quantity="700ml", price=20.0,
               type_of_liquor="Bitter Aperitif", abv=25.0, origin="Italy", user_notes="Essential for Negroni"),
        # Add Sweet Vermouth for Negroni
        Mixer(name="Martini Rosso", brand="Martini", category="Sweet Vermouth", quantity="750ml", price=10.0,
              mixer_type="Vermouth"),
        Garnish(name="Lemon", brand="Fresh", category="Lemon", quantity="5 units", price=1.0,
                garnish_type="Citrus Fruit") # If recipes require "Lemon" as category
    ]

    print("--- Current Bar Inventory ---")
    if not current_inventory:
        print("Your bar is empty!")
    else:
        for item in current_inventory:
            print(item.display_details()) # Your display_details should print or return a string to be printed

    # --- 2. Get All Cocktail Recipes ---
    all_recipes = get_all_recipes()
    if not all_recipes:
        print("\nNo cocktail recipes loaded.")
        return

    # --- 3. Find Makeable Cocktails ---
    makeable = find_makeable_cocktails(current_inventory, all_recipes)

    print("\n--- Cocktails You Can Make ---")
    if not makeable:
        print("You can't make any cocktails with the current inventory and recipes.")
    else:
        for cocktail in makeable:
            # cocktail.display_recipe() # This method prints directly
            print(f"- {cocktail.name}") # Or just print the name

    # --- Optional: Display full recipes for makeable cocktails ---
    # print("\n--- Full Recipes for Makeable Cocktails ---")
    # for cocktail in makeable:
    #     cocktail.display_recipe()
    
    # In src/main.py (simplified example)



    current_inventory = load_inventory(DEFAULT_INVENTORY_FILE)

    # If inventory is empty (e.g., first run or file didn't exist),
    # you might want to add some default items and save.
    if not current_inventory:
        print("No existing inventory found. Creating a sample inventory.")
        # Create your sample inventory as before
        current_inventory = [
            Spirit(name="Hendrick's Gin", brand="Hendrick's", category="Gin", quantity="700ml", price=35.0,
                   type_of_liquor="Scottish Gin", abv=41.4, origin="Scotland"),
            Mixer(name="Schweppes Tonic", brand="Schweppes", category="Tonic Water", quantity="6x200ml", price=5.0,
                  mixer_type="Tonic Water"),
            # ... add more sample items
        ]
        # Save this new sample inventory
        save_inventory(current_inventory, DEFAULT_INVENTORY_FILE)


    print("\n--- Current Bar Inventory (Loaded) ---")
    if not current_inventory:
        print("Your bar is empty!")
    else:
        for item in current_inventory:
            print(item.display_details())

    # ... (rest of your program: get recipes, find makeable, etc.) ...

    # Example of when you might save again (e.g., after adding/modifying items - not implemented yet)
    # For now, we're just loading and potentially creating an initial file.
    # If you had a function to add items to current_inventory, you'd call save_inventory() after.
    # save_inventory(current_inventory, DEFAULT_INVENTORY_FILE)
    
    for item in current_inventory: enhance_inventory_item_with_api_data(item)




if __name__ == "__main__":
    run_bar_program()