package main

import (
	"embed"

	db "ain.com/database"
	"github.com/wailsapp/wails/v2"
	"github.com/wailsapp/wails/v2/pkg/logger"
	"github.com/wailsapp/wails/v2/pkg/options"
	"github.com/wailsapp/wails/v2/pkg/options/assetserver"
)

//go:embed all:frontend/dist
var assets embed.FS

func main() {
	// Create an instance of the app structure
	app := NewApp()

	// Create application with options
	err := wails.Run(&options.App{
		Title:  "Ain - Legal AI",
		Width:  1024,
		Height: 768,
		AssetServer: &assetserver.Options{
			Assets: assets,
		},
		BackgroundColour: &options.RGBA{R: 47, G: 54, B: 62, A: 1},
		OnStartup:        app.startup,
		Bind: []interface{}{
			app,
			&db.Dir{},
			&db.PDFMetadata{},
		},
		LogLevel:   logger.TRACE,
		OnShutdown: app.shutdown,
	})

	if err != nil {
		println("Error:", err.Error())
	}
}
