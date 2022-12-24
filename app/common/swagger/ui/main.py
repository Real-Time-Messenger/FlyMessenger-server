from app.common.swagger.ui.tags import tags_metadata

description = """
# API Documentation

## Features
### User
**OAuth2**
* We have an OAuth2 system that allows (in our case) a remote client (which is located on a different domain) to log in to our API. We do not want to use authorization through third-party applications, as we believe that this kind of application should have its own precise and strong authentication.

**Sessions**
* Our entire system is built on the technology of token sessions. That is, if a user is authorized in our client application (web client or desktop client), then his session token is stored in our database. This token can be used within a month, after which, the user needs to log in again. Also, the user has **IMMEDIATELY** the opportunity to delete his session on another device.\n
**Note:** _Without this confirmation, the user will **not be able** to use the site and log in._

### Messaging
**Real-time messaging**
* Our entire communication system between users is based on WebSockets. Each authorized user contacts our websocket and then connects to it.\n
**Note:** _If the user is not authorized, he will not be able to connect to the websocket._

**Message sending**
* The user can chat with registered people. They can be found through the search. When sending a message, the user with whom the dialogue is being conducted will be notified of a new message.\n
**Note:** _User can only delete dialogs._

## Websocket
**Websocket allows the user to:**
* Send a message
* Read messages
* Receive new message notifications from the user
* Delete recent user sessions

## Links
* [GitHub](https://github.com/Real-Time-Messenger/FlyMessenger-server) - Our GitHub repository
"""

# Override the default FastAPI OpenAPI(swagger) schema.
swagger_obj = {
    "title": "Fly Messegner API",
    "description": description,
    "version": "0.1.0",
    "license": {
        "name": "MIT",
    },
    "info": {
        "x-logo": {
            "url": "http://locahost:8000/public/logo.png",
        }
    },
    "servers": [
        {
            "url": "http://localhost:8000",
            "description": "Local server",
        }
    ],
    "openapi_tags": tags_metadata,
    "swagger_ui_parameters": {"operationsSorter": "method"},
}
