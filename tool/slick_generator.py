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
    for create_column in create_columns:
        name = create_column[0][1:-1]
        typestring = create_column[1]
        matched = False
        for k in sqltypemap:
            if k in typestring:
                cinfos.append({"k": name, "v": sqltypemap[k]})
                matched = True
                continue
        if not matched:
            print "error", typestring
    return tablename, cinfos


def _create_actor(tablename):
    base = '''
class %(class)sActor extends Actor {
  val tablename="%(var)s"
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
            self !("insert",%(var)ss)
          }else{
            //拿到底了
            Future {
              println(s"Blocking future start ")
              Thread.sleep(5000) //block for 5 seconds
              println(s"Blocking future finished ")
              self !("sync",lastid)
            }
          }
        }
      })
    }
    //  插入数据
    case ("insert",%(var)ss:List[%(class)s])=>{
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
        println("insert data result",data)
        //添加成功后更新last表
         val lastid=%(var)ss.last.id
         Sync.lastActor !("upsert",tablename,lastid)
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
              Thread.sleep(5000) //block for 5 seconds
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
  }
}

'''
    return base % {"var": tablename, "class": tablename[0].upper() + tablename[1:]}


def _create_class(tablename, columninfos):
    return '''
package main.tables
import java.sql.Date
import java.sql.Blob

import akka.actor.Actor
import main.tables.Conf._
import main.task.Sync
import slick.jdbc.MySQLProfile.api._
import slick.lifted.TableQuery

import scala.concurrent.ExecutionContext.Implicits.global
import scala.concurrent.Future

''' + _create_slick(tablename, columninfos) + "\n" + _create_actor(tablename)


generator_tables_slick(table_pdf.tables)
