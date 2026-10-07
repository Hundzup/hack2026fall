package handlers

import (
	"encoding/json"
	"net/http"

	"hack2026fall/backend/internal/ml"
)

type PredictHandler struct {
	ML *ml.Client
}

func (h *PredictHandler) Predict(w http.ResponseWriter, r *http.Request) {
	var in struct {
		Features []float64 `json:"features"`
	}
	if err := json.NewDecoder(r.Body).Decode(&in); err != nil {
		http.Error(w, "invalid json", http.StatusBadRequest)
		return
	}
	if len(in.Features) == 0 {
		http.Error(w, "features is empty", http.StatusBadRequest)
		return
	}

	res, err := h.ML.Predict(r.Context(), in.Features)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadGateway)
		return
	}
	writeJSON(w, http.StatusOK, res)
}
