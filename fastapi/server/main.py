from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware
import os
from fastapi_modules.s3_interactions import chat_router as s3_interactions
from fastapi_modules.parse_data_with_llm import chat_router \
    as parse_data_with_llm


app = FastAPI()


app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ['SECRET_KEY'],
    # https_only=os.environ['DEPLOY_ENV'] == 'PROD',
)


@app.middleware("http")
async def check_token_middleware(request: Request, call_next):
    """Allow only requests with the correct token."""
    token = request.headers.get("x-access-token")
    if token != os.environ['FAST_API_ACCESS_SECRET_TOKEN'] and \
       os.environ['ENV'] != 'local':
        return JSONResponse(status_code=403, content={'reason':
                            'Invalid or missing token'})
    response = await call_next(request)
    return response


app.include_router(s3_interactions, prefix='/s3_interactions',
                   tags=["S3 Interactions"])
app.include_router(parse_data_with_llm, prefix='/parse_data_with_llm',
                   tags=["LLM Parsing"])
