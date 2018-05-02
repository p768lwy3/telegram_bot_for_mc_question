CREATE TABLE IF NOT EXISTS HKDSEMATH (
	Qid int(6) NOT NULL,
	Year int(4),
	Qno int(2),
	Ans varchar(1),
	Qpath varchar(255),
	PRIMARY KEY(Qid)
);

CREATE TABLE IF NOT EXISTS TELEGRAM (
	Userid int(24) NOT NULL,
	Username varchar(255) NOT NULL,
	PRIMARY KEY(Userid)
);

CREATE TABLE IF NOT EXISTS QUERECORD (
	ID int(12) NOT NULL auto_increment,
	QDate DATE NOT NULL,
	Qid int(6) NOT NULL,
	Userid int(24) NOT NULL,
	PRIMARY KEY(ID)
);
	

CREATE TABLE IF NOT EXISTS ANSRECORD (
	ID int(12) NOT NULL auto_increment,
	Qid int(12) NOT NULL,
	ADate DATE NOT NULL,
	Userid int(24) NOT NULL,
	Reply varchar(1) NOT NULL,
	Correct int(1),
	PRIMARY KEY(ID),
	FOREIGN KEY(Qid) REFERENCES QUERECORD(ID)
);
	

INSERT INTO HKDSEMATH (Qid, Year, Qno, Ans, Qpath)
VALUES 
(201701, 2017, 1, 'A', './data/2017/1.png'),
(201702, 2017, 2, 'D', './data/2017/2.png'),
(201703, 2017, 3, 'A', './data/2017/3.png'),
(201704, 2017, 4, 'D', './data/2017/4.png'),
(201705, 2017, 5, 'D', './data/2017/5.png');
