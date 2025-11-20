from flask import Flask, request, jsonify 
from dataclasses import asdict, dataclass
from typing import Dict

app = Flask(__name__) 


@dataclass
class Student:
    id: int
    name: str
    age: int | None = None
    email: str | None = None

students: Dict[int, Student] = {}


def bad_request(msg: str, status: int = 400):
    """Retorna una respuesta de error JSON con el código de estado dado."""
    return jsonify({"error": msg}), status

# --- Rutas de la API ---

@app.get("/health")
def health():
    """Ruta de salud del servicio."""
    return jsonify({"status": "ok"}), 200

@app.get("/students")
def get_all_students():
    """Devuelve todos los estudiantes registrados."""
    all_students = [asdict(s) for s in students.values()]
    return jsonify(all_students), 200

@app.post("/student")
def create_student():
    """
    Crea un nuevo estudiante a partir de JSON.
    Ejemplo de cuerpo:
    {
    "id": 1,
    "name": "Wilfredo Sirin",
    "age": 22,
    "email": "wsirinma@email.com"
    }
    """

    if not request.is_json:
        return bad_request("Content-Type debe ser application/json", status=415)
    
    data = request.get_json(silent=True) or {}
    
    if not data:
        return bad_request("El cuerpo de la petición no puede estar vacío.")

    missing = [k for k in ("id", "name") if k not in data]
    if missing:
        return bad_request(f"Faltan los campos requeridos: {', '.join(missing)}")

    try:
        stu_id = int(data["id"])
    except Exception:
        return bad_request("El campo ID debe ser un número entero válido.")
    
    if stu_id in students:
        return bad_request(f"Ya existe un estudiante con el ID: {stu_id}", status=409)
    
    try:
        name = str(data["name"]).strip()
        if not name:
            return bad_request("El campo nombre no puede estar vacío.")
    except Exception: 
        return bad_request("El campo nombre no es válido.")

    age = None 
    if "age" in data and data["age"] is not None:
        try:
            age = int(data["age"])
        except Exception:
            return bad_request("El campo age debe ser un número entero válido.")
        
    email = None
    if "email" in data and data["email"] is not None:
        email = str(data["email"]).strip()
        if not email:
            email = None
            
    student = Student (id = stu_id, name=name, age=age, email=email)
    students[stu_id] = student

    print("Nuevo estudiante: ", asdict(student))
    return jsonify(asdict(student)), 201

    @app.get("/students/<int:student_id>")
    def get_student_by_id(student_id: int):
        """devuelve un estudiante por ID"""
        student = students.get(student_id)
        if not student:
            return bad_request("No existe el estudiante con el identificador enviado", 404)
        return jsonify(asdict(student)), 200



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)