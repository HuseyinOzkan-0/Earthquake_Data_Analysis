from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scraper import get_cleaned_data
import numpy as np

app = FastAPI()

# Allow React (localhost:3000) to access this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/earthquakes")
async def earthquakes():
    data = get_cleaned_data()
    return data

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

@app.get("/api/possible-earthquakes")
async def possible_earthquakes():
    data = get_cleaned_data()
    df = pd.DataFrame(data)
    
    # "Possible" Logic: Show areas with activity > 3.0 magnitude
    # to highlight more significant recent risks
    predictions = df[df['mag'] >= 3.0].copy()
    predictions['is_prediction'] = True
    
    return predictions.to_dict(orient="records")