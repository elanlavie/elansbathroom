# Classroom Bathroom Queue System

## Overview

This is a Flask-based web application designed to manage a classroom bathroom queue system. The application allows students to join a queue for bathroom usage, displays the current queue status, and manages a maximum capacity of 3 students in the queue at any time.

## System Architecture

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Flask
- **UI Framework**: Bootstrap 5 with dark theme
- **Icons**: Bootstrap Icons
- **Responsive Design**: Mobile-first approach with Bootstrap grid system

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **ORM**: SQLAlchemy with Flask-SQLAlchemy extension
- **Database**: SQLite (development) with PostgreSQL support (production)
- **WSGI Server**: Gunicorn for production deployment
- **Session Management**: Flask sessions with configurable secret key

### Application Structure
```
├── main.py          # Application entry point
├── app.py           # Flask application factory and configuration
├── models.py        # Database models
└── templates/       # Jinja2 templates
    ├── base.html    # Base template with navigation and layout
    └── index.html   # Main queue display and join form
```

## Key Components

### Database Models
- **QueueEntry**: Represents a student in the bathroom queue
  - `id`: Primary key
  - `student_name`: Student's name (max 50 characters)
  - `joined_at`: Timestamp when student joined queue
  - Includes position calculation method

### Core Features
- **Queue Management**: FIFO queue with 3-person maximum capacity
- **Real-time Status**: Display current queue with positions and join times
- **Form Validation**: Student name validation and duplicate prevention
- **Flash Messaging**: User feedback for actions and errors

### User Interface
- **Queue Display**: Shows current students with their positions and join times
- **Join Form**: Allows new students to join the queue
- **Status Indicators**: Visual feedback for queue availability vs full capacity
- **Responsive Design**: Works on desktop and mobile devices

## Data Flow

1. **Queue Joining**: Student submits name → validation → database insertion → redirect with confirmation
2. **Queue Display**: Database query → template rendering → browser display
3. **Queue Management**: Automatic position calculation based on join timestamps
4. **Status Updates**: Real-time queue count and availability status

## External Dependencies

### Python Packages
- `flask`: Web framework
- `flask-sqlalchemy`: Database ORM
- `gunicorn`: WSGI HTTP server
- `psycopg2-binary`: PostgreSQL adapter
- `email-validator`: Email validation support
- `werkzeug`: WSGI utilities and proxy fix

### Frontend Dependencies (CDN)
- Bootstrap 5 CSS with dark theme
- Bootstrap Icons
- Bootstrap JavaScript (implied for dismissible alerts)

## Deployment Strategy

### Environment Configuration
- **Development**: SQLite database with Flask dev server
- **Production**: PostgreSQL with Gunicorn on Replit's autoscale platform
- **Environment Variables**:
  - `DATABASE_URL`: Database connection string
  - `SESSION_SECRET`: Flask session encryption key

### Replit Configuration
- **Runtime**: Python 3.11 with Nix package management
- **Packages**: OpenSSL and PostgreSQL system packages
- **Deployment**: Autoscale target with Gunicorn binding to 0.0.0.0:5000
- **Workflows**: Parallel execution with hot reload in development

### Security Considerations
- Proxy fix middleware for proper header handling
- Configurable session secret
- SQL injection protection via SQLAlchemy ORM
- Input validation for student names

## Changelog
- June 18, 2025. Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.