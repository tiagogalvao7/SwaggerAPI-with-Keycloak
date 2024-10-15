# Keycloak Swagger API

This project is a **REST API** that integrates **Keycloak** with **Swagger** to manage user, group, and permission authentication and authorization. The API is built using **Flask** and exposes endpoints for Keycloak administration operations, such as creating users, managing groups, and assigning users to groups.

## Features

- **Authentication** via **Keycloak** to protect the API endpoints.
- **User Management**:
  - Create, list, update, and delete users.
- **Group Management**:
  - List all groups and their respective IDs.
  - Add users to groups.
- **Swagger UI** integration for API documentation and testing.

## Key Endpoints

- `GET /userinfo`: Returns authenticated user information.
- `POST /users`: Creates a new user.
- `PUT /users/{user_id}`: Updates user information.
- `DELETE /users/{user_id}`: Deletes a user.
- `GET /list-groups`: Lists all groups with their IDs.
- `PUT /users/{user_id}/groups/{group_id}`: Adds a user to a group.

## Technologies Used

- **Flask**: Python web framework.
- **Keycloak**: Identity and access management system.
- **Swagger UI**: Interface for API documentation and testing.
- **PostgreSQL**: Database used by Keycloak.

## How to Run

1. **Clone the repository**:

   ```bash
   git clone <REPOSITORY_URL>
   ```

2. **Start Keycloak and PostgreSQL Docker containers**:

   ```bash
   docker-compose up -d
   ```

3. **Run the Flask API**:

   ```bash
   python app.py
   ```

4. **Access the API documentation via Swagger**:

   Open your browser and go to:

   ```bash
   http://localhost:5000/swagger
   ```
