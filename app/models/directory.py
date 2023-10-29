from typing import Dict, Any

class PdfMetadata:
    def __init__(self, name: str, fullPath: str) -> None:
        self.name = name
        self.full_path = fullPath
    

class Directory:
    def __init__(self, dirName: str, ) -> None:
        self.dir_name = dirName
        

    def dir_to_dict(self) -> Dict[str, Any]:
        return vars(self)