from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView

from config import views
from crazyyy import views as frontend_views


urlpatterns = [

    # Customer frontend
    path(
        "",
        frontend_views.index,
        name="home"
    ),

    path(
        "auth/protected-test/",
        views.protected_test,
        name="protected_test"
    ),
    # Seller frontend
    path(
        "seller/",
        TemplateView.as_view(template_name="artisan-login.html"),
        name="seller",
    ),

    path(
        "seller/register/",
        TemplateView.as_view(template_name="artisan-register.html"),
        name="seller-register",
    ),

    path(
        "seller/dashboard/",
        TemplateView.as_view(template_name="artisan-dashboard.html"),
        name="seller-dashboard",
    ),

    path(
        "seller/profile/",
        TemplateView.as_view(template_name="artisan-profile.html"),
        name="seller-profile",
    ),

    path(
        "seller/upload/",
        TemplateView.as_view(
            template_name="artisan-upload-camera-fixed.html"
        ),
        name="seller-upload",
    ),

    path(
        "seller/publish/",
        TemplateView.as_view(
            template_name="artisan-publish-product.html"
        ),
        name="seller-publish",
    ),
    path(
    "seller/review-product/",
    TemplateView.as_view(
        template_name="artisan-review-product.html"
    ),
    name="seller-review-product",
),

    path(
        "seller/price-prediction/",
        TemplateView.as_view(
            template_name="artisan-price-prediction.html"
        ),
        name="seller-price-prediction",
    ),



    # Django admin
    path(
        "admin/",
        admin.site.urls
    ),


    # Supabase authentication
    path(
        "auth/signup/",
        views.signup,
        name="signup"
    ),

    path(
        "auth/login/",
        views.login_user,
        name="login"
    ),

    path(
        "auth/logout/",
        views.logout_user,
        name="logout"
    ),

    path(
    "artisan/profile/create/",
    views.create_artisan_profile,
    name="create_artisan_profile"
),

path(
    "artisan/profile/",
    views.get_artisan_profile,
    name="get_artisan_profile"
),

path(
    "artisan/profile/update/",
    views.update_artisan_profile,
    name="update_artisan_profile"
),

path(
    "customer/profile/create/",
    views.create_customer_profile,
    name="create_customer_profile"
),

path(
    "customer/profile/",
    views.get_customer_profile,
    name="get_customer_profile"
),

path(
    "customer/profile/update/",
    views.update_customer_profile,
    name="update_customer_profile"
),

path(
    "products/create/",
    views.create_product,
    name="create_product"
),

path(
    "products/mine/",
    views.get_my_products,
    name="get_my_products"
),

path(
    "products/<uuid:product_id>/",
    views.get_product,
    name="get_product"
),

path(
    "products/<uuid:product_id>/update/",
    views.update_product,
    name="update_product"
),

path(
    "products/<uuid:product_id>/delete/",
    views.delete_product,
    name="delete_product"
),

path(
    "products/<uuid:product_id>/publish/",
    views.publish_product,
    name="publish_product"
),

path(
    "products/<uuid:product_id>/image/",
    views.upload_product_image,
    name="upload_product_image"
),

path(
    "marketplace/products/",
    views.public_products,
    name="public_products"
),

path(
    "marketplace/products/<uuid:product_id>/",
    views.public_product_detail,
    name="public_product_detail"
),

path(
    "orders/create/",
    views.create_order,
    name="create_order"
),

path(
    "transactions/create/",
    views.create_transaction,
    name="create_transaction"
),

path(
    "transactions/mine/",
    views.get_my_transactions,
    name="get_my_transactions"
),

path(
    "transactions/<uuid:transaction_id>/",
    views.get_transaction,
    name="get_transaction"
),

path(
    "transactions/<uuid:transaction_id>/status/",
    views.update_transaction_status,
    name="update_transaction_status"
),

path(
    "transactions/<uuid:transaction_id>/status/",
    views.update_transaction_status,
    name="update_transaction_status"
),

path(
    "orders/mine/",
    views.get_my_orders,
    name="get_my_orders"
),

path(
    "orders/<uuid:order_id>/",
    views.get_order,
    name="get_order_detail"
),

path(
    "artisan/orders/",
    views.artisan_orders,
    name="get_artisan_orders"
),

path(
    "orders/<uuid:order_id>/status/",
    views.update_order_status,
    name="update_order_status"
),

path(
    "api/predict-price/",
    views.predict_price,
    name="predict_price"
),
]