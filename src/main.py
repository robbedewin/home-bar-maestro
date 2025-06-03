from inventory_manager import InventoryItem, Spirit, Mixer, Garnish

if __name__ == "__main__":
    # Example usage of the InventoryItem and its subclasses
    gin = Spirit(name="London Dry Gin", brand="Beefeater", category="Spirit", quantity="1 Bottle", price=25.00,
                 type_of_liquor="London Dry Gin", abv=40.0, origin="United Kingdom",
                 tasting_notes="Juniper-forward with citrus notes", suggested_pairings_raw="Tonic Water, Lime",
                 user_notes="Great for gin and tonics")

    tonic = Mixer(name="Tonic Water", brand="Schweppes", category="Mixer", quantity="6 Cans", price=3.50,
                  mixer_type="Tonic Water", user_notes="Perfect for mixing with gin")

    lemon = Garnish(name="Lemon", brand="Fresh Produce", category="Garnish", quantity="1 Bag", price=2.00,
                    garnish_type="Lemon Slices", user_notes="Use in cocktails or as a garnish")

    print(gin.display_details())
    print(tonic.display_details())
    print(lemon.display_details())
