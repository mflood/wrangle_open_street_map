import MySQLdb as sql


class Database():


    def __init__(self):
        self._connection = None


    def connect(self, host, port, database, username, password):
        self._connection = sql.connect(host=host,
                                       port=port,
                                       db=database,
                                       user=username,
                                       passwd=password)
        c = self._connection.cursor()
        c.execute("use udacity;")

    def test_connection(self):
        self._connection.query("""SHOW TABLES""")
        r = self._connection.use_result()
        print(r.fetch_row())

    def execute(self, sql):
        c = self._connection.cursor()
        c.execute(sql)
        

    def create_node_table(self):
        self._connection

        sql = """
            create table map_node (
               map_node_id int unsigned not null auto_increment primary key,
               opm_id varchar(255) not null unique,
               name varchar(255),
               amenity varchar(255),
               shop varchar(255),
               description text,
               cuisine text,
               denomination text,
               coordinates point
            );
        """
        c = self._connection.cursor()
        c.execute(sql)


    def get_closest_nodes(self, map_node_id, limit):
        print("Getting close nodes")
        sql = """
            select 
                  other.map_node_id
                , other.opm_id
                , other.name
                , other.amenity 
                , other.shop
                , other.description
                , other.cuisine
                , other.denomination
                , st_x(other.coordinates) as lon
                , st_y(other.coordinates) as lat
                , st_distance_sphere(other.coordinates, thisthis.coordinates) as distance
                from 
                udacity.map_node thisthis 
                cross join udacity.map_node other
                where thisthis.map_node_id = %s 
        --         and other.map_node_id != thisthis.map_node_id
                order by distance
                limit {}""".format(limit)

        c = self._connection.cursor()
        c.execute(sql, (map_node_id,))
        row = c.fetchone()
        results = []
        while (row):
            results.append(row)
            row = c.fetchone()

        return results
            

    def add_node(self, node):
        sql = """
            insert ignore into map_node(opm_id
                , name
                , coordinates
                , description
                , cuisine
                , denomination
                , amenity
                , shop
             )
            values (%s
                  , %s
                  , POINT(%s, %s)
                  , %s
                  , %s
                  , %s
                  , %s
                  , %s
             )
        """

        c = self._connection.cursor()
        c.execute("delete from map_node where opm_id = %s", (node['id'],))

        try:
            c.executemany(sql, [
                (node['id'],
                 node['name'],
                 node['lon'], 
                 node['lat'],
                 node['description'],
                 node['cuisine'],
                 node['denomination'],
                 node['amenity'],
                 node['shop'],
                 ),
            ])
        except UnicodeEncodeError as error:
            print(node)
            raise
        c.execute("commit")

if __name__ == "__main__":
    db = Database()
    db.connect(host="127.0.0.1",
               port=3306,
               database='udacity',
               username='root',
               password='ux19s128')
    #db.test_connection()
    #db.create_node_table()
    #db.test_connection()
    #db.add_node(None)
    closest = db.get_closest_nodes(3288, 100)
    for thing in closest:
        print(thing)
