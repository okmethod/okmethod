package main

import (
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
)

func main() {
	r := gin.Default()

	r.GET("/api/heartbeat", func(c *gin.Context) {
		now := time.Now()
		c.JSON(http.StatusOK, gin.H{
			"alive": now.Format(time.RFC3339),
		})
	})

	r.Run() // listen and serve on 0.0.0.0:8080
}
