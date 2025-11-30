-- checked: Phone numbers updated to 10-digit format
-- ==========================================
-- 1. basic

WITH const AS (
    SELECT date('2025-11-29') AS report_date
)

INSERT INTO hotel (hotelId, name) VALUES (1, 'Last Resort Hotel');
INSERT INTO building (buildingId, hotelId, name) VALUES (1, 1, 'The Manor'), (2, 1, 'Ocean Pavilion');
INSERT INTO wing (wingId, buildingId, wingName) VALUES (1, 1, 'East Wing'), (2, 1, 'West Wing'), (3, 2, 'Villa Wing');

-- five floors
INSERT INTO floor (floorId, wingId, floorNo) VALUES 
(1,1,1), (2,1,2), (3,1,3), (4,1,4), (5,1,5), 
(6,2,1), (7,2,2), (8,2,3), (9,2,4), (10,2,5); 

-- room type
INSERT INTO room_function VALUES ('SLP', 'Guest Room'), ('MTG', 'Meeting Salon'), ('STE', 'Grand Suite');
INSERT INTO bed_type VALUES (1, 'King', 2), (2, 'Queen', 2), (3, 'Twin', 1), (4, 'California King', 2);
INSERT INTO service_type VALUES ('ROOM', 'Room Charge'), ('FOOD', 'Dining'), ('SPA', 'Wellness'), ('EVENT', 'Banquet'), ('MISC', 'Concierge');
INSERT INTO room_fixture (fixtureId, name) VALUES (1, 'OLED TV'), (2, 'Crystal Bar'), (3, 'Marble Bath'), (4, 'Terrace'), (5, 'Workstation');

-- 2. room (60+)
-- East Wing (Floors 1-5)
INSERT INTO room (roomId, floorId, roomNumber, baseRate, currentStatus, isSmokingRoom) VALUES
(101, 1, 'E-101', 350, 'Clean', 0), (102, 1, 'E-102', 350, 'Occupied', 0), (103, 1, 'E-103', 350, 'Clean', 0), (104, 1, 'E-104', 380, 'Dirty', 0), (105, 1, 'E-105', 380, 'Clean', 0), (106, 1, 'E-106', 400, 'Clean', 0),
(201, 2, 'E-201', 350, 'Occupied', 0), (202, 2, 'E-202', 350, 'Clean', 0), (203, 2, 'E-203', 350, 'Clean', 0), (204, 2, 'E-204', 380, 'Occupied', 0), (205, 2, 'E-205', 380, 'Clean', 0), (206, 2, 'E-206', 400, 'Occupied', 0),
(301, 3, 'E-301', 450, 'Clean', 0), (302, 3, 'E-302', 450, 'Clean', 0), (303, 3, 'E-303', 450, 'Dirty', 0), (304, 3, 'E-304', 480, 'Clean', 0), (305, 3, 'E-305', 480, 'Clean', 0), (306, 3, 'E-306', 500, 'Clean', 0),
(401, 4, 'E-401', 550, 'Clean', 0), (402, 4, 'E-402', 550, 'Occupied', 0), (403, 4, 'E-403', 550, 'Clean', 0), (404, 4, 'E-404', 580, 'Clean', 0), (405, 4, 'E-405', 580, 'Clean', 0), (406, 4, 'E-406', 600, 'Clean', 0),
(501, 5, 'E-501', 800, 'Clean', 0), (502, 5, 'E-502', 800, 'Occupied', 0), (503, 5, 'E-503', 800, 'Dirty', 0), (504, 5, 'E-504', 850, 'Clean', 0), (505, 5, 'E-505', 850, 'Occupied', 0), (506, 5, 'E-506', 1000, 'Clean', 0);

-- West Wing (Floors 1-5)
INSERT INTO room (roomId, floorId, roomNumber, baseRate, currentStatus, isSmokingRoom) VALUES
(601, 6, 'W-101', 350, 'Clean', 0), (602, 6, 'W-102', 350, 'Clean', 0), (603, 6, 'W-103', 350, 'Occupied', 0), (604, 6, 'W-104', 350, 'Clean', 0), (605, 6, 'W-105', 380, 'Dirty', 0), (606, 6, 'W-106', 400, 'Clean', 0),
(701, 7, 'W-201', 350, 'Clean', 0), (702, 7, 'W-202', 350, 'Clean', 0), (703, 7, 'W-203', 350, 'Clean', 0), (704, 7, 'W-204', 380, 'Occupied', 0), (705, 7, 'W-205', 380, 'Clean', 0), (706, 7, 'W-206', 400, 'Occupied', 0),
(801, 8, 'W-301', 450, 'Occupied', 0), (802, 8, 'W-302', 450, 'Clean', 0), (803, 8, 'W-303', 450, 'Clean', 0), (804, 8, 'W-304', 480, 'Clean', 0), (805, 8, 'W-305', 480, 'Clean', 0), (806, 8, 'W-306', 500, 'Clean', 0),
(901, 9, 'W-401', 550, 'Clean', 0), (902, 9, 'W-402', 550, 'Clean', 0), (903, 9, 'W-403', 550, 'Occupied', 0), (904, 9, 'W-404', 580, 'Clean', 0), (905, 9, 'W-405', 580, 'Clean', 0), (906, 9, 'W-406', 600, 'Clean', 0),
(1001, 10, 'W-501', 1200, 'Clean', 0), (1002, 10, 'W-502', 1200, 'Occupied', 0), (1003, 10, 'W-503', 1200, 'Clean', 0), (1004, 10, 'W-504', 1500, 'Dirty', 0), (1005, 10, 'W-505', 1500, 'Clean', 0), (1006, 10, 'W-506', 2000, 'Clean', 0);

-- Meeting Rooms
INSERT INTO room (roomId, floorId, roomNumber, baseRate, currentStatus, isSmokingRoom) VALUES
(2001, 1, 'Conf-A', 2500, 'Clean', 0), (2002, 1, 'Conf-B', 2500, 'In Use', 0), (2003, 1, 'GrandBall', 8000, 'Clean', 0);

-- Config
INSERT INTO room_has_function (roomId, functionCode) SELECT roomId, 'SLP' FROM room WHERE baseRate < 1000;
INSERT INTO room_has_function (roomId, functionCode) SELECT roomId, 'STE' FROM room WHERE baseRate >= 1000 AND baseRate < 2500;
INSERT INTO room_has_function (roomId, functionCode) SELECT roomId, 'MTG' FROM room WHERE baseRate >= 2500;
INSERT INTO room_has_bed (roomId, bedTypeId, count) SELECT roomId, 1, 1 FROM room WHERE roomId < 2000; 
INSERT INTO room_has_fixture (roomId, fixtureId) SELECT roomId, 1 FROM room WHERE roomId < 2000;

-- 3.  (Parties) - Updated Phones
INSERT INTO party (partyId, email, phone) VALUES (1, 'contact@tesla.com', '212-555-0101'), (2, 'info@lvmh.com', '212-555-0102'), (3, 'events@vogue.com', '212-555-0103'), (4, 'admin@harvard.edu', '617-555-0104');
INSERT INTO organization (partyId, orgName, contactName) VALUES (1, 'Tesla Motors', 'Elon M'), (2, 'LVMH Group', 'Bernard A'), (3, 'Vogue Magazine', 'Anna W'), (4, 'Harvard University', 'Dean Smith');

INSERT INTO party (partyId, email, phone) VALUES 
(5, 'james.bond@mi6.uk', '007-007-0007'), (6, 'tony@stark.com', '212-555-2384'), (7, 'bruce@wayne.com', '212-555-7893'), (8, 'peter@parker.com', '212-555-2388'),
(9, 'clark@dailyplanet.com', '212-555-3853'), (10, 'diana@themyscira.com', '212-555-3784'), (11, 'natasha@shield.gov', '202-555-0111'), (12, 'steve@shield.gov', '202-555-0112'),
(13, 'wanda@avengers.com', '212-555-0113'), (14, 'vision@avengers.com', '212-555-0114'), (15, 'thor@asgard.com', '212-555-0115'), (16, 'loki@asgard.com', '212-555-0116'),
(17, 'stephen@strange.com', '212-555-0117'), (18, 'carol@marvel.com', '212-555-0118'), (19, 'tchalla@wakanda.gov', '212-555-0119'), (20, 'shuri@wakanda.gov', '212-555-0120'),
(21, 'scott@lang.com', '415-555-0121'), (22, 'hope@pym.com', '415-555-0122'), (23, 'peter@quill.com', '212-555-0123'), (24, 'gamora@guardians.com', '212-555-0124'),
(25, 'drax@guardians.com', '212-555-0125'), (26, 'rocket@guardians.com', '212-555-0126'), (27, 'groot@guardians.com', '212-555-0127'), (28, 'mantis@guardians.com', '212-555-0128'),
(29, 'nebula@guardians.com', '212-555-0129'), (30, 'thanos@titan.com', '212-555-0130'), (31, 'harry@potter.com', '020-555-0131'), (32, 'hermione@granger.com', '020-555-0132'),
(33, 'ron@weasley.com', '020-555-0133'), (34, 'albus@hogwarts.edu', '020-555-0134'), (35, 'severus@hogwarts.edu', '020-555-0135'), (36, 'draco@malfoy.com', '020-555-0136'),
(37, 'luna@lovegood.com', '020-555-0137'), (38, 'neville@longbottom.com', '020-555-0138'), (39, 'ginny@weasley.com', '020-555-0139'), (40, 'sirius@black.com', '020-555-0140'),
(41, 'remus@lupin.com', '020-555-0141'), (42, 'rubeus@hagrid.com', '020-555-0142'), (43, 'minerva@mcgonagall.com', '020-555-0143'), (44, 'tom@riddle.com', '020-555-0144'),
(45, 'frodo@baggins.com', '020-555-0145'), (46, 'sam@gamgee.com', '020-555-0146'), (47, 'gandalf@grey.com', '020-555-0147'), (48, 'aragorn@gondor.gov', '020-555-0148'),
(49, 'legolas@mirkwood.com', '020-555-0149'), (50, 'gimli@erebor.com', '020-555-0150'), (51, 'boromir@gondor.gov', '020-555-0151'), (52, 'faramir@gondor.gov', '020-555-0152'),
(53, 'arwen@rivendell.com', '020-555-0153'), (54, 'galadriel@lorien.com', '020-555-0154'), (55, 'elrond@rivendell.com', '020-555-0155'), (56, 'bilbo@baggins.com', '020-555-0156'),
(57, 'gollum@cave.com', '020-555-0157'), (58, 'sauron@mordor.gov', '020-555-0158'), (59, 'saruman@isengard.com', '020-555-0159'), (60, 'luke@skywalker.com', '212-555-0160'),
(61, 'leia@organa.gov', '212-555-0161'), (62, 'han@solo.com', '212-555-0162'), (63, 'chewbacca@wookie.com', '212-555-0163'), (64, 'obiwan@kenobi.com', '212-555-0164'),
(65, 'anakin@skywalker.com', '212-555-0165'), (66, 'yoda@jedi.com', '212-555-0166'), (67, 'mace@windu.com', '212-555-0167'), (68, 'padme@amidala.gov', '212-555-0168'),
(69, 'palpatine@empire.gov', '212-555-0169'), (70, 'maul@sith.com', '212-555-0170'), (71, 'dooku@sith.com', '212-555-0171'), (72, 'general@grievous.com', '212-555-0172'),
(73, 'boba@fett.com', '212-555-0173'), (74, 'din@djarin.com', '212-555-0174'), (75, 'grogu@jedi.com', '212-555-0175'), (76, 'ahsoka@tano.com', '212-555-0176'),
(77, 'rex@clone.com', '212-555-0177'), (78, 'cody@clone.com', '212-555-0178'), (79, 'wolffe@clone.com', '212-555-0179'), (80, 'gregor@clone.com', '212-555-0180'),
(81, 'echo@clone.com', '212-555-0181'), (82, 'tech@clone.com', '212-555-0182'), (83, 'wrecker@clone.com', '212-555-0183'), (84, 'hunter@clone.com', '212-555-0184'),
(85, 'crosshair@clone.com', '212-555-0185'), (86, 'omega@clone.com', '212-555-0186'), (87, 'hera@syndulla.com', '212-555-0187'), (88, 'kanan@jarrus.com', '212-555-0188'),
(89, 'ezra@bridger.com', '212-555-0189'), (90, 'sabine@wren.com', '212-555-0190'), (91, 'zeb@orrelios.com', '212-555-0191'), (92, 'chopper@droid.com', '212-555-0192'),
(93, 'grand@thrawn.com', '212-555-0193'), (94, 'jack@sparrow.com', '305-555-0194'), (95, 'will@turner.com', '305-555-0195'), (96, 'elizabeth@swann.com', '305-555-0196'),
(97, 'hector@barbossa.com', '305-555-0197'), (98, 'davy@jones.com', '305-555-0198'), (99, 'james@norrington.com', '305-555-0199'), (100, 'josh@gibbs.com', '305-555-0200');

INSERT INTO person (partyId, firstName, lastName) VALUES
(5, 'James', 'Bond'), (6, 'Tony', 'Stark'), (7, 'Bruce', 'Wayne'), (8, 'Peter', 'Parker'), (9, 'Clark', 'Kent'), (10, 'Diana', 'Prince'), (11, 'Natasha', 'Romanoff'), (12, 'Steve', 'Rogers'),
(13, 'Wanda', 'Maximoff'), (14, 'Vision', 'Android'), (15, 'Thor', 'Odinson'), (16, 'Loki', 'Laufeyson'),
(17, 'Stephen', 'Strange'), (18, 'Carol', 'Danvers'), (19, 'TChalla', 'Udaku'), (20, 'Shuri', 'Udaku'),
(21, 'Scott', 'Lang'), (22, 'Hope', 'VanDyne'), (23, 'Peter', 'Quill'), (24, 'Gamora', 'Zen'),
(25, 'Drax', 'Destroyer'), (26, 'Rocket', 'Raccoon'), (27, 'Groot', 'Tree'), (28, 'Mantis', 'Alien'),
(29, 'Nebula', 'Cyborg'), (30, 'Thanos', 'Titan'), (31, 'Harry', 'Potter'), (32, 'Hermione', 'Granger'),
(33, 'Ron', 'Weasley'), (34, 'Albus', 'Dumbledore'), (35, 'Severus', 'Snape'), (36, 'Draco', 'Malfoy'),
(37, 'Luna', 'Lovegood'), (38, 'Neville', 'Longbottom'), (39, 'Ginny', 'Weasley'), (40, 'Sirius', 'Black'),
(41, 'Remus', 'Lupin'), (42, 'Rubeus', 'Hagrid'), (43, 'Minerva', 'McGonagall'), (44, 'Tom', 'Riddle'),
(45, 'Frodo', 'Baggins'), (46, 'Samwise', 'Gamgee'), (47, 'Gandalf', 'Grey'), (48, 'Aragorn', 'Elessar'),
(49, 'Legolas', 'Greenleaf'), (50, 'Gimli', 'Gloin'), (51, 'Boromir', 'Denethor'), (52, 'Faramir', 'Denethor'),
(53, 'Arwen', 'Undomiel'), (54, 'Galadriel', 'Lady'), (55, 'Elrond', 'Halfelven'), (56, 'Bilbo', 'Baggins'),
(57, 'Gollum', 'Smeagol'), (58, 'Sauron', 'DarkLord'), (59, 'Saruman', 'White'), (60, 'Luke', 'Skywalker'),
(61, 'Leia', 'Organa'), (62, 'Han', 'Solo'), (63, 'Chewbacca', 'Wookie'), (64, 'ObiWan', 'Kenobi'),
(65, 'Anakin', 'Skywalker'), (66, 'Yoda', 'Master'), (67, 'Mace', 'Windu'), (68, 'Padme', 'Amidala'),
(69, 'Sheev', 'Palpatine'), (70, 'Darth', 'Maul'), (71, 'Count', 'Dooku'), (72, 'General', 'Grievous'),
(73, 'Boba', 'Fett'), (74, 'Din', 'Djarin'), (75, 'Grogu', 'Child'), (76, 'Ahsoka', 'Tano'),
(77, 'Rex', 'Captain'), (78, 'Cody', 'Commander'), (79, 'Wolffe', 'Commander'), (80, 'Gregor', 'Commando'),
(81, 'Echo', 'ARC'), (82, 'Tech', 'BadBatch'), (83, 'Wrecker', 'BadBatch'), (84, 'Hunter', 'BadBatch'),
(85, 'Crosshair', 'BadBatch'), (86, 'Omega', 'Clone'), (87, 'Hera', 'Syndulla'), (88, 'Kanan', 'Jarrus'),
(89, 'Ezra', 'Bridger'), (90, 'Sabine', 'Wren'), (91, 'Zeb', 'Orrelios'), (92, 'Chopper', 'C110P'),
(93, 'Grand', 'Thrawn'), (94, 'Jack', 'Sparrow'), (95, 'Will', 'Turner'), (96, 'Elizabeth', 'Swann'),
(97, 'Hector', 'Barbossa'), (98, 'Davy', 'Jones'), (99, 'James', 'Norrington'), (100, 'Joshamee', 'Gibbs');

-- 4. 预订 (Reservations) - 200+ Records
-- Past (100)
-- INSERT INTO reservation (partyId, startDate, endDate, status) 
-- SELECT partyId, '2025-08-01', '2025-01-09', 'CheckedOut' FROM party WHERE partyId BETWEEN 5 AND 55;
-- INSERT INTO reservation (partyId, startDate, endDate, status) 
-- SELECT partyId, '2025-09-10', '2025-09-15', 'CheckedOut' FROM party WHERE partyId BETWEEN 56 AND 100;

-- -- Current (50)
-- INSERT INTO reservation (partyId, startDate, endDate, status) 
-- SELECT partyId, '2025-11-20', '2025-11-28', 'CheckedIn' FROM party WHERE partyId BETWEEN 5 AND 30;

-- -- Future (50)
-- INSERT INTO reservation (partyId, startDate, endDate, status) 
-- SELECT partyId, '2025-12-24', '2025-12-30', 'Booked' FROM party WHERE partyId BETWEEN 31 AND 60;

-- 假设当前查看日期（Today's Date）是 '2025-11-25'
-- 目标：生成 200 条数据，partyId (1-75)， startDate (2025-09-01 到 2026-01-01)， stay_days (3-10)

-- 假设 reservation 表结构：
-- reservation(partyId INT, startDate DATETIME, endDate DATETIME, status NVARCHAR(20))

WITH seq AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1 FROM seq WHERE n < 200
)
INSERT INTO reservation (partyId, startDate, endDate, status)
SELECT
    -- 随机选择 partyId 1~75
    (ABS(CHECKSUM(NEWID())) % 75) + 1 AS partyId,

    -- 随机 startDate: 2025-09-01 到 2025-12-31
    DATEADD(
        day,
        ROUND(DATEDIFF(day, '2025-09-01', '2025-12-31') * RAND(CHECKSUM(NEWID())), 0),
        '2025-09-01'
    ) AS startDate,

    -- endDate = startDate + 随机停留天数 3~10
    DATEADD(
        day,
        (ABS(CHECKSUM(NEWID())) % 8) + 3,
        DATEADD(
            day,
            ROUND(DATEDIFF(day, '2025-09-01', '2025-12-31') * RAND(CHECKSUM(NEWID())), 0),
            '2025-09-01'
        )
    ) AS endDate,

    -- 状态判断
    CASE
        WHEN GETDATE() < DATEADD(
                day,
                ROUND(DATEDIFF(day, '2025-09-01', '2025-12-31') * RAND(CHECKSUM(NEWID())), 0),
                '2025-09-01'
             )
        THEN 'Booked'
        WHEN GETDATE() BETWEEN 
             DATEADD(
                day,
                ROUND(DATEDIFF(day, '2025-09-01', '2025-12-31') * RAND(CHECKSUM(NEWID())), 0),
                '2025-09-01'
             )
             AND 
             DATEADD(
                day,
                (ABS(CHECKSUM(NEWID())) % 8) + 3,
                DATEADD(
                    day,
                    ROUND(DATEDIFF(day, '2025-09-01', '2025-12-31') * RAND(CHECKSUM(NEWID())), 0),
                    '2025-09-01'
                )
             )
        THEN 'CheckedIn'
        ELSE 'CheckedOut'
    END AS status
FROM seq
OPTION (MAXRECURSION 0);


-- 5. Events & Billing
INSERT INTO event (eventId, name, description, startDate, endDate, partyId, roomId) VALUES
(1, 'Tesla Tech Day', 'AI & Robotics Showcase', '2025-12-01', '2025-12-01', 1, 2001),
(2, 'Vogue Gala', 'Fashion Week Opening', '2025-12-05', '2025-12-05', 3, 2003),
(3, 'Harvard Alumni', 'Networking Dinner', '2025-12-10', '2025-12-10', 4, 2001),
(4, 'Stark Expo', 'Clean Energy Summit', '2025-12-15', '2025-12-20', 6, 2002),
(5, 'Wayne Charity', 'Gotham Fundraiser', '2025-12-25', '2025-12-25', 7, 2003),
(6, 'LVMH Board', 'Annual Review', '2025-11-30', '2025-11-30', 2, 2001),
(7, 'Avengers Briefing', 'Strategic Planning', '2025-12-02', '2025-12-03', 6, 2002),
(8, 'Hogwarts Reunion', 'Magic & Mystery', '2025-12-24', '2025-12-26', 31, 2003),
(9, 'Jedi Council', 'Peace Talks', '2026-01-10', '2026-01-12', 66, 2002),
(10, 'Clone Force 99', 'Tactical Drill', '2025-11-28', '2025-11-29', 84, 2001);

-- Billing
INSERT INTO billing_account (accountId, partyId, status) SELECT partyId, partyId, 'Open' FROM party;
INSERT INTO charge (accountId, serviceCode, amount, dateIncurred)
SELECT
    b.accountId,
    'ROOM',
    r.baseRate * (julianday(res.endDate) - julianday(res.startDate)) AS amount,
    res.startDate AS dateIncurred
FROM reservation res
JOIN billing_account b ON b.partyId = res.partyId
JOIN room r ON r.roomId = ((res.partyId - 1) % (SELECT COUNT(*) FROM room)) + 1;
