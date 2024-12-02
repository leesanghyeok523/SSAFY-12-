import json
import random
from datetime import datetime, timedelta

# Define savings and deposit product IDs
savings_product_ids = [
    "WR0001F", "WR0001L", "00266451", "10521001000846001",
    "10527001000925000", "10527001001272000", "10527001001278000",
    "01020400490002", "01020400510001", "01020400530001", "01020400660001","1020400640001",
    "TD11330029000", "TD11330030000", "TD11330031000", "220002101",
    "220002501", "220002701", "10-01-30-031-0018-0000", "10-01-30-031-0036",
    "10-01-30-031-0049-0000", "21000111", "21001116", "21001199",
    "21001236", "21001259", "21001268", "01211210113", "01211210121",
    "01211210122", "03101", "03700", "010200100051", "010200100084",
    "010200100092", "010200100104", "010200100109", "230-0119-85",
    "10-047-1360-0002", "10-047-1365-0001", "10-047-1381-0001", "10-047-1387-0001", "10-059-1264-0001"
]

deposit_product_ids = [
    "WR0001B", "00320342", "10511008000996000", "10511008001004000", 
    "10511008001166004", "10511008001278000", "01030500510002", 
    "01030500560002", "01030500600002", "TD11300027000", 
    "TD11300031000", "TD11300035000", "TD11300036000", 
    "101272000006", "101272000057", "101272000058", 
    "10-01-20-024-0046-0000", "10-01-20-024-0059-0000", "21001115", 
    "21001203", "21001266", "01211310121", 
    "01211310130", "06492", "010300100335", "010300100335", "200-0135-12", "10-003-1225-0001", 
    "10-003-1381-0001", "10-003-1384-0001", "10-003-1387-0001", "01013000110000000001"
]



# Function to generate random date of birth
def random_date_of_birth(start_year=1970, end_year=2005):
    start_date = datetime(start_year, 1, 1)
    end_date = datetime(end_year, 1, 1)
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return (start_date + timedelta(days=random_days)).date()

# Generate dummy data
users = []
user_saving_products = []
user_deposit_products = []

# To prevent duplicate user_id and product_id combinations
used_saving_combinations = set()
used_deposit_combinations = set()

for user_id in range(1, 10001):  # Create 5 users
    date_of_birth = random_date_of_birth()
    age = datetime.now().year - date_of_birth.year
    
    # Create user data
    user_data = {
        "model": "core.user",
        "pk": user_id,
        "fields": {
            "password": f"password{user_id}",
            "username": f"user{user_id}",
            "email": f"user{user_id}@example.com",
            "date_of_birth": str(date_of_birth),
            "nickname": f"User{user_id}",
            "income_level": random.randint(28000000, 280000000),
            "current_assets": random.randint(1000000, 130000000),
            "age": age
        }
    }
    users.append(user_data)

    # Assign random saving products to the user
    for _ in range(random.randint(1, 4)):  # Assign 1-3 saving products
        while True:
            savings_product_id = random.choice(savings_product_ids)
            combination = (user_id, savings_product_id)
            if combination not in used_saving_combinations:
                used_saving_combinations.add(combination)
                saving_product_data = {
                    "model": "core.user_saving_products",
                    "pk": len(user_saving_products) + 1,
                    "fields": {
                        "user_id": user_id,
                        "savingsproduct_id": savings_product_id
                    }
                }
                user_saving_products.append(saving_product_data)
                break

    # Assign random deposit products to the user
    for _ in range(random.randint(1, 4)):  # Assign 1-3 deposit products
        while True:
            deposit_product_id = random.choice(deposit_product_ids)
            combination = (user_id, deposit_product_id)
            if combination not in used_deposit_combinations:
                used_deposit_combinations.add(combination)
                deposit_product_data = {
                    "model": "core.user_deposit_products",
                    "pk": len(user_deposit_products) + 1,
                    "fields": {
                        "user_id": user_id,
                        "depositproduct_id": deposit_product_id
                    }
                }
                user_deposit_products.append(deposit_product_data)
                break

# Combine all data
dummy_data = users + user_saving_products + user_deposit_products

# Save as JSON file
with open("fixtures/dummy_data_5.json", "w", encoding="utf-8") as f:
    json.dump(dummy_data, f, ensure_ascii=False, indent=2)

print("Dummy data generated and saved to fixtures/dummy_data_5.json")
