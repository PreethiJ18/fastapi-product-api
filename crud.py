from sqlalchemy.orm import Session
import models
import schemas

def get_products(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Product).offset(skip).limit(limit).all()

def create_product(db: Session, product: schemas.ProductCreate):
    try:
        with db.begin():  # TRANSACTION START

            db_product = models.Product(**product.dict())
            db.add(db_product)
            db.flush()  # ensures ID is generated

        return db_product  # auto commit

    except Exception as e:
        db.rollback()
        raise e
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product