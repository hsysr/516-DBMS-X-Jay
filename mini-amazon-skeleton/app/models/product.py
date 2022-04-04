from flask import current_app as app


class Product:
    def __init__(self, id, name, available, category, minprice=None):
        self.id = id
        self.name = name
        self.available = available
        self.category = category
        self.minprice = minprice


    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT id, name, available, category
FROM Products
WHERE id = :id
''',
                              id=id)
        return Product(*(rows[0])) if rows is not None else None

    @staticmethod
    def get_by_name(name):
        rows = app.db.execute('''
SELECT id, name, available, category
FROM Products
WHERE name = :name
''',
                              name=name)
        return Product(*(rows[0])) if rows is not None else None

    @staticmethod
    def get_all(available=True):
        rows = app.db.execute('''
SELECT Products.id, Products.name, Products.available, Products.category, MIN(Inventory.price) as minprice
FROM Products, Inventory
WHERE Products.available = :available and Inventory.pid=Products.id
GROUP BY Products.id
''',
                              available=available)
        return [Product(*row) for row in rows]

    @staticmethod
    def get_matching_keyword(namekeyword, categorykeyword, ordering, available=True):
        rows = app.db.execute(f'''
SELECT Products.id, Products.name, Products.available, Products.category, MIN(Inventory.price) as minprice
FROM Products, Inventory
WHERE Products.available = '{available}' and Inventory.pid=Products.id and Products.name LIKE '{"%"+namekeyword+"%"}' and Products.category LIKE '{"%"+categorykeyword+"%"}'
GROUP BY Products.id
ORDER BY {ordering}
''')
        return [Product(*row) for row in rows]
        

    @staticmethod
    def add_product(name, category):
        try:
            rows = app.db.execute("""
INSERT INTO Products(name, available, category)
VALUES(:name, true, :category)
RETURNING id
""",
                                  name = name,
                                  category = category)
            id = rows[0][0]
            return Product.get(id)
        except Exception as e:
            return Product.get_by_name(name)

    @staticmethod
    def getSellerInfo(pid):
        rows = app.db.execute('''
SELECT users.id, users.firstname, users.lastname, inventory.price, inventory.quantity, inventory.description
FROM inventory, users
WHERE inventory.pid = :id AND inventory.sid = users.id
''',
                              id=pid)
        return rows if rows is not None else None
        
    @staticmethod
    def addToCart(uid,pid,sid,quantity):
        existQt = app.db.execute('''
SELECT quantity FROM Cart
WHERE uid=:uid AND pid=:pid AND sid=:sid
''',
                uid=uid, pid=pid, sid=sid)
        if len(existQt) > 0:
            newQt = existQt[0][0] + quantity
            rows = app.db.execute('''
    UPDATE Cart
    SET quantity = :newQt
    WHERE uid=:uid AND pid=:pid AND sid=:sid
    RETURNING pid
    ''',
                newQt=newQt, uid=uid, pid=pid, sid=sid)
            return rows[0] if rows is not None else None
            
        else:
            rows = app.db.execute('''
    INSERT INTO Cart(uid, pid, sid, quantity)
    VALUES(:uid, :pid, :sid, :quantity)
    RETURNING pid
    ''',            uid=uid, pid=pid, sid=sid,quantity=quantity)
            return rows[0] if rows is not None else None