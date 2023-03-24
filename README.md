# Fly Messenger API

This is the API for the Fly Messenger app. It is a REST API built with Python and FastAPI framework.

## Table Of Contents

<!-- TOC -->

* [Getting Started](#getting-started)
    * [Prerequisites](#prerequisites)
    * [Installing](#installing)
    * [Running the API](#running-the-api)
* [API](#api)
    * [Authentication](#authentication)
    * [Users](#users)
    * [Dialogs](#dialogs)
    * [Search](#search)
* [Testing](#testing)
* [Technologies](#technologies)
* [Authors](#authors)
* [License](#license)

<!-- TOC -->

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing
purposes.

### Prerequisites

You will need to have `Python 3.7` or later installed and `MongoDB` installed and running. You can install **MongoDB
locally**
or use **MongoDB Atlas**.

### Installing

1. First, clone the repository to your local machine:

```bash
git clone https://github.com/Real-Time-Messenger/FlyMessenger-server.git
```

2. Next, navigate to the project directory and create a virtual environment:

```bash
cd FlyMessenger-server
python -m venv venv
```

3. Activate the virtual environment:

```bash
# Windows
venv\Scripts\activate

# Linux
source venv/bin/activate
```

4. Install the required dependencies:

```bash
pip install -r requirements.txt
```

5. Open the `.env.sample` file and fill in the required fields
6. Rename the `.env.sample` file to `.env`

### Running the API

To start the API, run the following command:

```bash
uvicorn app.main:app --reload 
```

The API will now be running at `http://localhost:8000`. You can use a tool like Postman to send requests to the API.

## API

The API is documented using Swagger UI. You can access the documentation at `http://localhost:8000/docs`.

**NOTE:** All requests URL should be prefixed with `/api`.

### Authentication

| Endpoint                          | Method | Description                                        |
|-----------------------------------|--------|----------------------------------------------------|
| `/auth/login`                     | `POST` | Login a user                                       |
| `/auth/signup`                    | `POST` | Register a user                                    |
| `/auth/logout`                    | `POST` | Logout a user                                      |
| `/auth/activate`                  | `POST` | Activate a user                                    |
| `/auth/call-reset-password`       | `POST` | Send a password reset email                        |
| `/auth/validation-reset-password` | `POST` | Validate a password reset token                    |
| `/auth/reset-password`            | `POST` | Reset a user's password                            |
| `/auth/two-factor`                | `POST` | Authenticate a user with two-factor authentication |
| `/auth/new-device`                | `POST` | Authenticate a user with a new device              |

### Users

| Endpoint                  | Method   | Description                          |
|---------------------------|----------|--------------------------------------|
| `/users/me`               | `GET`    | Get the current user                 |
| `/users/me/sessions`      | `GET`    | Get the current user's sessions      |
| `/users/me/blocked-users` | `GET`    | Get the current user's blocked users |
| `/users/me/blacklist`     | `POST`   | Block or unblock a user              |
| `/users/me`               | `PUT`    | Update the current user              |
| `/users/me/avatar`        | `PUT`    | Update the current user's avatar     |
| `/users/me`               | `DELETE` | Delete the current user              |

### Dialogs

| Endpoint                       | Method   | Description                    |
|--------------------------------|----------|--------------------------------|
| `/dialogs/me`                  | `GET`    | Get the current user's dialogs |
| `/dialogs/{dialogId}/messages` | `GET`    | Get a dialog's messages        |
| `/dialogs`                     | `POST`   | Create a new dialog            |
| `/dialogs/{dialogId}`          | `PUT`    | Update a dialog                |
| `/dialogs/{dialogId}`          | `DELETE` | Delete a dialog                |

### Search

| Endpoint                     | Method | Description                                  |
|------------------------------|--------|----------------------------------------------|
| `/search/{query}`            | `GET`  | Search users, dialogs, and messages by query |
| `/search/{dialogId}/{query}` | `GET`  | Search messages by query in a dialog         |

## Testing

To run the tests, run the following command:

```bash
pytest
```

## Technologies

- **[Python](https://www.python.org/)**: This RESTAPI is built using Python 3.7 or later.
- **[FastAPI](https://fastapi.tiangolo.com/)**: FastAPI is a modern, fast (high-performance), web framework for building APIs with Python 3.7+ based on standard Python type hints.
- **[UVICORN](https://www.uvicorn.org/)**: UVICORN is a lightning-fast ASGI server implementation, using uvloop and httptools. It is used to run the API in development.
- **[MongoDB](https://www.mongodb.com/)**: MongoDB is a cross-platform document-oriented database program. It is used to store the data for this RESTAPI.
- **[Motor](https://motor.readthedocs.io/)**: Motor is a Python asyncio library for MongoDB. It is used as an ORM (Object-Relational Mapper) to query the MongoDB database in this RESTAPI.
- **[Pydantic](https://pydantic-docs.helpmanual.io/)**: Pydantic is a library for data validation and error handling. It is used to define the models and schemas for the API endpoints.
- **[Pytest](https://docs.pytest.org/en/stable/)**: Pytest is a testing framework for Python. It is used to write and run tests for the RESTAPI.

## Authors

- **[Kirill Goritski](https://t.me/winicred)**
- **[Vladislav Hodzajev](https://t.me/white_wolf_dd)**

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details