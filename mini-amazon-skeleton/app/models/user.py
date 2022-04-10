from flask_login import UserMixin
from flask import current_app as app
from werkzeug.security import generate_password_hash, check_password_hash

from .. import login


class User(UserMixin):
    def __init__(self, id, email, firstname, lastname, address, balance):
        self.id = id
        self.email = email
        self.firstname = firstname
        self.lastname = lastname
        self.address = address
        self.balance = balance

    @staticmethod
    def get_by_auth(email, password):
        rows = app.db.execute("""
SELECT password, id, email, firstname, lastname, address, balance
FROM Users
WHERE email = :email
""",
                              email=email)
        if not rows:  # email not found
            return None
        elif not check_password_hash(rows[0][0], password):
            # incorrect password
            return None
        else:
            return User(*(rows[0][1:]))

    @staticmethod
    def email_exists(email):
        rows = app.db.execute("""
SELECT email
FROM Users
WHERE email = :email
""",
                              email=email)
        return len(rows) > 0
       
    @staticmethod
    def email_exists_for_edit_profile(id,email):
        rows = app.db.execute("""
SELECT id,email
FROM Users
WHERE email = :email
""",
                              email=email)
        if len(rows) == 0:
            return False
        return rows[0][0]!=id
                              

    @staticmethod
    def register(email, password, firstname, lastname,address,balance):
        try:
            rows = app.db.execute("""
INSERT INTO Users(email, password, firstname, lastname, address, balance )
VALUES(:email, :password, :firstname, :lastname, :address, :balance)
RETURNING id
""",
                                  email=email,
                                  password=generate_password_hash(password),
                                  firstname=firstname, lastname=lastname,address=address,balance=balance)
            id = rows[0][0]
            return User.get(id)
        except Exception as e:
            # likely email already in use; better error checking and reporting needed;
            # the following simply prints the error to the console:
            print(str(e))
            return None

    @staticmethod
    def editProfile(id, email, password, firstname, lastname,address):
        try:
            rows = app.db.execute("""
UPDATE users SET email=:email, password=:password,firstname=:firstname,lastname=:lastname,address=:address
WHERE users.id = :id
RETURNING id
""",
                                  email=email,
                                  password=generate_password_hash(password),
                                  firstname=firstname, lastname=lastname,address=address,id=id)
            id = rows[0][0]
            return User.get(id)
        except Exception as e:
            # likely email already in use; better error checking and reporting needed;
            # the following simply prints the error to the console:
            print(str(e))
            return None

    @staticmethod
    def balanceTopup(id, prev_balance, topup):
        try:
            new_balance = prev_balance + topup
            rows = app.db.execute("""
UPDATE users SET balance=:balance
WHERE users.id=:id
RETURNING id
""",
                    balance=new_balance, id=id)
            id = rows[0][0]
            return User.get(id)
        except Exception as e:
            print(str(e))
            return None
            
    @staticmethod
    def balanceWithdraw(id, prev_balance, withdraw):
        try:
            new_balance = prev_balance - withdraw
            rows = app.db.execute("""
UPDATE users SET balance=:balance
WHERE users.id=:id
RETURNING id
""",
                    balance=new_balance, id=id)
            id = rows[0][0]
            return User.get(id)
        except Exception as e:
            print(str(e))
            return None
            
            
    @staticmethod
    @login.user_loader
    def get(id):
        rows = app.db.execute("""
SELECT id, email, firstname, lastname, address, balance
FROM Users
WHERE id = :id
""",
                              id=id)
        return User(*(rows[0])) if rows else None
        
    @staticmethod
    def getPublicView(id):
        isSeller = app.db.execute('''
SELECT pid FROM inventory WHERE sid=:uid
''',        uid=id)
        rows = app.db.execute("""
SELECT id, email, firstname, lastname, address, balance
FROM Users
WHERE id = :id
""",
                              id=id)
        userInfo = User(*(rows[0])) if rows else None
        return isSeller, userInfo
        
    @staticmethod
    def get_by_purchase_id(purchase_id):
        rows = app.db.execute("""
SELECT DISTINCT users.id, email, firstname, lastname, address, balance
FROM users
JOIN purchases
ON purchases.uid = users.id AND purchases.id = :purchase_id
""",
                              purchase_id = purchase_id)
        if rows:
            ans = User(*(rows[0]))
            ans.id = -1
            ans.email = ""
            ans.balance = -1
            return ans
        return None
        
class SellerFeedback:
    def __init__(self, uid, sid, rating, review, time_submitted, vote):
        self.uid = uid
        self.sid = sid
        self.rating = rating
        self.review = review
        self.time_submitted = time_submitted
        self.vote = vote
    
    @staticmethod
    def getFeedback(sid):
        rows = app.db.execute('''
SELECT * FROM seller_feedback
WHERE sid = :sid
    ''',    sid=sid)
        return [SellerFeedback(*row) for row in rows]
    
