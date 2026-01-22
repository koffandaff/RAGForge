"""
LEARNING PHASE: Multi-Storage Manager
--------------------------------------
This file explains how to manage multiple document collections (Titles) 
and make them persistent using a JSON registry.
"""

import os
import json
import shutil
from typing import Dict, List

class EducationalStorageManager:
    """
    Manages the organization of multiple Vector DB indices on the hard drive.
    """

    def __init__(self, storage_dir: str):
        """
        Args:
            storage_dir: The main folder where everything will be saved.
        """
        self.storage_dir = storage_dir
        # This is our "Registry" file. It's the map of our library.
        self.registry_path = os.path.join(storage_dir, "titles_registry.json")
        
        # Ensure folders exist
        if not os.path.exists(storage_dir):
            os.makedirs(storage_dir)
            
        # 1. THE REGISTRY LOGIC
        # We load a JSON file that tells us which titles exist and where their files are.
        self.titles = self.load_registry()
        print(f"--- Storage Manager Ready: {len(self.titles)} titles loaded ---")

    def load_registry(self) -> Dict:
        """Loads the JSON map from disk"""
        if os.path.exists(self.registry_path):
            with open(self.registry_path, 'r') as f:
                return json.load(f)
        return {} # Return empty dict if no registry exists yet

    def save_registry(self):
        """Writes the current map of titles back to the JSON file"""
        with open(self.registry_path, 'w') as f:
            json.dump(self.titles, f, indent=4)

    def register_new_title(self, title: str):
        """
        Creates a new entry in our system for a knowledge base.
        """
        # 2. NORMALIZATION
        # We clear spaces and lowercase to avoid "AI Notes" vs "ai notes" duplicates.
        safe_title = title.strip().lower()
        
        if safe_title in self.titles:
            print(f"Title '{title}' already exists in registry.")
            return False
            
        # 3. PATH GENERATION
        # We decide where the binary index and the text chunks will live.
        self.titles[safe_title] = {
            "display_name": title,
            "index_file": os.path.join(self.storage_dir, f"{safe_title}.index"),
            "chunks_file": os.path.join(self.storage_dir, f"{safe_title}_chunks.json"),
            "chunk_count": 0
        }
        
        self.save_registry()
        print(f"Registered new knowledge base: {title}")
        return True

    def delete_title(self, title: str):
        """
        The Deletion Logic.
        When a user deletes a title, we must clean up BOTH the registry and the files.
        """
        safe_title = title.strip().lower()
        if safe_title not in self.titles:
            return False
            
        # 4. DISK CLEANUP
        # We find the file paths we registered earlier and physically remove them.
        info = self.titles[safe_title]
        try:
            if os.path.exists(info["index_file"]):
                os.remove(info["index_file"])
            if os.path.exists(info["chunks_file"]):
                os.remove(info["chunks_file"])
                
            # 5. REGISTRY PURGE
            # Remove from our runtime dict and save the JSON.
            del self.titles[safe_title]
            self.save_registry()
            
            print(f"Successfully deleted all data for: {title}")
            return True
        except Exception as e:
            print(f"Error during deletion: {e}")
            return False

# --- WHY USE A REGISTRY? ---
# 1. Isolation: Each 'Title' has its own FAISS index. Adding to one doesn't slow down others.
# 2. Persistence: By saving paths in JSON, the app remembers everything even after you close it.
# 3. Portability: You can easily see exactly which files belong to which document collection.

if __name__ == "__main__":
    # Test storage in a local 'test_storage' folder
    # manager = EducationalStorageManager("./test_storage")
    # manager.register_new_title("My Python Notes")
    pass
