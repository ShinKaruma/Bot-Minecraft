-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Hôte : 127.0.0.1:3306
-- Généré le : sam. 19 août 2023 à 20:45
-- Version du serveur : 8.0.31
-- Version de PHP : 8.0.26

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de données : `crafty_companion`
--

-- --------------------------------------------------------

--
-- Structure de la table `achat`
--

DROP TABLE IF EXISTS `achat`;
CREATE TABLE IF NOT EXISTS `achat` (
  `id_serveur_discord` bigint NOT NULL,
  `id_package` int NOT NULL,
  PRIMARY KEY (`id_serveur_discord`,`id_package`),
  KEY `id_package` (`id_package`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4  ;

-- --------------------------------------------------------

--
-- Structure de la table `daily`
--

DROP TABLE IF EXISTS `daily`;
CREATE TABLE IF NOT EXISTS `daily` (
  `ID_Item` varchar(50) NOT NULL,
  `poids` int DEFAULT NULL,
  PRIMARY KEY (`ID_Item`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4  ;

-- --------------------------------------------------------

--
-- Structure de la table `daily_premium`
--

DROP TABLE IF EXISTS `daily_premium`;
CREATE TABLE IF NOT EXISTS `daily_premium` (
  `ID_Item` varchar(50) NOT NULL,
  `poids` int DEFAULT NULL,
  `id_serveur_discord` bigint NOT NULL,
  PRIMARY KEY (`ID_Item`,`id_serveur_discord`),
  KEY `id_serveur_discord` (`id_serveur_discord`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4  ;

-- --------------------------------------------------------

--
-- Structure de la table `packages`
--

DROP TABLE IF EXISTS `packages`;
CREATE TABLE IF NOT EXISTS `packages` (
  `id_package` int NOT NULL,
  `libelle` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id_package`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4  ;

-- --------------------------------------------------------

--
-- Structure de la table `serveur`
--

DROP TABLE IF EXISTS `serveur`;
CREATE TABLE IF NOT EXISTS `serveur` (
  `id_serveur_discord` bigint NOT NULL,
  `ip_serveur_minecraft` varchar(15) DEFAULT NULL,
  `pwd_rcon` varchar(50) DEFAULT NULL,
  `port_rcon` int DEFAULT NULL,
  PRIMARY KEY (`id_serveur_discord`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4  ;

-- --------------------------------------------------------

--
-- Structure de la table `shop`
--

DROP TABLE IF EXISTS `shop`;
CREATE TABLE IF NOT EXISTS `shop` (
  `id_item` varchar(50) NOT NULL,
  `prix_item` int DEFAULT NULL,
  PRIMARY KEY (`id_item`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4  ;

-- --------------------------------------------------------

--
-- Structure de la table `shop_premium`
--

DROP TABLE IF EXISTS `shop_premium`;
CREATE TABLE IF NOT EXISTS `shop_premium` (
  `id_item` varchar(50) NOT NULL,
  `prix_item` int DEFAULT NULL,
  `id_serveur_discord` bigint NOT NULL,
  PRIMARY KEY (`id_item`,`id_serveur_discord`),
  KEY `id_serveur_discord` (`id_serveur_discord`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4  ;

-- --------------------------------------------------------

--
-- Structure de la table `user`
--

DROP TABLE IF EXISTS `user`;
CREATE TABLE IF NOT EXISTS `user` (
  `id_user_discord` bigint NOT NULL,
  `pseudo_minecraft` varchar(50) DEFAULT NULL,
  `date_dernier_daily` date DEFAULT NULL,
  `nb_daily` int DEFAULT NULL,
  `id_serveur_discord` bigint NOT NULL,
  PRIMARY KEY (`id_user_discord`,`id_serveur_discord`),
  UNIQUE KEY `pseudo_minecraft` (`pseudo_minecraft`),
  KEY `id_serveur_discord` (`id_serveur_discord`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4  ;

--
-- Contraintes pour les tables déchargées
--

--
-- Contraintes pour la table `achat`
--
ALTER TABLE `achat`
  ADD CONSTRAINT `achat_ibfk_1` FOREIGN KEY (`id_serveur_discord`) REFERENCES `serveur` (`id_serveur_discord`),
  ADD CONSTRAINT `achat_ibfk_2` FOREIGN KEY (`id_package`) REFERENCES `packages` (`id_package`);

--
-- Contraintes pour la table `daily_premium`
--
ALTER TABLE `daily_premium`
  ADD CONSTRAINT `daily_premium_ibfk_1` FOREIGN KEY (`id_serveur_discord`) REFERENCES `serveur` (`id_serveur_discord`);

--
-- Contraintes pour la table `shop_premium`
--
ALTER TABLE `shop_premium`
  ADD CONSTRAINT `shop_premium_ibfk_1` FOREIGN KEY (`id_serveur_discord`) REFERENCES `serveur` (`id_serveur_discord`);

--
-- Contraintes pour la table `user`
--
ALTER TABLE `user`
  ADD CONSTRAINT `user_ibfk_1` FOREIGN KEY (`id_serveur_discord`) REFERENCES `serveur` (`id_serveur_discord`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
