# CONNECTOR
import sqlite3

class Connector():
    
    def __init__(self, db):
        self.conn = sqlite3.connect(db)
        self.c = self.conn.cursor()
        
    def get(self, table):
        self.c.execute(f"SELECT oid, * from {table}")
        return self.c.fetchall()
    
    def get_on(self, table, oid):
        self.c.execute(f"SELECT * from {table} WHERE oid = {oid}")
        return self.c.fetchall()[0]
    
    def add(self, table, values):
        sql = f"INSERT INTO {table} VALUES ("
        for value in values:
            sql+= f"'{value}',"
        sql = sql[:-1] + ")"
        print(sql)
        self.c.execute(sql)
        self.conn.commit()
        
    def update_on(self, table, oid, values):
        sql = f"UPDATE {table} SET "
        for value_name, value in values.items():
            sql += f"{value_name} = '{value}',"
        sql = sql[0:-1] + f" WHERE oid = {oid}"
        self.c.execute(sql)
        self.conn.commit()
    
    def delete(self, table):
        self.c.execute(f"DELETE from {table}")
        self.conn.commit()
    
    def delete_on(self, table, oid):
        self.c.execute(f"DELETE from {table} WHERE oid={oid}")
        self.conn.commit()
    
    def list_(self, key, day):
        self.c.execute(f"SELECT distinct {key} FROM daily WHERE jour ='{day}'")
        _list = [val[0] for val in self.c.fetchall()]
        return _list
    
    def daily_report(self, day):
        """
        returns a list of rows : 
        planter1, seed1, seed2, ..., seedN, total, gross
        planter2, seed1, seed2, ..., seedN, total, gross
        ...
        planterM, seed1, seed2, ..., seedN, total, gross
        and a tuple : 
        (crew total, commission)
        """
        pid_list = self.list_('pid',day)
        sid_list = self.list_('sid', day)
        planter_list = []
        for pid in pid_list:
            self.c.execute(f"SELECT lname FROM planters WHERE oid ={pid}")
            planter_list.append(self.c.fetchall()[0][0])
        header = ["Planter"]
        for sid in sid_list:
            header.append(sid)
        header += ["Total", "Gross"]
        print(header)
        
        rows = []
        commission = 0
        crew_total = 0
        for planter in planter_list:
            row = [planter]
            planter_total = 0
            planter_gross = 0
            for sid in sid_list:
                self.c.execute(f"SELECT price FROM seedlots WHERE code = '{sid}'")
                seed_price = self.c.fetchall()[0][0]
                self.c.execute(f"SELECT (boxes*seedlots.box_size + bndls*seedlots.bndl_size) FROM daily JOIN seedlots ON sid = seedlots.code WHERE jour = '{day}' AND sid='{sid}'")
                seed_total = self.c.fetchall()[0][0]
                row.append(seed_total)
                planter_total += seed_total
                planter_gross += seed_total * seed_price
            commission += planter_gross * 0.15
            crew_total += planter_total
            row = row + [planter_total, round(planter_gross,2)]
            rows.append(row)
        return rows, (round(commission,2), crew_total)
        
        
        
        
    
c = Connector('../dayrates.db')
print(c.daily_report('2021-10-15'))