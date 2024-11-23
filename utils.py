import pandas as pd

# Load pricing data
pricing_df = pd.read_csv("pricing_data.csv")


def calculate_price_type_a(item):
    # Extract item details
    total_exposed_area = float(item["Total Exposed Area (Carcass)"])
    total_internal_area = float(item["Total Internal Area (Carcass)"])
    external_finish = item["External Finish"]
    internal_finish = item["Internal Finish"]
    external_category = item["External Category"]
    internal_category = item["Internal Category"]
    shutter_category = item["Shutter Category"]
    shutter_area = float(item["Shutter Area"])
    shutter_finish = item["Shutter Finish"]

    # Helper function to get price per sqft
    def get_price(finish, category):
        try:
            price = pricing_df[
                (pricing_df["Finish"] == finish) & (pricing_df["Category"] == category)
            ]["Price_per_sqft"]
            return float(price.values[0]) if not price.empty else 0.0
        except (ValueError, TypeError):
            return 0.0

    # Calculate prices with separate categories
    external_price = get_price(external_finish, external_category) * total_exposed_area
    internal_price = get_price(internal_finish, internal_category) * total_internal_area
    shutter_price = get_price(shutter_finish, shutter_category) * shutter_area

    total_price = external_price + internal_price + shutter_price
    return total_price


def calculate_price_type_b(item):
    total_area = float(item["Total Area"])
    finish = item["Finish"]

    # Helper function to get price per sqft for Type B (using rows where Category is None)
    def get_price(finish):
        try:
            price = pricing_df[
                (pricing_df["Finish"] == finish) & (pricing_df["Category"].isna())
            ]["Price_per_sqft"]
            return float(price.values[0]) if not price.empty else 0.0
        except (ValueError, TypeError):
            return 0.0

    total_price = get_price(finish) * total_area
    return total_price
