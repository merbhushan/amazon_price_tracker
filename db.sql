-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Server version:               8.0.21 - MySQL Community Server - GPL
-- Server OS:                    Win64
-- HeidiSQL Version:             10.2.0.5599
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;


-- Dumping database structure for digital_marketing
CREATE DATABASE IF NOT EXISTS `digital_marketing` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `digital_marketing`;

-- Dumping structure for table digital_marketing.amazon_price_history
CREATE TABLE IF NOT EXISTS `amazon_price_history` (
  `product_id` int unsigned DEFAULT NULL,
  `price` float unsigned DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Data exporting was unselected.

-- Dumping structure for table digital_marketing.amazon_products
CREATE TABLE IF NOT EXISTS `amazon_products` (
  `url` varchar(1000) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Data exporting was unselected.

-- Dumping structure for table digital_marketing.products
CREATE TABLE IF NOT EXISTS `products` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `amazon_url` varchar(1000) DEFAULT NULL,
  `amazon_converted_url` varchar(1000) DEFAULT NULL,
  `status` enum('Active','Inactive','Error') DEFAULT 'Active',
  `mrp` float DEFAULT NULL,
  `amazon_price` float DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Data exporting was unselected.

-- Dumping structure for trigger digital_marketing.products_after_insert
SET @OLDTMP_SQL_MODE=@@SQL_MODE, SQL_MODE='STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION';
DELIMITER //
CREATE TRIGGER `products_after_insert` AFTER INSERT ON `products` FOR EACH ROW BEGIN
	IF(NEW.amazon_price IS NOT NULL AND NEW.amazon_price > 0) THEN
		INSERT INTO amazon_price_history
			(amazon_price_history.product_id, amazon_price_history.price)
		VALUES
			(NEW.id, NEW.amazon_price);
	END IF;
END//
DELIMITER ;
SET SQL_MODE=@OLDTMP_SQL_MODE;

-- Dumping structure for trigger digital_marketing.products_before_update
SET @OLDTMP_SQL_MODE=@@SQL_MODE, SQL_MODE='STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION';
DELIMITER //
CREATE TRIGGER `products_before_update` BEFORE UPDATE ON `products` FOR EACH ROW BEGIN
	IF NEW.amazon_price <> OLD.amazon_price AND NEW.amazon_price IS NOT NULL AND NEW.amazon_price > 0 THEN
		INSERT INTO amazon_price_history
			(amazon_price_history.product_id, amazon_price_history.price)
		VALUES
			(NEW.id, NEW.amazon_price);
	END IF;

	IF NEW.amazon_url <> OLD.amazon_url THEN
		SET NEW.amazon_converted_url = NULL;
	END IF;
END//
DELIMITER ;
SET SQL_MODE=@OLDTMP_SQL_MODE;

/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IF(@OLD_FOREIGN_KEY_CHECKS IS NULL, 1, @OLD_FOREIGN_KEY_CHECKS) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
