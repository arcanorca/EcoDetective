from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import os
from dotenv import load_dotenv

# .env dosyasından API anahtarını yükle
load_dotenv()

# Gemini API yapılandırması
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-pro')

app = FastAPI()

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class BarcodeRequest(BaseModel):
    barcode: str

@app.post("/scan")
async def scan_barcode(request: BarcodeRequest):
    try:
        # İlk prompt: Ürün ve marka bilgisini al
        product_prompt = f"Barkod: {request.barcode}. Bu barkod hangi ürün ve markaya ait?"
        product_response = model.generate_content(product_prompt)
        product_text = product_response.text

        # Ürün ve marka bilgisini çıkar
        # Not: Gerçek uygulamada daha sağlam bir parsing mekanizması kullanılmalı
        product_info = product_text.split('\n')[0]
        brand = product_info.split()[0]  # Basit bir örnek

        # İkinci prompt: Sürdürülebilirlik puanı ve yorumu al
        sustainability_prompt = f"Marka: {brand}. Sürdürülebilirlik performansını 0-100 arasında puanla ve 1 cümle ile açıkla."
        sustainability_response = model.generate_content(sustainability_prompt)
        sustainability_text = sustainability_response.text

        # Yanıtı parse et
        # Not: Gerçek uygulamada daha sağlam bir parsing mekanizması kullanılmalı
        score = 75  # Örnek puan
        comment = sustainability_text.split('\n')[0]

        return {
            "product": product_info,
            "brand": brand,
            "score": score,
            "comment": comment
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 