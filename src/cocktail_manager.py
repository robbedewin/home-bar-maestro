import time
from api_client import search_cocktail_by_name
import json
import os

class IngredientRequirement:
    """
    Represents a single ingredient required for a cocktail recipe.
    """
    def __init__(self, category_needed: str, quantity: str, specific_brand_optional: str = None):
        """
        Initializes an IngredientRequirement.

        Args:
            category_needed (str): The category of the ingredient required.
                                   This should match an `InventoryItem.category`
                                   (e.g., "Gin", "Vodka", "Tonic Water", "Lime Juice", "Dry Vermouth").
            quantity (str): The amount of the ingredient needed (e.g., "50ml", "2 dashes", "1 part").
                            For Phase 2, we primarily care about presence, not exact amount.
            specific_brand_optional (str, optional): A specific brand required for this ingredient.
                                                     Defaults to None (any brand of the category will do).
                                                     This could also be a specific item name if the brand is intrinsic
                                                     (e.g., "Campari" for Campari).
        """
        self.category_needed = category_needed
        self.quantity = quantity
        self.specific_brand_optional = specific_brand_optional

    def __str__(self):
        """Returns a string representation for display."""
        brand_req = f" (Brand: {self.specific_brand_optional})" if self.specific_brand_optional else ""
        return f"{self.quantity} of {self.category_needed}{brand_req}"
    
    

class CocktailRecipe:
    """
    Represents a cocktail recipe.
    """
    def __init__(self, name: str, ingredients: list[IngredientRequirement],
                 preparation_instructions: str, garnish_suggestion: str = "",
                 description: str = "", image_url: str = "",
                 local_image_path: str = None):
        """
        Initializes a CocktailRecipe.

        Args:
            name (str): The name of the cocktail (e.g., "Gin & Tonic").
            ingredients (list[IngredientRequirement]): A list of IngredientRequirement objects.
            preparation_instructions (str): How to make the cocktail.
            garnish_suggestion (str, optional): Suggested garnish. Defaults to an empty string.
            description (str, optional): A brief description of the cocktail. Defaults to an empty string.
        """
        self.name = name
        self.ingredients = ingredients  # This will be a list of IngredientRequirement objects
        self.preparation_instructions = preparation_instructions
        self.garnish_suggestion = garnish_suggestion
        self.description = description
        self.image_url = image_url  # Optional, can be used for future phases with images
        self.local_image_path = local_image_path  # Optional, for local image storage in future phases

    def display_recipe(self):
        """Prints the details of the cocktail recipe."""
        print(f"\n--- {self.name} ---")
        if self.description:
            print(f"Description: {self.description}")
        print("Ingredients:")
        for req in self.ingredients:
            print(f"  - {str(req)}") # Uses the __str__ method of IngredientRequirement
        if self.garnish_suggestion:
            print(f"Garnish: {self.garnish_suggestion}")
        if self.local_image_path:
            print(f"Local Image Path: {self.local_image_path}")
        elif self.image_url:
            print(f"Image: {self.image_url}")
        print(f"Instructions: {self.preparation_instructions}")


COCKTAIL_RECIPES = [
    CocktailRecipe(
        name="Gin & Tonic",
        ingredients=[
            IngredientRequirement(category_needed="Gin", quantity="50ml"),
            IngredientRequirement(category_needed="Tonic Water", quantity="120ml")
        ],
        preparation_instructions="Fill a highball glass with ice. Add gin and top with tonic water. Stir gently.",
        garnish_suggestion="Lime wedge or cucumber slice",
        description="A classic refreshing cocktail."
    ),
    CocktailRecipe(
        name="Vodka Martini",
        ingredients=[
            IngredientRequirement(category_needed="Vodka", quantity="60ml"),
            IngredientRequirement(category_needed="Dry Vermouth", quantity="10ml")
        ],
        preparation_instructions="Stir ingredients with ice until well-chilled. Strain into a chilled martini glass.",
        garnish_suggestion="Lemon twist or olive",
        description="A sophisticated classic, shaken or stirred."
    ),
    CocktailRecipe(
        name="Negroni",
        ingredients=[
            IngredientRequirement(category_needed="Gin", quantity="30ml"),
            IngredientRequirement(category_needed="Sweet Vermouth", quantity="30ml"),
            IngredientRequirement(category_needed="Campari", quantity="30ml", specific_brand_optional="Campari") # Assuming Campari is its own category or its brand is "Campari"
        ],
        preparation_instructions="Stir all ingredients with ice in a mixing glass. Strain into a rocks glass filled with fresh ice.",
        garnish_suggestion="Orange peel or slice",
        description="A perfect balance of bitter, sweet, and herbal."
    ),
    CocktailRecipe(
        name="Screwdriver",
        ingredients=[
            IngredientRequirement(category_needed="Vodka", quantity="50ml"),
            IngredientRequirement(category_needed="Orange Juice", quantity="100ml") # Make sure "Orange Juice" is a category in your inventory
        ],
        preparation_instructions="Fill a highball glass with ice. Add vodka and orange juice. Stir.",
        garnish_suggestion="Orange slice (optional)",
        description="A simple and popular highball."
    )
    # Add 5-10 recipes to start
]

# You can add a simple function to get all recipes
def get_all_recipes() -> list[CocktailRecipe]:
    return COCKTAIL_RECIPES


# Still in src/cocktail_manager.py

# Assuming your InventoryItem and subclasses (Spirit, Mixer, Garnish)
# are defined in src.inventory_manager (adjust import if different)
from inventory_manager import InventoryItem # Use a relative import if in the same package

def find_makeable_cocktails(inventory: list[InventoryItem], recipes: list[CocktailRecipe]) -> list[CocktailRecipe]:
    """
    Determines which cocktails can be made from the given inventory.

    Args:
        inventory (list[InventoryItem]): A list of items currently in the bar.
        recipes (list[CocktailRecipe]): A list of all known cocktail recipes.

    Returns:
        list[CocktailRecipe]: A list of cocktail recipes that can be made.
    """
    makeable_cocktails = []
    inventory_categories = {item.category.lower() for item in inventory} # For quick lookup, case-insensitive
    # For brand checking, create a set of (category.lower(), brand.lower()) or (category.lower(), name.lower())
    # This helps if a specific brand is required.
    inventory_category_brands = set()
    for item in inventory:
        inventory_category_brands.add( (item.category.lower(), item.brand.lower()) )
        # If brand is often part of the name for unique items like "Campari", also consider adding item.name
        if item.name.lower() == item.brand.lower() or item.brand.lower() == "n/a": # crude check if name IS the brand
             inventory_category_brands.add( (item.category.lower(), item.name.lower()) )


    for recipe in recipes:
        can_make_cocktail = True
        for req in recipe.ingredients:
            # Normalize category for comparison
            required_category_lower = req.category_needed.lower()
            
            ingredient_found = False
            if req.specific_brand_optional:
                # If a specific brand is needed, check category AND brand/name
                required_brand_lower = req.specific_brand_optional.lower()
                if (required_category_lower, required_brand_lower) in inventory_category_brands:
                    ingredient_found = True
                # Fallback: maybe specific_brand_optional IS the category for very unique items
                elif required_brand_lower in inventory_categories and required_category_lower == required_brand_lower:
                    # e.g. req.category_needed = "Campari", req.specific_brand_optional = "Campari"
                    # and you have an item with category "Campari"
                    ingredient_found = True

            else:
                # If no specific brand, just check for the category's presence
                if required_category_lower in inventory_categories:
                    ingredient_found = True
            
            if not ingredient_found:
                can_make_cocktail = False
                break  # Move to the next recipe

        if can_make_cocktail:
            makeable_cocktails.append(recipe)

    return makeable_cocktails

def _parse_api_cocktail_data(api_drink_data: dict) -> CocktailRecipe | None:
    """
    Parses the drink data from TheCocktailDB API response into a CocktailRecipe object.
    """
    if not api_drink_data:
        return None

    name = api_drink_data.get("strDrink")
    instructions = api_drink_data.get("strInstructions")
    image_url = api_drink_data.get("strDrinkThumb")
    description = api_drink_data.get("strCategory", "") # Or some other field if you prefer for description
    garnish = api_drink_data.get("strGarnish", "") # API doesn't always have a direct garnish field, often in instructions

    ingredients = []
    for i in range(1, 16):  # API has strIngredient1 to strIngredient15
        ingredient_name = api_drink_data.get(f"strIngredient{i}")
        measure = api_drink_data.get(f"strMeasure{i}")

        if ingredient_name and ingredient_name.strip(): # If ingredient name exists
            # Basic cleanup for measure, can be more sophisticated
            quantity = measure.strip() if measure else "a bit" # Default quantity if measure is missing
            
            # For specific_brand_optional: TheCocktailDB usually gives generic ingredients.
            # If an ingredient name itself is a brand (e.g., "Campari"), you might want to
            # set specific_brand_optional. This requires more complex logic or assumptions.
            # For now, we'll assume generic categories.
            ingredients.append(IngredientRequirement(category_needed=ingredient_name.strip(), quantity=quantity))
        else:
            break # No more ingredients

    if not name or not ingredients:
        return None # Essential data missing

    return CocktailRecipe(
        name=name,
        ingredients=ingredients,
        preparation_instructions=instructions if instructions else "No instructions provided.",
        garnish_suggestion=garnish,
        description=description,
        image_url=image_url if image_url else "",
        local_image_path=None  # Will be set later in Step 2
    )

# Keep a list of classic cocktail names you want to fetch
CLASSIC_COCKTAIL_NAMES = [
    "Margarita", "Martini", "Old Fashioned", "Mojito", "Daiquiri",
    "Manhattan", "Gin and Tonic", "Negroni", "Whiskey Sour", "Cosmopolitan",
    "Moscow Mule", "Pina Colada", "Mai Tai", "Bloody Mary", "Tequila Sunrise",
    "Screwdriver", "Long Island Iced Tea", "Bellini", "French 75", "Caipirinha",
]

_COCKTAIL_RECIPE_CACHE = {} # In-memory cache for CocktailRecipe objects for the current session

def get_all_recipes() -> list[CocktailRecipe]:
    """
    Fetches all cocktail recipes.
    Prioritizes loading from CURATED_COCKTAILS_FILE.
    If not found, fetches a predefined list of classics from TheCocktailDB API,
    saves them to CURATED_COCKTAILS_FILE, and returns them.
    Uses an in-memory cache for the session.
    """
    global _COCKTAIL_RECIPE_CACHE # In-memory cache for the session

    # Try loading from the curated JSON file first
    loaded_recipes = load_curated_cocktail_recipes(CURATED_COCKTAILS_FILE)
    if loaded_recipes:
        # Populate in-memory cache from file for consistency if needed by other parts
        for recipe in loaded_recipes:
            if recipe.name not in _COCKTAIL_RECIPE_CACHE:
                 _COCKTAIL_RECIPE_CACHE[recipe.name] = recipe
        return loaded_recipes

    # If curated file not found or empty, fetch from API, save, and return
    print(f"'{CURATED_COCKTAILS_FILE}' not found or empty. Fetching classics from API...")
    api_fetched_recipes = []
    for name in CLASSIC_COCKTAIL_NAMES: #
        if name in _COCKTAIL_RECIPE_CACHE: # Should be empty if file wasn't loaded
            recipe_obj = _COCKTAIL_RECIPE_CACHE[name]
            if recipe_obj: # Make sure it's not None if cache was somehow populated with a miss
                 api_fetched_recipes.append(recipe_obj)
            continue

        api_data = search_cocktail_by_name(name) #
        if api_data and api_data.get("drinks"):
            # The _parse_api_cocktail_data function needs to create CocktailRecipe objects
            # Ensure it's using the updated CocktailRecipe constructor (with local_image_path=None)
            parsed_recipe = _parse_api_cocktail_data(api_data["drinks"][0]) #
            if parsed_recipe:
                api_fetched_recipes.append(parsed_recipe)
                _COCKTAIL_RECIPE_CACHE[name] = parsed_recipe
                time.sleep(0.2) 
        else:
            print(f"Could not fetch or parse recipe for: {name} from API.")
            _COCKTAIL_RECIPE_CACHE[name] = None # Cache the miss to avoid re-fetching in this session

    if api_fetched_recipes:
        print(f"Saving {len(api_fetched_recipes)} API-fetched recipes to '{CURATED_COCKTAILS_FILE}'...")
        save_cocktail_recipes_to_json(api_fetched_recipes, CURATED_COCKTAILS_FILE)
    
    return api_fetched_recipes


def _ingredient_req_to_dict(req: IngredientRequirement) -> dict:
    return {
        "category_needed": req.category_needed,
        "quantity": req.quantity,
        "specific_brand_optional": req.specific_brand_optional
    }

def _dict_to_ingredient_req(data: dict) -> IngredientRequirement:
    return IngredientRequirement(
        category_needed=data.get("category_needed", ""),
        quantity=data.get("quantity", ""),
        specific_brand_optional=data.get("specific_brand_optional")
    )

def _cocktail_recipe_to_dict(recipe: CocktailRecipe) -> dict:
    """Converts a CocktailRecipe object to a dictionary for JSON storage."""
    return {
        "name": recipe.name,
        "ingredients": [_ingredient_req_to_dict(req) for req in recipe.ingredients],
        "preparation_instructions": recipe.preparation_instructions,
        "garnish_suggestion": recipe.garnish_suggestion,
        "description": recipe.description,
        "image_url": recipe.image_url,
        "local_image_path": recipe.local_image_path # Will be added in Step 2
    }

def _dict_to_cocktail_recipe(data: dict) -> CocktailRecipe | None:
    """Converts a dictionary (from JSON) back to a CocktailRecipe object."""
    try:
        ingredients_data = data.get("ingredients", [])
        ingredients = [_dict_to_ingredient_req(req_data) for req_data in ingredients_data]

        # Ensure essential fields are present
        if not data.get("name") or not ingredients:
            print(f"Warning: Skipping recipe due to missing name or ingredients. Data: {data.get('name')}")
            return None

        return CocktailRecipe(
            name=data.get("name"),
            ingredients=ingredients,
            preparation_instructions=data.get("preparation_instructions", "No instructions provided."),
            garnish_suggestion=data.get("garnish_suggestion", ""),
            description=data.get("description", ""),
            image_url=data.get("image_url", ""),
            local_image_path=data.get("local_image_path") # Will be added in Step 2
        )
    except Exception as e:
        print(f"Error converting dict to CocktailRecipe for '{data.get('name')}': {e}")
        return None

# --- File path for curated cocktails ---
CURATED_COCKTAILS_FILE = "data/cocktails.json"

# In src/cocktail_manager.py (continued)

def load_curated_cocktail_recipes(filepath: str = CURATED_COCKTAILS_FILE) -> list[CocktailRecipe]:
    """Loads cocktail recipes from a JSON file."""
    if not os.path.exists(filepath):
        print(f"Info: Curated cocktails file '{filepath}' not found.")
        return []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            list_of_dicts = json.load(f)
        
        recipes = []
        for data in list_of_dicts:
            recipe = _dict_to_cocktail_recipe(data)
            if recipe: # Only add if parsing was successful
                recipes.append(recipe)
        print(f"Loaded {len(recipes)} recipes from {filepath}")
        return recipes
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error loading or parsing {filepath}: {e}")
        return []

def save_cocktail_recipes_to_json(recipes: list[CocktailRecipe], filepath: str = CURATED_COCKTAILS_FILE):
    """Saves a list of CocktailRecipe objects to a JSON file."""
    try:
        # Ensure the directory exists
        directory = os.path.dirname(filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")

        list_of_dicts = [_cocktail_recipe_to_dict(recipe) for recipe in recipes]
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(list_of_dicts, f, indent=4)
        print(f"Saved {len(recipes)} recipes to {filepath}")
    except IOError as e:
        print(f"Error saving recipes to {filepath}: {e}")