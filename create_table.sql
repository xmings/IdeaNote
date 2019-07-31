CREATE TABLE t_catalog (
	id                       INTEGER PRIMARY KEY AUTOINCREMENT,
	title                    VARCHAR ( 100 ),
	icon                     BLOB,
	parent_id                INTEGER,
	content                  TEXT,
    content_sha              VARCHAR ( 100 ),
    seq_no                   INTEGER,
	status                   INTEGER NOT NULL,
	creation_time            DATETIME,
	modification_time        DATETIME
);

CREATE TABLE t_note_reference_image (
    id                       INTEGER PRIMARY KEY AUTOINCREMENT,
    note_id                  INTEGER REFERENCES t_catalog (id),
    image                    BLOB,
	status                   INTEGER NOT NULL,
	creation_time            DATETIME,
	modification_time        DATETIME
)

CREATE TABLE t_content_snap (
	id                       INTEGER PRIMARY KEY AUTOINCREMENT,
	note_id                  INTEGER REFERENCES t_catalog (id),
	content                  TEXT,
	creation_time            DATETIME,
	modification_time        DATETIME
);

CREATE TABLE t_sync_log (
    id                       INTEGER PRIMARY KEY AUTOINCREMENT,
    sync_sha                 VARCHAR ( 100 ),
    creation_time            DATETIME,
	modification_time        DATETIME
);