# Extended Lactation Dashboard

## Local Development

This guide provides instructions for running the application locally with hot reloading.

### Prerequisites

1. **Python Environment Setup**
   ```bash
   # Create and activate virtual environment (optional but recommended)
   python -m venv venv
   source venv/bin/activate  # Unix/Mac
   # or
   .\venv\Scripts\activate  # Windows

   # Install Python dependencies
   cd backend
   pip install -r requirements.txt
   ```

2. **Node.js Environment Setup**
   ```bash
   # Install Node.js dependencies
   cd frontend
   npm install
   ```

### Running the Application
The backend requires a .env file to define environment variables. It will use a .sqlite3 database.

1. **Start the Backend Server**
   ```bash
   cd backend
      
   # Run Django development server
   gunicorn backend.wsgi:application --bind 0.0.0.0:8000 --reload
   ```

2. **Start the Frontend Server**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Access the Application**
   - Frontend: http://localhost:5173
   - Django Admin: http://localhost:8000/admin

## Docker Development Environment

This guide provides instructions for setting up and running the development environment using Docker.

### Prerequisites

1. **Install Docker Desktop**
   - Download Docker Desktop for your OS:
     - [Windows](https://docs.docker.com/desktop/install/windows-install/)
     - [Mac](https://docs.docker.com/desktop/install/mac-install/)
     - [Linux](https://docs.docker.com/desktop/setup/install/linux/)
   - Follow the installation instructions for your system
   - Start Docker Desktop
   - Verify installation by running: `docker --version`

### Running Development Version

1. **Navigate to project directory**
   ```bash
   cd extended-lactation-dashboard
   ```

2. **Build and start the containers**
   ```bash
   # Build and start all services
   docker compose up --build
   ```

### Accessing the Applications
- Frontend: http://localhost:3000
- Django Admin: http://localhost:8000/admin

### Accessing Django Admin
Django admin can be used to view the database tables and add/remove/edit data.

1. **Create a superuser account**
   ```bash
   # In a new terminal window
   docker compose exec backend python manage.py createsuperuser
   ```

2. **Access the admin interface**
   - Open http://localhost:8000/admin in your browser
   - Log in with your superuser credentials
