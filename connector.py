import sqlite3
from statistics import mean, pstdev


TOTAL = "(boxes*seedlots.box_size + bndls*seedlots.bndl_size)"
GROSS = "(boxes*seedlots.box_size + bndls*seedlots.bndl_size)*seedlots.price"
def build_database():
    conn = sqlite3.connect('dayrates.db')
    c = conn.cursor()
    c.execute("""CREATE TABLE planters (
        fname text,
        lname text
        );
""")
    
    c.execute("""CREATE TABLE seedlots (
        code text,
        species text,
        price real,
        box_size int ,
        bndl_size int
        );
""")

    c.execute("""CREATE TABLE daily (
        jour text,
        pid int,
        sid text,
        boxes int,
        bndls int,
        foreign key (sid) references seedlots (code)
        foreign key (pid) references planters (code) 
        );    
""")
    c.execute("""CREATE TABLE blocks (
    code text,
    sid text,
    foreign key (sid) references seedlots(code)
    );
              """)
    
class Connector():
    
    def __init__(self, db):
        self.conn = sqlite3.connect(db)
        self.c = self.conn.cursor()
    
    def new(self): 
        # RETURNS TRUE IF ALL TABLES ARE EMPTY 
        for table in ['planters', 'seedlots', 'blocks', 'daily']: 
            self.c.execute(f'SELECT * FROM {table}')
            if (self.c.fetchall()): 
                return False
        return True


    def get(self, table):
        self.c.execute(f"SELECT oid, * from {table}")
        return self.c.fetchall()

    def get_blocks(self): 
        """
        returns a dictionary of block codes and the corresponding seeds
        { block1: [seed1, seed2, seed3],
          block2: [seed1, seed4],
          ...
          blockM: [*seeds]
          }
        """

        self.c.execute(f"SELECT DISTINCT code FROM blocks")
        block_list = [block[0] for block in self.c.fetchall()] 
        block_and_seeds = {}
        for block in block_list: 
            seed_list = []
            self.c.execute(f"SELECT DISTINCT sid FROM blocks WHERE code = '{block}'")
            seed_list = [seed[0] for seed in self.c.fetchall()]
            block_and_seeds[block] = seed_list
        return block_and_seeds

    def get_on(self, table, key, keyword='oid'):
        self.c.execute(f"SELECT * from {table} WHERE {keyword} = '{key}'")
        return self.c.fetchall()[0]

    def get_seed_oid(self, code): 
        self.c.execute(f"SELECT oid from seedlots WHERE code='{code}'")
        return self.c.fetchall()[0][0]

    def seed_code_exists(self, code): 
        self.c.execute(f"SELECT * from seedlots WHERE code='{code}'")
        return bool(self.c.fetchall())


    def in_daily(self, key, value): 
        self.c.execute(f"SELECT * FROM daily WHERE {key} = '{value}'")
        return bool(self.c.fetchall())

    def add(self, table, values):
        # raw values as a list:
        # ['john','doe']
        
        sql = f"INSERT INTO {table} VALUES ("
        for value in values:
            sql+= f"'{value}',"
        sql = sql[:-1] + ")"
        self.c.execute(sql)
        self.conn.commit()

    def next_pid(self): 
        self.c.execute('SELECT MAX(oid) FROM planters')
        self.conn.commit() 
        return self.c.fetchall()[0][0]
        
    def update_on(self, table, key, values, keyword='oid'):
        # values here is a dictionary,
        # for example with the planters table:
        # { 'fname':'John', 'lname':'Doe' }
        # or the seedlots table:
        # { 'code':SX001, 'spec':'Spruce','price':0.15,...
    
        sql = f"UPDATE {table} SET "
        for value_name, value in values.items():
            sql += f"{value_name} = '{value}',"
        sql = sql[0:-1] + f" WHERE {keyword} = '{key}'"
        self.c.execute(sql)
        self.conn.commit()
    
    def delete(self, table):
        self.c.execute(f"DELETE from {table}")
        self.conn.commit()
    
    def delete_on(self, table, key, keyword='code'):
        self.c.execute(f"DELETE from {table} WHERE {keyword}='{key}'")
        self.conn.commit()
    
    def remove_seed_from_block(self, block, sid): 
        self.c.execute(f"DELETE FROM blocks WHERE code='{block}' AND sid = '{sid}'")
        self.conn.commit() 

    def list_(self, key, day):
        self.c.execute(f"SELECT distinct {key} FROM daily WHERE jour ='{day}'")
        _list = [val[0] for val in self.c.fetchall()]
        return _list

    def day_list(self): 
        self.c.execute(f"SELECT DISTINCT jour FROM daily ORDER BY jour DESC")
        return [jour[0] for jour in self.c.fetchall()]

    def planter_list(self): 
        self.c.execute(f"SELECT oid,lname FROM planters")
        return [str(planter[0]) + " " + planter[1] for planter in self.c.fetchall()]
    
    def dummy(self): 
        # inserts one dummy row to each table
        try:
            self.add('planters',['fname','lname'])
        except:
            pass
        try:
            self.add('seedlots',['seed1','species',0,0,0])
        except:
            pass
        try:
            self.add('blocks', ['block1', 'code'])
        except:
            pass
        
    def daily_report(self, day, foreman=False):
        """
        if foreman==False:
        returns a list of rows :
        PLANTER,  seed1, seed2, ...,        seedN,  TOTAL, GROSS
        planter1, planted1, planted2, ..., plantedN, total, gross
        planter2, planted1, planted2, ..., plantedN, total, gross
        ...
        planterM, planted1, planted2, ..., plantedN, total, gross
        
        always returns the tuple : 
        (crew total, commission)
        """
        pid_list = self.list_('pid',day)
        sid_list = self.list_('sid', day)
        planter_list = []
        for pid in pid_list:
            self.c.execute(f"SELECT lname FROM planters WHERE oid ={pid}")
            planter_list.append((pid,self.c.fetchall()[0][0]))
        header = ["Planter"]
        for sid in sid_list:
            header.append(sid)
        header += ["Total", "Gross"]        
        rows = [header]
        commission = 0
        crew_total = 0
        for planter in planter_list:
            row = [planter[1]]
            planter_total = 0
            planter_gross = 0
            for sid in sid_list:
                self.c.execute(f"SELECT price FROM seedlots WHERE code = '{sid}'")
                seed_price = self.c.fetchall()[0][0]
                self.c.execute(f"SELECT {TOTAL} FROM daily JOIN seedlots ON sid = seedlots.code WHERE jour = '{day}' AND sid='{sid}' AND pid = '{planter[0]}'")
                seed_total = self.c.fetchall()[0][0]
                row.append(seed_total)
                planter_total += seed_total
                planter_gross += seed_total * seed_price
            commission += planter_gross * 0.15
            crew_total += planter_total
            row = row + [planter_total, round(planter_gross,2)]
            rows.append(row)
        if not foreman:
            return rows, (crew_total, round(commission,2))
        else:
            # used for foreman report
            return(crew_total, round(commission,2))
        
    def planter_report(self, pid, stats=False):
        """
        if stats == False: 
        returns a list of rows:
        [['Date'     'Planted'     'Earned'
         [day1     planted1     earned1],
         [day2     planted2     earned2],
         ...
         [dayM      plantedM    earnedM]]
        and a tuple:
        (total, gross)
        
        Always returns this tuple:
        (average, best,    std_dev)
        """
        self.c.execute(f"SELECT DISTINCT jour FROM daily WHERE pid = {pid} ORDER BY jour ASC")
        day_list = [day[0] for day in self.c.fetchall()]
        rows = []
        total = 0
        gross = 0
        for day in day_list:
            self.c.execute(f"SELECT {TOTAL}, {GROSS} FROM daily JOIN seedlots ON sid = seedlots.code WHERE pid = {pid} AND jour='{day}'")
            daily_data = self.c.fetchall()
            daily_total = 0
            daily_gross = 0 
            for entry in daily_data:
                daily_total += entry[0]
                daily_gross += entry[1]
            rows.append( [day, daily_total, round(daily_gross,2)] )
        planted = [row[1] for row in rows]
        grossed = [row[2] for row in rows]
        total = sum(planted)
        gross = sum(grossed)
        average = mean(planted)
        personal_best = max(planted)
        stdev = pstdev(planted)
        
        if not stats:
            return rows, (total,gross), (round(average,2),personal_best, round(stdev,2))
        else:
            # used for the statistical report
            return (total, round(average,2), personal_best, round(stdev,2)) 
        
    def stats_report(self):
        """
        returns a list of rows:
        ['Planter', 'Total', 'Average', 'Best', 'STDEV'],
        [planter1,  total1, avg1,   pb1,    stdev1],
        [planter2,  total2, avg2,   pb2,    stdev2],
        ...
        [planterM,  total3, avgM,   pbM,    stddevM]
"""
        self.c.execute("SELECT oid, lname FROM planters")
        planter_list = [pid for pid in self.c.fetchall()]
        rows=[]
        for planter in planter_list:
            try:
                stats = self.planter_report(planter[0], stats=True)
            except Exception as e: 
                stats=[0,0,0,0]
            rows.append([planter[1], stats[0], stats[1], stats[2], stats[3]])
        rows.sort(key=lambda x: x[1], reverse=True)
        
        return rows
    
    def foreman_report(self):
        """
        returns a list of rows:
        [['Date',    'Planted',  'Crew Planted', 'Gross'],
        [day1,      planted1,   crew_planted1,  gross1],
        ...
        [dayM,      plantedM,   crew_plantedM,  grossM]]
        
        and a tuple:
        (total, crew_total, cmsn_total, gross_total)
        """
        rows = [['Date', 'Planted', 'Crew Planted', 'Gross']]
        self.c.execute('SELECT DISTINCT jour FROM daily ORDER BY jour ASC')
        day_list = [day[0] for day in self.c.fetchall()]
        total = 0
        crew_total = 0
        gross_total = 0
        cmsn_total = 0
        for day in day_list:
            self.c.execute(f"SELECT {TOTAL}, {GROSS} FROM daily JOIN seedlots ON sid = seedlots.code WHERE jour = '{day}' AND pid = 1")
            data = self.c.fetchall()
            daily_planted = 0
            daily_grossed = 0
            crew_planted, commission = self.daily_report(day,foreman=True)
            crew_total += crew_planted
            cmsn_total += commission
            for entry in data:
                daily_planted += entry[0]
                daily_grossed += entry[1]
            total += daily_planted
            gross_total += daily_grossed
            rows.append([day, daily_planted, crew_planted, round(daily_grossed + commission,2)])
        return rows, (total, crew_total, cmsn_total, round(gross_total+cmsn_total,2))


# testing stuff
if __name__ == '__main__':
    build_database()
