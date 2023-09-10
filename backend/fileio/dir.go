package fileio

import (
	"fmt"
	"log"
	"os"
	"path/filepath"
	"strings"

	db "ain.com/database"
)

func CrawlDirectory(dirName string) *db.Dir {
	// Get a list of files in the directory.
	files, err := os.ReadDir(dirName)
	if err != nil {
		log.Fatalf("Error reading directory: %v", err)
	}
	// Loop through the files and process PDFs.
	dir := &db.Dir{
		DirName: dirName,
	}
	dir.PDFs = make([]*db.PDFMetadata, 0)
	for _, file := range files {
		if !file.IsDir() && strings.HasSuffix(file.Name(), ".pdf") {
			pdfFilePath := filepath.Join(dirName, file.Name())
			pdf := &db.PDFMetadata{
				Name:     file.Name(),
				FullPath: pdfFilePath,
			}
			dir.PDFs = append(dir.PDFs, pdf)
		}
	}
	return dir
}

func DirStat(dirName string) error {
	fileInfo, err := os.Stat(dirName)

	if err != nil {
		if os.IsNotExist(err) {
			log.Printf("Directory %s does not exist", dirName)
		} else {
			log.Printf("Error while getting stat for directory %s ", dirName)
		}
		return err
	}

	// Check if the path points to a directory
	if fileInfo.IsDir() {
		log.Printf("Directory %s exists.\n", dirName)
		return nil
	}
	return fmt.Errorf("%s is not a directory", dirName)

}
