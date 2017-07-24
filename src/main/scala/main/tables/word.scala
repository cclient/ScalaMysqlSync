
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

case class Word(id: Int,engine: String,source_id: String,title: String,url: String,desc: String)

class Words(tag: Tag) extends Table[(Int,String,String,String,String,String)](tag, "word") {
	 def id =  column[Int]("id")
	 def engine =  column[String]("engine")
	 def source_id =  column[String]("source_id")
	 def title =  column[String]("title")
	 def url =  column[String]("url")
	 def desc =  column[String]("desc")
	def * = (id,engine,source_id,title,url,desc)
}

class WordActor extends Actor {
  val tablename="word"
  val is_just_insert=false
  //  implicit val executionContext: ExecutionContext = context.system.dispatchers.lookup("my-blocking-dispatcher")
  override def receive: Receive = {
    //  从这个id开始后移拿数
    case (BYOFFSET_GET,lastid:Int) => {
      println("sync start by",lastid)
      val words = TableQuery[Words]
      //      val action=ORIGIN_DB.run(Word.filter(_.id > lastid).take(PAGE_SIZE).result)
      val action=ORIGIN_DB.run(words.filter(_.id > lastid).take(PAGE_SIZE).result)
      action.onComplete(data=>{
        println("sync get data",data.get.length)
        if (data.isSuccess){
          val words=data.get.toList.map(a=>{
            Word.tupled(a)
          })
          if (words.length>0){
            Future {
              println(s"Blocking next page 1s start")
              TimeUnit.SECONDS.sleep(1)
              println(s"Blocking next page 1s finished")
              //同步时只考虑insert
              if(is_just_insert){
                self !(BYOFFSET_INSERT,words)
              }else{
                //如果会更新历史数据
                self !(BYOFFSET_INSERT_UPDATE,words)
              }
            }
          }else{
            //拿到底了
            Future {
              println(s"Blocking future 5m start")
              TimeUnit.MINUTES.sleep(5)
              println(s"Blocking future 5m finished")
              self !(BYOFFSET_GET,lastid)
            }
          }
        }
      })
    }
    //  插入数据
    case (BYOFFSET_INSERT,words:List[Word])=>{
      println("insert start",words.length)
      val word = TableQuery[Words]
      word.++=(words.map(a=>{
        Word.unapply(a).get
      }))
      //Word.+=(Word.unapply(words.head).get)
      val insertActions = DBIO.seq(
        word.++=(words.map(a=>{
          Word.unapply(a).get
        }))
      )
      DEST_DB.run(insertActions).onComplete(data=>{
       if (data.isSuccess){
        println("insert data result",data)
        //添加成功后更新last表
         val lastid=words.last.id
         Sync.lastActor !(BYOFFSET_UPSERT_OFFSET,tablename,lastid)
       }else{
          self !(BYOFFSET_INSERT,words)
        }            
      })
    }
    
    //  批量插入数据，有则更新 这种方法失败 sqlu String Interpolation error 待官方修复
    case ("insertOnDuplicateKey2",words:List[Word])=>{
      def buildSql(execpre:String,values: String,execafter:String): DBIO[Int] = sqlu"$execpre $values $execafter"
      val execpre="insert into word (id,engine,source_id,title,url,desc)  values "
      val execafter=" ON DUPLICATE KEY UPDATE  `id`=values(id),`engine`=values(engine),`source_id`=values(source_id),`title`=values(title),`url`=values(url),`desc`=values(desc)"
      val valuesstr=words.map(row=>("("+List(row.id,"'"+row.engine+"'","'"+row.source_id+"'","'"+row.title+"'","'"+row.url+"'","'"+row.desc+"'").mkString(",")+")")).mkString(",\n")
      val insertOrUpdateAction=DBIO.seq(
             buildSql(execpre,valuesstr,execafter)
      )
      DEST_DB.run(insertOrUpdateAction).onComplete(data=>{

       if (data.isSuccess){
        println("insertOnDuplicateKey data result",data)
        //添加成功后更新last表
        val lastid=words.last.id
        Sync.lastActor !(BYOFFSET_UPSERT_OFFSET,tablename,lastid)
       }else{
          self !("insertOnDuplicateKey2",words)
        }            
      })
    }
    
    //  批量插入数据，有则更新 成功但sql有冗余
    case (BYOFFSET_INSERT_UPDATE,words:List[Word])=>{
      def buildInsert(r: Word): DBIO[Int] =
        sqlu"insert into word (id,engine,source_id,title,url,desc) values (${r.id},${r.engine},${r.source_id},${r.title},${r.url},${r.desc}) ON DUPLICATE KEY UPDATE `id`=values(id),`engine`=values(engine),`source_id`=values(source_id),`title`=values(title),`url`=values(url),`desc`=values(desc)"
      val inserts: Seq[DBIO[Int]] = words.map(buildInsert)
      val combined: DBIO[Seq[Int]] = DBIO.sequence(inserts)
      DEST_DB.run(combined).onComplete(data=>{
        println("insertOnDuplicateKey data result",data.get.mkString)
        if (data.isSuccess){
          println(data.get)
          //添加成功后更新last表
          val lastid=words.last.id
          Sync.lastActor !(BYOFFSET_UPSERT_OFFSET,tablename,lastid)
        }else{
          self !(BYOFFSET_INSERT_UPDATE,words)
        }
      })
    }    

    case BYOFFSET_TASK_START=>{
      println("table Word start")
      println(sender())
      println(sender().path)
      Sync.lastActor !(BYOFFSET_OFFSET_FROM_HISTORY_RECORD,tablename)
    }

    case (BYOFFSET_OFFSET_FROM_DESTTABLE,lastid:Int)=>{
      println("last table",lastid)
      //为0或没到拿（异常）
      if (lastid==0){
        val words = TableQuery[Words]
        val q = words.map(_.id)
        val maxaction = q.max.result
        val resultFuture: Future[Option[Int]] = DEST_DB.run(maxaction)
        resultFuture.onComplete(data=>{
          println(BYOFFSET_OFFSET_FROM_DESTTABLE,data)
          if (data.isSuccess){
            if (!data.get.isEmpty){
              self !(BYOFFSET_GET,data.get.get)
            }else{
              self !(BYOFFSET_GET,0)
            }
          }else{
            Future {
              println(s"Blocking future start ")
              TimeUnit.MINUTES.sleep(5)
              println(s"Blocking future finished ")
              println("aa",data.get.get)
              self !(BYOFFSET_OFFSET_FROM_DESTTABLE,data.get.get)
            }
          }
        })
      }else{
        println("sync ",lastid)
        self !(BYOFFSET_GET,lastid)
      }
    }
  }
}    
