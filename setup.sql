CREATE DATABASE assetdb;
USE assetdb;

CREATE TABLE assets (
    id          INT PRIMARY KEY AUTO_INCREMENT,
    name        VARCHAR(100),
    status      VARCHAR(20),
    assigned_to VARCHAR(100)
);

INSERT INTO assets VALUES
    (1, 'Dell Laptop',    'Assigned',    'Rahul Sharma'),
    (2, 'HP Monitor',     'Available',   ''),
    (3, 'MacBook Pro',    'Assigned',    'Priya Mehta'),
    (4, 'Cisco Router',   'Maintenance', ''),
    (5, 'Logitech Mouse', 'Available',   '');
