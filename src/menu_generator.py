# src/menu_generator.py
import os
import argparse # For command-line arguments
from jinja2 import Environment, FileSystemLoader
from xhtml2pdf import pisa

# Import necessary functions and classes from your other modules
from inventory_manager import InventoryItem, Spirit, Mixer, Garnish, enhance_inventory_item_with_api_data
from cocktail_manager import get_all_recipes, find_makeable_cocktails, CocktailRecipe
from data_handler import load_inventory # DEFAULT_INVENTORY_FILE will be used from this script's global

# Project root and default inventory file (respecting your specific JSON file)
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__)) # This gives the parent of 'src'
DEFAULT_INVENTORY_FILE = os.path.join(PROJECT_ROOT, "data", "inventory_VD85.json")


def format_inventory_markdown(inventory_list: list[InventoryItem], show_prices: bool, show_descriptions: bool) -> str:
    """
    Formats the inventory into a Markdown string, grouped by category.
    (Your existing function - no changes needed here for HTML output, it's Markdown specific)
    """
    if not inventory_list:
        return "## Bar Inventory\n\nYour bar is currently empty!\n"

    markdown_parts = ["# Bar Inventory\n"]
    
    inventory_by_category = {}
    for item in inventory_list:
        if item.category not in inventory_by_category:
            inventory_by_category[item.category] = []
        inventory_by_category[item.category].append(item)

    for category, items in sorted(inventory_by_category.items()):
        markdown_parts.append(f"\n## {category}\n")
        for item in sorted(items, key=lambda x: x.name):
            brand_display = f" ({item.brand})" if item.brand and item.brand.lower() != item.name.lower() else ""
            price_display = f" - €{item.price:.2f}" if show_prices and hasattr(item, 'price') and item.price is not None else ""
            markdown_parts.append(f"- **{item.name}**{brand_display}{price_display}")
            
            if show_descriptions:
                description = ""
                if isinstance(item, Spirit) and item.tasting_notes:
                    description = item.tasting_notes
                elif item.user_notes:
                    description = item.user_notes
                
                if description:
                    desc_lines = description.split('\n')
                    for line in desc_lines:
                        markdown_parts.append(f"  - *{line.strip()}*")
            markdown_parts.append("") 

    return "\n".join(markdown_parts)

def format_cocktails_markdown(makeable_cocktails: list[CocktailRecipe]) -> str:
    """
    Formats the list of makeable cocktails into a Markdown string.
    (Your existing function - no changes needed here for HTML output, it's Markdown specific)
    """
    if not makeable_cocktails:
        return "\n---\n\n# Makeable Cocktails\n\nNo cocktails can be made with the current inventory and recipes.\n"

    markdown_parts = ["\n---\n\n# Makeable Cocktails\n"]

    for cocktail in sorted(makeable_cocktails, key=lambda x: x.name):
        markdown_parts.append(f"\n## {cocktail.name}\n")
        
        image_md = ""
        if cocktail.local_image_path:
            image_md = f"![{cocktail.name} Image]({cocktail.local_image_path})\n"    
        elif cocktail.image_url:
            image_md = f"![{cocktail.name} Image]({cocktail.image_url})\n"
        
        if image_md:
            markdown_parts.append(image_md)
            
        if cocktail.description:
            markdown_parts.append(f"*{cocktail.description}*\n")
            
        markdown_parts.append("\n**Ingredients:**")
        for req in cocktail.ingredients:
            markdown_parts.append(f"- {str(req)}")
            
        if cocktail.garnish_suggestion:
            markdown_parts.append(f"\n**Garnish:** {cocktail.garnish_suggestion}")
            
        if cocktail.preparation_instructions:
            markdown_parts.append(f"\n**Instructions:**\n{cocktail.preparation_instructions}")
        markdown_parts.append("\n")

    return "\n".join(markdown_parts)

# This is your existing HTML generation function, it looks good.
def generate_html_menu(context: dict, output_html_path: str): # <<< CORRECTED SIGNATURE
    """
    Generates an HTML menu using Jinja2 templates with the provided context.
    The context dictionary is expected to be fully prepared by the caller.
    """
    # project_root should use abspath for robustness when script is called from other dirs
    current_script_path = os.path.abspath(__file__)
    project_root_from_script = os.path.dirname(os.path.dirname(current_script_path))
    
    # Use TEMPLATES_DIR global, but ensure it's based on robust project root
    # TEMPLATES_DIR is already defined globally using os.path.dirname(__file__), which is fine
    # if the script is always run from project root relative to src.
    # Using the one derived from abspath is safer if this script could be called from elsewhere.
    # For consistency with your global TEMPLATES_DIR:
    # templates_dir_for_loader = TEMPLATES_DIR

    # Or, more robustly within the function if TEMPLATES_DIR wasn't global or to be sure:
    templates_dir_for_loader = os.path.join(project_root_from_script, "templates")

    if not os.path.exists(templates_dir_for_loader):
        os.makedirs(templates_dir_for_loader)
        print(f"Created templates directory: {templates_dir_for_loader}.")
        # You should create menu_template.html in this directory
        # For now, we'll just warn if the template file itself is missing.
        
    env = Environment(loader=FileSystemLoader(templates_dir_for_loader))
    try:
        template = env.get_template("menu_template.html")
    except Exception as e: # jinja2.exceptions.TemplateNotFound is more specific
        print(f"Error: Could not find 'menu_template.html' in '{templates_dir_for_loader}'. {e}")
        print("Please create 'menu_template.html' inside the 'templates' directory (in your project root).")
        return

    # The 'context' dictionary is now passed in directly and should already contain:
    # "bar_name", 
    # "spirits_by_category", (this was inventory_by_category from the old generate_html_menu internal logic)
    # "mixers_by_category", 
    # "makeable_cocktails",
    # "show_prices", 
    # "show_descriptions"
    # The item._type was also set in main_orchestrator for items in these categories.

    html_output = template.render(context) # Use the pre-prepared context

    try:
        # Ensure output directory for HTML file exists
        output_dir = os.path.dirname(output_html_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"Created output directory for HTML: {output_dir}")

        with open(output_html_path, 'w', encoding='utf-8') as f:
            f.write(html_output)
        print(f"HTML Menu successfully generated: {output_html_path}")
    except IOError as e:
        print(f"Error writing HTML menu file: {e}")
        
def convert_html_to_pdf(html_filepath: str, pdf_filepath: str, css_filepath: str = None): # Add css_filepath
    print(f"Converting '{html_filepath}' to PDF using xhtml2pdf: '{pdf_filepath}'...")
    if css_filepath and os.path.exists(css_filepath):
        print(f"Note: xhtml2pdf primarily uses CSS linked in the HTML. External CSS path: {css_filepath}")
    elif css_filepath:
        print(f"Warning: External CSS file '{css_filepath}' not found. xhtml2pdf will rely on CSS linked in HTML.")

    try:
        with open(html_filepath, 'r', encoding='utf-8') as source_html_file:
            source_html = source_html_file.read()

        with open(pdf_filepath, "w+b") as result_file:
            # xhtml2pdf uses CSS linked in the HTML. If you need to pass an external CSS path
            # directly to pisa.CreatePDF, it's usually done by ensuring the HTML source
            # correctly links to it using a <link> tag with a resolvable path,
            # or by embedding styles in <style> tags.
            # The 'css_filepath' argument here is more for compatibility if you switch
            # to a library like WeasyPrint, or for logging/debugging.
            pisa_status = pisa.CreatePDF(
                    source_html,
                    dest=result_file,
                    encoding='utf-8') 

            if not pisa_status.err:
                print(f"PDF successfully generated with xhtml2pdf: {pdf_filepath}")
                return True
            else:
                print(f"Error during PDF conversion with xhtml2pdf: {pisa_status.err}")
                return False
    except Exception as e:
        print(f"An unexpected error occurred with xhtml2pdf: {e}")
        return False

def main_orchestrator(output_path: str, output_format: str,
                      show_prices: bool, show_descriptions: bool, 
                      enhance_inventory: bool, bar_name: str,
                      pdf_output_path: str = None): # <<< Added pdf_output_path
    # ... (Existing data loading and preparation logic as in your latest script)
    # ... (This includes loading inventory, enhancing, getting recipes, finding makeable,
    #      separating spirits and mixers, sorting them, and creating html_context)
    print(f"Starting menu generation for format: {output_format.upper()}...")

    # 1. Load Inventory
    print(f"Loading inventory from: {DEFAULT_INVENTORY_FILE}")
    current_inventory = load_inventory(DEFAULT_INVENTORY_FILE)
    
    if not current_inventory:
        print(f"Inventory is empty or could not be loaded from {DEFAULT_INVENTORY_FILE}.")
    
    # 2. (Optional) Enhance Inventory
    if enhance_inventory and current_inventory:
        print("Enhancing inventory with API data...")
        for item in current_inventory:
            enhance_inventory_item_with_api_data(item)
    
    # 3. Get Cocktail Recipes
    print("Fetching cocktail recipes...")
    all_recipes = get_all_recipes()
    
    makeable_cocktails = []
    if not all_recipes:
        print("No cocktail recipes found.")
    elif not current_inventory:
        print("Inventory is empty, no cocktails can be made.")
    else:
        print("Finding makeable cocktails...")
        makeable_cocktails = find_makeable_cocktails(current_inventory, all_recipes)

    # Prepare data for HTML template (separated and sorted)
    spirits_and_liqueurs_by_cat = {}
    mixers_by_cat = {}
    MIXER_CATEGORIES = ["Tonic Water", "Soda Water", "Juice", "Syrup", "Cola", "Ginger Ale", "Ginger Beer", "Mixer", "Soft Drink"] 

    if current_inventory:
        for item in current_inventory:
            item._type = item.__class__.__name__
            is_mixer = any(mixer_cat_keyword.lower() in item.category.lower() for mixer_cat_keyword in MIXER_CATEGORIES)
            target_dict = mixers_by_cat if is_mixer else spirits_and_liqueurs_by_cat
            if item.category not in target_dict:
                target_dict[item.category] = []
            target_dict[item.category].append(item)

    sorted_spirits_and_liqueurs = {k: sorted(v, key=lambda x: x.name) for k, v in sorted(spirits_and_liqueurs_by_cat.items())}
    sorted_mixers = {k: sorted(v, key=lambda x: x.name) for k, v in sorted(mixers_by_cat.items())}
    sorted_makeable_cocktails = sorted(makeable_cocktails, key=lambda x: x.name)
    
    html_generated_path = None

    if output_format.lower() == 'html' or pdf_output_path: # Generate HTML if format is HTML or if PDF is requested
        html_context = {
            "bar_name": bar_name,
            "spirits_by_category": sorted_spirits_and_liqueurs,
            "mixers_by_category": sorted_mixers,
            "makeable_cocktails": sorted_makeable_cocktails,
            "show_prices": show_prices,
            "show_descriptions": show_descriptions
        }
        
        # Determine HTML output path
        # If only PDF is requested, we can use a temporary HTML file or a fixed name
        current_html_output_path = output_path if output_format.lower() == 'html' else os.path.join(PROJECT_ROOT, "temp_menu_for_pdf.html")
        
        generate_html_menu(html_context, current_html_output_path)
        html_generated_path = current_html_output_path # Store path if HTML was generated

    elif output_format.lower() in ['md', 'markdown']:
        inventory_md = format_inventory_markdown(current_inventory if current_inventory else [], show_prices, show_descriptions)
        cocktails_md = format_cocktails_markdown(makeable_cocktails)
        final_markdown = inventory_md + "\n" + cocktails_md
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(final_markdown)
            print(f"Markdown Menu successfully generated: {output_path}")
        except IOError as e:
            print(f"Error writing Markdown menu file: {e}")
    else:
        if not pdf_output_path: # Only error if not just generating PDF
             print(f"Error: Unsupported output format '{output_format}'. Choose 'html' or 'md'.")


    # 5. Convert to PDF if requested and HTML was generated
    if pdf_output_path and html_generated_path and os.path.exists(html_generated_path):
        # Assuming menu_style.css is in the same directory as the generated HTML
        # or in a standard location like 'static/css/menu_style.css' relative to PROJECT_ROOT
        # For simplicity, let's assume menu_style.css is in PROJECT_ROOT
        css_file_path = os.path.join(PROJECT_ROOT, "menu_style.css") # Or your actual path
        if not os.path.exists(css_file_path):
            print(f"Warning: CSS file not found at {css_file_path}. PDF might not be styled as expected.")
            css_file_path = None # Proceed without external CSS if not found

        convert_html_to_pdf(html_generated_path, pdf_output_path, css_filepath=css_file_path)
        
        # Clean up temporary HTML file if it was created only for PDF
        if output_format.lower() != 'html' and html_generated_path == os.path.join(PROJECT_ROOT, "temp_menu_for_pdf.html"):
            try:
                os.remove(html_generated_path)
                print(f"Removed temporary HTML file: {html_generated_path}")
            except OSError as e:
                print(f"Error removing temporary HTML file: {e}")
    elif pdf_output_path and not html_generated_path:
        print("Error: PDF output requested, but HTML generation failed or was skipped.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a bar menu in HTML, Markdown, or PDF format.")
    parser.add_argument("--output", 
                        help="Output filename for HTML or Markdown (e.g., menu.html or menu.md). Default determined by --format.")
    parser.add_argument("--pdf", dest="pdf_output", default=None,
                        help="Output filename for PDF (e.g., menu.pdf). If provided, HTML will be generated first and then converted.")
    parser.add_argument("--format", default="html", choices=['html', 'md', 'markdown'], 
                        help="Primary output format if not generating PDF directly: html or md (default: html). If --pdf is used, HTML is generated as an intermediate step.")
    # ... (other arguments: --hide-prices, --hide-descriptions, --no-enhance, --bar-name remain the same)
    parser.add_argument("--hide-prices", action="store_false", dest="show_prices", 
                        help="Hide prices in the inventory section.")
    parser.add_argument("--hide-descriptions", action="store_false", dest="show_descriptions", 
                        help="Hide descriptions in the inventory section.")
    parser.add_argument("--no-enhance", action="store_false", dest="enhance_inventory", 
                        help="Do not attempt to enhance inventory with API data.")
    parser.add_argument("--bar-name", default="The Home Bar", help="Name of the bar for the menu title.")
    
    parser.set_defaults(show_prices=True, show_descriptions=True, enhance_inventory=True)
    args = parser.parse_args()

    output_filename_arg = args.output
    if not output_filename_arg and not args.pdf_output : # If no output specified at all
        output_filename_arg = "menu.html" if args.format.lower() == 'html' else "menu.md"
    elif not output_filename_arg and args.pdf_output and args.format.lower() != 'html':
        # If only --pdf is given, and --format isn't html, we still need an html output name for the intermediate step
         output_filename_arg = "temp_menu_for_pdf.html" # Default name for intermediate HTML if not specified

    # Determine absolute path for primary output (HTML/MD)
    primary_output_abs_path = None
    if output_filename_arg:
        if os.path.isabs(output_filename_arg):
            primary_output_abs_path = output_filename_arg
        else:
            primary_output_abs_path = os.path.join(PROJECT_ROOT, output_filename_arg)
        
        output_dir_for_file = os.path.dirname(primary_output_abs_path)
        if output_dir_for_file and not os.path.exists(output_dir_for_file):
            os.makedirs(output_dir_for_file)
            print(f"Created output directory: {output_dir_for_file}")

    # Determine absolute path for PDF output
    pdf_abs_path = None
    if args.pdf_output:
        if os.path.isabs(args.pdf_output):
            pdf_abs_path = args.pdf_output
        else:
            pdf_abs_path = os.path.join(PROJECT_ROOT, args.pdf_output)
        
        pdf_output_dir = os.path.dirname(pdf_abs_path)
        if pdf_output_dir and not os.path.exists(pdf_output_dir):
            os.makedirs(pdf_output_dir)
            print(f"Created PDF output directory: {pdf_output_dir}")

    # If only --pdf is specified, the primary output format for the intermediate step is HTML.
    effective_output_format = args.format
    if args.pdf_output and not primary_output_abs_path:
        effective_output_format = 'html' # Intermediate must be HTML for PDF conversion
        primary_output_abs_path = os.path.join(PROJECT_ROOT, "temp_menu_for_pdf.html")


    main_orchestrator(primary_output_abs_path, effective_output_format, 
                      args.show_prices, args.show_descriptions, 
                      args.enhance_inventory, args.bar_name,
                      pdf_output_path=pdf_abs_path)

