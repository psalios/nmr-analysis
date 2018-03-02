-- MySQL dump 10.13  Distrib 5.7.19, for osx10.12 (x86_64)
--
-- Host: localhost    Database: mp236_sh
-- ------------------------------------------------------
-- Server version	5.7.19

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `peaks`
--

DROP TABLE IF EXISTS `peaks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `peaks` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `peak` double(15,5) DEFAULT NULL,
  `class` varchar(4) DEFAULT 'm' NOT NULL,
  `spectrum_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_peak_spectrum` (`peak`,`spectrum_id`),
  KEY `fk_peaks_spectrum` (`spectrum_id`),
  CONSTRAINT `fk_peaks_spectrum` FOREIGN KEY (`spectrum_id`) REFERENCES `spectrum` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=33 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `peaks`
--

LOCK TABLES `peaks` WRITE;
/*!40000 ALTER TABLE `peaks` DISABLE KEYS */;
INSERT INTO `peaks` VALUES (2,1.00000,26),(4,2.00000,26),(5,3.50000,26),(32,8.27514,109),(29,8.27792,109);
/*!40000 ALTER TABLE `peaks` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `spectrum`
--

DROP TABLE IF EXISTS `spectrum`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `spectrum` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `hash` char(64) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `spectrum_hash_unique_key` (`hash`)
) ENGINE=InnoDB AUTO_INCREMENT=110 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `spectrum`
--

LOCK TABLES `spectrum` WRITE;
/*!40000 ALTER TABLE `spectrum` DISABLE KEYS */;
INSERT INTO `spectrum` VALUES (109,'034de96ab43d48e21a7a38395b612f10bf74a95fa5005a3e7d0a1cca26ec14cf'),(26,'e09f8840115808e27f5b6311eef903387a1d644cba21573696bfc2bf5cf87cb1');
/*!40000 ALTER TABLE `spectrum` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2018-02-11 20:31:52
