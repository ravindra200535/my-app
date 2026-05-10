import pandas as pd
import os
from datetime import datetime

class InventoryManager:
    """
    Core Logic Engine for 'The Big Game'.
    Handles inventory tracking, sales trends, and shortage predictions.
    """
    def __init__(self, data_file='inventory.csv'):
        self.data_file = data_file
        self.inventory = self.load_data()

    def load_data(self):
        """Loads inventory data from CSV or creates a new one."""
        if os.path.exists(self.data_file):
            return pd.read_csv(self.data_file)
        else:
            # Initial schema for the wholesaler/retailer
            columns = [
                'Product Name', 'Current Stock', 'Unit', 
                'Avg Daily Sales', 'Last Restocked', 'Threshold'
            ]
            return pd.DataFrame(columns=columns)

    def add_or_update_stock(self, bill_items):
        """
        Updates inventory based on items extracted from a bill.
        bill_items: List of dicts [{'Product Name': '...', 'Quantity': ...}]
        """
        for item in bill_items:
            name = item['Product Name'].strip().title()
            qty = float(item['Quantity'])
            
            if name in self.inventory['Product Name'].values:
                # Update existing stock
                idx = self.inventory[self.inventory['Product Name'] == name].index[0]
                self.inventory.at[idx, 'Current Stock'] += qty
                self.inventory.at[idx, 'Last Restocked'] = datetime.now().strftime("%Y-%m-%d")
            else:
                # Add new product to catalog
                new_row = {
                    'Product Name': name,
                    'Current Stock': qty,
                    'Unit': 'pcs',  # Default unit
                    'Avg Daily Sales': 1.0,  # Seed value
                    'Last Restocked': datetime.now().strftime("%Y-%m-%d"),
                    'Threshold': 10.0 # Default warning threshold
                }
                self.inventory = pd.concat([self.inventory, pd.DataFrame([new_row])], ignore_index=True)
        
        self.save_data()

    def calculate_predictions(self, panic_factor=1.0):
        """
        Predicts how many days of stock are left.
        Panic Factor: A multiplier for 'Avg Daily Sales' to account for high demand periods (e.g., festivals).
        """
        if self.inventory.empty:
            return self.inventory

        # Days of Stock Left (DSL) = Current Stock / (Avg Daily Sales * Panic Factor)
        self.inventory['Days of Stock Left'] = self.inventory.apply(
            lambda row: round(row['Current Stock'] / (max(row['Avg Daily Sales'], 0.1) * panic_factor), 1),
            axis=1
        )
        
        # Status calculation
        self.inventory['Status'] = self.inventory['Days of Stock Left'].apply(
            lambda x: 'CRITICAL' if x < 5 else 'STABLE'
        )
        
        return self.inventory

    def save_data(self):
        """Saves current inventory state to CSV."""
        self.inventory.to_csv(self.data_file, index=False)

if __name__ == "__main__":
    # Quick test logic
    engine = InventoryManager('test_inventory.csv')
    test_items = [{'Product Name': 'Basmati Rice', 'Quantity': 50}]
    engine.add_or_update_stock(test_items)
    print(engine.calculate_predictions())
