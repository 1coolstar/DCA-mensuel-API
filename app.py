from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

openapi_schema = {
    "openapi": "3.1.0",
    "info": { "title": "API DCA PDF", "version": "1.0.0" },
    "servers": [
        { "url": "https://dca-mensuel-api.onrender.com" }
    ],
    "paths": {
        "/health": {
            "get": {
                "operationId": "checkHealth",
                "summary": "Vérifie l'état du service",
                "responses": {
                    "200": {
                        "description": "OK",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": { "status": { "type": "string" } }
                                }
                            }
                        }
                    }
                }
            }
        },
        "/generate-pdf": {
            "post": {
                "operationId": "generateDcaPdf",
                "summary": "Génère le PDF DCA",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "portfolioId": { "type": "string" },
                                    "month": { "type": "string", "format": "date" }
                                },
                                "required": ["portfolioId"]
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "PDF généré",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["status", "url"],
                                    "properties": {
                                        "status": { "type": "string" },
                                        "url": { "type": "string", "format": "uri" }
                                    }
                                }
                            }
                        }
                    },
                    "401": { "description": "Clé invalide" }
                },
                "security": [{ "ApiKeyAuth": [] }]
            }
        }
    },
    "components": {
        "schemas": {},
        "securitySchemes": {
            "ApiKeyAuth": {
                "type": "apiKey",
                "in": "header",
                "name": "X-API-Key"
            }
        }
    }
}

@app.get("/openapi.json")
def get_openapi():
    return JSONResponse(content=openapi_schema)
