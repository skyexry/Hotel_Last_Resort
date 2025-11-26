-- checked: Schema verified for 3NF and completeness
-- 1. 基础架构表
CREATE TABLE hotel (
    hotelId INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE building (
    buildingId INTEGER PRIMARY KEY,
    hotelId INTEGER,
    name TEXT,
    FOREIGN KEY(hotelId) REFERENCES hotel(hotelId)
);

CREATE TABLE wing (
    wingId INTEGER PRIMARY KEY,
    buildingId INTEGER,
    wingName TEXT,
    FOREIGN KEY(buildingId) REFERENCES building(buildingId)
);

CREATE TABLE floor (
    floorId INTEGER PRIMARY KEY,
    wingId INTEGER,
    floorNo INTEGER,
    FOREIGN KEY(wingId) REFERENCES wing(wingId)
);

-- 2. 房间与属性
CREATE TABLE room_function (
    functionCode TEXT PRIMARY KEY, -- SLP, MTG, STE
    name TEXT
);

CREATE TABLE bed_type (
    bedTypeId INTEGER PRIMARY KEY,
    name TEXT, -- King, Queen, Double
    capacity INTEGER
);

CREATE TABLE room (
    roomId INTEGER PRIMARY KEY,
    floorId INTEGER,
    roomNumber TEXT,
    baseRate REAL,
    currentStatus TEXT, -- Clean, Dirty, Occupied, OOO
    isSmokingRoom BOOLEAN,
    FOREIGN KEY(floorId) REFERENCES floor(floorId)
);

CREATE TABLE room_fixture (
    fixtureId INTEGER PRIMARY KEY,
    name TEXT
);

CREATE TABLE room_has_fixture (
    roomId INTEGER,
    fixtureId INTEGER,
    PRIMARY KEY (roomId, fixtureId),
    FOREIGN KEY(roomId) REFERENCES room(roomId),
    FOREIGN KEY(fixtureId) REFERENCES room_fixture(fixtureId)
);

CREATE TABLE room_has_function (
    roomId INTEGER,
    functionCode TEXT,
    PRIMARY KEY (roomId, functionCode),
    FOREIGN KEY(roomId) REFERENCES room(roomId),
    FOREIGN KEY(functionCode) REFERENCES room_function(functionCode)
);

CREATE TABLE room_has_bed (
    roomId INTEGER,
    bedTypeId INTEGER,
    count INTEGER,
    PRIMARY KEY (roomId, bedTypeId),
    FOREIGN KEY(roomId) REFERENCES room(roomId),
    FOREIGN KEY(bedTypeId) REFERENCES bed_type(bedTypeId)
);

-- 连通房
CREATE TABLE room_adjacency (
    roomId1 INTEGER,
    roomId2 INTEGER,
    connectionType TEXT, 
    PRIMARY KEY (roomId1, roomId2),
    FOREIGN KEY(roomId1) REFERENCES room(roomId),
    FOREIGN KEY(roomId2) REFERENCES room(roomId)
);

-- 维修工单
CREATE TABLE maintenance_ticket (
    ticketId INTEGER PRIMARY KEY,
    roomId INTEGER,
    issueDescription TEXT,
    status TEXT,
    dateCreated DATE,
    dateResolved DATE,
    FOREIGN KEY(roomId) REFERENCES room(roomId)
);

-- 3. 客户与Party
CREATE TABLE party (
    partyId INTEGER PRIMARY KEY,
    email TEXT,
    phone TEXT
);

CREATE TABLE person (
    partyId INTEGER PRIMARY KEY,
    firstName TEXT,
    lastName TEXT,
    FOREIGN KEY(partyId) REFERENCES party(partyId)
);

CREATE TABLE organization (
    partyId INTEGER PRIMARY KEY,
    orgName TEXT,
    contactName TEXT,
    FOREIGN KEY(partyId) REFERENCES party(partyId)
);

-- 4. 预订与入住
CREATE TABLE reservation (
    resvId INTEGER PRIMARY KEY,
    partyId INTEGER, 
    dateCreated DATETIME DEFAULT CURRENT_TIMESTAMP,
    startDate DATE,
    endDate DATE,
    status TEXT, 
    FOREIGN KEY(partyId) REFERENCES party(partyId)
);

CREATE TABLE stay (
    stayId INTEGER PRIMARY KEY,
    resvId INTEGER,
    checkInTime DATETIME,
    checkOutTime DATETIME,
    FOREIGN KEY(resvId) REFERENCES reservation(resvId)
);

CREATE TABLE room_assignment (
    assignmentId INTEGER PRIMARY KEY,
    resvId INTEGER,
    roomId INTEGER,
    FOREIGN KEY(resvId) REFERENCES reservation(resvId),
    FOREIGN KEY(roomId) REFERENCES room(roomId)
);

-- 5. 账单与服务
CREATE TABLE billing_account (
    accountId INTEGER PRIMARY KEY,
    partyId INTEGER,
    status TEXT,
    FOREIGN KEY(partyId) REFERENCES party(partyId)
);

CREATE TABLE service_type (
    serviceCode TEXT PRIMARY KEY,
    description TEXT
);

CREATE TABLE event (
    eventId INTEGER PRIMARY KEY,
    name TEXT,
    description TEXT,
    startDate DATETIME,
    endDate DATETIME,
    partyId INTEGER,
    roomId INTEGER,
    FOREIGN KEY(partyId) REFERENCES party(partyId),
    FOREIGN KEY(roomId) REFERENCES room(roomId)
);

CREATE TABLE charge (
    chargeId INTEGER PRIMARY KEY,
    accountId INTEGER,
    serviceCode TEXT,
    description TEXT,
    amount REAL,
    dateIncurred DATE,
    stayId INTEGER,
    eventId INTEGER,
    FOREIGN KEY(accountId) REFERENCES billing_account(accountId),
    FOREIGN KEY(serviceCode) REFERENCES service_type(serviceCode)
);