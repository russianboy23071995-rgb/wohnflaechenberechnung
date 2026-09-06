"""SQLite-Schema und Migrationen."""

from wohnflaechen.infrastructure.database.connection import DatabaseConnection

SCHEMA_VERSION = 6

CREATE_TABLES = """
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS auftraege (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL DEFAULT '',
    client_name TEXT NOT NULL DEFAULT '',
    client_address TEXT NOT NULL DEFAULT '',
    client_email TEXT NOT NULL DEFAULT '',
    client_phone TEXT NOT NULL DEFAULT '',
    object_name TEXT NOT NULL DEFAULT '',
    object_address TEXT NOT NULL DEFAULT '',
    editor TEXT NOT NULL DEFAULT '',
    notes TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS angebote (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    auftrag_id INTEGER NOT NULL,
    number TEXT NOT NULL DEFAULT '',
    date TEXT,
    service_description TEXT NOT NULL DEFAULT '',
    price REAL NOT NULL DEFAULT 0,
    notes TEXT NOT NULL DEFAULT '',
    file_path TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    FOREIGN KEY (auftrag_id) REFERENCES auftraege(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS rechnungen (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    auftrag_id INTEGER NOT NULL,
    number TEXT NOT NULL DEFAULT '',
    date TEXT,
    service_description TEXT NOT NULL DEFAULT '',
    price REAL NOT NULL DEFAULT 0,
    notes TEXT NOT NULL DEFAULT '',
    file_path TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    FOREIGN KEY (auftrag_id) REFERENCES auftraege(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS app_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    auftrag_id INTEGER,
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
    file_path TEXT NOT NULL DEFAULT '',
    FOREIGN KEY (auftrag_id) REFERENCES auftraege(id) ON DELETE SET NULL
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

CREATE INDEX IF NOT EXISTS idx_auftraege_created ON auftraege(created_at);
CREATE INDEX IF NOT EXISTS idx_angebote_auftrag ON angebote(auftrag_id);
CREATE INDEX IF NOT EXISTS idx_rechnungen_auftrag ON rechnungen(auftrag_id);
CREATE INDEX IF NOT EXISTS idx_projects_auftrag ON projects(auftrag_id);
CREATE INDEX IF NOT EXISTS idx_floors_project ON floors(project_id);
CREATE INDEX IF NOT EXISTS idx_rooms_project ON rooms(project_id);
CREATE INDEX IF NOT EXISTS idx_rooms_floor ON rooms(floor_id);
CREATE INDEX IF NOT EXISTS idx_text_blocks_project ON text_blocks(project_id);

CREATE TABLE IF NOT EXISTS client_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    address TEXT NOT NULL DEFAULT '',
    email TEXT NOT NULL DEFAULT '',
    phone TEXT NOT NULL DEFAULT '',
    last_used_at TEXT,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_client_profiles_name ON client_profiles(name);
CREATE INDEX IF NOT EXISTS idx_client_profiles_last_used ON client_profiles(last_used_at);
"""


def initialize_schema(connection: DatabaseConnection) -> None:
    conn = connection.connect()
    row = conn.execute("SELECT version FROM schema_version LIMIT 1").fetchone()
    if row is None:
        conn.executescript(CREATE_TABLES)
        if SCHEMA_VERSION >= 6:
            _migrate_to_v6(conn)
        conn.execute("INSERT INTO schema_version (version) VALUES (?)", (SCHEMA_VERSION,))
    else:
        current_version = row["version"]
        if current_version < 2:
            _migrate_to_v2(conn)
        if current_version < 3:
            _migrate_to_v3(conn)
        if current_version < 4:
            _migrate_to_v4(conn)
        if current_version < 5:
            _migrate_to_v5(conn)
        if current_version < 6:
            _migrate_to_v6(conn)
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


def _migrate_to_v3(conn) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS auftraege (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL DEFAULT '',
            client_name TEXT NOT NULL DEFAULT '',
            client_address TEXT NOT NULL DEFAULT '',
            client_email TEXT NOT NULL DEFAULT '',
            client_phone TEXT NOT NULL DEFAULT '',
            object_name TEXT NOT NULL DEFAULT '',
            object_address TEXT NOT NULL DEFAULT '',
            editor TEXT NOT NULL DEFAULT '',
            notes TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS angebote (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            auftrag_id INTEGER NOT NULL,
            number TEXT NOT NULL DEFAULT '',
            date TEXT,
            service_description TEXT NOT NULL DEFAULT '',
            price REAL NOT NULL DEFAULT 0,
            notes TEXT NOT NULL DEFAULT '',
            file_path TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL,
            FOREIGN KEY (auftrag_id) REFERENCES auftraege(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS rechnungen (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            auftrag_id INTEGER NOT NULL,
            number TEXT NOT NULL DEFAULT '',
            date TEXT,
            service_description TEXT NOT NULL DEFAULT '',
            price REAL NOT NULL DEFAULT 0,
            notes TEXT NOT NULL DEFAULT '',
            file_path TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL,
            FOREIGN KEY (auftrag_id) REFERENCES auftraege(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS app_settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL DEFAULT ''
        );
        """
    )
    columns = {row["name"] for row in conn.execute("PRAGMA table_info(projects)").fetchall()}
    if "auftrag_id" not in columns:
        conn.execute("ALTER TABLE projects ADD COLUMN auftrag_id INTEGER")
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_projects_auftrag ON projects(auftrag_id)"
    )


def _migrate_to_v4(conn) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS client_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT NOT NULL DEFAULT '',
            email TEXT NOT NULL DEFAULT '',
            phone TEXT NOT NULL DEFAULT '',
            last_used_at TEXT,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_client_profiles_name ON client_profiles(name);
        CREATE INDEX IF NOT EXISTS idx_client_profiles_last_used ON client_profiles(last_used_at);
        """
    )
    rows = conn.execute(
        """
        SELECT client_name, client_address, client_email, client_phone, created_at
        FROM auftraege
        WHERE trim(client_name) != ''
        ORDER BY created_at DESC
        """
    ).fetchall()
    seen: set[str] = set()
    for row in rows:
        key = row["client_name"].strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        conn.execute(
            """
            INSERT INTO client_profiles (
                name, address, email, phone, last_used_at, created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                row["client_name"].strip(),
                row["client_address"] or "",
                row["client_email"] or "",
                row["client_phone"] or "",
                row["created_at"],
                row["created_at"],
            ),
        )


def _migrate_to_v5(conn) -> None:
    columns = {row["name"] for row in conn.execute("PRAGMA table_info(auftraege)").fetchall()}
    if "completed" not in columns:
        conn.execute(
            "ALTER TABLE auftraege ADD COLUMN completed INTEGER NOT NULL DEFAULT 0"
        )
    columns = {row["name"] for row in conn.execute("PRAGMA table_info(projects)").fetchall()}
    if "completed" not in columns:
        conn.execute(
            "ALTER TABLE projects ADD COLUMN completed INTEGER NOT NULL DEFAULT 0"
        )
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS folders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            parent_id INTEGER,
            category TEXT NOT NULL DEFAULT 'vorgaenge',
            sort_order INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (parent_id) REFERENCES folders(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS folder_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            folder_id INTEGER NOT NULL,
            entity_type TEXT NOT NULL,
            entity_id INTEGER NOT NULL,
            UNIQUE(folder_id, entity_type, entity_id),
            FOREIGN KEY (folder_id) REFERENCES folders(id) ON DELETE CASCADE
        );
        CREATE INDEX IF NOT EXISTS idx_folder_items_folder ON folder_items(folder_id);
        CREATE INDEX IF NOT EXISTS idx_folder_items_entity ON folder_items(entity_type, entity_id);
        """
    )
    existing = conn.execute("SELECT COUNT(*) AS c FROM folders").fetchone()["c"]
    if existing == 0:
        roots = [
            ("Vorgänge", "vorgaenge", 0),
            ("Kunden", "kunden", 1),
            ("Objekte", "objekte", 2),
            ("Angebote", "angebote", 3),
            ("Rechnungen", "rechnungen", 4),
        ]
        for name, category, order in roots:
            conn.execute(
                "INSERT INTO folders (name, parent_id, category, sort_order) VALUES (?, NULL, ?, ?)",
                (name, category, order),
            )


def _migrate_to_v6(conn) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS buildings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            name TEXT NOT NULL DEFAULT '',
            room_prefix TEXT NOT NULL DEFAULT '',
            sort_order INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        );
        CREATE INDEX IF NOT EXISTS idx_buildings_project ON buildings(project_id);
        """
    )
    floor_columns = {row["name"] for row in conn.execute("PRAGMA table_info(floors)").fetchall()}
    if "building_id" not in floor_columns:
        conn.execute(
            "ALTER TABLE floors ADD COLUMN building_id INTEGER REFERENCES buildings(id) ON DELETE SET NULL"
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_floors_building ON floors(building_id)")
    room_columns = {row["name"] for row in conn.execute("PRAGMA table_info(rooms)").fetchall()}
    if "building_id" not in room_columns:
        conn.execute(
            "ALTER TABLE rooms ADD COLUMN building_id INTEGER REFERENCES buildings(id) ON DELETE SET NULL"
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_rooms_building ON rooms(building_id)")
