from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
import requests

app = Flask(__name__)

# Enable CORS to allow cross-origin requests
CORS(app)

# Configure Swagger UI
SWAGGER_URL = "/swagger"
API_URL = "/static/swagger.json"  # Path to the Swagger JSON file
swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


# Example of a Keycloak protected endpoint
@app.route("/api/userinfo", methods=["GET"])
def protected():
    token = request.headers.get("Authorization")

    # Check if the token is present in the request headers
    if token is None:
        return jsonify({"error": "Token not provided"}), 401

    # Verify the token with Keycloak server (adjust the URL if needed)
    response = requests.get(
        "http://localhost:8080/realms/master/protocol/openid-connect/userinfo",
        headers={"Authorization": token},
    )

    if response.status_code == 200:
        user_info = response.json()
        return jsonify(user_info)
    else:
        return jsonify({"error": "Invalid or expired token"}), 401


# Endpoint to get the user's groups
@app.route("/api/groups", methods=["GET"])
def get_user_groups():
    token = request.headers.get("Authorization")

    # Check if the token is present in the request headers
    if token is None:
        return jsonify({"error": "Token not provided"}), 401

    # Get user information to retrieve the user ID (sub)
    user_info_response = requests.get(
        "http://localhost:8080/realms/master/protocol/openid-connect/userinfo",
        headers={"Authorization": token},
    )

    if user_info_response.status_code != 200:
        return jsonify({"error": "Invalid or expired token"}), 401

    user_info = user_info_response.json()
    user_id = user_info.get("sub")  # Extract the user ID (sub claim)

    # Make a request to Keycloak Admin API to get the user's groups
    admin_token = get_admin_token()
    if admin_token is None:
        return jsonify({"error": "Unable to retrieve admin token"}), 401

    response = requests.get(
        f"http://localhost:8080/admin/realms/master/users/{user_id}/groups",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    if response.status_code == 200:
        groups = response.json()
        return jsonify(groups), 200
    else:
        return (
            jsonify({"error": "Unable to retrieve user groups"}),
            response.status_code,
        )


# New Endpoint to List All Groups with IDs
@app.route("/api/list-groups", methods=["GET"])
def list_groups():
    admin_token = get_admin_token()

    if admin_token is None:
        return jsonify({"error": "Unable to retrieve admin token"}), 401

    response = requests.get(
        "http://localhost:8080/admin/realms/master/groups",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    if response.status_code == 200:
        groups = response.json()
        return jsonify(groups), 200
    else:
        return jsonify({"error": "Failed to retrieve groups"}), response.status_code


# New Endpoint to Create a User (POST)
@app.route("/api/users", methods=["POST"])
def create_user():
    data = request.json
    admin_token = get_admin_token()

    if admin_token is None:
        return jsonify({"error": "Unable to retrieve admin token"}), 401

    user_data = {
        "username": data.get("username"),
        "email": data.get("email"),
        "enabled": True,
        "credentials": [{"type": "password", "value": data.get("password")}],
    }

    response = requests.post(
        "http://localhost:8080/admin/realms/master/users",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=user_data,
    )

    if response.status_code == 201:
        return jsonify({"message": "User created successfully"}), 201
    else:
        return jsonify({"error": "Failed to create user"}), response.status_code


# New Endpoint to Delete a User (DELETE)
@app.route("/api/users/<user_id>", methods=["DELETE"])
def delete_user(user_id):
    admin_token = get_admin_token()

    if admin_token is None:
        return jsonify({"error": "Unable to retrieve admin token"}), 401

    response = requests.delete(
        f"http://localhost:8080/admin/realms/master/users/{user_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    if response.status_code == 204:
        return jsonify({"message": "User deleted successfully"}), 204
    else:
        return jsonify({"error": "Failed to delete user"}), response.status_code


# Endpoint to Update User Information (PUT)
@app.route("/api/users/<user_id>", methods=["PUT"])
def update_user(user_id):
    data = request.json
    admin_token = get_admin_token()

    if admin_token is None:
        return jsonify({"error": "Unable to retrieve admin token"}), 401

    response = requests.put(
        f"http://localhost:8080/admin/realms/master/users/{user_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=data,
    )

    if response.status_code == 204:
        return jsonify({"message": "User updated successfully"}), 204
    else:
        return jsonify({"error": "Failed to update user"}), response.status_code


# Endpoint to List All Users (GET)
@app.route("/api/users", methods=["GET"])
def list_users():
    admin_token = get_admin_token()

    if admin_token is None:
        return jsonify({"error": "Unable to retrieve admin token"}), 401

    response = requests.get(
        "http://localhost:8080/admin/realms/master/users",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    if response.status_code == 200:
        users = response.json()
        return jsonify(users), 200
    else:
        return jsonify({"error": "Failed to retrieve users"}), response.status_code


# Endpoint to Add User to a Group (PUT)
@app.route("/api/users/<user_id>/groups/<group_id>", methods=["PUT"])
def add_user_to_group(user_id, group_id):
    admin_token = get_admin_token()

    if admin_token is None:
        return jsonify({"error": "Unable to retrieve admin token"}), 401

    response = requests.put(
        f"http://localhost:8080/admin/realms/master/users/{user_id}/groups/{group_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    if response.status_code == 204:
        return jsonify({"message": "User added to group successfully"}), 204
    else:
        return jsonify({"error": "Failed to add user to group"}), response.status_code


# Function to obtain admin token
def get_admin_token():
    data = {
        "grant_type": "client_credentials",
        "client_id": "swagger-client",  # Ensure this matches Keycloak
        "client_secret": "7YZDkOP6dgwUvVekFJeUIVKzMZlCNF3v",  # Ensure this matches Keycloak client secret
    }
    response = requests.post(
        "http://localhost:8080/realms/master/protocol/openid-connect/token", data=data
    )
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        return None


# Public endpoint
@app.route("/api", methods=["GET"])
def public_endpoint():
    return jsonify({"message": "Welcome to the public API!"})


if __name__ == "__main__":
    app.run(port=5000, debug=True)
