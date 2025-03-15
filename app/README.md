# Running the FastAPI Application

This application can be run in several ways, depending on your needs and from which directory you wish to start it.

## Option 1: Run from the parent directory (recommended)

```bash
cd ..  # Go to the parent directory if you're in the app directory
python run.py
```

## Option 2: Run from the app directory

### Using the start.py script (recommended)
```bash
# From within the app directory
python start.py
```

### Using app_runner.py
```bash
# From within the app directory
python app_runner.py
```

### Using uvicorn directly
```bash
# From within the app directory
python -m uvicorn main:app --reload
```

## Troubleshooting

If you're getting `ModuleNotFoundError: No module named 'app'` or similar import errors:

1. Make sure you're using the correct command for your current directory
2. Try using one of the runner scripts instead of direct uvicorn commands
3. If running from the app directory, use `main:app` instead of `app.main:app`

## Development Notes

The application structure uses relative imports, so the way you run it affects how Python resolves these imports. 
The provided scripts adjust the Python path as needed to ensure modules can be found regardless of where 
you run the application from. 