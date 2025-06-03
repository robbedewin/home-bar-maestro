# src/setup_my_inventory.py
import os
from inventory_manager import Spirit, Mixer, Garnish # Your classes
from data_handler import save_inventory, DEFAULT_INVENTORY_FILE

def create_bar_inventory():
    """
    Define all the items in the bar inventory here.
    This function will return a list of InventoryItem objects.
    """
    inventory = [
        # === Spirits ===
        Spirit(name="Hendrick's Gin", brand="Hendrick's", category="Gin", quantity="700ml", price=35.0,
               type_of_liquor="Scottish Gin", abv=41.4, origin="Scotland", 
               user_notes="Delicate, with cucumber and rose notes."),
        Spirit(name="Absolut Vodka", brand="Absolut", category="Vodka", quantity="1L", price=22.0,
               type_of_liquor="Swedish Vodka", abv=40.0, origin="Sweden"),
        Spirit(name="Jameson Irish Whiskey", brand="Jameson", category="Irish Whiskey", quantity="700ml", price=25.0,
               type_of_liquor="Blended Irish Whiskey", abv=40.0, origin="Ireland"),
        Spirit(name="Campari", brand="Campari", category="Campari", quantity="700ml", price=20.0,
               type_of_liquor="Bitter Aperitif", abv=25.0, origin="Italy", 
               user_notes="Essential for Negronis."),
        Spirit(name="Johnnie Walker Blue Label", brand="Johnnie Walker", category="Scotch Whisky", quantity="1L", price=180.0, type_of_liquor="Blended Scotch Whisky",
               abv=40.0, origin="Scotland", tasting_notes="Rich and complex with notes of honey, vanilla, and smoke."),
        Spirit(name="Tanqueray No. Ten", brand="Tanqueray", category="Gin", quantity="700ml", price=40.0,
                type_of_liquor="Premium Gin", abv=47.3, origin="Scotland",
                tasting_notes="Citrusy and floral with a hint of chamomile.",
                suggested_pairings_raw="Great with tonic or in a martini.",
                user_notes="A favorite for martinis and gin and tonics."),
        Spirit(name="Copperhead Gin", brand="Copperhead", category="Gin", 
                quantity="500ml", price=40.95, abv=40.0, type_of_liquor="Belgian Gin", origin="Belgium",
                user_notes="De gebruikte botanicals zijn engelwortel, jeneverbessen, kardemom, korianderzaad en sinaasappelzeste. Samen zorgt dit voor een soepel en kruidig karakter."),
        Spirit(name= "Monkey 47 Schwarzwald Dry Gin", brand="Monkey 47", category="Gin",
               quantity="500ml", price=36.5, abv=47.0, origin="Germany", type_of_liquor="Schwarzwald Dry Gin",),
        Spirit(name="Martini Reserve Riserva Speciale Rubino", brand="Martini", category="Vermouth",
               quantity="750ml", price=15.0, abv=18.0, origin="Italy", type_of_liquor="Sweet Vermouth",),
        
        # ... add all your father's spirits ...

        # === Mixers ===
        Mixer(name="Schweppes Indian Tonic", brand="Schweppes", category="Tonic Water", quantity="6x200ml", price=5.0,
              mixer_type="Tonic Water"),
        Mixer(name="Fever-Tree Elderflower Tonic", brand="Fever-Tree", category="Tonic Water", quantity="4x200ml", price=6.0,
              mixer_type="Flavoured Tonic Water", user_notes="Pairs well with floral gins."),
        Mixer(name="Generic Orange Juice", brand="Juicy Co.", category="Orange Juice", quantity="1L", price=2.0,
              mixer_type="Juice"),
        Mixer(name="Noilly Prat Original Dry", brand="Noilly Prat", category="Dry Vermouth", quantity="750ml", price=15.0,
              mixer_type="Vermouth"),
        Mixer(name="Martini Rosso", brand="Martini", category="Sweet Vermouth", quantity="750ml", price=10.0,
              mixer_type="Vermouth"),
        Mixer(name="Coca-Cola Classic", brand="Coca-Cola", category="Cola", quantity="6x330ml", price=4.0, mixer_type="Cola",),
        # ... add all your mixers ...

        # === Garnishes ===
        Garnish(name="Lemon", brand="Fresh", category="Lemon", quantity="5 units", price=1.0,
                garnish_type="Citrus Fruit", user_notes="For wedges and twists."),
        Garnish(name="Lime", brand="Fresh", category="Lime", quantity="6 units", price=1.2,
                garnish_type="Citrus Fruit"),
        Garnish(name="Orange", brand="Fresh", category="Orange", quantity="3 units", price=0.9,
                garnish_type="Citrus Fruit", user_notes="For slices and peels."),
        # ... add all your garnishes ...
    ]
    return inventory

def main():
    print("Creating a detailed bar inventory...")
    my_bar_inventory = create_bar_inventory()

    # Ensure the data directory exists (though save_inventory also does this)
    project_root = os.path.dirname(os.path.dirname(__file__)) # Correctly gets src's parent
    data_dir = os.path.join(project_root, "data") 
    os.makedirs(data_dir, exist_ok=True)

    inventory_file_path = os.path.join(data_dir, "inventory_VD85.json") # Ensures it uses the data subdir

    save_inventory(my_bar_inventory, inventory_file_path) # Use the specific path
    print(f"Detailed inventory saved to {inventory_file_path} with {len(my_bar_inventory)} items.")
    print("You can now run main.py or menu_generator.py, and they will load this inventory.")

if __name__ == "__main__":
    main()