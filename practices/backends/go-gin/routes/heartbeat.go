package routes

import (
	"gin-app/types"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
)

func HeartbeatRouter(c *gin.Context) {
	now := time.Now()
	response := types.HeartbeatResponse{
		Alive: now.Format(time.RFC3339),
	}
	c.JSON(http.StatusOK, response)
}
