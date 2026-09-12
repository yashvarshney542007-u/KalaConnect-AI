import json
import uuid

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from config.supabase_client import supabase, supabase_admin


# ============================================================
# HELPERS
# ============================================================

def json_body(request):
    try:
        return json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return {}


def get_token(request):
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    return auth.split(" ", 1)[1].strip()


def get_authenticated_user(request):
    token = get_token(request)

    if not token:
        return None, JsonResponse(
            {"error": "Authorization token required"},
            status=401
        )

    try:
        response = supabase.auth.get_user(token)
        user = response.user

        if not user:
            return None, JsonResponse(
                {"error": "Invalid or expired token"},
                status=401
            )

        return user, None

    except Exception as e:
        return None, JsonResponse(
            {"error": "Authentication failed", "details": str(e)},
            status=401
        )


def get_user_profile(user_id):
    response = (
        supabase_admin
        .table("users")
        .select("*")
        .eq("id", user_id)
        .limit(1)
        .execute()
    )

    if response.data:
        return response.data[0]

    return None


def get_artisan_by_user(user_id):
    response = (
        supabase_admin
        .table("artisans")
        .select("*")
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )

    if response.data:
        return response.data[0]

    return None


# ============================================================
# HOME
# ============================================================

def home(request):
    return JsonResponse({
        "message": "KalaConnect Django API is running"
    })


# ============================================================
# AUTHENTICATION
# ============================================================

@csrf_exempt
def signup(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    data = json_body(request)

    email = data.get("email")
    password = data.get("password")
    name = data.get("name") or data.get("full_name")
    phone_number = data.get("phone_number") or data.get("phone")

    if not email or not password:
        return JsonResponse(
            {"error": "Email and password are required"},
            status=400
        )

    try:
        auth_response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "name": name or ""
                }
            }
        })

        user = auth_response.user

        if not user:
            return JsonResponse(
                {"error": "Signup failed"},
                status=400
            )

        # Create corresponding public.users record.
        existing = get_user_profile(str(user.id))

        if not existing:
            supabase_admin.table("users").insert({
                "id": str(user.id),
                "name": name or email.split("@")[0],
                "email": email,
                "phone_number": phone_number
            }).execute()

        session = auth_response.session

        return JsonResponse({
            "message": "Signup successful",
            "user": {
                "id": str(user.id),
                "email": user.email
            },
            "access_token": (
                session.access_token if session else None
            ),
            "refresh_token": (
                session.refresh_token if session else None
            )
        }, status=201)

    except Exception as e:
        return JsonResponse(
            {"error": "Signup failed", "details": str(e)},
            status=400
        )


@csrf_exempt
def login_user(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    data = json_body(request)

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return JsonResponse(
            {"error": "Email and password are required"},
            status=400
        )

    try:
        auth_response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        user = auth_response.user
        session = auth_response.session

        if not user or not session:
            return JsonResponse(
                {"error": "Login failed"},
                status=401
            )

        return JsonResponse({
            "message": "Login successful",
            "user": {
                "id": str(user.id),
                "email": user.email
            },
            "access_token": session.access_token,
            "refresh_token": session.refresh_token
        })

    except Exception as e:
        return JsonResponse(
            {"error": "Invalid email or password", "details": str(e)},
            status=401
        )


@csrf_exempt
def logout_user(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    return JsonResponse({
        "message": "Logout handled by Supabase client"
    })


def protected_test(request):
    user, error = get_authenticated_user(request)

    if error:
        return error

    return JsonResponse({
        "message": "Authentication successful",
        "user_id": str(user.id),
        "email": user.email
    })


# ============================================================
# USER PROFILE
# ============================================================

@csrf_exempt
def create_customer_profile(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    user, error = get_authenticated_user(request)

    if error:
        return error

    data = json_body(request)

    existing = get_user_profile(str(user.id))

    if existing:
        return JsonResponse({
            "message": "User profile already exists",
            "profile": existing
        })

    profile = {
        "id": str(user.id),
        "name": data.get("name") or user.email.split("@")[0],
        "email": data.get("email") or user.email,
        "phone_number": data.get("phone_number")
    }

    try:
        response = (
            supabase_admin
            .table("users")
            .insert(profile)
            .execute()
        )

        return JsonResponse({
            "message": "User profile created",
            "profile": response.data[0] if response.data else profile
        }, status=201)

    except Exception as e:
        return JsonResponse(
            {"error": "Could not create profile", "details": str(e)},
            status=400
        )


def get_customer_profile(request):
    if request.method != "GET":
        return JsonResponse({"error": "GET required"}, status=405)

    user, error = get_authenticated_user(request)

    if error:
        return error

    profile = get_user_profile(str(user.id))

    if not profile:
        return JsonResponse(
            {"error": "User profile not found"},
            status=404
        )

    return JsonResponse({"profile": profile})


@csrf_exempt
def update_customer_profile(request):
    if request.method != "PATCH" and request.method != "PUT":
        return JsonResponse(
            {"error": "PATCH or PUT required"},
            status=405
        )

    user, error = get_authenticated_user(request)

    if error:
        return error

    data = json_body(request)

    allowed = {
        "name",
        "email",
        "phone_number"
    }

    updates = {
        key: value
        for key, value in data.items()
        if key in allowed
    }

    if not updates:
        return JsonResponse(
            {"error": "No valid fields supplied"},
            status=400
        )

    try:
        response = (
            supabase_admin
            .table("users")
            .update(updates)
            .eq("id", str(user.id))
            .execute()
        )

        return JsonResponse({
            "message": "Profile updated",
            "profile": response.data[0] if response.data else None
        })

    except Exception as e:
        return JsonResponse(
            {"error": "Could not update profile", "details": str(e)},
            status=400
        )


# ============================================================
# ARTISAN PROFILE
# ============================================================

@csrf_exempt
def create_artisan_profile(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    user, error = get_authenticated_user(request)

    if error:
        return error

    data = json_body(request)

    existing = get_artisan_by_user(str(user.id))

    if existing:
        return JsonResponse({
            "message": "Artisan profile already exists",
            "profile": existing
        })

    profile = {
        "user_id": str(user.id),
        "name": data.get("name") or data.get("full_name") or user.email.split("@")[0],
        "email": data.get("email") or user.email,
        "phone_number": data.get("phone_number") or data.get("phone"),
        "craft": data.get("craft"),
        "location": data.get("location")
    }

    try:
        response = (
            supabase_admin
            .table("artisans")
            .insert(profile)
            .execute()
        )

        return JsonResponse({
            "message": "Artisan profile created",
            "profile": response.data[0] if response.data else profile
        }, status=201)

    except Exception as e:
        return JsonResponse(
            {"error": "Could not create artisan profile",
             "details": str(e)},
            status=400
        )


def get_artisan_profile(request):
    if request.method != "GET":
        return JsonResponse({"error": "GET required"}, status=405)

    user, error = get_authenticated_user(request)

    if error:
        return error

    profile = get_artisan_by_user(str(user.id))

    if not profile:
        return JsonResponse(
            {"error": "Artisan profile not found"},
            status=404
        )

    return JsonResponse({"profile": profile})


@csrf_exempt
def update_artisan_profile(request):
    if request.method != "PATCH" and request.method != "PUT":
        return JsonResponse(
            {"error": "PATCH or PUT required"},
            status=405
        )

    user, error = get_authenticated_user(request)

    if error:
        return error

    data = json_body(request)

    allowed = {
        "name",
        "email",
        "phone_number",
        "craft",
        "location"
    }

    updates = {
        key: value
        for key, value in data.items()
        if key in allowed
    }

    if not updates:
        return JsonResponse(
            {"error": "No valid fields supplied"},
            status=400
        )

    try:
        response = (
            supabase_admin
            .table("artisans")
            .update(updates)
            .eq("user_id", str(user.id))
            .execute()
        )

        return JsonResponse({
            "message": "Artisan profile updated",
            "profile": response.data[0] if response.data else None
        })

    except Exception as e:
        return JsonResponse(
            {"error": "Could not update artisan profile",
             "details": str(e)},
            status=400
        )


# ============================================================
# PRODUCTS
# ============================================================

@csrf_exempt
def create_product(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    user, error = get_authenticated_user(request)

    if error:
        return error

    artisan = get_artisan_by_user(str(user.id))

    if not artisan:
        return JsonResponse(
            {"error": "Create an artisan profile first"},
            status=403
        )

    data = json_body(request)

    if not data.get("name"):
        return JsonResponse(
            {"error": "Product name is required"},
            status=400
        )

    if data.get("price") is None:
        return JsonResponse(
            {"error": "Product price is required"},
            status=400
        )

    product = {
        "artisan_id": str(artisan["id"]),
        "name": data["name"],
        "description": data.get("description"),
        "price": data["price"],
        "image_url": data.get("image_url")
    }

    try:
        response = (
            supabase_admin
            .table("products")
            .insert(product)
            .execute()
        )

        return JsonResponse({
            "message": "Product created",
            "product": response.data[0] if response.data else None
        }, status=201)

    except Exception as e:
        return JsonResponse(
            {"error": "Could not create product", "details": str(e)},
            status=400
        )


def get_my_products(request):
    if request.method != "GET":
        return JsonResponse({"error": "GET required"}, status=405)

    user, error = get_authenticated_user(request)

    if error:
        return error

    artisan = get_artisan_by_user(str(user.id))

    if not artisan:
        return JsonResponse({"products": []})

    response = (
        supabase_admin
        .table("products")
        .select("*")
        .eq("artisan_id", str(artisan["id"]))
        .order("created_at", desc=True)
        .execute()
    )

    return JsonResponse({
        "products": response.data or []
    })


def get_product(request, product_id):
    if request.method != "GET":
        return JsonResponse({"error": "GET required"}, status=405)

    try:
        uuid.UUID(str(product_id))
    except ValueError:
        return JsonResponse({"error": "Invalid product ID"}, status=400)

    response = (
        supabase_admin
        .table("products")
        .select("*")
        .eq("id", str(product_id))
        .limit(1)
        .execute()
    )

    if not response.data:
        return JsonResponse(
            {"error": "Product not found"},
            status=404
        )

    return JsonResponse({
        "product": response.data[0]
    })


@csrf_exempt
def update_product(request, product_id):
    if request.method != "PATCH" and request.method != "PUT":
        return JsonResponse(
            {"error": "PATCH or PUT required"},
            status=405
        )

    user, error = get_authenticated_user(request)

    if error:
        return error

    artisan = get_artisan_by_user(str(user.id))

    if not artisan:
        return JsonResponse(
            {"error": "Artisan profile not found"},
            status=403
        )

    data = json_body(request)

    allowed = {
        "name",
        "description",
        "price",
        "image_url"
    }

    updates = {
        key: value
        for key, value in data.items()
        if key in allowed
    }

    if not updates:
        return JsonResponse(
            {"error": "No valid fields supplied"},
            status=400
        )

    try:
        response = (
            supabase_admin
            .table("products")
            .update(updates)
            .eq("id", str(product_id))
            .eq("artisan_id", str(artisan["id"]))
            .execute()
        )

        if not response.data:
            return JsonResponse(
                {"error": "Product not found or not owned by you"},
                status=404
            )

        return JsonResponse({
            "message": "Product updated",
            "product": response.data[0]
        })

    except Exception as e:
        return JsonResponse(
            {"error": "Could not update product", "details": str(e)},
            status=400
        )


@csrf_exempt
def delete_product(request, product_id):
    if request.method != "DELETE":
        return JsonResponse({"error": "DELETE required"}, status=405)

    user, error = get_authenticated_user(request)

    if error:
        return error

    artisan = get_artisan_by_user(str(user.id))

    if not artisan:
        return JsonResponse(
            {"error": "Artisan profile not found"},
            status=403
        )

    try:
        response = (
            supabase_admin
            .table("products")
            .delete()
            .eq("id", str(product_id))
            .eq("artisan_id", str(artisan["id"]))
            .execute()
        )

        return JsonResponse({
            "message": "Product deleted",
            "deleted": bool(response.data)
        })

    except Exception as e:
        return JsonResponse(
            {"error": "Could not delete product", "details": str(e)},
            status=400
        )


@csrf_exempt
def publish_product(request, product_id):
    """
    The final products schema has no status/is_available columns.
    Therefore a product is considered published as soon as it exists.
    This endpoint is retained so the existing frontend URL does not break.
    """

    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    user, error = get_authenticated_user(request)

    if error:
        return error

    artisan = get_artisan_by_user(str(user.id))

    if not artisan:
        return JsonResponse(
            {"error": "Artisan profile not found"},
            status=403
        )

    response = (
        supabase_admin
        .table("products")
        .select("*")
        .eq("id", str(product_id))
        .eq("artisan_id", str(artisan["id"]))
        .limit(1)
        .execute()
    )

    if not response.data:
        return JsonResponse(
            {"error": "Product not found or not owned by you"},
            status=404
        )

    return JsonResponse({
        "message": "Product published successfully",
        "product": response.data[0]
    })


@csrf_exempt
def upload_product_image(request, product_id):
    """
    Final schema stores image_url only.
    The frontend can provide an already uploaded/public image URL.
    """

    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    user, error = get_authenticated_user(request)

    if error:
        return error

    artisan = get_artisan_by_user(str(user.id))

    if not artisan:
        return JsonResponse(
            {"error": "Artisan profile not found"},
            status=403
        )

    image_url = request.POST.get("image_url")

    if not image_url:
        try:
            data = json_body(request)
            image_url = data.get("image_url")
        except Exception:
            image_url = None

    if not image_url:
        return JsonResponse(
            {"error": "image_url is required"},
            status=400
        )

    response = (
        supabase_admin
        .table("products")
        .update({"image_url": image_url})
        .eq("id", str(product_id))
        .eq("artisan_id", str(artisan["id"]))
        .execute()
    )

    if not response.data:
        return JsonResponse(
            {"error": "Product not found or not owned by you"},
            status=404
        )

    return JsonResponse({
        "message": "Product image updated",
        "product": response.data[0]
    })


# ============================================================
# MARKETPLACE
# ============================================================

def public_products(request):
    if request.method != "GET":
        return JsonResponse({"error": "GET required"}, status=405)

    response = (
        supabase_admin
        .table("products")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )

    return JsonResponse({
        "products": response.data or []
    })


def public_product_detail(request, product_id):
    if request.method != "GET":
        return JsonResponse({"error": "GET required"}, status=405)

    response = (
        supabase_admin
        .table("products")
        .select("*")
        .eq("id", str(product_id))
        .limit(1)
        .execute()
    )

    if not response.data:
        return JsonResponse(
            {"error": "Product not found"},
            status=404
        )

    return JsonResponse({
        "product": response.data[0]
    })


# ============================================================
# ORDERS
# ============================================================

@csrf_exempt
def create_order(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    user, error = get_authenticated_user(request)

    if error:
        return error

    data = json_body(request)

    product_id = data.get("product_id")
    quantity = data.get("quantity", 1)

    if not product_id:
        return JsonResponse(
            {"error": "product_id is required"},
            status=400
        )

    try:
        quantity = int(quantity)

        if quantity <= 0:
            raise ValueError

    except (ValueError, TypeError):
        return JsonResponse(
            {"error": "quantity must be a positive integer"},
            status=400
        )

    product_response = (
        supabase_admin
        .table("products")
        .select("*")
        .eq("id", str(product_id))
        .limit(1)
        .execute()
    )

    if not product_response.data:
        return JsonResponse(
            {"error": "Product not found"},
            status=404
        )

    product = product_response.data[0]

    total_amount = float(product["price"]) * quantity

    order = {
        "user_id": str(user.id),
        "product_id": str(product["id"]),
        "quantity": quantity,
        "total_amount": total_amount,
        "status": "pending"
    }

    try:
        response = (
            supabase_admin
            .table("orders")
            .insert(order)
            .execute()
        )

        return JsonResponse({
            "message": "Order created",
            "order": response.data[0] if response.data else None
        }, status=201)

    except Exception as e:
        return JsonResponse(
            {"error": "Could not create order", "details": str(e)},
            status=400
        )


def get_my_orders(request):
    if request.method != "GET":
        return JsonResponse({"error": "GET required"}, status=405)

    user, error = get_authenticated_user(request)

    if error:
        return error

    response = (
        supabase_admin
        .table("orders")
        .select("*")
        .eq("user_id", str(user.id))
        .order("created_at", desc=True)
        .execute()
    )

    return JsonResponse({
        "orders": response.data or []
    })


def get_order(request, order_id):
    if request.method != "GET":
        return JsonResponse({"error": "GET required"}, status=405)

    user, error = get_authenticated_user(request)

    if error:
        return error

    response = (
        supabase_admin
        .table("orders")
        .select("*")
        .eq("id", str(order_id))
        .eq("user_id", str(user.id))
        .limit(1)
        .execute()
    )

    if not response.data:
        return JsonResponse(
            {"error": "Order not found"},
            status=404
        )

    return JsonResponse({
        "order": response.data[0]
    })


def artisan_orders(request):
    if request.method != "GET":
        return JsonResponse({"error": "GET required"}, status=405)

    user, error = get_authenticated_user(request)

    if error:
        return error

    artisan = get_artisan_by_user(str(user.id))

    if not artisan:
        return JsonResponse({"orders": []})

    products_response = (
        supabase_admin
        .table("products")
        .select("id")
        .eq("artisan_id", str(artisan["id"]))
        .execute()
    )

    product_ids = [
        product["id"]
        for product in (products_response.data or [])
    ]

    if not product_ids:
        return JsonResponse({"orders": []})

    orders_response = (
        supabase_admin
        .table("orders")
        .select("*")
        .in_("product_id", product_ids)
        .order("created_at", desc=True)
        .execute()
    )

    return JsonResponse({
        "orders": orders_response.data or []
    })


@csrf_exempt
def update_order_status(request, order_id):
    if request.method != "PATCH" and request.method != "PUT":
        return JsonResponse(
            {"error": "PATCH or PUT required"},
            status=405
        )

    user, error = get_authenticated_user(request)

    if error:
        return error

    data = json_body(request)
    status_value = data.get("status")

    if not status_value:
        return JsonResponse(
            {"error": "status is required"},
            status=400
        )

    allowed_statuses = {
        "pending",
        "confirmed",
        "processing",
        "shipped",
        "delivered",
        "cancelled"
    }

    if status_value not in allowed_statuses:
        return JsonResponse(
            {"error": "Invalid order status"},
            status=400
        )

    artisan = get_artisan_by_user(str(user.id))

    if not artisan:
        return JsonResponse(
            {"error": "Artisan profile not found"},
            status=403
        )

    order_response = (
        supabase_admin
        .table("orders")
        .select("*, products!inner(artisan_id)")
        .eq("id", str(order_id))
        .eq("products.artisan_id", str(artisan["id"]))
        .limit(1)
        .execute()
    )

    if not order_response.data:
        return JsonResponse(
            {"error": "Order not found or not associated with your products"},
            status=404
        )

    response = (
        supabase_admin
        .table("orders")
        .update({"status": status_value})
        .eq("id", str(order_id))
        .execute()
    )

    return JsonResponse({
        "message": "Order status updated",
        "order": response.data[0] if response.data else None
    })


# ============================================================
# SALES
# ============================================================

@csrf_exempt
def create_transaction(request):
    """
    Compatibility endpoint.
    Final database uses `sales`, not `transactions`.
    """

    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    user, error = get_authenticated_user(request)

    if error:
        return error

    artisan = get_artisan_by_user(str(user.id))

    if not artisan:
        return JsonResponse(
            {"error": "Artisan profile not found"},
            status=403
        )

    data = json_body(request)

    order_id = data.get("order_id")
    amount = data.get("amount")

    if not order_id:
        return JsonResponse(
            {"error": "order_id is required"},
            status=400
        )

    order_response = (
        supabase_admin
        .table("orders")
        .select("*, products!inner(artisan_id)")
        .eq("id", str(order_id))
        .eq("products.artisan_id", str(artisan["id"]))
        .limit(1)
        .execute()
    )

    if not order_response.data:
        return JsonResponse(
            {"error": "Order not found or not associated with your product"},
            status=404
        )

    order = order_response.data[0]

    sale = {
        "order_id": str(order["id"]),
        "artisan_id": str(artisan["id"]),
        "amount": amount if amount is not None else order["total_amount"]
    }

    try:
        response = (
            supabase_admin
            .table("sales")
            .insert(sale)
            .execute()
        )

        return JsonResponse({
            "message": "Sale created",
            "sale": response.data[0] if response.data else None
        }, status=201)

    except Exception as e:
        return JsonResponse(
            {"error": "Could not create sale", "details": str(e)},
            status=400
        )


def get_my_transactions(request):
    if request.method != "GET":
        return JsonResponse({"error": "GET required"}, status=405)

    user, error = get_authenticated_user(request)

    if error:
        return error

    artisan = get_artisan_by_user(str(user.id))

    if not artisan:
        return JsonResponse({"transactions": []})

    response = (
        supabase_admin
        .table("sales")
        .select("*")
        .eq("artisan_id", str(artisan["id"]))
        .order("created_at", desc=True)
        .execute()
    )

    return JsonResponse({
        "transactions": response.data or [],
        "sales": response.data or []
    })


def get_transaction(request, transaction_id):
    if request.method != "GET":
        return JsonResponse({"error": "GET required"}, status=405)

    user, error = get_authenticated_user(request)

    if error:
        return error

    artisan = get_artisan_by_user(str(user.id))

    if not artisan:
        return JsonResponse(
            {"error": "Artisan profile not found"},
            status=403
        )

    response = (
        supabase_admin
        .table("sales")
        .select("*")
        .eq("id", str(transaction_id))
        .eq("artisan_id", str(artisan["id"]))
        .limit(1)
        .execute()
    )

    if not response.data:
        return JsonResponse(
            {"error": "Sale not found"},
            status=404
        )

    return JsonResponse({
        "transaction": response.data[0],
        "sale": response.data[0]
    })


@csrf_exempt
def update_transaction_status(request, transaction_id):
    """
    `sales` has no status column in the final schema.
    Status belongs to `orders`.
    """

    return JsonResponse({
        "message": "Transaction status is not stored in the final schema. Use order status instead."
    }, status=400)