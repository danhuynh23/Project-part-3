-- MariaDB dump 10.19  Distrib 10.4.32-MariaDB, for Win64 (AMD64)
--
-- Host: localhost    Database: air_ticketing_system
-- ------------------------------------------------------
-- Server version	10.4.32-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `airline`
--

DROP TABLE IF EXISTS `airline`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `airline` (
  `name` varchar(100) NOT NULL,
  PRIMARY KEY (`name`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `airline`
--

LOCK TABLES `airline` WRITE;
/*!40000 ALTER TABLE `airline` DISABLE KEYS */;
INSERT INTO `airline` VALUES ('Air France'),('American Airlines'),('British Airways'),('Dan\'s Air'),('Delta Airlines'),('Emirates'),('Lufthansa'),('Qatar Airways'),('Singapore Airlines'),('Southwest Airlines'),('United Airlines');
/*!40000 ALTER TABLE `airline` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `airline_staff`
--

DROP TABLE IF EXISTS `airline_staff`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `airline_staff` (
  `username` varchar(100) NOT NULL,
  `name` varchar(100) NOT NULL,
  `password` varchar(100) DEFAULT NULL,
  `first_name` varchar(50) DEFAULT NULL,
  `last_name` varchar(50) DEFAULT NULL,
  `date_of_birth` date DEFAULT NULL,
  PRIMARY KEY (`username`,`name`),
  KEY `name` (`name`),
  CONSTRAINT `airline_staff_ibfk_1` FOREIGN KEY (`name`) REFERENCES `airline` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `airline_staff`
--

LOCK TABLES `airline_staff` WRITE;
/*!40000 ALTER TABLE `airline_staff` DISABLE KEYS */;
INSERT INTO `airline_staff` VALUES ('Amex','American Airlines','53bc3911362cda98b1014b8566f6800c72f6be0688961274130bd6a3fcfee8b9','Dan','Huynh','2001-11-23'),('Dan_AA','American Airlines','53bc3911362cda98b1014b8566f6800c72f6be0688961274130bd6a3fcfee8b9','Dan','Huynh','2001-04-22'),('DH_40','Dan\'s Air','53bc3911362cda98b1014b8566f6800c72f6be0688961274130bd6a3fcfee8b9','Dan ','Huynh','2001-04-23');
/*!40000 ALTER TABLE `airline_staff` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `airlinestaffpermission`
--

DROP TABLE IF EXISTS `airlinestaffpermission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `airlinestaffpermission` (
  `username` varchar(100) NOT NULL,
  `permission` varchar(50) NOT NULL,
  PRIMARY KEY (`username`,`permission`),
  CONSTRAINT `airlinestaffpermission_ibfk_1` FOREIGN KEY (`username`) REFERENCES `airline_staff` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `airlinestaffpermission`
--

LOCK TABLES `airlinestaffpermission` WRITE;
/*!40000 ALTER TABLE `airlinestaffpermission` DISABLE KEYS */;
/*!40000 ALTER TABLE `airlinestaffpermission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `airplane`
--

DROP TABLE IF EXISTS `airplane`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `airplane` (
  `id` varchar(50) NOT NULL,
  `name_airline` varchar(100) NOT NULL,
  `capacity` int(11) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `name_airline` (`name_airline`),
  KEY `idx_airplane_id_name_airline` (`id`,`name_airline`),
  CONSTRAINT `airplane_ibfk_1` FOREIGN KEY (`name_airline`) REFERENCES `airline` (`name`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `airplane`
--

LOCK TABLES `airplane` WRITE;
/*!40000 ALTER TABLE `airplane` DISABLE KEYS */;
INSERT INTO `airplane` VALUES ('B747-1','American Airlines',180,'Boeing 747');
/*!40000 ALTER TABLE `airplane` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `airport`
--

DROP TABLE IF EXISTS `airport`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `airport` (
  `name` varchar(50) NOT NULL,
  `city` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`name`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `airport`
--

LOCK TABLES `airport` WRITE;
/*!40000 ALTER TABLE `airport` DISABLE KEYS */;
INSERT INTO `airport` VALUES ('ATL','Atlanta'),('CDG','Paris'),('DEN','Denver'),('DFW','Dallas'),('DOH','Doha'),('DXB','Dubai'),('FRA','Frankfurt'),('HKG','Hong Kong'),('HND ','Tokyo'),('JFK','New York'),('LAX','Los Angeles'),('LHR','London'),('MIA','Miami'),('ORD','Chicago'),('SEA','Seattle'),('SFO','San Francisco'),('SIN','Singapore');
/*!40000 ALTER TABLE `airport` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `booking_agent`
--

DROP TABLE IF EXISTS `booking_agent`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `booking_agent` (
  `email` varchar(100) NOT NULL,
  `name` varchar(255) NOT NULL,
  `password` varchar(100) DEFAULT NULL,
  `booking_agent_id` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`email`,`name`),
  UNIQUE KEY `booking_agent_id` (`booking_agent_id`),
  KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `booking_agent`
--

LOCK TABLES `booking_agent` WRITE;
/*!40000 ALTER TABLE `booking_agent` DISABLE KEYS */;
INSERT INTO `booking_agent` VALUES ('agent1@example.com','American Airlines','securepassword123',NULL),('GeogreBush@email.com','American Airlines','53bc3911362cda98b1014b8566f6800c72f6be0688961274130bd6a3fcfee8b9','Geogre Bush Booking'),('jeff_bush@gmail.com','American Airlines','53bc3911362cda98b1014b8566f6800c72f6be0688961274130bd6a3fcfee8b9','Jeff Book');
/*!40000 ALTER TABLE `booking_agent` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `customer`
--

DROP TABLE IF EXISTS `customer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `customer` (
  `email` varchar(100) NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `password` varchar(200) DEFAULT NULL,
  `building_number` varchar(10) DEFAULT NULL,
  `street` varchar(100) DEFAULT NULL,
  `city` varchar(50) DEFAULT NULL,
  `state` varchar(50) DEFAULT NULL,
  `phone_number` varchar(15) DEFAULT NULL,
  `passport_number` varchar(50) DEFAULT NULL,
  `passport_expiration` date DEFAULT NULL,
  `passport_country` varchar(50) DEFAULT NULL,
  `date_of_birth` date DEFAULT NULL,
  PRIMARY KEY (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `customer`
--

LOCK TABLES `customer` WRITE;
/*!40000 ALTER TABLE `customer` DISABLE KEYS */;
INSERT INTO `customer` VALUES ('customer1@example.com','Alice Johnson',NULL,'123','Main St','New York','NY','123-456-7890','P123456','2025-05-15','USA','1980-06-25'),('customer2@example.com','Bob Smith',NULL,'456','Broadway','Los Angeles','CA','234-567-8901','P654321','2026-03-10','USA','1985-09-12'),('customer3@example.com','Charlie Brown',NULL,'789','Ocean Drive','Miami','FL','345-678-9012','P987654','2027-01-20','USA','1990-11-05'),('customer4@example.com','Diana Prince',NULL,'321','Elm St','Seattle','WA','456-789-0123','P567890','2025-12-30','USA','1995-08-18'),('customer5@example.com','Ethan Hunt',NULL,'654','5th Ave','Chicago','IL','567-890-1234','P432109','2026-09-25','USA','1992-04-14'),('dsh400@nyu.edu','Dan Huynh','53bc3911362cda98b1014b8566f6800c72f6be0688961274130bd6a3fcfee8b9','','65 Duong 51 Binh Trung Dong, Quan 2','Ho Chi Minh','HCM','0901663700','123','2024-11-01','VN','2024-11-30'),('Newguy@gmail.com','New Guy ','53bc3911362cda98b1014b8566f6800c72f6be0688961274130bd6a3fcfee8b9','12','140 E 14th Street','NYC','NY','+16468525947','G262','2028-11-11','GR','2001-04-23'),('wawa@gmail.com','Dan','53bc3911362cda98b1014b8566f6800c72f6be0688961274130bd6a3fcfee8b9','','140 E 14 St','New York','NY','+16468525947','C19865877','2024-11-30','VN','2001-04-23');
/*!40000 ALTER TABLE `customer` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `flight`
--

DROP TABLE IF EXISTS `flight`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `flight` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `flight_number` varchar(10) NOT NULL,
  `name_depart` varchar(255) NOT NULL,
  `name_arrive` varchar(100) NOT NULL,
  `name_airline` varchar(100) NOT NULL,
  `depart_time` datetime NOT NULL,
  `arrive_time` datetime NOT NULL,
  `price` int(11) NOT NULL,
  `status` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_flight` (`name_airline`,`flight_number`,`depart_time`),
  KEY `name_depart` (`name_depart`),
  KEY `name_arrive` (`name_arrive`),
  CONSTRAINT `flight_ibfk_1` FOREIGN KEY (`name_depart`) REFERENCES `airport` (`name`),
  CONSTRAINT `flight_ibfk_2` FOREIGN KEY (`name_arrive`) REFERENCES `airport` (`name`),
  CONSTRAINT `flight_ibfk_3` FOREIGN KEY (`name_airline`) REFERENCES `airline` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=98 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `flight`
--

LOCK TABLES `flight` WRITE;
/*!40000 ALTER TABLE `flight` DISABLE KEYS */;
INSERT INTO `flight` VALUES (1,'AA101','JFK','LAX','American Airlines','2024-11-15 08:00:00','2024-11-15 11:00:00',350,'Completed'),(2,'AA102','JFK','LAX','American Airlines','2024-11-15 08:30:00','2024-11-15 11:30:00',350,'Completed'),(3,'DL103','ORD','MIA','Delta Airlines','2024-11-15 09:30:00','2024-11-15 12:30:00',400,'Available'),(4,'UA104','SFO','SEA','United Airlines','2024-11-15 14:00:00','2024-11-15 16:00:00',200,'On Time'),(5,'AF105','CDG','ATL','Air France','2024-11-15 10:00:00','2024-11-15 15:00:00',450,'On Time'),(6,'BA106','LHR','JFK','British Airways','2024-11-17 16:00:00','2024-11-17 19:00:00',500,'On Time'),(7,'EK107','DXB','SFO','Emirates','2024-11-20 22:00:00','2024-11-21 08:00:00',600,'On Time'),(8,'LH108','FRA','ORD','Lufthansa','2024-11-19 12:00:00','2024-11-19 17:00:00',400,'Delayed'),(9,'QR109','DOH','LAX','Qatar Airways','2024-11-21 01:00:00','2024-11-21 11:00:00',620,'On Time'),(10,'SQ110','SIN','LHR','Singapore Airlines','2024-11-22 22:00:00','2024-11-22 22:00:00',550,'On Time'),(11,'SW111','JFK','LAX','Southwest Airlines','2024-11-15 11:00:00','2024-11-15 14:00:00',375,'Available'),(12,'SW112','DFW','DEN','Southwest Airlines','2024-11-16 12:00:00','2024-11-16 13:30:00',150,'Cancelled'),(13,'UA113','JFK','LAX','United Airlines','2024-11-15 13:00:00','2024-11-15 15:00:00',450,'Available'),(14,'AA114','ORD','SFO','American Airlines','2024-11-15 09:00:00','2024-11-15 12:00:00',500,'Completed'),(15,'DL115','JFK','LAX','Delta Airlines','2024-11-15 14:00:00','2024-11-15 16:30:00',375,'On Time'),(16,'AF116','CDG','ORD','Air France','2024-11-16 07:00:00','2024-11-16 12:00:00',525,'Delayed'),(17,'BA117','LHR','JFK','British Airways','2024-11-17 09:00:00','2024-11-17 12:00:00',490,'Available'),(18,'EK118','DXB','LAX','Emirates','2024-11-18 13:00:00','2024-11-18 18:00:00',650,'On Time'),(19,'LH119','FRA','ORD','Lufthansa','2024-11-19 16:00:00','2024-11-19 20:00:00',470,'On Time'),(20,'QR120','DOH','LHR','Qatar Airways','2024-11-20 06:00:00','2024-11-20 11:00:00',560,'Available'),(21,'SQ121','SIN','SFO','Singapore Airlines','2024-11-22 09:00:00','2024-11-22 18:00:00',700,'On Time'),(22,'SW122','JFK','SEA','Southwest Airlines','2024-11-22 15:00:00','2024-11-22 17:00:00',250,'Cancelled'),(23,'UA123','ORD','LAX','United Airlines','2024-11-15 07:00:00','2024-11-15 09:00:00',330,'Available'),(24,'AA124','JFK','LAX','American Airlines','2024-11-15 08:30:00','2024-11-15 11:30:00',350,'Available'),(25,'DL125','ORD','MIA','Delta Airlines','2024-11-16 11:00:00','2024-11-16 14:00:00',400,'Delayed'),(26,'AF126','CDG','SFO','Air France','2024-11-17 12:00:00','2024-11-17 17:00:00',420,'On Time'),(27,'BA127','LHR','ORD','British Airways','2024-11-18 08:00:00','2024-11-18 11:30:00',450,'Available'),(28,'EK128','DXB','LAX','Emirates','2024-11-19 21:00:00','2024-11-20 06:00:00',550,'Available'),(29,'AA125','JFK','LAX','American Airlines','2024-11-14 09:00:00','2024-11-14 12:00:00',330,'On Time'),(30,'AA126','JFK','LAX','American Airlines','2024-11-14 13:00:00','2024-11-14 16:00:00',340,'Available'),(31,'DL127','JFK','LAX','Delta Airlines','2024-11-14 11:30:00','2024-11-14 14:30:00',380,'Available'),(32,'DL128','JFK','LAX','Delta Airlines','2024-11-14 14:00:00','2024-11-14 17:00:00',390,'On Time'),(33,'UA129','JFK','LAX','United Airlines','2024-11-14 08:30:00','2024-11-14 11:30:00',320,'Delayed'),(34,'UA130','JFK','LAX','United Airlines','2024-11-14 10:00:00','2024-11-14 13:00:00',340,'On Time'),(35,'AA131','JFK','LAX','American Airlines','2024-11-16 09:00:00','2024-11-16 12:00:00',355,'Available'),(36,'AA132','JFK','LAX','American Airlines','2024-11-16 12:30:00','2024-11-16 15:30:00',365,'On Time'),(37,'DL133','JFK','LAX','Delta Airlines','2024-11-16 08:30:00','2024-11-16 11:30:00',400,'Available'),(38,'DL134','JFK','LAX','Delta Airlines','2024-11-16 13:00:00','2024-11-16 16:00:00',410,'Delayed'),(39,'UA135','JFK','LAX','United Airlines','2024-11-16 14:00:00','2024-11-16 17:00:00',330,'On Time'),(40,'UA136','JFK','LAX','United Airlines','2024-11-16 16:30:00','2024-11-16 19:30:00',350,'Available'),(41,'AA137','JFK','LAX','American Airlines','2024-11-17 07:00:00','2024-11-17 10:00:00',340,'On Time'),(42,'AA138','JFK','LAX','American Airlines','2024-11-17 10:30:00','2024-11-17 13:30:00',355,'Scheduled'),(43,'DL139','JFK','LAX','Delta Airlines','2024-11-17 12:00:00','2024-11-17 15:00:00',400,'On Time'),(44,'DL140','JFK','LAX','Delta Airlines','2024-11-17 14:30:00','2024-11-17 17:30:00',410,'Available'),(45,'AA203','JFK ','LAX','American Airlines','2024-12-01 14:19:00','2024-12-02 14:19:00',475,'Scheduled'),(46,'AA204','JFK','LAX','American Airlines','2024-12-03 14:23:00','2024-12-03 14:23:00',200,'Scheduled'),(47,'AA205','JFK','HND','American Airlines','2024-12-01 14:00:00','2024-12-02 07:00:00',800,'Delayed'),(65,'AA201','JFK','LAX','American Airlines','2024-12-01 08:00:00','2024-12-01 11:30:00',375,'On Time'),(66,'AA202','LAX','JFK','American Airlines','2024-12-01 14:00:00','2024-12-01 22:00:00',400,'On Time'),(67,'AA203','ORD','ATL','American Airlines','2024-12-05 10:00:00','2024-12-05 12:30:00',250,'Scheduled'),(68,'AA204','DFW','MIA','American Airlines','2024-12-06 06:00:00','2024-12-06 09:00:00',275,'On Time'),(69,'AA205','ATL','ORD','American Airlines','2024-12-10 18:00:00','2024-12-10 20:30:00',240,'Delayed'),(70,'DL301','SEA','SFO','Delta Airlines','2024-12-02 12:00:00','2024-12-02 14:00:00',200,'On Time'),(71,'DL302','SFO','SEA','Delta Airlines','2024-12-02 16:00:00','2024-12-02 18:00:00',210,'On Time'),(72,'DL303','LAX','ATL','Delta Airlines','2024-12-07 20:00:00','2024-12-08 00:30:00',340,'On Time'),(73,'DL304','ORD','LHR','Delta Airlines','2024-12-15 18:00:00','2024-12-16 06:00:00',650,'Available'),(74,'DL305','MIA','JFK','Delta Airlines','2024-12-20 09:00:00','2024-12-20 12:00:00',310,'On Time'),(75,'UA401','ORD','DEN','United Airlines','2024-12-01 07:00:00','2024-12-01 09:00:00',150,'On Time'),(76,'UA402','DEN','ORD','United Airlines','2024-12-01 12:00:00','2024-12-01 14:00:00',160,'Available'),(77,'UA403','LAX','DFW','United Airlines','2024-12-10 15:00:00','2024-12-10 18:00:00',275,'On Time'),(78,'UA404','JFK','SEA','United Airlines','2024-12-12 06:00:00','2024-12-12 10:00:00',450,'Delayed'),(79,'UA405','SEA','JFK','United Airlines','2024-12-13 20:00:00','2024-12-14 00:30:00',460,'On Time'),(80,'EK501','DXB','SIN','Emirates','2024-12-03 22:00:00','2024-12-04 05:00:00',800,'On Time'),(81,'EK502','SIN','DXB','Emirates','2024-12-04 10:00:00','2024-12-04 17:00:00',820,'On Time'),(82,'EK503','DXB','LHR','Emirates','2024-12-07 14:00:00','2024-12-07 20:00:00',900,'Available'),(83,'EK504','LHR','DXB','Emirates','2024-12-08 10:00:00','2024-12-08 18:00:00',920,'On Time'),(84,'EK505','DXB','JFK','Emirates','2024-12-15 23:00:00','2024-12-16 09:00:00',1000,'On Time'),(85,'QR601','DOH','LAX','Qatar Airways','2024-12-05 01:00:00','2024-12-05 10:00:00',1100,'Available'),(86,'QR602','LAX','DOH','Qatar Airways','2024-12-10 18:00:00','2024-12-11 04:00:00',1120,'On Time'),(87,'QR603','DOH','JFK','Qatar Airways','2024-12-20 23:00:00','2024-12-21 08:00:00',1050,'On Time'),(88,'QR604','JFK','DOH','Qatar Airways','2024-12-21 15:00:00','2024-12-22 01:00:00',1070,'Delayed'),(89,'QR605','DOH','ORD','Qatar Airways','2024-12-25 09:00:00','2024-12-25 17:00:00',950,'On Time'),(90,'LH701','FRA','ORD','Lufthansa','2024-12-01 08:00:00','2024-12-01 12:00:00',750,'On Time'),(91,'LH702','ORD','FRA','Lufthansa','2024-12-05 16:00:00','2024-12-06 06:00:00',770,'On Time'),(92,'LH703','FRA','JFK','Lufthansa','2024-12-10 14:00:00','2024-12-10 18:00:00',800,'Available'),(93,'LH704','JFK','FRA','Lufthansa','2024-12-15 20:00:00','2024-12-16 08:00:00',820,'On Time'),(94,'LH705','FRA','SFO','Lufthansa','2024-12-25 13:00:00','2024-12-25 21:00:00',780,'On Time'),(95,'AA205','JFK ','LAX','American Airlines','2024-12-03 14:00:00','2024-12-03 20:01:00',450,'Delayed'),(96,'AA206','HKG','SFO','American Airlines','2024-12-03 15:19:00','2024-12-04 15:19:00',1000,'Scheduled'),(97,'AA207','HKG','HND','American Airlines','2024-12-10 15:42:00','2024-12-11 15:43:00',1200,'Scheduled');
/*!40000 ALTER TABLE `flight` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `flight_airplane`
--

DROP TABLE IF EXISTS `flight_airplane`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `flight_airplane` (
  `flight_id` int(11) NOT NULL,
  `airplane_id` varchar(50) NOT NULL,
  `name_airline` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`flight_id`,`airplane_id`,`name_airline`),
  KEY `airplane_id` (`airplane_id`,`name_airline`),
  CONSTRAINT `flight_airplane_ibfk_1` FOREIGN KEY (`flight_id`) REFERENCES `flight` (`id`) ON DELETE CASCADE,
  CONSTRAINT `flight_airplane_ibfk_2` FOREIGN KEY (`airplane_id`, `name_airline`) REFERENCES `airplane` (`id`, `name_airline`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `flight_airplane`
--

LOCK TABLES `flight_airplane` WRITE;
/*!40000 ALTER TABLE `flight_airplane` DISABLE KEYS */;
/*!40000 ALTER TABLE `flight_airplane` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `permissions`
--

DROP TABLE IF EXISTS `permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(255) DEFAULT NULL,
  `permission` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `permissions_ibfk_1` (`username`),
  CONSTRAINT `permissions_ibfk_1` FOREIGN KEY (`username`) REFERENCES `airline_staff` (`username`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `permissions`
--

LOCK TABLES `permissions` WRITE;
/*!40000 ALTER TABLE `permissions` DISABLE KEYS */;
INSERT INTO `permissions` VALUES (5,'Dan_AA','Admin'),(6,'Dan_AA','Operator'),(7,'Amex','Admin'),(8,'Amex','Operator');
/*!40000 ALTER TABLE `permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `purchases`
--

DROP TABLE IF EXISTS `purchases`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `purchases` (
  `ticket_id` int(11) NOT NULL,
  `customer_email` varchar(100) NOT NULL,
  `booking_agent_id` varchar(200) DEFAULT NULL,
  `purchase_date` date NOT NULL,
  PRIMARY KEY (`ticket_id`,`customer_email`),
  KEY `customer_email` (`customer_email`),
  CONSTRAINT `purchases_ibfk_1` FOREIGN KEY (`ticket_id`) REFERENCES `ticket` (`ticket_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `purchases_ibfk_2` FOREIGN KEY (`customer_email`) REFERENCES `customer` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `purchases`
--

LOCK TABLES `purchases` WRITE;
/*!40000 ALTER TABLE `purchases` DISABLE KEYS */;
INSERT INTO `purchases` VALUES (81,'dsh400@nyu.edu','Geogre Bush Booking','2024-11-30'),(82,'customer1@example.com','Geogre Bush Booking','2024-11-30'),(91,'dsh400@nyu.edu',NULL,'2024-12-10');
/*!40000 ALTER TABLE `purchases` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ticket`
--

DROP TABLE IF EXISTS `ticket`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ticket` (
  `ticket_id` int(11) NOT NULL AUTO_INCREMENT,
  `name_airline` varchar(100) NOT NULL,
  `flight_number` varchar(10) NOT NULL,
  `depart_time` datetime DEFAULT NULL,
  `flight_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`ticket_id`),
  KEY `ticket_fk` (`name_airline`,`flight_number`,`depart_time`),
  KEY `fk_flight_id` (`flight_id`),
  CONSTRAINT `fk_flight_id` FOREIGN KEY (`flight_id`) REFERENCES `flight` (`id`) ON DELETE CASCADE,
  CONSTRAINT `ticket_fk` FOREIGN KEY (`name_airline`, `flight_number`, `depart_time`) REFERENCES `flight` (`name_airline`, `flight_number`, `depart_time`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `ticket_ibfk_1` FOREIGN KEY (`name_airline`, `flight_number`) REFERENCES `flight` (`name_airline`, `flight_number`)
) ENGINE=InnoDB AUTO_INCREMENT=92 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ticket`
--

LOCK TABLES `ticket` WRITE;
/*!40000 ALTER TABLE `ticket` DISABLE KEYS */;
INSERT INTO `ticket` VALUES (81,'American Airlines','AA203','2024-12-01 14:19:00',45),(82,'American Airlines','AA205','2024-12-01 14:00:00',47),(91,'American Airlines','AA207','2024-12-10 15:42:00',97);
/*!40000 ALTER TABLE `ticket` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-12-10 16:43:42
