from fastapi import Request
from fastapi.responses import JSONResponse
from app.exceptions.exceptions import UsuarioNaoAutorizado, TokenNaoAutenticado, ContaExistente, DadosInvalidos, UserNotFound, DistinctPasswords, DesactivatedUser

async def user_not_found_handler(request: Request, exc: UserNotFound):
    return JSONResponse(
            status_code=404,
            content={
                'detail': exc.message
            }
        )

async def distinct_passwords_handler(request: Request, exc: DistinctPasswords):
    return JSONResponse(
            status_code=400,
            content={
                'detail': exc.message
            }
        )

async def desactivated_user_handler(request: Request, exc: DesactivatedUser):
    return JSONResponse(
            status_code=403,
            content={
                'detail': exc.message
            }
        )


async def token_nao_Autenticado(request: Request, exc: TokenNaoAutenticado):
    return JSONResponse(
        status_code=401,
        content={
            'detail': exc.message
        }
    )

async def usuario_nao_Autorizado(request: Request, exc: UsuarioNaoAutorizado):
    return JSONResponse(
        status_code=403,
        content={
            'detail': exc.message
        }
    )

async def dados_invalidos(request: Request, exc: DadosInvalidos):
    return JSONResponse(
        status_code=400,
        content={
            'detail': exc.message
        }
    )

async def conta_existente(request: Request, exc: ContaExistente):
    return JSONResponse(
        status_code=409,
        content={
            'detail': exc.message
        }
    )