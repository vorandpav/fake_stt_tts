import asyncio
import logging
import random
import os

from fastapi import FastAPI
from pydantic import BaseModel, Field

# --- Настройка ---
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

app = FastAPI()


# --- Модели данных для API ---
class SimilarityRequest(BaseModel):
    vacancy_text: str = Field(..., description="Полный текст вакансии.")
    resume_text: str = Field(..., description="Полный текст резюме.")


class SimilarityResponse(BaseModel):
    score: float = Field(..., example=0.85, description="Оценка схожести от 0.0 до 1.0.")
    comment: str = Field(..., example="Кандидат отлично подходит...", description="Текстовый комментарий от ML-модели.")


# --- Эндпоинты ---
@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/analyze", response_model=SimilarityResponse)
async def analyze_similarity(request: SimilarityRequest):
    """
    Принимает тексты, имитирует долгую обработку и возвращает результат.
    """
    log.info("Получен запрос на анализ схожести...")

    # 1. Имитируем "тяжелую" работу ML-модели
    processing_time = random.uniform(5, 12)  # Думаем от 5 до 12 секунд
    log.info(f"Имитация обработки... займет {processing_time:.2f} секунд.")
    await asyncio.sleep(processing_time)

    # 2. "Умная" логика подсчета (Jaccard Similarity по словам)
    words_vacancy = set(request.vacancy_text.lower().split())
    words_resume = set(request.resume_text.lower().split())

    intersection = len(words_vacancy.intersection(words_resume))
    union = len(words_vacancy.union(words_resume))
    score = intersection / union if union > 0 else 0

    # 3. Генерируем комментарий
    comment = f"Анализ (заглушка): Схожесть на {score:.1%}. "
    if score > 0.7:
        comment += "Высокая степень совпадения ключевых навыков. Рекомендуется к рассмотрению."
    elif score > 0.4:
        comment += "Есть частичное совпадение. Требуется дополнительный скрининг."
    else:
        comment += "Низкая степень совпадения. Возможно, кандидат не подходит на эту роль."

    log.info(f"Анализ завершен. Оценка: {score:.2f}")

    return SimilarityResponse(score=score, comment=comment)


# --- Инструкции по запуску ---
if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8001))
    log.info(f"Запуск Fake Similarity Server на порту {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
