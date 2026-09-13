from fastapi import APIRouter, UploadFile, File
from pypdf import PdfReader
from supabase import create_client, Client

import io
import re
import os
import requests

from dotenv import load_dotenv

load_dotenv()

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
PERSONA_API_KEY = os.getenv("PERSONA_API_KEY")
PERSONA_TEMPLATE_ID = os.getenv("PERSONA_TEMPLATE_ID")
NESSIE_API_KEY = os.getenv("NESSIE_API_KEY")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_PUBLISHABLE_KEY = os.getenv("SUPABASE_PUBLISHABLE_KEY")

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_PUBLISHABLE_KEY
)

latest_financial_aid = {}

router = APIRouter()


@router.get("/test-nessie-key")
def test_nessie_key():
    return {
        "nessie_key_loaded": bool(NESSIE_API_KEY)
    }

@router.get("/nessie/accounts")
def get_nessie_accounts():

    url = "https://api.nessieisreal.com/accounts"

    params = {
        "key": NESSIE_API_KEY
    }

    response = requests.get(
        url,
        params=params
    )

    return response.json()

@router.post("/nessie/create-test-customer")
def create_test_customer():

    url = "https://api.nessieisreal.com/customers"

    params = {
        "key": NESSIE_API_KEY
    }

    customer = {
        "first_name": "Test",
        "last_name": "Student",
        "address": {
            "street_number": "123",
            "street_name": "College Ave",
            "city": "Houston",
            "state": "TX",
            "zip": "77002"
        }
    }

@router.post("/nessie/create-test-account")
def create_test_account():

    customer_id = "83546e2e-bb3a-49c3-88ca-4c9d917cc60f"

    url = f"https://api.nessieisreal.com/customers/{customer_id}/accounts"

    params = {
        "key": NESSIE_API_KEY
    }

    account = {
        "type": "Checking",
        "nickname": "Student Checking",
        "rewards": 0,
        "balance": 1500
    }

    response = requests.post(
        url,
        params=params,
        json=account
    )

    return response.json()

    response = requests.post(
        url,
        params=params,
        json=customer
    )

    return response.json()

@router.post("/nessie/create-test-merchant")
def create_test_merchant():

    url = "https://api.nessieisreal.com/merchants"

    params = {
        "key": NESSIE_API_KEY
    }

    merchant = {
        "name": "Starbucks",
        "category": "Food",
        "address": {
            "street_number": "123",
            "street_name": "Main St",
            "city": "Houston",
            "state": "TX",
            "zip": "77002"
        },
        "geocode": {
            "lat": 29.7604,
            "lng": -95.3698
        }
    }

    response = requests.post(
        url,
        params=params,
        json=merchant
    )

    return response.json()

# --------------------------------------------------
# MOCK TRANSACTION DATA
# We will replace this with Nessie later
# --------------------------------------------------

transactions = [
    {"merchant": "Starbucks", "amount": 7.50, "category": "Food"},
    {"merchant": "H-E-B", "amount": 52.30, "category": "Groceries"},
    {"merchant": "Chipotle", "amount": 12.45, "category": "Food"},
    {"merchant": "Shell", "amount": 35.00, "category": "Transportation"},
    {"merchant": "Target", "amount": 41.25, "category": "Shopping"}
]

student_discounts = [
    {
        "merchant": "Apple",
        "discount": "Education pricing available",
        "verification": "Student eligibility required",
        "category": "Technology",
        "type": "online",
        "url": "https://www.apple.com/us-edu/store"
    },
    {
        "merchant": "Spotify",
        "discount": "Student plan available",
        "verification": "Student verification required",
        "category": "Entertainment",
        "type": "online",
        "url": "https://www.spotify.com/us/student/"
    },
    {
        "merchant": "Amazon",
        "discount": "Student membership pricing available",
        "verification": "Student eligibility required",
        "category": "Shopping",
        "type": "online",
        "url": "https://www.amazon.com/amazonprime"
    },
    {
        "merchant": "YouTube",
        "discount": "Student plan available",
        "verification": "Student verification required",
        "category": "Entertainment",
        "type": "online",
        "url": "https://www.youtube.com/premium/student/inapp"
    },
    {
        "merchant": "Adobe",
        "discount": "Student pricing available",
        "verification": "Student eligibility required",
        "category": "Technology",
        "type": "online",
        "url": "https://www.adobe.com/creativecloud/buy/students.html"
    },
    {
        "merchant": "Nike",
        "discount": "10% student discount",
        "verification": "Student verification required",
        "category": "Shopping",
        "type": "online",
        "url": "https://www.nike.com/help/a/student-discount"
    },
    {
        "merchant": "Levi's",
        "discount": "10% student discount",
        "verification": "Student verification required",
        "category": "Shopping",
        "type": "online",
        "url": "https://www.levi.com/US/en_US/cms/student"
    },
    {
        "merchant": "AMC",
        "discount": "Student ticket pricing available",
        "verification": "Valid student ID may be required",
        "category": "Entertainment",
        "type": "in_person",
        "url": "https://www.amctheatres.com/offers"
    }
]


# --------------------------------------------------
# HOME
# --------------------------------------------------

@router.get("/")
def home():

    return {
        "message": "Student Budget API is running!"
    }


# --------------------------------------------------
# TRANSACTIONS
# --------------------------------------------------

@router.get("/transactions")
def get_transactions():

    return transactions


# --------------------------------------------------
# OVERALL BUDGET
# --------------------------------------------------

@router.get("/budget")
def get_budget():

    monthly_budget = 1000

    amount_spent = 0

    for transaction in transactions:
        amount_spent += transaction["amount"]

    remaining = monthly_budget - amount_spent

    return {
        "monthly_budget": monthly_budget,
        "amount_spent": amount_spent,
        "remaining": remaining
    }


# --------------------------------------------------
# SPENDING BY CATEGORY
# --------------------------------------------------

@router.get("/spending-by-category")
def spending_by_category():

    category_totals = {}

    for transaction in transactions:

        category = transaction["category"]
        amount = transaction["amount"]

        if category in category_totals:
            category_totals[category] += amount

        else:
            category_totals[category] = amount

    return category_totals


# --------------------------------------------------
# CATEGORY BUDGETS
# --------------------------------------------------

@router.get("/category-budgets")
def category_budgets():

    budgets = {
        "Food": 100,
        "Groceries": 200,
        "Transportation": 150,
        "Entertainment": 100
    }

    category_totals = {}

    # Calculate how much was spent in each category
    for transaction in transactions:

        category = transaction["category"]
        amount = transaction["amount"]

        if category in category_totals:
            category_totals[category] += amount

        else:
            category_totals[category] = amount


    results = {}


    # Compare spending to each category budget
    for category in budgets:

        budget_amount = budgets[category]

        spent = category_totals.get(category, 0)

        remaining = budget_amount - spent

        percent_used = (spent / budget_amount) * 100


        # Determine budget status
        if spent > budget_amount:

            status = "Over budget"

        elif percent_used >= 80:

            status = "Near limit"

        else:

            status = "On track"


        results[category] = {
            "budget": budget_amount,
            "spent": spent,
            "remaining": remaining,
            "status": status
        }


    return results


# --------------------------------------------------
# FINANCIAL AID TEXT PARSER
# --------------------------------------------------

def extract_financial_aid_info(text):

    data = {
        "student_aid_index": None,
        "pell_grant": None,
        "grants_and_scholarships": None,
        "loans_offered": None,
        "cost_of_attendance": None,
        "remaining_cost": None
    }


    # Patterns tell Python what information
    # to search for inside the PDF
    patterns = {

        "student_aid_index":
            r"Student Aid Index \(SAI\)\s*:?\s*(-?[\d,]+)",

        "pell_grant":
            r"Federal Pell Grant\s*:?\s*\$?([\d,]+)",

        "grants_and_scholarships":
            r"Total Grants and Scholarships\s*:?\s*\$?([\d,]+)",

        "loans_offered":
            r"Total Loans Offered\s*:?\s*\$?([\d,]+)",

        "cost_of_attendance":
            r"Cost of Attendance\s*:?\s*\$?([\d,]+)",

        "remaining_cost":
            r"Estimated Remaining Cost\s*:?\s*\$?([\d,]+)"
    }


    # Search the PDF text for each value
    for key, pattern in patterns.items():

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            value = match.group(1)

            # Example:
            # 4,500 becomes 4500
            value = value.replace(",", "")

            # Convert text into a real number
            data[key] = int(value)


    return data


# --------------------------------------------------
# FINANCIAL AID PDF UPLOAD
# --------------------------------------------------

# --------------------------------------------------
# FINANCIAL AID PDF UPLOAD
# --------------------------------------------------

@router.post("/upload-financial-aid")
async def upload_financial_aid(
    file: UploadFile = File(...)
):

    global latest_financial_aid

    # Only allow PDF files
    if file.content_type != "application/pdf":
        return {
            "error": "Only PDF files are allowed."
        }

    # Read uploaded PDF
    file_bytes = await file.read()

    # Open PDF
    pdf_reader = PdfReader(
        io.BytesIO(file_bytes)
    )

    # Extract text from every page
    extracted_text = ""

    for page in pdf_reader.pages:
        extracted_text += page.extract_text() or ""

    # Send extracted text to our existing parser
    financial_aid_data = extract_financial_aid_info(
        extracted_text
    )

    # Save latest result so Dashboard can access it
    latest_financial_aid = financial_aid_data

    return {
        "filename": file.filename,
        "message": "Financial aid document uploaded successfully!",
        "financial_aid_data": financial_aid_data
    }

@router.get("/test-google-key")
def test_google_key():

    if GOOGLE_MAPS_API_KEY:
        return {"message": "Google Maps API key loaded successfully!"}

    return {"message": "Google Maps API key was not found."}

@router.get("/cheap-food")
def get_cheap_food(latitude: float, longitude: float):

    # -----------------------------
    # 1. Calculate food spending
    # -----------------------------

    food_budget = 100

    food_spent = 0

    for transaction in transactions:

        if transaction["category"] == "Food":
            food_spent += transaction["amount"]

    food_remaining = food_budget - food_spent


    # -----------------------------
    # 2. Call Google Places
    # -----------------------------

    url = "https://places.googleapis.com/v1/places:searchNearby"

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_MAPS_API_KEY,
        "X-Goog-FieldMask":
            "places.displayName,"
            "places.formattedAddress,"
            "places.rating,"
            "places.priceLevel,"
            "places.googleMapsUri"
    }

    body = {
        "includedTypes": ["restaurant"],
        "maxResultCount": 20,

        "locationRestriction": {
            "circle": {
                "center": {
                    "latitude": latitude,
                    "longitude": longitude
                },
                "radius": 3000
            }
        }
    }

    response = requests.post(
        url,
        headers=headers,
        json=body
    )

    data = response.json()


    # -----------------------------
    # 3. Keep affordable places
    # -----------------------------

    cheap_places = []

    for place in data.get("places", []):

        price_level = place.get(
            "priceLevel",
            "PRICE_LEVEL_UNKNOWN"
        )

        if price_level in [
            "PRICE_LEVEL_FREE",
            "PRICE_LEVEL_INEXPENSIVE"
        ]:

            if price_level == "PRICE_LEVEL_FREE":
                price = "Free"

            else:
                price = "$"


            cheap_places.append({
                "name": place.get(
                    "displayName",
                    {}
                ).get("text", "Unknown"),

                "address": place.get(
                    "formattedAddress",
                    "Address unavailable"
                ),

                "rating": place.get(
                    "rating",
                    "No rating"
                ),

                "price": price,

                "google_maps_link": place.get(
                    "googleMapsUri"
                )
            })


    # -----------------------------
    # 4. Return budget + restaurants
    # -----------------------------

    return {
        "food_budget": {
            "budget": food_budget,
            "spent": food_spent,
            "remaining": food_remaining
        },

        "recommendation":
            f"You have ${food_remaining:.2f} left in your food budget.",

        "nearby_places": cheap_places
    }

@router.get("/test-persona")
def test_persona():
    return {
        "api_key_loaded": PERSONA_API_KEY is not None,
        "template_id_loaded": PERSONA_TEMPLATE_ID is not None
    }

@router.post("/persona/create-inquiry")
def create_persona_inquiry():

    url = "https://api.withpersona.com/api/v1/inquiries"

    headers = {
        "Authorization": f"Bearer {PERSONA_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Persona-Version": "2023-01-05"
    }

    body = {
        "data": {
            "attributes": {
                "inquiry-template-id": PERSONA_TEMPLATE_ID
            }
        }
    }

    response = requests.post(url, headers=headers, json=body)

    data = response.json()

    if "data" not in data:
        return {
            "success": False,
            "error": data
        }

    return {
        "success": True,
        "inquiry_id": data["data"]["id"],
        "status": data["data"]["attributes"]["status"]
    }

@router.get("/persona/check-status/{inquiry_id}")
def check_persona_status(inquiry_id: str):

    url = f"https://api.withpersona.com/api/v1/inquiries/{inquiry_id}"

    headers = {
        "Authorization": f"Bearer {PERSONA_API_KEY}",
        "Accept": "application/json",
        "Persona-Version": "2023-01-05"
    }

    response = requests.get(url, headers=headers)

    data = response.json()

    if "data" not in data:
        return {
            "success": False,
            "error": data
        }

    status = data["data"]["attributes"]["status"]

    return {
        "success": True,
        "inquiry_id": inquiry_id,
        "status": status,
        "verified": status == "completed"
    }

@router.get("/student-discounts")
def get_student_discounts():
    return {
        "count": len(student_discounts),
        "discounts": student_discounts
    }

@router.get("/nearby-student-discounts")
def nearby_student_discounts(latitude: float, longitude: float):

    url = "https://places.googleapis.com/v1/places:searchText"

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_MAPS_API_KEY,
        "X-Goog-FieldMask":
            "places.displayName,"
            "places.formattedAddress,"
            "places.rating,"
            "places.googleMapsUri"
    }

    matches = []

    for discount in student_discounts:

        # Only search Google Maps for physical locations
        if discount["type"] != "in_person":
            continue

        body = {
            "textQuery": discount["merchant"],

            "pageSize": 1,

            "locationBias": {
                "circle": {
                    "center": {
                        "latitude": latitude,
                        "longitude": longitude
                    },
                    "radius": 10000
                }
            }
        }

        response = requests.post(
            url,
            headers=headers,
            json=body
        )

        data = response.json()

        for place in data.get("places", []):

            matches.append({
                "name": place.get(
                    "displayName", {}
                ).get(
                    "text",
                    discount["merchant"]
                ),

                "address": place.get(
                    "formattedAddress",
                    "Address unavailable"
                ),

                "rating": place.get(
                    "rating",
                    "No rating"
                ),

                "student_discount":
                    discount["discount"],

                "verification":
                    discount["verification"],

                "category":
                    discount["category"],

                "google_maps_link":
                    place.get("googleMapsUri")
            })

    return {
        "count": len(matches),
        "nearby_student_discounts": matches
    }

@router.get("/dashboard")
def get_dashboard():

    monthly_budget = 1000

    total_spent = 0
    category_spending = {}

    for transaction in transactions:

        total_spent += transaction["amount"]

        category = transaction["category"]

        if category not in category_spending:
            category_spending[category] = 0

        category_spending[category] += transaction["amount"]

    remaining = monthly_budget - total_spent

    # Simple financial health message
    percent_used = (total_spent / monthly_budget) * 100

    if percent_used >= 90:
        message = "You're getting close to your monthly limit."

    elif percent_used >= 70:
        message = "Keep an eye on your spending."

    else:
        message = "You're playing your cards right!"

    return {
        "monthly_budget": monthly_budget,
        "total_spent": round(total_spent, 2),
        "remaining": round(remaining, 2),
        "percent_used": round(percent_used, 1),
        "category_spending": category_spending,
        "message": message
    }

@router.get("/recommendations")
def get_recommendations(latitude: float, longitude: float):

    # -------------------------
    # CATEGORY BUDGETS
    # -------------------------

    category_budgets = {
        "Food": 100,
        "Groceries": 200,
        "Transportation": 150,
        "Shopping": 100
    }

    category_spending = {}

    # Calculate how much was spent in each category
    for transaction in transactions:

        category = transaction["category"]
        amount = transaction["amount"]

        if category not in category_spending:
            category_spending[category] = 0

        category_spending[category] += amount


    # -------------------------
    # BUDGET RECOMMENDATIONS
    # -------------------------

    recommendations = []

    for category, budget in category_budgets.items():

        spent = category_spending.get(category, 0)

        percent_used = (spent / budget) * 100

        if percent_used >= 100:

            recommendations.append({
                "category": category,
                "priority": "high",
                "message": f"You've gone over your {category} budget."
            })

        elif percent_used >= 80:

            recommendations.append({
                "category": category,
                "priority": "medium",
                "message": f"You're getting close to your {category} limit."
            })


    # -------------------------
    # CHEAP FOOD
    # -------------------------

    cheap_food = []

    food_spent = category_spending.get("Food", 0)
    food_budget = category_budgets["Food"]

    # Only search for cheap food if 80% or more
    # of the food budget has been used
    if True:

        url = "https://places.googleapis.com/v1/places:searchNearby"

        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": GOOGLE_MAPS_API_KEY,
            "X-Goog-FieldMask":
                "places.displayName,"
                "places.formattedAddress,"
                "places.rating,"
                "places.priceLevel,"
                "places.googleMapsUri"
        }

        body = {
            "includedTypes": ["restaurant"],
            "maxResultCount": 20,
            "locationRestriction": {
                "circle": {
                    "center": {
                        "latitude": latitude,
                        "longitude": longitude
                    },
                    "radius": 3000
                }
            }
        }

        response = requests.post(
            url,
            headers=headers,
            json=body
        )

        data = response.json()

        for place in data.get("places", []):

            price_level = place.get(
                "priceLevel",
                "PRICE_LEVEL_UNKNOWN"
            )

            # Keep inexpensive or moderately priced restaurants
            if price_level in [
                "PRICE_LEVEL_FREE",
                "PRICE_LEVEL_INEXPENSIVE",
                "PRICE_LEVEL_MODERATE"
            ]:

                cheap_food.append({
                    "name": place.get(
                        "displayName", {}
                    ).get(
                        "text",
                        "Unknown"
                    ),

                    "address": place.get(
                        "formattedAddress",
                        "Address unavailable"
                    ),

                    "rating": place.get(
                        "rating",
                        "No rating"
                    ),

                    "price_level": price_level,

                    "google_maps_link":
                        place.get("googleMapsUri")
                })


    # -------------------------
    # STUDENT DISCOUNTS
    # -------------------------

    student_deals = []

    shopping_spent = category_spending.get("Shopping", 0)
    shopping_budget = category_budgets["Shopping"]

    # Only search for student deals if 80% or more
    # of the shopping budget has been used
    if shopping_spent >= shopping_budget * 0.80:

        url = "https://places.googleapis.com/v1/places:searchText"

        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": GOOGLE_MAPS_API_KEY,
            "X-Goog-FieldMask":
                "places.displayName,"
                "places.formattedAddress,"
                "places.rating,"
                "places.googleMapsUri"
        }

        # Go through our known student discounts
        for discount in student_discounts:

            # Only search Google Maps for physical locations
            if discount["type"] != "in_person":
                continue

            body = {
                "textQuery": discount["merchant"],

                "pageSize": 1,

                "locationBias": {
                    "circle": {
                        "center": {
                            "latitude": latitude,
                            "longitude": longitude
                        },
                        "radius": 10000
                    }
                }
            }

            response = requests.post(
                url,
                headers=headers,
                json=body
            )

            data = response.json()

            for place in data.get("places", []):

                student_deals.append({
                    "name": place.get(
                        "displayName", {}
                    ).get(
                        "text",
                        discount["merchant"]
                    ),

                    "address": place.get(
                        "formattedAddress",
                        "Address unavailable"
                    ),

                    "rating": place.get(
                        "rating",
                        "No rating"
                    ),

                    "student_discount":
                        discount["discount"],

                    "verification":
                        discount["verification"],

                    "category":
                        discount["category"],

                    "google_maps_link":
                        place.get("googleMapsUri")
                })


    # -------------------------
    # IF EVERYTHING IS OK
    # -------------------------

    if len(recommendations) == 0:

        recommendations.append({
            "category": "Overall",
            "priority": "low",
            "message": "You're playing your cards right!"
        })


    # -------------------------
    # SEND EVERYTHING TO FRONTEND
    # -------------------------

    return {
        "recommendations": recommendations,
        "cheap_food_options": cheap_food,
        "student_discount_options": student_deals
    }

@router.get("/test-supabase")
def test_supabase():
    return {
        "supabase_url_loaded": bool(SUPABASE_URL),
        "supabase_key_loaded": bool(SUPABASE_PUBLISHABLE_KEY)
    }

@router.get("/supabase-budget")
def get_supabase_budget():
    response = (
        supabase
        .table("budgets")
        .select("*")
        .limit(1)
        .execute()
    )

    return response.data

# ----------------------------------
# LATEST FINANCIAL AID SUMMARY
# ----------------------------------

@router.get("/financial-aid-summary")
def financial_aid_summary():

    return latest_financial_aid


# ----------------------------------
# DEMO BANK CONNECTION
# ----------------------------------

@router.get("/demo-bank-account")
def demo_bank_account():

    url = "https://api.nessieisreal.com/accounts"

    params = {
        "key": NESSIE_API_KEY
    }

    response = requests.get(
        url,
        params=params
    )

    if response.status_code != 200:

        return {
            "connected": False
        }


    accounts = response.json()


    if len(accounts) == 0:

        return {
            "connected": False
        }


    account = accounts[0]


    return {
        "connected": True,
        "nickname": account.get(
            "nickname",
            "Student Checking"
        ),
        "type": account.get(
            "type",
            "Checking"
        ),
        "balance": account.get(
            "balance",
            0
        )
    }