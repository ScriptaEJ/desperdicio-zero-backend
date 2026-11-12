from fastapi import FastAPI
from app.exceptions.exceptions import UserNotFound, DistinctPasswords, DesactivatedUser, UsuarioNaoAutorizado, TokenNaoAutenticado
from app.exceptions.handlers import user_not_found_handler, distinct_passwords_handler, desactivated_user_handler, usuario_nao_Autorizado, token_nao_Autenticado, dados_invalidos, conta_existente
from fastapi.middleware.cors import CORSMiddleware
from app.routes.auth_routes import auth_routes
from app.routes.usuario_routes import user_routes
app = FastAPI()

# ---------------- CORS ----------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

origins = [
    "http://localhost:5173",
    "*", 
]

# ------------------ HANDLERS ------------------

app.add_exception_handler(
    UserNotFound,
    user_not_found_handler
)

app.add_exception_handler(
    DistinctPasswords,
    distinct_passwords_handler
)

app.add_exception_handler(
    DesactivatedUser,
    desactivated_user_handler
)

app.add_exception_handler(
    TokenNaoAutenticado,
    token_nao_Autenticado
)

app.add_exception_handler(
    UsuarioNaoAutorizado,
    usuario_nao_Autorizado
)

# ------------------ HANDLERS ------------------

app.include_router(auth_routes, prefix='/api')
app.include_router(user_routes, prefix='/api')

@app.get('/')
def root():
    return {'status_api': 'active'}

