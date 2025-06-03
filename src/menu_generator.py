# src/menu_generator.py
import os
import argparse # For command-line arguments

# Import necessary functions and classes from your other modules
from inventory_manager import InventoryItem, Spirit, Mixer, Garnish, enhance_inventory_item_with_api_data
from cocktail_manager import get_all_recipes, find_makeable_cocktails, CocktailRecipe
from data_handler import load_inventory, DEFAULT_INVENTORY_FILE

OUTPUT_FILENAME = "menu.md"
DEFAULT_INVENTORY_FILE = "data/inventory_VD85.json"

def format_inventory_markdown(inventory_list: list[InventoryItem], show_prices: bool, show_descriptions: bool) -> str:
    """
    Formats the inventory into a Markdown string, grouped by category.
    """
    if not inventory_list:
        return "## Bar Inventory\n\nYour bar is currently empty!\n"

    markdown_parts = ["# Bar Inventory\n"]
    
    # Group items by category
    inventory_by_category = {}
    for item in inventory_list:
        if item.category not in inventory_by_category:
            inventory_by_category[item.category] = []
        inventory_by_category[item.category].append(item)

    for category, items in sorted(inventory_by_category.items()):
        markdown_parts.append(f"\n## {category}\n")
        for item in sorted(items, key=lambda x: x.name): # Sort items by name within category
            brand_display = f" ({item.brand})" if item.brand and item.brand.lower() != item.name.lower() else ""
            price_display = f" - €{item.price:.2f}" if show_prices and hasattr(item, 'price') and item.price is not None else ""
            markdown_parts.append(f"- **{item.name}**{brand_display}{price_display}")
            
            if show_descriptions:
                description = ""
                if isinstance(item, Spirit) and item.tasting_notes:
                    description = item.tasting_notes
                elif item.user_notes: # Fallback to user_notes for any item
                    description = item.user_notes
                
                if description:
                    # Indent description for better readability
                    desc_lines = description.split('\n')
                    for line in desc_lines:
                        markdown_parts.append(f"  - *{line.strip()}*") # Italicize and indent description
            markdown_parts.append("") # Add a blank line for spacing after item, or remove if too much

    return "\n".join(markdown_parts)

def format_cocktails_markdown(makeable_cocktails: list[CocktailRecipe]) -> str:
    """
    Formats the list of makeable cocktails into a Markdown string.
    """
    if not makeable_cocktails:
        return "\n---\n\n# Makeable Cocktails\n\nNo cocktails can be made with the current inventory and recipes.\n"

    markdown_parts = ["\n---\n\n# Makeable Cocktails\n"]

    for cocktail in sorted(makeable_cocktails, key=lambda x: x.name): # Sort cocktails by name
        markdown_parts.append(f"\n## {cocktail.name}\n")
        
        if cocktail.image_url:
            # For Markdown, this is a link. For actual embedding in PDF, this URL would be downloaded.
            markdown_parts.append(f"![{cocktail.name} Image]({cocktail.image_url})\n") 
            
        if cocktail.description:
            markdown_parts.append(f"*{cocktail.description}*\n")
            
        markdown_parts.append("\n**Ingredients:**")
        for req in cocktail.ingredients:
            markdown_parts.append(f"- {str(req)}") # Uses IngredientRequirement.__str__
            
        if cocktail.garnish_suggestion:
            markdown_parts.append(f"\n**Garnish:** {cocktail.garnish_suggestion}")
            
        if cocktail.preparation_instructions:
            markdown_parts.append(f"\n**Instructions:**\n{cocktail.preparation_instructions}")
        markdown_parts.append("\n")

    return "\n".join(markdown_parts)

def generate_menu_file(filepath: str, show_prices: bool, show_descriptions: bool, enhance_inventory: bool):
    """
    Main function to generate the menu markdown file.
    """
    print("Starting menu generation...")

    # 1. Load Inventory
    current_inventory = load_inventory(DEFAULT_INVENTORY_FILE)
    if not current_inventory:
        print(f"Inventory is empty or could not be loaded from {DEFAULT_INVENTORY_FILE}. Cannot generate a meaningful menu.")
        # Optionally, create a dummy inventory for testing if needed here, then save it.
        # For now, we'll just exit if it's empty after trying to load.
        # If you want to ensure a sample is created if none exists, that logic
        # should ideally be in main.py or when an "add item" flow is implemented.
        # For this script, we assume inventory.json might exist or user adds items via other means.

    # 2. (Optional) Enhance Inventory with API data
    if enhance_inventory and current_inventory: # Only enhance if there's inventory
        print("Enhancing inventory with API data (this might take a moment)...")
        for item in current_inventory:
            enhance_inventory_item_with_api_data(item) #
        # Note: The enhance_inventory_item_with_api_data function modifies items in-place.
        # If you want these enhancements to persist, you should save the inventory back.
        # from data_handler import save_inventory # Import if you decide to save here
        # save_inventory(current_inventory, DEFAULT_INVENTORY_FILE)
        # print("Enhanced inventory saved.")
        # For now, enhancement is for this menu generation session only unless saved explicitly.
    
    # 3. Format Inventory Section
    inventory_md = format_inventory_markdown(current_inventory, show_prices, show_descriptions)

    # 4. Get Cocktail Recipes
    print("Fetching cocktail recipes...")
    all_recipes = get_all_recipes() #
    if not all_recipes:
        print("No cocktail recipes found. Cocktail section will be empty.")
        makeable_cocktails = []
    else:
        # 5. Find Makeable Cocktails
        print("Finding makeable cocktails...")
        makeable_cocktails = find_makeable_cocktails(current_inventory, all_recipes) #

    # 6. Format Cocktails Section
    cocktails_md = format_cocktails_markdown(makeable_cocktails)

    # 7. Combine and Write to File
    final_markdown = inventory_md + "\n" + cocktails_md
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(final_markdown)
        print(f"Menu successfully generated: {filepath}")
    except IOError as e:
        print(f"Error writing menu file: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a bar menu in Markdown format.")
    parser.add_argument("--output", default=OUTPUT_FILENAME, help=f"Output filename (default: {OUTPUT_FILENAME})")
    parser.add_argument("--hide-prices", action="store_false", dest="show_prices", help="Hide prices in the inventory section.")
    parser.add_argument("--hide-descriptions", action="store_false", dest="show_descriptions", help="Hide descriptions in the inventory section.")
    parser.add_argument("--no-enhance", action="store_false", dest="enhance_inventory", help="Do not attempt to enhance inventory with API data.")
    
    # Set defaults for boolean flags that are 'store_false'
    parser.set_defaults(show_prices=True, show_descriptions=True, enhance_inventory=True)

    args = parser.parse_args()

    # Ensure the output directory exists (if the filepath includes a directory)
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")

    generate_menu_file(args.output, args.show_prices, args.show_descriptions, args.enhance_inventory)