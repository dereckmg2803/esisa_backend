from datetime import datetime
from zoneinfo import ZoneInfo
import resend
import os

resend.api_key = os.getenv("RESEND_API_KEY")

async def send_contact_emails(contact):

    timestamp = datetime.now(ZoneInfo("America/Bogota")).strftime("%d/%m/%Y %H:%M")

    # Email al cliente
    resend.Emails.send({
        "from": "Glenia & Macondo <no-reply@mail.gleniaymacondo.com>",
        "to": [contact.email],
        "subject": "Hemos recibido tu mensaje ✨",
        "html": f"""
        <h2>Hola {contact.name} 👋</h2>
        <p>Gracias por contactarnos. Hemos recibido tu mensaje correctamente.</p>

        <p><strong>Tu mensaje:</strong></p>
        <p>{contact.message}</p>

        <p>Pronto te responderemos.</p>

        <hr>
        <small>Fecha: {timestamp}</small>
        """
    })

    # Email para ti (notificación)
    resend.Emails.send({
        "from": "Formulario Web <no-reply@mail.gleniaymacondo.com>",
        "to": ["gleniazuniga08@gmail.com"],
        "subject": "📩 Nuevo contacto desde la web",
        "html": f"""
        <h2>Nuevo mensaje recibido</h2>

        <p><strong>Nombre:</strong> {contact.name}</p>
        <p><strong>Email:</strong> {contact.email}</p>
        <p><strong>Teléfono:</strong> {contact.phone}</p>

        <p><strong>Mensaje:</strong></p>
        <p>{contact.message}</p>

        <p><strong>Productos:</strong> {contact.products}</p>

        <hr>
        <small>Fecha: {timestamp}</small>
        """
    })