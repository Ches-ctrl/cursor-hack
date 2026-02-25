# Big Tony Landing Page

This is the landing page for the Big Tony bot, Unicorn Mafia's community bot.

## Features

- Clean, minimal design with gradient background
- WhatsApp button that redirects to Big Tony bot: `https://wa.me/447488895960?text=i've got what it takes`
- Wassist branding (powered by [Wassist](https://wassist.app))
- Credits to Josh Warwick for development
- Fully responsive design

## Running the Application

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running Locally

Start the Flask server:
```bash
python app.py
```

The application will be available at:
- Homepage: `http://localhost:5000/`
- Big Tony page: `http://localhost:5000/bt`

### Deployment

The Flask application can be deployed to various platforms:

- **Heroku**: Use a `Procfile` with `web: gunicorn app:app`
- **Render**: Point to `app.py` as the entry point
- **Railway**: Auto-detects Flask applications
- **PythonAnywhere**: Upload files and configure WSGI

For production deployment, consider using `gunicorn`:
```bash
pip install gunicorn
gunicorn app:app
```

## Page Structure

The `/bt` page includes:
- Big Tony logo (BT initials)
- Welcome message
- WhatsApp contact button
- Wassist attribution
- Developer credits (Josh Warwick)

## Design

The page features:
- Purple gradient background (#667eea to #764ba2)
- Modern card-based layout
- Hover effects on the WhatsApp button
- Mobile-responsive design
- Clean typography using system fonts
