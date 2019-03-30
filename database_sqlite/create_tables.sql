-- Create the sqllite tables
--
CREATE TABLE node (
    node_id INTEGER PRIMARY KEY NOT NULL,
    node_lat REAL,
    node_lon REAL,
    node_user TEXT,
    node_uid INTEGER,
    node_version INTEGER,
    node_changeset INTEGER,
    node_timestamp TEXT
);

CREATE TABLE node_tag (
    node_id INTEGER,
    tag_key TEXT,
    tag_value TEXT,
    tag_type TEXT,
    FOREIGN KEY (node_id) REFERENCES node(node_id)
);

CREATE TABLE way (
    way_id INTEGER PRIMARY KEY NOT NULL,
    way_user TEXT,
    way_uid INTEGER,
    way_version TEXT,
    way_changeset INTEGER,
    way_timestamp TEXT
);

CREATE TABLE way_node (
    way_id INTEGER NOT NULL,
    node_id INTEGER NOT NULL,
    position INTEGER NOT NULL,
    FOREIGN KEY (way_id) REFERENCES way(way_id),
    FOREIGN KEY (node_id) REFERENCES node(node_id)
);

CREATE TABLE way_tag (
    way_id INTEGER NOT NULL,
    tag_key TEXT NOT NULL,
    tag_value TEXT NOT NULL,
    tag_type TEXT,
    FOREIGN KEY (way_id) REFERENCES way(way_id)
);

