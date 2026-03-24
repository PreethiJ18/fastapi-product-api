from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import crud, models, schemas
from database import SessionLocal, engine
from pydantic import BaseModel, Field
from fastapi import HTTPException
import time
class PurchaseRequest(BaseModel):
    qty: int = Field(..., ge=1)

class StockResetRequest(BaseModel):
    stock: int = Field(..., ge=0)
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": "Ateko API Running"}

@app.get("/products")
def read_products(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_products(db, skip, limit)

@app.post("/products")
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    return crud.create_product(db, product)

@app.get("/products_raw")

def read_products_raw(db: Session = Depends(get_db)):
    result = db.execute("SELECT * FROM products")
    return result.fetchall()

@app.put("/products/{product_id}")
def update_product(product_id: int, product: schemas.ProductCreate, db: Session = Depends(get_db)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if db_product:
        db_product.name = product.name
        db_product.category = product.category
        db_product.price = product.price
        db.commit()
        db.refresh(db_product)
    return db_product

@app.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if db_product:
        db.delete(db_product)
        db.commit()
    return {"message": "Product deleted"}

@app.get("/products/{product_id}/stock")
def get_stock(product_id: int, db: Session = Depends(get_db)):
    p = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="product not found")
    return {"product_id": p.id, "stock": p.stock}


@app.post("/products/{product_id}/stock/reset")
def reset_stock(product_id: int, body: StockResetRequest, db: Session = Depends(get_db)):
    p = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="product not found")

    p.stock = body.stock
    db.commit()
    db.refresh(p)

    return {"ok": True, "new_stock": p.stock}


@app.post("/products/{product_id}/purchase-unsafe")
def purchase_unsafe(product_id: int, body: PurchaseRequest, db: Session = Depends(get_db)):
    p = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not p:
        raise HTTPException(status_code=404)

    if p.stock < body.qty:
        raise HTTPException(status_code=409, detail="insufficient stock")

    import time
    time.sleep(0.01)

    p.stock -= body.qty
    db.commit()
    db.refresh(p)

    return {"remaining_stock": p.stock}


@app.post("/products/{product_id}/purchase")
def purchase_safe(product_id: int, body: PurchaseRequest, db: Session = Depends(get_db)):
    with db.begin():
        p = db.query(models.Product).filter(models.Product.id == product_id).with_for_update().first()

        if not p:
            raise HTTPException(status_code=404)

        if p.stock < body.qty:
            raise HTTPException(status_code=409, detail="insufficient stock")

        p.stock -= body.qty

    return {"remaining_stock": p.stock}
    

from fastapi import HTTPException
from pydantic import BaseModel

class StockResetRequest(BaseModel):
    stock: int

@app.post("/products/{product_id}/stock/reset")
def reset_stock(product_id: int, request: StockResetRequest, db: Session = Depends(get_db)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()

    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    db_product.stock = request.stock
    db.commit()
    db.refresh(db_product)

    return {"message": "Stock reset successful", "stock": db_product.stock}
    