CREATE TABLE t_catalog (
	node_id INTEGER NOT NULL,
	node_title VARCHAR(100),
	node_type VARCHAR(10),
	node_pid INTEGER,
	node_img BLOB,
	file_name VARCHAR(100),
	file_hash VARCHAR(100),
	level INTEGER,
	status VARCHAR(2) NOT NULL,
	create_time DATETIME,
	modify_time DATETIME,
	PRIMARY KEY (node_id),
	FOREIGN KEY(node_pid) REFERENCES t_catalog (node_id),
	UNIQUE (file_name)
);

CREATE TABLE operation (
	oper_id INTEGER NOT NULL,
	seq_no INTEGER,
	command VARCHAR(200),
	status VARCHAR(2) NOT NULL,
	create_time DATETIME,
	modify_time DATETIME,
	PRIMARY KEY (oper_id)
);