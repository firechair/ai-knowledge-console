import os
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Callable
from huggingface_hub import hf_hub_download, list_repo_files, snapshot_download
from huggingface_hub.utils import HfHubHTTPError

MODELS_DIR = Path(__file__).parent.parent / "models"
MODELS_DIR.mkdir(exist_ok=True)

TRACKING_FILE = MODELS_DIR / "embedding_models.json"

class ModelManager:
    """Manages downloading and listing models"""

    def __init__(self):
        self.active_downloads: Dict[str, Dict] = {}
        self._ensure_tracking_file()

    def _ensure_tracking_file(self):
        """Create tracking file if it doesn't exist"""
        if not TRACKING_FILE.exists():
            import json
            with open(TRACKING_FILE, 'w') as f:
                json.dump(["all-MiniLM-L6-v2"], f)

    def _get_tracked_models(self) -> List[str]:
        """Get list of tracked models"""
        try:
            import json
            with open(TRACKING_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return ["all-MiniLM-L6-v2"]

    def _add_tracked_model(self, model_name: str):
        """Add model to tracking file"""
        models = self._get_tracked_models()
        if model_name not in models:
            models.append(model_name)
            import json
            with open(TRACKING_FILE, 'w') as f:
                json.dump(models, f)

    def list_local_llm_models(self) -> List[Dict[str, str]]:
        """List GGUF models in backend/models/"""
        models = []
        for file in MODELS_DIR.glob("*.gguf"):
            models.append({
                "filename": file.name,
                "size_mb": round(file.stat().st_size / (1024 * 1024), 2),
                "path": str(file)
            })
        return models

    def list_local_embedding_models(self) -> List[str]:
        """List tracked and cached SentenceTransformer models"""
        tracked_models = self._get_tracked_models()
        cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
        
        if not cache_dir.exists():
            # If no cache at all, only return what we might have had
            # but usually they are one and the same
            return [m for m in tracked_models if m == "all-MiniLM-L6-v2"]

        available = []
        for m_name in tracked_models:
            # Check if it exists in cache
            safe_name = "models--" + m_name.replace("/", "--")
            if (cache_dir / safe_name).exists():
                available.append(m_name)
        
        return available

    async def download_gguf_model(
        self,
        repo_id: str,
        filename: str,
        token: Optional[str] = None,
        progress_callback: Optional[Callable] = None
    ):
        """Download a GGUF model from HuggingFace"""
        download_id = f"{repo_id}/{filename}"

        try:
            self.active_downloads[download_id] = {
                "status": "downloading",
                "progress": 0,
                "repo_id": repo_id,
                "filename": filename
            }

            # Download in separate thread to avoid blocking
            def download_with_progress():
                try:
                    path = hf_hub_download(
                        repo_id=repo_id,
                        filename=filename,
                        local_dir=MODELS_DIR,
                        local_dir_use_symlinks=False,
                        token=token
                    )
                    return path
                except Exception as e:
                    raise e

            # Run in executor
            loop = asyncio.get_event_loop()
            model_path = await loop.run_in_executor(None, download_with_progress)

            self.active_downloads[download_id] = {
                "status": "completed",
                "progress": 100,
                "path": model_path
            }

            return model_path

        except HfHubHTTPError as e:
            self.active_downloads[download_id] = {
                "status": "error",
                "error": f"HuggingFace error: {str(e)}"
            }
            raise
        except Exception as e:
            self.active_downloads[download_id] = {
                "status": "error",
                "error": str(e)
            }
            raise

    async def download_embedding_model(
        self,
        model_name: str,
        progress_callback: Optional[Callable] = None
    ):
        """Download a SentenceTransformer model"""
        try:
            self.active_downloads[model_name] = {
                "status": "downloading",
                "progress": 0,
                "model": model_name
            }

            # SentenceTransformer auto-downloads on first use
            from sentence_transformers import SentenceTransformer

            def download():
                model = SentenceTransformer(model_name)
                # Register in local tracker
                self._add_tracked_model(model_name)
                return model

            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, download)

            self.active_downloads[model_name] = {
                "status": "completed",
                "progress": 100
            }

        except Exception as e:
            self.active_downloads[model_name] = {
                "status": "error",
                "error": str(e)
            }
            raise

    def get_download_status(self, download_id: str) -> Optional[Dict]:
        """Get status of active/completed download"""
        return self.active_downloads.get(download_id)

    def list_downloads(self) -> Dict[str, Dict]:
        """List all tracked downloads"""
        return self.active_downloads

# Singleton
_model_manager: Optional[ModelManager] = None

def get_model_manager() -> ModelManager:
    global _model_manager
    if _model_manager is None:
        _model_manager = ModelManager()
    return _model_manager
