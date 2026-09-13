import json
import uuid
import os
import tempfile
import requests

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

from config.supabase_client import supabase, supabase_admin

from src import pricing_service
AI_BASE_URL = os.getenv("AI_BASE_URL")
# from src.ai.vision_service import analyze_image
# from src.ai.voice_service import transcribe_audio
# --------------------------------------------------
# TEST API
# --------------------------------------------------

def home(request):
    return render(request, "landingpage.html")
def customer_page(request):
    return render(request, "index.html")

def artisan_page(request):
    return render(request, "artisan.html")

def artisan_login_page(request):
    return render(request, "artisan-login.html")


def artisan_register_page(request):
    return render(request, "artisan-register.html")

def artisan_dashboard_page(request):
    return render(request, "artisan-dashboard.html")


def artisan_upload_page(request):
    return render(request, "artisan-upload-camera-fixed.html")


def artisan_review_page(request):
    return render(request, "artisan-review-product.html")


def artisan_price_page(request):
    return render(request, "artisan-price-prediction.html")


def artisan_publish_page(request):
    return render(request, "artisan-publish-product.html")


def artisan_profile_page(request):
    return render(request, "artisan-profile.html")


def artisan_edit_page(request):
    return render(request, "artisan-edit-product.html")


def artisan_view_page(request):
    return render(request, "artisan-view-product.html")
# --------------------------------------------------
# SIGNUP
# --------------------------------------------------

@csrf_exempt
def signup(request):

    if request.method != "POST":

        return JsonResponse(
            {
                "error": "Only POST requests are allowed"
            },
            status=405
        )

    try:

        data = json.loads(request.body)


        email = data.get("email")
        password = data.get("password")


        if not email:

            return JsonResponse(
                {
                    "error": "Email is required"
                },
                status=400
            )


        if not password:

            return JsonResponse(
                {
                    "error": "Password is required"
                },
                status=400
            )


        if len(password) < 6:

            return JsonResponse(
                {
                    "error": (
                        "Password must contain at least "
                        "6 characters"
                    )
                },
                status=400
            )


        # Supabase signup
        response = supabase.auth.sign_up({

            "email": email,

            "password": password

        })


        user = response.user


        if not user:

            return JsonResponse(
                {
                    "error": "Unable to create user"
                },
                status=400
            )


        return JsonResponse(
            {
                "message": "Signup successful",

                "user": {
                    "id": user.id,
                    "email": user.email
                },

                "email_confirmation_required": (
                    response.session is None
                )
            },
            status=201
        )


    except json.JSONDecodeError:

        return JsonResponse(
            {
                "error": "Invalid JSON body"
            },
            status=400
        )


    except Exception as e:

        return JsonResponse(
            {
                "error": str(e)
            },
            status=400
        )


# --------------------------------------------------
# LOGIN
# --------------------------------------------------

@csrf_exempt
def login_user(request):

    if request.method != "POST":

        return JsonResponse(
            {
                "error": "Only POST requests are allowed"
            },
            status=405
        )


    try:

        data = json.loads(request.body)


        email = data.get("email")
        password = data.get("password")


        if not email or not password:

            return JsonResponse(
                {
                    "error": (
                        "Email and password are required"
                    )
                },
                status=400
            )


        # Supabase login
        response = (
            supabase.auth.sign_in_with_password(
                {
                    "email": email,
                    "password": password
                }
            )
        )


        user = response.user

        session = response.session


        if not user or not session:

            return JsonResponse(
                {
                    "error": "Login failed"
                },
                status=401
            )


        return JsonResponse(
            {
                "message": "Login successful",

                "user": {
                    "id": user.id,
                    "email": user.email
                },

                "access_token": (
                    session.access_token
                ),

                "refresh_token": (
                    session.refresh_token
                )
            },
            status=200
        )


    except json.JSONDecodeError:

        return JsonResponse(
            {
                "error": "Invalid JSON body"
            },
            status=400
        )


    except Exception as e:

        return JsonResponse(
            {
                "error": str(e)
            },
            status=401
        )


# --------------------------------------------------
# LOGOUT
# --------------------------------------------------

@csrf_exempt
def logout_user(request):

    if request.method != "POST":

        return JsonResponse(
            {
                "error": "Only POST requests are allowed"
            },
            status=405
        )


    try:

        supabase.auth.sign_out()


        return JsonResponse(
            {
                "message": "Logout successful"
            },
            status=200
        )


    except Exception as e:

        return JsonResponse(
            {
                "error": str(e)
            },
            status=400
        )
@csrf_exempt
def protected_test(request):

    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return JsonResponse(
            {"error": "Authorization header missing"},
            status=401
        )

    try:
        token_type, token = auth_header.split(" ")

        if token_type != "Bearer":
            return JsonResponse(
                {"error": "Invalid authorization type"},
                status=401
            )

        user_response = supabase.auth.get_user(token)

        user = user_response.user

        if not user:
            return JsonResponse(
                {"error": "Invalid or expired token"},
                status=401
            )

        return JsonResponse({
            "message": "Protected route accessed successfully",
            "user": {
                "id": user.id,
                "email": user.email
            }
        })

    except Exception as e:
        return JsonResponse(
            {"error": str(e)},
            status=401
        )

@csrf_exempt
def create_artisan_profile(request):

    if request.method != "POST":
        return JsonResponse(
            {"error": "Only POST requests are allowed"},
            status=405
        )

    try:
        # 1. Authorization header
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return JsonResponse(
                {"error": "Authorization header missing"},
                status=401
            )

        # 2. Bearer token nikaalo
        token_type, token = auth_header.split(" ")

        if token_type != "Bearer":
            return JsonResponse(
                {"error": "Invalid authorization type"},
                status=401
            )

        # 3. Supabase se token verify
        user_response = supabase.auth.get_user(token)
        user = user_response.user

        if not user:
            return JsonResponse(
                {"error": "Invalid or expired token"},
                status=401
            )

        # 4. Supabase request ko user's JWT do
        supabase.postgrest.auth(token)

        # 5. Check if same user is already a customer
        customer_check = (
            supabase.table("customers")
            .select("id")
            .eq("id", user.id)
            .execute()
        )

        if customer_check.data:
            return JsonResponse(
                {
                    "error": (
                        "This account is already registered "
                        "as a customer"
                    )
                },
                status=400
            )

        # 6. Check if artisan profile already exists
        artisan_check = (
            supabase.table("artisans")
            .select("id")
            .eq("id", user.id)
            .execute()
        )

        if artisan_check.data:
            return JsonResponse(
                {"error": "Artisan profile already exists"},
                status=400
            )

        # 7. Frontend JSON data
        data = json.loads(request.body)

        full_name = data.get("full_name")

        if not full_name:
            return JsonResponse(
                {"error": "full_name is required"},
                status=400
            )

        # 8. Artisan data
        artisan_data = {
            "id": user.id,
            "full_name": full_name,
            "email": user.email,
            "phone": data.get("phone"),
            "state": data.get("state"),
            "district": data.get("district"),
            "village": data.get("village"),
            "craft_type": data.get("craft_type"),
            "experience_years": data.get("experience_years", 0),
            "bio": data.get("bio"),
            "role": "artisan"
        }

        # 9. Insert into artisans table
        response = (
            supabase.table("artisans")
            .insert(artisan_data)
            .execute()
        )

        return JsonResponse({
            "message": "Artisan profile created successfully",
            "artisan": response.data
        }, status=201)

    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON body"},
            status=400
        )

    except ValueError:
        return JsonResponse(
            {"error": "Invalid Authorization header"},
            status=401
        )

    except Exception as e:
        print("ARTISAN PROFILE ERROR:", repr(e))

        return JsonResponse(
            {"error": str(e)},
            status=400
        )

@csrf_exempt
def get_artisan_profile(request):

    if request.method != "GET":
        return JsonResponse(
            {"error": "Only GET requests are allowed"},
            status=405
        )

    try:
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return JsonResponse(
                {"error": "Authorization header missing"},
                status=401
            )

        token_type, token = auth_header.split(" ")

        if token_type != "Bearer":
            return JsonResponse(
                {"error": "Invalid authorization type"},
                status=401
            )

        user_response = supabase.auth.get_user(token)
        user = user_response.user

        if not user:
            return JsonResponse(
                {"error": "Invalid or expired token"},
                status=401
            )

        supabase.postgrest.auth(token)

        response = (
            supabase.table("artisans")
            .select("*")
            .eq("id", user.id)
            .execute()
        )

        if not response.data:
            return JsonResponse(
                {"error": "Artisan profile not found"},
                status=404
            )

        return JsonResponse({
            "message": "Artisan profile fetched successfully",
            "artisan": response.data[0]
        })

    except Exception as e:
        print("GET ARTISAN PROFILE ERROR:", repr(e))

        return JsonResponse(
            {"error": str(e)},
            status=400
        )

@csrf_exempt
def update_artisan_profile(request):

    if request.method not in ["PUT", "PATCH"]:
        return JsonResponse(
            {"error": "Only PUT or PATCH requests are allowed"},
            status=405
        )

    try:
        # 1. Authorization header
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return JsonResponse(
                {"error": "Authorization header missing"},
                status=401
            )

        token_type, token = auth_header.split(" ")

        if token_type != "Bearer":
            return JsonResponse(
                {"error": "Invalid authorization type"},
                status=401
            )

        # 2. Verify user
        user_response = supabase.auth.get_user(token)
        user = user_response.user

        if not user:
            return JsonResponse(
                {"error": "Invalid or expired token"},
                status=401
            )

        # 3. Read frontend data
        data = json.loads(request.body)

        # Only allow these fields to be updated
        allowed_fields = [
            "full_name",
            "phone",
            "state",
            "district",
            "village",
            "craft_type",
            "experience_years",
            "bio",
            "profile_image_url",
            "verification_document_url"
        ]

        update_data = {}

        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]

        if not update_data:
            return JsonResponse(
                {"error": "No valid fields provided for update"},
                status=400
            )

        # Important: user must NOT manually set verification
        # is_verified is intentionally not allowed above

        supabase.postgrest.auth(token)

        response = (
            supabase.table("artisans")
            .update(update_data)
            .eq("id", user.id)
            .execute()
        )

        if not response.data:
            return JsonResponse(
                {"error": "Artisan profile not found"},
                status=404
            )

        return JsonResponse({
            "message": "Artisan profile updated successfully",
            "artisan": response.data[0]
        })

    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON body"},
            status=400
        )

    except ValueError:
        return JsonResponse(
            {"error": "Invalid Authorization header"},
            status=401
        )

    except Exception as e:
        print("UPDATE ARTISAN PROFILE ERROR:", repr(e))

        return JsonResponse(
            {"error": str(e)},
            status=400
        )

@csrf_exempt
def create_customer_profile(request):

    if request.method != "POST":
        return JsonResponse(
            {"error": "Only POST requests are allowed"},
            status=405
        )

    try:
        # 1. Authorization header
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return JsonResponse(
                {"error": "Authorization header missing"},
                status=401
            )

        # 2. Bearer token
        token_type, token = auth_header.split(" ")

        if token_type != "Bearer":
            return JsonResponse(
                {"error": "Invalid authorization type"},
                status=401
            )

        # 3. Verify token
        user_response = supabase.auth.get_user(token)
        user = user_response.user

        if not user:
            return JsonResponse(
                {"error": "Invalid or expired token"},
                status=401
            )

        # 4. Give JWT to Supabase PostgREST
        supabase.postgrest.auth(token)

        # 5. Check if same user is already an artisan
        artisan_check = (
            supabase.table("artisans")
            .select("id")
            .eq("id", user.id)
            .execute()
        )

        if artisan_check.data:
            return JsonResponse(
                {
                    "error": (
                        "This account is already registered "
                        "as an artisan"
                    )
                },
                status=400
            )

        # 6. Check if customer profile already exists
        customer_check = (
            supabase.table("customers")
            .select("id")
            .eq("id", user.id)
            .execute()
        )

        if customer_check.data:
            return JsonResponse(
                {"error": "Customer profile already exists"},
                status=400
            )

        # 7. Read request data
        data = json.loads(request.body)

        full_name = data.get("full_name")

        if not full_name:
            return JsonResponse(
                {"error": "full_name is required"},
                status=400
            )

        # 8. Customer data
        customer_data = {
            "id": user.id,
            "full_name": full_name,
            "email": user.email,
            "phone": data.get("phone"),
            "address": data.get("address"),
            "city": data.get("city"),
            "state": data.get("state"),
            "pincode": data.get("pincode"),
            "role": "customer"
        }

        # 9. Insert customer profile
        response = (
            supabase.table("customers")
            .insert(customer_data)
            .execute()
        )

        return JsonResponse({
            "message": "Customer profile created successfully",
            "customer": response.data
        }, status=201)

    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON body"},
            status=400
        )

    except ValueError:
        return JsonResponse(
            {"error": "Invalid Authorization header"},
            status=401
        )

    except Exception as e:
        print("CUSTOMER PROFILE ERROR:", repr(e))

        return JsonResponse(
            {"error": str(e)},
            status=400
        )

@csrf_exempt
def get_customer_profile(request):

    if request.method != "GET":
        return JsonResponse(
            {"error": "Only GET requests are allowed"},
            status=405
        )

    try:
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return JsonResponse(
                {"error": "Authorization header missing"},
                status=401
            )

        token_type, token = auth_header.split(" ")

        if token_type != "Bearer":
            return JsonResponse(
                {"error": "Invalid authorization type"},
                status=401
            )

        user_response = supabase.auth.get_user(token)
        user = user_response.user

        if not user:
            return JsonResponse(
                {"error": "Invalid or expired token"},
                status=401
            )

        supabase.postgrest.auth(token)

        response = (
            supabase.table("customers")
            .select("*")
            .eq("id", user.id)
            .execute()
        )

        if not response.data:
            return JsonResponse(
                {"error": "Customer profile not found"},
                status=404
            )

        return JsonResponse({
            "message": "Customer profile fetched successfully",
            "customer": response.data[0]
        })

    except Exception as e:
        print("GET CUSTOMER PROFILE ERROR:", repr(e))

        return JsonResponse(
            {"error": str(e)},
            status=400
        )
    
@csrf_exempt
def update_customer_profile(request):

    if request.method not in ["PUT", "PATCH"]:
        return JsonResponse(
            {"error": "Only PUT or PATCH requests are allowed"},
            status=405
        )

    try:
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return JsonResponse(
                {"error": "Authorization header missing"},
                status=401
            )

        token_type, token = auth_header.split(" ")

        if token_type != "Bearer":
            return JsonResponse(
                {"error": "Invalid authorization type"},
                status=401
            )

        user_response = supabase.auth.get_user(token)
        user = user_response.user

        if not user:
            return JsonResponse(
                {"error": "Invalid or expired token"},
                status=401
            )

        data = json.loads(request.body)

        allowed_fields = [
            "full_name",
            "phone",
            "address",
            "city",
            "state",
            "pincode",
            "profile_image_url"
        ]

        update_data = {}

        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]

        if not update_data:
            return JsonResponse(
                {"error": "No valid fields provided for update"},
                status=400
            )

        supabase.postgrest.auth(token)

        response = (
            supabase.table("customers")
            .update(update_data)
            .eq("id", user.id)
            .execute()
        )

        if not response.data:
            return JsonResponse(
                {"error": "Customer profile not found"},
                status=404
            )

        return JsonResponse({
            "message": "Customer profile updated successfully",
            "customer": response.data[0]
        })

    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON body"},
            status=400
        )

    except ValueError:
        return JsonResponse(
            {"error": "Invalid Authorization header"},
            status=401
        )

    except Exception as e:
        print("UPDATE CUSTOMER PROFILE ERROR:", repr(e))

        return JsonResponse(
            {"error": str(e)},
            status=400
        )


@csrf_exempt
def create_product(request):

    if request.method != "POST":
        return JsonResponse(
            {"error": "Only POST requests are allowed"},
            status=405
        )

    try:
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return JsonResponse(
                {"error": "Authorization header missing"},
                status=401
            )

        token_type, token = auth_header.split(" ")

        if token_type != "Bearer":
            return JsonResponse(
                {"error": "Invalid authorization type"},
                status=401
            )

        user_response = supabase.auth.get_user(token)
        user = user_response.user

        if not user:
            return JsonResponse(
                {"error": "Invalid or expired token"},
                status=401
            )

        data = json.loads(request.body)

        name = data.get("name")
        price = data.get("price")

        if not name:
            return JsonResponse(
                {"error": "Product name is required"},
                status=400
            )

        if price is None:
            return JsonResponse(
                {"error": "Product price is required"},
                status=400
            )

        product_data = {
            "artisan_id": user.id,

            "name": name,
            "description": data.get("description"),

            "category": data.get("category"),
            "subcategory": data.get("subcategory"),

            "craft": data.get("craft"),
            "material": data.get("material"),
            "technique": data.get("technique"),

            "state": data.get("state"),
            "district": data.get("district"),

            "price": price,
            "original_price": data.get("original_price"),
            "discount_percent": data.get("discount_percent"),

            "ai_suggested_price": data.get("ai_suggested_price"),
            "direct_artisan_earning": data.get("direct_artisan_earning"),

            "stock": data.get("stock", 1),

            "image_url": data.get("image_url"),

            "status": data.get("status", "draft"),

            "voice_language": data.get("voice_language"),
            "voice_transcript": data.get("voice_transcript"),

            "room_compatibility": data.get("room_compatibility"),

            "gi_tag": data.get("gi_tag"),
            "artisan_story": data.get("artisan_story"),

            "is_available": data.get("is_available", True)
        }

        supabase.postgrest.auth(token)

        response = (
            supabase.table("products")
            .insert(product_data)
            .execute()
        )

        return JsonResponse({
            "message": "Product created successfully",
            "product": response.data[0]
        }, status=201)

    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON body"},
            status=400
        )

    except ValueError:
        return JsonResponse(
            {"error": "Invalid Authorization header"},
            status=401
        )

    except Exception as e:
        print("CREATE PRODUCT ERROR:", repr(e))

        return JsonResponse(
            {"error": str(e)},
            status=400
        )

@csrf_exempt
def get_my_products(request):

    if request.method != "GET":
        return JsonResponse(
            {"error": "Only GET requests are allowed"},
            status=405
        )

    try:
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return JsonResponse(
                {"error": "Authorization header missing"},
                status=401
            )

        token_type, token = auth_header.split(" ")

        if token_type != "Bearer":
            return JsonResponse(
                {"error": "Invalid authorization type"},
                status=401
            )

        user_response = supabase.auth.get_user(token)
        user = user_response.user

        if not user:
            return JsonResponse(
                {"error": "Invalid or expired token"},
                status=401
            )

        supabase.postgrest.auth(token)

        response = (
            supabase.table("products")
            .select("*")
            .eq("artisan_id", user.id)
            .order("created_at", desc=True)
            .execute()
        )

        return JsonResponse({
            "message": "Products fetched successfully",
            "count": len(response.data),
            "products": response.data
        })

    except Exception as e:
        print("GET MY PRODUCTS ERROR:", repr(e))

        return JsonResponse(
            {"error": str(e)},
            status=400
        )

@csrf_exempt
def get_product(request, product_id):

    if request.method != "GET":
        return JsonResponse(
            {"error": "Only GET requests are allowed"},
            status=405
        )

    try:
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return JsonResponse(
                {"error": "Authorization header missing"},
                status=401
            )

        token_type, token = auth_header.split(" ")

        if token_type != "Bearer":
            return JsonResponse(
                {"error": "Invalid authorization type"},
                status=401
            )

        user_response = supabase.auth.get_user(token)
        user = user_response.user

        if not user:
            return JsonResponse(
                {"error": "Invalid or expired token"},
                status=401
            )

        supabase.postgrest.auth(token)

        response = (
            supabase.table("products")
            .select("*")
            .eq("id", product_id)
            .eq("artisan_id", user.id)
            .execute()
        )

        if not response.data:
            return JsonResponse(
                {"error": "Product not found"},
                status=404
            )

        return JsonResponse({
            "message": "Product fetched successfully",
            "product": response.data[0]
        })

    except Exception as e:
        print("GET PRODUCT ERROR:", repr(e))

        return JsonResponse(
            {"error": str(e)},
            status=400
        )
    
@csrf_exempt
def update_product(request, product_id):

    if request.method not in ["PUT", "PATCH"]:
        return JsonResponse(
            {"error": "Only PUT or PATCH requests are allowed"},
            status=405
        )

    try:
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return JsonResponse(
                {"error": "Authorization header missing"},
                status=401
            )

        token_type, token = auth_header.split(" ")

        if token_type != "Bearer":
            return JsonResponse(
                {"error": "Invalid authorization type"},
                status=401
            )

        user_response = supabase.auth.get_user(token)
        user = user_response.user

        if not user:
            return JsonResponse(
                {"error": "Invalid or expired token"},
                status=401
            )

        data = json.loads(request.body)

        allowed_fields = [
            "name",
            "description",
            "category",
            "subcategory",
            "craft",
            "material",
            "technique",
            "state",
            "district",
            "price",
            "original_price",
            "discount_percent",
            "ai_suggested_price",
            "direct_artisan_earning",
            "stock",
            "image_url",
            "status",
            "voice_language",
            "voice_transcript",
            "room_compatibility",
            "gi_tag",
            "artisan_story",
            "is_available"
        ]

        update_data = {}

        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]

        if not update_data:
            return JsonResponse(
                {"error": "No valid fields provided"},
                status=400
            )

        supabase.postgrest.auth(token)

        response = (
            supabase.table("products")
            .update(update_data)
            .eq("id", str(product_id))
            .eq("artisan_id", user.id)
            .execute()
        )

        if not response.data:
            return JsonResponse(
                {"error": "Product not found or not owned by you"},
                status=404
            )

        return JsonResponse({
            "message": "Product updated successfully",
            "product": response.data[0]
        })

    except Exception as e:
        print("UPDATE PRODUCT ERROR:", repr(e))

        return JsonResponse(
            {"error": str(e)},
            status=400
        )

@csrf_exempt
def delete_product(request, product_id):

    if request.method != "DELETE":
        return JsonResponse(
            {"error": "Only DELETE requests are allowed"},
            status=405
        )

    try:
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return JsonResponse(
                {"error": "Authorization header missing"},
                status=401
            )

        token_type, token = auth_header.split(" ")

        if token_type != "Bearer":
            return JsonResponse(
                {"error": "Invalid authorization type"},
                status=401
            )

        user_response = supabase.auth.get_user(token)
        user = user_response.user

        supabase.postgrest.auth(token)

        response = (
            supabase.table("products")
            .delete()
            .eq("id", str(product_id))
            .eq("artisan_id", user.id)
            .execute()
        )

        if not response.data:
            return JsonResponse(
                {"error": "Product not found or not owned by you"},
                status=404
            )

        return JsonResponse({
            "message": "Product deleted successfully"
        })

    except Exception as e:
        print("DELETE PRODUCT ERROR:", repr(e))

        return JsonResponse(
            {"error": str(e)},
            status=400
        )

@csrf_exempt
def publish_product(request, product_id):

    if request.method != "PATCH":
        return JsonResponse(
            {"error": "Only PATCH requests are allowed"},
            status=405
        )

    try:
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return JsonResponse(
                {"error": "Authorization header missing"},
                status=401
            )

        token_type, token = auth_header.split(" ")

        if token_type != "Bearer":
            return JsonResponse(
                {"error": "Invalid authorization type"},
                status=401
            )

        user_response = supabase.auth.get_user(token)
        user = user_response.user

        supabase.postgrest.auth(token)

        current = (
            supabase.table("products")
            .select("*")
            .eq("id", str(product_id))
            .eq("artisan_id", user.id)
            .execute()
        )

        if not current.data:
            return JsonResponse(
                {"error": "Product not found"},
                status=404
            )

        product = current.data[0]

        required_fields = [
            "name",
            "craft",
            "material",
            "technique",
            "description",
            "price",
            "image_url"
        ]

        missing = []

        for field in required_fields:
            if not product.get(field):
                missing.append(field)

        if missing:
            return JsonResponse({
                "error": "Product is incomplete",
                "missing_fields": missing
            }, status=400)

        response = (
            supabase.table("products")
            .update({
                "status": "published",
                "is_available": True
            })
            .eq("id", str(product_id))
            .eq("artisan_id", user.id)
            .execute()
        )

        return JsonResponse({
            "message": "Product published successfully",
            "product": response.data[0]
        })

    except Exception as e:
        print("PUBLISH PRODUCT ERROR:", repr(e))

        return JsonResponse(
            {"error": str(e)},
            status=400
        )

@csrf_exempt
def upload_product_image(request, product_id):

    if request.method != "POST":
        return JsonResponse(
            {"error": "Only POST requests are allowed"},
            status=405
        )

    try:
        # ----------------------------
        # 1. CHECK AUTH TOKEN
        # ----------------------------
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return JsonResponse(
                {"error": "Authorization header missing"},
                status=401
            )

        token_type, token = auth_header.split(" ")

        if token_type != "Bearer":
            return JsonResponse(
                {"error": "Invalid authorization type"},
                status=401
            )

        # ----------------------------
        # 2. VERIFY USER
        # ----------------------------
        user_response = supabase.auth.get_user(token)
        user = user_response.user

        if not user:
            return JsonResponse(
                {"error": "Invalid or expired token"},
                status=401
            )

        supabase.postgrest.auth(token)

        # ----------------------------
        # 3. CHECK PRODUCT OWNERSHIP
        # ----------------------------
        product_response = (
            supabase.table("products")
            .select("id, artisan_id")
            .eq("id", str(product_id))
            .eq("artisan_id", user.id)
            .execute()
        )

        if not product_response.data:
            return JsonResponse(
                {"error": "Product not found or not owned by you"},
                status=404
            )

        # ----------------------------
        # 4. GET IMAGE
        # ----------------------------
        image = request.FILES.get("image")

        if not image:
            return JsonResponse(
                {"error": "Image file is required"},
                status=400
            )

        # ----------------------------
        # 5. VALIDATE IMAGE TYPE
        # ----------------------------
        allowed_types = [
            "image/jpeg",
            "image/png",
            "image/webp"
        ]

        if image.content_type not in allowed_types:
            return JsonResponse(
                {
                    "error": "Invalid image type. Only JPG, PNG and WEBP are allowed."
                },
                status=400
            )

        # 5 MB limit
        if image.size > 5 * 1024 * 1024:
            return JsonResponse(
                {"error": "Image must be smaller than 5 MB"},
                status=400
            )

        # ----------------------------
        # 6. CREATE SAFE FILE NAME
        # ----------------------------
        extension = os.path.splitext(image.name)[1].lower()

        if extension not in [".jpg", ".jpeg", ".png", ".webp"]:
            return JsonResponse(
                {"error": "Invalid file extension"},
                status=400
            )

        filename = f"{uuid.uuid4()}{extension}"

        file_path = f"{user.id}/{filename}"

        # ----------------------------
        # 7. READ FILE
        # ----------------------------
        file_bytes = image.read()

        # Storage needs user JWT for RLS
        supabase.storage.from_("product-images").upload(
            path=file_path,
            file=file_bytes,
            file_options={
                "content-type": image.content_type,
                "upsert": "false"
            }
        )

        # ----------------------------
        # 8. GET PUBLIC URL
        # ----------------------------
        public_url = (
            supabase.storage
            .from_("product-images")
            .get_public_url(file_path)
        )

        # ----------------------------
        # 9. SAVE URL IN PRODUCT
        # ----------------------------
        update_response = (
            supabase.table("products")
            .update({
                "image_url": public_url
            })
            .eq("id", str(product_id))
            .eq("artisan_id", user.id)
            .execute()
        )

        return JsonResponse({
            "message": "Product image uploaded successfully",
            "image_url": public_url,
            "product": update_response.data[0]
        })

    except ValueError:
        return JsonResponse(
            {"error": "Invalid Authorization header"},
            status=401
        )

    except Exception as e:
        print("IMAGE UPLOAD ERROR:", repr(e))

        return JsonResponse(
            {"error": str(e)},
            status=400
        )

@csrf_exempt
def public_products(request):

    if request.method != "GET":
        return JsonResponse(
            {"error": "Only GET requests are allowed"},
            status=405
        )

    try:
        query = (
    supabase.table("products")
    .select("*")
)

        search = request.GET.get("search")
        category = request.GET.get("category")
        state = request.GET.get("state")
        room = request.GET.get("room")

        if search:
            query = query.or_(
                f"name.ilike.%{search}%,"
                f"description.ilike.%{search}%,"
                f"craft.ilike.%{search}%,"
                f"material.ilike.%{search}%"
            )

        if category:
            query = query.eq("category", category)

        if state:
            query = query.eq("state", state)

        if room:
            query = query.contains(
                "room_compatibility",
                [room]
            )

        response = (
            query
            .order("created_at", desc=True)
            .execute()
        )

        return JsonResponse({
            "message": "Published products fetched successfully",
            "count": len(response.data),
            "products": response.data
        })

    except Exception as e:
        print("PUBLIC PRODUCTS ERROR:", repr(e))

        return JsonResponse(
            {"error": str(e)},
            status=400
        )

@csrf_exempt
def public_product_detail(request, product_id):

    if request.method != "GET":
        return JsonResponse(
            {"error": "Only GET requests are allowed"},
            status=405
        )

    try:
        response = (
            supabase.table("products")
            .select("*")
            .eq("id", str(product_id))
            .eq("status", "published")
            .eq("is_available", True)
            .execute()
        )

        if not response.data:
            return JsonResponse(
                {"error": "Product not found"},
                status=404
            )

        return JsonResponse({
            "message": "Product fetched successfully",
            "product": response.data[0]
        })

    except Exception as e:
        print("PUBLIC PRODUCT DETAIL ERROR:", repr(e))

        return JsonResponse(
            {"error": str(e)},
            status=400
        )

@csrf_exempt
def create_order(request):

    if request.method != "POST":
        return JsonResponse(
            {"error": "Only POST requests are allowed"},
            status=405
        )

    try:
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return JsonResponse(
                {"error": "Authorization header missing"},
                status=401
            )

        token_type, token = auth_header.split(" ")

        if token_type != "Bearer":
            return JsonResponse(
                {"error": "Invalid authorization type"},
                status=401
            )

        user_response = supabase.auth.get_user(token)
        user = user_response.user

        if not user:
            return JsonResponse(
                {"error": "Invalid or expired token"},
                status=401
            )

        data = json.loads(request.body)

        items = data.get("items", [])
        shipping_address = data.get("shipping_address")

        if not items:
            return JsonResponse(
                {"error": "Order items are required"},
                status=400
            )

        if not shipping_address:
            return JsonResponse(
                {"error": "Shipping address is required"},
                status=400
            )

        supabase.postgrest.auth(token)

        # Check customer profile exists
        customer_response = (
            supabase.table("customers")
            .select("id")
            .eq("id", user.id)
            .execute()
        )

        if not customer_response.data:
            return JsonResponse(
                {"error": "Customer profile not found"},
                status=404
            )

        order_items_data = []
        total_amount = 0

        for item in items:

            product_id = item.get("product_id")
            quantity = item.get("quantity", 1)

            if not product_id:
                return JsonResponse(
                    {"error": "product_id is required"},
                    status=400
                )

            if quantity <= 0:
                return JsonResponse(
                    {"error": "Quantity must be greater than 0"},
                    status=400
                )

            product_response = (
                supabase.table("products")
                .select(
                    "id, artisan_id, name, price, stock, "
                    "status, is_available"
                )
                .eq("id", product_id)
                .eq("status", "published")
                .eq("is_available", True)
                .execute()
            )

            if not product_response.data:
                return JsonResponse(
                    {
                        "error": (
                            f"Product {product_id} "
                            "not found or unavailable"
                        )
                    },
                    status=404
                )

            product = product_response.data[0]

            if product["stock"] < quantity:
                return JsonResponse(
                    {
                        "error": (
                            f"Not enough stock for "
                            f"{product['name']}"
                        )
                    },
                    status=400
                )

            price = float(product["price"])

            item_total = price * quantity
            total_amount += item_total

            order_items_data.append({
                "product_id": product["id"],
                "artisan_id": product["artisan_id"],
                "quantity": quantity,
                "price": price
            })

        # Create order
        order_response = (
            supabase.table("orders")
            .insert({
                "customer_id": user.id,
                "total_amount": total_amount,
                "status": "pending",
                "shipping_address": shipping_address
            })
            .execute()
        )

        if not order_response.data:
            return JsonResponse(
                {"error": "Unable to create order"},
                status=400
            )

        order = order_response.data[0]
        order_id = order["id"]

        # Add order_id to each item
        for item in order_items_data:
            item["order_id"] = order_id

        items_response = (
            supabase.table("order_items")
            .insert(order_items_data)
            .execute()
        )

        return JsonResponse({
            "message": "Order created successfully",
            "order": order,
            "items": items_response.data
        }, status=201)

    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON body"},
            status=400
        )

    except ValueError:
        return JsonResponse(
            {"error": "Invalid Authorization header"},
            status=401
        )

    except Exception as e:
        print("CREATE ORDER ERROR:", repr(e))

        return JsonResponse(
            {"error": str(e)},
            status=400
        )

@csrf_exempt
def create_transaction(request):

    if request.method != "POST":
        return JsonResponse(
            {"error": "Only POST requests are allowed"},
            status=405
        )

    try:
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return JsonResponse(
                {"error": "Authorization header missing"},
                status=401
            )

        token_type, token = auth_header.split(" ")

        if token_type != "Bearer":
            return JsonResponse(
                {"error": "Invalid authorization type"},
                status=401
            )

        user_response = supabase.auth.get_user(token)
        user = user_response.user

        if not user:
            return JsonResponse(
                {"error": "Invalid or expired token"},
                status=401
            )

        data = json.loads(request.body)

        order_id = data.get("order_id")
        payment_method = data.get("payment_method")

        if not order_id:
            return JsonResponse(
                {"error": "order_id is required"},
                status=400
            )

        if not payment_method:
            return JsonResponse(
                {"error": "payment_method is required"},
                status=400
            )

        supabase.postgrest.auth(token)

        # Check order belongs to logged-in customer
        order_response = (
            supabase.table("orders")
            .select("id, customer_id, total_amount, status")
            .eq("id", order_id)
            .eq("customer_id", user.id)
            .execute()
        )

        if not order_response.data:
            return JsonResponse(
                {"error": "Order not found"},
                status=404
            )

        order = order_response.data[0]

        # Prevent duplicate transaction
        existing = (
            supabase.table("transactions")
            .select("id")
            .eq("order_id", order_id)
            .execute()
        )

        if existing.data:
            return JsonResponse(
                {"error": "Transaction already exists for this order"},
                status=400
            )

        transaction_reference = (
            f"KALA-{uuid.uuid4().hex[:12].upper()}"
        )

        transaction_data = {
            "order_id": order_id,
            "customer_id": user.id,
            "transaction_reference": transaction_reference,
            "payment_method": payment_method,

            # IMPORTANT:
            # amount DB ke order se aa raha hai,
            # frontend se nahi
            "amount": order["total_amount"],

            # frontend payment success decide nahi karega
            "payment_status": "pending"
        }

        response = (
            supabase.table("transactions")
            .insert(transaction_data)
            .execute()
        )

        return JsonResponse({
            "message": "Transaction created successfully",
            "transaction": response.data[0]
        }, status=201)

    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON body"},
            status=400
        )

    except ValueError:
        return JsonResponse(
            {"error": "Invalid Authorization header"},
            status=401
        )

    except Exception as e:
        print("CREATE TRANSACTION ERROR:", repr(e))

        return JsonResponse(
            {"error": str(e)},
            status=400
        )

@csrf_exempt
def get_my_transactions(request):

    if request.method != "GET":
        return JsonResponse(
            {"error": "Only GET requests are allowed"},
            status=405
        )

    try:
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return JsonResponse(
                {"error": "Authorization header missing"},
                status=401
            )

        token_type, token = auth_header.split(" ")

        if token_type != "Bearer":
            return JsonResponse(
                {"error": "Invalid authorization type"},
                status=401
            )

        user_response = supabase.auth.get_user(token)
        user = user_response.user

        if not user:
            return JsonResponse(
                {"error": "Invalid or expired token"},
                status=401
            )

        supabase.postgrest.auth(token)

        response = (
            supabase.table("transactions")
            .select("*")
            .eq("customer_id", user.id)
            .order("created_at", desc=True)
            .execute()
        )

        return JsonResponse({
            "message": "Transactions fetched successfully",
            "count": len(response.data),
            "transactions": response.data
        })

    except ValueError:
        return JsonResponse(
            {"error": "Invalid Authorization header"},
            status=401
        )

    except Exception as e:
        print("GET TRANSACTIONS ERROR:", repr(e))

        return JsonResponse(
            {"error": str(e)},
            status=400
        )

@csrf_exempt
def get_transaction(request, transaction_id):

    if request.method != "GET":
        return JsonResponse(
            {"error": "Only GET requests are allowed"},
            status=405
        )

    try:
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return JsonResponse(
                {"error": "Authorization header missing"},
                status=401
            )

        token_type, token = auth_header.split(" ")

        if token_type != "Bearer":
            return JsonResponse(
                {"error": "Invalid authorization type"},
                status=401
            )

        user_response = supabase.auth.get_user(token)
        user = user_response.user

        if not user:
            return JsonResponse(
                {"error": "Invalid or expired token"},
                status=401
            )

        supabase.postgrest.auth(token)

        response = (
            supabase.table("transactions")
            .select("*")
            .eq("id", str(transaction_id))
            .eq("customer_id", user.id)
            .execute()
        )

        if not response.data:
            return JsonResponse(
                {"error": "Transaction not found"},
                status=404
            )

        return JsonResponse({
            "message": "Transaction fetched successfully",
            "transaction": response.data[0]
        })

    except ValueError:
        return JsonResponse(
            {"error": "Invalid Authorization header"},
            status=401
        )

    except Exception as e:
        print("GET TRANSACTION ERROR:", repr(e))

        return JsonResponse(
            {"error": str(e)},
            status=400
        )

@csrf_exempt
def update_transaction_status(request, transaction_id):

    if request.method not in ["PATCH", "PUT"]:
        return JsonResponse(
            {"error": "Only PATCH or PUT requests are allowed"},
            status=405
        )

    try:
        # --------------------------------
        # AUTHENTICATE REQUEST
        # --------------------------------
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return JsonResponse(
                {"error": "Authorization header missing"},
                status=401
            )

        parts = auth_header.split(" ")

        if len(parts) != 2:
            return JsonResponse(
                {"error": "Invalid Authorization header"},
                status=401
            )

        token_type, token = parts

        if token_type != "Bearer":
            return JsonResponse(
                {"error": "Invalid authorization type"},
                status=401
            )

        user_response = supabase.auth.get_user(token)
        user = user_response.user

        if not user:
            return JsonResponse(
                {"error": "Invalid or expired token"},
                status=401
            )

        # --------------------------------
        # READ STATUS
        # --------------------------------
        data = json.loads(request.body)

        new_status = data.get("payment_status")

        allowed_statuses = [
            "pending",
            "successful",
            "failed",
            "refunded"
        ]

        if new_status not in allowed_statuses:
            return JsonResponse(
                {"error": "Invalid payment status"},
                status=400
            )

        # --------------------------------
        # SERVER-SIDE TRANSACTION LOOKUP
        # --------------------------------
        transaction_response = (
            supabase_admin
            .table("transactions")
            .select("*")
            .eq("id", str(transaction_id))
            .execute()
        )

        if not transaction_response.data:
            return JsonResponse(
                {"error": "Transaction not found"},
                status=404
            )

        transaction = transaction_response.data[0]

        # For current testing:
        # user can only target own transaction
        if transaction["customer_id"] != user.id:
            return JsonResponse(
                {"error": "You cannot access this transaction"},
                status=403
            )

        # --------------------------------
        # UPDATE PAYMENT
        # --------------------------------
        update_response = (
            supabase_admin
            .table("transactions")
            .update({
                "payment_status": new_status
            })
            .eq("id", str(transaction_id))
            .execute()
        )

        if not update_response.data:
            return JsonResponse(
                {"error": "Unable to update transaction"},
                status=400
            )

        updated_transaction = update_response.data[0]

        order_id = transaction["order_id"]

        # --------------------------------
        # UPDATE LINKED ORDER
        # --------------------------------
        if new_status == "successful":
            order_status = "confirmed"

        elif new_status == "failed":
            order_status = "pending"

        elif new_status == "refunded":
            order_status = "cancelled"

        else:
            order_status = "pending"

        order_response = (
            supabase_admin
            .table("orders")
            .update({
                "status": order_status
            })
            .eq("id", order_id)
            .execute()
        )

        return JsonResponse({
            "message": (
                "Transaction status updated successfully"
            ),
            "transaction": updated_transaction,
            "order": (
                order_response.data[0]
                if order_response.data
                else None
            )
        })

    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON body"},
            status=400
        )

    except Exception as e:
        print(
            "UPDATE TRANSACTION STATUS ERROR:",
            repr(e)
        )

        return JsonResponse(
            {"error": str(e)},
            status=400
        )

@csrf_exempt
def get_my_orders(request):

    if request.method != "GET":
        return JsonResponse(
            {"error": "Only GET requests are allowed"},
            status=405
        )

    try:
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return JsonResponse(
                {"error": "Authorization header missing"},
                status=401
            )

        parts = auth_header.split(" ")

        if len(parts) != 2:
            return JsonResponse(
                {"error": "Invalid Authorization header"},
                status=401
            )

        token_type, token = parts

        if token_type != "Bearer":
            return JsonResponse(
                {"error": "Invalid authorization type"},
                status=401
            )

        user_response = supabase.auth.get_user(token)
        user = user_response.user

        if not user:
            return JsonResponse(
                {"error": "Invalid or expired token"},
                status=401
            )

        supabase.postgrest.auth(token)

        orders_response = (
            supabase
            .table("orders")
            .select("*")
            .eq("customer_id", user.id)
            .order("created_at", desc=True)
            .execute()
        )

        orders = orders_response.data or []

        # Har order ke items fetch karo
        for order in orders:

            items_response = (
                supabase
                .table("order_items")
                .select(
                    "id, order_id, product_id, artisan_id, "
                    "quantity, price, created_at"
                )
                .eq("order_id", order["id"])
                .execute()
            )

            order["items"] = items_response.data or []

        return JsonResponse({
            "message": "Orders fetched successfully",
            "count": len(orders),
            "orders": orders
        })

    except Exception as e:

        print(
            "GET MY ORDERS ERROR:",
            repr(e)
        )

        return JsonResponse(
            {"error": str(e)},
            status=400
        )

@csrf_exempt
def get_order_detail(request, order_id):

    if request.method != "GET":
        return JsonResponse(
            {"error": "Only GET requests are allowed"},
            status=405
        )

    try:
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return JsonResponse(
                {"error": "Authorization header missing"},
                status=401
            )

        token_type, token = auth_header.split(" ")

        if token_type != "Bearer":
            return JsonResponse(
                {"error": "Invalid authorization type"},
                status=401
            )

        user_response = supabase.auth.get_user(token)
        user = user_response.user

        if not user:
            return JsonResponse(
                {"error": "Invalid or expired token"},
                status=401
            )

        supabase.postgrest.auth(token)

        order_response = (
            supabase
            .table("orders")
            .select("*")
            .eq("id", str(order_id))
            .eq("customer_id", user.id)
            .execute()
        )

        if not order_response.data:
            return JsonResponse(
                {"error": "Order not found"},
                status=404
            )

        order = order_response.data[0]

        items_response = (
            supabase
            .table("order_items")
            .select("*")
            .eq("order_id", str(order_id))
            .execute()
        )

        order["items"] = items_response.data or []

        return JsonResponse({
            "message": "Order fetched successfully",
            "order": order
        })

    except Exception as e:
        print("GET ORDER DETAIL ERROR:", repr(e))

        return JsonResponse(
            {"error": str(e)},
            status=400
        )

@csrf_exempt
def get_artisan_orders(request):

    if request.method != "GET":
        return JsonResponse(
            {"error": "Only GET requests are allowed"},
            status=405
        )

    try:
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return JsonResponse(
                {"error": "Authorization header missing"},
                status=401
            )

        token_type, token = auth_header.split(" ")

        if token_type != "Bearer":
            return JsonResponse(
                {"error": "Invalid authorization type"},
                status=401
            )

        user_response = supabase.auth.get_user(token)
        user = user_response.user

        if not user:
            return JsonResponse(
                {"error": "Invalid or expired token"},
                status=401
            )

        supabase.postgrest.auth(token)

        items_response = (
            supabase
            .table("order_items")
            .select("*")
            .eq("artisan_id", user.id)
            .order("created_at", desc=True)
            .execute()
        )

        items = items_response.data or []

        return JsonResponse({
            "message": "Artisan orders fetched successfully",
            "count": len(items),
            "orders": items
        })

    except Exception as e:

        print("GET ARTISAN ORDERS ERROR:", repr(e))

        return JsonResponse(
            {"error": str(e)},
            status=400
        )

@csrf_exempt
def update_order_status(request, order_id):

    if request.method not in ["PATCH", "PUT"]:
        return JsonResponse(
            {"error": "Only PATCH or PUT requests are allowed"},
            status=405
        )

    try:
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return JsonResponse(
                {"error": "Authorization header missing"},
                status=401
            )

        token_type, token = auth_header.split(" ")

        if token_type != "Bearer":
            return JsonResponse(
                {"error": "Invalid authorization type"},
                status=401
            )

        user_response = supabase.auth.get_user(token)
        user = user_response.user

        if not user:
            return JsonResponse(
                {"error": "Invalid or expired token"},
                status=401
            )

        data = json.loads(request.body)

        new_status = data.get("status")

        allowed_statuses = [
            "processing",
            "shipped",
            "delivered"
        ]

        if new_status not in allowed_statuses:
            return JsonResponse(
                {
                    "error": (
                        "Allowed statuses: "
                        "processing, shipped, delivered"
                    )
                },
                status=400
            )

        # Check artisan owns an item in this order
        ownership = (
            supabase_admin
            .table("order_items")
            .select("id")
            .eq("order_id", str(order_id))
            .eq("artisan_id", user.id)
            .execute()
        )

        if not ownership.data:
            return JsonResponse(
                {"error": "You cannot update this order"},
                status=403
            )

        order_response = (
            supabase_admin
            .table("orders")
            .select("*")
            .eq("id", str(order_id))
            .execute()
        )

        if not order_response.data:
            return JsonResponse(
                {"error": "Order not found"},
                status=404
            )

        current_order = order_response.data[0]
        current_status = current_order["status"]

        transitions = {
            "confirmed": ["processing"],
            "processing": ["shipped"],
            "shipped": ["delivered"]
        }

        allowed_next = transitions.get(
            current_status,
            []
        )

        if new_status not in allowed_next:
            return JsonResponse(
                {
                    "error": (
                        f"Cannot change order from "
                        f"{current_status} to {new_status}"
                    )
                },
                status=400
            )

        update_response = (
            supabase_admin
            .table("orders")
            .update({
                "status": new_status
            })
            .eq("id", str(order_id))
            .execute()
        )

        return JsonResponse({
            "message": "Order status updated successfully",
            "order": update_response.data[0]
        })

    except json.JSONDecodeError:

        return JsonResponse(
            {"error": "Invalid JSON body"},
            status=400
        )

    except Exception as e:

        print("UPDATE ORDER STATUS ERROR:", repr(e))

        return JsonResponse(
            {"error": str(e)},
            status=400
        )
# --------------------------------------------------
# IMAGE + VOICE AI
# --------------------------------------------------

@csrf_exempt
def analyze_product_image(request):
    if request.method != "POST":
        return JsonResponse(
            {"error": "POST required"},
            status=405
        )

    uploaded_file = request.FILES.get("file")

    if not uploaded_file:
        return JsonResponse(
            {"error": "No image file provided"},
            status=400
        )

    allowed_types = {
        "image/jpeg",
        "image/jpg",
        "image/png",
        "image/webp",
    }

    if uploaded_file.content_type not in allowed_types:
        return JsonResponse(
            {
                "error": "Unsupported image type",
                "type": uploaded_file.content_type,
            },
            status=400
        )

    if uploaded_file.size > 10 * 1024 * 1024:
        return JsonResponse(
            {"error": "Image exceeds 10 MB limit"},
            status=400
        )

    suffix = os.path.splitext(uploaded_file.name)[1] or ".jpg"
    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix
        ) as temp_file:
            for chunk in uploaded_file.chunks():
                temp_file.write(chunk)

            temp_path = temp_file.name

        if not AI_BASE_URL:
            return JsonResponse(
                {"error": "AI_BASE_URL is not configured"},
                status=500
            )

        with open(temp_path, "rb") as f:
            ai_response = requests.post(
                f"{AI_BASE_URL.rstrip('/')}/api/vision/analyze",
                files={
                    "file": (
                        uploaded_file.name,
                        f,
                        uploaded_file.content_type
                    )
                },
                timeout=180
            )

        ai_response.raise_for_status()
        ai_data = ai_response.json()
        analysis = ai_data.get("analysis")

        return JsonResponse({
            "success": True,
            "filename": uploaded_file.name,
            "analysis": analysis,
        })

    except Exception as e:
        print("VISION AI ERROR:", repr(e))

        return JsonResponse(
            {"error": str(e)},
            status=500
        )

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


@csrf_exempt
def transcribe_product_voice(request):
    if request.method != "POST":
        return JsonResponse(
            {"error": "POST required"},
            status=405
        )

    uploaded_file = request.FILES.get("file")

    if not uploaded_file:
        return JsonResponse(
            {"error": "No audio file provided"},
            status=400
        )

    allowed_types = {
        "audio/wav",
        "audio/mpeg",
        "audio/mp3",
        "audio/x-wav",
        "audio/webm",
        "audio/mp4",
        "audio/ogg",
    }

    if uploaded_file.content_type not in allowed_types:
        return JsonResponse(
            {
                "error": "Unsupported audio type",
                "type": uploaded_file.content_type,
            },
            status=400
        )

    suffix = os.path.splitext(uploaded_file.name)[1] or ".webm"
    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix
        ) as temp_file:
            for chunk in uploaded_file.chunks():
                temp_file.write(chunk)

            temp_path = temp_file.name

        if not AI_BASE_URL:
            return JsonResponse(
                {"error": "AI_BASE_URL is not configured"},
                status=500
            )

        with open(temp_path, "rb") as f:
            ai_response = requests.post(
                f"{AI_BASE_URL.rstrip('/')}/api/voice/transcribe",
                files={
                    "file": (
                        uploaded_file.name,
                        f,
                        uploaded_file.content_type
                    )
                },
                timeout=180
            )

        ai_response.raise_for_status()
        ai_data = ai_response.json()
        result = {
            "text": ai_data.get("text", ""),
            "language": ai_data.get("language"),
            "language_probability": ai_data.get("language_probability")
        }

        return JsonResponse({
            "success": True,
            **result,
        })

    except Exception as e:
        print("VOICE AI ERROR:", repr(e))

        return JsonResponse(
            {"error": str(e)},
            status=500
        )

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


@csrf_exempt
def predict_price(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        data = json.loads(request.body)

        required_fields = [
            "product",
            "category",
            "subcategory",
            "craft",
            "material",
            "technique",
            "state",
            "region",
            "size",
            "complexity",
            "customization",
            "labor_hours",
            "raw_material_cost",
            "packaging_cost",
            "transport_cost",
            "direct_cost",
        ]

        missing_fields = [
            field for field in required_fields
            if field not in data
        ]

        if missing_fields:
            return JsonResponse(
                {
                    "error": "Missing required fields",
                    "fields": missing_fields,
                },
                status=400,
            )

        result = pricing_service.predict(data)

        return JsonResponse({
            "success": True,
            "predicted_price": result["predicted_price"],
            "currency": "INR",
            "market_features": result["market_features"],
        })

    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON body"},
            status=400,
        )

    except Exception as e:
        print("PREDICT PRICE ERROR:", repr(e))
        return JsonResponse(
            {"error": str(e)},
            status=400,
        )