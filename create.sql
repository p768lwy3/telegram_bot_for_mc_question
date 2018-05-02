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

INSERT INTO HKDSEMATH (Qid, Year, Qno, Ans, Qpath)
VALUES 
(201701, 2017, 1, 'A', './data/2017/1.png'),
(201702, 2017, 2, 'D', './data/2017/2.png'),
(201703, 2017, 3, 'A', './data/2017/3.png'),
(201704, 2017, 4, 'D', './data/2017/4.png'),
(201705, 2017, 5, 'D', './data/2017/5.png');
