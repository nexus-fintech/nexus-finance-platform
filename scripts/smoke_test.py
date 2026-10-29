"""Recorre la plataforma levantada de punta a punta, como lo harían un cliente y un analista:
registro, perfil, solicitud de préstamo y aprobación, que pasa por el motor de riesgo. También
comprueba reglas de seguridad: el registro no da rol de administrador, un cliente no aprueba su
propio préstamo y un cuerpo inválido es un 400. Solo usa la biblioteca estándar de Python.

    NEXUS_ADMIN_USERNAME=... NEXUS_ADMIN_PASSWORD=... python scripts/smoke_test.py [http://localhost:8080]
"""

import json
import os
import sys
import time
import urllib.error
import urllib.request

API = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8080").rstrip("/") + "/api/v1"


def call(method, path, body=None, token=None, raw=None):
    """Returns (status, JSON answer or None). An HTTP error status is returned, not raised."""
    data = raw if raw is not None else (json.dumps(body).encode() if body is not None else None)
    request = urllib.request.Request(API + path, data=data, method=method)
    request.add_header("Content-Type", "application/json")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = response.read()
            return response.status, json.loads(payload) if payload else None
    except urllib.error.HTTPError as error:
        return error.code, None


def ok(method, path, body=None, token=None):
    """The JSON answer of a call that must succeed."""
    status, payload = call(method, path, body, token)
    if not 200 <= status < 300:
        sys.exit(f"FALLÓ: {method} {path} respondió {status}")
    return payload


def expect(description, actual, wanted):
    if actual != wanted:
        sys.exit(f"FALLÓ: {description} (se esperaba {wanted!r}, llegó {actual!r})")
    print(f"  ok: {description}")


def main():
    admin_user = os.environ.get("NEXUS_ADMIN_USERNAME")
    admin_password = os.environ.get("NEXUS_ADMIN_PASSWORD")
    if not admin_user or not admin_password:
        sys.exit("Exporta NEXUS_ADMIN_USERNAME y NEXUS_ADMIN_PASSWORD, los mismos de .env")
    run = int(time.time())
    user, password = f"cliente-{run}", f"Clave-{run}"

    print("1. Un cliente se registra, pidiendo además ser administrador, e ingresa")
    created = ok("POST", "/authentication/sign-up", {"username": user, "password": password, "roles": ["ROLE_ADMIN"]})
    expect("el registro crea un cliente", created["roles"], ["ROLE_CLIENT"])
    expect("un cuerpo inválido es un 400", call("POST", "/authentication/sign-up", raw=b"{roto")[0], 400)
    client_token = ok("POST", "/authentication/sign-in", {"username": user, "password": password})["token"]

    print("2. Crea su perfil y pide un préstamo")
    profile = ok("POST", "/clients", {
        "firstName": "Ana", "lastName": "Torres", "email": f"{user}@example.com", "dni": f"{run % 100_000_000:08d}",
        "street": "Av. Arequipa 123", "city": "Lima", "zipCode": "15001", "country": "Perú",
    }, client_token)
    loan = ok("POST", "/loans", {
        "clientId": profile["id"], "amount": 3000, "termInMonths": 6, "annualInterestRate": 0.2,
    }, client_token)
    expect("la solicitud queda registrada", loan["status"], "REQUESTED")

    print("3. El cliente intenta aprobar su propio préstamo")
    evaluation = {"clientAge": 30, "monthlyIncome": 5000, "monthlyDebt": 200}
    expect("aprobar es solo del administrador", call("POST", f"/loans/{loan['id']}/approve", evaluation, client_token)[0], 403)

    print("4. El administrador lo aprueba: el backend consulta al motor de riesgo")
    admin_token = ok("POST", "/authentication/sign-in", {"username": admin_user, "password": admin_password})["token"]
    approved = ok("POST", f"/loans/{loan['id']}/approve", evaluation, admin_token)
    expect("un perfil de bajo riesgo queda activo", approved["status"], "ACTIVE")
    detail = ok("GET", f"/loans/{loan['id']}", token=client_token)
    expect("el cliente ve su cronograma, una cuota por mes", len(detail["schedule"]), 6)

    print("Plataforma verificada de punta a punta.")


if __name__ == "__main__":
    main()
