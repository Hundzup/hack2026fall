package handlers

import (
	"encoding/json"
	"net/http"
)

// Как-нибудь сделать по адекватному)))
func writeJSON(w http.ResponseWriter, status int, v any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(v)
}
