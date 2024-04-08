import json
import uvicorn
from database.configurations import init_db, db_session
from database.schema import ItemSchema
from database.models import Item
from fastapi import FastAPI, Depends, Request, Response, HTTPException, status
from fastapi.responses import HTMLResponse
# from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

# Initiate fastapi instance
app = FastAPI()

# Configure static route
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure template
templates = Jinja2Templates(directory="templates")


@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request":request})

@app.get("/api/todo")
def get_items(session: Session = Depends(db_session)):
    items = session.query(Item).all()
    return items

@app.post("/api/todo")
def add_item(item: ItemSchema, session: Session = Depends(db_session)):
    todoitem = Item(task=item.task)
    session.add(todoitem)
    session.commit()
    session.refresh(todoitem)
    return todoitem

@app.patch("/api/todo/{id}")
def update_item(id: int, item: ItemSchema, session: Session = Depends(db_session)):
    todoitem = session.query(Item).get(id)
    if todoitem:
        todoitem.task = item.task
        session.commit()
        session.close()
        response = json.dumps({"msg": "Item has been updated."})
        return Response(content=response, media_type='application/json', status_code=200)
    else:
        response = json.dumps({"msg": "Item not found"})
        return Response(content=response, media_type='application/json', status_code=404)
    
@app.delete("/api/todo/{id}")
def delete_item(id: int, session: Session = Depends(db_session)):
    todoitem = session.query(Item).get(id)
    if todoitem:
        session.delete(todoitem)
        session.commit()
        session.close()
        response = json.dumps({"msg": "Item has been deleted."})
        return Response(content=response, media_type='application/json', status_code=200)
    else:
        response = json.dumps({"msg": "Item not found"})
        return Response(content=response, media_type='application/json', status_code=404)
    
if __name__ == "__main__":
    uvicorn.run(app, host="127.1.2.3", port=8000)