"""Model configuration manager."""

import uuid
from datetime import datetime
from typing import List, Optional

from backend.models.model_config import ModelConfig, ModelParameters
from backend.services.config.config_manager import ConfigManager


class ModelConfigManager:
    """Manages LLM model configurations."""

    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.config_file = "models.json"

    def create(
        self,
        name: str,
        api_base: str,
        api_key: str,
        model_name: str,
        parameters: Optional[ModelParameters] = None,
        is_default: bool = False,
    ) -> ModelConfig:
        """Create a new model configuration."""
        model_id = str(uuid.uuid4())

        # If this is set as default, unset other defaults
        if is_default:
            self._unset_all_defaults()

        model = ModelConfig(
            id=model_id,
            name=name,
            api_base=api_base,
            api_key=api_key,
            model_name=model_name,
            parameters=parameters or ModelParameters(),
            is_default=is_default,
        )

        self.config_manager.create(self.config_file, model_id, model.dict())

        return model

    def get(self, model_id: str) -> Optional[ModelConfig]:
        """Get a model configuration by ID."""
        model_data = self.config_manager.get_by_id(self.config_file, model_id)
        if model_data and model_data.get('status') == 'active':
            return ModelConfig(**model_data)
        return None

    def list(self, include_deleted: bool = False) -> List[ModelConfig]:
        """List all model configurations."""
        data = self.config_manager.load(self.config_file)
        if not data:
            return []

        models = [ModelConfig(**m) for m in data.values()]

        if not include_deleted:
            models = [m for m in models if m.status == 'active']

        return models

    def get_default(self) -> Optional[ModelConfig]:
        """Get the default model configuration."""
        models = self.list()
        for model in models:
            if model.is_default:
                return model
        return models[0] if models else None

    def update(self, model_id: str, **kwargs) -> Optional[ModelConfig]:
        """Update a model configuration."""
        model = self.config_manager.get_by_id(self.config_file, model_id)
        if not model:
            return None

        # If setting as default, unset other defaults
        if kwargs.get('is_default'):
            self._unset_all_defaults()

        for key, value in kwargs.items():
            if key in model:
                model[key] = value
        model['updated_at'] = datetime.utcnow().isoformat()

        self.config_manager.update(self.config_file, model_id, model)
        return ModelConfig(**model)

    def delete(self, model_id: str) -> bool:
        """Soft delete a model configuration."""
        return self.update(model_id, status='deleted') is not None

    def set_default(self, model_id: str) -> Optional[ModelConfig]:
        """Set a model as the default."""
        model = self.get(model_id)
        if not model:
            return None

        self._unset_all_defaults()
        return self.update(model_id, is_default=True)

    def _unset_all_defaults(self):
        """Unset default flag for all models."""
        models = self.list()
        for model in models:
            if model.is_default:
                self.update(model.id, is_default=False)
