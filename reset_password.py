import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv("SUPABASE_URL")
secret_key = os.getenv("SUPABASE_SECRET_KEY")

admin = create_client(url, secret_key)

user_id = "c9fdb190-b818-427e-a753-46a5ffc381f2"

new_password = input("Enter new password: ")

response = admin.auth.admin.update_user_by_id(
    user_id,
    {
        "password": new_password,
        "email_confirm": True
    }
)

print("Password updated successfully")
print(response.user.email)