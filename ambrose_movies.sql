-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jun 03, 2025 at 09:49 PM
-- Server version: 10.4.28-MariaDB
-- PHP Version: 8.2.4

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `ambrose_movies`
--

-- --------------------------------------------------------

--
-- Table structure for table `actors`
--

CREATE TABLE `actors` (
  `actor_id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `birthdate` date DEFAULT NULL,
  `gender` varchar(10) DEFAULT NULL,
  `nationality` varchar(255) DEFAULT NULL,
  `date_id` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `catalog`
--

CREATE TABLE `catalog` (
  `id` int(11) NOT NULL,
  `catalog_id` varchar(30) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `date_id` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `directors`
--

CREATE TABLE `directors` (
  `director_id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `birthdate` date DEFAULT NULL,
  `nationality` varchar(255) DEFAULT NULL,
  `date_id` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `genres`
--

CREATE TABLE `genres` (
  `genre_id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `date_id` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `movies`
--

CREATE TABLE `movies` (
  `movie_id` int(11) NOT NULL,
  `user_id` varchar(30) DEFAULT NULL,
  `catalog_id` varchar(255) DEFAULT NULL,
  `title` varchar(255) NOT NULL,
  `description` text DEFAULT NULL,
  `runtime` varchar(255) DEFAULT NULL,
  `release_date` varchar(50) DEFAULT NULL,
  `genres` varchar(255) DEFAULT NULL,
  `cast` varchar(255) DEFAULT NULL,
  `director` varchar(255) DEFAULT NULL,
  `producer` varchar(255) DEFAULT NULL,
  `keywords` varchar(255) DEFAULT NULL,
  `images` varchar(255) DEFAULT NULL,
  `video_link` text DEFAULT NULL,
  `date_id` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `movies`
--

INSERT INTO `movies` (`movie_id`, `user_id`, `catalog_id`, `title`, `description`, `runtime`, `release_date`, `genres`, `cast`, `director`, `producer`, `keywords`, `images`, `video_link`, `date_id`) VALUES
(1, 'uid', 'cid', 'the movie title', 'the long description', '12:34', '2024', 'action, 18+', 'Silver stone, Amber rose', 'geuu nation', 'don jzzy', 'fntcy, fiction, commitment', 'cover.jpg', 'https://www.youtube.com/watch?v=_PS6rQBXJ54', '2025-03-16 02:58:23'),
(5, '1', '1', 'The Dark Knight', 'A battle between Batman and Joker', '152', '2025-03-12', ' Action, Crime', 'Heath Ledger, Christian Bale, Morgan Freeman', 'Christopher Nolan', 'Warner Bros.', 'atman, Joker, Gotham', 'cover4.jpg', 'https://www.youtube.com/watch?si=06p2hXZNgxETDIpH', '2025-03-17 09:05:06'),
(6, '1', '1', 'Inception', 'A thief enters dreams to steal secrets', '148', '2025-03-08', 'Sci-Fi, Thriller', ' Leonardo DiCaprio, Joseph Gordon-Levitt, Tom Hardy', 'Christopher Nolan', 'Legendary Pictures', 'Dreams, Heist, Mind', 'cover8.jpg', 'https://www.youtube.com/watch?v=Yi9tdfPegdk', '2025-03-17 09:09:23'),
(7, '1', '1', 'Titanic', 'A love story on a doomed ship', '195', '2025-03-06', 'Romance, Drama', ' Leonardo DiCaprio, Kate Winslet, Billy Zane', 'James Cameron', 'Paramount Pictures', 'Romance, Shipwreck, Love', 'cover13.jpg', 'https://www.youtube.com/watch?v=ZihFGIzdpz8', '2025-03-17 09:12:55'),
(8, '1', '1', 'Superman Batman', 'Based on the comedy series', '195', '2025-02-06', 'Action, Romance, Drama', ' Leonardo DiCaprio, Kate Winslet, Billy Zane', 'James Cameron', 'Paramount Pictures', 'Romance, Shipwreck, Love', 'cover15.jpg', 'https://www.youtube.com/watch?v=ZihFGIzdpz8', '2025-03-18 20:54:50'),
(9, '1', '1', 'Superman Batman', 'Superman is the best moviess in the world', '195', '2025-05-07', 'Action, Romance, Drama', ' Leonardo DiCaprio, Kate Winslet, Billy Zane', 'James Cameron', 'Paramount Pictures', 'Romance, Shipwreck, Love', 'first.png', 'https://www.youtube.com/watch?v=ZihFGIzdpz8', '2025-05-08 19:08:56'),
(10, '1', '1', 'The Green Latern', 'The best movie in the world', '167', '2025-05-01', 'Action, Romance, Drama', ' Leonardo DiCaprio, Kate Winslet, Billy Zane', 'James Cameron', 'Paramount Pictures', 'Romance, Shipwreck, Love', 'Screenshot_2023-08-17_215119.png', 'https://www.youtube.com/watch?v=ZihFGIzdpz8', '2025-05-08 19:28:14'),
(11, '1', '5', 'The Matrix', 'A hacker discovers reality is a simulation.', '136', '1999-03-31', 'Sci-Fi, Action', 'Keanu Reeves, Laurence Fishburne', 'Lana Wachowski, Lilly Wachowski', 'Joel Silver', 'matrix, simulation, action', 'IMG-20231010-WA0003_1.jpg', 'https://www.youtube.com/watch?v=vKQi3bBA1y8', '2025-05-20 21:51:20');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `user_id` varchar(30) DEFAULT NULL,
  `full_name` varchar(255) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `phone` varchar(30) DEFAULT NULL,
  `date_id` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `user_id`, `full_name`, `email`, `password`, `phone`, `date_id`) VALUES
(1, NULL, 'Unyime Ephraim Udoh', 'udohunyime0@gmail.com', '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4', '09025928492', '2025-03-14 05:08:31'),
(2, NULL, 'Unyime Ephraim Udoh', 'udohunyime0@gmail.com', '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4', '09025928492', '2025-03-14 05:41:36'),
(3, NULL, 'Unyime Ephraim Udoh', 'udohunyime0@gmail.com', '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4', '09025928492', '2025-03-14 06:09:13'),
(4, '608093219184869719212566170383', 'Unyime Ephraim Udoh', 'udohunyime1@gmail.com', '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4', '09025928492', '2025-03-18 19:45:23'),
(5, '873070981322904351892697539791', 'Ambrose Ali', 'ambrose@gmail.com', '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4', '08136146684', '2025-03-18 20:52:47'),
(6, '215868139402111900356700510949', 'Peter', 'peter@gmail.com', '21665c051f0a2fadcb29a51c02cbedcdb20ced2a95089dd058d5fe112ec44eb7', '0987654321', '2025-05-08 19:01:44'),
(7, '699382266666744490684442085019', 'Sam Loco', 'sam@gmail.com', 'c3334b243d9f0bc5100861f54b982fe184a471cb57c64ac849da76ce943932aa', '1234567890', '2025-05-08 19:24:04'),
(8, '289808812591949393001104199106', 'test1', 'test1@gmail.com', '937e8d5fbb48bd4949536cd65b8d35c426b80d2f830c5c308e2cdec422ae2244', '1234567890', '2025-05-17 07:01:03'),
(9, '279289601815514257576101580208', 'John Doe', 'john.doe@example.com', 'dda69783f28fdf6f1c5a83e8400f2472e9300887d1dffffe12a07b92a3d0aa25', '1234567890', '2025-05-19 09:38:49'),
(10, '121292774759313402255070270144', 'John Doe', 'john.doe@example.com', 'dda69783f28fdf6f1c5a83e8400f2472e9300887d1dffffe12a07b92a3d0aa25', '1234567890', '2025-05-19 11:36:06'),
(11, '127049962002566992162690256304', 'test1', 'test1@gmail.com', '937e8d5fbb48bd4949536cd65b8d35c426b80d2f830c5c308e2cdec422ae2244', '1234567890', '2025-05-22 05:58:45');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `actors`
--
ALTER TABLE `actors`
  ADD PRIMARY KEY (`actor_id`);

--
-- Indexes for table `catalog`
--
ALTER TABLE `catalog`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `directors`
--
ALTER TABLE `directors`
  ADD PRIMARY KEY (`director_id`);

--
-- Indexes for table `genres`
--
ALTER TABLE `genres`
  ADD PRIMARY KEY (`genre_id`),
  ADD UNIQUE KEY `name` (`name`);

--
-- Indexes for table `movies`
--
ALTER TABLE `movies`
  ADD PRIMARY KEY (`movie_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `actors`
--
ALTER TABLE `actors`
  MODIFY `actor_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `catalog`
--
ALTER TABLE `catalog`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `directors`
--
ALTER TABLE `directors`
  MODIFY `director_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `genres`
--
ALTER TABLE `genres`
  MODIFY `genre_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `movies`
--
ALTER TABLE `movies`
  MODIFY `movie_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
