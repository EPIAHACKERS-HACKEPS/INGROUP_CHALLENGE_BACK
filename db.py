from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def addAndCommit(*models):
    
    if len(models) == 0: return False
    
    for model in models:
        if model: db.session.add(model)
        
    db.session.commit()
    
    return True

def deleteAndCommit(*models):
    
    if len(models) == 0: return False
    
    for model in models:
        if model: db.session.delete(model)
        
    db.session.commit()
    
    return True