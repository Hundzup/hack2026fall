package handlers

import (
	"encoding/json"
	"net/http"
)

// Как-нибудь сделать по адекватному)))
func writeJSON(w http.ResponseWriter, status int, v any) {
	w.Header().Set("Content-Type", "application/json")
	// Lasies and gentelmens, we are fucked
	w.Header().Set("Access-Control-Allow-Origin", "*")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(v)
}
