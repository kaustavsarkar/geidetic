from typing import Dict, Any


class PdfMetadata:
    """Represents the metadata for a pdf"""

    def __init__(self, name: str, full_path: str) -> None:
        self.name = name
        self.full_path = full_path

    @staticmethod
    def from_tuple(row: tuple):
        """Converts tuple recieved from database to object"""
        pdf = PdfMetadata(row[1], row[2])
        return pdf

    @property
    def to_dict(self) -> str:
        return self.__dict__


class Directory:
    """Represents directory structure of a file system"""

    def __init__(self, dir_name: str, ) -> None:
        self.dir_name = dir_name

    def dir_to_dict(self) -> Dict[str, Any]:
        """Converts object to dictionary"""
        return vars(self)
