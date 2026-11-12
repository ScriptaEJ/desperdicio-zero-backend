from jose import jwt, JWTError, ExpiredSignatureError
from datetime import datetime, timedelta
import os
import resend
from dotenv import load_dotenv

load_dotenv()

SECRET = os.getenv("JWT_SECRET")
ALGORITHM = os.getenv("JWT_ALGORITHM")

resend.api_key = os.getenv("RESEND_API_KEY")

# ---------------------------- CRIA TOKEN RECUPERACAO SENHA ----------------------------

def criar_token_recuperacao_senha(email: str):
    payload = {
        "sub": email,
        "type": "password_reset",
        "exp": datetime.utcnow() + timedelta(hours=0.5)
    }
    return jwt.encode(payload, SECRET, algorithm=ALGORITHM)

# ---------------------------- VALIDA TOKEN RECUPERACAO SENHA ----------------------------

def validar_token_recuperacao_senha(token: str):
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])

        if payload.get("type") != "password_reset":
            return {"erro": "tipo_invalido"}

        return payload

    except ExpiredSignatureError:
        return {"erro": "expirado"}

    except JWTError as e:
        print("Erro ao validar token:", str(e))
        return {"erro": "invalido"}

# ---------------------------- ENVIA EMAIL ----------------------------

def enviar_email(destinatario: str, assunto: str, html_content: str):
    try:
        response = resend.Emails.send({
            "from": os.getenv("EMAIL_FROM"),
            "to": [destinatario],
            "subject": assunto,
            "html": html_content,
        })

        print("Email enviado!", response)

    except Exception as e:
        print("Erro ao enviar email:", str(e))
        raise e
