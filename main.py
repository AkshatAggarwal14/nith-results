from fastapi import FastAPI
import scrape
app = FastAPI(title="NITH Results API", docs_url="/")

@app.get("/result/{rollNo}")
async def result(rollNo: str):
    resp = await scrape.get_result(rollNo)
    return resp
