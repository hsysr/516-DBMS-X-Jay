from flask import current_app as app


class Inventory:
    def __init__(self, pid, sid, quantity, price, description):
        self.pid = pid
        self.sid = sid
        self.quantity = quantity
        self.price = price
        self.description = description

    @staticmethod
    def get(pid, sid):
        rows = app.db.execute('''
SELECT pid, sid, quantity, price, description
FROM Inventory
WHERE pid = :pid
AND sid = :sid
''',
                              pid=pid,
                              sid=sid)
        return Inventory(*(rows[0])) if rows else None

    @staticmethod
    def get_all_by_sid(sid):
        rows = app.db.execute('''
SELECT pid, sid, quantity, price, description
FROM Inventory
WHERE sid = :sid
ORDER BY pid
''',
                              sid=sid)
        return [Inventory(*row) for row in rows]

    @staticmethod
    def change_quantity(pid, sid, quantity):
        app.db.execute('''
UPDATE Inventory
SET quantity = :quantity
WHERE pid = :pid
AND sid = :sid
''',
                              sid=sid,
                              pid=pid,
                              quantity=quantity)

    @staticmethod
    def change_price(pid, sid, price):
        app.db.execute('''
UPDATE Inventory
SET price = :price
WHERE pid = :pid
AND sid = :sid
''',
                              sid=sid,
                              pid=pid,
                              price=price)

    @staticmethod
    def change_inventory(pid, sid, quantity, price, description):
        app.db.execute('''
UPDATE Inventory
SET price = :price, quantity = :quantity, description = :description
WHERE pid = :pid
AND sid = :sid
''',
                              sid=sid,
                              pid=pid,
                              quantity=quantity,
                              price=price,
                              description=description)

    @staticmethod
    def remove_inventory(pid, sid):
        app.db.execute('''
DELETE FROM Inventory
WHERE pid = :pid
AND sid = :sid
''',
                              sid=sid,
                              pid=pid)

    @staticmethod
    def add_inventory(pid, sid, quantity, price, description):
        try:
          app.db.execute('''
INSERT INTO Inventory(pid, sid, quantity, price, description)
VALUES(:pid, :sid, :quantity, :price, :description)
''',
                              sid=sid,
                              pid=pid,
                              quantity = quantity,
                              price = price,
                              description = description)
        except Exception as e:
            # likely inventory already exist; better error checking and reporting needed;
            # the following simply prints the error to the console:
            print(str(e))
            return None
        return "success"