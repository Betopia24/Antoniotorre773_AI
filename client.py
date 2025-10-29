#!/usr/bin/env python
"""
RGB to CMYK Converter API Client

This script uploads an image to the RGB to CMYK Converter API and downloads the converted CMYK TIFF file.
"""

import os
import sys
import requests
import argparse
from urllib.parse import urljoin

def convert_image(api_url, image_path, output_path=None):
    """
    Convert an RGB image to CMYK using the API
    
    Args:
        api_url (str): Base URL of the API (e.g. http://localhost:8045)
        image_path (str): Path to the image file
        output_path (str, optional): Path to save the converted file
    
    Returns:
        str: Path to the saved CMYK file
    """
    # Check if file exists
    if not os.path.exists(image_path):
        print(f"Error: File {image_path} not found.")
        return None
    
    # Extract filename if output_path is not provided
    if not output_path:
        filename = os.path.basename(image_path)
        name, _ = os.path.splitext(filename)
        output_path = f"{name}_cmyk.tiff"
    
    # Prepare the file for upload
    files = {"file": (os.path.basename(image_path), open(image_path, "rb"), "image/png")}
    
    try:
        # Make POST request to convert endpoint
        print(f"Uploading {image_path}...")
        convert_url = urljoin(api_url, "convert-to-cmyk/")
        response = requests.post(convert_url, files=files)
        
        # Check if the request was successful
        response.raise_for_status()
        result = response.json()
        
        # Get the download URL
        if "download_url" in result:
            download_url = result["download_url"]
            
            # If URL doesn't start with http, make it absolute
            if not download_url.startswith(('http://', 'https://')):
                download_url = urljoin(api_url, download_url)
                
            print(f"Downloading from: {download_url}")
            
            # Download the converted file
            download_response = requests.get(download_url)
            download_response.raise_for_status()
            
            # Save the file
            with open(output_path, "wb") as f:
                f.write(download_response.content)
                
            print(f"Saved CMYK file to: {output_path}")
            return output_path
        else:
            print("Error: No download URL in response")
            print(f"Response: {result}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error communicating with API: {e}")
        if hasattr(e, 'response') and e.response:
            try:
                error_detail = e.response.json()
                print(f"API Error: {error_detail}")
            except:
                print(f"Status Code: {e.response.status_code}")
                print(f"Response: {e.response.text}")
        return None
    finally:
        # Close the file
        files["file"][1].close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert RGB images to CMYK using the API")
    parser.add_argument("image", help="Path to the image file")
    parser.add_argument("--output", "-o", help="Path to save the converted file")
    parser.add_argument("--url", default="http://134.199.198.12:8045", help="API URL (default: http://134.199.198.12:8045)")
    
    args = parser.parse_args()
    
    convert_image(args.url, args.image, args.output)