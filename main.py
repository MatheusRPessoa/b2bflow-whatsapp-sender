import os
import re
import logging
import requests
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def get_supabase_client() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        raise EnvironmentError("SUPABASE_URL e SUPABASE_KEY devem estar definidos no .env")

    return create_client(url, key)


def fetch_contacts(client: Client, limit: int = 3) -> list[dict]:
    logger.info("Buscando contatos no Supabase...")

    response = (
        client.table("contacts")
        .select("name, phone")
        .limit(limit)
        .execute()
    )

    contacts = response.data

    if not contacts:
        logger.warning("Nenhum contato encontrado na tabela 'contacts'.")
    else:
        logger.info(f"{len(contacts)} contato(s) encontrado(s).")

    return contacts


def is_valid_phone(phone: str) -> bool:
    return bool(re.fullmatch(r"\d{10,15}", phone))


def send_whatsapp_message(phone: str, message: str) -> bool:
    instance_id = os.getenv("ZAPI_INSTANCE_ID")
    token = os.getenv("ZAPI_TOKEN")

    if not instance_id or not token:
        raise EnvironmentError(
            "ZAPI_INSTANCE_ID e ZAPI_TOKEN devem estar definidos no .env"
        )

    url = f"https://api.z-api.io/instances/{instance_id}/token/{token}/send-text"

    headers = {
        "Content-Type": "application/json",
    }

    payload = {
        "phone": phone,
        "message": message,
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        message_id = response.json().get("messageId")
        logger.info(f"Mensagem enviada para {phone} (messageId={message_id})")
        return True
    except requests.exceptions.HTTPError as e:
        logger.error(f"Erro HTTP ao enviar para {phone}: {e.response.status_code} - {e.response.text}")
        return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro de conexão ao enviar para {phone}: {e}")
        return False


def main():
    logger.info("=== Iniciando envio de mensagens ===")

    try:
        supabase = get_supabase_client()
        contacts = fetch_contacts(supabase, limit=3)
    except Exception as e:
        logger.error(f"Falha ao conectar/buscar contatos no Supabase: {e}")
        return

    if not contacts:
        logger.warning("Nenhum contato para enviar. Encerrando.")
        return

    success_count = 0
    fail_count = 0

    for contact in contacts:
        name = (contact.get("name") or "").strip()
        phone = (contact.get("phone") or "").strip()

        if not name or not phone:
            logger.warning(f"Contato inválido (campo vazio): {contact}")
            fail_count += 1
            continue

        if not is_valid_phone(phone):
            logger.warning(f"Telefone em formato inválido para {name}: {phone}")
            fail_count += 1
            continue

        message = f"Olá, {name} tudo bem com você?"
        sent = send_whatsapp_message(phone, message)

        if sent:
            success_count += 1
        else:
            fail_count += 1

    logger.info(f"=== Concluído: {success_count} enviado(s), {fail_count} falha(s) ===")


if __name__ == "__main__":
    main()