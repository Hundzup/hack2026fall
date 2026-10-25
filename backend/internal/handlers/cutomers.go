package handlers

import (
	"errors"
	"log"
	"net/http"
	"strconv"

	"github.com/go-chi/chi/v5"
	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
)

// TODO вынести взаимодействие с DB в model слой
type CustomersHandler struct {
	DB *pgxpool.Pool
}

type Customer struct {
	ID int `db:"id" json:"id" example:"42"`
	// Вообще это можно было всё в int закинуть, но уже пофиг)
	Balance      float32  `db:"balance_eur" json:"balance_eur" example:"1337"`
	TotalDeposit float32  `db:"total_replenished_eur" json:"total_replenished_eur" example:"100500"`
	RiskScore    float32  `db:"risk_score" json:"risk_score" example:"67"`
	RiskLevel    string   `db:"risk_level" json:"risk_level" example:"high"`
	Email        string   `db:"email" json:"email" example:"user@example.com"`
	Reasons      []reason `json:"reasons"`
}

type reason struct {
	Feature      string  `db:"feature" json:"feature" example:"low_replenishment"`
	Contribution float32 `db:"contribution" json:"contribution" example:"0.4592"`
	Title        string  `db:"title" json:"title" example:"Низкие пополнения"`
}

func (h *CustomersHandler) List(w http.ResponseWriter, r *http.Request) {
	rows, err := h.DB.Query(r.Context(),
		"SELECT * FROM customers -- ORDER BY id")
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	customers, err := pgx.CollectRows(rows, pgx.RowToStructByName[Customer])
	if err != nil {
		log.Printf("CollectRows error: %v", err)
		http.Error(w, "failed to fetch customers", http.StatusInternalServerError)
		return
	}

	writeJSON(w, http.StatusOK, customers)
}

func (h *CustomersHandler) GetCustomer(w http.ResponseWriter, r *http.Request) {
	customerID, err := strconv.Atoi(chi.URLParam(r, "customerID"))
	if err != nil {
		http.Error(w, "invalid customerID", http.StatusBadRequest)
		return
	}

	rows, err := h.DB.Query(r.Context(),
		"SELECT * FROM customers WHERE id = $1", customerID)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	defer rows.Close()
	customer, err := pgx.CollectExactlyOneRow(rows, pgx.RowToStructByName[Customer])
	if errors.Is(err, pgx.ErrNoRows) {
		http.Error(w, "no customer with such ID", http.StatusNotFound)
		return
	}
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	writeJSON(w, http.StatusCreated, customer)
}
