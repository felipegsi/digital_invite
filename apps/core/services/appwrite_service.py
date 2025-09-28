import logging
import os
import tempfile
from typing import Optional, Tuple

from appwrite.client import Client
from appwrite.services.storage import Storage
from appwrite.input_file import InputFile
from digital_invite.settings import base
from PIL import Image, UnidentifiedImageError


class AppwriteService:
    """
    Serviço utilitário para integração com Appwrite Storage.
    Arquivo: `apps/core/services/appwrite_service.py`
    """

    @staticmethod
    def _save_temp_file(django_file) -> str:
        extension = os.path.splitext(django_file.name)[1]
        with tempfile.NamedTemporaryFile(suffix=extension, delete=False) as temp:
            for chunk in django_file.chunks():
                temp.write(chunk)
            return temp.name

    @staticmethod
    def get_client() -> Client:
        client = Client()
        client.set_endpoint(base.APPWRITE_ENDPOINT)
        client.set_project(base.APPWRITE_PROJECT_ID)
        client.set_key(base.APPWRITE_API_KEY)
        return client

    @staticmethod
    def _is_image(path: str) -> bool:
        try:
            with Image.open(path):
                return True
        except (UnidentifiedImageError, OSError):
            return False

    @staticmethod
    def _resize_image(path: str, target_size: Tuple[int, int]) -> None:
        """
        Redimensiona a imagem em `path` para caber dentro de `target_size`
        mantendo a proporção. Substitui o ficheiro original.
        Compatível com diferentes versões do Pillow.
        """
        try:
            with Image.open(path) as img:
                target_w, target_h = target_size
                if img.size == (target_w, target_h):
                    return

                img_format = img.format or "JPEG"
                has_alpha = img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info)

                # Converte para RGB quando não há alpha (compatibilidade JPEG)
                if not has_alpha:
                    img = img.convert("RGB")

                # Compatibilidade Pillow: usa Image.Resampling.LANCZOS quando disponível
                resample = getattr(Image, "Resampling", Image).LANCZOS
                img.thumbnail((target_w, target_h), resample=resample)

                save_kwargs = {}
                if has_alpha and img_format.upper() == "PNG":
                    save_kwargs["format"] = "PNG"
                else:
                    save_kwargs["format"] = "JPEG"
                    save_kwargs["quality"] = 85

                img.save(path, **save_kwargs)
        except (UnidentifiedImageError, OSError) as exc:
            logging.warning("Falha ao redimensionar imagem (%s): %s", path, exc)
            # prosseguir sem redimensionamento
        except Exception as exc:
            logging.warning("Falha inesperada ao redimensionar imagem (%s): %s", path, exc)

    @staticmethod
    def _create_input_file(path: str) -> InputFile:
        return InputFile.from_path(path)

    @staticmethod
    def _upload_to_appwrite(input_file: InputFile, permissions: list) -> Optional[str]:
        client = AppwriteService.get_client()
        storage = Storage(client)
        result = storage.create_file(
            bucket_id=base.APPWRITE_BUCKET_ID,
            file_id="unique()",
            file=input_file,
            permissions=permissions,
        )
        # result normalmente é um dict com $id
        return result.get("$id") if isinstance(result, dict) else None

    @staticmethod
    def upload_file(file, permissions: Optional[list] = None, resize_to: Optional[Tuple[int, int]] = None) -> Optional[str]:
        """
        Faz upload de `file` para Appwrite. Se `resize_to` for fornecido e o ficheiro
        for uma imagem, redimensiona antes do upload. Retorna o id do ficheiro ou None.
        """
        permissions = permissions or ['read("any")']
        temp_path = AppwriteService._save_temp_file(file)

        try:
            if resize_to and AppwriteService._is_image(temp_path):
                AppwriteService._resize_image(temp_path, resize_to)

            input_file = AppwriteService._create_input_file(temp_path)
            file_id = AppwriteService._upload_to_appwrite(input_file, permissions)
            return file_id
        except Exception as exc:
            logging.error("Erro ao fazer upload para Appwrite: %s", exc)
            return None
        finally:
            if os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except OSError:
                    logging.warning("Falha ao remover ficheiro temporário: %s", temp_path)

    @staticmethod
    def get_file_url(file_id: str) -> Optional[str]:
        if not file_id:
            return None
        endpoint = base.APPWRITE_ENDPOINT.rstrip("/")
        bucket_id = base.APPWRITE_BUCKET_ID
        project_id = base.APPWRITE_PROJECT_ID
        return f"{endpoint}/storage/buckets/{bucket_id}/files/{file_id}/view?project={project_id}"
