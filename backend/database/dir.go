package db

import (
	"database/sql"
	"encoding/json"
	"log"

	_ "github.com/mattn/go-sqlite3"
)

func (dir *Dir) Save(db *sql.DB, txn *sql.Tx) error {
	stmt, prepErr := txn.Prepare(`INSERT INTO directories(DirName, PDFs) 
	VALUES (?,?)
	ON CONFLICT(DirName) DO UPDATE SET PDFs=excluded.PDFs`)
	if prepErr != nil {
		return prepErr
	}
	defer stmt.Close()

	pdfListByte, marshErr := json.Marshal(dir.PDFs)

	if marshErr != nil {
		log.Printf("Error while marshalling directory %v %v", *dir, marshErr)
		return marshErr
	}
	pdfJson := string(pdfListByte)
	_, execErr := stmt.Exec(dir.DirName, pdfJson)
	if execErr != nil {
		log.Printf("Error while saving data %s", execErr.Error())
		return execErr
	}
	return nil
}

func ListDirectories(db *sql.DB, txn *sql.Tx) ([]*Dir, error) {
	// Query to select all rows from the "directories" table
	query := "SELECT DirName, PDFs FROM directories"
	// Execute the query
	rows, err := db.Query(query)
	if err != nil {
		log.Printf("error while executing query %s", err.Error())
		return nil, err
	}
	defer rows.Close()
	// Slice to store the results
	var directories []*Dir

	// Iterate through the rows and scan data into Dir structs
	for rows.Next() {
		var dirName string
		var pdfsJson string

		// Scan values from the row into variables
		if err := rows.Scan(&dirName, &pdfsJson); err != nil {
			log.Printf("error while scanning row %s", err.Error())
		}
		// Parse the JSON string into a slice of PDFMetadata structs
		var pdfs []*PDFMetadata
		if err := json.Unmarshal([]byte(pdfsJson), &pdfs); err != nil {
			log.Fatal(err)
		}
		// Create a Dir struct and add it to the slice
		dir := Dir{
			DirName: dirName,
			PDFs:    pdfs,
		}
		directories = append(directories, &dir)
	}
	return directories, rows.Err()
}

func (dir *Dir) Exist(db *sql.DB, txn *sql.Tx) (bool, error) {
	stmt, prepErr := txn.Prepare(`SELECT 1
	FROM directories
	WHERE DirName = ?`)

	if prepErr != nil {
		return true, prepErr
	}
	defer stmt.Close()

	var exists bool
	execErr := stmt.QueryRow(dir.DirName).Scan(&exists)
	if execErr != nil {
		log.Printf("Error while saving data %s", execErr.Error())
		return false, execErr
	}
	return exists, nil
}
