package db

type PDFMetadata struct {
	Name     string `json:"name,omitempty"`
	FullPath string `json:"fullPath,omitempty"`
}

type Dir struct {
	DirName string
	PDFs    []*PDFMetadata
}
