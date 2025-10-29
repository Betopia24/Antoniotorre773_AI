# RGB to CMYK Converter

A FastAPI application that converts uploaded RGB images to CMYK TIFF files with color profile support.

## Quick start (PowerShell on Windows)

1. Install dependencies:

```powershell
pip install -r requirements.txt
```

2. Run the API server:

```powershell
python -m uvicorn main:app --host 0.0.0.0 --port 8045
```

- API root: http://134.199.198.12:8045
- Interactive docs: http://134.199.198.12:8045/docs

## API Endpoints

The service provides the following endpoints:

- `POST /convert-to-cmyk/`: Upload an image file to convert from RGB to CMYK
- `GET /download/{image_id}`: Download a converted CMYK TIFF file
- `GET /view/{image_id}`: View a converted image in the browser

## Using the Python Client

```powershell
# Basic usage (uses default server at 134.199.198.12:8045)
python client.py path/to/image.png

# Specify output file
python client.py path/to/image.png --output converted.tiff

# Use a different server URL
python client.py path/to/image.png --url http://localhost:8045
```

## Features

- RGB to CMYK conversion with ICC profile support
- Browser-viewable converted images
- API for programmatic access
- Docker containerization

## Docker Support

### Using Docker Compose (Recommended)

1. Build and start the container:

```powershell
docker-compose up -d
```

2. The API will be available at: http://134.199.198.12:8045

3. Stop the container:

```powershell
docker-compose down
```

## Response Format

When converting an image, the API returns a JSON response:

```json
{
  "image_id": "7d2bd273-cbae-41cb-892d-79f0dca7725f",
  "download_url": "http://134.199.198.12:8045/download/7d2bd273-cbae-41cb-892d-79f0dca7725f",
  "view_url": "http://134.199.198.12:8045/view/7d2bd273-cbae-41cb-892d-79f0dca7725f"
}
```

- `image_id`: Unique identifier for the converted image
- `download_url`: URL to download the converted CMYK TIFF file
- `view_url`: URL to view the converted image in a web browser

## Project Structure

- `main.py` - FastAPI application
- `client.py` - Python client for the API
- `docker-compose.yml` - Docker Compose configuration
- `Dockerfile` - Docker container configuration
- `requirements.txt` - Python dependencies
- `icc/` - ICC color profiles for conversion
- `converted_images/` - Storage for converted CMYK images
- `uploads/` - Temporary storage for uploaded images