package main.tables
import java.io.File
import java.sql.Date
import java.util.Properties
import com.typesafe.config.ConfigFactory
import slick.jdbc.MySQLProfile.api._

/**
  * Created by cclient on 7/3/17.
  */

object Conf {
//  val parsedConfig = ConfigFactory.parseFile(new File("src/main/application.conf"))
//  val conf = ConfigFactory.load(parsedConfig)
//  val ORORIGIN_DBIGIN_DB = Database.forConfig("mysqlorginal", config = conf)
  val ORIGIN_DB = Database.forURL("jdbc:mysql://localhost:3306/geekbang?characterEncoding=UTF-8&charset=utf8mb4", user = "root", password = "admaster", driver = "com.mysql.jdbc.Driver")
  val DEST_DB = Database.forURL("jdbc:mysql://localhost:3306/zhihu?characterEncoding=UTF-8&charset=utf8mb4", user = "root", password = "admaster", driver = "com.mysql.jdbc.Driver")
  val PAGE_SIZE = 2
  val DEFAULT_DATE = new Date(2016, 1, 1)
}
