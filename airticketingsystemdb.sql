SET FOREIGN_KEY_CHECKS=0;

-- MySQL dump 10.13  Distrib 8.0.31, for Linux (x86_64)
--
-- Host: 127.0.0.1    Database: airticketingsystem
-- ------------------------------------------------------
-- Server version	8.0.31-google

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `airticketingsystem`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `airticketingsystem` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `airticketingsystem`;

--
-- Table structure for table `airline`
--

DROP TABLE IF EXISTS `airline`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `airline` (
  `name` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
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
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `airline_staff` (
  `username` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `name` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `password` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `first_name` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `last_name` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `date_of_birth` date DEFAULT NULL,
  PRIMARY KEY (`username`, `name`),
  KEY `name` (`name`),
  UNIQUE KEY `username` (`username`),
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

CREATE TABLE `airlinestaffpermission` (
  `username` varchar(100) NOT NULL,
  `name` varchar(100) NOT NULL,
  `permission` varchar(50) NOT NULL,
  PRIMARY KEY (`username`, `name`, `permission`),
  CONSTRAINT `airlinestaffpermission_ibfk_1` FOREIGN KEY (`username`, `name`) REFERENCES `airline_staff` (`username`, `name`) ON DELETE CASCADE
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
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `airplane` (
  `id` varchar(50) COLLATE utf8mb4_general_ci NOT NULL,
  `name_airline` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `capacity` int NOT NULL,
  `model` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `name_airline` (`name_airline`),
  UNIQUE KEY `idx_airplane_id_name_airline` (`id`, `name_airline`),
  CONSTRAINT `airplane_ibfk_1` FOREIGN KEY (`name_airline`) REFERENCES `airline` (`name`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `airplane`
--

LOCK TABLES `airplane` WRITE;
/*!40000 ALTER TABLE `airplane` DISABLE KEYS */;
INSERT INTO `airplane` VALUES ('999','American Airlines',2,'Boeing 747'),('B747-1','American Airlines',180,'Boeing 747'),('B747-2','American Airlines',180,'Boeing 747');
/*!40000 ALTER TABLE `airplane` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `airport`
--

DROP TABLE IF EXISTS `airport`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `airport` (
  `name` varchar(50) COLLATE utf8mb4_general_ci NOT NULL,
  `city` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL,
  PRIMARY KEY (`name`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `airport`
--

LOCK TABLES `airport` WRITE;
/*!40000 ALTER TABLE `airport` DISABLE KEYS */;
INSERT INTO `airport` VALUES ('ATL','Atlanta'),('CDG','Paris'),('DEN','Denver'),('DFW','Dallas'),('DOH','Doha'),('DXB','Dubai'),('FRA','Frankfurt'),('Hangzhou','HZI'),('HKG','Hong Kong'),('HND ','Tokyo'),('JFK','New York'),('LAX','Los Angeles'),('LHR','London'),('MIA','Miami'),('NUQ','California'),('ORD','Chicago'),('SEA','Seattle'),('SFO','San Francisco'),('SIN','Singapore');
/*!40000 ALTER TABLE `airport` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `booking_agent`
--

DROP TABLE IF EXISTS `booking_agent`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `booking_agent` (
  `email` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `password` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `booking_agent_id` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL,
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
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `customer` (
  `email` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `name` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `password` varchar(200) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `building_number` varchar(10) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `street` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `city` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `state` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `phone_number` varchar(15) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `passport_number` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `passport_expiration` date DEFAULT NULL,
  `passport_country` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `date_of_birth` date DEFAULT NULL,
  PRIMARY KEY (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `customer`
--

LOCK TABLES `customer` WRITE;
/*!40000 ALTER TABLE `customer` DISABLE KEYS */;
INSERT INTO `customer` VALUES ('customer1@example.com','Alice Johnson',NULL,'123','Main St','New York','NY','123-456-7890','P123456','2025-05-15','USA','1980-06-25'),('customer2@example.com','Bob Smith',NULL,'456','Broadway','Los Angeles','CA','234-567-8901','P654321','2026-03-10','USA','1985-09-12'),('customer3@example.com','Charlie Brown',NULL,'789','Ocean Drive','Miami','FL','345-678-9012','P987654','2027-01-20','USA','1990-11-05'),('customer4@example.com','Diana Prince',NULL,'321','Elm St','Seattle','WA','456-789-0123','P567890','2025-12-30','USA','1995-08-18'),('customer5@example.com','Ethan Hunt',NULL,'654','5th Ave','Chicago','IL','567-890-1234','P432109','2026-09-25','USA','1992-04-14'),('dsh400@nyu.edu','Dan Huynh','53bc3911362cda98b1014b8566f6800c72f6be0688961274130bd6a3fcfee8b9','','65 Duong 51 Binh Trung Dong, Quan 2','Ho Chi Minh','HCM','0901663700','123','2024-11-01','VN','2024-11-30'),('Newguy@gmail.com','New Guy ','53bc3911362cda98b1014b8566f6800c72f6be0688961274130bd6a3fcfee8b9','12','140 E 14th Street','NYC','NY','+16468525947','G262','2028-11-11','GR','2001-04-23'),('squirrelboat@gmail.com','Dan Huynh','53bc3911362cda98b1014b8566f6800c72f6be0688961274130bd6a3fcfee8b9','0','140 E 14 St','New York','NY','+16468525947','US122','2024-12-10','US','2024-12-10'),('wawa@gmail.com','Dan','53bc3911362cda98b1014b8566f6800c72f6be0688961274130bd6a3fcfee8b9','','140 E 14 St','New York','NY','+16468525947','C19865877','2024-11-30','VN','2001-04-23');
/*!40000 ALTER TABLE `customer` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `flight`
--

DROP TABLE IF EXISTS `flight`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `flight` (
  `id` int NOT NULL AUTO_INCREMENT,
  `flight_number` varchar(10) COLLATE utf8mb4_general_ci NOT NULL,
  `name_depart` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `name_arrive` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `name_airline` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `depart_time` datetime NOT NULL,
  `arrive_time` datetime NOT NULL,
  `price` int NOT NULL,
  `status` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `seats` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_flight` (`name_airline`,`flight_number`,`depart_time`),
  KEY `name_depart` (`name_depart`),
  KEY `name_arrive` (`name_arrive`),
  CONSTRAINT `flight_ibfk_1` FOREIGN KEY (`name_depart`) REFERENCES `airport` (`name`),
  CONSTRAINT `flight_ibfk_2` FOREIGN KEY (`name_arrive`) REFERENCES `airport` (`name`),
  CONSTRAINT `flight_ibfk_3` FOREIGN KEY (`name_airline`) REFERENCES `airline` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=109 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `flight`
--

LOCK TABLES `flight` WRITE;
/*!40000 ALTER TABLE `flight` DISABLE KEYS */;
INSERT INTO `flight` VALUES (1,'AA101','JFK','LAX','American Airlines','2024-11-15 08:00:00','2024-11-15 11:00:00',350,'Completed',NULL),(2,'AA102','JFK','LAX','American Airlines','2024-11-15 08:30:00','2024-11-15 11:30:00',350,'Completed',NULL),(3,'DL103','ORD','MIA','Delta Airlines','2024-11-15 09:30:00','2024-11-15 12:30:00',400,'Available',NULL),(4,'UA104','SFO','SEA','United Airlines','2024-11-15 14:00:00','2024-11-15 16:00:00',200,'On Time',NULL),(5,'AF105','CDG','ATL','Air France','2024-11-15 10:00:00','2024-11-15 15:00:00',450,'On Time',NULL),(6,'BA106','LHR','JFK','British Airways','2024-11-17 16:00:00','2024-11-17 19:00:00',500,'On Time',NULL),(7,'EK107','DXB','SFO','Emirates','2024-11-20 22:00:00','2024-11-21 08:00:00',600,'On Time',NULL),(8,'LH108','FRA','ORD','Lufthansa','2024-11-19 12:00:00','2024-11-19 17:00:00',400,'Delayed',NULL),(9,'QR109','DOH','LAX','Qatar Airways','2024-11-21 01:00:00','2024-11-21 11:00:00',620,'On Time',NULL),(10,'SQ110','SIN','LHR','Singapore Airlines','2024-11-22 22:00:00','2024-11-22 22:00:00',550,'On Time',NULL),(11,'SW111','JFK','LAX','Southwest Airlines','2024-11-15 11:00:00','2024-11-15 14:00:00',375,'Available',NULL),(12,'SW112','DFW','DEN','Southwest Airlines','2024-11-16 12:00:00','2024-11-16 13:30:00',150,'Cancelled',NULL),(13,'UA113','JFK','LAX','United Airlines','2024-11-15 13:00:00','2024-11-15 15:00:00',450,'Available',NULL),(14,'AA114','ORD','SFO','American Airlines','2024-11-15 09:00:00','2024-11-15 12:00:00',500,'Completed',NULL),(15,'DL115','JFK','LAX','Delta Airlines','2024-11-15 14:00:00','2024-11-15 16:30:00',375,'On Time',NULL),(16,'AF116','CDG','ORD','Air France','2024-11-16 07:00:00','2024-11-16 12:00:00',525,'Delayed',NULL),(17,'BA117','LHR','JFK','British Airways','2024-11-17 09:00:00','2024-11-17 12:00:00',490,'Available',NULL),(18,'EK118','DXB','LAX','Emirates','2024-11-18 13:00:00','2024-11-18 18:00:00',650,'On Time',NULL),(19,'LH119','FRA','ORD','Lufthansa','2024-11-19 16:00:00','2024-11-19 20:00:00',470,'On Time',NULL),(20,'QR120','DOH','LHR','Qatar Airways','2024-11-20 06:00:00','2024-11-20 11:00:00',560,'Available',NULL),(21,'SQ121','SIN','SFO','Singapore Airlines','2024-11-22 09:00:00','2024-11-22 18:00:00',700,'On Time',NULL),(22,'SW122','JFK','SEA','Southwest Airlines','2024-11-22 15:00:00','2024-11-22 17:00:00',250,'Cancelled',NULL),(23,'UA123','ORD','LAX','United Airlines','2024-11-15 07:00:00','2024-11-15 09:00:00',330,'Available',NULL),(24,'AA124','JFK','LAX','American Airlines','2024-11-15 08:30:00','2024-11-15 11:30:00',350,'Available',NULL),(25,'DL125','ORD','MIA','Delta Airlines','2024-11-16 11:00:00','2024-11-16 14:00:00',400,'Delayed',NULL),(26,'AF126','CDG','SFO','Air France','2024-11-17 12:00:00','2024-11-17 17:00:00',420,'On Time',NULL),(27,'BA127','LHR','ORD','British Airways','2024-11-18 08:00:00','2024-11-18 11:30:00',450,'Available',NULL),(28,'EK128','DXB','LAX','Emirates','2024-11-19 21:00:00','2024-11-20 06:00:00',550,'Available',NULL),(29,'AA125','JFK','LAX','American Airlines','2024-11-14 09:00:00','2024-11-14 12:00:00',330,'On Time',NULL),(30,'AA126','JFK','LAX','American Airlines','2024-11-14 13:00:00','2024-11-14 16:00:00',340,'Available',NULL),(31,'DL127','JFK','LAX','Delta Airlines','2024-11-14 11:30:00','2024-11-14 14:30:00',380,'Available',NULL),(32,'DL128','JFK','LAX','Delta Airlines','2024-11-14 14:00:00','2024-11-14 17:00:00',390,'On Time',NULL),(33,'UA129','JFK','LAX','United Airlines','2024-11-14 08:30:00','2024-11-14 11:30:00',320,'Delayed',NULL),(34,'UA130','JFK','LAX','United Airlines','2024-11-14 10:00:00','2024-11-14 13:00:00',340,'On Time',NULL),(35,'AA131','JFK','LAX','American Airlines','2024-11-16 09:00:00','2024-11-16 12:00:00',355,'Available',NULL),(36,'AA132','JFK','LAX','American Airlines','2024-11-16 12:30:00','2024-11-16 15:30:00',365,'On Time',NULL),(37,'DL133','JFK','LAX','Delta Airlines','2024-11-16 08:30:00','2024-11-16 11:30:00',400,'Available',NULL),(38,'DL134','JFK','LAX','Delta Airlines','2024-11-16 13:00:00','2024-11-16 16:00:00',410,'Delayed',NULL),(39,'UA135','JFK','LAX','United Airlines','2024-11-16 14:00:00','2024-11-16 17:00:00',330,'On Time',NULL),(40,'UA136','JFK','LAX','United Airlines','2024-11-16 16:30:00','2024-11-16 19:30:00',350,'Available',NULL),(41,'AA137','JFK','LAX','American Airlines','2024-11-17 07:00:00','2024-11-17 10:00:00',340,'On Time',NULL),(42,'AA138','JFK','LAX','American Airlines','2024-11-17 10:30:00','2024-11-17 13:30:00',355,'Scheduled',NULL),(43,'DL139','JFK','LAX','Delta Airlines','2024-11-17 12:00:00','2024-11-17 15:00:00',400,'On Time',NULL),(44,'DL140','JFK','LAX','Delta Airlines','2024-11-17 14:30:00','2024-11-17 17:30:00',410,'Available',NULL),(45,'AA203','JFK ','LAX','American Airlines','2024-12-01 14:19:00','2024-12-02 14:19:00',475,'Scheduled',NULL),(46,'AA204','JFK','LAX','American Airlines','2024-12-03 14:23:00','2024-12-03 14:23:00',200,'Scheduled',NULL),(47,'AA205','JFK','HND','American Airlines','2024-12-01 14:00:00','2024-12-02 07:00:00',800,'Delayed',NULL),(65,'AA201','JFK','LAX','American Airlines','2024-12-01 08:00:00','2024-12-01 11:30:00',375,'On Time',NULL),(66,'AA202','LAX','JFK','American Airlines','2024-12-01 14:00:00','2024-12-01 22:00:00',400,'On Time',NULL),(67,'AA203','ORD','ATL','American Airlines','2024-12-05 10:00:00','2024-12-05 12:30:00',250,'Scheduled',NULL),(68,'AA204','DFW','MIA','American Airlines','2024-12-06 06:00:00','2024-12-06 09:00:00',275,'On Time',NULL),(69,'AA205','ATL','ORD','American Airlines','2024-12-10 18:00:00','2024-12-10 20:30:00',240,'Delayed',NULL),(70,'DL301','SEA','SFO','Delta Airlines','2024-12-02 12:00:00','2024-12-02 14:00:00',200,'On Time',NULL),(71,'DL302','SFO','SEA','Delta Airlines','2024-12-02 16:00:00','2024-12-02 18:00:00',210,'On Time',NULL),(72,'DL303','LAX','ATL','Delta Airlines','2024-12-07 20:00:00','2024-12-08 00:30:00',340,'On Time',NULL),(73,'DL304','ORD','LHR','Delta Airlines','2024-12-15 18:00:00','2024-12-16 06:00:00',650,'Available',NULL),(74,'DL305','MIA','JFK','Delta Airlines','2024-12-20 09:00:00','2024-12-20 12:00:00',310,'On Time',NULL),(75,'UA401','ORD','DEN','United Airlines','2024-12-01 07:00:00','2024-12-01 09:00:00',150,'On Time',NULL),(76,'UA402','DEN','ORD','United Airlines','2024-12-01 12:00:00','2024-12-01 14:00:00',160,'Available',NULL),(77,'UA403','LAX','DFW','United Airlines','2024-12-10 15:00:00','2024-12-10 18:00:00',275,'On Time',NULL),(78,'UA404','JFK','SEA','United Airlines','2024-12-12 06:00:00','2024-12-12 10:00:00',450,'Delayed',NULL),(79,'UA405','SEA','JFK','United Airlines','2024-12-13 20:00:00','2024-12-14 00:30:00',460,'On Time',NULL),(80,'EK501','DXB','SIN','Emirates','2024-12-03 22:00:00','2024-12-04 05:00:00',800,'On Time',NULL),(81,'EK502','SIN','DXB','Emirates','2024-12-04 10:00:00','2024-12-04 17:00:00',820,'On Time',NULL),(82,'EK503','DXB','LHR','Emirates','2024-12-07 14:00:00','2024-12-07 20:00:00',900,'Available',NULL),(83,'EK504','LHR','DXB','Emirates','2024-12-08 10:00:00','2024-12-08 18:00:00',920,'On Time',NULL),(84,'EK505','DXB','JFK','Emirates','2024-12-15 23:00:00','2024-12-16 09:00:00',1000,'On Time',NULL),(85,'QR601','DOH','LAX','Qatar Airways','2024-12-05 01:00:00','2024-12-05 10:00:00',1100,'Available',NULL),(86,'QR602','LAX','DOH','Qatar Airways','2024-12-10 18:00:00','2024-12-11 04:00:00',1120,'On Time',NULL),(87,'QR603','DOH','JFK','Qatar Airways','2024-12-20 23:00:00','2024-12-21 08:00:00',1050,'On Time',NULL),(88,'QR604','JFK','DOH','Qatar Airways','2024-12-21 15:00:00','2024-12-22 01:00:00',1070,'Delayed',NULL),(89,'QR605','DOH','ORD','Qatar Airways','2024-12-25 09:00:00','2024-12-25 17:00:00',950,'On Time',NULL),(90,'LH701','FRA','ORD','Lufthansa','2024-12-01 08:00:00','2024-12-01 12:00:00',750,'On Time',NULL),(91,'LH702','ORD','FRA','Lufthansa','2024-12-05 16:00:00','2024-12-06 06:00:00',770,'On Time',NULL),(92,'LH703','FRA','JFK','Lufthansa','2024-12-10 14:00:00','2024-12-10 18:00:00',800,'Available',NULL),(93,'LH704','JFK','FRA','Lufthansa','2024-12-15 20:00:00','2024-12-16 08:00:00',820,'On Time',NULL),(94,'LH705','FRA','SFO','Lufthansa','2024-12-25 13:00:00','2024-12-25 21:00:00',780,'On Time',NULL),(95,'AA205','JFK ','LAX','American Airlines','2024-12-03 14:00:00','2024-12-03 20:01:00',450,'Delayed',NULL),(96,'AA206','HKG','SFO','American Airlines','2024-12-03 15:19:00','2024-12-04 15:19:00',1000,'Scheduled',NULL),(97,'AA207','HKG','HND','American Airlines','2024-12-10 15:42:00','2024-12-11 15:43:00',1200,'Scheduled',NULL),(99,'AA301','NUQ','JFK','American Airlines','2024-12-10 19:23:00','2024-12-11 19:23:00',400,'Scheduled',NULL),(100,'AA302','NUQ','SFO','American Airlines','2024-12-11 15:57:00','2024-12-12 15:57:00',670,'Scheduled',NULL),(101,'AA401','NUQ','HND','American Airlines','2024-12-12 12:14:00','2024-12-13 12:14:00',1203,'Scheduled',NULL),(102,'AA405','JFK','HND','American Airlines','2024-12-12 12:43:00','2024-12-13 12:43:00',1400,'Scheduled',NULL),(104,'9999','Hangzhou','JFK','American Airlines','2024-12-12 13:13:00','2024-12-13 13:13:00',1300,'Scheduled',NULL),(105,'AA707','JFK','HND','American Airlines','2024-12-12 14:33:00','2024-12-13 14:33:00',2000,'Scheduled',1),(106,'AA301','JFK ','SFO','American Airlines','2024-12-12 14:40:00','2024-12-13 14:40:00',120,'Scheduled',2),(107,'AA206','JFK ','HND','American Airlines','2024-12-13 15:14:00','2024-12-14 15:14:00',2002,'Scheduled',1),(108,' AA809','JFK','SFO','American Airlines','2024-12-14 15:21:00','2024-12-14 18:21:00',1200,'Scheduled',1);
/*!40000 ALTER TABLE `flight` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `flight_airplane`
--

DROP TABLE IF EXISTS `flight_airplane`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `flight_airplane` (
  `flight_id` int NOT NULL,
  `airplane_id` varchar(50) COLLATE utf8mb4_general_ci NOT NULL,
  `name_airline` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
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
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `permissions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `permission` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
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
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `purchases` (
  `ticket_id` int NOT NULL,
  `customer_email` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `booking_agent_id` varchar(200) COLLATE utf8mb4_general_ci DEFAULT NULL,
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
INSERT INTO `purchases` VALUES (81,'dsh400@nyu.edu','Geogre Bush Booking','2024-11-30'),(82,'customer1@example.com','Geogre Bush Booking','2024-11-30'),(91,'dsh400@nyu.edu',NULL,'2024-12-10'),(92,'dsh400@nyu.edu',NULL,'2024-12-10'),(93,'dsh400@nyu.edu',NULL,'2024-12-10'),(94,'dsh400@nyu.edu',NULL,'2024-12-10'),(95,'dsh400@nyu.edu',NULL,'2024-12-10'),(96,'squirrelboat@gmail.com',NULL,'2024-12-10'),(97,'dsh400@nyu.edu',NULL,'2024-12-11'),(98,'dsh400@nyu.edu','Jeff Book','2024-12-12'),(99,'dsh400@nyu.edu','Jeff Book','2024-12-12'),(100,'dsh400@nyu.edu','Jeff Book','2024-12-12'),(101,'dsh400@nyu.edu',NULL,'2024-12-12'),(102,'dsh400@nyu.edu',NULL,'2024-12-12'),(103,'dsh400@nyu.edu',NULL,'2024-12-12'),(104,'dsh400@nyu.edu',NULL,'2024-12-12');
/*!40000 ALTER TABLE `purchases` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ticket`
--

DROP TABLE IF EXISTS `ticket`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ticket` (
  `ticket_id` int NOT NULL AUTO_INCREMENT,
  `name_airline` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `flight_number` varchar(10) COLLATE utf8mb4_general_ci NOT NULL,
  `depart_time` datetime DEFAULT NULL,
  `flight_id` int DEFAULT NULL,
  PRIMARY KEY (`ticket_id`),
  KEY `ticket_fk` (`name_airline`, `flight_number`, `depart_time`),
  KEY `fk_flight_id` (`flight_id`),
  CONSTRAINT `fk_flight_id` FOREIGN KEY (`flight_id`) 
    REFERENCES `flight` (`id`) 
    ON DELETE CASCADE,
  CONSTRAINT `ticket_fk` FOREIGN KEY (`name_airline`, `flight_number`, `depart_time`) 
    REFERENCES `flight` (`name_airline`, `flight_number`, `depart_time`) 
    ON DELETE CASCADE 
    ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=105 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ticket`
--

LOCK TABLES `ticket` WRITE;
/*!40000 ALTER TABLE `ticket` DISABLE KEYS */;
INSERT INTO `ticket` VALUES (81,'American Airlines','AA203','2024-12-01 14:19:00',45),(82,'American Airlines','AA205','2024-12-01 14:00:00',47),(91,'American Airlines','AA207','2024-12-10 15:42:00',97),(92,'American Airlines','AA207','2024-12-10 15:42:00',97),(93,'American Airlines','AA207','2024-12-10 15:42:00',97),(94,'American Airlines','AA205','2024-12-01 14:00:00',47),(95,'American Airlines','AA301','2024-12-10 19:23:00',99),(96,'American Airlines','AA301','2024-12-10 19:23:00',99),(97,'American Airlines','AA302','2024-12-11 15:57:00',100),(98,'American Airlines','AA401','2024-12-12 12:14:00',101),(99,'American Airlines','9999','2024-12-12 13:13:00',104),(100,'American Airlines','9999','2024-12-12 13:13:00',104),(101,'American Airlines','AA301','2024-12-12 14:40:00',106),(102,'American Airlines','AA301','2024-12-12 14:40:00',106),(103,'American Airlines','AA707','2024-12-12 14:33:00',105),(104,'American Airlines','AA206','2024-12-13 15:14:00',107);
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

-- Dump completed on 2024-12-20 10:07:56
