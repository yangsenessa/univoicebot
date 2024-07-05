from sqlalchemy.orm import Session
from transaction import User_claim_jnl
from loguru import logger

def get_user_claim_list(db:Session, user_id:str):
    return db.query(User_claim_jnl).filter(User_claim_jnl.status!='FINISH').all()

def insert_user_claim_jnl(db:Session, user_claim_jnl:User_claim_jnl):
    db.add(user_claim_jnl)
    db.commit()
