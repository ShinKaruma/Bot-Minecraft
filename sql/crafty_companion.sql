-- phpMyAdmin SQL Dump
-- version 4.5.4.1
-- http://www.phpmyadmin.net
--
-- Client :  localhost
-- Généré le :  Dim 28 Avril 2024 à 12:31
-- Version du serveur :  5.7.11
-- Version de PHP :  7.0.3

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de données :  `crafty_companion`
--

-- --------------------------------------------------------

--
-- Structure de la table `achat`
--

CREATE TABLE `achat` (
  `id_serveur_discord` bigint(20) NOT NULL,
  `id_package` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Structure de la table `daily`
--

CREATE TABLE `daily` (
  `id_libelle` int(11) NOT NULL,
  `ID_Item` varchar(50) NOT NULL,
  `poids` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Contenu de la table `daily`
--

INSERT INTO `daily` (`id_libelle`, `ID_Item`, `poids`) VALUES
(1, "minecraft:deepslate 64", 40),
(2, "minecraft:stone 64", 40),
(3, "minecraft:birch_log 32", 30),
(4, "minecraft:oak_log 32", 30),
(5, "minecraft:spruce_log 32", 30),
(6, "minecraft:potato 16", 20),
(7, "minecraft:carrot 16", 20),
(8, "minecraft:gold_ingot 8", 10),
(9, "minecraft:iron_block 8", 10),
(10, "minecraft:experience_bottle 16", 15),
(11, "minecraft:enchanted_golden_apple 1", 6),
(12, "minecraft:netherite_ingot 1", 1),
(13, "minecraft:wither_skeleton_skull 1", 8),
(14, "minecraft:wither_skeleton_skull 2", 5),
(15, "minecraft:wither_skeleton_skull 3", 3);

-- --------------------------------------------------------

--
-- Structure de la table `daily_premium`
--

CREATE TABLE `daily_premium` (
  `ID_Item` varchar(50) NOT NULL,
  `poids` int(11) DEFAULT NULL,
  `id_serveur_discord` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Structure de la table `libelle_daily`
--

CREATE TABLE `libelle_daily` (
  `id_libelle` int(11) NOT NULL,
  `libelle` varchar(60) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Contenu de la table `libelle_daily`
--

INSERT INTO `libelle_daily` (`id_libelle`, `libelle`) VALUES
(1, "64 blocs de deepslate"),
(2, "64 blocs de stone"),
(3, "32 bûches de boulot"),
(4, "32 bûches de chêne"),
(5, "32 bûches de sapin"),
(6, "16 pommes de terre"),
(7, "16 carottes"),
(8, "8 lingots d'or"),
(9, "8 blocs de fer"),
(10, "16 bouteilles d'expérience"),
(11, "1 pomme d'or enchantée"),
(12, "1 lingot de netherite"),
(13, "1 crâne de wither squelette"),
(14, "2 crânes de wither squelette"),
(15, "3 crânes de wither squelette");

-- --------------------------------------------------------

--
-- Structure de la table `packages`
--

CREATE TABLE `packages` (
  `id_package` int(11) NOT NULL,
  `libelle` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Structure de la table `serveur`
--

CREATE TABLE `serveur` (
  `id_serveur_discord` bigint(20) NOT NULL,
  `ip_serveur_minecraft` varchar(15) DEFAULT NULL,
  `pwd_rcon` varbinary(50) DEFAULT NULL,
  `port_rcon` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Structure de la table `shop`
--

CREATE TABLE `shop` (
  `id_item` varchar(50) NOT NULL,
  `prix_item` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Structure de la table `shop_premium`
--

CREATE TABLE `shop_premium` (
  `id_item` varchar(50) NOT NULL,
  `prix_item` int(11) DEFAULT NULL,
  `id_serveur_discord` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Structure de la table `user`
--

CREATE TABLE `user` (
  `id_user_discord` bigint(20) NOT NULL,
  `id_serveur_discord` bigint(20) NOT NULL,
  `pseudo_minecraft` varchar(50) DEFAULT NULL,
  `date_dernier_daily` date DEFAULT NULL,
  `nb_daily` int(11) DEFAULT "0",
  `total_coins` int(11) DEFAULT "0"
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Index pour les tables exportées
--

--
-- Index pour la table `achat`
--
ALTER TABLE `achat`
  ADD PRIMARY KEY (`id_serveur_discord`,`id_package`),
  ADD KEY `id_package` (`id_package`);

--
-- Index pour la table `daily`
--
ALTER TABLE `daily`
  ADD PRIMARY KEY (`id_libelle`) USING BTREE;

--
-- Index pour la table `daily_premium`
--
ALTER TABLE `daily_premium`
  ADD PRIMARY KEY (`ID_Item`,`id_serveur_discord`),
  ADD KEY `id_serveur_discord` (`id_serveur_discord`);

--
-- Index pour la table `libelle_daily`
--
ALTER TABLE `libelle_daily`
  ADD PRIMARY KEY (`id_libelle`);

--
-- Index pour la table `packages`
--
ALTER TABLE `packages`
  ADD PRIMARY KEY (`id_package`);

--
-- Index pour la table `serveur`
--
ALTER TABLE `serveur`
  ADD PRIMARY KEY (`id_serveur_discord`);

--
-- Index pour la table `shop`
--
ALTER TABLE `shop`
  ADD PRIMARY KEY (`id_item`);

--
-- Index pour la table `shop_premium`
--
ALTER TABLE `shop_premium`
  ADD PRIMARY KEY (`id_item`,`id_serveur_discord`),
  ADD KEY `id_serveur_discord` (`id_serveur_discord`);

--
-- Index pour la table `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`id_user_discord`,`id_serveur_discord`),
  ADD KEY `id_serveur_discord` (`id_serveur_discord`);

--
-- Contraintes pour les tables exportées
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
-- Contraintes pour la table `libelle_daily`
--
ALTER TABLE `libelle_daily`
  ADD CONSTRAINT `fk_daily_libelle` FOREIGN KEY (`id_libelle`) REFERENCES `daily` (`id_libelle`) ON DELETE CASCADE ON UPDATE CASCADE;

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

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
