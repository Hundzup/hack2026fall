package main

import (
	"context"
	"errors"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
	"github.com/joho/godotenv"

	"hack2026fall/backend/internal/db"
	"hack2026fall/backend/internal/handlers"
	"hack2026fall/backend/internal/ml"
)

func main() {
	_ = godotenv.Load()

	dsn := os.Getenv("DATABASE_URL")
	mlURL := os.Getenv("ML_URL")
host := os.Getenv("LISTEN_HOST")
	if host == "" {
		host = "127.0.0.1"
	}
	port := os.Getenv("LISTEN_PORT")
	if port == "" {
		port = "8080"
	}

	ctx := context.Background()
logger := log.Default()

logger.Print("Try to connect to DB")
	pool, err := db.NewPool(ctx, dsn)
	if err != nil {
		logger.Fatalf("db: %v", err)
	}
	defer pool.Close()

	mlClient := ml.NewClient(mlURL)

	customersHandler := &handlers.CustomersHandler{DB: pool}

	r := chi.NewRouter()
	r.Use(middleware.Logger)
	r.Use(middleware.Recoverer)

	r.Route("/api/v1", func(r chi.Router) {
		r.Get("/customers", customersHandler.List)
		r.Get("/customers/{customerID}", customersHandler.GetCustomer)
	})

	srv := &http.Server{
		Addr:              host + ":" + port,
		Handler:           r,
		ReadHeaderTimeout: 5 * time.Second,
	}

	go func() {
		logger.Printf("server is listening on %s", srv.Addr)
		if err := srv.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
			logger.Fatalf("listen: %v", err)
		}
	}()

	// graceful shutdown
	stop := make(chan os.Signal, 1)
	signal.Notify(stop, os.Interrupt, syscall.SIGTERM)
	<-stop

	shutdownCtx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	_ = srv.Shutdown(shutdownCtx)
	log.Println("stopped")
}
