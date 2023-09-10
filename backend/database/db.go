package db

import "database/sql"

func Open() (*sql.DB, error) {
	db, dbErr := sql.Open("sqlite3", "fs.db")
	if dbErr != nil {
		return nil, dbErr
	}

	createTableSql := `
	CREATE TABLE IF NOT EXISTS directories (
		DirName TEXT UNIQUE,
		PDFs TEXT
	)
	`
	if _, execErr := db.Exec(createTableSql); execErr != nil {
		return nil, execErr
	}

	return db, nil
}

func Close(db *sql.DB) error {
	return db.Close()
}
