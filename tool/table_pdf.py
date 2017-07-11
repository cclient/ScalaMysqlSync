# -*- coding: utf-8 -*-

pdf = '''
CREATE TABLE `pdf` (
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

answer = '''
CREATE TABLE `answer` (
  `aid` int(10) unsigned NOT NULL,
  `bid` int(10) unsigned NOT NULL,
  `sbid` int(10) unsigned NOT NULL,
  `qid` int(10) unsigned NOT NULL,
  `ups` int(10) unsigned NOT NULL,
  `author` varchar(64) NOT NULL,
  `uid` varchar(16) NOT NULL,
  `nick` varchar(256) NOT NULL,
  `pub_time` timestamp NOT NULL DEFAULT '2000-01-01 00:00:00',
  `content` text NOT NULL,
  `good` tinyint(1) unsigned NOT NULL,
  `hot` tinyint(1) unsigned NOT NULL,
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `reply` tinyint(3) unsigned NOT NULL,
  `pic` tinyint(1) unsigned NOT NULL DEFAULT '0',
  `spider_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `index_spidertime` (`spider_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
'''

board = '''
CREATE TABLE `board` (
  `bid` int(10) unsigned NOT NULL,
  `name` varchar(64) NOT NULL,
  PRIMARY KEY (`bid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

'''

comment = '''
CREATE TABLE `comment` (
  `cid` int(10) unsigned NOT NULL,
  `aid` int(10) unsigned NOT NULL,
  `ups` int(10) unsigned NOT NULL,
  `uid` varchar(20) NOT NULL,
  `author` varchar(64) NOT NULL,
  `pub_date` date NOT NULL,
  `content` text NOT NULL,
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `spider_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY `id` (`id`),
  KEY `index_spidertime` (`spider_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

'''

question = '''
CREATE TABLE `question` (
  `qid` int(10) unsigned NOT NULL,
  `bid` int(10) unsigned NOT NULL,
  `sbid` int(10) unsigned NOT NULL,
  `uid` varchar(16) NOT NULL,
  `title` varchar(1024) NOT NULL,
  `content` text NOT NULL,
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `spider_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `index_spidertime` (`spider_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
'''

sub_board = '''
CREATE TABLE `sub_board` (
  `sbid` int(10) unsigned NOT NULL,
  `bid` int(10) unsigned NOT NULL,
  `name` varchar(64) NOT NULL,
  PRIMARY KEY (`sbid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
'''

topic_selection = '''
CREATE TABLE `topic_selection` (
  `uid` varchar(64) NOT NULL,
  `topic` varchar(64) NOT NULL,
  PRIMARY KEY (`uid`,`topic`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

'''

user = '''
CREATE TABLE `user` (
  `uid` varchar(64) NOT NULL,
  `name` varchar(64) NOT NULL,
  `nick` varchar(256) NOT NULL,
  `gender` tinyint(3) unsigned NOT NULL,
  `location` varchar(64) NOT NULL,
  `business` varchar(64) NOT NULL,
  `education` varchar(64) NOT NULL,
  `major` varchar(64) NOT NULL,
  `employment` varchar(64) NOT NULL,
  `position` varchar(64) NOT NULL,
  `ups` int(10) unsigned NOT NULL,
  `thanks` int(10) unsigned NOT NULL,
  `asks` int(10) unsigned NOT NULL,
  `answers` int(10) unsigned NOT NULL,
  `posts` int(10) unsigned NOT NULL,
  `collections` int(10) unsigned NOT NULL,
  PRIMARY KEY (`uid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

'''

last = '''
CREATE TABLE `last` (
  `table_name` char(20) NOT NULL,
  `id` bigint(20) DEFAULT NULL,
  `pub_time` datetime DEFAULT NULL,
  `spider_time` datetime DEFAULT NULL,
  PRIMARY KEY (`table_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

'''

test = '''
CREATE TABLE `otherbbs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `province` varchar(100) NOT NULL,
  `city` varchar(100) NOT NULL,
  `gender` varchar(45) NOT NULL,
  `bankuaiid` varchar(200) NOT NULL,
  `author` varchar(200) NOT NULL,
  `title` varchar(800) NOT NULL,
  `url` varchar(500) NOT NULL,
  `comment_num` int(11) NOT NULL DEFAULT '0',
  `floor` int(11) NOT NULL DEFAULT '0',
  `view_num` int(11) NOT NULL DEFAULT '0',
  `content` mediumblob NOT NULL,
  `time` datetime NOT NULL,
  `threadid` char(32) NOT NULL,
  `device` varchar(200) NOT NULL,
  `bankuainame` varchar(200) NOT NULL,
  `level` varchar(100) NOT NULL,
  `authorurl` varchar(500) NOT NULL,
  `site` varchar(100) NOT NULL,
  `domain` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `thread` (`threadid`,`author`,`time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

'''

# tables = [pdf,user, topic_selection, sub_board, question, comment, board, answer, last, test]
# tables = [answer, comment, question]
tables = [answer]
# tables = [topic_selection]
