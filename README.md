# AI Career Advisor: How to use the Docker Images

This project consists of two Docker containers:

1. A PostgreSQL database preconfigured with pgvector and data.
2. A Streamlit application that interacts with the database.

Follow the steps below to set up and run the project.

---

## Prerequisites

Before starting, ensure the following are installed on your system:

- **Docker**:
  - For Windows/Mac: Install Docker Desktop.
  - For Linux: Refer to the [Docker Installation Guide](https://docs.docker.com/get-docker/).
- The `.tar` files for the Docker images (can be found in docker_images):
  - `my_pgvector_with_data.tar` (Database image)
  - `streamlit_app.tar` (Streamlit app image)

---

## Step 1: Set Up and Run the PostgreSQL Database

### 1. Load the Docker Image
Run the following command to load the database Docker image:
```bash
docker load < my_pgvector_with_data.tar
```

### 2. Create a Docker Network
Create a custom network to allow the containers to communicate:
```bash
docker network create app_network
```

### 3. Run the Database Container
Start the database container with:
```bash
docker run -d --name vector_db_instance --network app_network -p 5433:5432 my_pgvector_with_data
```

#### Options Explained:
- `-d`: Runs the container in detached mode.
- `--name vector_db_instance`: Assigns a name to the container.
- `--network app_network`: Connects the container to the custom Docker network.
- `-p 5433:5432`: Maps port 5433 on your machine to port 5432 inside the container.

### 4. Access the Database
The database is now running and accessible with the following details:

- **Host**: `localhost`
- **Port**: `5433`
- **Database Name**: `vector_db`
- **Username**: `postgres`
- **Password**: `test`

You can connect using a PostgreSQL client like `psql` or `pgAdmin`, or directly from the Streamlit application.

---

## Step 2: Set Up and Run the Streamlit Application

### 1. Load the Docker Image
Run the following command to load the Streamlit Docker image:
```bash
docker load < streamlit_app.tar
```

### 2. Run the Application Container
Start the Streamlit application with:
```bash
docker run -d --name streamlit_app_instance --network app_network -p 8501:8501 streamlit_app
```

#### Options Explained:
- `-d`: Runs the container in detached mode.
- `--name streamlit_app_instance`: Assigns a name to the container.
- `--network app_network`: Connects the container to the custom Docker network.
- `-p 8501:8501`: Maps port 8501 on your machine to port 8501 inside the container.

### 3. Access the Application
Open your browser and navigate to:
```
http://localhost:8501
```
The Streamlit application will load and display its interface.

---

## Application Details

### Database Connection
The Streamlit application is preconfigured to connect to the database using the following connection string:
```bash
postgresql+psycopg2://postgres:test@vector_db_instance:5432/vector_db
```
Ensure the database container (`vector_db_instance`) is running before starting the Streamlit application.

---

## Troubleshooting

### Verify Running Containers
Use the command below to list running containers:
```bash
docker ps
```

### Restart a Stopped Container
If a container is not running, start it with:
```bash
docker start CONTAINER_NAME_OR_ID
```

### Check Logs
To view logs for any container, use:
```bash
docker logs CONTAINER_NAME_OR_ID
```

---

Now you're ready to run both the database and the Streamlit application seamlessly! If you face any issues, feel free to contact us at mmc55@mail.aub.edu

