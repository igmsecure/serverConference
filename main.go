package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"log"
	"math/rand"
	"net/http"
	"time"
)

const secretKey = "WTXKmg65e0zYNzFEaZ"

type ReviewRequest struct {
	ArticleID int `json:"articleID"`
	UserID    int `json:"userID"`
}

type ReviewResult struct {
	Result int `json:"result"`
}

type ReviewUser struct {
	UserID int `json:"userID"`
}

type Response struct {
	Message string `json:"message"`
}

func main() {
	http.HandleFunc("/asyncProcessReviewing", handleReview)
	log.Println("Server started on port 8080")
	log.Fatal(http.ListenAndServe(":8080", nil))
}

func handleReview(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		w.WriteHeader(http.StatusMethodNotAllowed)
		return
	}

	var req ReviewRequest
	err := json.NewDecoder(r.Body).Decode(&req)
	if err != nil {
		w.WriteHeader(http.StatusBadRequest)
		response := Response{
			Message: "Запрос не выполнен",
		}
		json.NewEncoder(w).Encode(response)
		return
	}

	w.WriteHeader(http.StatusOK)
	response := Response{
		Message: "Запрос выполнен",
	}
	json.NewEncoder(w).Encode(response)

	go processReview(req.ArticleID, req.UserID)

}

func processReview(articleID int, userID int) {
	// Имитация задержки выполнения действия
	delay := rand.Intn(6) + 5
	log.Printf("Processing review for article ID %d with a delay of %d seconds", articleID, delay)
	time.Sleep(time.Duration(delay) * time.Second)

	result := rand.Intn(5) - 2 // Получение случайного результата от -2 до 2

	// Отправка результата на другой веб-сервис
	sendResult(articleID, userID, result)
}

func sendResult(articleID int, userID int, result int) error {
	reviewSendResult := result
	// Создаем структуру данных для отправки
	reviewResult := struct {
		Result    int    `json:"result"`
		UserID    int    `json:"userID"`
		SecretKey string `json:"secretKey"`
	}{
		Result:    result,
		UserID:    userID,
		SecretKey: secretKey,
	}

	// Преобразуем структуру данных в JSON
	jsonData, err := json.Marshal(reviewResult)
	if err != nil {
		return fmt.Errorf("Ошибка при маршалинге JSON данных: %v", err)
	}

	// Создаем запрос на PUT-запрос
	req, err := http.NewRequest("PUT", fmt.Sprintf("http://127.0.0.1:8000/api/articleReviews/%d", articleID), bytes.NewBuffer(jsonData))
	if err != nil {
		return fmt.Errorf("Ошибка при создании PUT-запроса: %v", err)
	}

	// Устанавливаем заголовок Content-Type для JSON
	req.Header.Set("Content-Type", "application/json")

	// Создаем клиент и выполняем запрос
	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return fmt.Errorf("Ошибка при выполнении PUT-запроса: %v", err)
	}
	defer resp.Body.Close()

	// Проверяем код состояния ответа
	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("Ошибка при отправке результата: код состояния %d", resp.StatusCode)
	}

	log.Printf("Review result sent for article ID [%d] - review [%d]", articleID, reviewSendResult)

	return nil
}
