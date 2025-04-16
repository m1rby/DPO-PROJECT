# Art Marketplace

A modern web platform for buying and selling unique artworks. This Django-based application provides a centralized place for artists to showcase and sell their work, and for art enthusiasts to discover and purchase beautiful pieces.

## Features

- User authentication and registration
- Artist profiles with portfolio management
- Artwork listing and management
- Shopping cart functionality
- Secure checkout process
- Order tracking
- Search and filtering capabilities
- Responsive design
- Modern and clean UI

## Technology Stack

- Django 5.0.2
- Bootstrap 5
- SQLite (development)
- Pillow (image processing)
- django-crispy-forms
- django-allauth

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd art_marketplace
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

## Project Structure

```
art_marketplace/
├── art_marketplace/          # Project settings
├── marketplace/             # Main application
│   ├── migrations/          # Database migrations
│   ├── static/             # Static files
│   ├── templates/          # HTML templates
│   ├── models.py           # Database models
│   ├── views.py            # View functions
│   ├── forms.py            # Form definitions
│   └── urls.py             # URL patterns
├── media/                  # User-uploaded files
├── static/                 # Static files
├── templates/              # Base templates
└── requirements.txt        # Project dependencies
```

## Usage

1. Access the admin panel at `/admin` to manage users and artworks
2. Register as an artist to start selling your work
3. Browse artworks on the home page
4. Add items to cart and proceed to checkout
5. Track your orders in the profile section

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For any questions or suggestions, please open an issue in the repository. 