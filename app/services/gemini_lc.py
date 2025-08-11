#
# from langchain_google_vertexai import ChatVertexAI
# from app.config import settings
#
# gemini = ChatVertexAI(
#     model=settings.VERTEX_MODEL_ID,
#     location=settings.VERTEX_LOCATION,
#     temperature=0.2,
# )
#
# def simple_gemini_call(prompt: str) -> str:
#     return gemini.invoke(prompt).content or ""
