package main.task

import akka.actor.{Actor, ActorSystem, Props}
import main.tables._


/**
  * Created by cclient on 6/2/17.
  */

class Sync extends Actor {
  override def preStart(): Unit = {
  }

  override def postStop(): Unit = println("first stopped")

  override def receive: Receive = {
    case "stop" => context.stop(self)
    case ("start") => {
      val pdfactor = context.actorOf(Props[PdfActor], "pdf")
      pdfactor ! "start"
    }
  }
}


object Sync {
  val system = ActorSystem.create("sqlsync")
  val Sync = system.actorOf(Props[Sync], "Sync")
  //  val dataActor = system.actorOf(Props[SqlDataActor], "SqlDataActor")
  val lastActor = system.actorOf(Props[LastActor], "lastActor")

  def main(args: Array[String]) = {
    Sync ! "start"
    //    Thread.sleep(100000000)
    //    sqlDataStart !"article"
    //    sqlDataStart !"zhihu"
  }
}

