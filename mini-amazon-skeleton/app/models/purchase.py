from flask import current_app as app
from datetime import datetime

class Purchase:
    def __init__(self, id, uid, pid, time_purchased = None, fulfillstate = None, finalprice = None, quantity = None):
        self.id = id
        self.uid = uid
        self.pid = pid
        self.time_purchased = time_purchased
        self.fulfillstate = fulfillstate
        self.finalprice = finalprice
        self.quantity = quantity

    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT id, uid, pid, time_purchased
FROM Purchases
WHERE id = :id
''',
                              id=id)
        return Purchase(*(rows[0])) if rows else None

    @staticmethod
    def get_all_by_uid_since(uid, since):
        rows = app.db.execute('''
SELECT id, uid, pid, time_purchased
FROM Purchases
WHERE uid = :uid
AND time_purchased >= :since
ORDER BY time_purchased DESC
''',
                              uid=uid,
                              since=since)
        return [Purchase(*row) for row in rows]

    @staticmethod
    def get_all_unfullfilled_by_sid(sid):
        rows = app.db.execute('''
SELECT id
FROM purchases
WHERE sid = :sid
GROUP BY id
HAVING NOT BOOL_AND(fulfillstate)
ORDER BY MIN(time_purchased) DESC
''',
                              sid = sid)
        return [int(*row) for row in rows]

    @staticmethod
    def get_all_by_sid(sid):
        rows = app.db.execute('''
SELECT id
FROM purchases
WHERE sid = :sid
GROUP BY id
ORDER BY MIN(time_purchased) DESC
''',
                              sid = sid)
        return [int(*row) for row in rows]

    @staticmethod
    def get_all_fullfilled_by_sid(sid):
        rows = app.db.execute('''
SELECT id
FROM purchases
WHERE sid = :sid
GROUP BY id
HAVING BOOL_AND(fulfillstate)
ORDER BY MIN(time_purchased) DESC
''',
                              sid = sid)
        return [int(*row) for row in rows]
    
    @staticmethod
    def get_info(id):
        rows = app.db.execute('''
SELECT TO_CHAR(MIN(time_purchased),'YYYY-MM-DD HH24:MI:SS'), BOOL_AND(fulfillstate)
FROM purchases
WHERE id = :id
GROUP BY id
''',
                              id = id)
        return str(rows[0][0]), bool(rows[0][1]) if rows else None

    @staticmethod
    def get_by_id_sid(id, sid):
        rows = app.db.execute('''
SELECT id, uid, pid, time_purchased, fulfillstate, finalprice, quantity
FROM purchases
WHERE id = :id AND sid = :sid

''',
                              id = id,
                              sid = sid)
        return [Purchase(*row) for row in rows]

    @staticmethod
    def fulfill(id, pid, sid):
        app.db.execute('''
UPDATE Purchases
SET fulfillstate = true
WHERE id = :id AND pid = :pid AND sid = :sid
''',
                              id = id,
                              pid = pid,
                              sid = sid
)


class PurchaseSum:
    def __init__(self, orderid, totalprice, totalQt, time_purchased, isFulfill):
        self.orderid = orderid
        self.totalprice = totalprice
        self.totalQt = totalQt
        self.time_purchased = time_purchased
        self.isFulfill = isFulfill

    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT id, uid, pid, time_purchased
FROM Purchases
WHERE id = :id
''',
                              id=id)
        return PurchaseSum(*(rows[0])) if rows else None

    @staticmethod
    def get_all_by_uid_since(uid, since):
        rows = app.db.execute('''
SELECT id, SUM(finalprice*quantity),SUM(quantity), MAX(time_purchased) as time, EVERY(fulfillstate)
FROM Purchases
WHERE uid = :uid AND time_purchased >= :since
GROUP BY id
ORDER BY time DESC
''',
            uid=uid, since=since)
        return [PurchaseSum(*row) for row in rows]
  
class OrderDetail:
    def __init__(self, pid, productname, sid, sellerlastname, sellerfirstname,  quantity, final_unitprice, fulfilled):
        self.pid = pid
        self.productname = productname
        self.sid = sid
        self.sellerlastname = sellerlastname
        self.sellerfirstname = sellerfirstname
        self.quantity = quantity
        self.final_unitprice = final_unitprice
        self.fulfilled = fulfilled

    @staticmethod
    def getOrderDetail(orderid):
        uidRow = app.db.execute('''
SELECT MAX(uid) FROM purchases
WHERE id=:id GROUP BY id
''',     id=orderid)

        orderRows = app.db.execute('''
SELECT purchases.pid, products.name, purchases.sid, users.lastname, users.firstname, purchases.quantity, purchases.finalprice, purchases.fulfillstate
FROM purchases, products, users
WHERE purchases.id=:orderid
AND products.id=purchases.pid
AND users.id=purchases.sid
''',        orderid=orderid)
        return uidRow[0][0], [OrderDetail(*row) for row in orderRows]

class FilteredItem:
    def __init__(self,orderid, time_purchased, pid, productname, sid, sellerlastname, sellerfirstname, quantity, final_unitprice, fulfilled):
        self.orderid = orderid
        self.time_purchased = time_purchased
        self.pid = pid
        self.productname = productname
        self.sid = sid
        self.sellerlastname = sellerlastname
        self.sellerfirstname = sellerfirstname
        self.quantity = quantity
        self.final_unitprice = final_unitprice
        self.fulfilled = fulfilled
    
    @staticmethod
    def getFilteredItem(productNameKeyword, sellerLastNameKeyword, sellerFirstNameKeyword, date, uid):
        date = date.strftime("%Y-%m-%d")
        rows = app.db.execute(f'''
SELECT purchases.id, purchases.time_purchased, purchases.pid, products.name, purchases.sid, users.lastname, users.firstname, purchases.quantity, purchases.finalprice, purchases.fulfillstate
FROM purchases, products, users
WHERE purchases.uid=:uid
AND products.id=purchases.pid
AND users.id=purchases.sid
AND products.name LIKE '{"%"+productNameKeyword+"%"}'
AND users.lastname LIKE '{"%"+sellerLastNameKeyword+"%"}'
AND users.firstname LIKE '{"%"+sellerFirstNameKeyword+"%"}'
AND TO_CHAR(purchases.time_purchased,'YYYY-MM-DD') LIKE :date
ORDER BY purchases.time_purchased DESC
''', uid=uid, date=date)
        return  [FilteredItem(*row) for row in rows]


class Productsell:
    def __init__(self, pid, name, total_quantity):
        self.pid = pid
        self.name = name
        self.total_quantity = total_quantity


    @staticmethod
    def get_most_popular(sid):
        print(sid)
        rows = app.db.execute('''
SELECT products.id, products.name, T1.total_quantity FROM products
JOIN (SELECT pid, SUM(quantity) as total_quantity
FROM purchases 
WHERE sid = :sid
AND time_purchased > CURRENT_DATE - INTERVAL '1 month'
GROUP BY pid) T1
ON products.id = T1.pid
ORDER BY T1.total_quantity DESC
LIMIT 10
''',
                              sid=sid)
        return [Productsell(*row) for row in rows]