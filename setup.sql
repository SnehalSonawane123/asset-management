-- ─────────────────────────────────────────────
--  Asset Management System — SQLite Schema
--  Run once to initialise the database.
--  Called automatically by db.py → init_db()
-- ─────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS assets (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT    NOT NULL,
    category   TEXT    NOT NULL DEFAULT 'Other',
    quantity   INTEGER NOT NULL DEFAULT 1,
    location   TEXT             DEFAULT '',
    status     TEXT    NOT NULL DEFAULT 'Available',
    created_at TEXT             DEFAULT (datetime('now'))
);

-- ── Optional seed data (comment out if not needed) ──────────────────────────
INSERT OR IGNORE INTO assets (id, name, category, quantity, location, status) VALUES
    (1, 'Dell Laptop XPS 15',     'Electronics', 5,  'IT Room, Floor 2',    'Available'),
    (2, 'Office Chair Ergonomic', 'Furniture',   20, 'Main Hall',           'In Use'),
    (3, 'Toyota Hilux',           'Vehicles',    2,  'Parking Lot B',       'Available'),
    (4, 'Power Drill Set',        'Tools',       8,  'Maintenance Bay',     'Maintenance'),
    (5, 'Standing Desk',          'Furniture',   10, 'Floor 3 Open Space',  'Available'),
    (6, 'HP LaserJet Printer',    'Electronics', 3,  'Admin Office',        'In Use'),
    (7, 'Projector Epson EB-X41', 'Electronics', 4,  'Conference Room A',   'Available'),
    (8, 'Forklift Toyota 8FBN25', 'Vehicles',    1,  'Warehouse',           'Retired');
