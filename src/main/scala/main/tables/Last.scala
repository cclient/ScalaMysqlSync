package main.tables

import java.sql.Date

import akka.actor.Actor
import main.tables.Conf._
import slick.jdbc.MySQLProfile.api._
import slick.lifted.TableQuery

import scala.concurrent.ExecutionContext.Implicits.global

/**
  * Created by cclient on 7/3/17.
  */
case class Last(table_name: String, id: Int, pub_time: Date, spider_time: Date)

class Lasts(tag: Tag) extends Table[(String, Int, Date, Date)](tag, "last") {
  def * = (table_name, id, pub_time, spider_time)

  def table_name = column[String]("table_name")

  def id = column[Int]("id")

  def pub_time = column[Date]("pub_time")

  def spider_time = column[Date]("spider_time")
}

class LastActor extends Actor {
  override def receive: Receive = {
    //    case "getall" => {
    //      val lasts = TableQuery[Lasts]
    //      val action=ORIGIN_DB.run(lasts.result)
    //      action.onComplete(data=>{
    //        if (data.isSuccess){
    //          var articles=List[Last]()
    //          data.get.foreach(c=>{
    //            articles=articles.::(Last.tupled(c))
    //          })
    ////          Sync.dataActor !articles
    //        }
    //      })
    //    }
    //得到记录的最大id,如果失败，则直接读目标表
    case ("get", tablename: String) => {
      val send = sender()
      println(send.path)
      val lasts = TableQuery[Lasts]
      //      val q=lasts.filter(_.table_name==="answer").take(1).result
      val q = lasts.filter(_.table_name === tablename).result
      DEST_DB.run(q).onComplete(data => {
        println(sender().path)
        if (data.isSuccess && data.get.length > 0) {
          val last = Last.tupled(data.get.head)
          println("get lastid", last.id)
          send ! ("lastbydest", last.id)
        } else {
          println("don't get lastid")
          send ! ("lastbydest", 0)
        }
      })
    }

    case ("upsert", tablename: String, lastid: Int) => {
      val send = sender()
      val Last = TableQuery[Lasts]
      val updated = Last.insertOrUpdate((tablename, lastid, DEFAULT_DATE, DEFAULT_DATE))
      DEST_DB.run(updated).onComplete(data => {
        println(data)
        if (data.isSuccess) {
          send ! ("sync", lastid)
        } else {
          println("upsert last error")
          //          sender() !("sync",false)
        }
      })
    }

    //初始化，不必保持成功，后期每张表的任务upsert既可
    //    case "init"=>{
    //      val tables=List("article")
    //      val inserts=tables.map(tname=>{
    //        (tname,0, DEFAULT_DATE, DEFAULT_DATE)
    //      })
    //      val Last = TableQuery[Lasts]
    //      val insertActions = DBIO.seq(
    //        Last++=inserts
    //        //        Last.+=("answer",0, defaultDate, defaultDate),
    //        //        Last ++= Seq(
    //        //          ("question",0, defaultDate, defaultDate),
    //        //          ("answer",0, defaultDate, defaultDate)
    //        //        ),
    //        //        Last.map(c => (c.table_name, c.id, c.pub_time,c.spider_time)) += ("sub", 0, defaultDate, defaultDate)
    //      )
    //      val sql = Last.insertStatement
    //      println(sql)
    //      DEST_DB.run(insertActions).onComplete(data=>{
    //        println(data)
    //        if (data.isSuccess){
    //          sender() !("init_end",true)
    //        }else{
    //          sender() !("init_end",false)
    //        }
    //      })
    //    }

    case ("update", tablename: String, lastid: Int) => {
      val Last = TableQuery[Lasts]
      val q = for {c <- Last if c.table_name === tablename} yield c.id
      val updateAction = q.update(lastid)
      DEST_DB.run(updateAction).onComplete(data => {
        println(data)
        if (data.isSuccess) {
          sender() ! ("update_end", true)
        } else {
          sender() ! ("update_end", false)
        }
      })
    }
  }
}
