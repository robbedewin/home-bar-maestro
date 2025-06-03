import time
from api_client import search_cocktail_by_name

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
                 description: str = "", image_url: str = ""):
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
        if self.image_url:
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
        image_url=image_url if image_url else ""
    )

# Keep a list of classic cocktail names you want to fetch
CLASSIC_COCKTAIL_NAMES = [
    "Margarita", "Martini", "Old Fashioned", "Mojito", "Daiquiri",
    "Manhattan", "Gin and Tonic", "Negroni", "Whiskey Sour", "Cosmopolitan",
    "Moscow Mule", "Pina Colada" # Add more as you like
]

_COCKTAIL_RECIPE_CACHE = {} # In-memory cache for CocktailRecipe objects for the current session

def get_all_recipes() -> list[CocktailRecipe]:
    """
    Fetches a predefined list of classic cocktails from TheCocktailDB API
    and returns them as CocktailRecipe objects. Uses an in-memory cache.
    """
    global _COCKTAIL_RECIPE_CACHE
    
    fetched_recipes = []
    for name in CLASSIC_COCKTAIL_NAMES:
        if name in _COCKTAIL_RECIPE_CACHE:
            fetched_recipes.append(_COCKTAIL_RECIPE_CACHE[name])
            continue

        api_data = search_cocktail_by_name(name)
        if api_data and api_data.get("drinks"):
            # API might return multiple drinks for a search, take the first one
            parsed_recipe = _parse_api_cocktail_data(api_data["drinks"][0])
            if parsed_recipe:
                fetched_recipes.append(parsed_recipe)
                _COCKTAIL_RECIPE_CACHE[name] = parsed_recipe # Cache the parsed object
                time.sleep(0.2) # Be a little nice to the API, brief pause
        else:
            print(f"Could not fetch or parse recipe for: {name}")
            
    return fetched_recipes