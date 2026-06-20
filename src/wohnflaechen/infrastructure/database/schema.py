"""SQLite-Schema und Migrationen."""

from wohnflaechen.infrastructure.database.connection import DatabaseConnection

SCHEMA_VERSION = 2

CREATE_TABLES = """
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL DEFAULT '',
    object_name TEXT NOT NULL DEFAULT '',
    address TEXT NOT NULL DEFAULT '',
    client TEXT NOT NULL DEFAULT '',
    editor TEXT NOT NULL DEFAULT '',
    measurement_date TEXT,
    measurement_on_site INTEGER NOT NULL DEFAULT 1,
    measurement_note TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    notes TEXT NOT NULL DEFAULT '',
    file_path TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS floors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    name TEXT NOT NULL DEFAULT '',
    sort_order INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS rooms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    floor_id INTEGER,
    name TEXT NOT NULL DEFAULT '',
    number TEXT NOT NULL DEFAULT '',
    raw_area REAL NOT NULL DEFAULT 0,
    area_type TEXT NOT NULL DEFAULT '',
    factor REAL NOT NULL DEFAULT 1.0,
    calculation_path TEXT NOT NULL DEFAULT '',
    note TEXT NOT NULL DEFAULT '',
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (floor_id) REFERENCES floors(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS text_blocks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    block_type TEXT NOT NULL,
    content TEXT NOT NULL DEFAULT '',
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    UNIQUE(project_id, block_type)
);

CREATE INDEX IF NOT EXISTS idx_floors_project ON floors(project_id);
CREATE INDEX IF NOT EXISTS idx_rooms_project ON rooms(project_id);
CREATE INDEX IF NOT EXISTS idx_rooms_floor ON rooms(floor_id);
CREATE INDEX IF NOT EXISTS idx_text_blocks_project ON text_blocks(project_id);
"""


def initialize_schema(connection: DatabaseConnection) -> None:
    conn = connection.connect()
    conn.executescript(CREATE_TABLES)
    row = conn.execute("SELECT version FROM schema_version LIMIT 1").fetchone()
    if row is None:
        conn.execute("INSERT INTO schema_version (version) VALUES (?)", (SCHEMA_VERSION,))
    else:
        current_version = row["version"]
        if current_version < 2:
            _migrate_to_v2(conn)
            conn.execute("UPDATE schema_version SET version = ?", (SCHEMA_VERSION,))
    connection.commit()


def _migrate_to_v2(conn) -> None:
    columns = {
        row["name"] for row in conn.execute("PRAGMA table_info(projects)").fetchall()
    }
    if "measurement_on_site" not in columns:
        conn.execute(
            "ALTER TABLE projects ADD COLUMN measurement_on_site INTEGER NOT NULL DEFAULT 1"
        )
    conn.execute(
        """
        UPDATE projects
        SET measurement_on_site = CASE
            WHEN measurement_date IS NOT NULL AND measurement_date != '' THEN 1
            ELSE 0
        END
        """
    )
