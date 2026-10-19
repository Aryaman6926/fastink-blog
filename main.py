from fastapi import FastAPI, Form, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from starlette.templating import Jinja2Templates

DATABASE_URL = "sqlite:///./blogs.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()
app.mount("/static", StaticFiles(directory="."), name="static")

class BLOGCREATE(Base):
    __tablename__ = "blog"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(String, nullable=True)
    author = Column(String, nullable=True)

Base.metadata.create_all(bind=engine)
templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request, db: Session = Depends(get_db)):
    blogs = db.query(BLOGCREATE).all()
    return templates.TemplateResponse(request, "index.html", {"blogs": blogs})

@app.get("/editor", response_class=HTMLResponse)
def editor_page(request: Request):
    return templates.TemplateResponse(request, "editor.html")

@app.post("/blog", response_model=None)
def create_blog(
    title: str = Form(...),
    content: str = Form(None),
    author: str = Form(None),
    db: Session = Depends(get_db)
):
    db_blog = BLOGCREATE(title=title, content=content, author=author)
    db.add(db_blog)
    db.commit()
    db.refresh(db_blog)
    return RedirectResponse(url="/", status_code=303)

@app.get("/blog/{blog_id}", response_class=HTMLResponse)
def read_blog(request: Request, blog_id: int, db: Session = Depends(get_db)):
    blog = db.query(BLOGCREATE).filter(BLOGCREATE.id == blog_id).first()
    return templates.TemplateResponse(request, "post.html", {"blog": blog})