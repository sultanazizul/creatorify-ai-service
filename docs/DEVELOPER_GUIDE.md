# Developer Guide

## Setting Up Development Environment

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Secrets**:
   Ensure you have the necessary secrets in `.env` or Modal secrets:
   - `SUPABASE_URL`, `SUPABASE_KEY`
   - `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET`

## Adding a New AI Model

To add a new AI model (e.g., a new Image Generator):

1.  **Define the Service**:
    Create a new service class in `services/image/` that handles the model inference.
    ```python
    # services/image/generator.py
    class ImageGenerator:
        def generate(self, prompt: str):
            # Model logic here
            pass
    ```

2.  **Create Router**:
    Create a FastAPI router in `api/v1/routers/image.py`.
    ```python
    from fastapi import APIRouter
    from services.image.generator import ImageGenerator

    router = APIRouter()

    @router.post("/generate")
    def generate_image(prompt: str):
        service = ImageGenerator()
        return service.generate(prompt)
    ```

3.  **Register Router**:
    Add the router to `app.py`.
    ```python
    from api.v1.routers import image
    # ...
    web_app.include_router(image.router, prefix="/api/v1/image", tags=["image"])
    ```

4.  **Update Dependencies**:
    If the model requires new Python packages, add them to `image` definition in `app.py`.

## Testing

- Run unit tests (if available).
- Use `modal serve app.py` to test the API interactively.
