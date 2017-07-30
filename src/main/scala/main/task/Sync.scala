package main.task

import akka.actor.{Actor, ActorSystem, Props}
import main.tables._
import main.Action._

/**
  * Created by cclient on 6/2/17.
  */

class Sync extends Actor {
  override def preStart(): Unit = {
  }

  override def postStop(): Unit = println("first stopped")

  override def receive: Receive = {
    case MAIN_TASK_STOP => context.stop(self)
    case MAIN_TASK_START => {
      val excelactor = context.actorOf(Props[ExcelActor], "excel")
      excelactor ! BYOFFSET_TASK_START

      val wordactor = context.actorOf(Props[WordActor], "word")
      wordactor ! ONCEALL_TASK_START
    }
  }
}


object Sync {
  val system = ActorSystem.create("sqlsync")
  val Sync = system.actorOf(Props[Sync], "sync")
  val lastActor = system.actorOf(Props[LastActor], "lastActor")

  def main(args: Array[String]) = {
    Sync ! MAIN_TASK_START
  }
}

