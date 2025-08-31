import hvac
import os
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class VaultService:
    def __init__(self, vault_addr: str = None, vault_token: str = None):
        self.vault_addr = vault_addr or os.getenv("VAULT_ADDR", "http://localhost:8200")
        self.vault_token = vault_token or os.getenv("VAULT_TOKEN")

        if not self.vault_token:
            raise ValueError("VAULT_TOKEN не установлен")

        self.client = hvac.Client(url=self.vault_addr, token=self.vault_token)

    def store_credentials(self, path: str, credentials: Dict[str, str]) -> bool:
        """Сохранить учетные данные в Vault."""
        try:
            self.client.secrets.kv.v2.create_or_update_secret(
                path=path, secret=credentials
            )
            logger.info(f"Учетные данные сохранены в Vault по пути: {path}")
            return True
        except Exception as e:
            logger.error(f"Ошибка сохранения учетных данных в Vault: {e}")
            return False

    def get_credentials(self, path: str) -> Optional[Dict[str, Any]]:
        """Получить учетные данные из Vault."""
        try:
            secret_response = self.client.secrets.kv.v2.read_secret_version(path=path)
            return secret_response["data"]["data"]
        except Exception as e:
            logger.error(f"Ошибка получения учетных данных из Vault: {e}")
            return None

    def delete_credentials(self, path: str) -> bool:
        """Удалить учетные данные из Vault."""
        try:
            self.client.secrets.kv.v2.delete_metadata_and_all_versions(path=path)
            logger.info(f"Учетные данные удалены из Vault по пути: {path}")
            return True
        except Exception as e:
            logger.error(f"Ошибка удаления учетных данных из Vault: {e}")
            return False
