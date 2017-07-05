package main.tables

import akka.actor.Actor
import main.tables.Conf._
import main.task.Sync
import slick.jdbc.MySQLProfile.api._
import slick.lifted.TableQuery

import scala.concurrent.ExecutionContext.Implicits.global
import scala.concurrent.Future

case class Pdf(id: Int, engine: String, source_id: String, title: String, url: String, desc: String)

class Pdfs(tag: Tag) extends Table[(Int, String, String, String, String, String)](tag, "pdf") {
  def * = (id, engine, source_id, title, url, desc)

  def id = column[Int]("id")

  def engine = column[String]("engine")

  def source_id = column[String]("source_id")

  def title = column[String]("title")

  def url = column[String]("url")

  def desc = column[String]("desc")
}

class PdfActor extends Actor {
  val tablename = "pdf"

  //  implicit val executionContext: ExecutionContext = context.system.dispatchers.lookup("my-blocking-dispatcher")
  override def receive: Receive = {
    //  从这个id开始后移拿数
    case ("sync", lastid: Int) => {
      println("sync start by", lastid)
      val pdfs = TableQuery[Pdfs]
      //      val action=ORIGIN_DB.run(Pdf.filter(_.id > lastid).take(PAGE_SIZE).result)
      val action = ORIGIN_DB.run(pdfs.filter(_.id > lastid).take(PAGE_SIZE).result)
      action.onComplete(data => {
        println("sync get data", data.get.length)
        if (data.isSuccess) {
          val pdfs = data.get.toList.map(a => {
            println(a)
            Pdf.tupled(a)
          })
          if (pdfs.length > 0) {
            self ! ("insert", pdfs)
          } else {
            //拿到底了
            Future {
              println(s"Blocking future start ")
              Thread.sleep(5000) //block for 5 seconds
              println(s"Blocking future finished ")
              self ! ("sync", lastid)
            }
          }
        }
      })
    }
    //  插入数据
    case ("insert", pdfs: List[Pdf]) => {
      println("insert start", pdfs.length)
      val pdf = TableQuery[Pdfs]
      pdf.++=(pdfs.map(a => {
        Pdf.unapply(a).get
      }))
      //Pdf.+=(Pdf.unapply(pdfs.head).get)
      val insertActions = DBIO.seq(
        pdf.++=(pdfs.map(a => {
          Pdf.unapply(a).get
        }))
      )
      DEST_DB.run(insertActions).onComplete(data => {
        println("insert data result", data)
        //添加成功后更新last表
        val lastid = pdfs.last.id
        Sync.lastActor ! ("upsert", tablename, lastid)
      })
    }

    case "start" => {
      println("table Pdf start")
      println(sender())
      println(sender().path)
      Sync.lastActor ! ("get", tablename)
    }

    case ("lastbydest", lastid: Int) => {
      println("last table", lastid)
      //为0或没到拿（异常）
      if (lastid == 0) {
        val pdfs = TableQuery[Pdfs]
        val q = pdfs.map(_.id)
        val maxaction = q.max.result
        val resultFuture: Future[Option[Int]] = DEST_DB.run(maxaction)
        resultFuture.onComplete(data => {
          println("lastbydest", data)
          if (data.isSuccess) {
            if (!data.get.isEmpty) {
              self ! ("sync", data.get.get)
            } else {
              self ! ("sync", 0)
            }
          } else {
            Future {
              println(s"Blocking future start ")
              Thread.sleep(5000) //block for 5 seconds
              println(s"Blocking future finished ")
              println("aa", data.get.get)
              self ! ("lastbydest", data.get.get)
            }
          }
        })
      } else {
        println("sync ", lastid)
        self ! ("sync", lastid)
      }
    }
  }
}


//system.scheduler.scheduleOnce(1 second) {
//  self ! PoisonPill
//}