class InventoryItem:
    def __init__(self, name: str, brand: str, category: str, quantity: str, price: float, user_notes: str = ""): 
        """
        Initializes an InventoryItem instance.

        Args:
            name (str): Specific name of the item Hendrick's Gin, Schweppes Tonic, etc.
            brand (str): Specific brand of the item, e.g., Hendrick's, Schweppes.
            category (str): General category of the item, e.g., Gin, Tonic, Garnish, ...
            quantity (str): Description of quantity, e.g., 1L, 500ml, 3 lemons, etc.
            price (float): Price of the item in euros.
            user_notes (str): any additional notes the user wants to add about the item, defaults to an empty string.
        """
        
        self.name = name
        self.brand = brand
        self.category = category
        self.quantity = quantity
        self.price = price
        self.user_notes = user_notes
        
    def display_details(self):
        """
        Returns a string representation of the inventory item details.
        """
        return (f"Name: {self.name}, Brand: {self.brand}, Category: {self.category}, "
                f"Quantity: {self.quantity}, Price: €{self.price:.2f}, Notes: {self.user_notes}")
            
            
class Spirit(InventoryItem):
    def __init__(self, name: str, brand: str, category: str, quantity: str, price: float, type_of_liquor: str, abv: float, origin: str,
                 tasting_notes: str = "", suggested_pairings_raw: str = "", user_notes: str = ""):
        
        super().__init__(name, brand, category, quantity, price, user_notes)
        
        self.type_of_liquor = type_of_liquor  # e.g., "London Dry Gin", "Highland Single Malt Scotch"
        self.abv = abv  # Alcohol By Volume, e.g., 40.0
        self.origin = origin  # Country/Region of origin
        self.tasting_notes = tasting_notes  # Flavor profile
        self.suggested_pairings_raw = suggested_pairings_raw  # Simple text for pairings
        
    def display_details(self):
        """
        Returns a string representation of the spirit details, including specific attributes.
        """
        base_details = super().display_details()  # Call the base class method
        spirit_details = (f"Type: {self.type_of_liquor}, ABV: {self.abv}%, Origin: {self.origin}, "
                         f"Tasting Notes: {self.tasting_notes}, Pairings: {self.suggested_pairings_raw}")
        return f"{base_details}, {spirit_details}"


class Mixer(InventoryItem):
    def __init__(self, name: str, brand: str, category: str, quantity: str, price: float, mixer_type: str, user_notes: str = ""):
        super().__init__(name, brand, category, quantity, price, user_notes)
        
        self.mixer_type = mixer_type  # e.g., "Tonic Water", "Soda Water", "Juice"
        
    def display_details(self):
        """
        Returns a string representation of the mixer details, including specific attributes.
        """
        base_details = super().display_details()  # Call the base class method
        mixer_details = f"{base_details}, Mixer Type: {self.mixer_type}"
        return mixer_details
    
class Garnish(InventoryItem):
    def __init__(self, name: str, brand: str, category: str, quantity: str, price: float, garnish_type: str, user_notes: str = ""):
        super().__init__(name, brand, category, quantity, price, user_notes)
        
        self.garnish_type = garnish_type  # e.g., "Lemon", "Olive", "Mint"
        
    def display_details(self):
        """
        Returns a string representation of the garnish details, including specific attributes.
        """
        base_details = super().display_details()  # Call the base class method
        garnish_details = f"{base_details}, Garnish Type: {self.garnish_type}"
        return garnish_details
    


