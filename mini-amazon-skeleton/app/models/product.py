from flask import current_app as app


class Product:
    def __init__(self, id, name, price, available):
        self.id = id
        self.name = name
        self.price = price
        self.available = available
        self.quantity = 0

    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT id, name, price, available
FROM Products
WHERE id = :id
''',
                              id=id)
        return Product(*(rows[0])) if rows is not None else None

    @staticmethod
    def get_all(available=True):
        rows = app.db.execute('''
SELECT id, name, price, available
FROM Products
WHERE available = :available
''',
                              available=available)
        return [Product(*row) for row in rows]


    @staticmethod
    def add_product(name, price):
        try:
            rows = app.db.execute("""
INSERT INTO Products(name, price, available)
VALUES(:name, :price, true)
RETURNING id
""",
                                  name = name,
                                  price = price)
            id = rows[0][0]
            return Product.get(id)
        except Exception as e:
            # likely product already exist; better error checking and reporting needed;
            # the following simply prints the error to the console:
            print(str(e))
            return None