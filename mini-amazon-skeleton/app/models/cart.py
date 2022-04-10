from flask import current_app as app
from .user import User


class Cart:
    def __init__(self, uid, pid, productname, sid, sellerlastname, sellerfirstname,  quantity, unitprice):
        self.uid = uid
        self.pid = pid
        self.productname = productname
        self.sid = sid
        self.sellerlastname = sellerlastname
        self.sellerfirstname = sellerfirstname
        self.quantity = quantity
        self.unitprice = unitprice

    @staticmethod
    def get(uid):
        rows = app.db.execute('''
SELECT cart.uid, cart.pid, products.name, cart.sid, users.lastname, users.firstname, cart.quantity, inventory.price
FROM products, cart, users, inventory
WHERE cart.uid = :uid AND cart.pid=products.id
    AND cart.sid=users.id
    AND inventory.pid=products.id   AND inventory.sid=users.id
''',
                              uid=uid)
        return [Cart(*row) for row in rows] if rows is not None else None
        
    @staticmethod
    def checkout(uid):
        cart = Cart.get(uid)
        totalprice = 0
        currentQt = []
        for cartItem in cart:
            checkQt = app.db.execute('''
                SELECT inventory.quantity
                FROM inventory
                WHERE  inventory.pid=:pid AND inventory.sid=:sid
                AND inventory.quantity >= :quantity
                ''',  pid=cartItem.pid, sid=cartItem.sid, quantity=cartItem.quantity)
            if not checkQt:
                return "Sorry, no enough quantity for "+str(cartItem.productname)+" from "+ str(cartItem.sellerfirstname)+" "+str(cartItem.sellerlastname)
            currentQt.append(checkQt[0][0])
            totalprice += cartItem.quantity * cartItem.unitprice
            
        balance = User.get(uid).balance
        if balance < totalprice:
            return "Sorry, no enough balance on your account to pay"
           
        prev_order_id = app.db.execute('''SELECT MAX(id) FROM purchases ''')
        order_id = (prev_order_id[0][0] + 1) if prev_order_id[0][0] else 1
        for idx, cartItem in enumerate(cart):
            newQt = currentQt[idx] - cartItem.quantity
            row1 = app.db.execute('''
                UPDATE inventory
                SET quantity = :newQt
                WHERE pid=:pid AND sid=:sid
                RETURNING pid
                ''',   newQt=newQt, pid=cartItem.pid, sid=cartItem.sid)
            if not row1:
                return "Oops, something goes wrong when processing your order"
                    
            row2 = app.db.execute('''
                DELETE FROM Cart
                WHERE uid=:uid AND pid=:pid AND sid=:sid
                RETURNING pid
                ''', uid=uid, pid=cartItem.pid, sid=cartItem.sid)
            if not row2:
                return "Oops, something goes wrong when processing your order"

            row3 = app.db.execute('''
                INSERT INTO purchases(id, uid, pid, sid, finalprice, quantity)
                VALUES (:id, :uid, :pid, :sid, :price, :quantity)
                RETURNING id
                ''', id=order_id, uid=uid, pid=cartItem.pid, sid=cartItem.sid, price=cartItem.unitprice, quantity=cartItem.quantity)
            if not row3:
                return "Oops, something goes wrong when processing your order"
                    
        row4 = app.db.execute('''UPDATE Users SET balance=:leftmoney WHERE id=:uid RETURNING id
                ''', leftmoney=balance-totalprice, uid=uid)
        if not row4:
            return "Oops, something goes wrong when processing your order"

        return "success"
