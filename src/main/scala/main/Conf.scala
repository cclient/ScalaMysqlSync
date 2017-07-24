package main

import java.sql.Date

import slick.jdbc.MySQLProfile.api._

/**
  * Created by cclient on 7/3/17.
  */

object Conf {
//  val parsedConfig = ConfigFactory.parseFile(new File("src/main/application.conf"))
//  val conf = ConfigFactory.load(parsedConfig)
//  val ORORIGIN_DBIGIN_DB = Database.forConfig("mysqlorginal", config = conf)
  val ORIGIN_DB = Database.forURL("jdbc:mysql://localhost:3307/csdn?characterEncoding=UTF-8&charset=utf8mb4", user = "root", password = "passwd", driver = "com.mysql.jdbc.Driver",executor = AsyncExecutor("orgindb", numThreads=2, queueSize=1000))
  val DEST_DB = Database.forURL("jdbc:mysql://localhost:3306/geekbang?characterEncoding=UTF-8&charset=utf8mb4", user = "root", password = "passwd", driver = "com.mysql.jdbc.Driver")
  val PAGE_SIZE = 200
  val DEFAULT_DATE = new Date(2016, 1, 1)
}
