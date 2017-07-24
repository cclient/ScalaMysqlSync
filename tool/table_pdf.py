# -*- coding: utf-8 -*-
word = '''
CREATE TABLE `word` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `engine` char(10) NOT NULL,
  `source_id` char(13) NOT NULL,
  `title` varchar(200) NOT NULL,
  `url` varchar(200) NOT NULL,
  `desc` varchar(500) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `source_id_UNIQUE` (`source_id`)
) ENGINE=InnoDB AUTO_INCREMENT=290 DEFAULT CHARSET=utf8mb4;
'''


excel = '''
CREATE TABLE `excel` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `engine` char(10) NOT NULL,
  `source_id` char(13) NOT NULL,
  `title` varchar(200) NOT NULL,
  `url` varchar(200) NOT NULL,
  `desc` varchar(500) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `source_id_UNIQUE` (`source_id`)
) ENGINE=InnoDB AUTO_INCREMENT=290 DEFAULT CHARSET=utf8mb4;
'''

# 偏移增量
offset_tables = [word]
# 全表比对
once_tables = [excel]
tables = [
    {"desc": word, "type": "offset"},
    {"desc": excel, "type": "once"}
]