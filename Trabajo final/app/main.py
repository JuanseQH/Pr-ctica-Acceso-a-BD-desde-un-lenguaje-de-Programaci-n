from fastapi import FastAPI, HTTPException, Request
from sqlalchemy import create_engine, Column, String, Integer, MetaData, Table, UniqueConstraint
from sqlalchemy.orm import sessionmaker

# SQLite Database URL
DATABASE_URL = "sqlite:///test.db"

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create a new database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a FastAPI instance
app = FastAPI()

# Define the User table
metadata = MetaData()

users = Table(
    "users",
    metadata,
    Column("email", String, index=True, primary_key = True),
    Column("password", String),
    UniqueConstraint("email")
)

def db_execute(stmt):
    with engine.connect() as conn:
        result = conn.execute(stmt)
        conn.commit()
    return result

# Routes

@app.get("/users/")
def read_users():
    query = users.select()

    result = db_execute(query).all()

    # Convertir la lista de tuplas a un diccionario
    users_dict_list = [{'email': row[0], 'password': row[1]} for row in result]
    return users_dict_list

@app.get("/users/{email}")
def read_user(email: str):
    query = users.select().where(users.c.email == email)
    
    result = db_execute(query).first()

    users_dict = {'email': result[0], 'password': result[1]} 
    return users_dict

@app.post("/users/")
async def create_user(request: Request):
    user_data = await request.json()
    email = user_data.get("email")
    password = user_data.get("password")

    new_user = users.insert().values(email=email, password=password)
    try:
        db_execute(new_user)
    except: 
        raise HTTPException(status_code=404, detail="No se ha podido crear el ususario")
    return {"email": email}

# Update user by email
@app.put("/users/{email}")
async def update_user(email: str, request: Request):
    user_data = await request.json()
    new_email = user_data.get("email")
    new_password = user_data.get("password")

    stmt = users.update().where(users.c.email == email).values(email=new_email, password=new_password)
    result = db_execute(stmt)
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="No se ha podido actualizar el usuario")
    
    return {"email": new_email}

# Delete user by email
@app.delete("/users/{email}")
async def delete_user(email: str):
    stmt = users.delete().where(users.c.email == email)
    result = db_execute(stmt)
    return {"message": "User deleted successfully"}
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="No se pudo eliminar el usuario")    

# create the database tables
metadata.create_all(bind=engine)
