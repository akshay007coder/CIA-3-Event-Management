CREATE DATABASE event_management_sql;

USE event_management_sql;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('attendee', 'organizer') NOT NULL
);

CREATE TABLE events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    location VARCHAR(255) NOT NULL,
    date DATE NOT NULL,
    time TIME NOT NULL,
    description TEXT NOT NULL,
    capacity INT NOT NULL,
    vip_tickets INT NOT NULL,
    general_tickets INT NOT NULL,
    vip_price DECIMAL(10, 2) NOT NULL,
    general_price DECIMAL(10, 2) NOT NULL,
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    event_id INT NOT NULL,
    vip_tickets_booked INT NOT NULL,
    general_tickets_booked INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (event_id) REFERENCES events(id)
);

CREATE TABLE registrations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    event_id INT NOT NULL,
    registration_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (event_id) REFERENCES events(id),
    UNIQUE (user_id, event_id)
);

CREATE TABLE refunds (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    booking_id INT NOT NULL,
    event_id INT NOT NULL,
    request_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (booking_id) REFERENCES bookings(id),
    FOREIGN KEY (event_id) REFERENCES events(id),
    UNIQUE (booking_id)
);

# added this column so that when organizer cancels an event, it is shown in the ui
ALTER TABLE events ADD COLUMN status VARCHAR(20) DEFAULT 'active';

# To add a new value ('participant') to the existing ENUM in the role column of the users table
ALTER TABLE users 
MODIFY role ENUM('attendee', 'organizer', 'participant') NOT NULL;

# to add a poster_path column to the events table to store the file path of the uploaded poster.
ALTER TABLE events ADD COLUMN poster_path VARCHAR(255) DEFAULT NULL;

SELECT * from users;
DESCRIBE users;
SELECT * from events;
DESCRIBE events;
SELECT * from bookings;
DESCRIBE bookings;
SELECT * from registrations;
DESCRIBE registrations;
SELECT * from refunds;
DESCRIBE refunds;


INSERT INTO users (name, email, password, role) VALUES
('Emma Wilson', 'emma.w@example.com', 'pass201', 'attendee'),
('Liam Parker', 'liam.p@example.com', 'pass202', 'organizer'),
('Olivia Reed', 'olivia.r@example.com', 'pass203', 'participant'),
('Noah Turner', 'noah.t@example.com', 'pass204', 'attendee'),
('Ava Brooks', 'ava.b@example.com', 'pass205', 'organizer'),
('Ethan Hill', 'ethan.h@example.com', 'pass206', 'participant'),
('Sophia Lee', 'sophia.l@example.com', 'pass207', 'attendee'),
('Mason Gray', 'mason.g@example.com', 'pass208', 'organizer'),
('Isabella Cox', 'isabella.c@example.com', 'pass209', 'participant'),
('James King', 'james.k@example.com', 'pass210', 'attendee'),
('Charlotte Adams', 'charlotte.a@example.com', 'pass211', 'organizer'),
('Benjamin Ward', 'benjamin.w@example.com', 'pass212', 'participant'),
('Amelia Scott', 'amelia.s@example.com', 'pass213', 'attendee'),
('Henry Green', 'henry.g@example.com', 'pass214', 'organizer'),
('Evelyn Hall', 'evelyn.h@example.com', 'pass215', 'participant'),
('Alexander Cook', 'alexander.c@example.com', 'pass216', 'attendee'),
('Harper Young', 'harper.y@example.com', 'pass217', 'organizer'),
('Daniel Moore', 'daniel.m@example.com', 'pass218', 'participant'),
('Mia Evans', 'mia.e@example.com', 'pass219', 'attendee'),
('Lucas Baker', 'lucas.b@example.com', 'pass220', 'organizer');

INSERT INTO events (title, location, date, time, description, capacity, vip_tickets, general_tickets, vip_price, general_price, user_id, status, poster_path) VALUES
('Tech Conference 2025', 'Mumbai', '2025-05-10', '10:00:00', 'Tech innovation summit', 600, 60, 250, 60.00, 25.00, 2, 'active', '/posters/tech_conf.jpg'),
('Jazz Festival', 'Delhi', '2025-06-20', '18:30:00', 'Music and jazz event', 800, 80, 300, 80.00, 35.00, 5, 'canceled', '/posters/jazz_fest.jpg'),
('Art Gallery', 'Bangalore', '2025-07-15', '11:00:00', 'Art exhibition showcase', 350, 35, 150, 45.00, 20.00, 8, 'active', '/posters/art_gallery.jpg'),
('Health Seminar', 'Chennai', '2025-08-12', '14:00:00', 'Health and wellness talk', 450, 45, 200, 30.00, 15.00, 11, 'canceled', '/posters/health_sem.jpg'),
('Food Expo', 'Kolkata', '2025-09-25', '12:00:00', 'Culinary exhibition', 700, 70, 300, 55.00, 22.00, 14, 'active', '/posters/food_expo.jpg'),
('Coding Bootcamp', 'Hyderabad', '2025-10-05', '09:30:00', 'Coding skills workshop', 250, 25, 150, 40.00, 18.00, 2, 'canceled', '/posters/coding_boot.jpg'),
('Dance Showcase', 'Pune', '2025-11-18', '17:00:00', 'Dance performance event', 550, 55, 200, 35.00, 15.00, 5, 'active', '/posters/dance_show.jpg'),
('Science Expo', 'Jaipur', '2025-12-10', '13:00:00', 'Science and tech fair', 400, 40, 180, 25.00, 12.00, 8, 'canceled', '/posters/science_expo.jpg'),
('Film Screening', 'Ahmedabad', '2026-01-15', '15:30:00', 'Independent film festival', 750, 75, 350, 50.00, 20.00, 11, 'active', '/posters/film_screen.jpg'),
('Book Fair', 'Surat', '2026-02-25', '16:00:00', 'Literary book event', 300, 30, 120, 30.00, 12.00, 14, 'canceled', '/posters/book_fair.jpg'),
('Tech Workshop', 'Mumbai', '2026-03-20', '11:00:00', 'Tech skills training', 500, 50, 200, 45.00, 18.00, 2, 'active', '/posters/tech_workshop.jpg'),
('Rock Concert', 'Delhi', '2026-04-15', '19:00:00', 'Rock music night', 600, 60, 250, 60.00, 25.00, 5, 'canceled', '/posters/rock_concert.jpg'),
('Craft Market', 'Bangalore', '2026-05-10', '10:30:00', 'Handmade crafts fair', 400, 40, 180, 35.00, 15.00, 8, 'active', '/posters/craft_market.jpg'),
('Yoga Session', 'Chennai', '2026-06-20', '08:30:00', 'Yoga and meditation', 200, 20, 100, 25.00, 10.00, 11, 'canceled', '/posters/yoga_session.jpg'),
('Game Tournament', 'Kolkata', '2026-07-15', '09:00:00', 'Gaming competition', 350, 35, 150, 40.00, 18.00, 14, 'active', '/posters/game_tournament.jpg'),
('Theater Festival', 'Hyderabad', '2026-08-12', '18:00:00', 'Drama and theater', 300, 30, 120, 30.00, 12.00, 2, 'canceled', '/posters/theater_fest.jpg'),
('Photo Contest', 'Pune', '2026-09-25', '14:30:00', 'Photography competition', 400, 40, 180, 35.00, 15.00, 5, 'active', '/posters/photo_contest.jpg'),
('Charity Gala', 'Jaipur', '2026-10-10', '07:30:00', 'Charity fundraising', 500, 50, 200, 25.00, 10.00, 8, 'canceled', '/posters/charity_gala.jpg'),
('Comedy Show', 'Ahmedabad', '2026-11-20', '20:00:00', 'Stand-up comedy night', 450, 45, 200, 40.00, 18.00, 11, 'active', '/posters/comedy_show.jpg'),
('Education Forum', 'Surat', '2026-12-15', '11:30:00', 'Educational seminar', 600, 60, 250, 45.00, 20.00, 14, 'canceled', '/posters/edu_forum.jpg');

INSERT INTO bookings (user_id, event_id, vip_tickets_booked, general_tickets_booked) VALUES
(1, 1, 1, 2),    -- Active
(4, 3, 0, 3),
(7, 5, 2, 1),
(10, 7, 0, 2),
(13, 9, 1, 1),
(1, 11, 2, 0),
(4, 13, 0, 3),
(7, 15, 1, 2),
(10, 17, 2, 1),
(13, 19, 0, 2),
(1, 2, 1, 1),    -- Canceled
(4, 4, 0, 2),
(7, 6, 2, 0),
(10, 8, 1, 1),
(13, 10, 0, 3),
(1, 12, 1, 2),
(4, 14, 2, 0),
(7, 16, 0, 1),
(10, 18, 1, 2),
(13, 20, 2, 1);

INSERT INTO registrations (user_id, event_id, registration_date) VALUES
(3, 1, '2025-04-10 09:00:00'),   -- Active
(6, 3, '2025-05-15 14:00:00'),
(9, 5, '2025-06-20 10:30:00'),
(12, 7, '2025-07-10 11:15:00'),
(15, 9, '2025-08-15 13:45:00'),
(3, 11, '2025-09-20 09:30:00'),
(6, 13, '2025-10-25 15:00:00'),
(9, 15, '2025-11-30 12:20:00'),
(12, 17, '2026-01-10 10:00:00'),
(15, 19, '2026-02-15 14:30:00'),
(3, 2, '2025-04-12 08:00:00'),   -- Canceled
(6, 4, '2025-05-18 13:00:00'),
(9, 6, '2025-06-22 11:45:00'),
(12, 8, '2025-07-12 10:30:00'),
(15, 10, '2025-08-17 12:15:00'),
(3, 12, '2025-09-22 09:15:00'),
(6, 14, '2025-10-27 14:00:00'),
(9, 16, '2025-12-02 11:10:00'),
(12, 18, '2026-01-12 09:45:00'),
(15, 20, '2026-02-17 13:00:00');

INSERT INTO refunds (user_id, booking_id, event_id, status) VALUES
(1, 11, 2, 'pending'),   -- Booking 11 (user 1, event 2)
(4, 12, 4, 'approved'),  -- Booking 12 (user 4, event 4)
(7, 13, 6, 'rejected'),  -- Booking 13 (user 7, event 6)
(10, 14, 8, 'pending'),  -- Booking 14 (user 10, event 8)
(13, 15, 10, 'approved'), -- Booking 15 (user 13, event 10)
(1, 16, 12, 'rejected'),  -- Booking 16 (user 1, event 12)
(4, 17, 14, 'pending'),  -- Booking 17 (user 4, event 14)
(7, 18, 16, 'approved'),  -- Booking 18 (user 7, event 16)
(10, 19, 18, 'rejected'), -- Booking 19 (user 10, event 18)
(13, 20, 20, 'pending');  -- Booking 20 (user 13, event 20)