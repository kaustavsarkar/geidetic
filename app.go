package main

import (
	"context"
	"database/sql"
	"log"

	db "ain.com/database"
	"ain.com/fileio"
	"github.com/wailsapp/wails/v2/pkg/runtime"
)

// App struct
type App struct {
	ctx   context.Context
	appDb *sql.DB
}

// NewApp creates a new App application struct
func NewApp() *App {
	return &App{}
}

// startup is called when the app starts. The context is saved
// so we can call the runtime methods
func (a *App) startup(ctx context.Context) {
	a.ctx = ctx
	var dbErr error
	a.appDb, dbErr = db.Open()
	if dbErr != nil {
		log.Printf("Could not open the database %s", dbErr.Error())
	}
}

func (a *App) shutdown(ctx context.Context) {
	db.Close(a.appDb)
}

// Greet returns a greeting for the given name
func (a *App) ProcessDirectory() error {
	selection, dirErr := runtime.OpenDirectoryDialog(a.ctx, runtime.OpenDialogOptions{
		Title: "Select a Directory",
	})

	log.Printf("selected directory %s", selection)

	if dirErr != nil {
		return dirErr
	}

	statErr := fileio.DirStat(selection)

	if statErr != nil {
		return statErr
	}

	go a.handleRead(selection)

	return nil
}

func (a *App) ReadProcessedDirs() ([]*db.Dir, error) {
	txn, _ := a.appDb.Begin()
	defer txn.Commit()
	return db.ListDirectories(a.appDb, txn)
}

func (a *App) handleRead(dirPath string) {
	txn, _ := a.appDb.Begin()
	defer txn.Commit()
	dir := fileio.CrawlDirectory(dirPath)

	exists, _ := dir.Exist(a.appDb, txn)

	if exists {
		return
	}

	dir.Save(a.appDb, txn)
}
