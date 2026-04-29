"""Model configuration API routes."""

from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.models.model_config import ModelParameters
from backend.services.config.model_manager import ModelConfigManager

router = APIRouter(prefix="/api/models", tags=["models"])

# Global manager instance
_model_manager: ModelConfigManager = None


def init_model_routes(model_manager: ModelConfigManager):
    """Initialize model routes with manager."""
    global _model_manager
    _model_manager = model_manager


class CreateModelRequest(BaseModel):
    """Request to create a model configuration."""
    name: str
    api_base: str
    api_key: str
    model_name: str
    parameters: Optional[ModelParameters] = None
    is_default: bool = False


class UpdateModelRequest(BaseModel):
    """Request to update a model configuration."""
    name: Optional[str] = None
    api_base: Optional[str] = None
    api_key: Optional[str] = None
    model_name: Optional[str] = None
    parameters: Optional[ModelParameters] = None
    is_default: Optional[bool] = None


@router.post("")
async def create_model(request: CreateModelRequest):
    """Create a new model configuration."""
    if not _model_manager:
        raise HTTPException(status_code=500, detail="Model manager not initialized")

    model = _model_manager.create(
        name=request.name,
        api_base=request.api_base,
        api_key=request.api_key,
        model_name=request.model_name,
        parameters=request.parameters,
        is_default=request.is_default
    )

    return model.dict()


@router.get("")
async def list_models():
    """List all model configurations."""
    if not _model_manager:
        raise HTTPException(status_code=500, detail="Model manager not initialized")

    models = _model_manager.list()
    return [m.dict() for m in models]


@router.get("/default")
async def get_default_model():
    """Get the default model configuration."""
    if not _model_manager:
        raise HTTPException(status_code=500, detail="Model manager not initialized")

    model = _model_manager.get_default()
    if not model:
        raise HTTPException(status_code=404, detail="No default model configured")

    return model.dict()


@router.get("/{model_id}")
async def get_model(model_id: str):
    """Get a model configuration by ID."""
    if not _model_manager:
        raise HTTPException(status_code=500, detail="Model manager not initialized")

    model = _model_manager.get(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    return model.dict()


@router.put("/{model_id}")
async def update_model(model_id: str, request: UpdateModelRequest):
    """Update a model configuration."""
    if not _model_manager:
        raise HTTPException(status_code=500, detail="Model manager not initialized")

    update_data = {}
    if request.name is not None:
        update_data["name"] = request.name
    if request.api_base is not None:
        update_data["api_base"] = request.api_base
    if request.api_key is not None:
        update_data["api_key"] = request.api_key
    if request.model_name is not None:
        update_data["model_name"] = request.model_name
    if request.parameters is not None:
        update_data["parameters"] = request.parameters.dict()
    if request.is_default is not None:
        update_data["is_default"] = request.is_default

    model = _model_manager.update(model_id, **update_data)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    return model.dict()


@router.delete("/{model_id}")
async def delete_model(model_id: str):
    """Delete a model configuration."""
    if not _model_manager:
        raise HTTPException(status_code=500, detail="Model manager not initialized")

    success = _model_manager.delete(model_id)
    if not success:
        raise HTTPException(status_code=404, detail="Model not found")

    return {"success": True}


@router.post("/{model_id}/set-default")
async def set_default_model(model_id: str):
    """Set a model as the default."""
    if not _model_manager:
        raise HTTPException(status_code=500, detail="Model manager not initialized")

    model = _model_manager.set_default(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    return model.dict()


@router.post("/{model_id}/test")
async def test_model(model_id: str):
    """Test a model configuration."""
    if not _model_manager:
        raise HTTPException(status_code=500, detail="Model manager not initialized")

    model = _model_manager.get(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    try:
        from openai import OpenAI

        client = OpenAI(
            api_key=model.api_key,
            base_url=model.api_base
        )

        # Test with a simple completion
        response = client.chat.completions.create(
            model=model.model_name,
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10
        )

        return {
            "success": True,
            "message": "Model connection successful",
            "response": response.choices[0].message.content
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
