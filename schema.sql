CREATE DATABASE IF NOT EXISTS botanic_garden
  DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE botanic_garden;

CREATE TABLE taxonomy_class (
    class_id   SMALLINT AUTO_INCREMENT PRIMARY KEY,
    class_name VARCHAR(60) NOT NULL UNIQUE
);

CREATE TABLE taxonomy_order (
    order_id   SMALLINT AUTO_INCREMENT PRIMARY KEY,
    class_id   SMALLINT NOT NULL,
    order_name VARCHAR(60) NOT NULL,
    FOREIGN KEY (class_id) REFERENCES taxonomy_class(class_id),
    UNIQUE KEY uk_order (class_id, order_name)
);

CREATE TABLE taxonomy_family (
    family_id   SMALLINT AUTO_INCREMENT PRIMARY KEY,
    order_id    SMALLINT NOT NULL,
    family_name VARCHAR(60) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES taxonomy_order(order_id),
    UNIQUE KEY uk_family (order_id, family_name)
);

CREATE TABLE taxonomy_genus (
    genus_id   SMALLINT AUTO_INCREMENT PRIMARY KEY,
    family_id  SMALLINT NOT NULL,
    genus_name VARCHAR(60) NOT NULL,
    FOREIGN KEY (family_id) REFERENCES taxonomy_family(family_id),
    UNIQUE KEY uk_genus (family_id, genus_name)
);

CREATE TABLE plant (
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

CREATE TABLE zone (
    zone_id   SMALLINT AUTO_INCREMENT PRIMARY KEY,
    zone_name VARCHAR(60) NOT NULL UNIQUE,
    location  VARCHAR(120),
    intro     TEXT
);

CREATE TABLE plant_location (
    loc_id       INT AUTO_INCREMENT PRIMARY KEY,
    plant_id     INT NOT NULL,
    zone_id      SMALLINT NOT NULL,
    quantity     INT DEFAULT 1,
    planted_date DATE,
    status       ENUM('healthy','poor','dead') DEFAULT 'healthy',
    FOREIGN KEY (plant_id) REFERENCES plant(plant_id) ON DELETE CASCADE,
    FOREIGN KEY (zone_id)  REFERENCES zone(zone_id)
);

CREATE TABLE `user` (
    user_id     INT AUTO_INCREMENT PRIMARY KEY,
    username    VARCHAR(30) NOT NULL UNIQUE,
    password    VARCHAR(60) NOT NULL,
    email       VARCHAR(60) UNIQUE,
    role        ENUM('admin','guest') DEFAULT 'guest',
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

DELIMITER $$
CREATE TRIGGER trg_plant_update
BEFORE UPDATE ON plant
FOR EACH ROW
BEGIN
    SET NEW.updated_at = CURRENT_TIMESTAMP;
END$$
DELIMITER ;

INSERT INTO taxonomy_class(class_name) VALUES
('Magnoliopsida'),('Liliopsida'),('Gymnosperms');

INSERT INTO taxonomy_order(class_id,order_name) VALUES
(1,'Rosales'),(1,'Lamiales'),(1,'Asterales'),
(2,'Asparagales'),(2,'Poales'),
(3,'Pinales');

INSERT INTO taxonomy_family(order_id,family_name) VALUES
(1,'Rosaceae'),(2,'Lamiaceae'),(3,'Asteraceae'),
(4,'Asparagaceae'),(5,'Poaceae'),
(6,'Pinaceae');

INSERT INTO taxonomy_genus(family_id,genus_name) VALUES
(1,'Rosa'),(1,'Prunus'),
(2,'Salvia'),(2,'Lavandula'),
(3,'Chrysanthemum'),
(4,'Asparagus'),(4,'Hosta'),
(5,'Bambusa'),
(6,'Pinus');

INSERT INTO zone(zone_name,location,intro) VALUES
('蔷薇园','A区东侧','收集蔷薇科植物约 120 种'),
('草本香料园','B区中央','展示药用及香料植物 60 余种'),
('菊圃','C区南侧','秋季观花主园区'),
('蔬菜展示区','D区温室','可食用植物资源圃'),
('竹类园','E区山麓','散生竹与丛生竹专区'),
('松柏园','F区北坡','裸子植物专类园');

INSERT INTO plant(genus_id,species_name,chinese_name,description,origin,habitat,bloom_period,use_type) VALUES
(1,'chinensis','月季','常绿灌木，四季开花，花色丰富','中国','温带向阳坡地','5-10月','观赏'),
(1,'rugosa','玫瑰','落叶灌木，花香浓郁，可提炼精油','中国东北','海边沙地','6-7月','香精/食品'),
(2,'officinalis','药用鼠尾草','多年生草本，可提取精油','地中海','干旱草原','6-8月','药用/香料'),
(2,'angustifolia','薰衣草','半灌木，蓝紫色花序，香味浓郁','地中海','石灰岩坡地','6-8月','芳香/观赏'),
(3,'morifolium','杭菊','多年生草本，头状花序，清热解毒','中国','温带平原','9-11月','药用/茶饮'),
(4,'officinalis','芦笋','多年生宿根蔬菜，嫩茎食用','欧洲','温带沙壤土','4-5月','食用'),
(4,'plantaginea','玉簪','耐阴宿根草本，叶大花香','中国华东','林下阴湿处','7-8月','观赏'),
(5,'oldhamii','绿竹','丛生型竹类，笋用竹种','中国华南','亚热带丘陵','4-5月（笋）','食用/材用'),
(6,'massoniana','马尾松','常绿乔木，耐贫瘠','中国南方','酸性山地','3-4月','用材/造纸'),
(6,'tabuliformis','油松','常绿乔木，树皮灰褐色','中国华北','温带山地','4-5月','用材/绿化');

INSERT INTO plant_location(plant_id,zone_id,quantity,planted_date,status) VALUES
(1,1,150,'2022-03-15','healthy'),
(1,1,80,'2023-04-20','healthy'),
(2,1,60,'2021-10-10','healthy'),
(3,2,90,'2023-04-01','healthy'),
(4,2,120,'2022-06-01','healthy'),
(5,3,200,'2023-07-15','healthy'),
(6,4,300,'2023-02-20','healthy'),
(7,4,100,'2022-05-18','healthy'),
(8,5,500,'2021-12-05','healthy'),
(9,6,80,'2020-03-12','healthy'),
(10,6,70,'2021-04-08','healthy'),
(3,2,40,'2023-05-10','poor'),
(5,3,30,'2023-10-01','dead'),
(7,4,50,'2023-06-01','healthy'),
(9,6,20,'2023-09-15','healthy');

INSERT INTO `user`(username,password,email,role) VALUES
('admin','123456','admin@mail.com','admin'),
('gardener','123456','gardener@mail.com','admin');