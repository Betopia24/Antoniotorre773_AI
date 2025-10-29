from fastapi import FastAPI, UploadFile, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import io
import os
import tempfile
import uuid

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Ensure output directory exists
UPLOAD_DIR = "uploads"
OUTPUT_DIR = "converted_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Mount the converted_images directory to serve files statically
app.mount("/view-images", StaticFiles(directory=OUTPUT_DIR), name="view-images")


@app.get("/")
async def root():
    return {"message": "Welcome to the RGB to CMYK Converter API. Use the /convert-to-cmyk/ endpoint to convert images."}


@app.post("/convert-to-cmyk/")
async def convert_to_cmyk(request: Request, file: UploadFile):
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    # Generate a unique id and file paths
    image_id = str(uuid.uuid4())
    original_filename = f"{image_id}_{file.filename}"
    output_filename = f"{image_id}_cmyk.tiff"
    input_path = os.path.join(UPLOAD_DIR, original_filename)
    output_path = os.path.join(OUTPUT_DIR, output_filename)

    try:
        # Save uploaded file to disk
        with open(input_path, "wb") as f:
            f.write(await file.read())

        # Open the image
        image = Image.open(input_path)
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Convert to CMYK and save
        cmyk_image = image.convert("CMYK")
        cmyk_image.save(output_path, format="TIFF")

        # Build download and view URLs
        download_url = str(request.url_for("download_file", image_id=image_id))
        
        # Create a view URL for browser display
        base_url = str(request.base_url)
        view_url = str(request.url_for("view_file", image_id=image_id))

        return JSONResponse(status_code=200, content={
            "image_id": image_id,
            "download_url": download_url,
            "view_url": view_url
        })

    except Exception as e:
        # Cleanup on error
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")


@app.get("/download/{image_id}", name="download_file")
async def download_file(image_id: str):
    # Find the converted file in OUTPUT_DIR
    for filename in os.listdir(OUTPUT_DIR):
        if filename.startswith(image_id) and (filename.lower().endswith(".tif") or filename.lower().endswith(".tiff")):
            path = os.path.join(OUTPUT_DIR, filename)
            return FileResponse(
                path, 
                media_type="image/tiff", 
                filename=filename,
                # This header forces download
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
    raise HTTPException(status_code=404, detail="File not found")


@app.get("/view/{image_id}", name="view_file")
async def view_file(image_id: str):
    # Find the converted file in OUTPUT_DIR
    for filename in os.listdir(OUTPUT_DIR):
        if filename.startswith(image_id) and (filename.lower().endswith(".tif") or filename.lower().endswith(".tiff")):
            path = os.path.join(OUTPUT_DIR, filename)
            
            # Convert TIFF to a more browser-friendly format (JPEG)
            try:
                with Image.open(path) as img:
                    # Create a temporary buffer for the converted image
                    buffer = io.BytesIO()
                    # Convert to RGB if it's CMYK
                    if img.mode == "CMYK":
                        img = img.convert("RGB")
                    # Save as JPEG for browser viewing
                    img.save(buffer, format="JPEG", quality=90)
                    buffer.seek(0)
                    
                    # Return the image with inline Content-Disposition to show in browser
                    return Response(
                        content=buffer.getvalue(),
                        media_type="image/jpeg",
                        headers={"Content-Disposition": f"inline; filename={filename.replace('.tiff', '.jpg').replace('.tif', '.jpg')}"}
                    )
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error converting image for viewing: {str(e)}")
                
    raise HTTPException(status_code=404, detail="File not found")