from typing import Optional
from lancedb.pydantic import LanceModel, Vector
from lancedb import Table, DBConnection
import lancedb

from models.model import VectorResult

# ---------------------------
# CONFIG
# ---------------------------

DB_DIR = "db"
TABLE_NAME = "legal_embeddings"
EMBED_DIM = 384


# ---------------------------
# Schema Definition using LanceModel
# ---------------------------

class LegalEmbedding(LanceModel):
    """Schema for legal document embeddings in LanceDB."""
    
    # Primary fields
    id: str
    embedding: Vector(EMBED_DIM)
    text: str
    doc_type: str
    canonical_id: str
    
    # Constitution structure fields
    part: Optional[str] = None
    chapter: Optional[str] = None
    article: Optional[str] = None
    clause: Optional[str] = None
    sub_clause: Optional[str] = None
    
    # Schedule fields
    schedule_name: Optional[str] = None
    schedule_part: Optional[str] = None
    entry_number: Optional[str] = None
    metadata: Optional[str] = None
    
    # Act/Case fields
    act_name: Optional[str] = None
    act_year: Optional[int] = None
    case_name: Optional[str] = None
    court: Optional[str] = None
    citation: Optional[str] = None
    paragraph_no: Optional[int] = None
    
    # Temporal fields
    effective_from: Optional[str] = None
    effective_to: Optional[str] = None
    
    # Amendment fields
    amendment_marker: Optional[str] = None
    amendment_operation: Optional[str] = None
    
    # Source fields
    source_file: Optional[str] = None
    source_page: Optional[int] = None
    
    # General fields
    jurisdiction: str = "India"
    ingested_at: str


# ---------------------------
# Database Manager Class
# ---------------------------

class DatabaseManager:
    """
    Manages LanceDB connection and table access with singleton pattern.
    
    Usage:
        db_manager = DatabaseManager()
        db_manager.init_db()
        table = db_manager.get_table()
    """
    
    def __init__(self, db_dir: str = DB_DIR, table_name: str = TABLE_NAME):
        """
        Initialize the DatabaseManager.
        
        Args:
            db_dir: Directory for the LanceDB database
            table_name: Name of the table to create/open
        """
        self.db_dir = db_dir
        self.table_name = table_name
        self._db: Optional[DBConnection] = None
        self._table: Optional[Table] = None
        self._initialized: bool = False
    
    def _init_db(self) -> None:
        """
        Initialize the LanceDB connection and table.
        This method is idempotent - calling it multiple times will not reinitialize.
        """
        if self._initialized and self._table is not None and self._db is not None:
            print("Database already initialized, returning existing connection.")
            return
        
        print("Initializing LanceDB...")
        self._db = lancedb.connect(self.db_dir)
        
        if self.table_name not in self._db.table_names():
            print(f"Creating table '{self.table_name}'...")
            self._table = self._db.create_table(self.table_name, schema=LegalEmbedding)
        else:
            print(f"Opening existing table '{self.table_name}'...")
            self._table = self._db.open_table(self.table_name)
        
        self._initialized = True
        print("Database initialization complete.")


    def get_db(self) -> DBConnection:
        """
        Get the database connection. Initializes if not already done.
        
        Returns:
            DBConnection: The database connection object
        """
        if not self._initialized or self._db is None:
            self._init_db()
        if self._db is None:
            raise RuntimeError("Database connection not initialized.")
        return self._db
    
    def get_table(self) -> Table:
        """
        Get the table object. Initializes if not already done.
        
        Returns:
            Table: The table object
        """
        if not self._initialized or self._table is None:
            self._init_db()
        if self._table is None:
            raise RuntimeError("Table not initialized.")
        return self._table
    
    def query_embeddings(self, query_vector: list[float], 
                         effective_date: Optional[str] = None, top_k: int = 50) -> list[VectorResult]:
        """
        Query the database using vector similarity search.
        
        Args:
            query_vector: The embedding vector to search with
            effective_date: Optional date to filter results by effectiveness
            
        Returns:
            List of matching results with metadata
        """
        table = self.get_table()
        search_results = (
            table.search(query_vector, vector_column_name="embedding")
            .limit(top_k)
            .to_list()
        )
        filtered_results = []

        for row in search_results:
            row.update({"embedding": None})
            # Skip omitted law
            if row.get("is_omitted") is True:
                continue
            # Skip inactive law
            if row.get("is_active") is False:
                continue
            # Optional: time-travel filtering
            if effective_date:
                ef_from = row.get("effective_from")
                ef_to = row.get("effective_to")

                if ef_from and effective_date < ef_from:
                    continue

                if ef_to and effective_date > ef_to:
                    continue

            filtered_results.append(row)
            
        answers: list[VectorResult] = []

        for rank, row in enumerate(filtered_results, start=1):
            answer = VectorResult(
                rank=rank,
                text=row["text"],
                doc_type=row["doc_type"],
                canonical_id=row["canonical_id"],
                article=row.get("article"),
                clause=row.get("clause"),
                court=row.get("court"),
                citation=row.get("citation"),
                source_page=row.get("source_page"),
                source_file=row.get("source_file"),
                similarity_score=1-row.get("_distance"),
                schedule=row.get("schedule_name"),
                entry=row.get("entry_number"),
            )
            answers.append(answer)

        return answers
    
    def reset(self) -> None:
        """
        Reset the database state (useful for testing).
        """
        self._db = None
        self._table = None
        self._initialized = False
        print("Database state reset.")
    
    @property
    def is_initialized(self) -> bool:
        """Check if the database has been initialized."""
        return self._initialized
