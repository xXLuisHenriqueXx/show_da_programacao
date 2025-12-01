import json
import os
from typing import Dict, Any

class ConfigLoader:
    @staticmethod
    def load_config() -> Dict[str, Any]:
        """Carrega todo o arquivo de configuração do jogo."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, 'game_config.json')
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Arquivo de configuração não encontrado em: {file_path}")