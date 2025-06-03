# src/data_handler.py
import json
import os

# Import your inventory classes. Adjust the path if your structure is different.
# If data_handler.py is in the same 'src' directory as inventory_manager.py:
from inventory_manager import InventoryItem, Spirit, Mixer, Garnish

# Define a default filepath (can be overridden)
# It's good practice to put data files in a subdirectory like 'data/'
DEFAULT_INVENTORY_FILE = "data/inventory.json"

def _inventory_item_to_dict(item: InventoryItem) -> dict:
    """
    Converts an InventoryItem object (and its subclasses) to a dictionary
    suitable for JSON serialization.
    """
    data = {
        "_type": item.__class__.__name__,  # Stores the class name (e.g., "Spirit")
        "name": item.name,
        "brand": item.brand,
        "category": item.category,
        "quantity": item.quantity,
        "price": item.price, # You added price, which is good!
        "user_notes": item.user_notes
    }

    # Add subclass-specific attributes
    if isinstance(item, Spirit):
        data["type_of_liquor"] = item.type_of_liquor
        data["abv"] = item.abv
        data["origin"] = item.origin
        data["tasting_notes"] = item.tasting_notes
        data["suggested_pairings_raw"] = item.suggested_pairings_raw
    elif isinstance(item, Mixer):
        data["mixer_type"] = item.mixer_type # You used mixer_type
    elif isinstance(item, Garnish):
        data["garnish_type"] = item.garnish_type # You used garnish_type
    
    return data

def _dict_to_inventory_item(data: dict) -> InventoryItem:
    """
    Converts a dictionary (from JSON) back to an appropriate InventoryItem subclass instance.
    """
    item_type_str = data.pop("_type", None) # Get and remove the _type field

    # The **data syntax unpacks the dictionary `data` into keyword arguments
    # for the class constructors. This assumes your constructor arguments
    # match the keys in the dictionary (after _type is removed).
    if item_type_str == "Spirit":
        return Spirit(**data)
    elif item_type_str == "Mixer":
        return Mixer(**data)
    elif item_type_str == "Garnish":
        return Garnish(**data)
    elif item_type_str == "InventoryItem": # Fallback for generic items if ever needed
        return InventoryItem(**data)
    else:
        # Handle unknown types or corrupted data
        # You might want to log this error or handle it more gracefully
        raise ValueError(f"Unknown inventory item type: {item_type_str}")
    
    
# Still in src/data_handler.py

def save_inventory(inventory_list: list[InventoryItem], filepath: str = DEFAULT_INVENTORY_FILE):
    """
    Saves the current inventory list to a JSON file.

    Args:
        inventory_list (list[InventoryItem]): The list of inventory items to save.
        filepath (str, optional): The path to the JSON file.
                                   Defaults to DEFAULT_INVENTORY_FILE.
    """
    # Ensure the 'data' directory exists
    # os.path.dirname(filepath) gets the directory part of the path
    directory = os.path.dirname(filepath)
    if directory and not os.path.exists(directory):
        os.makedirs(directory) # Create the directory if it doesn't exist
        print(f"Created directory: {directory}")

    list_of_dicts = [_inventory_item_to_dict(item) for item in inventory_list]
    
    try:
        with open(filepath, 'w') as f:
            json.dump(list_of_dicts, f, indent=4) # indent=4 makes the JSON file human-readable
        print(f"Inventory successfully saved to {filepath}")
    except IOError as e:
        print(f"Error: Could not write to file {filepath}. {e}")
    except TypeError as e:
        print(f"Error: Could not serialize inventory data. {e}")


def load_inventory(filepath: str = DEFAULT_INVENTORY_FILE) -> list[InventoryItem]:
    """
    Loads the inventory list from a JSON file.

    Args:
        filepath (str, optional): The path to the JSON file.
                                   Defaults to DEFAULT_INVENTORY_FILE.

    Returns:
        list[InventoryItem]: The loaded list of inventory items, or an empty list if
                             the file doesn't exist or an error occurs.
    """
    if not os.path.exists(filepath):
        print(f"Info: Inventory file '{filepath}' not found. Starting with an empty inventory.")
        return []

    try:
        with open(filepath, 'r') as f:
            list_of_dicts = json.load(f)
        
        inventory_list = []
        for item_data in list_of_dicts:
            try:
                inventory_list.append(_dict_to_inventory_item(item_data))
            except ValueError as e: # Catch errors from _dict_to_inventory_item
                print(f"Warning: Skipping item due to error: {e}. Data: {item_data}")
        
        print(f"Inventory successfully loaded from {filepath}")
        return inventory_list
    except json.JSONDecodeError as e:
        print(f"Error: Could not decode JSON from {filepath}. File might be corrupted. {e}")
        return [] # Return empty list on error
    except IOError as e:
        print(f"Error: Could not read file {filepath}. {e}")
        return [] # Return empty list on error