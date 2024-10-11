# Real-Time Chat Application

![Chat Application Banner](https://via.placeholder.com/800x200.png?text=Real-Time+Chat+Application)

## 📌 Overview

This project is a robust real-time chat application built with Django Channels and PostgreSQL. It enables users to communicate instantaneously through one-on-one chats and group chat rooms. The application also features user notifications and an intuitive admin interface for efficient management of users and chat rooms.

## 📑 Table of Contents

- [Prerequisites](#-prerequisites)
- [Getting Started](#-getting-started)
- [Application Structure](#-application-structure)
- [API Endpoints](#-api-endpoints)
- [Environment Variables](#-environment-variables)
- [Additional Notes](#-additional-notes)
- [License](#-license)

## 🛠 Prerequisites

Ensure you have the following installed before proceeding:

- **Docker**: [Install Docker](https://docs.docker.com/get-docker/)
- **Docker Compose**: [Install Docker Compose](https://docs.docker.com/compose/install/)

## 🚀 Getting Started

Follow these steps to set up and run the application locally.

### 1. Clone the Repository

```bash
git clone https://your-repo-url.git
cd your-repo-name
```

### 2. Dockerizing and Running the Application

Before running the scripts, enable access for the scripts to run in the terminal:

```bash
chmod +x ./scripts/*.sh
```

#### Build the Image

```bash
./scripts/build.sh
```

#### Migrate the Database

When running for the first time, make migrations first:

```bash
./scripts/migrate.sh
```

#### Start the Application

```bash
./scripts/run.sh
```

The application will be accessible at:

- Web Application: [http://localhost:8000](http://localhost:8000)
- Admin Interface: [http://localhost:8001/admin](http://localhost:8001/admin)

## 🏗 Application Structure

### Services

The application is structured using Docker services as follows:

- **web**: Runs the main application using Daphne (Port 8000)
- **admin**: Hosts the Django admin interface (Port 8001)
- **db**: Uses PostgreSQL as the database with persistent storage

### Volumes

- **postgres_data**: A Docker volume providing persistent storage for the PostgreSQL database

## 🌐 WebSocket Routing

The real-time chat functionality is powered by Django Channels, which uses WebSockets to enable bi-directional communication between the client and the server.

Routing Configuration
The WebSocket routing is defined in the routing.py file:
  ```python
  from django.urls import re_path
  from chatrooms.consumer import ChatConsumer
  
  websocket_urlpatterns = [
      re_path(r'ws/chat/(?P<room_name>\w+)/$', ChatConsumer.as_asgi()),
  ]
  ```
 - **Endpoint**: ws/chat/<room_name>/

  #### Description: 
  - Establishes a WebSocket connection for a specific chat room identified by <room_name>.
  - Consumer: ChatConsumer handles the WebSocket events for sending and receiving messages.
  
  #### How It Works
  When a user navigates to a chat room, the client establishes a WebSocket connection to the server using the URL pattern defined above.
  The ChatConsumer listens for incoming WebSocket connections and handles messages sent over the WebSocket.
  Messages sent by users are broadcasted in real-time to all participants in the chat room.
  Additional Configuration
  Ensure that the routing is properly included in your project's ASGI application. In your asgi.py file, you should include:

  ```python
  import os
  import django
  from channels.routing import ProtocolTypeRouter, URLRouter
  from channels.auth import AuthMiddlewareStack
  from chatrooms.routing import websocket_urlpatterns
  
  os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatapp.settings')
  django.setup()
  
  application = ProtocolTypeRouter({
      'websocket': AuthMiddlewareStack(
          URLRouter(
              websocket_urlpatterns
          )
      ),
  })
  ```

## 🔗 API Endpoints

### User Authentication

| Endpoint | Method | Description | Request Body |
|----------|--------|-------------|--------------|
| `/api/register/` | POST | Register a new user | `{ "username": "string", "password": "string", "email": "string" }` |
| `/api/login/` | POST | Log in an existing user | `{ "username": "string", "password": "string" }` |
| `/api/logout/` | POST | Log out the authenticated user | N/A |

### Chat Rooms

| Endpoint | Method | Description | Request Body |
|----------|--------|-------------|--------------|
| `/api/rooms/` | POST | Create a new chat room | `{ "title": "string", "description": "string" }` |
| `/api/rooms/` | GET | Retrieve a list of chat rooms | N/A |
| `/api/rooms/<room_id>/` | GET | Retrieve details of a specific chat room | N/A |

### Messaging

| Endpoint | Method | Description | Request Body |
|----------|--------|-------------|--------------|
| `/api/messages/` | POST | Send a message to a chat room | `{ "room_id": "int", "message": "string" }` |
| `/api/messages/<room_id>/` | GET | Retrieve messages from a chat room | N/A |

## 🔐 Environment Variables

Ensure to set the following environment variables in your `.env` file or Docker environment:

- `DJANGO_SETTINGS_MODULE`: Specify your Django settings module (e.g., `chatapp.settings`)
- Database settings:
  - `POSTGRES_DB`: Database name (e.g., `quick_connect`)
  - `POSTGRES_USER`: PostgreSQL user (default: `postgres`)
  - `POSTGRES_PASSWORD`: PostgreSQL password (default: `postgres`)

## 📝 Additional Notes

- Ensure that your Docker daemon is running before executing the commands.
- You can modify the PostgreSQL credentials in `docker-compose.yml` as needed.
- The application requires certain dependencies specified in `requirements.txt`. Make sure to install them if you are running the application outside of Docker.

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

For more information or support, please [open an issue](https://your-repo-url/issues) or contact our support team.

