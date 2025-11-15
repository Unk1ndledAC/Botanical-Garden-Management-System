CREATE DATABASE IF NOT EXISTS botanic_garden
  DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE botanic_garden;

CREATE TABLE IF NOT EXISTS taxonomy_class (
    class_id   SMALLINT AUTO_INCREMENT PRIMARY KEY,
    class_name VARCHAR(60) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS taxonomy_order (
    order_id   SMALLINT AUTO_INCREMENT PRIMARY KEY,
    class_id   SMALLINT NOT NULL,
    order_name VARCHAR(60) NOT NULL,
    FOREIGN KEY (class_id) REFERENCES taxonomy_class(class_id),
    UNIQUE KEY uk_order (class_id, order_name)
);

CREATE TABLE IF NOT EXISTS taxonomy_family (
    family_id   SMALLINT AUTO_INCREMENT PRIMARY KEY,
    order_id    SMALLINT NOT NULL,
    family_name VARCHAR(60) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES taxonomy_order(order_id),
    UNIQUE KEY uk_family (order_id, family_name)
);

CREATE TABLE IF NOT EXISTS taxonomy_genus (
    genus_id   SMALLINT AUTO_INCREMENT PRIMARY KEY,
    family_id  SMALLINT NOT NULL,
    genus_name VARCHAR(60) NOT NULL,
    FOREIGN KEY (family_id) REFERENCES taxonomy_family(family_id),
    UNIQUE KEY uk_genus (family_id, genus_name)
);

CREATE TABLE IF NOT EXISTS plant (
    plant_id      INT AUTO_INCREMENT PRIMARY KEY,
    genus_id      SMALLINT NOT NULL,
    species_name  VARCHAR(60) NOT NULL,
    chinese_name  VARCHAR(60) NOT NULL,
    description   TEXT,
    origin        VARCHAR(120),
    habitat       VARCHAR(120),
    bloom_period  VARCHAR(60),
    use_type      VARCHAR(120),
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (genus_id) REFERENCES taxonomy_genus(genus_id),
    UNIQUE KEY uk_species (genus_id, species_name)
);

CREATE TABLE IF NOT EXISTS zone (
    zone_id   SMALLINT AUTO_INCREMENT PRIMARY KEY,
    zone_name VARCHAR(60) NOT NULL UNIQUE,
    location  VARCHAR(120),
    intro     TEXT
);

CREATE TABLE IF NOT EXISTS plant_location (
    loc_id       INT AUTO_INCREMENT PRIMARY KEY,
    plant_id     INT NOT NULL,
    zone_id      SMALLINT NOT NULL,
    quantity     INT DEFAULT 1,
    planted_date DATE,
    status       ENUM('healthy','poor','dead') DEFAULT 'healthy',
    FOREIGN KEY (plant_id) REFERENCES plant(plant_id) ON DELETE CASCADE,
    FOREIGN KEY (zone_id)  REFERENCES zone(zone_id)
);

CREATE TABLE IF NOT EXISTS `user` (
    user_id     INT AUTO_INCREMENT PRIMARY KEY,
    username    VARCHAR(30) NOT NULL UNIQUE,
    password    VARCHAR(60) NOT NULL,
    email       VARCHAR(60) UNIQUE,
    role        ENUM('admin','guest') DEFAULT 'guest',
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

DROP TRIGGER IF EXISTS trg_plant_update;

DELIMITER $$
CREATE TRIGGER trg_plant_update
BEFORE UPDATE ON plant
FOR EACH ROW
BEGIN
    SET NEW.updated_at = CURRENT_TIMESTAMP;
END$$
DELIMITER ;
