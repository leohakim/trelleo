# Trelleo - Django Trello-like Board

A Trello-like board application built with Django, Tailwind CSS, and HTMX for managing web apps, SaaS, and microSaaS projects.

## Features

- Create and manage multiple boards
- Add, edit, and delete lists within boards
- Create, edit, and move cards between lists
- Assign labels, due dates, and members to cards
- Drag and drop interface for easy organization
- Minimal JavaScript dependencies
- Modern UI with Shadcn-inspired components

## Requirements

- Python 3.8+
- Django 5.1+
- Node.js and npm (for Tailwind CSS)

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   ```
3. Activate the virtual environment:
   - On Windows: `venv\Scripts\activate`
   - On macOS/Linux: `source venv/bin/activate`
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Set up environment variables by creating a `.env` file in the project root:
   ```
   DEBUG=True
   SECRET_KEY=your-secret-key
   DATABASE_URL=sqlite:///db.sqlite3
   ```
6. Run migrations:
   ```
   python manage.py migrate
   ```
7. Create a superuser:
   ```
   python manage.py createsuperuser
   ```
8. Install Tailwind CSS:
   ```
   python manage.py tailwind install
   ```
9. Start the Tailwind CSS build process:
   ```
   python manage.py tailwind start
   ```
10. In a separate terminal, run the Django development server:
    ```
    python manage.py runserver
    ```

## Deployment

1. Set `DEBUG=False` in your `.env` file
2. Configure your production database in the `.env` file
3. Collect static files:
   ```
   python manage.py collectstatic
   ```
4. Use Gunicorn to serve the application:
   ```
   gunicorn trelleo.wsgi
   ```

## Extending the Application

The application is designed to be easily extendable:

- Add new models in the appropriate app directories
- Create new views and templates following the existing patterns
- Extend the UI components by adding new Tailwind CSS classes
- Use HTMX for interactive features with minimal JavaScript

## License

MIT
