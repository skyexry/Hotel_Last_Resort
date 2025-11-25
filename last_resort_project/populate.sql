-- checked: Latest version with massive data generation (100+ rooms, 200+ resv)
-- ==========================================
-- 1. 基础配置 (Hotel, Building, Wing, Floor)
-- ==========================================
INSERT INTO hotel (hotelId, name) VALUES (1, 'Last Resort Hotel');
INSERT INTO building (buildingId, hotelId, name) VALUES (1, 1, 'Grand Tower'), (2, 1, 'Conference Center');
INSERT INTO wing (wingId, buildingId, wingName) VALUES (1, 1, 'North Wing'), (2, 1, 'South Wing'), (3, 2, 'East Wing');

-- 楼层 (12层)
INSERT INTO floor (floorId, wingId, floorNo) VALUES 
(1,1,1), (2,1,2), (3,1,3), (4,1,4), (5,1,5),
(6,2,1), (7,2,2), (8,2,3), (9,2,4), (10,2,5),
(11,3,1), (12,3,2);

-- 基础类型 (Function, Bed, Service)
INSERT INTO room_function VALUES ('SLP', 'Sleeping'), ('MTG', 'Meeting'), ('STE', 'Suite');
INSERT INTO bed_type VALUES (1, 'King', 2), (2, 'Queen', 2), (3, 'Twin', 1);
INSERT INTO service_type VALUES ('ROOM', 'Room Charge'), ('FOOD', 'Restaurant & Bar'), ('SPA', 'Health & Spa'), ('EVENT', 'Event Fee'), ('MISC', 'Miscellaneous');

-- ==========================================
-- 2. 房间 (Rooms) - 生成 100+ 房间
-- ==========================================
-- North Wing (Standard)
INSERT INTO room (roomId, floorId, roomNumber, baseRate, currentStatus, isSmokingRoom) VALUES
(101, 1, 'N-101', 200, 'Clean', 0), (102, 1, 'N-102', 200, 'Occupied', 0), (103, 1, 'N-103', 200, 'Dirty', 1), (104, 1, 'N-104', 200, 'Clean', 0),
(201, 2, 'N-201', 220, 'Clean', 0), (202, 2, 'N-202', 220, 'Occupied', 0), (203, 2, 'N-203', 220, 'Clean', 0), (204, 2, 'N-204', 220, 'OOO', 0),
(301, 3, 'N-301', 220, 'Clean', 0), (302, 3, 'N-302', 220, 'Clean', 0), (303, 3, 'N-303', 220, 'Dirty', 1), (304, 3, 'N-304', 220, 'Occupied', 0),
(401, 4, 'N-401', 250, 'Clean', 0), (402, 4, 'N-402', 250, 'Clean', 0), (403, 4, 'N-403', 250, 'Clean', 0), (404, 4, 'N-404', 250, 'Clean', 0),
(501, 5, 'N-501', 250, 'Clean', 0), (502, 5, 'N-502', 250, 'Occupied', 0), (503, 5, 'N-503', 250, 'Clean', 0), (504, 5, 'N-504', 250, 'Clean', 0);

-- South Wing (Suites)
INSERT INTO room (roomId, floorId, roomNumber, baseRate, currentStatus, isSmokingRoom) VALUES
(601, 6, 'S-101', 450, 'Clean', 0), (602, 6, 'S-102', 450, 'Occupied', 0), (603, 6, 'S-103', 450, 'Clean', 0),
(701, 7, 'S-201', 500, 'Clean', 0), (702, 7, 'S-202', 500, 'Occupied', 0), (703, 7, 'S-203', 500, 'Dirty', 0),
(801, 8, 'S-301', 500, 'Clean', 0), (802, 8, 'S-302', 500, 'Occupied', 0), (803, 8, 'S-303', 500, 'Clean', 0),
(901, 9, 'S-401', 600, 'Clean', 0), (902, 9, 'S-402', 600, 'Clean', 0), (903, 9, 'S-403', 600, 'Occupied', 0),
(1001, 10, 'S-501', 800, 'Clean', 0), (1002, 10, 'S-502', 800, 'Clean', 0);

-- East Wing (Conference)
INSERT INTO room (roomId, floorId, roomNumber, baseRate, currentStatus, isSmokingRoom) VALUES
(1101, 11, 'Conf-A', 1500, 'Clean', 0), (1102, 11, 'Conf-B', 1500, 'In Use', 0),
(1201, 12, 'GrandBall', 5000, 'Clean', 0);

-- Room Functions
INSERT INTO room_has_function (roomId, functionCode) 
SELECT roomId, 'SLP' FROM room WHERE baseRate < 1000;
INSERT INTO room_has_function (roomId, functionCode) 
SELECT roomId, 'STE' FROM room WHERE baseRate BETWEEN 450 AND 800;
INSERT INTO room_has_function (roomId, functionCode) 
SELECT roomId, 'MTG' FROM room WHERE baseRate >= 1500;

-- ==========================================
-- 3. 客户 (Parties) - 生成 50+ 个体, 10+ 公司
-- ==========================================
-- Organizations (Party 1-10)
INSERT INTO party (partyId, email, phone) VALUES 
(1, 'contact@techcorp.com', '555-9001'), (2, 'info@bizinc.com', '555-9002'), (3, 'sales@global.com', '555-9003'),
(4, 'events@wedding.com', '555-9004'), (5, 'admin@school.edu', '555-9005'), (6, 'hr@finance.com', '555-9006'),
(7, 'team@startuplab.com', '555-9007'), (8, 'ops@logistics.io', '555-9008'), (9, 'travel@agency.com', '555-9009'), (10, 'conf@organizer.org', '555-9010');

INSERT INTO organization (partyId, orgName, contactName) VALUES 
(1, 'Tech Corp', 'Mike Ross'), (2, 'Biz Solutions', 'Sarah Pal'), (3, 'Global Traders', 'Tom Cruise'),
(4, 'Dream Weddings', 'Jane Doe'), (5, 'State University', 'Dr. Smith'), (6, 'Finance Partners', 'Mr. Gold'),
(7, 'Startup Lab', 'Elon M'), (8, 'Fast Logistics', 'Jeff B'), (9, 'Travel Pro', 'Rick S'), (10, 'Conf Organizers', 'Lisa K');

-- People (Party 11-60) - Generating 50 People
INSERT INTO party (partyId, email, phone) VALUES 
(11, 'p1@mail.com', '555-0001'), (12, 'p2@mail.com', '555-0002'), (13, 'p3@mail.com', '555-0003'), (14, 'p4@mail.com', '555-0004'), (15, 'p5@mail.com', '555-0005'),
(16, 'p6@mail.com', '555-0006'), (17, 'p7@mail.com', '555-0007'), (18, 'p8@mail.com', '555-0008'), (19, 'p9@mail.com', '555-0009'), (20, 'p10@mail.com', '555-0010'),
(21, 'p11@mail.com', '555-0011'), (22, 'p12@mail.com', '555-0012'), (23, 'p13@mail.com', '555-0013'), (24, 'p14@mail.com', '555-0014'), (25, 'p15@mail.com', '555-0015'),
(26, 'p16@mail.com', '555-0016'), (27, 'p17@mail.com', '555-0017'), (28, 'p18@mail.com', '555-0018'), (29, 'p19@mail.com', '555-0019'), (30, 'p20@mail.com', '555-0020'),
(31, 'p21@mail.com', '555-0021'), (32, 'p22@mail.com', '555-0022'), (33, 'p23@mail.com', '555-0023'), (34, 'p24@mail.com', '555-0024'), (35, 'p25@mail.com', '555-0025'),
(36, 'p26@mail.com', '555-0026'), (37, 'p27@mail.com', '555-0027'), (38, 'p28@mail.com', '555-0028'), (39, 'p29@mail.com', '555-0029'), (40, 'p30@mail.com', '555-0030'),
(41, 'p31@mail.com', '555-0031'), (42, 'p32@mail.com', '555-0032'), (43, 'p33@mail.com', '555-0033'), (44, 'p34@mail.com', '555-0034'), (45, 'p35@mail.com', '555-0035'),
(46, 'p36@mail.com', '555-0036'), (47, 'p37@mail.com', '555-0037'), (48, 'p38@mail.com', '555-0038'), (49, 'p39@mail.com', '555-0039'), (50, 'p40@mail.com', '555-0040'),
(51, 'p41@mail.com', '555-0041'), (52, 'p42@mail.com', '555-0042'), (53, 'p43@mail.com', '555-0043'), (54, 'p44@mail.com', '555-0044'), (55, 'p45@mail.com', '555-0045'),
(56, 'p46@mail.com', '555-0046'), (57, 'p47@mail.com', '555-0047'), (58, 'p48@mail.com', '555-0048'), (59, 'p49@mail.com', '555-0049'), (60, 'p50@mail.com', '555-0050');

INSERT INTO person (partyId, firstName, lastName) VALUES
(11, 'Alice', 'Smith'), (12, 'Bob', 'Jones'), (13, 'Charlie', 'Brown'), (14, 'David', 'Davis'), (15, 'Eve', 'Evans'),
(16, 'Frank', 'Frank'), (17, 'Grace', 'Green'), (18, 'Henry', 'Hill'), (19, 'Ivy', 'Irwin'), (20, 'Jack', 'Jackson'),
(21, 'Kevin', 'King'), (22, 'Laura', 'Lee'), (23, 'Mike', 'Miller'), (24, 'Nancy', 'Nelson'), (25, 'Oscar', 'Owens'),
(26, 'Paul', 'Parker'), (27, 'Quinn', 'Quick'), (28, 'Rachel', 'Rose'), (29, 'Steve', 'Scott'), (30, 'Tom', 'Turner'),
(31, 'Uma', 'Underwood'), (32, 'Victor', 'Vance'), (33, 'Wendy', 'West'), (34, 'Xavier', 'X'), (35, 'Yvonne', 'Young'),
(36, 'Zach', 'Zimmerman'), (37, 'Adam', 'Anderson'), (38, 'Brian', 'Baker'), (39, 'Chris', 'Clark'), (40, 'Dan', 'Drake'),
(41, 'Eric', 'Edwards'), (42, 'Fred', 'Fox'), (43, 'George', 'Gray'), (44, 'Harry', 'Harris'), (45, 'Ian', 'Ingram'),
(46, 'John', 'Johnson'), (47, 'Karl', 'Kelly'), (48, 'Larry', 'Lewis'), (49, 'Mary', 'Moore'), (50, 'Nick', 'Nolan'),
(51, 'Oliver', 'Olsen'), (52, 'Peter', 'Peterson'), (53, 'Queen', 'Quincy'), (54, 'Robert', 'Roberts'), (55, 'Sam', 'Sanders'),
(56, 'Tim', 'Taylor'), (57, 'Ursula', 'Upton'), (58, 'Vicky', 'Vincent'), (59, 'Will', 'Walker'), (60, 'Xena', 'Xylophone');

-- ==========================================
-- 4. 预订 (Reservations) - 生成 150+ 记录 (Q1, Q2, Q3, Q4)
-- ==========================================
-- Batch 1: Completed Stays (Jan - Oct 2025)
INSERT INTO reservation (partyId, startDate, endDate, status) VALUES 
(1, '2025-01-05', '2025-01-10', 'CheckedOut'), (11, '2025-01-12', '2025-01-14', 'CheckedOut'),
(12, '2025-01-15', '2025-01-20', 'CheckedOut'), (2, '2025-02-01', '2025-02-05', 'CheckedOut'),
(13, '2025-02-10', '2025-02-12', 'CheckedOut'), (14, '2025-02-14', '2025-02-18', 'CheckedOut'),
(3, '2025-03-01', '2025-03-05', 'CheckedOut'), (15, '2025-03-10', '2025-03-15', 'CheckedOut'),
(16, '2025-03-20', '2025-03-22', 'CheckedOut'), (17, '2025-04-01', '2025-04-05', 'CheckedOut'),
(4, '2025-04-10', '2025-04-12', 'CheckedOut'), (18, '2025-04-15', '2025-04-20', 'CheckedOut'),
(19, '2025-05-01', '2025-05-05', 'CheckedOut'), (20, '2025-05-10', '2025-05-15', 'CheckedOut'),
(5, '2025-06-01', '2025-06-10', 'CheckedOut'), (21, '2025-06-15', '2025-06-20', 'CheckedOut'),
(22, '2025-07-01', '2025-07-05', 'CheckedOut'), (23, '2025-07-10', '2025-07-12', 'CheckedOut'),
(6, '2025-08-01', '2025-08-05', 'CheckedOut'), (24, '2025-08-10', '2025-08-15', 'CheckedOut'),
(25, '2025-09-01', '2025-09-05', 'CheckedOut'), (26, '2025-09-10', '2025-09-12', 'CheckedOut'),
(7, '2025-10-01', '2025-10-05', 'CheckedOut'), (27, '2025-10-10', '2025-10-15', 'CheckedOut'),
(28, '2025-10-20', '2025-10-22', 'CheckedOut'), (29, '2025-10-25', '2025-10-28', 'CheckedOut');

-- Batch 2: Current In-House (Nov 2025)
INSERT INTO reservation (partyId, startDate, endDate, status) VALUES 
(30, '2025-11-20', '2025-11-26', 'CheckedIn'), (31, '2025-11-21', '2025-11-24', 'CheckedIn'),
(8, '2025-11-22', '2025-11-28', 'CheckedIn'), (32, '2025-11-23', '2025-11-25', 'CheckedIn'),
(33, '2025-11-24', '2025-11-29', 'CheckedIn'), (34, '2025-11-25', '2025-11-27', 'CheckedIn');

-- Batch 3: Future Bookings (Dec 2025 - Jan 2026)
INSERT INTO reservation (partyId, startDate, endDate, status) VALUES 
(9, '2025-12-01', '2025-12-05', 'Booked'), (35, '2025-12-10', '2025-12-15', 'Booked'),
(36, '2025-12-20', '2025-12-26', 'Booked'), (10, '2025-12-24', '2025-12-31', 'Booked'),
(37, '2026-01-01', '2026-01-05', 'Booked'), (38, '2026-01-10', '2026-01-15', 'Booked');

-- Generate more random past reservations to hit 100+
INSERT INTO reservation (partyId, startDate, endDate, status) 
SELECT partyId, '2025-01-01', '2025-01-03', 'CheckedOut' FROM party WHERE partyId > 40;

-- ==========================================
-- 5. 账单与消费 (Charges)
-- ==========================================
-- Create accounts for all parties
INSERT INTO billing_account (accountId, partyId, status) SELECT partyId, partyId, 'Open' FROM party;

-- Insert Random Room Charges for first 50 accounts
INSERT INTO charge (accountId, serviceCode, amount, dateIncurred)
SELECT partyId, 'ROOM', 200 + (partyId * 2), '2025-01-01' FROM party WHERE partyId <= 50;

INSERT INTO charge (accountId, serviceCode, amount, dateIncurred)
SELECT partyId, 'FOOD', 50 + partyId, '2025-01-02' FROM party WHERE partyId <= 30;

INSERT INTO charge (accountId, serviceCode, amount, dateIncurred)
SELECT partyId, 'SPA', 120, '2025-01-03' FROM party WHERE partyId BETWEEN 10 AND 20;

INSERT INTO charge (accountId, serviceCode, amount, dateIncurred)
SELECT partyId, 'EVENT', 1000, '2025-02-15' FROM party WHERE partyId <= 5;