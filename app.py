from fastapi import FastAPI, Header, HTTPException

app = FastAPI(title="API DCA PDF", version="1.0.0")

API_KEY = "remplace-par-une-variable-d-env"

@app.post("/generate-pdf")
def generate_pdf(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return {"status": "ok", "message": "PDF généré"}
