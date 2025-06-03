import os, json
from cocktail_manager import get_all_recipes

def _recipe_to_dict(recipe):
    return {
        "name": recipe.name,
        "description": recipe.description,
        "garnish": recipe.garnish_suggestion,
        "image_url": recipe.image_url,
        "instructions": recipe.preparation_instructions,
        "ingredients": [
            {
                "category_needed": req.category_needed,
                "quantity": req.quantity,
                "specific_brand_optional": req.specific_brand_optional
            }
            for req in recipe.ingredients
        ]
    }

def main():
    recipes = get_all_recipes()
    # ensure data folder exists
    project_root = os.path.dirname(os.path.dirname(__file__))
    out_dir = os.path.join(project_root, "data")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "cocktails.json")

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump([_recipe_to_dict(r) for r in recipes], f, indent=4)
    print(f"Wrote {len(recipes)} recipes to {out_file}")

if __name__ == "__main__":
    main()