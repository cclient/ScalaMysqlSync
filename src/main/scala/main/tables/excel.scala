
package main.tables

import java.sql.Blob
import java.sql.Date
import java.sql.Timestamp
import java.util.concurrent.TimeUnit

import akka.actor.Actor
import main.Conf._
import main.task.Sync
import main.Action._
import slick.jdbc.MySQLProfile.api._
import slick.lifted.TableQuery

import scala.concurrent.ExecutionContext.Implicits.global
import scala.concurrent.Future

case class Excel(id: Int,engine: String,source_id: String,title: String,url: String,desc: String)

class Excels(tag: Tag) extends Table[(Int,String,String,String,String,String)](tag, "excel") {
	 def id =  column[Int]("id")
	 def engine =  column[String]("engine")
	 def source_id =  column[String]("source_id")
	 def title =  column[String]("title")
	 def url =  column[String]("url")
	 def desc =  column[String]("desc")
	def * = (id,engine,source_id,title,url,desc)
}

class ExcelActor extends Actor {
  val tablename="excel"
  val is_just_insert=false
  //  implicit val executionContext: ExecutionContext = context.system.dispatchers.lookup("my-blocking-dispatcher")
  override def receive: Receive = {
      
    //最简单的办法是select id from dest.table,再 select * from orginal.table where id in 
    //对方要求的是只在他们表里作最基础的查询，索引join都不让
    //为了不在对方数据库里作sort,select in() 就在代码里diff
    case (ONCEALL_DIFF,records:List[Excel]) => {
          val excels = TableQuery[Excels]
          val action=DEST_DB.run(excels.result)
          action.onComplete(data=>{
            if (data.isSuccess){
              val destnowrecoreds=data.get.map(c =>Excel.tupled(c))
              println("records records",records.length)
              println("destnowrecoreds records",destnowrecoreds.length)
              //拿出源里有，但目的时目前没有的。
              val nohasrecords=records.filter(record=>{
                //目标里是否存在当前项
                !destnowrecoreds.exists(a=>{
                //todo 这里需要根据不同的表修改
                  (a.id==record.id)
                })
              })
              println("nohasrecords records",nohasrecords.length)
              self !(ONCEALL_INSERT,nohasrecords)
            }
          })
        }
    //  从这个id开始后移拿数不段循环直到拿全（数据量较小，内存可以承受）
    case (ONCEALL_GET,offset:Int,records:List[Excel]) => {
      println("sync by",offset)
      val excels = TableQuery[Excels]
      val action=ORIGIN_DB.run(excels.drop(offset).take(PAGE_SIZE).result)
      action.onComplete(data=>{
        println("sync get data",data.get.length)
        if (data.isSuccess){
          val excels=data.get.toList.map(a=>{
            Excel.tupled(a)
          })
          if (excels.length>0){
            val nrecords=records.:::(excels)
            Future {
              println(s"next page 1s start")
              TimeUnit.SECONDS.sleep(1)
              println(s"next page 1s finished")
              self !(ONCEALL_GET,nrecords.length,nrecords)
            }
          }else{
              self !(ONCEALL_DIFF,records)
          }
        }
      })
    }
    //  插入数据
    case (ONCEALL_INSERT,excels:List[Excel])=>{
      println("insert start",excels.length)
      val excel = TableQuery[Excels]
      excel.++=(excels.map(a=>{
        Excel.unapply(a).get
      }))
      val insertActions = DBIO.seq(
        excel.++=(excels.map(a=>{
          Excel.unapply(a).get
        }))
      )
      DEST_DB.run(insertActions).onComplete(data=>{
        println("insert data result",data)
        Future {
          println(s"Blocking future 12h start")
          TimeUnit.HOURS.sleep(12)
          println(s"Blocking future 12h finished")
          self !ONCEALL_TASK_START
        }
      })
    }
    //这个操作只适用于小表
    case ONCEALL_TASK_START=>{
      self !(ONCEALL_GET,0,List[Excel]())
    }
  }
}    
