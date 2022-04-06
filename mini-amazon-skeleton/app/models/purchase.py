from flask import current_app as app


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