Levanta MySQL en docker
> docker compose up -d

corre la API 
> python api_service.py


configuración de postaman:
GET: http://localhost:5000/health

JSON 

Body: 
{
    "type": "Email",
    "recipient": "test@ejemplo.com",
    "body": "Registro de prueba en BD."
}

probar en postman:
GET http://localhost:5000/health
