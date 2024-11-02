package main

import (
	"gin-app/routes"

	"github.com/gin-gonic/gin"
)

func setupRouter() *gin.Engine {
	r := gin.Default()

	apiGroup := r.Group("/api")
	apiGroup.GET("/heartbeat", routes.HeartbeatRouter)

	return r
}

func main() {
	r := setupRouter()
	r.SetTrustedProxies(nil) // disable trusted proxies
	r.Run()                  // listen and serve on 0.0.0.0:8080
}
