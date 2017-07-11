# -*- coding: utf-8 -*-

import table_pdf


def generator_tables_slick(tables):
    for t in tables:
        tablename, cinfos = generator_table_slick(t)
        print _create_class(tablename, cinfos)


def _create_slick(tablename, columninfos):
    keys = []
    types = []
    kvs = []
    cstrings = []
    for columninfo in columninfos:
        cname = columninfo["k"]
        ctype = columninfo["v"]
        ptype = ' column[%s]("%s")' % (ctype, cname)
        types.append(ctype)
        keys.append(cname)
        kvs.append(cname + ": " + ctype)
        cstrings.append("\t def " + cname.replace("-", "_") + " = " + ptype)
    tempclassname = tablename[0].upper() + tablename[1:]
    ptablecontent = 'class %s(tag: Tag) extends Table[(%s)](tag, "%s") {' % (
        tempclassname + "s", ",".join(types), tablename + "_lb") + "\n"
    ptable = "\n".join(cstrings) + '\n\tdef * = (%s)\n}' % (",".join(keys))
    return "case class %s(%s)" % (tempclassname, ",".join(kvs)) + "\n\n" + ptablecontent + ptable


def generator_table_slick(tablestring):
    lines = filter(lambda k: len(k) > 0, tablestring.split("\n"))
    tablename = lines[0].split(" ")[2][1:-1]
    tablecolumns = []
    for i in xrange(1, len(lines) - 1):
        tablecolumns.append(filter(lambda k: len(k) > 0, lines[i].split(" ")))
    create_columns = filter(lambda k: "`" in k[0], tablecolumns)
    cinfos = []
    sqltypemap = {
        "char": "String",
        "int": "Int",
        "timestamp": "Timestamp",
        "date": "Date",
        "datetime": "Date",
        "text": "String",
        "blob": "Blob",
    }

    #    values = ",".join(map(lambda k: ("row." + k["k"]) if k["is_num"] else ("\"row." + k["k"]+"\""), columninfos))

    for create_column in create_columns:
        name = create_column[0][1:-1]
        typestring = create_column[1]
        matched = False
        for k in sqltypemap:
            if k in typestring:
                cinfos.append({"k": name, "v": sqltypemap[k], "is_num": True if "int" in k else False})
                matched = True
                continue
        if not matched:
            print "error", typestring
    return tablename, cinfos


def _create_actor(tablename, strings, values, repvals, v3):
    base = '''
class %(class)sActor extends Actor {
  val tablename="%(var)s"
  val is_just_insert=false
  //  implicit val executionContext: ExecutionContext = context.system.dispatchers.lookup("my-blocking-dispatcher")
  override def receive: Receive = {
    //  从这个id开始后移拿数
    case ("sync",lastid:Int) => {
      println("sync start by",lastid)
      val %(var)ss = TableQuery[%(class)ss]
      //      val action=ORIGIN_DB.run(%(class)s.filter(_.id > lastid).take(PAGE_SIZE).result)
      val action=ORIGIN_DB.run(%(var)ss.filter(_.id > lastid).take(PAGE_SIZE).result)
      action.onComplete(data=>{
        println("sync get data",data.get.length)
        if (data.isSuccess){
          val %(var)ss=data.get.toList.map(a=>{
            println(a)
            %(class)s.tupled(a)
          })
          if (%(var)ss.length>0){
            Future {
              println(s"Blocking next page 1s start")
              TimeUnit.SECONDS.sleep(1)
              println(s"Blocking next page 1s finished")
              //同步时只考虑insert
              if(is_just_insert){
                self !("insertJust",%(var)ss)
              }else{
                //如果会更新历史数据
                self !("insertOnDuplicateKey",%(var)ss)
              }
            }
          }else{
            //拿到底了
            Future {
              println(s"Blocking future 5m start")
              TimeUnit.MINUTES.sleep(5)
              println(s"Blocking future 5m finished")
              self !("sync",lastid)
            }
          }
        }
      })
    }
    //  插入数据
    case ("insertJust",%(var)ss:List[%(class)s])=>{
      println("insert start",%(var)ss.length)
      val %(var)s = TableQuery[%(class)ss]
      %(var)s.++=(%(var)ss.map(a=>{
        %(class)s.unapply(a).get
      }))
      //%(class)s.+=(%(class)s.unapply(%(var)ss.head).get)
      val insertActions = DBIO.seq(
        %(var)s.++=(%(var)ss.map(a=>{
          %(class)s.unapply(a).get
        }))
      )
      DEST_DB.run(insertActions).onComplete(data=>{
       if (data.isSuccess){
        println("insert data result",data)
        //添加成功后更新last表
         val lastid=%(var)ss.last.id
         Sync.lastActor !("upsert",tablename,lastid)
       }else{
          self !("insertJust",%(var)ss)
        }            
      })
    }
    
    //  批量插入数据，有则更新 这种方法失败 sqlu String Interpolation error 待官方修复
    case ("insertOnDuplicateKey2",%(var)ss:List[%(class)s])=>{
      def buildSql(execpre:String,values: String,execafter:String): DBIO[Int] = sqlu"$execpre $values $execafter"
      val execpre="insert into %(var)s (%(v0)s)  values "
      val execafter=" ON DUPLICATE KEY UPDATE  %(v2)s"
      val valuesstr=%(var)ss.map(row=>("("+List(%(v1)s).mkString(",")+")")).mkString(",\\n")
      val insertOrUpdateAction=DBIO.seq(
             buildSql(execpre,valuesstr,execafter)
      )
      DEST_DB.run(insertOrUpdateAction).onComplete(data=>{

       if (data.isSuccess){
        println("insertOnDuplicateKey data result",data)
        //添加成功后更新last表
        val lastid=%(var)ss.last.id
        Sync.lastActor !("upsert",tablename,lastid)
       }else{
          self !("insertOnDuplicateKey2",%(var)ss)
        }            
      })
    }
    
    //  批量插入数据，有则更新 成功但sql有冗余
    case ("insertOnDuplicateKey",%(var)ss:List[Answer])=>{
      def buildInsert(r: Answer): DBIO[Int] =
        sqlu"insert into answer (%(v0)s) values (%(v3)s) ON DUPLICATE KEY UPDATE %(v2)s"
      val inserts: Seq[DBIO[Int]] = %(var)ss.map(buildInsert)
      val combined: DBIO[Seq[Int]] = DBIO.sequence(inserts)
      DEST_DB.run(combined).onComplete(data=>{
        println("insertOnDuplicateKey data result",data.get.mkString)
        if (data.isSuccess){
          println(data.get)
          //添加成功后更新last表
          val lastid=%(var)ss.last.id
          Sync.lastActor !("upsert",tablename,lastid)
        }else{
          self !("insertOnDuplicateKey",%(var)ss)
        }
      })
    }    

    case "start"=>{
      println("table %(class)s start")
      println(sender())
      println(sender().path)
      Sync.lastActor !("get",tablename)
    }

    case ("lastbydest",lastid:Int)=>{
      println("last table",lastid)
      //为0或没到拿（异常）
      if (lastid==0){
        val %(var)ss = TableQuery[%(class)ss]
        val q = %(var)ss.map(_.id)
        val maxaction = q.max.result
        val resultFuture: Future[Option[Int]] = DEST_DB.run(maxaction)
        resultFuture.onComplete(data=>{
          println("lastbydest",data)
          if (data.isSuccess){
            if (!data.get.isEmpty){
              self !("sync",data.get.get)
            }else{
              self !("sync",0)
            }
          }else{
            Future {
              println(s"Blocking future start ")
              TimeUnit.MINUTES.sleep(5)
              println(s"Blocking future finished ")
              println("aa",data.get.get)
              self !("lastbydest",data.get.get)
            }
          }
        })
      }else{
        println("sync ",lastid)
        self !("sync",lastid)
      }
    }
    
    //最简单的办法是select id from dest.table,再 select * from orginal.table where id in 
    //对方要求的是只在他们表里作最基础的查询，索引join都不让
    //为了不在对方数据库里作sort,select in() 就在代码里diff
    case ("diffOrginDest",records:List[%(class)s]) => {
          val %(var)ss = TableQuery[%(class)ss]
          val action=DEST_DB.run(%(var)ss.result)
          action.onComplete(data=>{
            if (data.isSuccess){
              val destnowrecoreds=data.get.map(c =>%(class)s.tupled(c))
              println("records records",records.length)
              println("destnowrecoreds records",destnowrecoreds.length)
              //拿出源里有，但目的时目前没有的。
              val nohasrecords=records.filter(record=>{
                //目标里是否存在当前项
                !destnowrecoreds.exists(a=>{
                //todo 这里需要根据不同的表修改
                  (a.topic==record.topic&&a.uid==record.uid)
                })
              })
              println("nohasrecords records",nohasrecords.length)
              self !("insertWithOutUpsertLast",nohasrecords)
            }
          })
        }
    //  从这个id开始后移拿数不段循环直到拿全（数据量较小，内存可以承受）
    case ("getByOffset",offset:Int,records:List[%(class)s]) => {
      println("sync by",offset)
      val %(var)ss = TableQuery[%(class)ss]
      val action=ORIGIN_DB.run(%(var)ss.drop(offset).take(PAGE_SIZE).result)
      action.onComplete(data=>{
        println("sync get data",data.get.length)
        if (data.isSuccess){
          val %(var)ss=data.get.toList.map(a=>{
            %(class)s.tupled(a)
          })
          if (%(var)ss.length>0){
            val nrecords=records.:::(%(var)ss)
            Future {
              println(s"next page 1s start")
              TimeUnit.SECONDS.sleep(1)
              println(s"next page 1s finished")
              self !("getByOffset",nrecords.length,nrecords)
            }
          }else{
              self !("diffOrginDest",records)
          }
        }
      })
    }
    //  插入数据
    case ("insertWithOutUpsertLast",%(var)ss:List[%(class)s])=>{
      println("insert start",%(var)ss.length)
      val %(var)s = TableQuery[%(class)ss]
      %(var)s.++=(%(var)ss.map(a=>{
        %(class)s.unapply(a).get
      }))
      val insertActions = DBIO.seq(
        %(var)s.++=(%(var)ss.map(a=>{
          %(class)s.unapply(a).get
        }))
      )
      DEST_DB.run(insertActions).onComplete(data=>{
        println("insert data result",data)
        Future {
          println(s"Blocking future 12h start")
          TimeUnit.HOURS.sleep(12)
          println(s"Blocking future 12h finished")
          self !"startByDiff"
        }
      })
    }
    //这个操作只适用于小表
    case "startByDiff"=>{
      self !("getByOffset",0,List[%(class)s]())
    }
  }
}

'''
    return base % {"var": tablename, "class": tablename[0].upper() + tablename[1:], "v0": strings, "v1": values,
                   "v2": repvals, "v3": v3}


def _create_class(tablename, columninfos):
    v0 = ",".join(map(lambda k: k["k"], columninfos))
    v1 = ",".join(
        map(lambda k: ("row." + k["k"]) if k["is_num"] else ('"\'"+' + "row." + k["k"] + '+"\'"'), columninfos))
    v2 = ",".join(map(lambda k: "`" + k["k"] + "`=values(" + k["k"] + ")", columninfos))
    # ${r.aid}
    v3 = ",".join(map(lambda k: "${r." + k["k"] + "}", columninfos))
    return '''
package main.tables

import java.sql.Blob
import java.sql.Date
import java.sql.Timestamp
import java.util.concurrent.TimeUnit

import akka.actor.Actor
import main.tables.Conf._
import main.task.Sync
import slick.jdbc.MySQLProfile.api._
import slick.lifted.TableQuery

import scala.concurrent.ExecutionContext.Implicits.global
import scala.concurrent.Future

''' + _create_slick(tablename, columninfos) + "\n" + _create_actor(tablename, v0, v1, v2, v3)


generator_tables_slick(table_pdf.tables)
