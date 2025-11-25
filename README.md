# **Nexus Finance \- Enterprise Microcredit Platform 🚀**

**Plataforma SaaS distribuida para la gestión inteligente de microcréditos, integrando un Core Bancario en Java con un Motor de Riesgo basado en IA (Python).**

## **📋 Visión General del Sistema**

**Nexus Finance** resuelve la complejidad de otorgar créditos mediante una arquitectura desacoplada. El sistema permite registrar clientes, solicitar préstamos y, mediante una **Capa Anticorrupción (ACL)**, consultar un motor externo de riesgo para aprobar o rechazar solicitudes en tiempo real, generando automáticamente cronogramas de pago con precisión financiera.

### **🏗️ Arquitectura de Contenedores**

El sistema se compone de 3 servicios orquestados que se comunican en una red privada:

```bash
graph LR
    A\[Client (Postman/Web)\] \--\>|HTTP REST| B(nexus-backend-core)
    B \--\>|JDBC| C\[(nexus-db)\]
    B \--\>|Internal HTTP/Feign| D(nexus-risk-engine)`
```

1. **nexus-backend-core (Spring Boot 3.4):**
   - Gestión de Clientes y Préstamos (DDD/CQRS).
   - Cálculo de Amortización (Sistema Francés).
   - Orquestador de la transacción.
2. **nexus-risk-engine (Python FastAPI):**
   - Microservicio _stateless_.
   - Evalúa reglas heurísticas (Ingresos vs Deuda, Edad, Historial) para determinar el CreditScore.
3. **nexus-db (MySQL 8.0):**
   - Persistencia relacional robusta para el núcleo transaccional.

## **🚀 Guía de Inicio Rápido (Despliegue)**

### **Prerrequisitos**

- [Docker Desktop](https://www.docker.com/products/docker-desktop) instalado y corriendo.
- Git.

### **Pasos para Ejecutar**

1. **Clonar el Repositorio:**  
   git clone \[https://github.com/tu-usuario/nexus-finance.git\](https://github.com/tu-usuario/nexus-finance.git)  
   cd nexus-finance

2. Levantar el Ecosistema:  
   Ejecuta el orquestador. Esto compilará el código Java y Python, construirá las imágenes y levantará los contenedores.  
   docker-compose up \--build

   _(La primera vez puede tardar unos minutos descargando las dependencias de Maven y Pip)._

3. Verificar Estado:  
   Una vez que veas los logs de Spring Boot y Uvicorn, el sistema está listo.

## **🔌 Puntos de Acceso (Endpoints)**

| Servicio             | URL Local                                                                                                      | Descripción                                                        | Credenciales            |
| :------------------- | :------------------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------- | :---------------------- |
| **Backend API Docs** | [http://localhost:8080/swagger-ui.html](https://www.google.com/search?q=http://localhost:8080/swagger-ui.html) | Swagger UI para probar endpoints de Clientes y Préstamos.          | \-                      |
| **Risk Engine Docs** | [http://localhost:8000/docs](https://www.google.com/search?q=http://localhost:8000/docs)                       | Swagger UI del motor de IA (Python).                               | \-                      |
| **Base de Datos**    | localhost:3307                                                                                                 | Conexión directa a MySQL (Mapeado al 3307 para evitar conflictos). | User: root / Pass: root |

## **🧪 Flujo de Prueba Sugerido (End-to-End)**

Para verificar la integración entre Java y Python:

1. **Crear Cliente (Java):**
   - POST /api/v1/clients \-\> Crea un perfil básico.
2. **Solicitar Préstamo (Java):**
   - POST /api/v1/loans \-\> Crea una solicitud con estado REQUESTED.
3. **Aprobar Préstamo (Java \-\> Python \-\> Java):**
   - POST /api/v1/loans/{id}/approve
   - **Body:** { "monthlyIncome": 5000, "monthlyDebt": 200, "clientAge": 30 }
   - _Resultado:_ El Backend llamará al Risk Engine. Si Python aprueba, Java calculará las cuotas y devolverá el préstamo ACTIVE.

## **🛠️ Configuración del Entorno (Variables)**

El archivo docker-compose.yml gestiona la configuración de red automáticamente.

- **Sobrescritura de URLs:**
  - SPRING_DATASOURCE_URL: Apunta automáticamente al contenedor nexus-db.
  - RISK_ENGINE_URL: Apunta automáticamente a http://nexus-risk-engine:8000.

_No es necesario configurar archivos .env manualmente para la prueba local._

## **👤 Autor**

**Angel Antonio Cancho Corilla** \- _Ingeniero de Software Full Stack_
